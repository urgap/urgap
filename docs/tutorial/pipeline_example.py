"""
Example: Running a pipeline with urgap

This example demonstrates:
- Creating a temporary directory for output
- Loading input files from test data
- Setting up a URunDict with parameters
- Running filter and compress nodes in sequence
- Inspecting the results
"""

import pandas as pd
import tempfile
from pathlib import Path
from pprint import pprint

import urgap


def main():
    """Run a simple pipeline with filter and compress nodes."""

    tmp_dir_obj = tempfile.TemporaryDirectory()
    tmp_dir = Path(tmp_dir_obj.name)
    print(f"Temp directory: {tmp_dir}")

    script_dir = Path(__file__).parent
    test_data_dir = script_dir.parent / "tests" / "data"

    ufiles = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{test_data_dir}?uftype={urgap.uftypes.any.CSV}"
                f"#unified_csvs/BSA1_xtandem_alanine_unified.csv",
            ),
        ],
    )
    print("Input files:")
    pprint(ufiles)

    urun_dict = urgap.URunDict(
        {
            "parameters": {
                "FilterTabularToCSV:1.0.0": {
                    "-q": "500 < `exp_mz` < 1000",
                },
                "CompressToTar:1.0.0": {},
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
        },
    )
    print("Pipeline configuration:")
    pprint(urun_dict)

    print("\n=== Running FilterTabularToCSV node ===")
    filter_node = urgap.init_unode("FilterTabularToCSV:1.0.0")
    filter_results = filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    print("Filter results:")
    pprint(filter_results)

    df = pd.read_csv(filter_results[0].path)
    print(f"\nFiltered data preview:\n{df.head()}")
    print(f"Shape: {df.shape}")

    print("\n=== Running CompressToTar node ===")
    compress_node = urgap.init_unode("CompressToTar:1.0.0")
    compress_results = compress_node.run(urun_dict=urun_dict, ufiles=filter_results)
    print("Compress results:")
    pprint(compress_results)

    print("\n=== Pipeline completed successfully ===")

    tmp_dir_obj.cleanup()
    print(f"\nCleaned up temporary directory")


if __name__ == "__main__":
    main()
