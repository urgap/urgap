"""Unit tests for the transport agnostic message bus worker.

A stub transport stands in for Azure Service Bus / GCP Pub/Sub, so these cover
the settlement and completion logic of the receive loop without a real bus.
"""

import json

import pytest

import urgap

from urgap.umessagebus import worker
from urgap.umessagebus.io._base import UMessageBusBase


class StubMessageBus(UMessageBusBase):
    """Transport handing out preloaded message batches and recording settlement."""

    SCHEMA = None

    def __init__(self, batches=None, **kwargs):
        kwargs.setdefault("cred_key", "stub://nowhere")
        kwargs.setdefault("subscription_key", "urgap_rebase")
        super().__init__(**kwargs)
        self.batches = list(batches or [])
        self.completed = []
        self.abandoned = []
        self.renewed = []
        self.published = []
        self.entities_ensured = False
        self.closed = False

    def connect(self) -> None:
        return

    def close(self) -> None:
        self.closed = True

    def ensure_entities(self) -> None:
        self.entities_ensured = True

    def receive(self, max_wait_time, max_messages=1):  # noqa: ARG002
        return self.batches.pop(0) if self.batches else []

    def get_body(self, message) -> str:
        return json.dumps(message)

    def complete(self, message) -> None:
        self.completed.append(message)

    def abandon(self, message) -> None:
        self.abandoned.append(message)

    def renew(self, message, duration) -> None:
        self.renewed.append((message, duration))

    def publish_completion(self, event) -> None:
        self.published.append(event)


def make_body(key="urgap_rebase"):
    return {
        "uuid": "an-id",
        "subscription_key": key,
        "consumer_kwargs": {"input_uris": ["file:///a#b.csv"]},
    }


def ok_handler(body):  # noqa: ARG001
    return True, ["file:///b#b.csv"]


def failing_handler(body):  # noqa: ARG001
    return False, None


def test_process_message_completes_on_success():
    body = make_body()
    bus = StubMessageBus(completion_topic=None)
    stop = worker.process_message(message=body, message_bus=bus, handler=ok_handler)
    assert stop is False
    assert bus.completed == [body]
    assert bus.abandoned == []


def test_process_message_abandons_on_failure():
    body = make_body()
    bus = StubMessageBus(completion_topic=None)
    worker.process_message(message=body, message_bus=bus, handler=failing_handler)
    assert bus.completed == []
    assert bus.abandoned == [body]


def test_process_message_abandons_foreign_subscription_key():
    body = make_body(key="SomeNode:1.0.0")
    bus = StubMessageBus(completion_topic=None)
    worker.process_message(message=body, message_bus=bus, handler=ok_handler)
    assert bus.abandoned == [body]
    assert bus.completed == []


def test_process_message_stops_when_exit_after_first():
    bus = StubMessageBus(completion_topic=None)
    stop = worker.process_message(
        message=make_body(),
        message_bus=bus,
        handler=ok_handler,
        exit_after_first=True,
    )
    assert stop is True


def test_process_message_publishes_completion_with_output_uris():
    bus = StubMessageBus(completion_topic="urgap_completed")
    worker.process_message(message=make_body(), message_bus=bus, handler=ok_handler)
    assert len(bus.published) == 1
    assert bus.published[0]["custom_message"]["output_uris"] == ["file:///b#b.csv"]
    assert bus.published[0]["uuid"] == "an-id"


def test_process_message_merges_into_existing_custom_message():
    bus = StubMessageBus(completion_topic="urgap_completed")
    body = make_body()
    body["custom_message"] = {"requested_by": "someone"}
    worker.process_message(message=body, message_bus=bus, handler=ok_handler)
    assert bus.published[0]["custom_message"] == {
        "requested_by": "someone",
        "output_uris": ["file:///b#b.csv"],
    }


def test_process_message_does_not_publish_without_completion_topic():
    bus = StubMessageBus(completion_topic=None)
    worker.process_message(message=make_body(), message_bus=bus, handler=ok_handler)
    assert bus.published == []


def test_handle_messages_exits_after_max_empty_polls(monkeypatch):
    monkeypatch.setattr(worker.time, "sleep", lambda _s: None)
    bus = StubMessageBus(completion_topic=None)
    worker.handle_messages(message_bus=bus, handler=ok_handler, max_empty_polls=3)
    assert bus.completed == []


def test_handle_messages_processes_all_batches(monkeypatch):
    monkeypatch.setattr(worker.time, "sleep", lambda _s: None)
    bodies = [make_body(), make_body()]
    bus = StubMessageBus(batches=[[bodies[0]], [bodies[1]]], completion_topic=None)
    worker.handle_messages(message_bus=bus, handler=ok_handler, max_empty_polls=1)
    assert bus.completed == bodies


def test_handle_messages_renews_lock_when_requested(monkeypatch):
    monkeypatch.setattr(worker.time, "sleep", lambda _s: None)
    body = make_body()
    bus = StubMessageBus(batches=[[body]], completion_topic=None)
    worker.handle_messages(
        message_bus=bus,
        handler=ok_handler,
        max_autorenew=120,
        max_empty_polls=1,
    )
    assert bus.renewed == [(body, 120)]


def test_handle_messages_does_not_renew_without_autorenew(monkeypatch):
    monkeypatch.setattr(worker.time, "sleep", lambda _s: None)
    bus = StubMessageBus(batches=[[make_body()]], completion_topic=None)
    worker.handle_messages(message_bus=bus, handler=ok_handler, max_empty_polls=1)
    assert bus.renewed == []


def test_init_message_bus_dispatches_on_scheme():
    bus = worker.init_message_bus(
        cred_key="azure-servicebus://ns.servicebus.windows.net",
        subscription_key="A2ACaller:1.0.0",
    )
    assert bus.SCHEMA == "azure-servicebus"
    assert bus.address == "ns.servicebus.windows.net"
    assert bus.subscription_name == "A2ACaller__1.0.0"


def test_init_message_bus_dispatches_to_pubsub():
    bus = worker.init_message_bus(
        cred_key="gcp-pubsub://my-project",
        subscription_key="urgap_rebase",
    )
    assert bus.SCHEMA == "gcp-pubsub"
    assert bus.project == "my-project"


def test_init_message_bus_rejects_unknown_scheme():
    with pytest.raises(ImportError, match="rabbitmq"):
        worker.init_message_bus(cred_key="rabbitmq://host", subscription_key="x")


def test_init_message_bus_honours_explicit_topics():
    bus = worker.init_message_bus(
        cred_key="gcp-pubsub://my-project",
        subscription_key="urgap_rebase",
        topic_name="my_topic",
        subscription_name="my_subscription",
        completion_topic="my_completion",
    )
    assert (bus.topic_name, bus.subscription_name, bus.completion_topic) == (
        "my_topic",
        "my_subscription",
        "my_completion",
    )


def test_load_message_context_applies_config_and_is_optional():
    worker.load_message_context({})
    worker.load_message_context({"config": {"service_bus_topic": "from_message"}})
    assert urgap.config["service_bus_topic"] == "from_message"


def test_base_class_context_manager_ensures_entities():
    bus = StubMessageBus(completion_topic=None)
    with bus as entered:
        assert entered is bus
        assert bus.entities_ensured is True
    assert bus.closed is True


def test_base_class_requires_implementations():
    bus = UMessageBusBase(cred_key="stub://nowhere", subscription_key="x")
    for method, args in (
        ("connect", ()),
        ("close", ()),
        ("ensure_entities", ()),
        ("receive", (5,)),
        ("get_body", (None,)),
        ("complete", (None,)),
        ("abandon", (None,)),
        ("renew", (None, 1)),
        ("publish_completion", ({},)),
    ):
        with pytest.raises(NotImplementedError):
            getattr(bus, method)(*args)
