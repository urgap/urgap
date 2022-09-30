"""Unode class.

"""
import copy
import os
import platform
import shutil
import sys
from pathlib import Path



        self.tmp_files = []

            urun_dict.unode_parameters.update(kwargs)
        )
        if len(reasons) > 0:
        else:
            self.delete_tmp_files()

        if self.has_all_required_installations() is False:
                f"Cannot execute {self.META_INFO['name']}, "
                f"it requires {self.required_3rd_party_installation} "
                "which not available on this system ..."
            )

                )
        self.tmp_files = []

                / "resources"
                / "platform_independent"
                / "arc_independent"
            )
        else:

        """

    @property

        Returns:
        """
        if self.META_INFO.get("platform_independent", True) is True:
            subfolder = "platform_independent/arc_independent"
        else:
        return subfolder


        Args:

        Returns:
        """
        pure_engine_exe_list = [Path(x).name for x in engine_exe_list]
        for uf in new_ufiles:
            if uf.path.name in pure_engine_exe_list:


        Args:

        Returns:
        """
        missing_exe = []


        if len(missing_exe) != 0:
            return False

        for path in self.tmp_files:
            if str(path) in [".", "/", "./", "../"]:
                continue
            if path.exists():
                if path.is_dir():
                    if path.is_symlink():
                        path.unlink()
                    else:
                        shutil.rmtree(path)
                else:
                    path.unlink()
        self.tmp_files = []



        Args:
        """

        """Remove umeta data for a given output_file.

        Args:
        """

    @property

        Returns:
        """
        return self.META_INFO.get("requires", None)

    @classmethod

        Args:

        Returns:
        """
        data = [
            {
                "section_title": "General Node Info",
                "tables": [
                    {
                        "title": "Run information",
                        "headers": ["key", "value"],
                        "rows": [
                            {
                                "value": f"{um.urun_dict['version']}",
                            },
                        ],
                        "caption": "URun Dict information associated with the file",
                ],
        ]
        for k in ["input_files", "output_files"]:
            for entry in um.urun_dict.get(k, []):
                data[0]["tables"][0]["rows"].append(
                )

            data[0]["tables"][0]["rows"].append({"key": "@wid", "value": wid})

        data[0]["tables"].append(
            {
                "title": "Parameters",
                "headers": ["key", "value"],
                "rows": [
                    {"key": k, "value": v}
                    for k, v in um.urun_dict["parameters"].items()
                ],
        )
            data += cls.generate_wrapper_vis(ufile)
        return data


        Args:

        Returns:

        """
            )

        execute_answer = []
        proc = None
                stdout=subprocess.PIPE,
            )
        else:
            execute_answer.append("Command list is empty")