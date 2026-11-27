"""Unit tests for the GCP Pub/Sub transport, with the Google clients stubbed."""

import json
import time

import pytest

from google.api_core.exceptions import AlreadyExists, DeadlineExceeded, PermissionDenied

from urgap.umessagebus.io.gcp_pubsub import (
    LEASE_RENEWAL_INTERVAL_SECONDS,
    MAX_ACK_DEADLINE_SECONDS,
    MAX_ATTRIBUTE_VALUE_BYTES,
    UMessageBusGCPPubSub,
)

DEAD_LETTER_TOPIC = "projects/my-project/topics/urgap_rebase_deadletter"


class StubPublisher:
    def __init__(self, existing_topics=()):
        self.existing_topics = set(existing_topics)
        self.created_topics = []
        self.published = []
        self.fail_publish = False

    @staticmethod
    def topic_path(project, topic):
        return f"projects/{project}/topics/{topic}"

    def create_topic(self, name):
        if name in self.existing_topics:
            raise AlreadyExists(name)
        self.created_topics.append(name)

    def publish(self, topic, data, **attrs):
        self.published.append((topic, data, attrs))
        fail = self.fail_publish

        class StubFuture:
            def result(self):
                if fail:
                    raise PermissionDenied("no publish rights on the topic")
                return "message-id"

        return StubFuture()


class StubMessage:
    def __init__(self, ack_id, body, attributes=None):
        self.ack_id = ack_id
        self.message = type(
            "Msg",
            (),
            {"data": json.dumps(body).encode(), "attributes": attributes or {}},
        )()


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
        self.dead_letter_topic = ""
        self.failing_lookups = 0
        self.lookups = 0

    @staticmethod
    def subscription_path(project, subscription):
        return f"projects/{project}/subscriptions/{subscription}"

    def create_subscription(self, request):
        if self.existing_filter is not None:
            raise AlreadyExists(request["name"])
        self.created.append(request)

    def get_subscription(self, request):  # noqa: ARG002
        self.lookups += 1
        if self.failing_lookups:
            self.failing_lookups -= 1
            raise PermissionDenied("no rights to read the subscription")
        policy = type("Policy", (), {"dead_letter_topic": self.dead_letter_topic})()
        return type(
            "Sub",
            (),
            {"filter": self.existing_filter, "dead_letter_policy": policy},
        )()

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


def connected_bus(monkeypatch, completion_topic="urgap_completed"):
    """Create a connected Pub/Sub transport with both Google clients stubbed."""
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
        completion_topic=completion_topic,
    )
    message_bus.connect()
    return message_bus


@pytest.fixture
def bus(monkeypatch):
    """A connected Pub/Sub transport with both Google clients stubbed."""
    message_bus = connected_bus(monkeypatch)
    yield message_bus
    message_bus.close()


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


def test_ensure_entities_subscribes_to_the_completion_topic(bus):
    bus.ensure_entities()
    created = bus.subscriber.created[1]
    assert created["name"] == "projects/my-project/subscriptions/Completed"
    assert created["topic"] == "projects/my-project/topics/urgap_completed"
    assert "filter" not in created


def test_ensure_entities_skips_the_completion_subscription_without_topic(monkeypatch):
    message_bus = connected_bus(monkeypatch, completion_topic=None)
    message_bus.ensure_entities()
    assert [request["name"] for request in message_bus.subscriber.created] == [
        "projects/my-project/subscriptions/urgap_rebase",
    ]


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


def test_renew_does_not_start_a_renewer_for_a_short_duration(bus):
    bus.renew(StubMessage("ack-1", {}), 120)
    assert bus._leases == {}
    assert bus._lease_thread is None


def test_renew_caps_the_first_extension_and_keeps_the_lease(bus):
    bus.renew(StubMessage("ack-1", {}), 3600)
    assert bus.subscriber.deadlines == [(["ack-1"], MAX_ACK_DEADLINE_SECONDS)]
    assert list(bus._leases) == ["ack-1"]
    assert bus._lease_thread.is_alive()


def test_renewer_extends_a_message_held_longer_than_the_maximum(bus):
    bus.renew(StubMessage("ack-1", {}), 3600)
    bus._renew_due_leases()
    assert bus.subscriber.deadlines == [
        (["ack-1"], MAX_ACK_DEADLINE_SECONDS),
        (["ack-1"], MAX_ACK_DEADLINE_SECONDS),
    ]


def test_renewer_gives_up_when_the_requested_duration_is_used_up(bus, caplog):
    bus.renew(StubMessage("ack-1", {}), 3600)
    bus._leases["ack-1"] = time.monotonic() + LEASE_RENEWAL_INTERVAL_SECONDS - 1
    bus._renew_due_leases()
    assert bus._leases == {}
    assert "is used up" in caplog.text
    assert bus.subscriber.deadlines == [(["ack-1"], MAX_ACK_DEADLINE_SECONDS)]


def test_settling_a_message_stops_renewing_it(bus):
    message = StubMessage("ack-1", {})
    bus.renew(message, 3600)
    bus.complete(message)
    bus._renew_due_leases()
    assert bus._leases == {}
    assert bus.subscriber.deadlines == [(["ack-1"], MAX_ACK_DEADLINE_SECONDS)]


def test_abandoning_a_message_stops_renewing_it(bus):
    message = StubMessage("ack-1", {})
    bus.renew(message, 3600)
    bus.abandon(message)
    bus._renew_due_leases()
    assert bus._leases == {}
    assert bus.subscriber.deadlines == [
        (["ack-1"], MAX_ACK_DEADLINE_SECONDS),
        (["ack-1"], 0),
    ]


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
    message_bus = connected_bus(monkeypatch, completion_topic=None)
    message_bus.publish_completion({"uuid": "an-id"})
    assert message_bus.publisher.published == []


def test_close_closes_the_subscriber(bus):
    bus.close()
    assert bus.subscriber is None


def test_close_stops_the_lease_renewer(bus):
    bus.renew(StubMessage("ack-1", {}), 3600)
    lease_thread = bus._lease_thread
    bus.close()
    assert not lease_thread.is_alive()
    assert bus._leases == {}


def test_dead_letter_publishes_to_the_dead_letter_topic_and_acknowledges(bus):
    bus.subscriber.dead_letter_topic = DEAD_LETTER_TOPIC
    message = StubMessage(
        "ack-1",
        {"uuid": "an-id"},
        attributes={"subscription_key": "urgap_rebase"},
    )
    bus.dead_letter(message, reason="Source file(s) do not exist: a.pdf")
    assert bus.publisher.published == [
        (
            DEAD_LETTER_TOPIC,
            message.message.data,
            {
                "subscription_key": "urgap_rebase",
                "dead_letter_reason": "Source file(s) do not exist: a.pdf",
                "dead_letter_source_subscription": (
                    "projects/my-project/subscriptions/urgap_rebase"
                ),
            },
        ),
    ]
    assert bus.subscriber.acknowledged == ["ack-1"]
    assert bus.subscriber.deadlines == []


def test_dead_letter_looks_up_the_dead_letter_topic_once(bus):
    bus.subscriber.dead_letter_topic = DEAD_LETTER_TOPIC
    bus.dead_letter(StubMessage("ack-1", {}), reason="missing")
    bus.dead_letter(StubMessage("ack-2", {}), reason="missing")
    assert bus.subscriber.lookups == 1
    assert bus.subscriber.acknowledged == ["ack-1", "ack-2"]


def test_dead_letter_abandons_without_a_dead_letter_topic(bus, caplog):
    bus.dead_letter(StubMessage("ack-1", {}), reason="missing")
    assert bus.publisher.published == []
    assert bus.subscriber.acknowledged == []
    assert bus.subscriber.deadlines == [(["ack-1"], 0)]
    assert "has no dead letter topic" in caplog.text


def test_dead_letter_abandons_when_publishing_fails(bus, caplog):
    bus.subscriber.dead_letter_topic = DEAD_LETTER_TOPIC
    bus.publisher.fail_publish = True
    bus.dead_letter(StubMessage("ack-1", {}), reason="missing")
    assert bus.subscriber.acknowledged == []
    assert bus.subscriber.deadlines == [(["ack-1"], 0)]
    assert "Could not publish to dead letter topic" in caplog.text


def test_dead_letter_retries_the_lookup_after_it_failed(bus):
    bus.subscriber.dead_letter_topic = DEAD_LETTER_TOPIC
    bus.subscriber.failing_lookups = 1
    bus.dead_letter(StubMessage("ack-1", {}), reason="missing")
    bus.dead_letter(StubMessage("ack-2", {}), reason="missing")
    assert bus.subscriber.deadlines == [(["ack-1"], 0)]
    assert bus.subscriber.acknowledged == ["ack-2"]
    assert bus.subscriber.lookups == 2


def test_dead_letter_reason_fits_the_attribute_limit(bus):
    bus.subscriber.dead_letter_topic = DEAD_LETTER_TOPIC
    bus.dead_letter(StubMessage("ack-1", {}), reason="é" * MAX_ATTRIBUTE_VALUE_BYTES)
    reason = bus.publisher.published[0][2]["dead_letter_reason"]
    assert len(reason.encode()) <= MAX_ATTRIBUTE_VALUE_BYTES
    assert set(reason) == {"é"}


def test_dead_letter_stops_renewing_the_message(bus):
    bus.subscriber.dead_letter_topic = DEAD_LETTER_TOPIC
    message = StubMessage("ack-1", {})
    bus.renew(message, MAX_ACK_DEADLINE_SECONDS * 3)
    bus.dead_letter(message, reason="missing")
    assert "ack-1" not in bus._leases
