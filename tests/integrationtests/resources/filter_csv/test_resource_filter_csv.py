import importlib
import sys

from pathlib import Path

import pandas as pd
import pytest

import urgap

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))
print(sys.path)


def import_engine_as_python_function(
    name: str,
    path: Path,
    function_name: str = "main",
) -> callable:
    """Allow to import any function from a given engine on which it is executed.

    Function selectivity is achieved by the function_name argument.

    Args:
        name: Node name.
        path: Path to node executable.
        function_name: Name of the function that should be imported.

    Returns:
        Imported function as defined by function_name.
    """
    resources = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(resources)
    resources.loader.exec_module(module)
    return getattr(module, function_name)


def test_filter_int():
    filter_csv = urgap.init_node("FilterTabularToCSV:1.0.0")
    main = import_engine_as_python_function(
        name=filter_csv.META_INFO["name"],
        path=filter_csv.construct_exe_path(),
    )

    input_file = urgap._test_folder / "data" / "unified_csvs" / "demo.csv"
    output_file = urgap._test_folder / "data" / "unified_csvs" / "test.csv"
    main(
        input_files=[input_file],
        output=output_file,
        mode="csv",
        query_string="`spectrum_id` > 3000",
    )
    df = pd.read_csv(output_file)
    assert df.shape[0] == 4
    output_file.unlink()


def test_filter_int_input_twice():
    filter_csv = urgap.init_node("filter_csv_1_0_0")
    main = import_engine_as_python_function(
        name=filter_csv.META_INFO["name"],
        path=filter_csv.construct_exe_path(),
    )

    input_file = urgap._test_folder / "data" / "unified_csvs" / "demo.csv"
    output_file = urgap._test_folder / "data" / "unified_csvs" / "test.csv"
    main(
        csvs=[input_file, input_file],
        output=output_file,
        query_string="`spectrum_id` > 3000",
    )
    df = pd.read_csv(output_file)
    assert df.shape[0] == 8
    output_file.unlink()


def test_filter_float():
    filter_csv = urgap.init_node("filter_csv_1_0_0")
    main = import_engine_as_python_function(
        name=filter_csv.META_INFO["name"],
        path=filter_csv.construct_exe_path(),
    )

    input_file = urgap._test_folder / "data" / "unified_csvs" / "demo.csv"
    output_file = urgap._test_folder / "data" / "unified_csvs" / "test.csv"
    main(
        csvs=[input_file],
        output=output_file,
        query_string="2050 < `Retention Time (s)` < 2100",
    )
    df = pd.read_csv(output_file)
    assert df.shape[0] == 1
    output_file.unlink()


def test_filter_str():
    filter_csv = urgap.init_node("filter_csv_1_0_0")
    main = import_engine_as_python_function(
        name=filter_csv.META_INFO["name"],
        path=filter_csv.construct_exe_path(),
    )

    input_file = urgap._test_folder / "data" / "unified_csvs" / "demo.csv"
    output_file = urgap._test_folder / "data" / "unified_csvs" / "test.csv"
    main(
        csvs=[input_file],
        output=output_file,
        query_string="`Raw data location`.str.contains('R2')",
    )
    df = pd.read_csv(output_file)
    assert df.shape[0] == 2
    output_file.unlink()


def test_filter_combined_str_and_float():
    filter_csv = urgap.init_node("filter_csv_1_0_0")
    main = import_engine_as_python_function(
        name=filter_csv.META_INFO["name"],
        path=filter_csv.construct_exe_path(),
    )

    input_file = urgap._test_folder / "data" / "unified_csvs" / "demo.csv"
    output_file = urgap._test_folder / "data" / "unified_csvs" / "test.csv"
    main(
        csvs=[input_file],
        output=output_file,
        query_string="`Raw data location`.str.contains('R2') and `Exp m/z` > 400",
    )
    df = pd.read_csv(output_file)
    assert df.shape[0] == 1
    output_file.unlink()


def test_query_string_wrong_format():
    filter_csv = urgap.init_node("filter_csv_1_0_0")
    main = import_engine_as_python_function(
        name=filter_csv.META_INFO["name"],
        path=filter_csv.construct_exe_path(),
    )

    with pytest.raises(RuntimeError):
        input_file = urgap._test_folder / "data" / "unified_csvs" / "demo.csv"
        output_file = urgap._test_folder / "data" / "unified_csvs" / "test.csv"
        main(
            csvs=[input_file],
            output=output_file,
            query_string="`Raw data location` yada yada",
        )


def test_query_string_missing_column():
    filter_csv = urgap.init_node("filter_csv_1_0_0")
    main = import_engine_as_python_function(
        name=filter_csv.META_INFO["name"],
        path=filter_csv.construct_exe_path(),
    )

    with pytest.raises(RuntimeError):
        input_file = urgap._test_folder / "data" / "unified_csvs" / "demo.csv"
        output_file = urgap._test_folder / "data" / "unified_csvs" / "test.csv"
        main(
            csvs=[input_file],
            output=output_file,
            query_string="`Not Existing Column` == 1",
        )