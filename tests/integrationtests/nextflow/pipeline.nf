#!/usr/bin/env nextflow

/*
 * Urgap-Nextflow integration test pipeline.
 *
 * Pipeline: 3 toy CSVs -> FilterTabularToCSV (per sample) -> FilterTabularToCSV (concat) -> CompressToZip
 *
 * Design:
 *   Nextflow owns all orchestration and parallelism.
 *   Urgap is invoked once per process as a Python subprocess.
 *   All data flows between processes via plain text files of urgap URIs.
 *
 *
 * Fan-out (FILTER_CSV):
 *   One channel item per sample -> one process per sample (parallel).
 *   All outputs are tagged with key "all" so groupTuple() can collect them.
 *
 * Fan-in (MERGE_FILTERED):
 *   groupTuple() yields a single item containing a LIST of URI files.
 *   FilterTabularToCSV receives all URI files via --input_uris and merges
 *   them before processing.
 *
 * Usage (called by pytest):
 *   nextflow run pipeline.nf \
 *       --samplesheet /path/to/samplesheet.csv \
 *       --config /path/to/pipeline_config.json \
 *       --outdir /path/to/results
 */

nextflow.enable.dsl = 2

// ============================================================================
// Parameters
// ============================================================================

params.samplesheet = null
params.config      = null
params.outdir      = 'results'

// ============================================================================
// Processes
// ============================================================================

process FILTER_CSV {
    tag "${sample_id}"
    label 'process_low'

    input:
    tuple val(sample_id), path(input_uris)
    path  config_json

    output:
    // Use a distinct suffix (_filtered_uris.txt) so the output filename can
    // never collide with the staged input symlink (${sample_id}_uris.txt).
    // Without this, Python's file write follows the symlink and overwrites
    // the original URI file in tmp_path, corrupting run-2 inputs.
    tuple val("all"), path("${sample_id}_filtered_uris.txt"), emit: uris

    script:
    """
    python -m urgap.uhelpers.nextflow \\
        --unode 'FilterTabularToCSV:1.0.0' \\
        --input_uris ${input_uris} \\
        --output_uris ${sample_id}_filtered_uris.txt \\
        --config ${config_json}
    """
}


process MERGE_FILTERED {
    tag "${group_id}"
    label 'process_low'

    input:
    tuple val(group_id), path(input_uris)   // input_uris is a LIST after groupTuple()
    path  config_json

    output:
    tuple val(group_id), path("output_uris.txt"), emit: uris

    script:
    """
    python -m urgap.uhelpers.nextflow \\
        --unode 'FilterTabularToCSV:1.0.0' \\
        --input_uris ${input_uris} \\
        --output_uris output_uris.txt \\
        --config ${config_json}
    """
}


process COMPRESS_ZIP {
    tag "${group_id}"
    label 'process_low'

    publishDir params.outdir, mode: 'copy'

    input:
    tuple val(group_id), path(input_uris)
    path  config_json

    output:
    tuple val(group_id), path("output_uris.txt"), emit: uris

    script:
    """
    python -m urgap.uhelpers.nextflow \\
        --unode 'CompressToZip:1.0.0' \\
        --input_uris ${input_uris} \\
        --output_uris output_uris.txt \\
        --config ${config_json}
    """
}

// ============================================================================
// Workflow
// ============================================================================

workflow {
    if (!params.samplesheet) {
        error "Please provide --samplesheet (CSV with columns: sample_id, uri_file)"
    }
    if (!params.config) {
        error "Please provide --config (path to urgap pipeline config JSON)"
    }

    samples_ch = Channel
        .fromPath(params.samplesheet)
        .splitCsv(header: true)
        .map { row -> tuple(row.sample_id, file(row.uri_file)) }

    config_ch = Channel.value(file(params.config))

    //   Channel: [(sample_a, uris_a.txt), (sample_b, uris_b.txt), (sample_c, uris_c.txt)]
    FILTER_CSV(samples_ch, config_ch)

    //   Channel: [("all", [out_a.txt, out_b.txt, out_c.txt])]  <- single item
    FILTER_CSV.out.uris
        | groupTuple()
        | set { grouped_ch }

    MERGE_FILTERED(grouped_ch, config_ch)

    COMPRESS_ZIP(MERGE_FILTERED.out.uris, config_ch)
}
