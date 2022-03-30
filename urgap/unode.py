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

        self.tmp_files = []

                / "resources"
                / "platform_independent"
                / "arc_independent"
            )
        else:

        """



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




    @property
        return self.META_INFO.get("requires", None)