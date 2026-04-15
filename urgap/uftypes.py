"""Collection of uftypes (i.e. filetypes) to be used with urgap workflow."""

import types

unknown = types.SimpleNamespace()
unknown.UNKNOWN = ".unknown"

# Proteomics====================================================================
proteomics = types.SimpleNamespace()
proteomics.ANY = "proteomics.ANY"
proteomics.THERMO_RAW = ".thermo.raw"
proteomics.BRUKER_D_TGZ = ".bruker_d.tgz"
proteomics.FASTA = ".protein.faa"
proteomics.MODS_XML = ".mods.xml"
proteomics.TMT_CORRECTION_FACTORS = ".tmt_correction_factors.json"

# Database Search Engines
proteomics.dbsearch = types.SimpleNamespace()
proteomics.dbsearch.ANY = "proteomics.dbsearch.ANY"
proteomics.dbsearch.COMET_MZID = ".comet.mzid"
proteomics.dbsearch.MASCOT_DAT = ".mascot.dat"
proteomics.dbsearch.MSAMANDA_CSV = ".msamanda.csv"
proteomics.dbsearch.MSFRAGGER_TSV = ".msfragger.tsv"
proteomics.dbsearch.MSGFPLUS_MZID = ".msgfplus.mzid"
proteomics.dbsearch.OMSSA_CSV = ".omssa.csv"
proteomics.dbsearch.XTANDEM_XML = ".xtandem.xml"
proteomics.dbsearch.DIANN_QUANT = ".diann.quant"
proteomics.dbsearch.DIANN_REPORT = ".diann_report.tsv"

# DIA-NN Libraries
proteomics.diannlibrary = types.SimpleNamespace()
proteomics.diannlibrary.ANY = "proteomics.diannlibrary.ANY"
proteomics.diannlibrary.DIANN_PREDICTED_LIBRARY = ".diann_predicted.speclib"
proteomics.diannlibrary.DIANN_EMPIRICIAL_LIBRARY = ".diann_emperical.speclib"

# De Novo Search Engines
proteomics.denovosearch = types.SimpleNamespace()
proteomics.denovosearch.NOVOR_CSV = ".novor.csv"


# Data Conversion
proteomics.converter = types.SimpleNamespace()
proteomics.converter.ANY = "proteomics.converter.ANY"
proteomics.converter.PYMZML_MGF = ".pymzml.mgf"
proteomics.converter.PYMZML_IDXGZ = ".pymzml_idx.gz"
proteomics.converter.PYIOHAT_CSV = ".pyiohat.csv"

# Validator
proteomics.validator = types.SimpleNamespace()
proteomics.validator.ANY = "proteomics.validator.ANY"
proteomics.validator.PERCOLATOR_CSV = ".percolator.csv"
proteomics.validator.PEPTIDEFOREST_CSV = ".peptideforest.csv"

# Quantification
proteomics.quantification = types.SimpleNamespace()
proteomics.quantification.ANY = "proteomics.quantification.ANY"
proteomics.quantification.FLASHLFQ_PSM_TSV = ".flashlfq_psms.tsv"
proteomics.quantification.FLASHLFQ_PEPTIDE_TSV = ".flashlfq_peptides.tsv"
proteomics.quantification.FLASHLFQ_PROTEIN_TSV = ".flashlfq_proteins.tsv"
proteomics.quantification.FLASHLFQ_BAYESFC_TSV = ".flashlfq_bayesFC.tsv"

# Reporter ion-based quantification
proteomics.quantification.reporter_ions = types.SimpleNamespace()
proteomics.quantification.reporter_ions.ANY = ".reporter_ions.ANY"
proteomics.quantification.reporter_ions.REPORTER_IONS = ".reporter_ions.csv"
proteomics.quantification.reporter_ions.ISO_CORRECTED_REPORTER_IONS = (
    ".iso_corrected_reporter_ions.csv"
)
proteomics.quantification.reporter_ions.S2I_CORRECTED_REPORTER_IONS = (
    ".s2i_corrected_reporter_ions.csv"
)

# Quality Control
proteomics.qc = types.SimpleNamespace()
proteomics.qc.ANY = "proteomics.qc.ANY"
proteomics.qc.OFFSET_CSV = ".offset.csv"

# Statistics====================================================================
stats = types.SimpleNamespace()
stats.ANY = "stats.ANY"
stats.PWSTATS_CSV = ".pwstats.csv"
stats.UMAP_CSV = ".umap.csv"

# Plotter=======================================================================
plotter = types.SimpleNamespace()
plotter.ANY = "plotter.ANY"
plotter.VOLCANO_PDF = ".volcano.pdf"
plotter.UMAP_PDF = ".umap.pdf"
plotter.VENN_RESULTS_CSV = ".venn_results.csv"
plotter.VENN_RESULTS_SVG = ".venn_results.svg"
plotter.UMAP_PDF = ".umap.pdf"
plotter.PLOTLY_HTML = ".plotly.html"

# Filetype =======================================================================
any = types.SimpleNamespace()
any.ANY = "any.ANY"
any.CSV = ".any.csv"
any.DAT = ".any.dat"
any.FAA = ".any.faa"
any.MGF = ".any.mgf"
any.MZID = ".any.mzid"
any.MZML = ".any.mzml"
any.PDF = ".any.pdf"
any.RAW = ".any.raw"
any.SVG = ".any.svg"
any.TSV = ".any.tsv"
any.XML = ".any.xml"
any.TABULAR = ".any.tabular"
any.TXT = ".any.txt"
any.PARQUET = ".any.parquet"
any.XLSX = ".any.xlsx"

# Metabolomics==================================================================
mx = types.SimpleNamespace()
mx.REF_MASS_CSV = ".ref_mass.csv"
mx.ADDUCTS_CSV = ".adducts.csv"
mx.MASS_SHIFT_CSV = ".mass_shift.csv"
mx.CAL_MASS_CSV = ".cal_mass.csv"
mx.QC_HTML = ".qc.html"
mx.QC_SVG = ".qc.svg"
mx.QC_PDF = ".qc.pdf"
mx.BEST_ION_MET_CSV = ".best_ion_met.csv"
mx.ANNOTATION_MET_HDF5 = ".annotation_met.hdf5"
mx.ANNOTATION_MET_EXCLUSION_CSV = ".annotation_met_exc.csv"
mx.INSTRUMENT_RESOLUTION_CSV = ".instr_res.csv"
mx.METADATA_MAP_JSON = ".metadata_map.json"
mx.METADATA_XLSX = ".metadata.xlsx"
mx.PIPELINE_EXP_DESIGN = ".pipeline_exp_design.csv"

# Transcriptomics===============================================================
transcriptomics = types.SimpleNamespace()
transcriptomics.FASTA = ".transcriptomics.fa"
transcriptomics.reads = types.SimpleNamespace()
transcriptomics.reads.ANY = "transcriptomics.reads.ANY"
transcriptomics.reads.FASTQ_GZ = ".transcriptomics_fastq.gz"
transcriptomics.reads.SAM = ".transcriptomics.sam"
transcriptomics.reads.BAM = ".transcriptomics.bam"
transcriptomics.BAM_INDEX = ".transcriptomics.bai"
transcriptomics.GTF = ".transcriptomics.gtf"
transcriptomics.READS = ".transcriptomics.reads"
transcriptomics.CODON_METRICS_PLOT_HTML = ".codon_metrics.html"
transcriptomics.RIBOSOME_PROFILING_FEATHER = ".rp.feather"
transcriptomics.CUTADAPT_STATS_JSON = ".cutadapt.json"
transcriptomics.STAR_2_INDEX = ".star2.idx"
transcriptomics.STAR_2_INDEX_META_ZIP = ".star2_idx_meta.zip"
transcriptomics.STAR_2_QUANT_TSV = ".star2_quant.tsv"
transcriptomics.BOWTIE_1_ALIGNMENT = ".bowtie1.align"
transcriptomics.BOWTIE_1_INDEX = ".bowtie1.idx"
transcriptomics.BOWTIE_1_INDEX_MAPPING = ".bowtie_1_index_mapping.json"
transcriptomics.KALLISTO_INDEX = ".kallisto.idx"
transcriptomics.KALLISTO_QUANT_TSV = ".kallisto_quant.tsv"
transcriptomics.FASTQC_HTML = ".fastqc.html"
transcriptomics.FASTQC_ZIP = ".fastqc.zip"
transcriptomics.cellranger = types.SimpleNamespace()
transcriptomics.cellranger.SAMPLE_SHEET = ".cellranger_sample_sheet.csv"
transcriptomics.cellranger.NOVASEQ_INPUT_TAR = ".cellranger_novaseq_input.tar"
transcriptomics.cellranger.MKFASTQ_OUTPUT_TAR = ".cellranger_mkfastq_output.tar"
transcriptomics.cellranger.REFERENCE_VDJ = ".10xreference_vdj.tar"
transcriptomics.cellranger.REFERENCE_GENOME = ".10xreference_genome.tar"
transcriptomics.cellranger.FEATUREREF_MULTI_CSV = ".cellranger_featureref_multi.csv"
transcriptomics.cellranger.MULTI_OUTPUT_TAR = ".cellranger_multi_output.tar"
transcriptomics.cellranger.FILTERED_OUTPUT_TAR = ".cellranger_filtered_output.tar"
transcriptomics.cellranger.SCRIPT = ".SCRIPT.sh"

# Imaging=======================================================================

# Mass Spec=====================================================================
ms = types.SimpleNamespace()
ms.RUN_META_CSV = ".run_meta.csv"
ms.RUN_BATCH_META_CSV = ".run_batch_meta.csv"
ms.SPECTRA_META_CSV = ".spectra_meta.csv"
ms.SPECTRA_NOISE_CSV = ".spectra_noise.csv"
ms.INSTRUMENT_UNIT_CSV = ".instrument_unit.csv"
ms.SCANS_CSV = ".scans.csv"
ms.PRECURSOR_WINDOW_CSV = ".precursor_window.csv"
ms.NORM_IT_CSV = ".norm_it.csv"
ms.ALIGN_SCANS_CSV = ".align_scans.csv"
ms.ION_TIC_CORR_CSV = ".ion_tic_corr.csv"
ms.AVG_SCANS_CSV = ".avg_scans.csv"
ms.RECAL_MZ_CSV = ".recal_mz.csv"
ms.MULTI_ALIGN_SCANS_CSV = ".multialign_scans.csv"
ms.MULTI_AVG_SCANS_CSV = ".multiavg_scans.csv"
ms.MERGED_IONS_CSV = ".merged_ions.csv"
ms.GLOBAL_RECAL_MZ_CSV = ".global_recal_mz.csv"
ms.IMMUTABLE_PEPTIDES = ".immutable_peptides.txt"
ms.ION_CHARGE_STATE_CSV = ".calculated_charge_state.csv"
ms.ANNOTATED_MET_CSV = ".annotated_metabolites.csv"
ms.ANNOTATED_MET_IEM_CSV = ".annotated_metabolites_iem.csv"
ms.IONS_CSV = ".ions.csv"
ms.IONS_DRIFT_CORRECTED_CSV = ".ions_drift_corrected.csv"
ms.KEGG_MAP_HTML = ".kegg_map.html"

# Flow Cytometry================================================================
flow_cytometry = types.SimpleNamespace()
flow_cytometry.FCS = ".flow_cytometry.fcs"
flow_cytometry.CALIBRATION_FCS = ".flow_cytometry.calibration_fcs"

flow_cytometry.qc = types.SimpleNamespace()

flow_cytometry.qc.reports = types.SimpleNamespace()
flow_cytometry.qc.reports.ANY = "flow_cytometry.qc.reports.ANY"
flow_cytometry.qc.reports.FLOWAI_QCMINI_TXT = ".flowai_qcmini.txt"
flow_cytometry.qc.reports.FLOWAI_REPORT_HTML = ".flowai_report.html"
flow_cytometry.qc.reports.PEACOQC_REPORT_TXT = ".peacoqc_report.txt"
flow_cytometry.qc.reports.PEACOQC_REPORT_PNG = ".peacoqc_report.png"
flow_cytometry.qc.reports.FLOWCUT_REPORT_TXT = ".flowcut_report.txt"
flow_cytometry.qc.reports.FLOWCUT_REPORT_PNG = ".flowcut_report.png"

flow_cytometry.qc.summary = types.SimpleNamespace()
flow_cytometry.qc.summary.ANY = "flow_cytometry.qc.summary.ANY"
flow_cytometry.qc.summary.FLOWAI_QCSTATS_XLSX = ".flowai_qc_stats.xlsx"
flow_cytometry.qc.summary.FLOWAI_QCSTATS_JPG = ".flowai_qc_stats.jpg"
flow_cytometry.qc.summary.PEACOQC_REPORT_TXT = ".peacoqc_summary.txt"
flow_cytometry.qc.summary.PEACOQC_REPORT_PNG = ".peacoqc_summary.png"
flow_cytometry.qc.summary.FLOWCUT_QCSTATS_XLSX = ".flowcut_qc_stats.xlsx"
flow_cytometry.qc.summary.FLOWCUT_QCSTATS_JPG = ".flowcut_qc_stats.jpg"
flow_cytometry.qc.summary.ROUTINE_GATING_STATS_XLSX = ".routine_gating_summary.xlsx"
flow_cytometry.qc.summary.ROUTINE_GATING_STATS_JPG = ".routine_gating_summary.jpg"

flow_cytometry.qc.gating = types.SimpleNamespace()
flow_cytometry.qc.gating.CYTOCLUSTER_STRAT_CSV = ".cytocluster_gating_strat.csv"
flow_cytometry.qc.gating.CYTOCLUSTER_STATS_TSV = ".cytocluster_gating_stats.tsv"
flow_cytometry.qc.gating.CYTOCLUSTER_JPG = ".cytocluster_gating.jpg"
flow_cytometry.qc.gating.CYTOCLUSTER_MARKER_EXPRESSION_HTML = (
    ".cytocluster_marker_expression.html"
)
flow_cytometry.qc.gating.CYTOCLUSTER_MARKER_EXPRESSION_TSV = (
    ".cytocluster_marker_expression.tsv"
)
flow_cytometry.gating_strategy = types.SimpleNamespace()
flow_cytometry.gating_strategy.ANY = "flow_cytometry.gating_strategy.ANY"
flow_cytometry.gating_strategy.FLOWJO_WSP = ".flowjo.wsp"
flow_cytometry.gating_strategy.CYTOBANK_XML = ".cytobank.xml"
flow_cytometry.gating_strategy.OMIQ_GFILE = ".omiq.gfile"

flow_cytometry.meta = types.SimpleNamespace()
flow_cytometry.meta.FPREPPY_EXP_METADATA_XLSX = ".fpreppy_exp_metadata.xlsx"
flow_cytometry.meta.FPREPPY_PLATE_METADATA_CSV = ".fpreppy_plate_metadata.csv"
flow_cytometry.meta.MARKER_MAPPING_JSON = ".flow_marker_mapping.json"
flow_cytometry.meta.GATE_MAPPING_JSON = ".flow_gate_mapping.json"
flow_cytometry.meta.ADDITONAL_MAPPING_JSON = ".flow_additional_mapping.json"
flow_cytometry.meta.OMIQ_GATE_BOOLEAN_FILE = ".omiq.gatebooleanfile"

flow_cytometry.stats = types.SimpleNamespace()
flow_cytometry.stats.STATS_CSV = ".fc_stats.csv"
flow_cytometry.stats.STATS_PARQUET = ".fc_stats.parquet"
flow_cytometry.stats.GATING_TREE = ".fc_gating_tree.txt"
flow_cytometry.stats.FREQS_CSV = ".fc_freqs.csv"


# Data Conversion===============================================================
ms.converter = types.SimpleNamespace()
ms.converter.ANY = "ms.converter.ANY"
ms.converter.mzml = types.SimpleNamespace()
ms.converter.mzml.ANY = "ms.converter.mzml.ANY"
ms.converter.mzml.THERMORAWPARSER_MZML = ".thermorawparser.mzml"
ms.converter.mzml.PYMZML_IDXGZ = ".pymzml_idx.gz"

# Compression formats===========================================================
compression = types.SimpleNamespace()
compression.TAR = ".compression.tar"
compression.GZ = ".compression.gz"
compression.ZIP = ".compression.zip"

# Experimental designs==========================================================
exp_design = types.SimpleNamespace()
exp_design.ANY = "exp_design.ANY"

exp_design.input = types.SimpleNamespace()
# assay type specific input formats
exp_design.input.ANY = "exp_design.input.ANY"
exp_design.input.UTMX_METADATA_XLSX = ".utmx_metadata.xlsx"
exp_design.input.PX_METADATA_JSON = ".px_metadata.json"
exp_design.input.NGS_METADATA_JSON = ".ngs_metadata.json"
exp_design.input.TEST_METADATA_JSON = ".test_metadata.json"
exp_design.input.FLOWCYTO_METADATA_XLSX = ".flowcyto_metadata.xlsx"

exp_design.output = types.SimpleNamespace()
# urgap experimental design type output formats
exp_design.output.ANY = "exp_design.output.ANY"
exp_design.output.UTMX_METADATA_CSV = ".utmx_metadata.csv"
exp_design.output.PX_METADATA_CSV = ".px_metadata.csv"
exp_design.output.NGS_METADATA_CSV = ".ngs_metadata.csv"
exp_design.output.TEST_METADATA_JSON = ".test_metadata.json"

# TCS Parser===================================================================
tcsparser = types.SimpleNamespace()
tcsparser.metadata = types.SimpleNamespace()
tcsparser.metadata.ANY = "tcsparser.metadata.ANY"
tcsparser.metadata.JSON = ".metadata.json"
tcsparser.config = types.SimpleNamespace()
tcsparser.config.ANY = "tcsparser.config.ANY"
tcsparser.config.CONFIG = ".config.config"
tcsparser.asmconfig = types.SimpleNamespace()
tcsparser.asmconfig.JSON = ".asmconfig.json"
tcsparser.asmconfig.XLSX = ".asmconfig.xlsx"
tcsparser.mapping = types.SimpleNamespace()
tcsparser.mapping.ANY = "tcsparser.mapping.ANY"
tcsparser.mapping.YAML = ".mapping.yaml"
tcsparser.input = types.SimpleNamespace()
tcsparser.input.ANY = "tcsparser.input.ANY"
tcsparser.input.QUANTSTUDIO_TXT = ".quantstudio.txt"
tcsparser.input.VICELL_TXT = ".vicell.txt"
tcsparser.input.VICELL_CSV = ".vicell.csv"
tcsparser.input.VICELLBLU_TXT = ".vicellblu.txt"
tcsparser.input.VICELLBLU_CSV = ".vicellblu.csv"
tcsparser.input.NUCLEOCOUNTER_CSV = ".nucleocounter.csv"
tcsparser.input.CEDEX_TXT = ".cedex.txt"
tcsparser.input.CEDEX_LOG = ".cedex.log"
tcsparser.input.ENVISION_CSV = ".envision.csv"
tcsparser.input.OCTET_XLS = ".octet.xlsx"
tcsparser.input.VICELL_XR_XLSX = ".vicellxr.xlsx"
tcsparser.input.VICELL_XR_TXT = ".vicellxr.txt"
tcsparser.input.NOVA_CSV = ".nova.csv"
tcsparser.output = types.SimpleNamespace()
tcsparser.output.ASM_JSON = ".tcs_asm_output.json"
tcsparser.output.PARSER_PARQUET = ".tcs_parser_output.parquet"
tcsparser.output.RESULT_PARQUET = ".tcs_result_output.parquet"

# Urgap internal===============================================================
test = types.SimpleNamespace()
test.ANY = "test.ANY"
test.TEST_FILE1 = ".test.test_file1"
test.TEST_FILE2 = ".test.test_file2"
test.TEST_FILE3 = ".test.test_file3"
test.TEST_FILE4 = ".test.test_file4"
test.MITSURUGI = ".test.mitsurugi"

# Another subcategory
test.rumpel = types.SimpleNamespace()
test.rumpel.ANY = ".test.rumpel.ANY"
test.rumpel.MORE = ".test.more"
test.rumpel.EVENMORE = ".test.evenmore"

# Genomics=====================================================================
genomics = types.SimpleNamespace()
genomics.ANY = "genomics.ANY"

# Generic variant formats
genomics.VCF = ".genomics.vcf"
genomics.VCF_GZ = ".genomics_vcf.gz"
genomics.BCF = ".genomics.bcf"

# PLINK tool-specific formats and outputs
genomics.plink = types.SimpleNamespace()
genomics.plink.ANY = "genomics.plink.ANY"

# PLINK 1.x binary format (.bed/.bim/.fam)
genomics.plink.BED = ".plink.bed"
genomics.plink.BIM = ".plink.bim"
genomics.plink.FAM = ".plink.fam"

# PLINK 2 format (.pgen/.pvar/.psam)
genomics.plink.PGEN = ".plink2.pgen"
genomics.plink.PVAR = ".plink2.pvar"
genomics.plink.PSAM = ".plink2.psam"

# PLINK output files
genomics.plink.FREQ = ".plink.afreq"
genomics.plink.FREQ_COUNTS = ".plink.acount"
genomics.plink.HWE = ".plink.hardy"
genomics.plink.MISSING = ".plink.vmiss"
genomics.plink.SAMPLE_MISSING = ".plink.smiss"
genomics.plink.HET = ".plink.het"
genomics.plink.ASSOC = ".plink.assoc"
genomics.plink.LOG = ".plink.log"

# # Generalized ends
