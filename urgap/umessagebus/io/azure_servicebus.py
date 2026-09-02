"""Azure Service Bus scheme subclass of urgap's UMessageBus submodule."""

from __future__ import annotations

import json
import logging

from typing import Any

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.servicebus import (
    AutoLockRenewer,
    ServiceBusClient,
    ServiceBusMessage,
    ServiceBusReceiveMode,
)
from azure.servicebus.management import (
    ServiceBusAdministrationClient,
    SqlRuleFilter,
)

from urgap.umessagebus.io._base import UMessageBusBase

logger = logging.getLogger(__name__)


class UMessageBusAzureServiceBus(UMessageBusBase):
    """UMessageBus class interface for Azure Service Bus topics.

    Messages are routed to a subscription by a SQL rule filter on the
    subscription_key application property and are received in PEEK_LOCK mode,
    so a failed message is abandoned and redelivered.
    """

    SCHEMA = "azure-servicebus"

    def __init__(self, **kwargs: Any) -> None:  # noqa: ANN401
        """Create a new UMessageBus class for Azure Service Bus."""
        super().__init__(**kwargs)
        self.credential = None
        self.client = None
        self.receiver = None
        self.completion_sender = None
        self.lock_renewer = None
        self._receiver_ctx = None

    def connect(self) -> None:
        """Open the Service Bus client, receiver and completion sender."""
        self.credential = DefaultAzureCredential()
        self.client = ServiceBusClient(
            fully_qualified_namespace=self.address,
            credential=self.credential,
        )

    def close(self) -> None:
        """Close receiver, renewer and client."""
        if self.lock_renewer is not None:
            self.lock_renewer.close()
            self.lock_renewer = None
        if self._receiver_ctx is not None:
            self._receiver_ctx.__exit__(None, None, None)
            self._receiver_ctx = None
            self.receiver = None
        if self.client is not None:
            self.client.close()
            self.client = None

    def ensure_entities(self) -> None:
        """Create the topics, the subscription and its routing filter."""
        admin = ServiceBusAdministrationClient(
            fully_qualified_namespace=self.address,
            credential=self.credential,
        )
        topic_subscription_filter_pairs = [
            (self.topic_name, self.subscription_name, self.subscription_key),
        ]
        if self.completion_topic is not None:
            topic_subscription_filter_pairs += [
                (self.completion_topic, "Completed", None),
            ]
        for topic, subscription, filter_value in topic_subscription_filter_pairs:
            newly_created_subscription = False
            try:
                admin.get_topic(topic)
            except ResourceNotFoundError:
                admin.create_topic(topic_name=topic)
            try:
                admin.get_subscription(topic, subscription)
            except ResourceNotFoundError:
                admin.create_subscription(
                    topic_name=topic,
                    subscription_name=subscription,
                )
                newly_created_subscription = True

            if (filter_value is not None) and newly_created_subscription:
                admin.delete_rule(topic, subscription, "$Default")
                admin.create_rule(
                    topic_name=topic,
                    subscription_name=subscription,
                    rule_name="unode_filter",
                    filter=SqlRuleFilter(
                        f"subscription_key = '{filter_value}'",
                    ),
                )

        self._receiver_ctx = self.client.get_subscription_receiver(
            topic_name=self.topic_name,
            subscription_name=self.subscription_name,
            max_wait_time=5,
            receive_mode=ServiceBusReceiveMode.PEEK_LOCK,
        )
        self.receiver = self._receiver_ctx.__enter__()
        if self.completion_topic:
            self.completion_sender = self.client.get_topic_sender(
                topic_name=self.completion_topic,
            )

    def receive(self, max_wait_time: int, max_messages: int = 1) -> list:
        """Receive messages from the subscription.

        Args:
            max_wait_time: Seconds to wait for a message before giving up.
            max_messages: Maximum number of messages to return.

        Returns:
            List of received Service Bus messages.
        """
        return self.receiver.receive_messages(
            max_wait_time=max_wait_time,
            max_message_count=max_messages,
        )

    def get_body(self, message: Any) -> str:  # noqa: ANN401
        """Get the json body of a Service Bus message.

        Args:
            message: Received Service Bus message.

        Returns:
            Message body as a json string.
        """
        return str(message)

    def complete(self, message: Any) -> None:  # noqa: ANN401
        """Complete a Service Bus message.

        Args:
            message: Received Service Bus message.
        """
        self.receiver.complete_message(message)

    def abandon(self, message: Any) -> None:  # noqa: ANN401
        """Abandon a Service Bus message so it is redelivered.

        Args:
            message: Received Service Bus message.
        """
        self.receiver.abandon_message(message)

    def renew(self, message: Any, duration: float) -> None:  # noqa: ANN401
        """Register a message with an AutoLockRenewer.

        Args:
            message: Received Service Bus message.
            duration: Maximum lock renewal duration in seconds.
        """
        if duration <= 0:
            return
        if self.lock_renewer is None:
            self.lock_renewer = AutoLockRenewer()
        self.lock_renewer.register(
            self.receiver,
            message,
            max_lock_renewal_duration=duration,
        )

    def publish_completion(self, event: dict) -> None:
        """Publish a completion event to the completion topic.

        Args:
            event: Event payload to serialize.
        """
        if not self.completion_topic or self.completion_sender is None:
            return
        self.completion_sender.send_messages(
            ServiceBusMessage(
                json.dumps(event),
                application_properties={
                    "subscription_key": event.get("subscription_key"),
                },
                correlation_id=event.get("uuid"),
            ),
        )
