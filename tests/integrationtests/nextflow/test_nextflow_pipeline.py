"""Nextflow integration test: 3 toy CSVs -> filter -> merge -> compress.

Pipeline under test
-------------------
::

    samplesheet (3 samples, toy CSVs with identical schema)
         | fan-out: one FilterTabularToCSV process per sample (parallel)
    FilterTabularToCSV:1.0.0  ---  3 x filtered .csv  (query: "value > 5")
         | groupTuple(): collect all 3 outputs under key "all"
    FilterTabularToCSV:1.0.0  ---  1 x merged .csv    (multi-input, idempotent re-filter)
         |
    CompressToZip:1.0.0  -------  1 x .zip

Expected intermediate results (toy data, query "value > 5")::

    toy_a.csv  ->  2 rows   (values 10, 8)
    toy_b.csv  ->  2 rows   (values  6, 9)
    toy_c.csv  ->  1 row    (value   7)
    merge      ->  5 rows   value_sum == 40   (3 inputs, re-filter idempotent)
    compress   ->  1 .zip

The ``test_filter_merge_compress_via_helpers`` test runs entirely in Python
without Nextflow, making it suitable for CI environments without Nextflow.
"""

import json
import subprocess

from pathlib import Path

import pandas as pd
import pytest
import urgap

from pprint import pprint
from urgap.uhelpers.nextflow import (
    read_uri_file,
    run_unode,
)

from .conftest import (
    EXPECTED_CONCAT_ROWS,
    EXPECTED_VALUE_SUM,
    FILTER_QUERY,
    TOY_DATA_DIR,
    TOY_UFTYPE,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def run_nextflow(
    pipeline_nf: Path, extra_args: list[str], cwd: Path
) -> subprocess.CompletedProcess:
    """Run a Nextflow pipeline and return the CompletedProcess."""
    cmd = ["nextflow", "run", str(pipeline_nf)] + extra_args
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd))


# ---------------------------------------------------------------------------
# Full end-to-end Nextflow pipeline test
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_nextflow_pipeline_filter_merge_compress(
    nextflow_available,
    pipeline_nf,
    samplesheet,
    pipeline_config,
    tmp_path,
):
    """Full pipeline: 3 toy CSVs -> filter (fan-out) -> merge (fan-in) -> compress.

    Asserts:
    * Nextflow exits with code 0.
    * ``results/`` contains at least one output URI file.
    * Each output URI points to a ``.zip`` file.
    """
    results_dir = tmp_path / "results"

    result = run_nextflow(
        pipeline_nf=pipeline_nf,
        extra_args=[
            "--samplesheet",
            str(samplesheet),
            "--config",
            str(pipeline_config),
            "--outdir",
            str(results_dir),
        ],
        cwd=tmp_path,
    )

    if result.returncode != 0:
        print("=== NEXTFLOW STDOUT ===")
        print(result.stdout)
        print("=== NEXTFLOW STDERR ===")
        print(result.stderr)

    assert result.returncode == 0, (
        f"Nextflow exited with code {result.returncode}\n"
        f"stderr: {result.stderr[-2000:]}"
    )

    output_uri_files = list(results_dir.rglob("output_uris.txt"))
    assert len(output_uri_files) >= 1, f"No output_uris.txt found under {results_dir}"

    for uri_file in output_uri_files:
        uris = read_uri_file(uri_file)
        assert len(uris) >= 1, f"Empty URI file: {uri_file}"
        for uri in uris:
            assert ".zip" in uri or urgap.uftypes.compression.ZIP in uri, (
                f"Expected ZIP output URI, got: {uri}"
            )


# ---------------------------------------------------------------------------
# Smart-rerun test: second run produces identical URIs (PaC skip)
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_nextflow_pipeline_smart_rerun(
    nextflow_available,
    pipeline_nf,
    samplesheet,
    pipeline_config,
    tmp_path,
):
    """Running the same pipeline twice uses urgap's PaC skip on the second run.

    Nextflow's ``-resume`` flag is NOT used: urgap's PaC hash guarantees that
    identical inputs + parameters produce the same output filenames, so the
    second run returns cached results without re-executing.
    """
    results_dir = tmp_path / "results"
    extra_args = [
        "--samplesheet",
        str(samplesheet),
        "--config",
        str(pipeline_config),
        "--outdir",
        str(results_dir),
    ]

    print(results_dir)
    pprint([p for p in results_dir.rglob("*")])
    print()
    result1 = run_nextflow(pipeline_nf, extra_args, cwd=tmp_path)

    print(results_dir)
    pprint([p for p in results_dir.rglob("*")])
    print()
    assert result1.returncode == 0, f"First run failed: {result1.stderr[-2000:]}"
    # Capture the set of files urgap wrote to storage after the first run.
    # URIs are NOT compared directly: they contain a dot_str_0= provenance
    # encoding that includes the Nextflow work directory path, which differs
    # between the two runs even though the actual output files are identical.
    output_dir = tmp_path / "urgap_output"
    first_files = frozenset(
        p.relative_to(output_dir) for p in output_dir.rglob("*") if p.is_file()
    )
    assert first_files, "No urgap output files found after first run"

    work_dir2 = tmp_path / "run2"
    work_dir2.mkdir()
    result2 = run_nextflow(pipeline_nf, extra_args, cwd=work_dir2)
    print(results_dir)
    pprint([p for p in results_dir.rglob("*")])
    print()
    assert result2.returncode == 0, f"Second run failed: {result2.stderr[-2000:]}"

    second_files = frozenset(
        p.relative_to(output_dir) for p in output_dir.rglob("*") if p.is_file()
    )

    new_files = second_files - first_files

    # Collect per-process urgap logs from Nextflow work directories.
    # Nextflow captures each process's stderr in .command.err; these contain
    # the [UFile.hash] / [calculate_ucfs] diagnostics that identify hash mismatches.
    def _collect_command_err(cwd: Path, label: str) -> str:
        lines = [f"=== {label} .command.err files ==="]
        work_root = cwd / "work"
        if work_root.exists():
            for err_file in sorted(work_root.rglob(".command.err")):
                content = err_file.read_text(errors="replace").strip()
                if content:
                    lines.append(f"--- {err_file.relative_to(cwd)} ---")
                    lines.append(content)
        return "\n".join(lines)

    # Include urgap logs in the failure message so the PaC rerun reason is visible
    # without needing to run pytest with -s / --capture=no.
    assert not new_files, (
        f"Second run created new output files -- urgap PaC skip may not be working.\n"
        f"First run files: {sorted(str(f) for f in first_files)}\n"
        f"New files: {sorted(str(f) for f in new_files)}\n\n"
        f"=== RUN 1 NEXTFLOW STDERR ===\n{result1.stderr[-2000:]}\n\n"
        f"=== RUN 2 NEXTFLOW STDERR ===\n{result2.stderr[-2000:]}\n\n"
        f"{_collect_command_err(tmp_path, 'RUN 1')}\n\n"
        f"{_collect_command_err(work_dir2, 'RUN 2')}"
    )


# ---------------------------------------------------------------------------
# Pure-Python integration test (no Nextflow required)
# ---------------------------------------------------------------------------


def test_filter_merge_compress_via_helpers(tmp_path):
    """Run the pipeline logic using Python helpers directly (no Nextflow).

    Reproduces what the Nextflow pipeline does:
    1. Fan-out: FilterTabularToCSV per sample (one call per toy CSV).
    2. Fan-in: FilterTabularToCSV with all 3 filtered outputs as input
       (multi-input concat; re-applying the query is idempotent).
    3. Compress the merged CSV to zip.

    Expected results:
    * toy_a filtered: 2 rows (values 10, 8)
    * toy_b filtered: 2 rows (values  6, 9)
    * toy_c filtered: 1 row  (value   7)
    * merge:          5 rows, ``value`` sum == 40
    * compress:       one ``.zip`` output URI
    """
    output_dir = tmp_path / "urgap_output"
    output_dir.mkdir()

    config = {
        "urun_dict": {
            "parameters": {
                "FilterTabularToCSV:1.0.0": {"-q": FILTER_QUERY},
                "CompressToZip:1.0.0": {},
            },
            "unode_parameters": {"storage_base_uri": f"file://{output_dir}"},
        },
        "credentials_lookup": [],
        "config": {"logging_level": "INFO"},
    }
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config))

    toy_csvs = ["toy_a.csv", "toy_b.csv", "toy_c.csv"]
    expected_per_file_rows = [2, 2, 1]

    # ------------------------------------------------------------------
    # Step 1: FilterTabularToCSV -- one call per sample (simulates fan-out)
    # ------------------------------------------------------------------
    filter_output_files = []
    for csv_name, expected_rows in zip(toy_csvs, expected_per_file_rows):
        input_uri = f"file://{TOY_DATA_DIR}?uftype={TOY_UFTYPE}#{csv_name}"
        input_uri_file = tmp_path / f"input_{csv_name}.txt"
        input_uri_file.write_text(input_uri + "\n")

        output_uri_file = tmp_path / f"filter_output_{csv_name}.txt"
        exit_code = run_unode(
            input_uri_files=[input_uri_file],
            output_uri_file=output_uri_file,
            unode="FilterTabularToCSV:1.0.0",
            config_path=config_file,
        )
        assert exit_code == 0, f"FilterTabularToCSV failed on {csv_name}"
        assert output_uri_file.exists()

        # Verify per-sample row count and that all remaining rows pass the filter
        uris = read_uri_file(output_uri_file)
        assert len(uris) == 1, f"Expected 1 output URI per sample, got {len(uris)}"
        df = pd.read_csv(urgap.UFile(uri=uris[0]).path)
        assert df.shape[0] == expected_rows, (
            f"{csv_name}: expected {expected_rows} rows, got {df.shape[0]}"
        )
        assert (df["value"] > 5).all(), f"{csv_name}: some rows have value <= 5"

        filter_output_files.append(output_uri_file)

    # ------------------------------------------------------------------
    # Step 2: FilterTabularToCSV -- multi-input merge (simulates fan-in)
    #
    # All 3 per-sample outputs are passed via --input_uris.  Urgap merges
    # them (pd.concat) and re-applies the query.  Since the inputs are
    # already filtered, the query is idempotent: all 5 rows are retained.
    # ------------------------------------------------------------------
    merge_output_file = tmp_path / "merge_output_uris.txt"
    exit_code = run_unode(
        input_uri_files=filter_output_files,  # 3 URI files -> merged by read_uri_files
        output_uri_file=merge_output_file,
        unode="FilterTabularToCSV:1.0.0",
        config_path=config_file,
    )
    assert exit_code == 0, "Merge (FilterTabularToCSV fan-in) failed"
    assert merge_output_file.exists()

    merge_uris = read_uri_file(merge_output_file)
    assert len(merge_uris) == 1, f"Expected 1 merged CSV URI, got {len(merge_uris)}"

    df_merged = pd.read_csv(urgap.UFile(uri=merge_uris[0]).path)
    assert df_merged.shape == (EXPECTED_CONCAT_ROWS, 3), (
        f"Merge shape mismatch: expected ({EXPECTED_CONCAT_ROWS}, 3), "
        f"got {df_merged.shape}"
    )
    assert df_merged["value"].sum() == EXPECTED_VALUE_SUM, (
        f"Merge value sum mismatch: expected {EXPECTED_VALUE_SUM}, "
        f"got {df_merged['value'].sum()}"
    )
    assert list(df_merged.columns) == ["id", "value", "name"], (
        f"Unexpected columns: {list(df_merged.columns)}"
    )

    # ------------------------------------------------------------------
    # Step 3: CompressToZip -- compress the merged CSV
    # ------------------------------------------------------------------
    zip_output_file = tmp_path / "zip_output_uris.txt"
    exit_code = run_unode(
        input_uri_files=[merge_output_file],
        output_uri_file=zip_output_file,
        unode="CompressToZip:1.0.0",
        config_path=config_file,
    )
    assert exit_code == 0, "CompressToZip failed"
    assert zip_output_file.exists()

    zip_uris = read_uri_file(zip_output_file)
    assert len(zip_uris) >= 1, "No ZIP output URIs written"
    assert any(
        ".zip" in uri or urgap.uftypes.compression.ZIP in uri for uri in zip_uris
    ), f"Expected a ZIP URI, got: {zip_uris}"
