"""Message bus worker of urgap.

The worker is agnostic of both the transport and of what a message asks for:
the transport owns the topic and subscription lifecycle and message settlement,
the handler performs the work, and this module owns the receive loop and the
completion event.

A message is expected to look like::

    {
        "uuid": "<correlation id>",
        "subscription_key": "<routing key the subscription filters on>",
        "consumer_kwargs": {...},   # whatever the handler needs
    }

and the handler is called with the full message body, returning
``(ok, output_uris)``.
"""

from __future__ import annotations

import json
import logging
import time

from typing import TYPE_CHECKING, Any, Protocol

import urgap

if TYPE_CHECKING:
    from multiprocessing.synchronize import Event as EventClass

    from urgap.umessagebus.io._base import UMessageBusBase

logger = logging.getLogger(__name__)

DEFAULT_MAX_WAIT_TIME = 5
DEFAULT_MAX_EMPTY_POLLS = 3
DEFAULT_EMPTY_POLL_SLEEP = 10
DEFAULT_TOPIC = "urgap_queue"
DEFAULT_COMPLETION_TOPIC = "urgap_completed"


class MessageHandler(Protocol):
    """Callable which performs the work a message asks for."""

    def __call__(self, body: dict) -> tuple[bool, list[str] | None]:
        """Handle one message body.

        Args:
            body: Full message body, including consumer_kwargs.

        Returns:
            Tuple of a success flag and the resulting urgap URIs.
        """
        ...  # pragma: no cover


def init_message_bus(
    cred_key: str,
    subscription_key: str,
    topic_name: str | None = None,
    subscription_name: str | None = None,
    completion_topic: str | None = None,
) -> UMessageBusBase:
    """Initialize the message bus transport for a cred_key.

    The scheme of the cred_key selects the implementation, e.g.
    ``azure-servicebus://<namespace>.servicebus.windows.net`` or
    ``gcp-pubsub://<project-id>``.

    Args:
        cred_key: UUri of the message bus.
        subscription_key: Routing key the worker accepts.
        topic_name: Topic to receive from, defaults to config service_bus_topic.
        subscription_name: Subscription to receive from.
        completion_topic: Topic to publish completion events to, defaults to
            config service_bus_completion_topic.

    Returns:
        Transport instance for the requested message bus.

    Raises:
        ImportError: If no transport is available for the cred_key scheme.
    """
    scheme = cred_key.split("://", 1)[0]
    available_io_classes = urgap.instances.umessagebus_manager.available_io_classes
    if scheme not in available_io_classes:
        msg = (
            f"Message bus class for scheme '{scheme}' cannot be imported due to "
            f"missing dependencies or unsupported scheme. Available: "
            f"{sorted(available_io_classes)}"
        )
        raise ImportError(msg)
    if topic_name is None:
        topic_name = urgap.config.get("service_bus_topic", DEFAULT_TOPIC)
    if completion_topic is None:
        completion_topic = urgap.config.get(
            "service_bus_completion_topic",
            DEFAULT_COMPLETION_TOPIC,
        )
    return available_io_classes[scheme](
        cred_key=cred_key,
        subscription_key=subscription_key,
        topic_name=topic_name,
        subscription_name=subscription_name,
        completion_topic=completion_topic,
    )


def process_message(
    message: Any,  # noqa: ANN401
    message_bus: UMessageBusBase,
    handler: MessageHandler,
    exit_after_first: bool = False,
) -> bool:
    """Handle a single message.

    Args:
        message: Received transport specific message.
        message_bus: Transport the message came from, used to settle it.
        handler: Callable performing the work the message asks for.
        exit_after_first: If True, stop the loop after one handled message.

    Returns:
        True if the worker loop should stop, False otherwise.
    """
    body = json.loads(message_bus.get_body(message))
    if body.get("subscription_key") != message_bus.subscription_key:
        message_bus.abandon(message)
        return False
    ok, output_uris = handler(body)
    if not ok:
        message_bus.abandon(message)
        return False
    if message_bus.completion_topic is not None:
        event_payload = body.copy()
        if "custom_message" in event_payload:
            event_payload["custom_message"].update({"output_uris": output_uris})
        else:
            event_payload["custom_message"] = {"output_uris": output_uris}
        message_bus.publish_completion(event_payload)
    message_bus.complete(message)
    if exit_after_first:
        logger.info(
            "Configured to exit after first message; stopping worker for %s",
            message_bus.subscription_key,
        )
        return True
    return False


def handle_messages(
    message_bus: UMessageBusBase,
    handler: MessageHandler,
    exit_after_first: bool = False,
    max_autorenew: float = 0,
    max_empty_polls: int = DEFAULT_MAX_EMPTY_POLLS,
) -> None:
    """Receive and handle messages until the worker is done.

    Args:
        message_bus: Transport to receive from.
        handler: Callable performing the work a message asks for.
        exit_after_first: If True, stop after one handled message.
        max_autorenew: Requested lock duration in seconds, 0 disables renewal.
        max_empty_polls: Number of consecutive empty polls after which the
            worker exits. 0 keeps the worker polling forever.
    """
    empty_polls = 0
    while True:
        messages = message_bus.receive(
            max_wait_time=DEFAULT_MAX_WAIT_TIME,
            max_messages=1,
        )
        if not messages:
            empty_polls += 1
            if max_empty_polls and empty_polls >= max_empty_polls:
                logger.info(
                    "No messages after %s consecutive polls exiting worker",
                    empty_polls,
                )
                return
            time.sleep(DEFAULT_EMPTY_POLL_SLEEP)
            continue
        empty_polls = 0
        for message in messages:
            if max_autorenew > 0:
                message_bus.renew(message, max_autorenew)
            stop = process_message(
                message=message,
                message_bus=message_bus,
                handler=handler,
                exit_after_first=exit_after_first,
            )
            if stop:
                return


def run_subscription_worker(
    cred_key: str,
    subscription_key: str,
    handler: MessageHandler,
    subscription_name: str | None = None,
    topic_name: str | None = None,
    completion_topic: str | None = None,
    exit_after_first: bool | None = None,
    max_autorenew: float | None = None,
    max_empty_polls: int = DEFAULT_MAX_EMPTY_POLLS,
    shutdown_event: EventClass | None = None,
) -> None:
    """Run a message bus subscription worker for one routing key.

    Args:
        cred_key: UUri of the message bus, its scheme selects the transport.
        subscription_key: Routing key this worker accepts, also used as the
            subscription filter value.
        handler: Callable performing the work a message asks for.
        subscription_name: Subscription to receive from, defaults to a
            transport safe form of subscription_key.
        topic_name: Topic to receive from, defaults to config service_bus_topic.
        completion_topic: Topic to publish completion events to, defaults to
            config service_bus_completion_topic.
        exit_after_first: If True, stop after one handled message. Defaults to
            config service_bus_exit_after_first_message.
        max_autorenew: Requested lock duration in seconds. Defaults to config
            service_bus_max_autorenewal_minutes.
        max_empty_polls: Number of consecutive empty polls after which the
            worker exits. 0 keeps the worker polling forever.
        shutdown_event: Event to signal the parent process to terminate.
    """
    if exit_after_first is None:
        exit_after_first = urgap.config.get(
            "service_bus_exit_after_first_message",
            True,
        )
    if max_autorenew is None:
        max_autorenew = urgap.config.get("service_bus_max_autorenewal_minutes", 0) * 60

    message_bus = init_message_bus(
        cred_key=cred_key,
        subscription_key=subscription_key,
        topic_name=topic_name,
        subscription_name=subscription_name,
        completion_topic=completion_topic,
    )
    with message_bus:
        logger.info(
            "%s worker started for key=%s topic=%s subscription=%s max_autorenew=%ss",
            message_bus.SCHEMA,
            message_bus.subscription_key,
            message_bus.topic_name,
            message_bus.subscription_name,
            max_autorenew,
        )
        handle_messages(
            message_bus=message_bus,
            handler=handler,
            exit_after_first=exit_after_first,
            max_autorenew=max_autorenew,
            max_empty_polls=max_empty_polls,
        )
    if exit_after_first and shutdown_event:
        shutdown_event.set()


def load_message_context(consumer_kwargs: dict[str, Any]) -> None:
    """Apply the config and ucredentials a message brought along.

    Args:
        consumer_kwargs: Consumer kwargs of a message.
    """
    if consumer_kwargs.get("config"):
        urgap.config.update(consumer_kwargs["config"])
    if consumer_kwargs.get("ucredentials"):
        urgap.instances.ucredential_manager.add_credentials(
            consumer_kwargs["ucredentials"],
        )
