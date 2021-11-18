import sys
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))
print(sys.path)


def test_filter_int():
    )
    df = pd.read_csv(output_file)
    assert df.shape[0] == 4
    output_file.unlink()


def test_filter_int_input_twice():
        csvs=[input_file, input_file],
        output=output_file,
    )
    df = pd.read_csv(output_file)
    assert df.shape[0] == 8
    output_file.unlink()


def test_filter_float():
        csvs=[input_file],
        output=output_file,
        query_string="2050 < `Retention Time (s)` < 2100",
    )
    df = pd.read_csv(output_file)
    assert df.shape[0] == 1
    output_file.unlink()


def test_filter_str():
        csvs=[input_file],
        output=output_file,
        query_string="`Raw data location`.str.contains('R2')",
    )
    df = pd.read_csv(output_file)
    assert df.shape[0] == 2
    output_file.unlink()


def test_filter_combined_str_and_float():
        csvs=[input_file],
        output=output_file,
        query_string="`Raw data location`.str.contains('R2') and `Exp m/z` > 400",
    )
    df = pd.read_csv(output_file)
    assert df.shape[0] == 1
    output_file.unlink()


def test_query_string_wrong_format():
            csvs=[input_file],
            output=output_file,
            query_string="`Raw data location` yada yada",
        )


def test_query_string_missing_column():
            csvs=[input_file],
            output=output_file,
            query_string="`Not Existing Column` == 1",
        )