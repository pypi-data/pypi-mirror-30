import json
from functools import partial
import time
try:
    from queue import Full, Empty
except ImportError:
    from Queue import Full, Empty
from collections import namedtuple

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.httpclient import AsyncHTTPClient
from tornado.escape import json_decode

from .rest_proxy import request_for_batch, ERROR_CODES, RETRIABLE_ERROR_CODES
from .message import Message
from .events import FlushReason, DropReason
from .custom_logging import getLogger

logger = getLogger('kafka_rest.producer')

class AsyncProducer(object):
    def __init__(self, client):
        self.client = client
        self.flush_timers = {}
        self.retry_timer = None
        self.inflight_requests = {}
        self.http_client = AsyncHTTPClient(io_loop=self.client.io_loop,
                                           max_clients=self.client.http_max_clients)

    def _schedule_retry_periodically(self):
        logger.trace('Scheduling retry queue processing every {0} seconds'.format(self.client.retry_period_seconds))
        self.retry_timer = PeriodicCallback(self._start_retries,
                                            self.client.retry_period_seconds * 1000)
        self.retry_timer.start()

    def _message_batches_from_queue(self, queue):
        current_time = time.time()
        current_batch = []
        while not queue.empty():
            try:
                message = queue.get_nowait()
            except Empty:
                break
            # If this is the retry queue, stop gathering if the first prioritized
            # item in the queue isn't due for retry yet. If this is the first-send
            # queue, this shouldn't ever trigger because retry_after_time is 0
            if message.retry_after_time > current_time:
                queue.put_nowait(message)
                break
            current_batch.append(message)
            if len(current_batch) >= self.client.flush_max_batch_size:
                yield current_batch
                current_batch = []
        if current_batch:
            yield current_batch

    def _start_retries(self):
        """Go through all the retry queues and schedule produce callbacks
        for all messages that are due to be retried."""
        if self.client.response_5xx_circuit_breaker.tripped:
            logger.trace('Transport circuit breaker is tripped, skipping retry pass')
            self.client.registrar.emit('circuit_breaker.retries')
            return

        logger.trace('Checking retry queues for events to retry')
        for topic, retry_queue in self.client.retry_queues.items():
            for batch in self._message_batches_from_queue(retry_queue):
                logger.trace('Retrying batch of size {0} for topic {1}'.format(len(batch), topic))
                self.client.registrar.emit('retry_batch', topic, batch)
                IOLoop.current().add_callback(self._send_batch_produce_request, topic, batch)

    def _reset_flush_timer(self, topic):
        if topic in self.flush_timers:
            logger.trace('Clearing flush timer for topic {0}'.format(topic))
            IOLoop.current().remove_timeout(self.flush_timers[topic])
        logger.trace('Scheduled new flush timer for topic {0} in {1} seconds'.format(topic,
                                                                                     self.client.flush_time_threshold_seconds))
        handle = IOLoop.current().call_later(self.client.flush_time_threshold_seconds,
                                             self._flush_topic, topic, FlushReason.TIME)
        self.flush_timers[topic] = handle

    def _send_batch_produce_request(self, topic, batch):
        if self.client.in_shutdown:
            connect_timeout = self.client.shutdown_timeout_seconds
            request_timeout = self.client.shutdown_timeout_seconds
        else:
            connect_timeout = self.client.connect_timeout_seconds
            request_timeout = self.client.request_timeout_seconds
        request = request_for_batch(self.client.host, self.client.port,
                                    connect_timeout, request_timeout,
                                    self.client.schema_cache, topic, batch)
        logger.info('Sending {0} events to topic {1}'.format(len(batch), topic))
        self.client.registrar.emit('send_request', topic, batch)
        self.inflight_requests[request._id] = request
        self.http_client.fetch(request,
                               callback=partial(self._handle_produce_response, topic),
                               raise_error=False)

    def _queue_message_for_retry(self, topic, message):
        if message.can_retry(self.client):
            new_message = message.for_retry(self.client)
            try:
                self.client.retry_queues[topic].put_nowait(new_message)
            except Full:
                logger.critical('Retry queue full for topic {0}, message {1} cannot be retried'.format(topic, message))
                self.client.registrar.emit('drop_message', topic, message, DropReason.RETRY_QUEUE_FULL)
            else:
                logger.trace('Queued failed message {0} for retry in topic {1}'.format(new_message, topic))
                self.client.registrar.emit('retry_message', topic, new_message)
        else:
            logger.critical('Dropping failed message {0} for topic {1}, has exceeded maximum retries'.format(message, topic))
            self.client.registrar.emit('drop_message', topic, message, DropReason.MAX_RETRIES_EXCEEDED)

    def _handle_produce_success(self, topic, response, response_body):
        # Store schema IDs if we haven't already
        if self.client.schema_cache[topic].get('value-id') is None:
            logger.debug('Storing value schema ID of {0} for topic {1}'.format(response_body['value_schema_id'], topic))
            self.client.schema_cache[topic]['value-id'] = response_body['value_schema_id']
        if response_body.get('key_schema_id') and self.client.schema_cache[topic].get('key-id') is None:
            logger.debug('Storing key schema ID of {0} for topic {1}'.format(response_body['key_schema_id'], topic))
            self.client.schema_cache[topic]['key-id'] = response_body['key_schema_id']

        # Individual requests could still have failed, need to check
        # each response object's error code
        succeeded, failed = [], []
        for idx, offset in enumerate(response_body['offsets']):
            message = response.request._batch[idx]
            if offset.get('error_code') is None:
                succeeded.append((message, offset))
            elif offset.get('error_code') in RETRIABLE_ERROR_CODES:
                failed.append((message, offset))
                self._queue_message_for_retry(topic, message)
            else:
                failed.append((message, offset))
                logger.critical('Got non-retriable error code ({0}: {1}) for message {2}'.format(offset.get('error_code'),
                                                                                                 offset.get('message'),
                                                                                                 response.request._batch[idx]))
                self.client.registrar.emit('drop_message', topic, message, DropReason.NONRETRIABLE)

        logger.info('Successful produce response for topic {0}. Succeeded: {1} Failed: {2}'.format(topic,
                                                                                                   len(succeeded),
                                                                                                   len(failed)))
        logger.trace('Failed messages with offsets: {0}'.format(failed))
        self.client.registrar.emit('produce_success', topic, succeeded, failed)

    def _handle_produce_response(self, topic, response):
        del self.inflight_requests[response.request._id]

        if response.code != 599:
            try:
                response_body = json_decode(response.body)
            except Exception:
                # The proxy should always respond to us in JSON but it's possible
                # something like a load balancer or reverse proxy could return
                # a response to us we are not expecting.
                logger.error('Got unexpected non-JSON body in response, will attempt to retry')
                self.client.registrar.emit('response_malformed', topic, response)
                self.client.response_5xx_circuit_breaker.record_failure()
                for message in response.request._batch:
                    self._queue_message_for_retry(topic, message)
                return
            else:
                error_code, error_message = response_body.get('error_code'), response_body.get('message')

        if response.code not in (200, 599):
            logger.error('Received {0} response ({1}: {2}) submitting batch to topic {3}'.format(response.code,
                                                                                                 error_code,
                                                                                                 error_message,
                                                                                                 topic))

        if response.code >= 500:
            self.client.response_5xx_circuit_breaker.record_failure()
            self.client.registrar.emit('response_5xx', topic, response)
        else:
            self.client.response_5xx_circuit_breaker.reset()

        if response.code == 200:
            self._handle_produce_success(topic, response, response_body)
        else: # We failed somehow, more information in the error code
            if response.code == 599 or error_code in RETRIABLE_ERROR_CODES:
                for message in response.request._batch:
                    self._queue_message_for_retry(topic, message)
            else: # Non-retriable failure of entire request
                for message in response.request._batch:
                    self.client.registrar.emit('drop_message', topic, message, DropReason.NONRETRIABLE)

    def _flush_topic(self, topic, reason):
        if self.client.response_5xx_circuit_breaker.tripped:
            logger.trace('Transport circuit breaker is tripped, skipping flush topic')
            self.client.registrar.emit('circuit_breaker.flush_topic', topic, reason)
        else:
            logger.trace('Flushing topic {0} (reason: {1})'.format(topic, reason))
            self.client.registrar.emit('flush_topic', topic, reason)
            queue = self.client.message_queues[topic]
            for batch in self._message_batches_from_queue(queue):
                IOLoop.current().add_callback(self._send_batch_produce_request, topic, batch)
        if not self.client.in_shutdown:
            self._reset_flush_timer(topic)

    def evaluate_queue(self, topic, queue):
        if queue.qsize() >= self.client.flush_length_threshold:
            self._flush_topic(topic, FlushReason.LENGTH)
        elif topic not in self.flush_timers:
            self._reset_flush_timer(topic)

    def start_shutdown(self):
        """Prevent the producer from firing off any additional requests
        as a result of timers, then schedule the remainder of the shutdown
        tasks to take place after giving in-flight requests some time
        to return."""
        # We need to take manual control of the event loop now, so
        # we stop the timers in order to not fight against them
        self.retry_timer.stop()
        for topic in self.flush_timers:
            logger.debug('Shutdown: removing flush timer for topic {0}'.format(topic))
            IOLoop.current().remove_timeout(self.flush_timers[topic])

        # Last-ditch send attempts on remaining messages. These will use
        # shorter shutdown timeouts on the request in order to finish
        # by the time we invoke _finish_shutdown
        self.client.response_5xx_circuit_breaker.reset()
        IOLoop.current().add_callback(self._start_retries)
        for topic, queue in self.client.message_queues.items():
            if not queue.empty():
                IOLoop.current().add_callback(self._flush_topic, topic, FlushReason.SHUTDOWN)

        logger.debug('Shutdown: waiting {0} seconds for in-flight requests to return'.format(self.client.shutdown_timeout_seconds))

        # We issue this step in a separate callback to get around a small timing issue
        # with sending out all these requests before shutdown. If you imagine that the
        # _flush_topic calls above take 0.1 seconds each to complete, if we simply
        # registered this call here before any of those calls did their 0.1 seconds
        # of work, we would actually invoke _finish_shutdown before the last request
        # made had the full length of time allotted to it to finish its request.
        # Additionally, we add a buffer second to the timeout to make sure the request
        # timeouts get into Tornado's IOLoop before the shutdown request.
        IOLoop.current().add_callback(lambda: IOLoop.current().call_later(self.client.shutdown_timeout_seconds + 1,
                                                                          self._finish_shutdown))

    def _finish_shutdown(self):
        # Anything not sent at this point is not going to make it out. We
        # fire off a specialized event in this case to give the
        # application code a chance to do something with this data all
        # at once.
        self.client.registrar.emit('shutdown',
                                   self.client.message_queues,
                                   self.client.retry_queues,
                                   self.inflight_requests)
        IOLoop.current().stop()
        logger.debug('Shutdown: producer issued stop command to IOLoop')
