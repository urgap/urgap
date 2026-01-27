"""Venn Diagram 2.0.

Based on the OG Münster Venndiagram.

by
    Stefan Schulze
    Anna Niehues
    Johannes Barth
    Till Bald
    Daniel Jaeger
    Christian Fufezan

"""

import argparse
import typing as t

from pathlib import Path

import pandas as pd


def process_csv_to_sets(
    csv_files: list[str],
    data_set_identifier_cols: list[str],
    data_set_value_cols: list[str],
) -> list[dict[str, list[str] | str]]:
    """Read CSV files and concatenate specified columns to form unique keys for sets.

    Args:
        csv_files (list of str): Paths to CSV files.
        data_set_identifier_cols (list of str): Column names to concatenate to create
            the data set identifier.
        data_set_value_cols (list of str): Column names to concatenate to create the
            data value columns.

    Returns:
        list of dict: Each dict is {'data': set_of_keys, 'label': 'filename_label'}.

    Raises:
        ValueError: If number of CSVs is not between 2 and 5, or columns are missing.
        FileNotFoundError: If a CSV file is not found.
        RuntimeError: For other CSV reading errors.
    """
    venn_data_list = []
    dfs = []
    for csv_file_path in csv_files:
        try:
            dfs.append(pd.read_csv(csv_file_path))
        except FileNotFoundError as e:
            msg = f"CSV file not found: {csv_file_path}"
            raise FileNotFoundError(msg) from e
        except pd.errors.PandasError as e:
            msg = f"Error reading CSV file {csv_file_path}: {e}"
            raise RuntimeError(msg) from e

    daten_rahmen_df_ruff = pd.concat(dfs)
    missing_cols = [
        col
        for col in data_set_value_cols + data_set_identifier_cols
        if col not in daten_rahmen_df_ruff.columns
    ]
    if missing_cols:
        msg = f"Columns {missing_cols} not found in the combined CSV data."
        raise ValueError(msg)

    daten_rahmen_df_ruff["_venn_identifier_key_"] = (
        daten_rahmen_df_ruff[data_set_identifier_cols].astype(str).agg("".join, axis=1)
    )
    daten_rahmen_df_ruff["_venn_value_key_"] = (
        daten_rahmen_df_ruff[data_set_value_cols].astype(str).agg("".join, axis=1)
    )
    if not (1 < daten_rahmen_df_ruff["_venn_identifier_key_"].nunique() < 6):
        msg = (
            "Can only create Venn diagrams for 2-5 unique data set identifiers, "
            f"got {daten_rahmen_df_ruff['_venn_identifier_key_'].unique()}"
        )
        raise ValueError(msg)

    for label, gdf in daten_rahmen_df_ruff.groupby("_venn_identifier_key_"):
        venn_data_list.append(
            {"data": gdf["_venn_value_key_"].to_list(), "label": str(label)},
        )

    return venn_data_list


def main(  # noqa: C901, PLR0912, PLR0915
    venn_input_data_list: list[dict[str, t.Any]],
    output_file: str | Path,
    header_title: str,
    demo_status: bool,
    **other_styling_kwargs: t.Any,  # noqa: ANN401
) -> dict[str, t.Any]:
    """Create a simple SVG Venn diagram.

    Accepts processed data (a list of dicts, where each dict represents a set),
    output file name, header title, demo status, and other styling options.

    Each dictionary in `venn_input_data_list` should have:
            {
                'data': set(),  # The actual data elements for the set.
                'label': str,   # Label for the set (e.g., derived from filename).
                'color': str    # Optional: Color for the set.
            }

    Returns:
        dict: A dictionary where keys are set combination strings (e.g., 'C-(A|B|D)')
            and values are dicts containing the 'results' (the set elements). Example keys:
        'A&B-(C|D)'
        'C&D-(A|B)'
        'B&C-(A|D)'
        'A&B&C&D'
        'A&C-(B|D)'
        'B&D-(A|C)'
        'A&D-(B|C)'
        '(A&C&D)-B'
        '(A&B&D)-C'
        '(A&B&C)-D'
        '(B&C&D)-A'
        'A-(B|C|D)'
        'D-(A|B|C)'
        'B-(A|C|D)'
        'C-(A|B|D)'

    or for 2 or 3  or 5 VennDiagrams the appropriate combinations ...
    """
    default_values = {
        "width": 1200,
        "height": 1200,
        "label_0": "A",
        "label_1": "B",
        "label_2": "C",
        "label_3": "D",
        "label_4": "E",
        "cx": 600,
        "cy": 400,
        "label font-size header": 31,
        "label font-size major": 25,
        "label font-size minor": 20,
        "label font-size venn": 20,
        "font": "Helvetica",
        "stroke-width": 2,
        "opacity": 0.3,
    }

    # Initialize kwargs for internal use, managing precedence:
    # 1. Internal defaults
    # 2. Styling arguments passed via **other_styling_kwargs
    # 3. Explicit function arguments (output_file, header_title, demo_status)
    kwargs = default_values.copy()
    kwargs.update(other_styling_kwargs)

    kwargs["output_file"] = output_file
    kwargs["header"] = header_title  # Renamed from header_title for consistency
    kwargs["demo"] = demo_status

    # Use 'data' internally for consistency
    data = venn_input_data_list
    A, B, C, D, E = set(), set(), set(), set(), set()  # noqa: N806
    data_sets = [A, B, C, D, E]
    processed_set_info = {}  # Stores {'A': {'label': 'labelA', 'color': 'colorA'}, ...}

    for pos, d_dict in enumerate(data):
        # d_dict is like {'data': {set_elements}, 'label': 'csv_filename_derived_label'}
        set_identifier = kwargs.get(f"label_{pos}", chr(ord("A") + pos))

        current_set_label = d_dict.get("label", set_identifier)
        current_set_color = d_dict.get(
            "color",
        )  # For future use if colors are passed in data

        processed_set_info[set_identifier] = {"label": current_set_label}
        if current_set_color:
            processed_set_info[set_identifier]["color"] = current_set_color

        if pos < len(data_sets):
            data_sets[pos] |= set(d_dict["data"])
        else:
            # Should be caught by process_csv_to_sets validation
            print(  # noqa: T201
                f"Warning: More data dicts than set placeholders. Pos: {pos}",
            )
    if len(data) == 2:
        kwargs["total-pos-cy"] = kwargs["cy"] + 220
    elif len(data) == 3 or len(data) == 4:
        kwargs["total-pos-cy"] = kwargs["cy"] + 320
    elif len(data) == 5:
        kwargs["total-pos-cy"] = kwargs["cy"] + 410
    else:
        msg = f"Unsupported number of data sets: {len(data)}. Must be 2-5."
        raise ValueError(msg)

    kwargs["total_n"] = len(A | B | C | D | E)

    num_data_sets = len(data)
    vd_type_specific = {
        2: {
            "A": {
                "color": "#e41a1c",
                "cx": kwargs["cx"] - 80,
                "cy": kwargs["cy"],
                "rx": 170,
                "ry": 170,
                "rot": 0,
                "text-anchor": "end",
                "text-pos-x": kwargs["cx"] - 280,
                "text-pos-y": kwargs["cy"] - 170,
            },
            "B": {
                "color": "#377eb8",
                "cx": kwargs["cx"] + 80,
                "cy": kwargs["cy"],
                "rx": 170,
                "ry": 170,
                "rot": 0,
                "text-anchor": "start",
                "text-pos-x": kwargs["cx"] + 280,
                "text-pos-y": kwargs["cy"] - 170,
            },
        },
        3: {
            "A": {
                "color": "#e41a1c",
                "cx": kwargs["cx"] - 80,
                "cy": kwargs["cy"] + 80,
                "rx": 220,
                "ry": 130,
                "rot": 50,
                "text-anchor": "end",
                "text-pos-x": kwargs["cx"] - 300,
                "text-pos-y": kwargs["cy"] - 70,
            },
            "B": {
                "color": "#377eb8",
                "cx": kwargs["cx"],
                "cy": kwargs["cy"] - 25,
                "rx": 220,
                "ry": 130,
                "rot": 90,
                "text-anchor": "end",
                "text-pos-x": kwargs["cx"],
                "text-pos-y": kwargs["cy"] - 310,
            },
            "C": {
                "color": "#4daf4a",
                "cx": kwargs["cx"] + 80,
                "cy": kwargs["cy"] + 80,
                "rx": 220,
                "ry": 130,
                "rot": -50,
                "text-anchor": "start",
                "text-pos-x": kwargs["cx"] + 300,
                "text-pos-y": kwargs["cy"] - 70,
            },
        },
        4: {
            "A": {
                "color": "#e41a1c",  # '#FF8C00',
                "cx": kwargs["cx"] - 80,
                "cy": kwargs["cy"] + 80,
                "rx": 220,
                "ry": 130,
                "rot": 50,
                "text-anchor": "end",
                "text-pos-x": kwargs["cx"] - 300,
                "text-pos-y": kwargs["cy"] - 70,
            },
            "B": {
                "color": "#377eb8",  # '#FF1493',
                "cx": kwargs["cx"],
                "cy": kwargs["cy"],
                "rx": 220,
                "ry": 130,
                "rot": +50,
                "text-anchor": "end",
                "text-pos-x": kwargs["cx"] - 200,
                "text-pos-y": kwargs["cy"] - 200,
            },
            "C": {
                "color": "#4daf4a",  # '#7D26CD',
                "cx": kwargs["cx"],
                "cy": kwargs["cy"],
                "rx": 220,
                "ry": 130,
                "rot": -50,
                "text-anchor": "start",
                "text-pos-x": kwargs["cx"] + 200,
                "text-pos-y": kwargs["cy"] - 200,
            },
            "D": {
                "color": "#984ea3",  # '#00CED1',
                "cx": kwargs["cx"] + 80,
                "cy": kwargs["cy"] + 80,
                "rx": 220,
                "ry": 130,
                "rot": -50,
                "text-anchor": "start",
                "text-pos-x": kwargs["cx"] + 300,
                "text-pos-y": kwargs["cy"] - 70,
            },
        },
        5: {
            "A": {
                "color": "#e41a1c",
                "cx": kwargs["cx"] - 70,
                "cy": kwargs["cy"] + 20,
                "rx": 280,
                "ry": 160,
                "rot": 14,
                "text-anchor": "end",
                "text-pos-x": kwargs["cx"] - 360,
                "text-pos-y": kwargs["cy"] - 60,
            },
            "B": {
                "color": "#377eb8",
                "cx": kwargs["cx"] + 10,
                "cy": kwargs["cy"],
                "rx": 280,
                "ry": 160,
                "rot": 86,
                "text-anchor": "end",
                "text-pos-x": kwargs["cx"] + 0,
                "text-pos-y": kwargs["cy"] - 320,
            },
            "C": {
                "color": "#4daf4a",
                "cx": kwargs["cx"] + 50,
                "cy": kwargs["cy"] + 65,
                "rx": 280,
                "ry": 160,
                "rot": 158,
                "text-anchor": "start",
                "text-pos-x": kwargs["cx"] + 330,
                "text-pos-y": kwargs["cy"] - 60,
            },
            "D": {
                "color": "#984ea3",
                "cx": kwargs["cx"] + 5,
                "cy": kwargs["cy"] + 125,
                "rx": 280,
                "ry": 160,
                "rot": 230,
                "text-anchor": "start",
                "text-pos-x": kwargs["cx"] + 210,
                "text-pos-y": kwargs["cy"] + 350,
            },
            "E": {
                "color": "#ff7f00",
                "cx": kwargs["cx"] - 75,
                "cy": kwargs["cy"] + 105,
                "rx": 280,
                "ry": 160,
                "rot": 302,
                "text-anchor": "end",
                "text-pos-x": kwargs["cx"] - 270,
                "text-pos-y": kwargs["cy"] + 350,
            },
        },
    }

    # Prepare the final configuration for each set ('A', 'B', etc.) and store it in kwargs
    # This merges vdTypeSpecific (for geometry, default colors) with processed_set_info (for labels, custom colors)
    # and general styling from the main kwargs.
    for (
        set_char_key,
        default_set_config_template,
    ) in vd_type_specific[num_data_sets].items():
        # Start with the default geometric/style configuration for this set
        final_set_config = default_set_config_template.copy()

        # Get properties for this set_char_key parsed from the input `data` list
        props_from_data = processed_set_info.get(set_char_key, {})

        # Override label (default to the set character like 'A', 'B')
        final_set_config["label"] = props_from_data.get("label", set_char_key)

        # Override color (if provided in data, otherwise default from vdTypeSpecific is kept)
        if "color" in props_from_data:
            final_set_config["color"] = props_from_data["color"]

        final_set_config["setSize"] = len(eval(set_char_key))  # eval('A'), eval('B')...
        for key_suffix in ["major", "minor", "venn"]:
            final_set_config[f"label font-size {key_suffix}"] = kwargs[
                f"label font-size {key_suffix}"
            ]
        kwargs[set_char_key] = (
            final_set_config  # Store final config in kwargs['A'], kwargs['B'], etc.
        )

    y2_val_header = kwargs["total-pos-cy"] + 30
    with Path(kwargs["output_file"]).open("w", encoding="utf-8") as io:
        print(
            f"""
<svg xmlns="http://www.w3.org/2000/svg" version="1.1"
width="{kwargs["width"]}" height="{kwargs["height"]}"
style="position:relative; top:0; left:0; z-index:-1;">
<title>{kwargs["header"]}</title>
<g font-family="{kwargs["font"]}" >
<text transform="translate({kwargs["cx"]} 40)" font-size="{kwargs["label font-size header"]}" text-anchor="middle">{kwargs["header"]}</text>
<text transform="translate({kwargs["cx"]} {kwargs["total-pos-cy"]})"  font-size="{kwargs["label font-size major"]}" text-anchor="middle">Total</text>
<text transform="translate({kwargs["cx"]} {y2_val_header})"  font-size="{kwargs["label font-size minor"]}" text-anchor="middle" font-style="italic">n = {kwargs["total_n"]}</text>
</g>""".strip(),
            file=io,
        )

        # Iterate over 'A', 'B', ... which are now keys in kwargs holding set configurations
        for set_key_char_loop in sorted(
            key for key in kwargs if key in "ABCDE" and isinstance(kwargs[key], dict)
        ):
            # Copy global style to set-specific config
            kwargs[set_key_char_loop]["opacity"] = kwargs["opacity"]
            kwargs[set_key_char_loop]["stroke-width"] = kwargs["stroke-width"]
            # -----
            set_config = kwargs[set_key_char_loop]
            print(
                f"""
        <ellipse rx="{set_config["rx"]}" ry="{set_config["ry"]}" transform="translate({set_config["cx"]} {set_config["cy"]}) rotate({set_config["rot"]})" style="fill:{set_config["color"]};fill-opacity:{set_config["opacity"]};stroke:{set_config["color"]};stroke-width:{set_config["stroke-width"]}" />""",
                file=io,
            )

        print(f"""\n<g font-family="{kwargs["font"]}" >""", file=io)

        for set_key_char_loop in sorted(
            key for key in kwargs if key in "ABCDE" and isinstance(kwargs[key], dict)
        ):
            set_config = kwargs[set_key_char_loop]
            y2_text_val = set_config["text-pos-y"] + 30
            major_font_size = set_config["label font-size major"]
            minor_font_size = set_config["label font-size minor"]
            print(
                f"""
        <text transform="translate({set_config["text-pos-x"]} {set_config["text-pos-y"]})"  font-size="{major_font_size}" text-anchor="{set_config["text-anchor"]}">{set_config["label"]}</text>
        <text transform="translate({set_config["text-pos-x"]} {y2_text_val})"  font-size="{minor_font_size}" text-anchor="{set_config["text-anchor"]}" font-style="italic">n = {set_config["setSize"]}</text>""",
                file=io,
            )
        print("</g>", file=io)

    if len(data) == 2:
        return_dict: dict[str, dict[str, t.Any]] = {
            "A&B": {
                "value": "A.B",
                "x": kwargs["cx"],
                "y": kwargs["cy"],
                "results": None,
            },
            "B-A": {
                "value": "B.C",  # Original value, might be a placeholder or typo
                "x": kwargs["cx"] + 170,
                "y": kwargs["cy"],
                "results": None,
            },
            "A-B": {
                "value": "A.C",  # Original value, might be a placeholder or typo
                "x": kwargs["cx"] - 170,
                "y": kwargs["cy"],
                "results": None,
            },
        }
    elif len(data) == 3:
        return_dict = {
            "A&B-C": {
                "value": "A.B",
                "x": kwargs["cx"] - 90,
                "y": kwargs["cy"],
                "results": None,
            },
            "B&C-A": {
                "value": "B.C",
                "x": kwargs["cx"] + 90,
                "y": kwargs["cy"],
                "results": None,
            },
            "A&C-B": {
                "value": "A.C",
                "x": kwargs["cx"],
                "y": kwargs["cy"] + 240,
                "results": None,
            },
            "A&B&C": {
                "value": "A.B.C",
                "x": kwargs["cx"],
                "y": kwargs["cy"] + 100,
                "results": None,
            },
            "A-(B|C)": {
                "value": "A",
                "x": kwargs["cx"] - 190,
                "y": kwargs["cy"],
                "results": None,
            },
            "C-(A|B)": {
                "value": "C",
                "x": kwargs["cx"] + 190,
                "y": kwargs["cy"],
                "results": None,
            },
            "B-(A|C)": {
                "value": "B",
                "x": kwargs["cx"],
                "y": kwargs["cy"] - 140,
                "results": None,
            },
        }
    elif len(data) == 4:
        return_dict = {
            "A&B-(C|D)": {
                "value": "A.B",
                "x": kwargs["cx"] - 140,
                "y": kwargs["cy"] - 70,
                "results": None,
            },
            "C&D-(A|B)": {
                "value": "C.D",
                "x": kwargs["cx"] + 140,
                "y": kwargs["cy"] - 70,
                "results": None,
            },
            "B&C-(A|D)": {
                "value": "B.C",
                "x": kwargs["cx"],
                "y": kwargs["cy"] - 70,
                "results": None,
            },
            "A&B&C&D": {
                "value": "A.B.C.D",
                "x": kwargs["cx"],
                "y": kwargs["cy"] + 100,
                "results": None,
            },
            "A&C-(B|D)": {
                "value": "A.C",
                "x": kwargs["cx"] - 125,
                "y": kwargs["cy"] + 135,
                "results": None,
            },
            "B&D-(A|C)": {
                "value": "B.D",
                "x": kwargs["cx"] + 125,
                "y": kwargs["cy"] + 135,
                "results": None,
            },
            "A&D-(B|C)": {
                "value": "A.D",
                "x": kwargs["cx"],
                "y": kwargs["cy"] + 240,
                "results": None,
            },
            "(A&C&D)-B": {
                "value": "A.C.D",
                "x": kwargs["cx"] - 55,
                "y": kwargs["cy"] + 170,
                "results": None,
            },
            "(A&B&D)-C": {
                "value": "A.B.D",
                "x": kwargs["cx"] + 55,
                "y": kwargs["cy"] + 170,
                "results": None,
            },
            "(A&B&C)-D": {
                "value": "A.B.C",
                "x": kwargs["cx"] - 95,
                "y": kwargs["cy"] + 30,
                "results": None,
            },
            "(B&C&D)-A": {
                "value": "B.C.D",
                "x": kwargs["cx"] + 95,
                "y": kwargs["cy"] + 30,
                "results": None,
            },
            "A-(B|C|D)": {
                "value": "A",
                "x": kwargs["cx"] - 200,
                "y": kwargs["cy"],
                "results": None,
            },
            "D-(A|B|C)": {
                "value": "D",
                "x": kwargs["cx"] + 200,
                "y": kwargs["cy"],
                "results": None,
            },
            "B-(A|C|D)": {
                "value": "B",
                "x": kwargs["cx"] - 95,
                "y": kwargs["cy"] - 140,
                "results": None,
            },
            "C-(A|B|D)": {
                "value": "C",
                "x": kwargs["cx"] + 95,
                "y": kwargs["cy"] - 140,
                "results": None,
            },
        }
    elif len(data) == 5:
        return_dict = {
            "A-(B|C|D|E)": {
                "value": "A",
                "x": kwargs["cx"] - 270,
                "y": kwargs["cy"] - 30,
                "results": None,
            },
            "D-(A|B|C|E)": {
                "value": "D",
                "x": kwargs["cx"] + 130,
                "y": kwargs["cy"] + 300,
                "results": None,
            },
            "B-(A|C|D|E)": {
                "value": "B",
                "x": kwargs["cx"],
                "y": kwargs["cy"] - 200,
                "results": None,
            },
            "C-(A|B|D|E)": {
                "value": "C",
                "x": kwargs["cx"] + 240,
                "y": kwargs["cy"] - 10,
                "results": None,
            },
            "E-(B|C|D|A)": {
                "value": "E",
                "x": kwargs["cx"] - 180,
                "y": kwargs["cy"] + 300,
                "results": None,
            },
            "A&B-(C|D|E)": {
                "value": "A.B",
                "x": kwargs["cx"] - 110,
                "y": kwargs["cy"] - 120,
                "results": None,
            },
            "C&D-(A|B|E)": {
                "value": "C.D",
                "x": kwargs["cx"] + 170,
                "y": kwargs["cy"] + 170,
                "results": None,
            },
            "B&C-(A|D|E)": {
                "value": "B.C",
                "x": kwargs["cx"] + 135,
                "y": kwargs["cy"] - 70,
                "results": None,
            },
            "E&C-(A|D|B)": {
                "value": "C.E",
                "x": kwargs["cx"] - 175,
                "y": kwargs["cy"] + 190,
                "results": None,
            },
            "B&E-(A|D|C)": {
                "value": "B.E",
                "x": kwargs["cx"] + 40,
                "y": kwargs["cy"] - 120,
                "results": None,
            },
            "A&E-(B|D|C)": {
                "value": "A.E",
                "x": kwargs["cx"] - 230,
                "y": kwargs["cy"] + 90,
                "results": None,
            },
            "E&D-(A|C|B)": {
                "value": "D.E",
                "x": kwargs["cx"] - 50,
                "y": kwargs["cy"] + 275,
                "results": None,
            },
            "A&C-(B|D|E)": {
                "value": "A.C",
                "x": kwargs["cx"] + 185,
                "y": kwargs["cy"] + 80,
                "results": None,
            },
            "B&D-(A|C|E)": {
                "value": "B.D",
                "x": kwargs["cx"] + 50,
                "y": kwargs["cy"] + 260,
                "results": None,
            },
            "A&D-(B|C|E)": {
                "value": "A.D",
                "x": kwargs["cx"] - 175,
                "y": kwargs["cy"] - 60,
                "results": None,
            },
            "(A&C&D)-(B|E)": {
                "value": "A.C.D",
                "x": kwargs["cx"] + 175,
                "y": kwargs["cy"] + 125,
                "results": None,
            },
            "(A&B&D)-(C|E)": {
                "value": "A.B.D",
                "x": kwargs["cx"] - 130,
                "y": kwargs["cy"] - 90,
                "results": None,
            },
            "(A&B&C)-(D|E)": {
                "value": "A.B.C",
                "x": kwargs["cx"] + 150,
                "y": kwargs["cy"] + 10,
                "results": None,
            },
            "(B&C&D)-(A|E)": {
                "value": "B.C.D",
                "x": kwargs["cx"] + 90,
                "y": kwargs["cy"] + 205,
                "results": None,
            },
            "(B&D&E)-(A|C)": {
                "value": "B.D.E",
                "x": kwargs["cx"] - 15,
                "y": kwargs["cy"] + 260,
                "results": None,
            },
            "(E&B&C)-(A|D)": {
                "value": "B.C.E",
                "x": kwargs["cx"] + 85,
                "y": kwargs["cy"] - 95,
                "results": None,
            },
            "(C&D&E)-(A|B)": {
                "value": "C.D.E",
                "x": kwargs["cx"] - 105,
                "y": kwargs["cy"] + 220,
                "results": None,
            },
            "(A&B&E)-(D|C)": {
                "value": "A.B.E",
                "x": kwargs["cx"] - 10,
                "y": kwargs["cy"] - 105,
                "results": None,
            },
            "(A&D&E)-(B|C)": {
                "value": "A.D.E",
                "x": kwargs["cx"] - 180,
                "y": kwargs["cy"] + 10,
                "results": None,
            },
            "(A&E&C)-(D|B)": {
                "value": "A.C.E",
                "x": kwargs["cx"] - 200,
                "y": kwargs["cy"] + 130,
                "results": None,
            },
            "(A&B&C&D)-E": {
                "value": "A.B.C.D",
                "x": kwargs["cx"] + 120,
                "y": kwargs["cy"] + 140,
                "results": None,
            },
            "(A&B&C&E)-D": {
                "value": "A.B.C.E",
                "x": kwargs["cx"] + 75,
                "y": kwargs["cy"] - 60,
                "results": None,
            },
            "(A&B&D&E)-C": {
                "value": "A.B.D.E",
                "x": kwargs["cx"] - 110,
                "y": kwargs["cy"] - 55,
                "results": None,
            },
            "(A&C&D&E)-B": {
                "value": "A.C.D.E",
                "x": kwargs["cx"] - 170,
                "y": kwargs["cy"] + 90,
                "results": None,
            },
            "(B&C&D&E)-A": {
                "value": "B.C.D.E",
                "x": kwargs["cx"] - 20,
                "y": kwargs["cy"] + 220,
                "results": None,
            },
            "A&B&C&D&E": {
                "value": "A.B.C.D.E",
                "x": kwargs["cx"] - 10,
                "y": kwargs["cy"] + 50,
                "results": None,
            },
        }
    else:
        print(  # noqa: T201
            """
            NOT SURE WHAT YOU WANT TO DO WITH MORE THAN 5 SETS ...
        """,
        )
        return_dict = {}  # Initialize to prevent NameError in the loop below

    # Calculate intersection sizes and store results
    for k_intersect_key in return_dict:
        # The eval uses A, B, C, D, E which are sets defined earlier
        r_set_result = eval(k_intersect_key)
        if not kwargs["demo"]:
            return_dict[k_intersect_key]["value"] = len(r_set_result)
        return_dict[k_intersect_key]["results"] = r_set_result

    # Append intersection labels and close SVG file
    with Path(kwargs["output_file"]).open("a", encoding="utf-8") as io:
        print(
            f"""\n<g font-family="{kwargs["font"]}" font-size="{kwargs["label font-size venn"]}" >""",
            file=io,
        )
        for label_config_dict in return_dict.values():
            # Ensure coordinates exist before trying to print the text element
            if "x" in label_config_dict and "y" in label_config_dict:
                print(
                    f"""<text transform="translate({label_config_dict["x"]} {label_config_dict["y"]})" text-anchor="middle" stroke="#777777" stroke-width="0.5" >{label_config_dict["value"]}</text>""",
                    file=io,
                )
        print("</g>", file=io)
        print("</svg>", file=io)

    print(f"Saved VennDiagram as {kwargs['output_file']}")  # noqa: T201

    # Populate the 'input' field in returnDict with the actual labels used
    return_dict["input"] = []
    # Use kwargs['label_0'], etc. which are the set identifiers ('A', 'B', ...)
    set_identifiers_ordered = [
        kwargs.get(f"label_{i}", chr(ord("A") + i)) for i in range(len(data))
    ]
    for set_id_char in set_identifiers_ordered:
        if set_id_char in processed_set_info:  # Ensure the set_id was processed
            label_used = processed_set_info[set_id_char].get("label", set_id_char)
            return_dict["input"].append({set_id_char: label_used})
    return return_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a Venn diagram from CSV files by concatenating columns.",
    )
    parser.add_argument(
        "--csv-file",
        action="append",
        required=True,
        help="Path to CSV file. Can be specified multiple times for multiple inputs.",
    )
    parser.add_argument(
        "--id-column",
        action="append",
        required=True,
        help="Column for data set IDs. Multiple uses concatenate columns.",
    )
    parser.add_argument(
        "--value-column",
        action="append",
        required=True,
        help="Column for data set values. Multiple uses concatenate columns.",
    )
    parser.add_argument(
        "--output-file",
        default="VennDiagram.svg",
        help="Path to the output SVG file (default: VennDiagram.svg).",
    )
    parser.add_argument(
        "--header",
        default="Venn Diagram",
        help="Title for the Venn diagram (default: Venn Diagram).",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Enable demo mode (shows set expressions in diagram instead of counts).",
    )
    # Add other styling arguments here if needed, e.g., --width, --font-size-major

    cli_args = parser.parse_args()

    try:
        venn_data_list = process_csv_to_sets(
            cli_args.csv_file,
            data_set_identifier_cols=cli_args.id_column,
            data_set_value_cols=cli_args.value_column,
        )

        # Collect any additional styling kwargs if they were added to argparse
        styling_kwargs = {}
        # Example: if cli_args.width: styling_kwargs['width'] = cli_args.width

        _ = main(  # Results are not used directly in CLI mode; SVG is written to file
            venn_input_data_list=venn_data_list,
            output_file=cli_args.output_file,
            header_title=cli_args.header,
            demo_status=cli_args.demo,
            **styling_kwargs,
        )
        # Optionally, print more details from 'results' if needed, especially in demo mode.

    except (ValueError, FileNotFoundError, RuntimeError) as e:
        print(f"Error: {e}")  # noqa: T201
        parser.print_help()
