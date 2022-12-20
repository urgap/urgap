import argparse


    if output_files is not None:
        for output_file in output_files:
                print(params, file=oo)
                print(input_files, file=oo)
    return "I am a yummy test dummy!"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", dest="input_files", nargs="+")
    parser.add_argument("--output", dest="output_files", nargs="+")
    parser.add_argument(
        "--params",
        dest="params",
    )
    main(
    )