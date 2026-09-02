"""GCP Pub/Sub scheme subclass of urgap's UMessageBus submodule."""

from __future__ import annotations

import json
import logging

from typing import Any

from google.api_core.exceptions import AlreadyExists, DeadlineExceeded
from google.cloud import pubsub_v1

from urgap.umessagebus.io._base import UMessageBusBase

logger = logging.getLogger(__name__)

# Pub/Sub refuses to extend an ack deadline beyond 10 minutes
MAX_ACK_DEADLINE_SECONDS = 600
DEFAULT_ACK_DEADLINE_SECONDS = 600


class UMessageBusGCPPubSub(UMessageBusBase):
    """UMessageBus class interface for GCP Pub/Sub topics.

    Messages are routed to a subscription by a subscription filter on the
    subscription_key attribute and are pulled synchronously, so a failed
    message has its ack deadline zeroed and is redelivered.

    The cred_key carries the project, e.g. ``gcp-pubsub://my-gcp-project``.

    Note:
        A Pub/Sub subscription filter is immutable. If the subscription already
        exists with a different filter it is used as it is, which is logged as
        a warning because messages may then not be the ones this worker
        expects.
    """

    SCHEMA = "gcp-pubsub"

    def __init__(self, **kwargs: Any) -> None:  # noqa: ANN401
        """Create a new UMessageBus class for GCP Pub/Sub."""
        super().__init__(**kwargs)
        self.subscriber = None
        self.publisher = None
        self.subscription_path = None
        self.completion_topic_path = None

    @property
    def project(self) -> str:
        """Get the GCP project this transport talks to.

        Returns:
            GCP project id.
        """
        return self.address

    @staticmethod
    def safe_subscription_name(subscription_key: str) -> str:
        """Turn a routing key into a valid Pub/Sub subscription id.

        Pub/Sub allows letters, numbers and ``-_.~+%`` only, so the colon of a
        unode_full_identifier is replaced.

        Args:
            subscription_key: Routing key, e.g. a unode_full_identifier.

        Returns:
            Subscription id Pub/Sub accepts.
        """
        return subscription_key.replace(":", "__")

    def connect(self) -> None:
        """Open the Pub/Sub subscriber and publisher clients."""
        self.subscriber = pubsub_v1.SubscriberClient()
        self.publisher = pubsub_v1.PublisherClient()
        self.subscription_path = self.subscriber.subscription_path(
            self.project,
            self.subscription_name,
        )
        if self.completion_topic:
            self.completion_topic_path = self.publisher.topic_path(
                self.project,
                self.completion_topic,
            )

    def close(self) -> None:
        """Close the subscriber client."""
        if self.subscriber is not None:
            self.subscriber.close()
            self.subscriber = None
        self.publisher = None

    def ensure_entities(self) -> None:
        """Create the topics and the filtered subscription if they are missing."""
        topic_path = self.publisher.topic_path(self.project, self.topic_name)
        topic_paths = [topic_path]
        if self.completion_topic_path:
            topic_paths.append(self.completion_topic_path)
        for path in topic_paths:
            try:
                self.publisher.create_topic(name=path)
            except AlreadyExists:
                logger.debug("Pub/Sub topic %s already exists", path)

        subscription_filter = f'attributes.subscription_key = "{self.subscription_key}"'
        try:
            self.subscriber.create_subscription(
                request={
                    "name": self.subscription_path,
                    "topic": topic_path,
                    "ack_deadline_seconds": DEFAULT_ACK_DEADLINE_SECONDS,
                    "filter": subscription_filter,
                },
            )
        except AlreadyExists:
            existing = self.subscriber.get_subscription(
                request={"subscription": self.subscription_path},
            )
            if existing.filter != subscription_filter:
                logger.warning(
                    "Pub/Sub subscription %s already exists with filter %r instead of "
                    "%r. Filters are immutable, so recreate the subscription if this "
                    "worker should only see its own messages.",
                    self.subscription_path,
                    existing.filter,
                    subscription_filter,
                )

    def receive(self, max_wait_time: int, max_messages: int = 1) -> list:
        """Pull messages from the subscription.

        Args:
            max_wait_time: Seconds to wait for a message before giving up.
            max_messages: Maximum number of messages to return.

        Returns:
            List of received Pub/Sub messages, empty if none arrived in time.
        """
        try:
            response = self.subscriber.pull(
                request={
                    "subscription": self.subscription_path,
                    "max_messages": max_messages,
                },
                timeout=max_wait_time,
            )
        except DeadlineExceeded:
            return []
        return list(response.received_messages)

    def get_body(self, message: Any) -> str:  # noqa: ANN401
        """Get the json body of a Pub/Sub message.

        Args:
            message: Received Pub/Sub message.

        Returns:
            Message body as a json string.
        """
        return message.message.data.decode()

    def complete(self, message: Any) -> None:  # noqa: ANN401
        """Acknowledge a Pub/Sub message.

        Args:
            message: Received Pub/Sub message.
        """
        self.subscriber.acknowledge(
            request={
                "subscription": self.subscription_path,
                "ack_ids": [message.ack_id],
            },
        )

    def abandon(self, message: Any) -> None:  # noqa: ANN401
        """Nack a Pub/Sub message by zeroing its ack deadline.

        Args:
            message: Received Pub/Sub message.
        """
        self.subscriber.modify_ack_deadline(
            request={
                "subscription": self.subscription_path,
                "ack_ids": [message.ack_id],
                "ack_deadline_seconds": 0,
            },
        )

    def renew(self, message: Any, duration: float) -> None:  # noqa: ANN401
        """Extend the ack deadline of a Pub/Sub message.

        Pub/Sub caps a single extension at 10 minutes. Unlike the Service Bus
        AutoLockRenewer this extends once instead of renewing in the
        background, so a handler running longer than the cap needs the message
        redelivered rather than kept.

        Args:
            message: Received Pub/Sub message.
            duration: Requested lock duration in seconds.
        """
        if duration <= 0:
            return
        ack_deadline_seconds = int(min(duration, MAX_ACK_DEADLINE_SECONDS))
        if duration > MAX_ACK_DEADLINE_SECONDS:
            logger.warning(
                "Pub/Sub caps the ack deadline at %ss, extending by that instead of %ss",
                MAX_ACK_DEADLINE_SECONDS,
                duration,
            )
        self.subscriber.modify_ack_deadline(
            request={
                "subscription": self.subscription_path,
                "ack_ids": [message.ack_id],
                "ack_deadline_seconds": ack_deadline_seconds,
            },
        )

    def publish_completion(self, event: dict) -> None:
        """Publish a completion event to the completion topic.

        Args:
            event: Event payload to serialize.
        """
        if not self.completion_topic_path:
            return
        future = self.publisher.publish(
            self.completion_topic_path,
            json.dumps(event).encode(),
            subscription_key=str(event.get("subscription_key") or ""),
            uuid=str(event.get("uuid") or ""),
        )
        future.result()
