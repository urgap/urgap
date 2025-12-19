"""Urgap CellrangerMulti wrapper."""

import csv
import logging
import os
import tarfile

from pathlib import Path

import tqdm

import urgap

logger = logging.getLogger(__name__)


class CellrangerMulti(urgap.unode.UNodeBase):
    """Urgap wrapper for CellrangerMulti."""

    META_INFO = {
        "name": "CellrangerMulti",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "versions": [
            {"version": "8.0.1", "exe_path": "$cellranger"},
        ],
        "parameters_not_triggering_rerun": [],
        "input_uftypes": {
            urgap.uftypes.transcriptomics.cellranger.MKFASTQ_OUTPUT_TAR: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.transcriptomics.cellranger.REFERENCE_VDJ: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.transcriptomics.cellranger.REFERENCE_GENOME: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.transcriptomics.cellranger.FEATUREREF_MULTI_CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.transcriptomics.cellranger.MULTI_OUTPUT_TAR: {
                "min": 1,
                "max": 1,
            },
        },
        "engine": None,
        "engine_type": ("transcriptomics",),
        "citation": """
        Zheng, G. X. Y. et al. (2017). Massively parallel digital transcriptional profiling of single cells. Nature Communications 8: 1-12, doi:10.1038/ncomms14049
        """,
    }

    def __init__(self) -> None:
        """Initialize CellrangerMulti class."""
        super().__init__()

    def create_command_list(
        self,
        utrace: urgap.UTrace,
        multi_csv: Path,
    ) -> urgap.UTrace:
        """Create the command list from input parameters.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.
            multi_csv: Location of input CSV.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        utrace.urun_dict.command_list = [str(self.exe_path)]
        utrace.urun_dict.command_list.append("multi")
        utrace.urun_dict.command_list.append(f"--csv={multi_csv!s}")
        for translated_dict in utrace.urun_dict.translations["all_params"].values():
            translated_dict_key = translated_dict["translated_key"]
            translated_dict_value = translated_dict["translated_value"]
            if translated_dict_key in [
                "--jobmode",
            ]:
                utrace.urun_dict.command_list.append(
                    f"{translated_dict_key}={translated_dict_value}",
                )
        for k, v in utrace.urun_dict.parameters.items():
            utrace.urun_dict.command_list.append(f"{k}={v}")
        return utrace

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for CellrangerMulti wrapper.

        During preflight,
            - input tars are untared
            - command list is composed

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        flowcell_id_index = utrace.input_files.get_indices_by_uftype(
            urgap.uftypes.transcriptomics.cellranger.MKFASTQ_OUTPUT_TAR,
        )[0]
        flowcell_id = utrace.input_files.data[flowcell_id_index].tags["flowcell_id"]
        mkfastq_output_path_tar = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.transcriptomics.cellranger.MKFASTQ_OUTPUT_TAR,
        )[0]
        vdj_path_tar = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.transcriptomics.cellranger.REFERENCE_VDJ,
        )[0]
        genome_path_tar = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.transcriptomics.cellranger.REFERENCE_GENOME,
        )[0]

        mkfastq_output_path = str(mkfastq_output_path_tar).replace(".tar", "")
        vdj_path = str(vdj_path_tar).replace(".tar", "")
        genome_path = str(genome_path_tar).replace(".tar", "")

        featureref_multi_csv_path = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.transcriptomics.cellranger.FEATUREREF_MULTI_CSV,
        )[0]

        for path_to_tar_file, untarred_folder, description in [
            (mkfastq_output_path_tar, mkfastq_output_path, "mkfastq_output"),
            (vdj_path_tar, vdj_path, "vdj"),
            (genome_path_tar, genome_path, "genome"),
        ]:
            _untar_with_progress(path_to_tar_file, untarred_folder, description)
        unpacked_mkfastq_output_path = mkfastq_output_path + "/" + flowcell_id
        path_to_multi_csv = urgap.scratch_disk_base / "multi_config.csv"
        # build multi csv
        logger.info("Writing input CSV.")
        genome_arcname = next(
            name
            for name in Path(genome_path).iterdir()
            if (genome_path / name).is_dir()
        )
        genome_input_path = genome_path + "/" + genome_arcname
        vdj_arcname = next(
            name for name in Path(vdj_path).iterdir() if (vdj_path / name).is_dir()
        )
        vdj_input_path = vdj_path + "/" + vdj_arcname
        with str(path_to_multi_csv.open(), "w", newline="") as csvfile:
            config_writer = csv.writer(csvfile, delimiter=",")
            config_writer.writerow(
                [
                    "[gene-expression]",
                    "",
                ],
            )
            config_writer.writerow(
                [
                    "reference",
                    genome_input_path,
                ],
            )
            config_writer.writerow(
                [
                    "chemistry",
                    "auto",
                ],
            )
            config_writer.writerow(
                [
                    "include-introns",
                    "TRUE",
                ],
            )
            config_writer.writerow(
                [
                    "create-bam",
                    "TRUE",
                ],
            )
            config_writer.writerow(
                [
                    "",
                    "",
                ],
            )
            config_writer.writerow(
                [
                    "[vdj]",
                    "",
                ],
            )
            config_writer.writerow(
                [
                    "reference",
                    vdj_input_path,
                ],
            )
            config_writer.writerow(
                [
                    "",
                    "",
                ],
            )
            config_writer.writerow(
                [
                    "[feature]",
                    "",
                ],
            )
            config_writer.writerow(
                [
                    "reference",
                    featureref_multi_csv_path,
                ],
            )
            config_writer.writerow(
                [
                    "",
                    "",
                ],
            )
            config_writer.writerow(
                [
                    "[libraries]",
                    "",
                ],
            )
            config_writer.writerow(["fastq_id", "fastqs", "feature_types"])
            config_writer.writerow(
                ["GEX_1", unpacked_mkfastq_output_path, "Gene Expression"],
            )
            config_writer.writerow(
                ["FBC_1", unpacked_mkfastq_output_path, "Antibody Capture"],
            )
            config_writer.writerow(["VDJT_1", unpacked_mkfastq_output_path, "VDJ-T"])

        utrace = self.create_command_list(utrace=utrace, multi_csv=path_to_multi_csv)
        os.chdir(urgap.scratch_disk_base)
        return utrace

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for CellrangerMulti wrapper.

        During postflight,
            - output tar is generated

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        multi_output = (
            urgap.scratch_disk_base / utrace.urun_dict.parameters["--id"] / "outs"
        )
        output_tar_path = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.transcriptomics.cellranger.MULTI_OUTPUT_TAR,
        )[0]
        logger.info("Taring output.")
        msg = f"Output tar path = {output_tar_path}"
        logger.info(msg)
        with tarfile.open(output_tar_path, mode="w:") as file:
            file.add(
                multi_output,
                arcname=utrace.urun_dict.parameters["--id"],
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
