import types

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

ms.converter = types.SimpleNamespace()
ms.converter.ANY = "ms.converter.ANY"
ms.converter.mzml = types.SimpleNamespace()
ms.converter.mzml.ANY = "ms.converter.mzml.ANY"
ms.converter.mzml.THERMORAWPARSER_MZML = ".thermorawparser.mzml"
ms.converter.mzml.PYMZML_IDXGZ = ".pymzml_idx.gz"

