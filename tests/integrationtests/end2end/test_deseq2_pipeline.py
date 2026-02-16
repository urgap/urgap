import fitz

import pandas as pd

import urgap


def test_filter_csv_pipeline(tmp_dir):
    ufiles = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.transcriptomics.COUNT_TABLE_CSV}"
                f"#unified_csvs/ncs2elp6_cropped_mRNA.count_table.csv",
            ),
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.transcriptomics.METADATA_CSV}"
                f"#unified_csvs/ncs2elp6.metadata.csv",
            ),
        ],
    )
    urun_dict = urgap.URunDict(
        {
            "parameters": {
                "DESeq2:1.0.0": {
                    "-q": "padj < 0.05 & abs(log2FoldChange) > 1",
                },
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
        },
    )
    deseq2_node = urgap.init_unode("DESeq2:1.0.0")

    deseq2_results = deseq2_node.run(urun_dict=urun_dict, ufiles=ufiles)
    df = pd.read_csv(deseq2_results[0].path)
    assert round(df["baseMean"].sum()) == 260084
    assert df.shape[0] == 31

    doc = fitz.open(deseq2_results[1].path)
    text = doc[0].get_text()
    doc.close()
    assert "PC1: 68% variance" in text
    assert "PC2: 20% variance" in text

    doc = fitz.open(deseq2_results[2].path)
    text = doc[0].get_text()
    doc.close()
    assert "1e+05" in text
    assert "\n−4\n−2\n0\n2\n4\n" in text

    urun_dict.parameters["DESeq2:1.0.0"].update(
        {"-q": "padj < 0.1 & abs(log2FoldChange) > 0.58"},
    )
    deseq2_results = deseq2_node.run(urun_dict=urun_dict, ufiles=ufiles)
    df = pd.read_csv(deseq2_results[0].path)
    assert round(df["baseMean"].sum()) == 1112663
    assert df.shape[0] == 125
