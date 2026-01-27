#!/usr/bin/env python

import pytest

import urgap


@pytest.mark.slow
@pytest.mark.skip(reason="Takes too long!")
@pytest.mark.xfail(strict=False)
def test_raw_to_pwstats_pipeline():
    raw_to_mzml = urgap.init_node("thermo_raw_file_parser_1_1_11")
    mzml_to_mgf = urgap.init_node("pymzml2mgf_2_5")
    spectrum_meta_data = urgap.init_node("spectrum_meta_data_0_0_1")
    target_decoy = urgap.init_node("generate_target_decoy_fasta_2_0_0")
    msfragger = urgap.init_node("msfragger_3")
    msgfplus = urgap.init_node("msgfplus_2021_03_22")
    pyiohat_csv = urgap.init_node("pyiohat_1_7_1")
    peptide_forest = urgap.init_node("peptide_forest_3")
    filter_node = urgap.init_node("filter_csv_1_0_0")
    urgap.init_node("flash_lfq_1_2_0")
    urgap.init_node("pw_stats_1_0_0")

    urun_dict = urgap.urun_dict.URunDict(
        {
            "parameters": {
                "pandas_query_string": "`q-value_peptide_forest` < 0.01 and `is_decoy` == False",
                "q_cut": 0.01,
                "q_cut_train": 0.1,
                "sensitivity": 0.9,
                "n_train": 10,
                "n_test": 10,
                "modifications": [
                    {
                        "aa": "M",
                        "type": "opt",
                        "position": "any",
                        "name": "Oxidation",
                    },
                    {
                        "aa": "C",
                        "type": "fix",
                        "position": "any",
                        "name": "Carbamidomethyl",
                    },
                    {
                        "aa": "*",
                        "type": "opt",
                        "position": "Prot-N-term",
                        "name": "Acetyl",
                    },
                    {
                        "aa": "K",
                        "type": "fix",
                        "position": "any",
                        "name": "TMT6plex",
                    },
                    {
                        "aa": "*",
                        "type": "opt",
                        "position": "N-term",
                        "name": "TMT6plex",
                    },
                ],
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{urgap._test_folder}/data/end2end",
            },
        },
    )

    raw_uftype = urgap.uftypes.proteomics.THERMO_RAW
    fasta_uftype = urgap.uftypes.proteomics.FASTA

    # curdir = Path(__file__).resolve()
    raw = urgap.UFile(
        uri=f"file:///Users/av568207/data/PXD005590/B?uftype={raw_uftype}#B02_08_161103_B2_HCD_OT_4ul.raw",
    )
    assert raw.path.exists()
    fasta = urgap.UFile(
        "https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/reference_proteomes/Eukaryota#UP000005640/UP000005640_9606.fasta.gz",
    )
    fasta = fasta.uncompress()
    fasta.rebase(f"file://{urgap._test_folder}/data")
    fasta.upload()
    fasta.tags.update({"uftype": fasta_uftype})
    assert fasta.path.exists()
    td_fasta = target_decoy.run([fasta], urun_dict)
    assert td_fasta[0].path.exists()
    # mzml = urgap.UFile(
    #     f"https://ftp.ebi.ac.uk/pride-archive/2017/04#PXD005590/B02_08_161103_B2_HCD_OT_4ul.raw",
    #     query=f"uftype={urgap.uftypes.ms.converter.mzml.THERMORAWPARSER_MZML}",
    # )
    # assert mzml.path.exists()
    mzml = raw_to_mzml.run([raw], urun_dict)
    assert mzml[0].path.exists()
    mgf = mzml_to_mgf.run([mzml], urun_dict)
    assert mgf[0].path.exists()
    meta = spectrum_meta_data.run([mzml], urun_dict)
    assert meta[0].path.exists()
    ident_msfragger = msfragger.run([mgf, td_fasta], urun_dict)
    assert ident_msfragger[0].path.exists()
    ident_msgfplus = msgfplus.run([mgf, td_fasta], urun_dict)
    assert ident_msgfplus[0].path.exists()

    unified_msfragger = pyiohat_csv.run([ident_msfragger, td_fasta, meta], urun_dict)
    assert unified_msfragger[0].path.exists()
    unified_msgfplus = pyiohat_csv.run([ident_msgfplus, td_fasta, meta], urun_dict)
    assert unified_msgfplus[0].path.exists()
    validated = peptide_forest.run([unified_msfragger, unified_msgfplus], urun_dict)
    assert validated[0].path.exists()
    filtered = filter_node.run([validated], urun_dict)
    assert filtered[0].path.exists()
    # quant = flash_lfq.run(filtered, urun_dict)
    # assert quant.path.exists()
    # contrasts = pw_stats.run(quants, urun_dict)
    # assert contrasts.path.exists()

    # do we need a bigger raw file
