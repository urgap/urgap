import platform
import shutil


        self.tmp_files = []

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
