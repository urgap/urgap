#!/usr/bin/env python
import pytest


@pytest.mark.slow
def test_raw_to_pwstats_pipeline():

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
            },
    )


    )
    assert raw.path.exists()
    )
    fasta = fasta.uncompress()
    fasta.upload()
    assert fasta.path.exists()
    td_fasta = target_decoy.run([fasta], urun_dict)
    mgf = mzml_to_mgf.run([mzml], urun_dict)
    meta = spectrum_meta_data.run([mzml], urun_dict)
    ident_msfragger = msfragger.run([mgf, td_fasta], urun_dict)
    ident_msgfplus = msgfplus.run([mgf, td_fasta], urun_dict)

    validated = peptide_forest.run([unified_msfragger, unified_msgfplus], urun_dict)
    filtered = filter_node.run([validated], urun_dict)

    # do we need a bigger raw file