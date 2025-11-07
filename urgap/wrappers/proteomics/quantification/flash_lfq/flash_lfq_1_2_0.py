"""Urgap flash_lfq_1_2_0 wrapper."""

import csv
import ctypes
import logging
import os
import sys
import tempfile

from pathlib import Path

import pandas as pd

import urgap

logger = logging.getLogger(__name__)

bits = ctypes.sizeof(ctypes.c_long) * 8
max_long = (2 ** (bits - 1)) - 1

csv.field_size_limit(min(sys.maxsize, max_long))


class flash_lfq_1_2_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the flash_lfq_1_2_0 resource.

    FlashLFQ is a computer program for high-speed label-free quantification of peptides
    following a search of bottom-up mass spectrometry data. See publication
    provided under META_INFO["citation"] for further info.
    """

    META_INFO = {
        "name": "flash_lfq_1_2_0",
        "version": "1.2.0",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "release_date": "13.07.2021",
        "api_port": 42724,
        "engine_type": ("quantification", "proteomics"),
        "platform_independent": True,  # dotnet :)
        "requires": {
            "other_uftypes": {
                "other_dependencies": ("dotnet",),
            },
        },
        "create_own_folder": True,
        "utranslation_style": "flash_lfq_style_1",
        "input_uftypes": {
            urgap.uftypes.ms.converter.mzml.THERMORAWPARSER_MZML: {
                "min": 1,
                "max": -1,
            },
            urgap.uftypes.proteomics.THERMO_RAW: {
                "min": 1,
                "max": -1,
            },
            urgap.uftypes.proteomics.converter.PYIOHAT_CSV: {
                "min": 1,
                "max": -1,
            },
            urgap.uftypes.proteomics.validator.PEPTIDEFOREST_CSV: {
                "min": 1,
                "max": -1,
            },
            urgap.uftypes.exp_design.output.PX_METADATA_CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.proteomics.quantification.FLASHLFQ_PSM_TSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.proteomics.quantification.FLASHLFQ_PEPTIDE_TSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.proteomics.quantification.FLASHLFQ_PROTEIN_TSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.proteomics.quantification.FLASHLFQ_BAYESFC_TSV: {
                "min": 0,
                "max": 1,
            },
        },
        # https://github.com/smith-chem-wisc/FlashLFQ/issues/99 found a version workoing with dotnet 5 here
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "CMD.dll",
                    "urn": "platform_independent/arc_independent/flash_lfq_1_2_0.zip",
                    "uri": None,
                    "md5_checksum": "",
                    "additional_exe": {},
                },
            },
        },
        "citation": """
        Millikin, R. J., Solntsev, S. K., Shortreed, M. R., & Smith, L. M. (2017). Ultrafast Peptide Label-Free Quantification with FlashLFQ.
        In Journal of Proteome Research (Vol. 17, Issue 1, pp. 386-391). American Chemical Society (ACS). https://doi.org/10.1021/acs.jproteome.7b00608
        """,
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize flash_lfq_1_2_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for flash_lfq_1_2_0 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        utrace.urun_dict.command_list = []
        output_folder = utrace.output_files[0].path.parent

        exp_design_path = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.exp_design.output.PX_METADATA_CSV,
        )[0]
        mzml_idx = utrace.input_files.get_indices_by_uftype(
            urgap.uftypes.ms.converter.mzml.THERMORAWPARSER_MZML,
        )
        raw_idx = utrace.input_files.get_indices_by_uftype(
            urgap.uftypes.proteomics.THERMO_RAW,
        )
        mzml_files = [utrace.input_files[i] for i in mzml_idx]
        raw_files = [utrace.input_files[i] for i in raw_idx]

        if len(mzml_files) == 0 and len(raw_files) > 0:
            spectra_files = raw_files
        elif len(raw_files) == 0 and len(mzml_files) > 0:
            spectra_files = mzml_files

        self.simple_name_lookup = self.create_simple_name_lookup(spectra_files)

        logger.debug("Writing combined ident file in tsv format")

        pyiohat_files = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.converter.PYIOHAT_CSV,
        )
        pep_forest_files = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.validator.PEPTIDEFOREST_CSV,
        )
        # unified_csvs = [utrace.input_files[i] for i in pyiohat_idx]
        # pep_forest_csvs = [utrace.input_files[i] for i in pep_forest_idx]
        ident_files = pyiohat_files + pep_forest_files
        msg = f"Write flashLFQ input file to {output_folder}"
        logger.debug(msg)
        flash_lfq_ident_file = self.write_identification_file(
            unified_csvs=ident_files,
            output_folder=output_folder,
        )

        logger.debug("Link mzMLs into output_folder")

        # check if we have the mzMLs ...
        tmp_spectra_files = set()
        for spectra_file in spectra_files:
            spectra_file = spectra_file.path
            if (
                ".mzml" in spectra_file.suffix.lower()
                or ".raw" in spectra_file.suffix.lower()
            ):
                tmp_spectra_files.add(spectra_file)
            else:
                msg = f"Cannot find spectra file {spectra_file}"
                logger.error(msg)

        spectra_files = list(tmp_spectra_files)

        for spec_path in spectra_files:
            msg = f"Linking {spec_path}"
            logger.debug(msg)
            target_path = output_folder / str(
                spec_path.stem.replace(".", "-") + spec_path.suffix,
            )
            target_path.unlink(missing_ok=True)
            os.symlink(spec_path, target_path)

        self.write_experimental_design(exp_design_path, output_folder, utrace)

        if sys.platform not in ["win32"]:
            utrace.urun_dict.command_list.append("dotnet")
        utrace.urun_dict.command_list.append(str(self.exe_path))

        # add translated parameters
        utrace = self.add_translated_params(utrace)

        # adding precursor mass tolerance
        utrace.urun_dict.command_list.append("--ppm")
        utrace.urun_dict.command_list.append(
            "{}".format(
                utrace.urun_dict.translations["all_params"][
                    "precursor_mass_tolerance_plus"
                ]["translated_value"]
                + abs(
                    utrace.urun_dict.translations["all_params"][
                        "precursor_mass_tolerance_minus"
                    ]["translated_value"],
                ),
            ),
        )

        self.tmp_dir = tempfile.TemporaryDirectory()
        # add --idt and --rep
        utrace.urun_dict.command_list.append("--idt")
        utrace.urun_dict.command_list.append(str(Path(flash_lfq_ident_file).resolve()))
        utrace.urun_dict.command_list.append("--rep")
        utrace.urun_dict.command_list.append(str(Path(output_folder).resolve()))
        utrace.urun_dict.command_list += ["--rea", "--out", self.tmp_dir.name]
        return utrace

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for flash_lfq_1_2_0 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        output_files = list(Path(self.tmp_dir.name).glob("*.tsv"))
        for file in output_files:
            if "peptide" in file.name.lower():
                target_file = utrace.output_files.get_path_objects_by_uftype(
                    urgap.uftypes.proteomics.quantification.FLASHLFQ_PEPTIDE_TSV,
                )[0]
            elif "peaks" in file.name.lower():
                target_file = utrace.output_files.get_path_objects_by_uftype(
                    urgap.uftypes.proteomics.quantification.FLASHLFQ_PSM_TSV,
                )[0]
            elif "protein" in file.name.lower():
                target_file = utrace.output_files.get_path_objects_by_uftype(
                    urgap.uftypes.proteomics.quantification.FLASHLFQ_PROTEIN_TSV,
                )[0]  # always max: 1
            elif "bayes" in file.name.lower():
                utrace.extend_output_files_by_uftype(
                    urgap.uftypes.proteomics.quantification.FLASHLFQ_BAYESFC_TSV,
                )
                target_file = utrace.output_files.get_path_objects_by_uftype(
                    urgap.uftypes.proteomics.quantification.FLASHLFQ_BAYESFC_TSV,
                )[0]
            msg = f"Move {file!s:40} -> {target_file!s:40}"
            logger.debug(msg)

            df = pd.read_csv(file, sep="\t")

            if "peptide" in str(file).lower():
                rename_dict = {}
                for c in df.columns:
                    if c.startswith("Intensity_"):
                        new_name = (
                            "Intensity_"
                            + self.simple_name_lookup[c.split("Intensity_")[1]]
                        )
                        rename_dict[c] = new_name
                    if c.startswith("Detection Type_"):
                        new_name = (
                            "Detection Type_"
                            + self.simple_name_lookup[c.split("Detection Type_")[1]]
                        )
                        rename_dict[c] = new_name
                df = df.rename(columns=rename_dict)
            if "File Name" in df.columns:
                df = df.replace({"File Name": self.simple_name_lookup})
            df.to_csv(target_file, sep="\t", index=False)

            os.remove(file)

        self.tmp_dir.cleanup()
        del self.tmp_dir
        return utrace

    def add_translated_params(self, utrace: urgap.UTrace) -> urgap.UTrace:
        """Add translated parameters to utrace.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        for urgap_key, param_dict in utrace.urun_dict.translations[
            "all_params"
        ].items():
            if urgap_key in [
                "header_translations",
                "experiment_design_header_translations",
                "quantification_evidences",
                "modifications",
                "experiment_setup",
                "unimod_xml_file_list",
                "precursor_mass_tolerance_plus",
                "precursor_mass_tolerance_minus",
            ]:
                continue
            if "exp-set" in urgap_key:
                continue

            if param_dict["translated_value"] is True:
                utrace.urun_dict.command_list.append(str(param_dict["translated_key"]))
            elif param_dict["translated_value"] is False:
                continue
            else:
                utrace.urun_dict.command_list.append(str(param_dict["translated_key"]))
                utrace.urun_dict.command_list.append(
                    str(param_dict["translated_value"]),
                )
        return utrace

    def write_identification_file(
        self,
        unified_csvs: list | None = None,
        output_folder: str | None = None,
    ) -> os.PathLike:
        """Write flashLFQ general input file.

        Args:
            unified_csvs: List of unified_csv ufiles.
            output_folder: Name of the FlashLFQ working folder.

        Returns:
            Input file path.
        """
        fieldnames = [
            "File Name",
            "Scan Retention Time",
            "Precursor Charge",
            "Base Sequence",
            "Full Sequence",
            "Peptide Monoisotopic Mass",
            "Protein Accession",
        ]
        out_name = output_folder / "flash_lfq_1_2_0_input.tsv"
        with open(out_name, "w") as flash_tsv_out:
            writer = csv.DictWriter(
                flash_tsv_out,
                fieldnames=fieldnames,
                delimiter="\t",
            )
            writer.writeheader()
            rts = []
            for path_object in unified_csvs:
                with open(path_object) as fin:
                    reader = csv.DictReader(fin)
                    for _i, line in enumerate(reader):
                        seq_mod = self.get_seq_mod(line)
                        simple_name = self.simple_name_lookup[line["raw_data_location"]]
                        line["FileName"] = simple_name
                        row = {
                            "File Name": simple_name,
                            "Scan Retention Time": float(line["retention_time_seconds"])
                            / 60,
                            "Precursor Charge": line["charge"],
                            "Base Sequence": line["sequence"],
                            "Full Sequence": seq_mod,
                            "Peptide Monoisotopic Mass": float(
                                line["ucalc_mass"],
                            ),  # BUG: use mass instead of mz!!
                            "Protein Accession": line["protein_id"],
                        }
                        rts.append(float(line["retention_time_seconds"]))
                        writer.writerow(row)
        return out_name

    def get_seq_mod(self, row: dict) -> str:
        """Create a string as an identifier for a sequence modification combination.

        Args:
            row: Rowdict.

        Returns:
            Identifier for a given peptidoform.
        """
        seq = row["sequence"]
        if row["modifications"] != "":
            mods = sorted(
                [m.split(":") for m in row["modifications"].split(";")],
                key=lambda x: int(x[1]),
                reverse=True,
            )
        else:
            mods = []
        for mod in mods:
            mod, pos = mod
            pos = int(pos)
            seq = seq[:pos] + f"[{mod}]" + seq[pos:]
        return seq

    def write_experimental_design(
        self,
        exp_design_path: os.PathLike,
        output_folder: str,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Create and write ExperimentalDesign file suitable for FlashLFQ.

        Args:
            exp_design_path: Path.
            output_folder: Name of the FlashLFQ working folder.
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Raises:
            Exception: fails if ExperimentalDesign is empty
        """
        msg = f"Copy experimental design into {output_folder}"
        logger.debug(msg)
        header_translations = utrace.urun_dict.translations["all_params"][
            "experiment_design_header_translations"
        ]["translated_value"]
        header_translations_rev = {v: k for k, v in header_translations.items()}
        target_design_path = output_folder / "ExperimentalDesign.tsv"
        with open(exp_design_path) as fin, open(target_design_path, "w") as fout:
            keys = ["FileName", "Condition", "Biorep", "Techrep", "Fraction"]
            reader = csv.DictReader(fin)
            writer = csv.DictWriter(fout, fieldnames=keys, delimiter="\t")
            writer.writeheader()
            for line in reader:
                line = {
                    header_translations_rev[k]: v
                    for k, v in line.items()
                    if k in header_translations_rev
                }
                writer.writerow(line)

    def create_simple_name_lookup(self, ufiles: urgap.UFileList) -> dict:
        """Create a lookup mapping the container name to a simplified name without '/' and '.'.

        Args:
            ufiles: List of ufiles or instance of UFileList.

        Returns:
            Mapping of container name to simple name.
        """
        lookup = {}
        for file in ufiles:
            object_name = file.object_name
            simple_name = file.simple_name
            if (
                simple_name in lookup
                or simple_name in lookup.values()
                or object_name in lookup
                or object_name in lookup.values()
            ):
                raise Exception(
                    f"Name collision detected: {object_name} or {simple_name} already in lookup",
                )
            lookup[object_name] = simple_name
            lookup[simple_name] = object_name
        return lookup
