



    META_INFO = {
        "input_uftypes": {
                "min": 0,
                "max": -1,
            },
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
                "min": 0,
                "max": 1,
            },
                "min": 1,
                "max": 9,
            },
                "min": 3,
                "max": 3,
            },
        },
    }



        Args:

        Returns:
        """


        Args:

        Returns:
        """
        minimal_dataset = utrace.output_files.number_of_uftypes()
            difference = n - minimal_dataset.get(filetype, 0)
                utrace.extend_output_files_by_uftype(uftype=filetype)

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "--params",
            "--input",
        ]
        for ufile in utrace.input_files:
            utrace.urun_dict.command_list.append(str(ufile.path))
        utrace.urun_dict.command_list.append("--output")
        for ufile in utrace.output_files:
            utrace.urun_dict.command_list.append(str(ufile.path))