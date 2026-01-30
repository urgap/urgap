import argparse

def main(
    input_files: str | list | None = None,
    output: str | None = None,
) -> None:
    r"""DESeq2 node.

    Args:
        
    """
    
    with open(output, "w") as file:
        file.write(f"Deseq2 data will be here {input_files}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_files",
        dest="input_files",
        action="append",
        help="input files to be analysed",
    )
    parser.add_argument("-o", "--output_file", dest="output_file", help="output file")
    
    args = parser.parse_args()
    main(
        input_files=args.input_files,
        output=args.output_file,
    )
