import types

unknown = types.SimpleNamespace()
unknown.UNKNOWN = ".unknown"

# Proteomics====================================================================
proteomics = types.SimpleNamespace()
proteomics.ANY = "proteomics.ANY"
proteomics.THERMO_RAW = ".thermo.raw"
proteomics.FASTA = ".protein.faa"
proteomics.MODS_XML = ".mods.xml"

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

# Imaging=======================================================================

# Mass Spec=====================================================================
ms = types.SimpleNamespace()
ms.SPECTRA_META_CSV = ".spectra_meta.csv"
ms.SCANS_CSV = ".scans.csv"
ms.NORM_IT_CSV = ".norm_it.csv"
ms.ALIGN_SCANS_CSV = ".align_scans.csv"
ms.ION_TIC_CORR_CSV = ".ion_tic_corr.csv"
ms.AVG_SCANS_CSV = ".avg_scans.csv"
ms.RECAL_MZ_CSV = ".recal_mz.csv"
ms.MULTI_ALIGN_SCANS_CSV = ".multialign_scans.csv"
ms.MULTI_AVG_SCANS_CSV = ".multiavg_scans.csv"
ms.MERGED_IONS_CSV = ".merged_ions.csv"
ms.GLOBAL_RECAL_MZ_CSV = ".global_recal_mz.csv"

ms.converter = types.SimpleNamespace()
ms.converter.ANY = "ms.converter.ANY"