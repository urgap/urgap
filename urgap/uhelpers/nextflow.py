"""UHelper.nextflow — urgap integration for Nextflow DSL2 pipelines.

Provides CLI entry points that Nextflow processes invoke as subprocesses.
Data flows between processes via plain text files containing urgap URI strings
(one URI per line). Nextflow owns all parallelism and orchestration; urgap
owns all business logic (provenance, smart rerun, metadata, execution).

Design
------
One channel item = one URI file = one subprocess invocation = one urgap execution.
Urgap is completely unaware of parallelism — it receives URIs, runs a node,
and returns output URIs.

Fan-in (groupTuple) is handled transparently: ``--input_uris`` accepts one or
more URI files; all are merged before the node is called.  This is the Nextflow
equivalent of Beam's ``_unpack_list`` / ``flatten_to_list``.

Usage
-----
Single-sample (standard fan-out)::

    python -m urgap.uhelpers.nextflow \\
        --unode "FilterTabularToCSV:1.0.0" \\
        --input_uris sample_a_uris.txt \\
        --output_uris output_uris.txt \\
        --config pipeline_config.json

Grouped-sample (after groupTuple, multiple URI files)::

    python -m urgap.uhelpers.nextflow \\
        --unode "ConcatCSVs:1.0.0" \\
        --input_uris sample_a_uris.txt sample_b_uris.txt sample_c_uris.txt \\
        --output_uris output_uris.txt \\
        --config pipeline_config.json

Exit codes
----------
* ``0`` — success (node executed or PaC skip occurred)
* ``1`` — unrecoverable error
* ``2`` — no valid input URIs; output file written as empty

Config JSON format
------------------
::

    {
        "urun_dict": {
            "parameters": {
                "FilterTabularToCSV:1.0.0": {"-q": "value > 100"},
                "ConcatCSVs:1.0.0": {},
                "CompressToZip:1.0.0": {}
            },
            "unode_parameters": {
                "storage_base_uri": "gs://my-bucket/output"
            }
        },
        "credentials_lookup": [
            {
                "host": "storage.googleapis.com",
                "user": "svc@project.iam.gserviceaccount.com",
                "scheme": "gs",
                "password": "GOOGLE_APPLICATION_CREDENTIALS",
                "secret_store": "env"
            }
        ],
        "config": {
            "hash_algorithm": "md5",
            "logging_level": "INFO"
        },
        "default_pipeline_config_json": null
    }
"""

import argparse
import copy
import json
import logging
import sys

from pathlib import Path
from typing import ParamSpec

import urgap

P = ParamSpec("P")

logger = logging.getLogger(__name__)

INCOMPLETE_WARNING = (
    "No valid input URIs received. Writing empty output and exiting with code 2."
)


# =============================================================================
# URI file I/O
# =============================================================================


def read_uri_file(path: str | Path) -> list[str]:
    """Read urgap URIs from a plain-text file (one URI per line).

    Lines are stripped of surrounding whitespace. Blank lines and lines
    starting with ``#`` are silently ignored.

    Args:
        path: Path to the URI text file.

    Returns:
        Ordered list of non-empty, non-comment URI strings.

    Raises:
        FileNotFoundError: If *path* does not exist.
        OSError: On any other I/O failure.
    """
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [
        line.strip()
        for line in lines
        if line.strip() and not line.strip().startswith("#")
    ]


def read_uri_files(paths: list[str | Path]) -> list[str]:
    """Read and merge urgap URIs from one or more URI files.

    Handles the ``groupTuple()`` fan-in case where Nextflow stages multiple URI
    files into the work directory for a single process invocation. Equivalent
    to Beam's ``_unpack_list`` / ``flatten_to_list`` for grouped inputs.

    URIs are returned in file order; exact duplicates (same string) are
    removed while first-seen order is preserved.

    Args:
        paths: One or more paths to URI text files. Must not be empty.

    Returns:
        Merged, deduplicated list of URI strings across all files.

    Raises:
        ValueError: If *paths* is empty.
        FileNotFoundError: If any file in *paths* does not exist.
    """
    if not paths:
        raise ValueError("paths must not be empty")
    seen: dict[str, None] = {}  # ordered set via dict keys
    for p in paths:
        for uri in read_uri_file(p):
            seen.setdefault(uri, None)
    return list(seen.keys())


def write_uri_file(uris: list[str | None], path: str | Path) -> None:
    """Write urgap URIs to a plain-text file (one URI per line).

    ``None`` values are silently skipped so callers may pass the raw output
    of ``urgap.UFileList`` operations without prior filtering.

    Args:
        uris: Sequence of URI strings (or ``None``) to write.
        path: Destination file path. Parent directories must exist.

    Raises:
        OSError: On any I/O failure.
    """
    valid = [u for u in uris if u is not None]
    Path(path).write_text("\n".join(valid) + ("\n" if valid else ""), encoding="utf-8")


# =============================================================================
# Config parsing
# =============================================================================


def parse_config(
    config_path: str | Path,
) -> tuple["urgap.URunDict", list[dict], dict]:
    """Parse a pipeline configuration JSON file into urgap objects.

    The JSON file must contain at least a ``"urun_dict"`` key. All other
    top-level keys are optional:

    * ``"credentials_lookup"`` — list of credential dicts (default ``[]``).
    * ``"config"`` — urgap config overrides (default ``{}``).
    * ``"default_pipeline_config_json"`` — path to a JSON file whose
      ``"pipeline_configuration"`` dict is merged *under* the explicit
      ``urun_dict`` (matching the Beam / Prefect pattern).

    When ``"default_pipeline_config_json"`` is set, explicit ``urun_dict``
    values always take precedence over defaults.

    Args:
        config_path: Path to the pipeline configuration JSON file.

    Returns:
        Three-tuple of:
        * ``URunDict`` — merged run configuration.
        * ``list[dict]`` — credential dicts (may be empty).
        * ``dict`` — urgap config overrides (may be empty).

    Raises:
        FileNotFoundError: If *config_path* does not exist.
        KeyError: If required ``"urun_dict"`` key is absent.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    data = json.loads(Path(config_path).read_text(encoding="utf-8"))

    # Optionally load a default config and merge (explicit values override)
    default_config_json_path = data.get("default_pipeline_config_json")
    if default_config_json_path is not None:
        default_data = json.loads(
            Path(default_config_json_path).read_text(encoding="utf-8")
        )
        default_urun_dict = default_data.get("urun_dict", {})
    else:
        default_urun_dict = {}

    # Deep-merge: start from defaults, then overlay explicit values
    merged_urun_dict = copy.deepcopy(default_urun_dict)
    for key, value in data["urun_dict"].items():
        if (
            key in merged_urun_dict
            and isinstance(merged_urun_dict[key], dict)
            and isinstance(value, dict)
        ):
            merged_urun_dict[key].update(value)
        else:
            merged_urun_dict[key] = value

    urd = urgap.URunDict(merged_urun_dict)
    ucredentials = data.get("credentials_lookup") or []
    config = data.get("config") or {}

    return urd, ucredentials, config


# =============================================================================
# Urgap initialisation
# =============================================================================


def setup_urgap(ucredentials: list[dict], config: dict) -> None:
    """Apply urgap configuration and inject credentials.

    Must be called before any ``urgap.init_unode()`` / ``node.run()``
    invocation. Identical in behaviour to ``prefect.setup_urgap`` for
    cross-integration consistency.

    Args:
        ucredentials: List of credential dicts to add to the credential
            manager. Each dict must contain at minimum ``"host"``,
            ``"user"``, ``"scheme"``, ``"password"``, and
            ``"secret_store"``.
        config: Mapping of urgap config keys to values. Applied via
            ``urgap.config.update()``.
    """
    urgap.config.update(config)
    urgap.instances.ucredential_manager.add_credentials(ucredentials)


# =============================================================================
# Core execution
# =============================================================================


def run_unode(
    input_uri_files: list[str | Path],
    output_uri_file: str | Path,
    unode: str,
    config_path: str | Path,
    **kwargs: P.kwargs,
) -> int:
    """Execute an urgap UNode, reading input URIs from files and writing
    output URIs to a file.

    This is the primary entry point for Nextflow process execution.

    **Single-sample case** — one URI file is provided. Urgap receives its
    contents and processes them.

    **Grouped-sample case** (after Nextflow ``groupTuple()``) — multiple URI
    files are provided. They are merged via :func:`read_uri_files` before
    being passed to urgap. Urgap is unaware of the grouping; it just sees a
    flat list of URIs.

    Urgap's PaC hash determines whether computation actually runs. The helper
    always writes ``output_uri_file`` with whatever urgap returns — cached
    or freshly computed. Nextflow sees a successful process in both cases.

    Args:
        input_uri_files: One or more paths to URI text files. Nextflow
            stages these into the work directory before calling the script.
        output_uri_file: Path to write output urgap URIs (one per line).
            Written even when inputs are empty (empty file, exit 2).
        unode: Urgap node identifier in ``"Name:version"`` format,
            e.g. ``"FilterTabularToCSV:1.0.0"``.
        config_path: Path to the pipeline configuration JSON file.
        **kwargs: Extra keyword arguments forwarded to ``node.run()``.

    Returns:
        Exit code:
        * ``0`` — success.
        * ``1`` — unrecoverable error (exception raised).
        * ``2`` — no valid input URIs; output file written empty.
    """
    try:
        urd, ucredentials, config = parse_config(config_path)
        setup_urgap(ucredentials=ucredentials, config=config)

        uris = read_uri_files(input_uri_files)

        if not uris:
            logger.warning(INCOMPLETE_WARNING)
            write_uri_file([], output_uri_file)
            return 2

        node = urgap.init_unode(unode)
        result = node.run(ufiles=uris, urun_dict=urd, **kwargs)
        output_uris = [uf.as_uri() if uf is not None else None for uf in result]
        write_uri_file(output_uris, output_uri_file)
        return 0

    except Exception:
        logger.exception("run_unode failed for unode=%s", unode)
        return 1


# =============================================================================
# CLI
# =============================================================================


def parse_cli_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for the Nextflow helper.

    Args:
        argv: Argument list (defaults to ``sys.argv[1:]``).

    Returns:
        Populated :class:`argparse.Namespace` with attributes:
        ``unode``, ``input_uris`` (list), ``output_uris``, ``config``,
        ``log_level``.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Urgap Nextflow helper: execute urgap nodes within Nextflow "
            "processes. Input/output data flows via URI text files."
        ),
        prog="python -m urgap.uhelpers.nextflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--unode",
        required=True,
        metavar="NAME:VERSION",
        help=(
            "Urgap UNode identifier, e.g. 'FilterTabularToCSV:1.0.0'. "
            "Use 'latest' as the version to resolve to the newest available."
        ),
    )
    parser.add_argument(
        "--input_uris",
        required=True,
        nargs="+",
        metavar="FILE",
        help=(
            "Path(s) to URI text file(s). One file = single-sample execution. "
            "Multiple files = grouped execution (after Nextflow groupTuple()): "
            "all files are merged before being passed to urgap."
        ),
    )
    parser.add_argument(
        "--output_uris",
        required=True,
        metavar="FILE",
        help="Path to write output urgap URIs (one per line).",
    )
    parser.add_argument(
        "--config",
        required=True,
        metavar="FILE",
        help="Path to the pipeline configuration JSON file.",
    )
    parser.add_argument(
        "--log_level",
        default=None,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Override the logging level set in the config JSON.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point for ``python -m urgap.uhelpers.nextflow``.

    Parses arguments, configures logging, then delegates to
    :func:`run_unode`.

    Args:
        argv: Argument list (defaults to ``sys.argv[1:]``).

    Returns:
        Exit code (0 / 1 / 2 — see :func:`run_unode`).
    """
    args = parse_cli_args(argv)

    # Determine log level: CLI flag > config file > default "INFO".
    # Reading the config file here (before run_unode) lets the pipeline's
    # logging_level setting take effect for all urgap library messages,
    # including DEBUG-level hash diagnostic logs.
    log_level = args.log_level
    if log_level is None:
        try:
            import json as _json

            _cfg_data = _json.loads(Path(args.config).read_text(encoding="utf-8"))
            log_level = _cfg_data.get("config", {}).get("logging_level", "INFO")
        except Exception:
            log_level = "INFO"

    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        stream=sys.stderr,  # Nextflow captures stderr; stdout is for Groovy
    )

    logger.info("urgap Nextflow helper — unode=%s", args.unode)
    logger.info("input_uris=%s", args.input_uris)
    logger.info("output_uris=%s", args.output_uris)
    logger.info("config=%s", args.config)

    try:
        return run_unode(
            input_uri_files=args.input_uris,
            output_uri_file=args.output_uris,
            unode=args.unode,
            config_path=args.config,
        )
    except Exception:
        logger.exception("urgap Nextflow helper failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
