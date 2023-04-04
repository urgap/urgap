import argparse


    parser = argparse.ArgumentParser()
    parser.add_argument("--output", dest="output_files", nargs="+")
    known_args = parser.parse_args(argv)

    hal = "Dave, this conversation can serve no purpose anymore. Goodbye."
    for file in known_args.output_files:
            print(hal, file=oo)


if __name__ == "__main__":
    main()