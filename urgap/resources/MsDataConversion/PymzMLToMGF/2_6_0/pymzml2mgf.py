"""pymzml resource."""

#!/usr/bin/env python

import argparse
import logging
import os
import sys
from pathlib import Path

import pymzml


def main(
    mzml=None,
    mgf=None,
    number_of_i_decimals=5,
    number_of_mz_decimals=5,
    machine_offset_in_ppm=None,
    scan_exclusion_list=None,
    scan_inclusion_list=None,
    scan_skip_modulo_step=None,
    ms_level=2,
    precursor_min_charge=1,
    precursor_max_charge=5,
    ion_mode="pos",
    # spec_id_attribute=None,
    signal_to_noise_threshold=None,
    # scan_rt_lookup_path=None,
    **kwargs,
):
    """Convert mzML to mgf.

    A new mgf file will be created at the same location as the mzML file

    Usage:
    ./pymzml2mgf.py <mzML_file_name> <mgf_file_name>

    Args:
        mzml (str, Path): path to mzml file
        mgf (str, Path): path to mgf file
        number_of_i_decimals (int): numer of intensity decimals to use
        number_of_mz_decimals (int): number of mz decimals to use
        machine_offset_in_ppm (float): machine offset in ppm
        scan_exclusion_list (list): spectra rejected during mzml2mgf conversion
        scan_inclusion_list (list): exclusively spectra included from the mzml, e.g. during mzml2mgf conversion
        scan_skip_modulo_step (int): Include only the n-th spectrum during mzml2mgf conversion
        ms_level (int): mass spec level
        precursor_min_charge (int): minimum precursor charge
        precursor_max_charge (int): maximum precursor charge
        ion_mode (str): ion mode that has been used for acquiring mass spectra (positive or negative)
        spec_id_attribute (dict): specify the spectrum ID attribute to be used to access the spectrum ID (ID, id_dict or index)
        signal_to_noise_threshold (float): only peaks above the given signal to noise (S/N) threshold will be accepted
        scan_rt_lookup_path (str, Path): name of the pickle that is used to map the retention time
        **kwargs: further kwargs

    Returns:
        mgf (str): output file path
    """
    logging.info(
        "Converting file:\n\tmzml : {0}\n\tto\n\tmgf : {1}".format(
            mzml,
            mgf,
        )
    )
    mgf_name_base = os.path.basename(mgf).split(".mgf")[0]
    # if scan_rt_lookup_path is None:
    #     scan_rt_lookup_path = Path(mzml).parent / f"{mgf_name_base}_ursgal_lookup.csv"
    run = pymzml.run.Reader(mzml)

    mgf_entries = 0
    written_specs = 0
    if scan_exclusion_list is None:
        scan_exclusion_list = []
    else:
        scan_exclusion_list = [int(spec_id) for spec_id in scan_exclusion_list]

    if machine_offset_in_ppm is not None:
        mz_correction_factor = machine_offset_in_ppm * 1e-6
    else:
        mz_correction_factor = 0
    if precursor_min_charge is not None and precursor_max_charge is not None:
        precursor_charge_range = f"{precursor_min_charge}"
        for charge in range(precursor_min_charge + 1, precursor_max_charge + 1):
            precursor_charge_range += f" and {charge}"
    else:
        precursor_charge_range = None
    mzml_basename = os.path.basename(mzml)
    WAS_WARNED = False
    with open(mgf, "w") as fout:
        for n, spec in enumerate(run):
            if n % 1000 == 0:
                logging.info(
                    "File : {0:^40} : Processing spectrum {1}".format(
                        mzml_basename,
                        n,
                    ),
                )

            scan_time, scan_time_unit = spec.scan_time
            if scan_time_unit.upper() in ["MINUTE", "MINUTES"]:
                scan_time *= 60
                scan_time_unit = "second"
            elif scan_time_unit.upper() not in [
                "MINUTE",
                "MINUTES",
                "SECOND",
                "SECONDS",
            ]:
                if not WAS_WARNED:
                    logging.warning(
                        """
                        [Warning] The retention time unit is not recognized or not specified.
                        [Warning] It is assumed to be minutes and continues with that.
                    """
                    )
                    WAS_WARNED = True
                scan_time *= 60

            # if spec_id_attribute is None:
            spectrum_id = spec.ID
            # else:
            #     if len(spec_id_attribute.keys()) != 1:
            #         raise IOError(
            #             """
            #         [ERROR] Multiple entries in spec_id_attribute for mzml2mgf. Unclear which to choose.
            #         """
            #         )
            #     id_attribute, id_key = list(spec_id_attribute.items())[0]
            #     if id_attribute == "ID":
            #         spectrum_id = spec.ID
            #     elif id_attribute == "index":
            #         spectrum_id = spec.index + 1
            #     elif id_attribute == "id_dict":
            #         spectrum_id = spec.id_dict[id_key]
            #     else:
            #         logging.error(
            #             """
            #             [ERROR] Please specifiy an available spec_id_attribute for mzml2mgf.
            #             [ERROR] Available: ID, id_dict, index
            #         """
            #         )
            #         sys.exit(1)

            spec_ms_level = spec.ms_level
            if spec_ms_level != ms_level:
                continue
            if scan_inclusion_list is not None:
                if int(spectrum_id) not in scan_inclusion_list:
                    continue
            if int(spectrum_id) in scan_exclusion_list:
                continue

            if signal_to_noise_threshold is not None:
                spec = spec.remove_noise(
                    mode="median",
                    signal_to_noise_threshold=signal_to_noise_threshold,
                )
                peaks_2_write = spec.peaks("centroided")
            else:
                peaks_2_write = spec.peaks("centroided")

            precursor_mz = spec.selected_precursors[0]["mz"]
            precursor_charge = spec.selected_precursors[0].get("charge", None)
            precursor_mz += precursor_mz * mz_correction_factor

            if len(peaks_2_write) == 0:
                continue

            if scan_skip_modulo_step is not None:
                if mgf_entries % scan_skip_modulo_step != 0:
                    mgf_entries += 1
                    continue

            mgf_entries += 1

            mz_i_list = []
            for mz, intensity in peaks_2_write:
                # if fragment_ppm_offset is not None:
                mz += mz * mz_correction_factor
                mz_i_list.append(
                    f"{mz:<10.{number_of_mz_decimals}f} {intensity:<10.{number_of_i_decimals}f}"
                )
            mz_i_string = "\n".join(mz_i_list)

            if ion_mode == "pos":
                ion_mode = "+"
            elif ion_mode == "neg":
                ion_mode = "-"
            else:
                logging.warning(
                    """
                    [Warning] Unknown ion mode: {0}
                """.format(
                        ion_mode
                    )
                )
            if precursor_charge is not None:
                c_string = "CHARGE={0}{1}".format(precursor_charge, ion_mode)
            elif precursor_charge_range is not None:
                c_string = "CHARGE={0}{1}".format(precursor_charge_range, ion_mode)
            else:
                c_string = "CHARGE="

            fout.write(
                f"""BEGIN IONS
TITLE={mgf_name_base}.{spectrum_id}.{spectrum_id}.{precursor_charge}
SCANS={spectrum_id}
RTINSECONDS={round(scan_time, 11)}
PEPMASS={precursor_mz}
{c_string}
{mz_i_string}
END IONS

"""
            )
            written_specs += 1

    logging.info("Wrote {0} mgf entries to file {1}".format(written_specs, mgf))
    return mgf


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_file",
        type=str,
        dest="input_file",
        help="input file to be converted",
    )
    parser.add_argument(
        "-o",
        "--output_file",
        type=str,
        dest="output_file",
        help="output file",
    )
    parser.add_argument(
        "-ni",
        "--num_i_decimals",
        type=int,
        dest="num_i_decimals",
        help="number of decimal points for intensity",
        default=5,
    )
    parser.add_argument(
        "-nm",
        "--num_mz_decimals",
        type=int,
        dest="num_mz_decimals",
        help="number of decimal points for mz",
        default=5,
    )
    parser.add_argument(
        "-of",
        "--offset",
        type=int,
        dest="offset",
        help="machine offset in ppm",
        default=0,
    )
    parser.add_argument(
        "-el",
        "--exclusion_list",
        action="append",
        dest="exclusion_list",
        help="list of excluded spectra",
        default=None,
    )
    parser.add_argument(
        "-il",
        "--inclusion_list",
        action="append",
        dest="inclusion_list",
        help="list of excluded spectra",
        default=None,
    )
    parser.add_argument(
        "-s",
        "--skip_step",
        type=int,
        dest="skip_step",
        help="scan skip modulo step",
        default=None,
    )
    parser.add_argument(
        "-ms",
        "--ms_level",
        type=int,
        dest="ms_level",
        help="ms lvel",
        default=2,
    )
    parser.add_argument(
        "-cmin",
        "--min_charge",
        type=int,
        dest="min_charge",
        help="minimum precursor charge",
        default=1,
    )
    parser.add_argument(
        "-cmax",
        "--max_charge",
        type=int,
        dest="max_charge",
        help="maximum precursor charge",
        default=5,
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        dest="mode",
        help="ion mode",
        default="pos",
    )
    parser.add_argument(
        "-sn",
        "--signal_noise_threshold",
        type=float,
        dest="signal_noise_threshold",
        help="signal to noise threshold",
        default=None,
    )
    args = parser.parse_args()
    main(
        mzml=args.input_file,
        mgf=args.output_file,
        number_of_i_decimals=args.num_i_decimals,
        number_of_mz_decimals=args.num_mz_decimals,
        machine_offset_in_ppm=args.offset,
        scan_exclusion_list=args.exclusion_list,
        scan_inclusion_list=args.inclusion_list,
        scan_skip_modulo_step=args.skip_step,
        ms_level=args.ms_level,
        precursor_min_charge=args.min_charge,
        precursor_max_charge=args.max_charge,
        ion_mode=args.mode,
        # spec_id_attribute=args.min_charge,
        signal_to_noise_threshold=args.signal_noise_threshold,
        # scan_rt_lookup_path=args.rt_lookup,
    )
