#!/usr/bin/env python3
# encoding: utf-8

"""


"""

import logging
from pathlib import Path


def source_sphinx(inc, path_to_inc):
    return f"""

    :noindex:

    """


def main():
    # logging.info(
    #     f"Formatting example scripts from {example_script_path} into rst files for docs"
    # )
    example_path = (
        Path(f"{__file__}").parent.resolve() / ".." / "example_scripts"
    ).resolve()
    rst_data = {}
    for example_file in example_path.glob("**/*.py"):
        doc_path = Path("source/code_inc")
        sub_folder_structure = example_file.parts[
            example_file.parts.index("example_scripts") + 1 : -1
        ]
        for part in sub_folder_structure:
            doc_path = doc_path / part

        doc_path.mkdir(parents=True, exist_ok=True)

        basename = example_file.with_suffix(".inc").name
        current_level = rst_data
        for subfolder in sub_folder_structure:
            if subfolder not in current_level.keys():
                current_level[subfolder] = {}
            current_level = current_level[subfolder]

        current_level[basename] = doc_path / basename
        with open(Path(__file__).resolve().parent / doc_path / basename, "w") as o:
            print(""".. code-block:: python\n""", file=o)
            with open(example_file) as infile:
                for line in infile:
                    print("\t{0}".format(line.rstrip()), file=o)

    def plot(current_level=1, current_dict=None, file=None):
        level_to_sphinx = {
            1: "=",
            2: "-",
            3: '"',
        }
        for h1 in current_dict.keys():
            if h1.endswith(".inc"):
                print(source_sphinx(h1, current_dict[h1]), file=file)
            else:
                print(h1, file=e)
                print(level_to_sphinx[current_level] * len(h1), file=e)
                print("", file=e)
                plot(
                    current_level=current_level + 1,
                    current_dict=current_dict[h1],
                    file=file,
                )

    with open("source/example_scripts.rst", "w") as e:
        print(
            """.. _example_scripts:

Example Scripts
###############

""",
            file=e,
        )
        plot(current_level=1, current_dict=rst_data, file=e)


if __name__ == "__main__":
    main()