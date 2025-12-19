.. _uftypes:

UFtypes
#######

.. automodule:: urgap.uftypes

Module Variables
================

This module defines file type constants organized in nested namespaces for different scientific domains and workflows.

Unknown File Types
------------------

.. py:data:: unknown
   :type: types.SimpleNamespace

   Namespace for unknown file types.

   .. py:attribute:: UNKNOWN
      :type: str
      :value: ".unknown"

      Unknown file type.

Proteomics File Types
---------------------

.. py:data:: proteomics
   :type: types.SimpleNamespace

   Namespace for proteomics-related file types.

   .. py:attribute:: ANY
      :type: str
      :value: "proteomics.ANY"

      Any proteomics file type.

   .. py:attribute:: THERMO_RAW
      :type: str
      :value: ".thermo.raw"

      Thermo Scientific RAW format.

   .. py:attribute:: BRUKER_D_TGZ
      :type: str
      :value: ".bruker_d.tgz"

      Bruker D folder compressed as tar.gz.

   .. py:attribute:: FASTA
      :type: str
      :value: ".protein.faa"

      Protein FASTA format.

   .. py:attribute:: MODS_XML
      :type: str
      :value: ".mods.xml"

      Modifications XML format.

   .. py:attribute:: TMT_CORRECTION_FACTORS
      :type: str
      :value: ".tmt_correction_factors.json"

      TMT correction factors in JSON format.

   .. py:data:: dbsearch
      :type: types.SimpleNamespace

      Database search engine output formats.

      .. py:attribute:: ANY
         :type: str
         :value: "proteomics.dbsearch.ANY"

         Any database search output format.

      .. py:attribute:: COMET_MZID
         :type: str
         :value: ".comet.mzid"

         Comet mzIdentML output.

      .. py:attribute:: MASCOT_DAT
         :type: str
         :value: ".mascot.dat"

         Mascot DAT file output.

      .. py:attribute:: MSAMANDA_CSV
         :type: str
         :value: ".msamanda.csv"

         MSAmanda CSV output.

      .. py:attribute:: MSFRAGGER_TSV
         :type: str
         :value: ".msfragger.tsv"

         MSFragger TSV output.

      .. py:attribute:: MSGFPLUS_MZID
         :type: str
         :value: ".msgfplus.mzid"

         MS-GF+ mzIdentML output.

      .. py:attribute:: OMSSA_CSV
         :type: str
         :value: ".omssa.csv"

         OMSSA CSV output.

      .. py:attribute:: XTANDEM_XML
         :type: str
         :value: ".xtandem.xml"

         X!Tandem XML output.

      .. py:attribute:: DIANN_QUANT
         :type: str
         :value: ".diann.quant"

         DIA-NN quantification output.

      .. py:attribute:: DIANN_REPORT
         :type: str
         :value: ".diann_report.tsv"

         DIA-NN report TSV.

   .. py:data:: diannlibrary
      :type: types.SimpleNamespace

      DIA-NN library formats.

      .. py:attribute:: ANY
         :type: str
         :value: "proteomics.diannlibrary.ANY"

         Any DIA-NN library format.

      .. py:attribute:: DIANN_PREDICTED_LIBRARY
         :type: str
         :value: ".diann_predicted.speclib"

         DIA-NN predicted spectral library.

      .. py:attribute:: DIANN_EMPIRICIAL_LIBRARY
         :type: str
         :value: ".diann_emperical.speclib"

         DIA-NN empirical spectral library.

   .. py:data:: denovosearch
      :type: types.SimpleNamespace

      De novo search engine output formats.

      .. py:attribute:: NOVOR_CSV
         :type: str
         :value: ".novor.csv"

         Novor CSV output.

   .. py:data:: converter
      :type: types.SimpleNamespace

      Data conversion output formats.

      .. py:attribute:: ANY
         :type: str
         :value: "proteomics.converter.ANY"

         Any converter output format.

      .. py:attribute:: PYMZML_MGF
         :type: str
         :value: ".pymzml.mgf"

         pyMzML MGF output.

      .. py:attribute:: PYMZML_IDXGZ
         :type: str
         :value: ".pymzml_idx.gz"

         pyMzML indexed gzip output.

      .. py:attribute:: PYIOHAT_CSV
         :type: str
         :value: ".pyiohat.csv"

         pyIOHAT CSV output.

   .. py:data:: validator
      :type: types.SimpleNamespace

      Validation tool output formats.

      .. py:attribute:: ANY
         :type: str
         :value: "proteomics.validator.ANY"

         Any validator output format.

      .. py:attribute:: PERCOLATOR_CSV
         :type: str
         :value: ".percolator.csv"

         Percolator CSV output.

      .. py:attribute:: PEPTIDEFOREST_CSV
         :type: str
         :value: ".peptideforest.csv"

         PeptideForest CSV output.

   .. py:data:: quantification
      :type: types.SimpleNamespace

      Quantification tool output formats.

      .. py:attribute:: ANY
         :type: str
         :value: "proteomics.quantification.ANY"

         Any quantification output format.

      .. py:attribute:: FLASHLFQ_PSM_TSV
         :type: str
         :value: ".flashlfq_psms.tsv"

         FlashLFQ PSM-level quantification.

      .. py:attribute:: FLASHLFQ_PEPTIDE_TSV
         :type: str
         :value: ".flashlfq_peptides.tsv"

         FlashLFQ peptide-level quantification.

      .. py:attribute:: FLASHLFQ_PROTEIN_TSV
         :type: str
         :value: ".flashlfq_proteins.tsv"

         FlashLFQ protein-level quantification.

      .. py:attribute:: FLASHLFQ_BAYESFC_TSV
         :type: str
         :value: ".flashlfq_bayesFC.tsv"

         FlashLFQ Bayesian fold change analysis.

      .. py:data:: reporter_ions
         :type: types.SimpleNamespace

         Reporter ion-based quantification formats.

         .. py:attribute:: ANY
            :type: str
            :value: ".reporter_ions.ANY"

            Any reporter ion format.

         .. py:attribute:: REPORTER_IONS
            :type: str
            :value: ".reporter_ions.csv"

            Reporter ion intensities.

         .. py:attribute:: ISO_CORRECTED_REPORTER_IONS
            :type: str
            :value: ".iso_corrected_reporter_ions.csv"

            Isotope-corrected reporter ion intensities.

         .. py:attribute:: S2I_CORRECTED_REPORTER_IONS
            :type: str
            :value: ".s2i_corrected_reporter_ions.csv"

            S2I-corrected reporter ion intensities.

   .. py:data:: qc
      :type: types.SimpleNamespace

      Quality control output formats.

      .. py:attribute:: ANY
         :type: str
         :value: "proteomics.qc.ANY"

         Any QC output format.

      .. py:attribute:: OFFSET_CSV
         :type: str
         :value: ".offset.csv"

         Offset CSV file.

Statistics File Types
---------------------

.. py:data:: stats
   :type: types.SimpleNamespace

   Namespace for statistical analysis file types.

   .. py:attribute:: ANY
      :type: str
      :value: "stats.ANY"

      Any statistics file type.

   .. py:attribute:: PWSTATS_CSV
      :type: str
      :value: ".pwstats.csv"

      Pairwise statistics CSV.

   .. py:attribute:: UMAP_CSV
      :type: str
      :value: ".umap.csv"

      UMAP results CSV.

Plotter File Types
------------------

.. py:data:: plotter
   :type: types.SimpleNamespace

   Namespace for plotting and visualization output file types.

   .. py:attribute:: ANY
      :type: str
      :value: "plotter.ANY"

      Any plotter output format.

   .. py:attribute:: VOLCANO_PDF
      :type: str
      :value: ".volcano.pdf"

      Volcano plot PDF.

   .. py:attribute:: UMAP_PDF
      :type: str
      :value: ".umap.pdf"

      UMAP plot PDF.

   .. py:attribute:: VENN_RESULTS_CSV
      :type: str
      :value: ".venn_results.csv"

      Venn diagram results CSV.

   .. py:attribute:: VENN_RESULTS_SVG
      :type: str
      :value: ".venn_results.svg"

      Venn diagram SVG.

Generic File Types
------------------

.. py:data:: any
   :type: types.SimpleNamespace

   Namespace for generic file types.

   .. py:attribute:: ANY
      :type: str
      :value: "any.ANY"

      Any file type.

   .. py:attribute:: CSV
      :type: str
      :value: ".any.csv"

      Generic CSV file.

   .. py:attribute:: DAT
      :type: str
      :value: ".any.dat"

      Generic DAT file.

   .. py:attribute:: FAA
      :type: str
      :value: ".any.faa"

      Generic FASTA amino acid file.

   .. py:attribute:: MGF
      :type: str
      :value: ".any.mgf"

      Generic MGF file.

   .. py:attribute:: MZID
      :type: str
      :value: ".any.mzid"

      Generic mzIdentML file.

   .. py:attribute:: MZML
      :type: str
      :value: ".any.mzml"

      Generic mzML file.

   .. py:attribute:: PDF
      :type: str
      :value: ".any.pdf"

      Generic PDF file.

   .. py:attribute:: RAW
      :type: str
      :value: ".any.raw"

      Generic RAW file.

   .. py:attribute:: SVG
      :type: str
      :value: ".any.svg"

      Generic SVG file.

   .. py:attribute:: TSV
      :type: str
      :value: ".any.tsv"

      Generic TSV file.

   .. py:attribute:: XML
      :type: str
      :value: ".any.xml"

      Generic XML file.

   .. py:attribute:: TABULAR
      :type: str
      :value: ".any.tabular"

      Generic tabular file.

   .. py:attribute:: TXT
      :type: str
      :value: ".any.txt"

      Generic text file.

   .. py:attribute:: PARQUET
      :type: str
      :value: ".any.parquet"

      Generic Parquet file.

   .. py:attribute:: XLSX
      :type: str
      :value: ".any.xlsx"

      Generic Excel XLSX file.

Metabolomics File Types
------------------------

.. py:data:: mx
   :type: types.SimpleNamespace

   Namespace for metabolomics file types.

   .. py:attribute:: REF_MASS_CSV
      :type: str
      :value: ".ref_mass.csv"

      Reference mass CSV.

   .. py:attribute:: ADDUCTS_CSV
      :type: str
      :value: ".adducts.csv"

      Adducts CSV.

   .. py:attribute:: MASS_SHIFT_CSV
      :type: str
      :value: ".mass_shift.csv"

      Mass shift CSV.

   .. py:attribute:: CAL_MASS_CSV
      :type: str
      :value: ".cal_mass.csv"

      Calibrated mass CSV.

   .. py:attribute:: QC_HTML
      :type: str
      :value: ".qc.html"

      QC report HTML.

   .. py:attribute:: QC_SVG
      :type: str
      :value: ".qc.svg"

      QC report SVG.

   .. py:attribute:: QC_PDF
      :type: str
      :value: ".qc.pdf"

      QC report PDF.

   .. py:attribute:: BEST_ION_MET_CSV
      :type: str
      :value: ".best_ion_met.csv"

      Best ion metabolite CSV.

   .. py:attribute:: ANNOTATION_MET_HDF5
      :type: str
      :value: ".annotation_met.hdf5"

      Annotated metabolite HDF5.

   .. py:attribute:: ANNOTATION_MET_EXCLUSION_CSV
      :type: str
      :value: ".annotation_met_exc.csv"

      Annotated metabolite exclusion CSV.

   .. py:attribute:: INSTRUMENT_RESOLUTION_CSV
      :type: str
      :value: ".instr_res.csv"

      Instrument resolution CSV.

   .. py:attribute:: METADATA_MAP_JSON
      :type: str
      :value: ".metadata_map.json"

      Metadata mapping JSON.

   .. py:attribute:: METADATA_XLSX
      :type: str
      :value: ".metadata.xlsx"

      Metadata XLSX.

   .. py:attribute:: PIPELINE_EXP_DESIGN
      :type: str
      :value: ".pipeline_exp_design.csv"

      Pipeline experimental design CSV.

Transcriptomics File Types
---------------------------

.. py:data:: transcriptomics
   :type: types.SimpleNamespace

   Namespace for transcriptomics file types.

   .. py:attribute:: FASTA
      :type: str
      :value: ".transcriptomics.fa"

      Transcriptomics FASTA.

   .. py:attribute:: BAM_INDEX
      :type: str
      :value: ".transcriptomics.bai"

      BAM index file.

   .. py:attribute:: GTF
      :type: str
      :value: ".transcriptomics.gtf"

      Gene transfer format file.

   .. py:attribute:: READS
      :type: str
      :value: ".transcriptomics.reads"

      Reads file.

   .. py:attribute:: CODON_METRICS_PLOT_HTML
      :type: str
      :value: ".codon_metrics.html"

      Codon metrics plot HTML.

   .. py:attribute:: RIBOSOME_PROFILING_FEATHER
      :type: str
      :value: ".rp.feather"

      Ribosome profiling Feather format.

   .. py:attribute:: CUTADAPT_STATS_JSON
      :type: str
      :value: ".cutadapt.json"

      Cutadapt statistics JSON.

   .. py:attribute:: STAR_2_INDEX
      :type: str
      :value: ".star2.idx"

      STAR2 index.

   .. py:attribute:: STAR_2_INDEX_META_ZIP
      :type: str
      :value: ".star2_idx_meta.zip"

      STAR2 index metadata ZIP.

   .. py:attribute:: STAR_2_QUANT_TSV
      :type: str
      :value: ".star2_quant.tsv"

      STAR2 quantification TSV.

   .. py:attribute:: BOWTIE_1_ALIGNMENT
      :type: str
      :value: ".bowtie1.align"

      Bowtie1 alignment.

   .. py:attribute:: BOWTIE_1_INDEX
      :type: str
      :value: ".bowtie1.idx"

      Bowtie1 index.

   .. py:attribute:: BOWTIE_1_INDEX_MAPPING
      :type: str
      :value: ".bowtie_1_index_mapping.json"

      Bowtie1 index mapping JSON.

   .. py:attribute:: KALLISTO_INDEX
      :type: str
      :value: ".kallisto.idx"

      Kallisto index.

   .. py:attribute:: KALLISTO_QUANT_TSV
      :type: str
      :value: ".kallisto_quant.tsv"

      Kallisto quantification TSV.

   .. py:attribute:: FASTQC_HTML
      :type: str
      :value: ".fastqc.html"

      FastQC HTML report.

   .. py:attribute:: FASTQC_ZIP
      :type: str
      :value: ".fastqc.zip"

      FastQC ZIP output.

   .. py:data:: reads
      :type: types.SimpleNamespace

      Sequencing reads formats.

      .. py:attribute:: ANY
         :type: str
         :value: "transcriptomics.reads.ANY"

         Any reads format.

      .. py:attribute:: FASTQ_GZ
         :type: str
         :value: ".transcriptomics_fastq.gz"

         Compressed FASTQ file.

      .. py:attribute:: SAM
         :type: str
         :value: ".transcriptomics.sam"

         SAM alignment file.

      .. py:attribute:: BAM
         :type: str
         :value: ".transcriptomics.bam"

         BAM alignment file.

   .. py:data:: cellranger
      :type: types.SimpleNamespace

      CellRanger single-cell analysis formats.

      .. py:attribute:: SAMPLE_SHEET
         :type: str
         :value: ".cellranger_sample_sheet.csv"

         CellRanger sample sheet CSV.

      .. py:attribute:: NOVASEQ_INPUT_TAR
         :type: str
         :value: ".cellranger_novaseq_input.tar"

         CellRanger NovaSeq input TAR.

      .. py:attribute:: MKFASTQ_OUTPUT_TAR
         :type: str
         :value: ".cellranger_mkfastq_output.tar"

         CellRanger mkfastq output TAR.

      .. py:attribute:: REFERENCE_VDJ
         :type: str
         :value: ".10xreference_vdj.tar"

         10x Genomics VDJ reference TAR.

      .. py:attribute:: REFERENCE_GENOME
         :type: str
         :value: ".10xreference_genome.tar"

         10x Genomics genome reference TAR.

      .. py:attribute:: FEATUREREF_MULTI_CSV
         :type: str
         :value: ".cellranger_featureref_multi.csv"

         CellRanger multi feature reference CSV.

      .. py:attribute:: MULTI_OUTPUT_TAR
         :type: str
         :value: ".cellranger_multi_output.tar"

         CellRanger multi output TAR.

      .. py:attribute:: FILTERED_OUTPUT_TAR
         :type: str
         :value: ".cellranger_filtered_output.tar"

         CellRanger filtered output TAR.

      .. py:attribute:: SCRIPT
         :type: str
         :value: ".SCRIPT.sh"

         CellRanger script file.

Beacon Imaging File Types
--------------------------

.. py:data:: beacon
   :type: types.SimpleNamespace

   Namespace for Beacon imaging file types.

   .. py:attribute:: IMAGE_TIFF
      :type: str
      :value: ".image.tiff"

      Image TIFF file.

   .. py:attribute:: ESSAY_XML
      :type: str
      :value: ".essay.xml"

      Essay XML file.

   .. py:attribute:: OPTOSELECT_XML
      :type: str
      :value: ".optoselect.xml"

      OptoSelect XML file.

   .. py:attribute:: MLSUMMARY_PARQUET
      :type: str
      :value: ".mlsummary.parquet"

      Machine learning summary Parquet.

   .. py:attribute:: MLRAW_PARQUET
      :type: str
      :value: ".mlraw.parquet"

      Machine learning raw Parquet.

   .. py:attribute:: SUMMARY_PARQUET
      :type: str
      :value: ".summary.parquet"

      Summary Parquet.

   .. py:attribute:: BRIGHTFIELD_SUMMARY_PARQUET
      :type: str
      :value: ".brightfield_summary.parquet"

      Brightfield summary Parquet.

   .. py:attribute:: RESULT_PNG
      :type: str
      :value: ".result.png"

      Result PNG image.

Molecular Structure File Types
-------------------------------

.. py:data:: molecular_structure
   :type: types.SimpleNamespace

   Namespace for molecular structure file types.

   .. py:attribute:: ANY
      :type: str
      :value: "molecular_structure.ANY"

      Any molecular structure format.

   .. py:attribute:: PROTEIN
      :type: str
      :value: ".protein.ctf"

      Protein CTF format.

   .. py:attribute:: POLYSACC
      :type: str
      :value: ".polysacc.yaml"

      Polysaccharide YAML format.

Interdock File Types
---------------------

.. py:data:: interdock
   :type: types.SimpleNamespace

   Namespace for Interdock molecular docking file types.

   .. py:attribute:: LOG
      :type: str
      :value: ".interdock.log"

      Interdock log file.

   .. py:attribute:: CONFIG
      :type: str
      :value: ".interdock.config"

      Interdock config file (mock, file has no extension).

   .. py:attribute:: OUT
      :type: str
      :value: ".interdock.out"

      Interdock output file.

   .. py:data:: model
      :type: types.SimpleNamespace

      Interdock model formats.

      .. py:attribute:: ANY
         :type: str
         :value: "interdock.model.ANY"

         Any model format.

      .. py:attribute:: PDBQT
         :type: str
         :value: ".model_pdbqt.pdbqt"

         Model PDBQT format.

      .. py:attribute:: PDB
         :type: str
         :value: ".model_pdb.pdb"

         Model PDB format.

Mass Spectrometry File Types
-----------------------------

.. py:data:: ms
   :type: types.SimpleNamespace

   Namespace for mass spectrometry file types and metadata.

   .. py:attribute:: RUN_META_CSV
      :type: str
      :value: ".run_meta.csv"

      Run metadata CSV.

   .. py:attribute:: RUN_BATCH_META_CSV
      :type: str
      :value: ".run_batch_meta.csv"

      Run batch metadata CSV.

   .. py:attribute:: SPECTRA_META_CSV
      :type: str
      :value: ".spectra_meta.csv"

      Spectra metadata CSV.

   .. py:attribute:: SPECTRA_NOISE_CSV
      :type: str
      :value: ".spectra_noise.csv"

      Spectra noise CSV.

   .. py:attribute:: INSTRUMENT_UNIT_CSV
      :type: str
      :value: ".instrument_unit.csv"

      Instrument unit CSV.

   .. py:attribute:: SCANS_CSV
      :type: str
      :value: ".scans.csv"

      Scans CSV.

   .. py:attribute:: PRECURSOR_WINDOW_CSV
      :type: str
      :value: ".precursor_window.csv"

      Precursor window CSV.

   .. py:attribute:: NORM_IT_CSV
      :type: str
      :value: ".norm_it.csv"

      Normalized intensity CSV.

   .. py:attribute:: ALIGN_SCANS_CSV
      :type: str
      :value: ".align_scans.csv"

      Aligned scans CSV.

   .. py:attribute:: ION_TIC_CORR_CSV
      :type: str
      :value: ".ion_tic_corr.csv"

      Ion TIC correlation CSV.

   .. py:attribute:: AVG_SCANS_CSV
      :type: str
      :value: ".avg_scans.csv"

      Average scans CSV.

   .. py:attribute:: RECAL_MZ_CSV
      :type: str
      :value: ".recal_mz.csv"

      Recalibrated m/z CSV.

   .. py:attribute:: MULTI_ALIGN_SCANS_CSV
      :type: str
      :value: ".multialign_scans.csv"

      Multi-aligned scans CSV.

   .. py:attribute:: MULTI_AVG_SCANS_CSV
      :type: str
      :value: ".multiavg_scans.csv"

      Multi-average scans CSV.

   .. py:attribute:: MERGED_IONS_CSV
      :type: str
      :value: ".merged_ions.csv"

      Merged ions CSV.

   .. py:attribute:: GLOBAL_RECAL_MZ_CSV
      :type: str
      :value: ".global_recal_mz.csv"

      Global recalibrated m/z CSV.

   .. py:attribute:: IMMUTABLE_PEPTIDES
      :type: str
      :value: ".immutable_peptides.txt"

      Immutable peptides text file.

   .. py:attribute:: ION_CHARGE_STATE_CSV
      :type: str
      :value: ".calculated_charge_state.csv"

      Calculated ion charge state CSV.

   .. py:attribute:: ANNOTATED_MET_CSV
      :type: str
      :value: ".annotated_metabolites.csv"

      Annotated metabolites CSV.

   .. py:attribute:: ANNOTATED_MET_IEM_CSV
      :type: str
      :value: ".annotated_metabolites_iem.csv"

      Annotated metabolites IEM CSV.

   .. py:attribute:: IONS_CSV
      :type: str
      :value: ".ions.csv"

      Ions CSV.

   .. py:attribute:: IONS_DRIFT_CORRECTED_CSV
      :type: str
      :value: ".ions_drift_corrected.csv"

      Drift-corrected ions CSV.

   .. py:attribute:: KEGG_MAP_HTML
      :type: str
      :value: ".kegg_map.html"

      KEGG pathway map HTML.

   .. py:data:: converter
      :type: types.SimpleNamespace

      Mass spectrometry data conversion formats.

      .. py:attribute:: ANY
         :type: str
         :value: "ms.converter.ANY"

         Any MS converter format.

      .. py:data:: mzml
         :type: types.SimpleNamespace

         mzML conversion formats.

         .. py:attribute:: ANY
            :type: str
            :value: "ms.converter.mzml.ANY"

            Any mzML converter format.

         .. py:attribute:: THERMORAWPARSER_MZML
            :type: str
            :value: ".thermorawparser.mzml"

            ThermoRawFileParser mzML output.

         .. py:attribute:: PYMZML_IDXGZ
            :type: str
            :value: ".pymzml_idx.gz"

            pyMzML indexed gzip output.

Flow Cytometry File Types
--------------------------

.. py:data:: flow_cytometry
   :type: types.SimpleNamespace

   Namespace for flow cytometry file types.

   .. py:attribute:: FCS
      :type: str
      :value: ".flow_cytometry.fcs"

      Flow cytometry FCS file.

   .. py:attribute:: CALIBRATION_FCS
      :type: str
      :value: ".flow_cytometry.calibration_fcs"

      Calibration FCS file.

   .. py:data:: qc
      :type: types.SimpleNamespace

      Quality control formats.

      .. py:data:: reports
         :type: types.SimpleNamespace

         QC report formats.

         .. py:attribute:: ANY
            :type: str
            :value: "flow_cytometry.qc.reports.ANY"

            Any QC report format.

         .. py:attribute:: FLOWAI_QCMINI_TXT
            :type: str
            :value: ".flowai_qcmini.txt"

            FlowAI QC mini report text.

         .. py:attribute:: FLOWAI_REPORT_HTML
            :type: str
            :value: ".flowai_report.html"

            FlowAI report HTML.

         .. py:attribute:: PEACOQC_REPORT_TXT
            :type: str
            :value: ".peacoqc_report.txt"

            PeacoQC report text.

         .. py:attribute:: PEACOQC_REPORT_PNG
            :type: str
            :value: ".peacoqc_report.png"

            PeacoQC report PNG.

         .. py:attribute:: FLOWCUT_REPORT_TXT
            :type: str
            :value: ".flowcut_report.txt"

            flowCut report text.

         .. py:attribute:: FLOWCUT_REPORT_PNG
            :type: str
            :value: ".flowcut_report.png"

            flowCut report PNG.

      .. py:data:: summary
         :type: types.SimpleNamespace

         QC summary formats.

         .. py:attribute:: ANY
            :type: str
            :value: "flow_cytometry.qc.summary.ANY"

            Any QC summary format.

         .. py:attribute:: FLOWAI_QCSTATS_XLSX
            :type: str
            :value: ".flowai_qc_stats.xlsx"

            FlowAI QC statistics XLSX.

         .. py:attribute:: FLOWAI_QCSTATS_JPG
            :type: str
            :value: ".flowai_qc_stats.jpg"

            FlowAI QC statistics JPG.

         .. py:attribute:: PEACOQC_REPORT_TXT
            :type: str
            :value: ".peacoqc_summary.txt"

            PeacoQC summary text.

         .. py:attribute:: PEACOQC_REPORT_PNG
            :type: str
            :value: ".peacoqc_summary.png"

            PeacoQC summary PNG.

         .. py:attribute:: FLOWCUT_QCSTATS_XLSX
            :type: str
            :value: ".flowcut_qc_stats.xlsx"

            flowCut QC statistics XLSX.

         .. py:attribute:: FLOWCUT_QCSTATS_JPG
            :type: str
            :value: ".flowcut_qc_stats.jpg"

            flowCut QC statistics JPG.

         .. py:attribute:: ROUTINE_GATING_STATS_XLSX
            :type: str
            :value: ".routine_gating_summary.xlsx"

            Routine gating summary XLSX.

         .. py:attribute:: ROUTINE_GATING_STATS_JPG
            :type: str
            :value: ".routine_gating_summary.jpg"

            Routine gating summary JPG.

      .. py:data:: gating
         :type: types.SimpleNamespace

         Gating formats.

         .. py:attribute:: CYTOCLUSTER_STRAT_CSV
            :type: str
            :value: ".cytocluster_gating_strat.csv"

            Cytocluster gating strategy CSV.

         .. py:attribute:: CYTOCLUSTER_STATS_TSV
            :type: str
            :value: ".cytocluster_gating_stats.tsv"

            Cytocluster gating statistics TSV.

         .. py:attribute:: CYTOCLUSTER_JPG
            :type: str
            :value: ".cytocluster_gating.jpg"

            Cytocluster gating JPG.

         .. py:attribute:: CYTOCLUSTER_MARKER_EXPRESSION_HTML
            :type: str
            :value: ".cytocluster_marker_expression.html"

            Cytocluster marker expression HTML.

         .. py:attribute:: CYTOCLUSTER_MARKER_EXPRESSION_TSV
            :type: str
            :value: ".cytocluster_marker_expression.tsv"

            Cytocluster marker expression TSV.

   .. py:data:: gating_strategy
      :type: types.SimpleNamespace

      Gating strategy formats.

      .. py:attribute:: ANY
         :type: str
         :value: "flow_cytometry.gating_strategy.ANY"

         Any gating strategy format.

      .. py:attribute:: FLOWJO_WSP
         :type: str
         :value: ".flowjo.wsp"

         FlowJo workspace file.

      .. py:attribute:: CYTOBANK_XML
         :type: str
         :value: ".cytobank.xml"

         Cytobank XML file.

      .. py:attribute:: OMIQ_GFILE
         :type: str
         :value: ".omiq.gfile"

         OMIQ gating file.

   .. py:data:: meta
      :type: types.SimpleNamespace

      Metadata formats.

      .. py:attribute:: FPREPPY_EXP_METADATA_XLSX
         :type: str
         :value: ".fpreppy_exp_metadata.xlsx"

         fPreppy experimental metadata XLSX.

      .. py:attribute:: FPREPPY_PLATE_METADATA_CSV
         :type: str
         :value: ".fpreppy_plate_metadata.csv"

         fPreppy plate metadata CSV.

      .. py:attribute:: MARKER_MAPPING_JSON
         :type: str
         :value: ".flow_marker_mapping.json"

         Flow marker mapping JSON.

      .. py:attribute:: GATE_MAPPING_JSON
         :type: str
         :value: ".flow_gate_mapping.json"

         Flow gate mapping JSON.

      .. py:attribute:: ADDITONAL_MAPPING_JSON
         :type: str
         :value: ".flow_additional_mapping.json"

         Flow additional mapping JSON.

      .. py:attribute:: OMIQ_GATE_BOOLEAN_FILE
         :type: str
         :value: ".omiq.gatebooleanfile"

         OMIQ gate boolean file.

   .. py:data:: stats
      :type: types.SimpleNamespace

      Statistics formats.

      .. py:attribute:: STATS_CSV
         :type: str
         :value: ".fc_stats.csv"

         Flow cytometry statistics CSV.

      .. py:attribute:: STATS_PARQUET
         :type: str
         :value: ".fc_stats.parquet"

         Flow cytometry statistics Parquet.

      .. py:attribute:: GATING_TREE
         :type: str
         :value: ".fc_gating_tree.txt"

         Gating tree text.

      .. py:attribute:: FREQS_CSV
         :type: str
         :value: ".fc_freqs.csv"

         Frequencies CSV.

Compression Format File Types
------------------------------

.. py:data:: compression
   :type: types.SimpleNamespace

   Namespace for compression format file types.

   .. py:attribute:: TAR
      :type: str
      :value: ".compression.tar"

      TAR archive.

   .. py:attribute:: GZ
      :type: str
      :value: ".compression.gz"

      Gzip compressed file.

   .. py:attribute:: ZIP
      :type: str
      :value: ".compression.zip"

      ZIP archive.

Experimental Design File Types
-------------------------------

.. py:data:: exp_design
   :type: types.SimpleNamespace

   Namespace for experimental design file types.

   .. py:attribute:: ANY
      :type: str
      :value: "exp_design.ANY"

      Any experimental design format.

   .. py:data:: input
      :type: types.SimpleNamespace

      Assay-type specific input formats.

      .. py:attribute:: ANY
         :type: str
         :value: "exp_design.input.ANY"

         Any experimental design input format.

      .. py:attribute:: UTMX_METADATA_XLSX
         :type: str
         :value: ".utmx_metadata.xlsx"

         UTMX metadata XLSX.

      .. py:attribute:: PX_METADATA_JSON
         :type: str
         :value: ".px_metadata.json"

         Proteomics metadata JSON.

      .. py:attribute:: NGS_METADATA_JSON
         :type: str
         :value: ".ngs_metadata.json"

         NGS metadata JSON.

      .. py:attribute:: TEST_METADATA_JSON
         :type: str
         :value: ".test_metadata.json"

         Test metadata JSON.

      .. py:attribute:: FLOWCYTO_METADATA_XLSX
         :type: str
         :value: ".flowcyto_metadata.xlsx"

         Flow cytometry metadata XLSX.

   .. py:data:: output
      :type: types.SimpleNamespace

      URGAP experimental design output formats.

      .. py:attribute:: ANY
         :type: str
         :value: "exp_design.output.ANY"

         Any experimental design output format.

      .. py:attribute:: UTMX_METADATA_CSV
         :type: str
         :value: ".utmx_metadata.csv"

         UTMX metadata CSV.

      .. py:attribute:: PX_METADATA_CSV
         :type: str
         :value: ".px_metadata.csv"

         Proteomics metadata CSV.

      .. py:attribute:: NGS_METADATA_CSV
         :type: str
         :value: ".ngs_metadata.csv"

         NGS metadata CSV.

      .. py:attribute:: TEST_METADATA_JSON
         :type: str
         :value: ".test_metadata.json"

         Test metadata JSON.

Test File Types
----------------

.. py:data:: test
   :type: types.SimpleNamespace

   Namespace for internal test file types.

   .. py:attribute:: ANY
      :type: str
      :value: "test.ANY"

      Any test file type.

   .. py:attribute:: TEST_FILE1
      :type: str
      :value: ".test.test_file1"

      Test file 1.

   .. py:attribute:: TEST_FILE2
      :type: str
      :value: ".test.test_file2"

      Test file 2.

   .. py:attribute:: TEST_FILE3
      :type: str
      :value: ".test.test_file3"

      Test file 3.

   .. py:attribute:: TEST_FILE4
      :type: str
      :value: ".test.test_file4"

      Test file 4.

   .. py:attribute:: MITSURUGI
      :type: str
      :value: ".test.mitsurugi"

      Test Mitsurugi file.

   .. py:data:: rumpel
      :type: types.SimpleNamespace

      Rumpel test subcategory.

      .. py:attribute:: ANY
         :type: str
         :value: ".test.rumpel.ANY"

         Any Rumpel test file type.

      .. py:attribute:: MORE
         :type: str
         :value: ".test.more"

         Rumpel more test file.

      .. py:attribute:: EVENMORE
         :type: str
         :value: ".test.evenmore"

         Rumpel evenmore test file.