"""GCP Pub/Sub scheme subclass of urgap's UMessageBus submodule."""

from __future__ import annotations

import json
import logging
import threading
import time

from typing import Any

from google.api_core.exceptions import (
    AlreadyExists,
    DeadlineExceeded,
    GoogleAPICallError,
)
from google.cloud import pubsub_v1

from urgap.umessagebus.io._base import COMPLETION_SUBSCRIPTION_NAME, UMessageBusBase

logger = logging.getLogger(__name__)

# Pub/Sub refuses to extend an ack deadline beyond 10 minutes in one call
MAX_ACK_DEADLINE_SECONDS = 600
DEFAULT_ACK_DEADLINE_SECONDS = 600
# How often the background renewer re-extends the deadline of a held message,
# comfortably inside MAX_ACK_DEADLINE_SECONDS so a slow call still has margin
LEASE_RENEWAL_INTERVAL_SECONDS = 300
LEASE_RENEWER_JOIN_TIMEOUT_SECONDS = 5


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
        self._leases: dict[str, float] = {}
        self._lease_lock = threading.Lock()
        self._lease_stop = threading.Event()
        self._lease_thread: threading.Thread | None = None

    @property
    def project(self) -> str:
        """Get the GCP project this transport talks to.

        Returns:
            GCP project id.
        """
        return self.address

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
        """Stop the lease renewer and close the subscriber client."""
        self._stop_lease_renewer()
        if self.subscriber is not None:
            self.subscriber.close()
            self.subscriber = None
        self.publisher = None

    def ensure_entities(self) -> None:
        """Create the topics and the subscriptions if they are missing."""
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

        self._ensure_completion_subscription()

    def _ensure_completion_subscription(self) -> None:
        """Create the unfiltered subscription on the completion topic.

        Pub/Sub drops what is published to a topic nothing subscribes to, so
        the completion events would be lost before whoever submitted the work
        gets to read them. The same subscription is created by the Service Bus
        transport.
        """
        if not self.completion_topic_path:
            return
        completion_subscription_path = self.subscriber.subscription_path(
            self.project,
            COMPLETION_SUBSCRIPTION_NAME,
        )
        try:
            self.subscriber.create_subscription(
                request={
                    "name": completion_subscription_path,
                    "topic": self.completion_topic_path,
                    "ack_deadline_seconds": DEFAULT_ACK_DEADLINE_SECONDS,
                },
            )
        except AlreadyExists:
            logger.debug(
                "Pub/Sub subscription %s already exists",
                completion_subscription_path,
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
        self._forget_lease(message.ack_id)
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
        self._forget_lease(message.ack_id)
        self.subscriber.modify_ack_deadline(
            request={
                "subscription": self.subscription_path,
                "ack_ids": [message.ack_id],
                "ack_deadline_seconds": 0,
            },
        )

    def renew(self, message: Any, duration: float) -> None:  # noqa: ANN401
        """Keep a Pub/Sub message leased while it is being handled.

        Pub/Sub caps a single extension at 10 minutes, so a longer duration is
        held by re-extending the deadline from a background thread until the
        duration is used up or the message is settled, which is what the
        Service Bus AutoLockRenewer does for that transport.

        Args:
            message: Received Pub/Sub message.
            duration: Requested lock duration in seconds.
        """
        if duration <= 0:
            return
        self._extend_ack_deadline(
            message.ack_id,
            int(min(duration, MAX_ACK_DEADLINE_SECONDS)),
        )
        if duration <= MAX_ACK_DEADLINE_SECONDS:
            return
        with self._lease_lock:
            self._leases[message.ack_id] = time.monotonic() + duration
        self._start_lease_renewer()

    def _extend_ack_deadline(self, ack_id: str, ack_deadline_seconds: int) -> None:
        """Extend the ack deadline of one message.

        Args:
            ack_id: Ack id of the message to extend.
            ack_deadline_seconds: Seconds to extend the deadline by.
        """
        if self.subscriber is None:
            return
        self.subscriber.modify_ack_deadline(
            request={
                "subscription": self.subscription_path,
                "ack_ids": [ack_id],
                "ack_deadline_seconds": ack_deadline_seconds,
            },
        )

    def _forget_lease(self, ack_id: str) -> None:
        """Stop renewing the deadline of a message that is settled.

        Args:
            ack_id: Ack id of the settled message.
        """
        with self._lease_lock:
            self._leases.pop(ack_id, None)

    def _start_lease_renewer(self) -> None:
        """Start the background renewer thread unless it is already running."""
        with self._lease_lock:
            if self._lease_thread is not None and self._lease_thread.is_alive():
                return
            self._lease_stop.clear()
            self._lease_thread = threading.Thread(
                target=self._lease_renewal_loop,
                name=f"pubsub-lease-renewer-{self.subscription_name}",
                daemon=True,
            )
            self._lease_thread.start()

    def _stop_lease_renewer(self) -> None:
        """Stop the background renewer thread and drop the leases it holds."""
        self._lease_stop.set()
        if self._lease_thread is not None:
            self._lease_thread.join(timeout=LEASE_RENEWER_JOIN_TIMEOUT_SECONDS)
            self._lease_thread = None
        with self._lease_lock:
            self._leases.clear()

    def _lease_renewal_loop(self) -> None:
        """Re-extend the held messages until the transport is closed."""
        while not self._lease_stop.wait(LEASE_RENEWAL_INTERVAL_SECONDS):
            self._renew_due_leases()

    def _renew_due_leases(self) -> None:
        """Extend every held message which has renewal duration left."""
        now = time.monotonic()
        with self._lease_lock:
            leases = list(self._leases.items())
        for ack_id, expires_at in leases:
            remaining = expires_at - now
            if remaining <= LEASE_RENEWAL_INTERVAL_SECONDS:
                # Renewing again would outlive the requested duration, so the
                # current deadline is left to lapse and the message redelivered
                self._forget_lease(ack_id)
                logger.warning(
                    "Renewal duration of Pub/Sub message %s is used up, it is "
                    "redelivered if the handler has not settled it yet",
                    ack_id,
                )
                continue
            try:
                self._extend_ack_deadline(
                    ack_id,
                    int(min(remaining, MAX_ACK_DEADLINE_SECONDS)),
                )
            except GoogleAPICallError:
                logger.warning(
                    "Could not extend the ack deadline of Pub/Sub message %s",
                    ack_id,
                    exc_info=True,
                )
                self._forget_lease(ack_id)

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
