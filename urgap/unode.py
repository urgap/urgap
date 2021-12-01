import platform
import shutil


        self.tmp_files = []

        if len(reasons) > 0:
            self.delete_tmp_files()
                / "resources"
                / "platform_independent"
                / "arc_independent"
            )
        else:

        """


        for path in self.tmp_files:
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