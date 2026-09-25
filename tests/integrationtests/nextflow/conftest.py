"""Pytest configuration for Nextflow integration tests.

The entire test module is skipped when Nextflow is not installed.
Individual tests may additionally require specific cloud credentials or
container runtimes, in which case they apply their own skip markers.
"""

import json
import shutil
import subprocess

from pathlib import Path

import pytest
import urgap


# ---------------------------------------------------------------------------
# Nextflow work-dir cleanup
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def cleanup_nextflow_dirs(tmp_path):
    """Remove Nextflow work directories after each test."""
    yield  # let the test run first so outputs are available for inspection

    for cwd in [tmp_path, tmp_path / "run2"]:
        for entry in cwd.iterdir() if cwd.exists() else []:
            if entry.name in {"work", ".nextflow"} or entry.name.startswith(
                ".nextflow.log"
            ):
                shutil.rmtree(entry, ignore_errors=True)


# ---------------------------------------------------------------------------
# Toy data constants
# ---------------------------------------------------------------------------

#: Absolute path to the toy CSV files.  Using an absolute path is required
#: for ``file://`` URIs so that urgap can resolve the files on disk.
TOY_DATA_DIR = Path(__file__).parents[2].resolve() / "data" / "nextflow_toy_csvs"

#: Uftype used for the toy input CSVs.
#: ``.any.csv`` is a child of ``.any.tabular`` in the urgap uftype tree, so
#: FilterTabularToCSV (which declares ``.any.tabular`` as input) accepts it.
TOY_UFTYPE = urgap.uftypes.any.CSV

#: Pandas query applied to the toy CSVs by FilterTabularToCSV.
#: Yields 2 rows from toy_a, 2 from toy_b, 1 from toy_c = 5 total.
FILTER_QUERY = "value > 5"

#: Expected total rows after concat of all three filtered CSVs.
EXPECTED_CONCAT_ROWS = 5

#: Expected sum of the ``value`` column after concat.
EXPECTED_VALUE_SUM = 40


# ---------------------------------------------------------------------------
# Module-level skip guard
# ---------------------------------------------------------------------------


def pytest_collection_modifyitems(items):
    """Skip Nextflow-dependent tests when Nextflow is not on PATH.

    Only tests decorated with ``@pytest.mark.integration`` are skipped;
    pure-Python tests (e.g. ``test_filter_merge_compress_via_helpers``)
    run regardless of whether Nextflow is installed.
    """
    if shutil.which("nextflow") is None:
        skip_marker = pytest.mark.skip(reason="Nextflow not installed / not on PATH")
        for item in items:
            if (
                "integrationtests/nextflow" in str(item.fspath)
                and item.get_closest_marker("integration") is not None
            ):
                item.add_marker(skip_marker)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def nextflow_available():
    """Assert Nextflow is available and return its version string."""
    nf = shutil.which("nextflow")
    if nf is None:
        pytest.skip("Nextflow not installed")
    result = subprocess.run(
        ["nextflow", "-version"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


@pytest.fixture
def pipeline_nf():
    """Return the path to the integration-test Nextflow pipeline."""
    path = Path(__file__).parent / "pipeline.nf"
    assert path.exists(), f"pipeline.nf not found at {path}"
    return path


@pytest.fixture
def toy_uri_files(tmp_path):
    """Create three URI text files, each pointing to one toy CSV.

    Uses the toy CSVs in ``data/`` alongside this conftest.  The files share
    an identical ``id,value,name`` schema, so FilterTabularToCSV output can
    be fed into ConcatCSVs without schema errors.

    Returns:
        List of three Path objects (one URI file per sample).
    """
    toy_csvs = ["toy_a.csv", "toy_b.csv", "toy_c.csv"]
    uri_files = []
    for i, csv_name in enumerate(toy_csvs):
        uri = f"file://{TOY_DATA_DIR}?uftype={TOY_UFTYPE}#{csv_name}"
        uri_file = tmp_path / f"sample_{chr(ord('a') + i)}_uris.txt"
        uri_file.write_text(uri + "\n")
        uri_files.append(uri_file)
    return uri_files


@pytest.fixture
def samplesheet(tmp_path, toy_uri_files):
    """Create a samplesheet CSV referencing the three toy URI files.

    Format::

        sample_id,uri_file
        sample_a,/path/to/sample_a_uris.txt
        sample_b,/path/to/sample_b_uris.txt
        sample_c,/path/to/sample_c_uris.txt
    """
    csv_path = tmp_path / "samplesheet.csv"
    lines = ["sample_id,uri_file"]
    for i, uri_file in enumerate(toy_uri_files):
        lines.append(f"sample_{chr(ord('a') + i)},{uri_file}")
    csv_path.write_text("\n".join(lines) + "\n")
    return csv_path


@pytest.fixture
def pipeline_config(tmp_path):
    """Write a pipeline_config.json for the integration test pipeline.

    Stores outputs under ``tmp_path/urgap_output`` so every pytest run gets
    a fresh output directory.
    """
    output_dir = tmp_path / "urgap_output"
    output_dir.mkdir()

    config = {
        "urun_dict": {
            "parameters": {
                # The same node and query are used for both the per-sample filter
                # (fan-out) and the multi-input merge (fan-in).  Re-applying the
                # query to already-filtered data is idempotent.
                "FilterTabularToCSV:1.0.0": {
                    "-q": FILTER_QUERY,
                },
                "CompressToZip:1.0.0": {},
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{output_dir}",
            },
        },
        "credentials_lookup": [],
        "config": {
            # DEBUG enables [UFile.hash] and [calculate_ucfs] diagnostic messages
            # that print the exact ucfs/scratch-path/hash values for each file.
            # These are essential for diagnosing PaC-skip hash mismatches.
            "logging_level": "DEBUG",
        },
    }

    config_file = tmp_path / "pipeline_config.json"
    config_file.write_text(json.dumps(config, indent=2))
    return config_file
