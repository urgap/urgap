"""Ribosome profiling codon metrics."""

import argparse
import csv
import itertools
import multiprocessing
import re
import tempfile

from collections import defaultdict
from contextlib import ExitStack, suppress
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from pandas.api.types import CategoricalDtype
from scipy.signal import find_peaks
from tqdm import tqdm

multiprocessing.set_start_method("fork", force=True)


CODONS = {
    "AAA": "Lys",
    "AAC": "Asn",
    "AAG": "Lys",
    "AAT": "Asn",
    "ACA": "Thr",
    "ACC": "Thr",
    "ACG": "Thr",
    "ACT": "Thr",
    "AGA": "Arg",
    "AGC": "Ser",
    "AGG": "Arg",
    "AGT": "Ser",
    "ATA": "Ile",
    "ATC": "Ile",
    "ATG": "Met",
    "ATT": "Ile",
    "CAA": "Gln",
    "CAC": "His",
    "CAG": "Gln",
    "CAT": "His",
    "CCA": "Pro",
    "CCC": "Pro",
    "CCG": "Pro",
    "CCT": "Pro",
    "CGA": "Arg",
    "CGC": "Arg",
    "CGG": "Arg",
    "CGT": "Arg",
    "CTA": "Leu",
    "CTC": "Leu",
    "CTG": "Leu",
    "CTT": "Leu",
    "GAA": "Glu",
    "GAC": "Asp",
    "GAG": "Glu",
    "GAT": "Asp",
    "GCA": "Ala",
    "GCC": "Ala",
    "GCG": "Ala",
    "GCT": "Ala",
    "GGA": "Gly",
    "GGC": "Gly",
    "GGG": "Gly",
    "GGT": "Gly",
    "GTA": "Val",
    "GTC": "Val",
    "GTG": "Val",
    "GTT": "Val",
    "TAA": "STOP",
    "TAC": "Tyr",
    "TAG": "STOP",
    "TAT": "Tyr",
    "TCA": "Ser",
    "TCC": "Ser",
    "TCG": "Ser",
    "TCT": "Ser",
    "TGA": "STOP",
    "TGC": "Cys",
    "TGG": "Trp",
    "TGT": "Cys",
    "TTA": "Leu",
    "TTC": "Phe",
    "TTG": "Leu",
    "TTT": "Phe",
}
CODON_CATS = CategoricalDtype(categories=CODONS.keys(), ordered=True)


def parse_fasta(fasta_file: str | Path, relevant_transcripts: set) -> dict:
    """Parse a fasta file.

    Args:
        fasta_file (str or Path): path to fasta file
        relevant_transcripts (set): set of transcript identifiers to filter by

    Returns:
        protein_dict (dict of str: str): dict with protein identifiers as keys and
                                         respective sequences as values
    """
    protein_dict = defaultdict(list)
    with Path(fasta_file).open() as fasta:
        chunks = fasta.read().split("\n>")
    for chunk in chunks:
        idseq_split = chunk.split("\n")
        transcript_id = idseq_split[0].lstrip(">").split("|")[0].split("_")[0]
        if transcript_id in relevant_transcripts:
            protein_dict[transcript_id].append("".join(idseq_split[1:]))
    return protein_dict


def _process_chromosome_strand(chunk: tuple) -> tuple:
    """Multiprocess executor for get_cds_from_gtf.

    Args:
        chunk (tuple): ((<chr>, (<strand>), group dataframe)

    Returns:
        chr (str): chromosome
        strand (str): strand
        cds (list): CDS objects of transcripts on strand and chromosome
        drop_reasons (dict): number of dropped transcripts and reasons
    """
    (_chr, strand), df = chunk
    drop_reasons = defaultdict(int)
    transcripts = {}
    for transcript_id, grp in df.groupby("transcript_id"):
        features = grp["feature"].value_counts()
        try:
            if features["start_codon"] != 1:
                drop_reasons["Too many start codons"] += 1
                continue
            if features["stop_codon"] != 1:
                drop_reasons["Too many stop codons"] += 1
                continue
        except KeyError:
            drop_reasons["Missing start/stop codon"] += 1
            continue
        if len(grp) < 3:
            drop_reasons["Missing exons"] += 1
            continue
        if strand == "+":
            grp_sorted = grp.sort_values(["feature", "start"])
        else:
            grp_sorted = grp.sort_values(["feature", "end"], ascending=[True, False])

        start_codon = grp_sorted.iloc[-2][["start", "end"]].to_dict()
        stop_codon = grp_sorted.iloc[-1][["start", "end"]].to_dict()
        grp_sorted["len"] = ((grp_sorted["end"] - grp_sorted["start"]) + 1).cumsum()

        if strand == "+":
            try:
                start_codon_row = (
                    grp_sorted[:-2]
                    .query(
                        f"(`start` <= {start_codon['start']}) & ({start_codon['start']} <= `end`)",
                    )
                    .iloc[0]
                )
                stop_codon_row = (
                    grp_sorted[:-2]
                    .query(
                        f"(`start` <= {stop_codon['end']}) & ({stop_codon['end']} <= `end`)",
                    )
                    .iloc[0]
                )
            except IndexError:
                drop_reasons["Start/stop outside exon boundaries"] += 1
                continue
            offset_start_codon = start_codon_row["len"] - (
                start_codon_row["end"] - start_codon["start"] + 1
            )
            offset_stop_codon = stop_codon_row["len"] - (
                stop_codon_row["end"] - stop_codon["end"]
            )

        else:
            try:
                start_codon_row = (
                    grp_sorted[:-2]
                    .query(
                        f"(`start` <= {start_codon['end']}) & ({start_codon['end']} <= `end`)",
                    )
                    .iloc[0]
                )
                stop_codon_row = (
                    grp_sorted[:-2]
                    .query(
                        f"(`start` <= {stop_codon['start']}) & ({stop_codon['start']} <= `end`)",
                    )
                    .iloc[0]
                )
            except IndexError:
                drop_reasons["Start/stop outside exon boundaries"] += 1
                continue
            offset_start_codon = start_codon_row["len"] + (
                start_codon_row["start"] - start_codon["end"] - 1
            )
            offset_stop_codon = stop_codon_row["len"] + (
                stop_codon_row["start"] - stop_codon["start"]
            )

        transcripts[transcript_id] = (offset_start_codon, offset_stop_codon)

    return transcripts, drop_reasons


def get_cds_from_gtf(gtf_file: str, filter_tag: str | None, threads: int) -> tuple:
    """Read and process a GTF file to find all CDSs.

    CDSs are dropped if:
        - not member of the consensus CDS gene set
          (agreement between ENSEMBL, UCSC, NCBI, and HAVANA)
        - start or stop codons are separated from the other CDSs
        - too many/too few start or stop codons are found
        - the sum of the bases in all CDSs per transcript id is not divisible by three

    Args:
        gtf_file (str): path to gtf file
        filter_tag (str, None): regex expression to filter CDSs by (e.g. ccds tags)
        padding (int): number of nucleotides to pad 5'/3' of the CDS boundaries
               i.e. CDS are extended by this number of nucleotides
        threads (int): number of processes to use

    Returns:
        cds_map (dict): dict containing retained information about the coding sequences
                        {
                            cds[<chromosome>][<strand>]:
                                [<CodingSequence object>, <...>],
                            <...>
                        }
        drop_reasons (dict): reasons why transcripts were dropped
    """
    gtf = pd.read_csv(
        gtf_file,
        sep="\t",
        header=None,
        comment="#",
        names=[
            "chrom",
            "source",
            "feature",
            "start",
            "end",
            "score",
            "strand",
            "frame",
            "attributes",
        ],
    )
    gtf = gtf[gtf["feature"].isin(("start_codon", "stop_codon", "exon"))]
    gtf["transcript_id"] = gtf["attributes"].str.extract(
        r"(?<=transcript_id \")(.+?)(?=\")",
    )
    if filter_tag is not None:
        gtf["filter_tag"] = gtf["attributes"].str.contains(
            filter_tag,
            flags=re.IGNORECASE,
            regex=True,
        )
        gtf = gtf[gtf.groupby("transcript_id")["filter_tag"].transform("all")]
    gtf["gene"] = gtf["attributes"].str.extract(r"(?<=gene_name \")(.+?)(?=\")")
    gtf = gtf[["chrom", "feature", "start", "end", "strand", "transcript_id", "gene"]]
    gtf.loc[:, ["has_start", "has_stop"]] = False
    drop_reasons = defaultdict(int)
    transcripts = {}
    with multiprocessing.Pool(processes=threads) as pool:
        chunks = gtf.groupby(["chrom", "strand"])
        for result in tqdm(
            pool.imap_unordered(_process_chromosome_strand, chunks),
            total=chunks.ngroups,
        ):
            sub_transcripts, sub_drop_reasons = result
            transcripts.update(sub_transcripts)
            for key, value in sub_drop_reasons.items():
                drop_reasons[key] += value
        pool.terminate()
    return transcripts, drop_reasons


def _init_process_sam_line(
    transcripts: dict,
    min_length: int,
    max_length: int,
    padding: int,
) -> None:
    """Initialize multiprocess executor for map_reads_to_cds.

    Args:
        transcripts (dict): dict of transcript information
        min_length (int): length of the shortest reads to retain in nt
        max_length (int): length of the longest reads to retain in nt
        padding (int): number of nucleotides to pad the CDS boundaries
    """
    _process_sam_line.transcripts = transcripts
    _process_sam_line.min_length = min_length
    _process_sam_line.max_length = max_length
    _process_sam_line.padding = padding


def _process_sam_line(line: str) -> list:
    """Multiprocess executor for map_reads_to_cds.

    Computes reading frame and distance from both read end to both CDS boundaries.

    Args:
        line (str): single entry (i.e. line) of SAM file

    Returns:
        mapped_reads (list): list for dataframe construction of CDS-mappable reads
                             with metrics
    """
    if line.startswith("@"):
        return 0
    read_data = line.split("\t")
    strand = "+" if not (int(read_data[1]) & 16) else "-"
    transcript = read_data[2].split("|")[0].split("_")[0]
    seq = read_data[9]
    read_len = len(seq)
    if not _process_sam_line.min_length <= read_len <= _process_sam_line.max_length:
        return 1
    if strand == "+":
        start = int(read_data[3]) - 1
        end = start + len(seq) - 1
    else:
        end = int(read_data[3]) - 1
        start = end + len(seq) - 1

    try:
        transcript_start, transcript_stop = _process_sam_line.transcripts[transcript]
    except KeyError:
        return 2
    five_to_start = start - transcript_start
    five_to_end = start - transcript_stop
    three_to_start = end - transcript_start
    three_to_end = end - transcript_stop
    reading_frame = five_to_start % 3
    has_start = (
        (start - _process_sam_line.padding)
        <= transcript_start
        <= (end + _process_sam_line.padding)
    )
    has_stop = (
        (start - _process_sam_line.padding)
        <= transcript_stop
        <= (end + _process_sam_line.padding)
    )

    return [
        transcript,
        strand,
        np.int32(start),
        np.int32(end),
        seq,
        read_len,
        np.uint8(reading_frame),
        np.int32(five_to_start),
        np.int32(five_to_end),
        np.int32(three_to_start),
        np.int32(three_to_end),
        has_start,
        has_stop,
    ]


def map_reads_to_cds(
    sam_file: str,
    transcripts: dict,
    threads: int,
    min_length: int,
    max_length: int,
    padding: int,
) -> pd.DataFrame:
    """Map reads from a SAM file to CDSs.

    Determine the offset in nucleotides from the 5' end of the read to the start codon,
    from the 3' end of the read to the stop codon, and the reading frame with
    respect to the start codon.    Args:
        sam_file (str): path to sam file
        transcripts (dict): dict of transcript information
        threads (int): number of processes to use for multiprocessing
        min_length (int): length of the shortest reads to retain in nt
        max_length (int): length of the longest reads to retain in nt
        padding (int): number of nucleotides to pad the CDS boundaries

    Returns:
        mapped_reads (pd.DataFrame): CDS-mapped reads
    """
    failed_mapping = defaultdict(int)
    mapped_reads_per_len_rf = defaultdict(int)
    tmp_dir = tempfile.TemporaryDirectory()
    with ExitStack() as stack:
        len_rf_combos = itertools.product(range(min_length, max_length + 1), (0, 1, 2))
        writers = {}
        for len_rf in len_rf_combos:
            file_path = Path(tmp_dir.name) / "_".join(map(str, len_rf))
            file = file_path.open("w")
            stack.push(file)
            writers[len_rf] = csv.writer(file)
            writers[len_rf].writerow(
                (
                    "transcript_id",
                    "strand",
                    "start",
                    "end",
                    "seq",
                    "read_len",
                    "reading_frame",
                    "d_five_to_start",
                    "d_five_to_stop",
                    "d_three_to_start",
                    "d_three_to_stop",
                    "has_start",
                    "has_stop",
                ),
            )
        total_lines = 0
        with Path(sam_file).open() as sam:
            for _line in sam:
                total_lines += 1

        def _read_sam(sam_file: str) -> object:
            with Path(sam_file).open() as sam:
                for line in sam:
                    yield line.strip()

        with multiprocessing.Pool(
            processes=threads,
            initializer=_init_process_sam_line,
            initargs=(transcripts, min_length, max_length, padding),
            maxtasksperchild=20,
        ) as pool:
            for line_mapped_reads in tqdm(
                pool.imap_unordered(
                    _process_sam_line,
                    _read_sam(sam_file),
                    chunksize=1000,
                ),
                total=total_lines,
            ):
                if isinstance(line_mapped_reads, int):
                    failed_mapping[line_mapped_reads] += 1
                else:
                    len_rf = (line_mapped_reads[5], line_mapped_reads[6])
                    writers[len_rf].writerow(line_mapped_reads)
                    mapped_reads_per_len_rf[len_rf] += 1
            pool.terminate()

    total_mapped = sum(mapped_reads_per_len_rf.values())
    dropped_percentage = 0.0
    drop_threshold = 1.0
    for len_rf, n_mapped in mapped_reads_per_len_rf.items():
        sub_dropped_percentage = n_mapped / total_mapped * 100
        if sub_dropped_percentage < drop_threshold:
            (Path(tmp_dir.name) / "_".join(map(str, len_rf))).unlink()
            dropped_percentage += sub_dropped_percentage
    return tmp_dir


def determine_overhang_position(
    df: pd.DataFrame,
    n_five_prime_codons: int,
    n_three_prime_codons: int,
    fasta_dict: dict,
) -> pd.DataFrame:
    """Determine the offsets from the 5' read end to the first base of the ribosomal P-site.

    Args:
        df (pd.DataFrame): CDS-mapped reads
        n_five_prime_codons (int): number of codons to provide on the 5' side of the RPFs
        n_three_prime_codons (int): number of codons to provide on the 3' side of the RPFs
        fasta_dict (dict): dict with reference sequence to extend sequence end with


    Returns:
        positioned_reads (pd.DataFrame): input dataframe with new columns for
                                         positioned codons around the ribosome
    """
    read_length = df.iloc[0]["read_len"]

    distance_counts_five_start = (
        df[
            (df["d_five_to_start"] >= -20)
            & (df["d_five_to_start"] <= 0)
            & df["has_start"]
        ]["d_five_to_start"]
        .value_counts()
        .sort_index()
    )
    peaks_five_start = find_peaks(
        distance_counts_five_start.to_list(),
        height=0.2 * distance_counts_five_start.sum(),
    )[0]
    overhang_five_start = distance_counts_five_start.iloc[
        peaks_five_start
    ].index.to_list()

    distance_counts_three_start = (
        df[
            (df["d_three_to_start"] <= 25)
            & (df["d_three_to_start"] >= 0)
            & df["has_start"]
        ]["d_three_to_start"]
        .value_counts()
        .sort_index()
    )
    peaks_three_start = find_peaks(
        distance_counts_three_start.to_list(),
        height=0.2 * distance_counts_three_start.sum(),
    )[0]
    overhang_three_start = distance_counts_three_start.iloc[
        peaks_three_start
    ].index.to_list()

    possible_five_combinations = []
    if (len(overhang_five_start) == 1) or (len(overhang_three_start) == 1):
        for five_overhang, three_overhang in list(
            itertools.product(overhang_five_start, overhang_three_start),
        ):
            if (abs(five_overhang) + abs(three_overhang) + 1) == read_length:
                possible_five_combinations.append(
                    (abs(five_overhang), abs(three_overhang)),
                )
    if len(possible_five_combinations) == 1:
        five_prime_to_p_site = possible_five_combinations[0][0]
        skip_bases_five_prime = five_prime_to_p_site % 3
        nth_codon_is_p_site = five_prime_to_p_site // 3
        codons = determine_ribosome_position(
            df=df,
            skip_bases_five_prime=skip_bases_five_prime,
            ith_codon_is_p_site=nth_codon_is_p_site,
            n_five_prime_codons=n_five_prime_codons,
            n_three_prime_codons=n_three_prime_codons,
            fasta_dict=fasta_dict,
        )
        return pd.concat([df, codons], axis=1)
    return None


def _get_codons_index_safe(seq: list, start: int, stop: int) -> list:
    """Get codons from a sequence safely."""
    codons = []
    for i in range(start, stop - 2, 3):
        if (i < 0) or (i + 2 >= len(seq)):
            codons.append(None)
        else:
            codons.append(seq[i : i + 3])
    return codons


def determine_ribosome_position(
    df: pd.DataFrame,
    skip_bases_five_prime: int,
    ith_codon_is_p_site: int,
    n_five_prime_codons: int,
    n_three_prime_codons: int,
    fasta_dict: dict,
) -> pd.DataFrame:
    """Determine the position of the ribosome on a given read and extract codons.

    Args:
        df (pd.DataFrame): CDS-mapped reads
        skip_bases_five_prime (int): number of bases to be skipped on the 5' read end
                                     as they do not constitute complete codons
        ith_codon_is_p_site (int): i-th complete codon is the ribosomal P-site
        n_five_prime_codons (int): number of codons to provide on the 5' side of the RPFs
        n_three_prime_codons (int): number of codons to provide on the 3' side of the RPFs
        fasta_dict (dict): dict with reference sequence to extend sequence end with

    Returns:
        codons (pd.DataFrame): positioned codons within read
    """
    p_site_position = df["start"] + skip_bases_five_prime + (ith_codon_is_p_site * 3)
    df["required_start_position"] = p_site_position - (n_five_prime_codons * 3)
    df["required_end_position"] = p_site_position + 3 + (n_three_prime_codons * 3)
    codons = df.apply(
        lambda row: _get_codons_index_safe(
            fasta_dict[row["transcript_id"]][0],
            row["required_start_position"],
            row["required_end_position"],
        ),
        axis=1,
    )
    codons = pd.DataFrame(codon for codon in codons).astype(CODON_CATS)

    columns = [f"-{i}_codon" for i in range(n_five_prime_codons - 1, 0, -1)]
    columns += ["E_site", "P_site", "A_site"]
    columns += [
        f"{i}_codon" for i in range(1, len(codons.columns) - n_five_prime_codons - 1)
    ]
    codons.columns = columns
    codons.index = df.index
    return codons


def plot_read_position_distribution(
    mapped_reads: pd.DataFrame,
    query_string: str | None = None,
) -> str:
    """Plot frequencies of read positions within CDSs.

    Args:
        mapped_reads (pd.DataFrame): CDS-mapped reads
        query_string (str, optional): pandas query string to subset mapped_reads df

    Returns:
        (str): plot in HTML div string representation
    """
    title = "Frequency of relative position of read midpoints within CDSs"
    if query_string is not None:
        mapped_reads = mapped_reads.query(expr=query_string)
        title += f" ({query_string})"
    read_midpoint = (
        mapped_reads["d_five_to_start"] + (mapped_reads["read_len"] / 2)
    ).round(decimals=0)
    cds_length = (
        mapped_reads["d_five_to_start"]
        - mapped_reads["d_three_to_stop"]
        + mapped_reads["read_len"]
    )
    mapped_reads.loc[:, "Relative read position"] = read_midpoint / cds_length
    min_pos = mapped_reads["Relative read position"].min()
    max_pos = mapped_reads["Relative read position"].max()
    read_len_histograms = {
        "Relative read position": [],
        "Frequency": [],
        "Read length": [],
    }
    for name, grp in mapped_reads.groupby("read_len"):
        counts, bins = np.histogram(
            grp["Relative read position"],
            bins=1000,
            range=(min_pos, max_pos),
        )
        read_len_histograms["Frequency"] += counts.tolist()
        read_len_histograms["Relative read position"] += (
            bins[:-1] + np.diff(bins) / 2
        ).tolist()
        read_len_histograms["Read length"] += len(counts) * [name]

    plt_df = pd.DataFrame(read_len_histograms)
    fig = px.bar(
        data_frame=plt_df,
        x="Relative read position",
        y="Frequency",
        facet_row="Read length",
        template="simple_white",
        title=title,
        category_orders={
            "Read length": sorted(plt_df["Read length"].unique().tolist()),
        },
    )
    fig.update_yaxes(autorange=True)
    return fig.to_html(full_html=False, include_plotlyjs=True)


def plot_read_length_distribution(mapped_reads: pd.DataFrame) -> str:
    """Plot read length distribution with reading frame info.

    Args:
        mapped_reads (pd.DataFrame): CDS-mapped reads

    Returns:
        (str): plot in HTML div string representation
    """
    len_dist_df = (
        mapped_reads.groupby(["read_len", "reading_frame", "source"])
        .agg("size")
        .reset_index()
    )
    len_dist_df.rename(
        columns={
            "read_len": "Read length",
            "reading_frame": "Reading frame",
            0: "Reads",
        },
    )
    len_dist_df["Reading frame"] = len_dist_df["Reading frame"].astype(str)
    len_dist_df = len_dist_df.groupby(["Read length", "Reading frame"]).agg(
        {"Reads": ["median", "min", "max"]},
    )
    len_dist_df.columns = ["Median number of reads", "Min", "Max"]
    len_dist_df = len_dist_df.reset_index()
    len_dist_df["Max"] -= len_dist_df["Median number of reads"]
    len_dist_df["Min"] = len_dist_df["Median number of reads"] - len_dist_df["Min"]
    fig = px.bar(
        data_frame=len_dist_df,
        x="Read length",
        y="Median number of reads",
        error_y="Max",
        error_y_minus="Min",
        color="Reading frame",
        color_discrete_map={"0": "#b2df8a", "1": "#a6cee3", "2": "#1f78b4"},
        barmode="group",
        template="simple_white",
        title="Read length and reading frame distribution",
        category_orders={
            "Read length": sorted(len_dist_df["Read length"].unique().tolist()),
        },
    )
    fig.update_yaxes(autorange=True)
    return fig.to_html(full_html=False, include_plotlyjs=False)


def plot_codon_occupancy(mapped_reads: pd.DataFrame) -> str:
    """Plot codon occupancy across all SAM files.

    Args:
        mapped_reads (pd.DataFrame): CDS-mapped reads

    Returns:
        (str): plot in HTML div string representation
    """
    occupied_codons = mapped_reads.groupby("source").agg(
        dict.fromkeys(["E_site", "P_site", "A_site"], "value_counts"),
    )
    occupied_codons = occupied_codons.reset_index(names=["source", "Codon"])
    occupied_codons["Amino acid"] = occupied_codons["Codon"].map(CODONS)
    plt_df = pd.melt(
        occupied_codons,
        id_vars=["source", "Codon", "Amino acid"],
        value_vars=["E_site", "P_site", "A_site"],
        var_name="Ribosome site",
        value_name="Frequency",
    )
    plt_df = plt_df.groupby(
        ["Codon", "Amino acid", "Ribosome site"],
        observed=True,
    ).agg({"Frequency": ["median", "min", "max"]})
    plt_df.columns = ["Median frequency", "Min", "Max"]
    plt_df = plt_df.reset_index()
    plt_df["Max"] -= plt_df["Median frequency"]
    plt_df["Min"] = plt_df["Median frequency"] - plt_df["Min"]
    plt_df.loc[:, ["Median frequency", "Min", "Max"]] = plt_df[
        ["Median frequency", "Min", "Max"]
    ].fillna(0.0)
    color_map = {"E_site": "#6a3d9a", "P_site: A_site": "#ffb900"}  # 00a0b0",
    fig = go.Figure()
    for name, grp_data in plt_df.groupby("Ribosome site"):
        grp_sorted = grp_data.sort_values(["Amino acid", "Codon"])
        fig.add_trace(
            go.Bar(
                x=[grp_sorted["Amino acid"].to_list(), grp_sorted["Codon"].to_list()],
                y=grp_sorted["Median frequency"].to_list(),
                name=name,
                marker_color=color_map.get(name),
                error_y={
                    "type": "data",
                    "symmetric": False,
                    "array": grp_sorted["Max"].to_list(),
                    "arrayminus": grp_sorted["Min"].to_list(),
                },
            ),
        )

    fig.update_layout(title_text="Codon occupancy")
    fig.update_yaxes(autorange=True)
    return fig.to_html(full_html=False, include_plotlyjs=False)


def plot_cds_boundaries(
    mapped_reads: pd.DataFrame,
    region_nt: int,
    from_five_prime: bool = True,
) -> str:
    """Plot read counts around the start and stop codon.

    Args:
        mapped_reads (pd.DataFrame): CDS-mapped reads
        region_nt (int): number of nucleotides to show on each side of each codon
        from_five_prime (bool): if True uses distances from 5' end of the read (else 3')

    Returns:
        (str): plot in HTML div string representation
    """
    read_end = "five" if from_five_prime is True else "three"
    start_col = f"d_{read_end}_to_start"
    stop_col = f"d_{read_end}_to_stop"
    plt_df_start = mapped_reads[
        (abs(mapped_reads[start_col]) <= region_nt) & (mapped_reads["has_start"])
    ]
    plt_df_start = (
        plt_df_start.groupby(["read_len", "reading_frame", start_col, "source"])
        .agg("size")
        .reset_index()
    )
    plt_df_stop = mapped_reads[
        (abs(mapped_reads[stop_col]) <= region_nt) & (mapped_reads["has_stop"])
    ]
    plt_df_stop = (
        plt_df_stop.groupby(["read_len", "reading_frame", stop_col, "source"])
        .agg("size")
        .reset_index()
    )
    plt_df = pd.concat([plt_df_start, plt_df_stop], axis=0, ignore_index=True)
    plt_df["distance_to_codon"] = plt_df[start_col].fillna(plt_df[stop_col])
    plt_df["codon"] = (
        plt_df[start_col].isna().apply(lambda x: "start" if x is False else "stop")
    )
    plt_df = plt_df.drop(columns=[start_col, stop_col])
    plt_df["reading_frame"] = plt_df["reading_frame"].astype(str)
    plt_df.rename(
        columns={
            0: "Reads",
            "distance_to_codon": "Codon offset in nt",
            "reading_frame": "Reading frame",
            "codon": "Codon",
            "read_len": "Read length",
        },
    )
    read_end = "5" if read_end == "five" else "3"
    plt_df = plt_df.groupby(
        ["Read length", "Reading frame", "Codon", "Codon offset in nt"],
    ).agg({"Reads": ["median", "min", "max"]})
    plt_df.columns = ["Median number of reads", "Min", "Max"]
    plt_df = plt_df.reset_index()
    plt_df["Max"] -= plt_df["Median number of reads"]
    plt_df["Min"] = plt_df["Median number of reads"] - plt_df["Min"]
    fig = px.bar(
        plt_df,
        x="Codon offset in nt",
        y="Median number of reads",
        error_y="Max",
        error_y_minus="Min",
        range_x=(-region_nt, region_nt),
        color="Reading frame",
        facet_row="Read length",
        facet_col="Codon",
        color_discrete_map={"0": "#b2df8a", "1": "#a6cee3", "2": "#1f78b4"},
        template="simple_white",
        title=f"CDS boundary offsets from {read_end}' read end",
    )
    tickvals = list(range((-region_nt // 3) * 3 + 3, (region_nt // 3) * 3 + 3, 3))
    fig.update_xaxes(tickmode="array", tickvals=tickvals)
    start_stop_background = ((-0.5, 2.5), (-2.5, 0.5))
    for col, (x_start, x_stop) in enumerate(start_stop_background):
        with suppress(IndexError):
            fig.add_vrect(
                x0=x_start,
                x1=x_stop,
                line_width=0,
                fillcolor="red",
                opacity=0.2,
                col=col + 1,
            )
    fig.update_yaxes(autorange=True)
    return fig.to_html(full_html=False, include_plotlyjs=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-g",
        dest="gtf",
        help="path to gtf file",
    )
    parser.add_argument(
        "-s",
        dest="sam",
        help="paths to sam files",
    )
    parser.add_argument(
        "-f",
        dest="fasta",
        help="path to fasta files",
    )
    parser.add_argument(
        "-m",
        dest="meta",
        type=str,
        default=None,
        help="path to metadata csv",
    )
    parser.add_argument(
        "-r",
        "--region",
        dest="reg",
        type=int,
        help="regions around start and stop codons to consider while mapping",
    )
    parser.add_argument(
        "-t",
        "--threads",
        dest="cpu",
        type=int,
        help="number of threads",
    )
    parser.add_argument(
        "--min",
        dest="min",
        type=int,
        help="min read length",
    )
    parser.add_argument(
        "--max",
        dest="max",
        type=int,
        help="max read length",
    )
    parser.add_argument(
        "--pad",
        dest="padding",
        default=0,
        type=int,
        help="CDS boundary padding (extension)",
    )
    parser.add_argument(
        "--extend-three-prime-codons",
        dest="n_three_prime_codons",
        default=3,
        type=int,
        help="number of codons to extend three prime of RPFs",
    )
    parser.add_argument(
        "--extend-five-prime-codons",
        dest="n_five_prime_codons",
        default=3,
        type=int,
        help="number of codons to extend five prime of RPFs",
    )
    parser.add_argument(
        "-o",
        "--out",
        dest="output",
        help="output directory",
    )
    parser.add_argument(
        "--filter",
        dest="filter_tag",
        default=None,
        type=str,
        help="Regex expression which needs to be included in CDS attributes",
    )
    args = parser.parse_args()
    if args.meta is not None:
        metadata_df = pd.read_csv(args.meta)
        metadata = metadata_df.set_index("object_identifier").to_dict(orient="index")
    sam_files = args.sam.split(",")
    transcripts, drop_reasons = get_cds_from_gtf(
        gtf_file=args.gtf,
        filter_tag=args.filter_tag,
        threads=args.cpu,
    )
    read_dirs = []
    for sam in sam_files:
        tmp_dir = map_reads_to_cds(
            sam_file=sam,
            transcripts=transcripts,
            threads=args.cpu,
            min_length=args.min,
            max_length=args.max,
            padding=args.padding,
        )
        read_dirs.append(tmp_dir)
    mapped_reads = []
    fasta_dict = None
    if args.fasta is not None:
        fasta_dict = parse_fasta(
            fasta_file=args.fasta,
            relevant_transcripts=transcripts.keys(),
        )
    for i, tmp_dir in enumerate(read_dirs):
        positioned_reads = []
        for file in Path.glob(str(Path(tmp_dir.name) / "*")):
            df = pd.read_csv(
                file,
                dtype={
                    "chr": "category",
                    "strand": "category",
                    "start": np.int32,
                    "end": np.int32,
                    "seq": str,
                    "gene": str,
                    "read_len": np.uint8,
                    "reading_frame": np.uint8,
                    "d_five_to_start": np.int32,
                    "d_five_to_stop": np.int32,
                    "d_three_to_start": np.int32,
                    "d_three_to_stop": np.int32,
                    "has_start": bool,
                    "has_stop": bool,
                },
            )
            if len(df) == 0:
                continue
            positioned_reads.append(
                determine_overhang_position(
                    df=df,
                    n_five_prime_codons=args.n_five_prime_codons,
                    n_three_prime_codons=args.n_three_prime_codons,
                    fasta_dict=fasta_dict,
                ),
            )
        positioned_reads = pd.concat(positioned_reads, axis=0, join="outer")
        positioned_reads = positioned_reads[~positioned_reads["seq"].str.contains("N")]
        if args.meta is not None:
            sam_file_name = Path(sam_files[i]).name
            if sam_file_name not in metadata:
                sam_file_name = Path(sam_files[i]).parent.name + "/" + sam_file_name
            positioned_reads["source"] = metadata[sam_file_name]["filename"]
            positioned_reads["condition"] = metadata[sam_file_name]["condition"]
            positioned_reads["bio_rep"] = metadata[sam_file_name]["bio_rep"]
            positioned_reads["tech_rep"] = metadata[sam_file_name]["tech_rep"]
        else:
            positioned_reads["source"] = sam_files[i]
        mapped_reads.append(positioned_reads)
        del positioned_reads
        tmp_dir.cleanup()
    mapped_reads = pd.concat(mapped_reads, copy=False, axis=0, join="outer")
    if args.meta is not None:
        mapped_reads.loc[:, "condition"] = mapped_reads["condition"].astype("category")
    mapped_reads.loc[:, "source"] = mapped_reads["source"].astype("category")
    mapped_reads = mapped_reads.reset_index(drop=True)
    mapped_reads.to_feather(str(Path(args.output) / "analysis.feather"))
    with (Path(args.output) / "plots.html").open("a") as plot_file:
        plot_file.write(
            plot_read_position_distribution(
                mapped_reads=mapped_reads,
            ),
        )
        plot_file.write(
            plot_read_length_distribution(
                mapped_reads=mapped_reads,
            ),
        )
        plot_file.write(
            plot_cds_boundaries(
                mapped_reads=mapped_reads,
                region_nt=args.reg,
                from_five_prime=True,
            ),
        )
        plot_file.write(
            plot_cds_boundaries(
                mapped_reads=mapped_reads,
                region_nt=args.reg,
                from_five_prime=False,
            ),
        )
        plot_file.write(
            plot_codon_occupancy(
                mapped_reads=mapped_reads,
            ),
        )
