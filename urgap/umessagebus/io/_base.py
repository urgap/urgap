"""UMessageBus IO submodule of urgap."""

from __future__ import annotations

from typing import Any, Self

DEFAULT_TOPIC = "urgap_queue"


class UMessageBusBase:
    """Base class for message bus transports in urgap.

    A transport owns the topic and subscription lifecycle of one subscription
    and settles the messages it hands out. It is addressed by a cred_key UUri
    whose scheme selects the implementation, e.g.
    ``azure-servicebus://<namespace>.servicebus.windows.net`` or
    ``gcp-pubsub://<project-id>``.

    Subclasses implement the transport specific parts and are discovered by
    their SCHEMA attribute.
    """

    SCHEMA: str | None = None

    def __init__(
        self,
        cred_key: str,
        subscription_key: str,
        topic_name: str | None = None,
        subscription_name: str | None = None,
        completion_topic: str | None = None,
    ) -> None:
        """Create a transport for one subscription.

        Args:
            cred_key: UUri of the message bus, its scheme selects this class and
                its remainder addresses the namespace, project or account.
            subscription_key: Routing key this worker accepts, also used as the
                subscription filter value.
            topic_name: Topic to receive from.
            subscription_name: Subscription to receive from, defaults to a
                transport safe form of subscription_key.
            completion_topic: Topic to publish completion events to, None
                disables completion events.
        """
        self.cred_key = cred_key
        self.subscription_key = subscription_key
        self.topic_name = topic_name or DEFAULT_TOPIC
        self.subscription_name = subscription_name or self.safe_subscription_name(
            subscription_key,
        )
        self.completion_topic = completion_topic

    @property
    def address(self) -> str:
        """Get the transport address, i.e. the cred_key without its scheme.

        Returns:
            Namespace, project or account this transport talks to.
        """
        return self.cred_key.split("://", 1)[-1].rstrip("/")

    @staticmethod
    def safe_subscription_name(subscription_key: str) -> str:
        """Turn a routing key into a name every transport accepts.

        Args:
            subscription_key: Routing key, e.g. a unode_full_identifier.

        Returns:
            Subscription name without characters the transports reject.
        """
        return subscription_key.replace(":", "__")

    def __enter__(self) -> Self:
        """Connect to the message bus and make sure the entities exist."""
        self.connect()
        self.ensure_entities()
        return self

    def __exit__(self, *_exc_info: object) -> None:
        """Disconnect from the message bus."""
        self.close()

    def connect(self) -> None:
        """Open the clients this transport needs."""
        raise NotImplementedError(self._not_implemented_msg("connect"))

    def close(self) -> None:
        """Close the clients this transport opened."""
        raise NotImplementedError(self._not_implemented_msg("close"))

    def ensure_entities(self) -> None:
        """Create topic, subscription and routing filter if they do not exist."""
        raise NotImplementedError(self._not_implemented_msg("ensure_entities"))

    def receive(self, max_wait_time: int, max_messages: int = 1) -> list:
        """Receive up to max_messages messages.

        Args:
            max_wait_time: Seconds to wait for a message before giving up.
            max_messages: Maximum number of messages to return.

        Returns:
            List of transport specific messages, empty if none arrived.
        """
        raise NotImplementedError(self._not_implemented_msg("receive"))

    def get_body(self, message: Any) -> str:  # noqa: ANN401
        """Get the json body of a received message.

        Args:
            message: Transport specific message.

        Returns:
            Message body as a json string.
        """
        raise NotImplementedError(self._not_implemented_msg("get_body"))

    def complete(self, message: Any) -> None:  # noqa: ANN401
        """Settle a message as handled so it is not redelivered.

        Args:
            message: Transport specific message.
        """
        raise NotImplementedError(self._not_implemented_msg("complete"))

    def abandon(self, message: Any) -> None:  # noqa: ANN401
        """Release a message back to the subscription for redelivery.

        Args:
            message: Transport specific message.
        """
        raise NotImplementedError(self._not_implemented_msg("abandon"))

    def renew(self, message: Any, duration: float) -> None:  # noqa: ANN401
        """Keep a message locked while it is being handled.

        Args:
            message: Transport specific message.
            duration: Requested lock duration in seconds.
        """
        raise NotImplementedError(self._not_implemented_msg("renew"))

    def publish_completion(self, event: dict) -> None:
        """Publish a completion event, if a completion topic is configured.

        Args:
            event: Event payload to serialize.
        """
        raise NotImplementedError(self._not_implemented_msg("publish_completion"))

    def _not_implemented_msg(self, method: str) -> str:
        return f"{method} needs to be implemented in the UMessageBus class"
