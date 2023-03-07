import types

unknown = types.SimpleNamespace()
unknown.UNKNOWN = ".unknown"

# Proteomics====================================================================
proteomics = types.SimpleNamespace()
proteomics.ANY = "proteomics.ANY"
proteomics.THERMO_RAW = ".thermo.raw"
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

# De Novo Search Engines
proteomics.denovosearch = types.SimpleNamespace()
proteomics.denovosearch.NOVOR_CSV = ".novor.csv"


# Data Conversion
proteomics.converter = types.SimpleNamespace()
proteomics.converter.ANY = "proteomics.converter.ANY"
proteomics.converter.PYMZML_MGF = ".pymzml.mgf"
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
any.TXT = ".any.txt"

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

# Transcriptomics===============================================================
transcriptomics = types.SimpleNamespace()
transcriptomics.FASTA = ".transcriptomics.fa"
transcriptomics.GTF = ".transcriptomics.gtf"
transcriptomics.READS = ".transcriptomics.reads"
transcriptomics.STAR_2_INDEX = ".star2.idx"
transcriptomics.STAR_2_INDEX_META_ZIP = ".star2_idx_meta.zip"
transcriptomics.STAR_2_QUANT_TSV = ".star2_quant.tsv"
transcriptomics.BOWTIE_1_ALIGNMENT = ".bowtie1.align"
transcriptomics.BOWTIE_1_INDEX = ".bowtie1.idx"
transcriptomics.BOWTIE_1_INDEX_MAPPING = ".bowtie_1_index_mapping.json"
transcriptomics.KALLISTO_INDEX = ".kallisto.idx"
transcriptomics.KALLISTO_QUANT_TSV = ".kallisto_quant.tsv"

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

# Data Conversion===============================================================
ms.converter = types.SimpleNamespace()
ms.converter.ANY = "ms.converter.ANY"

# Compression formats===========================================================
compression = types.SimpleNamespace()
compression.TAR = ".compression.tar"
compression.GZ = ".compression.gz"
compression.ZIP = ".compression.zip"


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

# # Generalized ends