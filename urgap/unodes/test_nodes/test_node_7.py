


    META_INFO = {
        "input_uftypes": {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
                "min": 1,
                "max": 1,
            },
        },
    }



        Args:

        Returns:
        """
        super().execute(utrace)


        Args:

        Returns:
        """
        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
        ]
        utrace.urun_dict.command_list.append("--output")
        for ufile in utrace.output_files:
            utrace.urun_dict.command_list.append(str(ufile.path))