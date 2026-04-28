import types

proteomics = types.SimpleNamespace()
proteomics.ANY = "proteomics.ANY"
proteomics.THERMO_RAW = ".thermo.raw"
proteomics.BRUKER_D_TGZ = ".bruker_d.tgz"
proteomics.FASTA = ".protein.faa"
proteomics.MODS_XML = ".mods.xml"
proteomics.TMT_CORRECTION_FACTORS = ".tmt_correction_factors.json"

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

proteomics.diannlibrary = types.SimpleNamespace()
proteomics.diannlibrary.ANY = "proteomics.diannlibrary.ANY"
proteomics.diannlibrary.DIANN_PREDICTED_LIBRARY = ".diann_predicted.speclib"
proteomics.diannlibrary.DIANN_EMPIRICIAL_LIBRARY = ".diann_emperical.speclib"

proteomics.denovosearch = types.SimpleNamespace()
proteomics.denovosearch.NOVOR_CSV = ".novor.csv"

proteomics.converter = types.SimpleNamespace()
proteomics.converter.ANY = "proteomics.converter.ANY"
proteomics.converter.PYMZML_MGF = ".pymzml.mgf"
proteomics.converter.PYMZML_IDXGZ = ".pymzml_idx.gz"
proteomics.converter.PYIOHAT_CSV = ".pyiohat.csv"

proteomics.validator = types.SimpleNamespace()
proteomics.validator.ANY = "proteomics.validator.ANY"
proteomics.validator.PERCOLATOR_CSV = ".percolator.csv"
proteomics.validator.PEPTIDEFOREST_CSV = ".peptideforest.csv"

proteomics.quantification = types.SimpleNamespace()
proteomics.quantification.ANY = "proteomics.quantification.ANY"
proteomics.quantification.FLASHLFQ_PSM_TSV = ".flashlfq_psms.tsv"
proteomics.quantification.FLASHLFQ_PEPTIDE_TSV = ".flashlfq_peptides.tsv"
proteomics.quantification.FLASHLFQ_PROTEIN_TSV = ".flashlfq_proteins.tsv"
proteomics.quantification.FLASHLFQ_BAYESFC_TSV = ".flashlfq_bayesFC.tsv"

proteomics.quantification.reporter_ions = types.SimpleNamespace()
proteomics.quantification.reporter_ions.ANY = ".reporter_ions.ANY"
proteomics.quantification.reporter_ions.REPORTER_IONS = ".reporter_ions.csv"
proteomics.quantification.reporter_ions.ISO_CORRECTED_REPORTER_IONS = (
    ".iso_corrected_reporter_ions.csv"
)
proteomics.quantification.reporter_ions.S2I_CORRECTED_REPORTER_IONS = (
    ".s2i_corrected_reporter_ions.csv"
)

proteomics.qc = types.SimpleNamespace()
proteomics.qc.ANY = "proteomics.qc.ANY"
proteomics.qc.OFFSET_CSV = ".offset.csv"
