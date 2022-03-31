import types

unknown = types.SimpleNamespace()
unknown.UNKNOWN = ".unknown"
# Proteomics====================================================================
proteomics = types.SimpleNamespace()
proteomics.ANY = "proteomics.ANY"
proteomics.THERMO_RAW = ".thermo.raw"
proteomics.FASTA = ".protein.faa"
proteomics.MODS_XML = ".mods.xml"

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

# Plotter=======================================================================
plotter = types.SimpleNamespace()
plotter.ANY = "plotter.ANY"
plotter.VOLCANO_PDF = ".volcano.pdf"
# Metabolomics==================================================================
# Imaging=======================================================================

# Mass Spec=====================================================================
ms = types.SimpleNamespace()
ms.SPECTRA_META_CSV = ".spectra_meta.csv"