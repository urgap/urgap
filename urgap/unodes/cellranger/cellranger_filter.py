"""Urgap CellrangerFilterSh wrapper."""

import logging
import tarfile

from pathlib import Path

import tqdm

import urgap

logger = logging.getLogger(__name__)


class CellrangerFilterSh(urgap.unode.UNodeBase):
    """Urgap wrapper for CellrangerFilterSh."""

    META_INFO = {
        "name": "CellrangerFilterSh",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "versions": [
            {"version": "8.0.1", "exe_path": "$sh"},
        ],
        "parameters_not_triggering_rerun": [],
        "input_uftypes": {
            urgap.uftypes.transcriptomics.cellranger.MULTI_OUTPUT_TAR: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.transcriptomics.cellranger.FILTERED_OUTPUT_TAR: {
                "min": 1,
                "max": 1,
            },
        },
        "engine": None,
        "engine_type": ("transcriptomics",),
        "citation": "Urgap team (2021)",
    }

    def __init__(self) -> None:
        """Initialize CellrangerFilterSh class."""
        super().__init__()
        self.tmp_output_dir = None

    def create_command_list(
        self,
        utrace: urgap.UTrace,
        script_path: Path,
        untarred_multi_folder: Path,
    ) -> urgap.UTrace:
        """Create the command list from input parameters.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.
            script_path: Path to the filter script.
            untarred_multi_folder: Path to the output of the Multi stage.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        utrace.urun_dict.command_list = [
            str(self.exe_path),
            script_path,
            f"{urgap.scratch_disk_base}/filtered_multi_output/",
            untarred_multi_folder,
        ]
        for k, v in utrace.urun_dict.parameters.items():
            if k == "output_folder":
                continue
            utrace.urun_dict.command_list.append(v)
        return utrace

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for CellrangerFilterSh wrapper.

        During preflight,
            - input tar is untared
            - command list is composed
        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        multi_output_path_tar = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.transcriptomics.cellranger.MULTI_OUTPUT_TAR,
        )[0]
        filter_script_path = utrace.urun_dict["parameters"]["-s"]
        multi_output_untarred = urgap.scratch_disk_base / "multi_output_untarred"
        _untar_with_progress(
            multi_output_path_tar,
            multi_output_untarred,
            "Multi Output.",
        )
        return self.create_command_list(
            utrace=utrace,
            script_path=filter_script_path,
            untarred_multi_folder=multi_output_untarred,
        )

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for CellrangerFilterSh wrapper.

        During postflight,
            - output tar is generated
        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        multi_output = urgap.scratch_disk_base / "filtered_multi_output"
        output_tar_path = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.transcriptomics.cellranger.FILTERED_OUTPUT_TAR,
        )[0]
        logger.info("Taring output.")
        msg = f"Output tar path = {output_tar_path}"
        logger.info(msg)
        with tarfile.open(output_tar_path, mode="w:") as file:
            file.add(
                multi_output,
                arcname="10Xoutputs-summary",
            )
        return utrace


def _untar_with_progress(
    tar_path: str | Path,
    extract_path: str | Path,
    description: str,
) -> None:
    total_size = Path(tar_path).stat().st_size
    with (
        tar_path.open("rb") as f,
        tqdm.tqdm(
            total=total_size,
            unit="B",
            unit_scale=True,
            desc=f"Untarring {description}",
        ) as pbar,
        tarfile.open(fileobj=f) as tar,
    ):
        for member in tar:
            tar.extract(member, path=extract_path)
            pbar.update(member.size)
