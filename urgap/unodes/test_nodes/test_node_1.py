


    META_INFO = {
        "input_uftypes": {
        },
        "output_uftypes": {
        },
    }

        """Initialize VennDiagram_1_1_0 class."""


        Args:

        Returns:
        """
        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "--params",
            utrace.urun_dict.parameters,
            "--input",
        ]
        for ufile in utrace.input_files:
            utrace.urun_dict.command_list.append(str(ufile.path))
        utrace.urun_dict.command_list.append("--output")
        for ufile in utrace.output_files:
            utrace.urun_dict.command_list.append(str(ufile.path))


        Args:
        Returns:
        """
        super().execute(utrace)



        Args:

        Returns:
        """
        utrace.output_files[-1].path.write_text("Writing into 3_of_N")