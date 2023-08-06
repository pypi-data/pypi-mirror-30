import boto3
import dramatiq

from base64 import b64decode, b64encode
from collections import deque
from typing import Any, Dict, Iterable, List, Optional

#: The max number of bytes in a message.
MAX_MESSAGE_SIZE = 256 * 1024

#: The min and max number of seconds messages may be retained for.
MIN_MESSAGE_RETENTION = 60
MAX_MESSAGE_RETENTION = 14 * 86400

#: The maximum amount of time SQS will wait before redelivering a
#: message.  This is also the maximum amount of time that a message can
#: be delayed for.
MAX_VISIBILITY_TIMEOUT = 2 * 3600

#: The max number of messages that may be prefetched at a time.
MAX_PREFETCH = 10

#: The min value for WaitTimeSeconds.
MIN_TIMEOUT = 120


class SQSBroker(dramatiq.Broker):
    """A Dramatiq_ broker that can be used with `Amazon SQS`_

    This backend has a number of limitations compared to the built-in
    Redis and RMQ backends:

      * it does not currently implement a dead-letter queue,
      * the max amount of time messages can be delayed by is 15 seconds,
      * messages can be at most 256KiB large,
      * messages must be processed within 2 hours of being pulled,
        otherwise they will be redelivered.

    The backend uses boto3_ under the hood.  For details on how
    authorization works, check out its docs_.

    Parameters:
      namespace: The prefix to use when creating queues.
      middleware: The set of middleware that apply to this broker.
      retention: The number of seconds messages can be retained for.
        Defaults to 14 days.

    .. _Dramatiq: https://dramatiq.io
    .. _Amazon SQS: https://aws.amazon.com/sqs/
    .. _boto3: http://boto3.readthedocs.io/en/latest/index.html
    .. _docs: http://boto3.readthedocs.io/en/latest/guide/configuration.html
    """

    def __init__(
            self, *,
            namespace: Optional[str] = None,
            middleware: Optional[List[dramatiq.Middleware]] = None,
            retention: int = MAX_MESSAGE_RETENTION,
    ) -> None:
        super().__init__(middleware=middleware)

        if retention < MIN_MESSAGE_RETENTION or retention > MAX_MESSAGE_RETENTION:
            raise ValueError(f"'retention' must be between {MIN_MESSAGE_RETENTION} and {MAX_MESSAGE_RETENTION}.")

        self.namespace: str = namespace
        self.retention: str = str(retention)
        self.queues: Dict[str, Any] = {}
        self.sqs: Any = boto3.resource("sqs")

    def consume(self, queue_name: str, prefetch: int = 1, timeout: int = 30000) -> dramatiq.Consumer:
        try:
            return _SQSConsumer(self.queues[queue_name], prefetch, timeout)
        except KeyError:  # pragma: no cover
            raise dramatiq.QueueNotFound(queue_name)

    def declare_queue(self, queue_name: str) -> None:
        if queue_name not in self.queues:
            prefixed_queue_name = queue_name
            if self.namespace is not None:
                prefixed_queue_name = "%(namespace)s_%(queue_name)s" % {
                    "namespace": self.namespace,
                    "queue_name": queue_name,
                }

            self.emit_before("declare_queue", queue_name)
            self.queues[queue_name] = self.sqs.create_queue(
                QueueName=prefixed_queue_name,
                Attributes={
                    "MessageRetentionPeriod": self.retention,
                }
            )
            self.emit_after("declare_queue", queue_name)

    def enqueue(self, message: dramatiq.Message, *, delay: Optional[int] = None) -> dramatiq.Message:
        queue_name = message.queue_name
        if delay is None:
            queue = self.queues[queue_name]
            delay_seconds = 0
        elif delay <= 15000:
            queue = self.queues[queue_name]
            delay_seconds = int(delay / 1000)
        else:
            raise ValueError("Messages in SQS cannot be delayed for longer than 15 seconds.")

        encoded_message = b64encode(message.encode()).decode()
        if len(encoded_message) > MAX_MESSAGE_SIZE:
            raise RuntimeError("Messages in SQS can be at most 256KiB large.")

        self.logger.debug("Enqueueing message %r on queue %r.", message.message_id, queue_name)
        self.emit_before("enqueue", message, delay)
        queue.send_message(
            MessageBody=encoded_message,
            DelaySeconds=delay_seconds,
        )
        self.emit_after("enqueue", message, delay)
        return message

    def get_declared_queues(self) -> Iterable[str]:
        return set(self.queues)

    def get_declared_delay_queues(self) -> Iterable[str]:
        return set()


class _SQSConsumer(dramatiq.Consumer):
    def __init__(self, queue: Any, prefetch: int, timeout: int) -> None:
        self.queue = queue
        self.prefetch = min(prefetch, MAX_PREFETCH)
        self.timeout = min(int(timeout / 1000), MIN_TIMEOUT)
        self.messages: deque = deque()

    def ack(self, message: "_SQSMessage") -> None:
        message.delete()

    #: We don't use DLQs yet so nack is the same as ack.
    nack = ack

    def requeue(self, messages: List["_SQSMessage"]) -> None:
        """SQS doesn't support requeueing messages so we have to wait
        for the visibility timeout to pass.
        """

    def __next__(self) -> Optional[dramatiq.Message]:
        try:
            return self.messages.popleft()
        except IndexError:
            messages = []
            for sqs_message in self.queue.receive_messages(
                MaxNumberOfMessages=self.prefetch,
                WaitTimeSeconds=self.timeout,
                VisibilityTimeout=MAX_VISIBILITY_TIMEOUT,
            ):
                encoded_message = b64decode(sqs_message.body)
                dramatiq_message = dramatiq.Message.decode(encoded_message)
                messages.append(_SQSMessage(sqs_message, dramatiq_message))

            if messages:
                self.messages = deque(messages)
                return self.messages.popleft()
            return None


class _SQSMessage(dramatiq.MessageProxy):
    def __init__(self, sqs_message: Any, message: dramatiq.Message) -> None:
        super().__init__(message)

        self._sqs_message = sqs_message

    def delete(self):
        """Acknowledge a message by removing it from the queue.
        Messages may still be re-delivered if the server the message
        is stored on is down while the delete request is processed.
        """
        return self._sqs_message.delete()
