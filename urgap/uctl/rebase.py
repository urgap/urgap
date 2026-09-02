"""Rebase submodule of urgap.uctl.

Relocates UFiles from one storage location to another without processing them
and without renaming them. Available synchronously via ``uctl rebase`` and
message driven via ``uctl run rebase-worker``, which pulls work from any
message bus urgap supports (Azure Service Bus or GCP Pub/Sub).
"""

import logging
import pprint

import click

import urgap

from urgap.umessagebus.worker import load_message_context, run_subscription_worker

logger = logging.getLogger(__name__)

REBASE_SUBSCRIPTION_KEY = "urgap_rebase"


def rebase_uris(uris: list[str], storage_base_uri: str) -> list[str]:
    """Rebase UFiles onto a new storage base UUri, keeping their object names.

    Args:
        uris: Urgap URIs of the UFiles to relocate.
        storage_base_uri: Target storage base UUri, e.g. "azure://account/container".

    Returns:
        List of urgap URIs of the relocated UFiles.
    """
    ufiles = urgap.UFileList.from_uri_list(list(uris))
    ufiles.rebase(storage_base_uri=storage_base_uri, upload=True)
    return ufiles.as_uri_list()


@click.command()
@click.argument("storage_base_uri")
@click.argument("uris", nargs=-1, required=True)
def rebase_uris_click(storage_base_uri: str, uris: tuple) -> None:
    """Rebase UFiles to a STORAGE_BASE_URI without renaming them.

    The source files are left untouched, only a copy is placed at the target
    location under the very same object name.

    Example:
        uctl rebase uris azure://account-b/container azure://account-a/container#sub/data.csv
    """
    resulting_uris = rebase_uris(uris=list(uris), storage_base_uri=storage_base_uri)
    logger.info(pprint.pformat("Rebase finished, final uris:"))
    for uri in resulting_uris:
        msg = f"'{uri}'"
        logger.info(pprint.pformat(msg))


def process_rebase_message(body: dict) -> tuple[bool, list[str] | None]:
    """Rebase the UFiles a message asks for.

    Expected consumer_kwargs:
      - input_uris: list of urgap URIs of the UFiles in the source location
      - storage_base_uri: target storage base UUri
      - config: optional urgap config overrides
      - ucredentials: optional credentials needed to reach source and target

    Args:
        body: Full message body.

    Returns:
        Tuple of a success flag and the urgap URIs of the relocated UFiles.
    """
    ok = False
    output_uris = None
    try:
        consumer_kwargs = body["consumer_kwargs"]
        load_message_context(consumer_kwargs)
        output_uris = rebase_uris(
            uris=consumer_kwargs["input_uris"],
            storage_base_uri=consumer_kwargs["storage_base_uri"],
        )
        ok = True
    except Exception:
        logger.exception("Failed to rebase files requested by message")
    return ok, output_uris


@click.command(name="rebase-worker")
@click.option(
    "--via-message-bus",
    "--via-servicebus",
    "via_message_bus",
    help=(
        "Message bus ucredentials key. The scheme selects the transport, e.g. "
        "azure-servicebus://<ns>.servicebus.windows.net or gcp-pubsub://<project-id>."
    ),
    required=True,
)
@click.option(
    "--subscription-key",
    help="Routing key the worker subscribes to.",
    default=REBASE_SUBSCRIPTION_KEY,
    show_default=True,
)
@click.option(
    "--topic",
    help="Topic to receive from. Defaults to the configured service_bus_topic.",
    default=None,
)
@click.option(
    "--completion-topic",
    help=(
        "Topic to publish completion events to. Defaults to the configured "
        "service_bus_completion_topic."
    ),
    default=None,
)
@click.option(
    "--exit-after-first/--stay-alive",
    help="Exit after the first handled message instead of polling forever.",
    default=False,
    show_default=True,
)
def rebase_worker(
    via_message_bus: str,
    subscription_key: str,
    topic: str | None,
    completion_topic: str | None,
    exit_after_first: bool,
) -> None:
    """Relocate UFiles requested via a message bus.

    Each message names the UFiles in the source location and the storage base
    UUri of the target location, the worker copies them over under their
    existing object names and publishes the resulting URIs to the completion
    topic.
    """
    run_subscription_worker(
        cred_key=via_message_bus,
        subscription_key=subscription_key,
        handler=process_rebase_message,
        topic_name=topic,
        completion_topic=completion_topic,
        exit_after_first=exit_after_first,
        # A relay is long lived, it should not give up on an idle queue
        max_empty_polls=0,
    )


@click.group()
def rebase() -> None:
    """Relocate files between storage locations without renaming them."""


rebase.add_command(rebase_uris_click, name="uris")
