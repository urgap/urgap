"""Unit tests for the GCP Pub/Sub transport, with the Google clients stubbed."""

import json

import pytest

from google.api_core.exceptions import AlreadyExists, DeadlineExceeded

from urgap.umessagebus.io.gcp_pubsub import (
    MAX_ACK_DEADLINE_SECONDS,
    UMessageBusGCPPubSub,
)


class StubPublisher:
    def __init__(self, existing_topics=()):
        self.existing_topics = set(existing_topics)
        self.created_topics = []
        self.published = []

    @staticmethod
    def topic_path(project, topic):
        return f"projects/{project}/topics/{topic}"

    def create_topic(self, name):
        if name in self.existing_topics:
            raise AlreadyExists(name)
        self.created_topics.append(name)

    def publish(self, topic, data, **attrs):
        self.published.append((topic, data, attrs))

        class StubFuture:
            def result(self):
                return "message-id"

        return StubFuture()


class StubMessage:
    def __init__(self, ack_id, body):
        self.ack_id = ack_id
        self.message = type("Msg", (), {"data": json.dumps(body).encode()})()


class StubPullResponse:
    def __init__(self, messages):
        self.received_messages = messages


class StubSubscriber:
    def __init__(self, batches=None, existing_filter=None, raise_deadline=False):
        self.batches = list(batches or [])
        self.existing_filter = existing_filter
        self.raise_deadline = raise_deadline
        self.created = []
        self.acknowledged = []
        self.deadlines = []
        self.closed = False

    @staticmethod
    def subscription_path(project, subscription):
        return f"projects/{project}/subscriptions/{subscription}"

    def create_subscription(self, request):
        if self.existing_filter is not None:
            raise AlreadyExists(request["name"])
        self.created.append(request)

    def get_subscription(self, request):  # noqa: ARG002
        return type("Sub", (), {"filter": self.existing_filter})()

    def pull(self, request, timeout=None):  # noqa: ARG002
        if self.raise_deadline:
            raise DeadlineExceeded("no messages")
        return StubPullResponse(self.batches.pop(0) if self.batches else [])

    def acknowledge(self, request):
        self.acknowledged.extend(request["ack_ids"])

    def modify_ack_deadline(self, request):
        self.deadlines.append(
            (request["ack_ids"], request["ack_deadline_seconds"]),
        )

    def close(self):
        self.closed = True


@pytest.fixture
def bus(monkeypatch):
    """A connected Pub/Sub transport with both Google clients stubbed."""
    subscriber = StubSubscriber()
    publisher = StubPublisher()
    monkeypatch.setattr(
        "urgap.umessagebus.io.gcp_pubsub.pubsub_v1.SubscriberClient",
        lambda: subscriber,
    )
    monkeypatch.setattr(
        "urgap.umessagebus.io.gcp_pubsub.pubsub_v1.PublisherClient",
        lambda: publisher,
    )
    message_bus = UMessageBusGCPPubSub(
        cred_key="gcp-pubsub://my-project",
        subscription_key="urgap_rebase",
        completion_topic="urgap_completed",
    )
    message_bus.connect()
    return message_bus


def test_project_and_paths_come_from_cred_key(bus):
    assert bus.project == "my-project"
    assert bus.subscription_path == "projects/my-project/subscriptions/urgap_rebase"
    assert bus.completion_topic_path == "projects/my-project/topics/urgap_completed"


def test_subscription_name_strips_colon_from_unode_identifier():
    assert (
        UMessageBusGCPPubSub.safe_subscription_name("A2ACaller:1.0.0")
        == "A2ACaller__1.0.0"
    )


def test_ensure_entities_creates_topics_and_filtered_subscription(bus):
    bus.ensure_entities()
    assert bus.publisher.created_topics == [
        "projects/my-project/topics/urgap_queue",
        "projects/my-project/topics/urgap_completed",
    ]
    assert bus.subscriber.created[0]["filter"] == (
        'attributes.subscription_key = "urgap_rebase"'
    )
    assert bus.subscriber.created[0]["topic"] == "projects/my-project/topics/urgap_queue"


def test_ensure_entities_tolerates_existing_topics(bus):
    bus.publisher.existing_topics = {"projects/my-project/topics/urgap_queue"}
    bus.ensure_entities()
    assert bus.publisher.created_topics == ["projects/my-project/topics/urgap_completed"]


def test_ensure_entities_warns_on_mismatched_immutable_filter(bus, caplog):
    bus.subscriber.existing_filter = 'attributes.subscription_key = "something_else"'
    bus.ensure_entities()
    assert "Filters are immutable" in caplog.text


def test_ensure_entities_is_quiet_on_matching_filter(bus, caplog):
    bus.subscriber.existing_filter = 'attributes.subscription_key = "urgap_rebase"'
    bus.ensure_entities()
    assert "Filters are immutable" not in caplog.text


def test_receive_returns_messages(bus):
    bus.subscriber.batches = [[StubMessage("ack-1", {"uuid": "an-id"})]]
    messages = bus.receive(max_wait_time=5)
    assert len(messages) == 1
    assert json.loads(bus.get_body(messages[0])) == {"uuid": "an-id"}


def test_receive_treats_deadline_exceeded_as_empty(bus):
    bus.subscriber.raise_deadline = True
    assert bus.receive(max_wait_time=5) == []


def test_complete_acknowledges(bus):
    bus.complete(StubMessage("ack-1", {}))
    assert bus.subscriber.acknowledged == ["ack-1"]


def test_abandon_zeroes_the_ack_deadline(bus):
    bus.abandon(StubMessage("ack-1", {}))
    assert bus.subscriber.deadlines == [(["ack-1"], 0)]


def test_renew_extends_the_ack_deadline(bus):
    bus.renew(StubMessage("ack-1", {}), 120)
    assert bus.subscriber.deadlines == [(["ack-1"], 120)]


def test_renew_is_capped_at_the_pubsub_maximum(bus, caplog):
    bus.renew(StubMessage("ack-1", {}), 3600)
    assert bus.subscriber.deadlines == [(["ack-1"], MAX_ACK_DEADLINE_SECONDS)]
    assert "caps the ack deadline" in caplog.text


def test_renew_is_a_noop_without_duration(bus):
    bus.renew(StubMessage("ack-1", {}), 0)
    assert bus.subscriber.deadlines == []


def test_publish_completion_sends_json_with_attributes(bus):
    bus.publish_completion({"uuid": "an-id", "subscription_key": "urgap_rebase"})
    topic, data, attrs = bus.publisher.published[0]
    assert topic == "projects/my-project/topics/urgap_completed"
    assert json.loads(data.decode())["uuid"] == "an-id"
    assert attrs == {"subscription_key": "urgap_rebase", "uuid": "an-id"}


def test_publish_completion_is_noop_without_completion_topic(monkeypatch):
    subscriber, publisher = StubSubscriber(), StubPublisher()
    monkeypatch.setattr(
        "urgap.umessagebus.io.gcp_pubsub.pubsub_v1.SubscriberClient",
        lambda: subscriber,
    )
    monkeypatch.setattr(
        "urgap.umessagebus.io.gcp_pubsub.pubsub_v1.PublisherClient",
        lambda: publisher,
    )
    message_bus = UMessageBusGCPPubSub(
        cred_key="gcp-pubsub://my-project",
        subscription_key="urgap_rebase",
        completion_topic=None,
    )
    message_bus.connect()
    message_bus.publish_completion({"uuid": "an-id"})
    assert publisher.published == []


def test_close_closes_the_subscriber(bus):
    bus.close()
    assert bus.subscriber is None
