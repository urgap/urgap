"""Uinit module of urgap."""

import json
import logging
import os
import secrets
import shutil
import sys
import tempfile
import traceback

from pathlib import Path

import urgap

logger = logging.getLogger(__name__)


def copy_resources_if_needed(
    target_dir: str | os.PathLike,
    force: bool = False,
) -> None:
    """Copy package resource files to a target directory if they do not already exist, or overwrite them if forced.

    Resources are copied from the package's 'resources' directory to the specified target directory.
    Files are only overwritten if 'force' is set to True.

    Args:
        target_dir: Path to the target folder where resources will be copied.
        force: If True, resources will always be copied and overwritten at the target directory.
    """
    source_resources_path = urgap.package_dir / "resources"
    target_resources_path = Path(target_dir) / "resources"
    target_resources_path.mkdir(exist_ok=True)
    for rfile in source_resources_path.glob("**/*"):
        if rfile.is_file() is True:
            if rfile.name.startswith("."):
                continue
            target_rfile = Path(
                str(rfile).replace(
                    str(source_resources_path),
                    str(target_resources_path),
                ),
            )
            if target_rfile.exists() is False or force is True:
                target_rfile.parent.mkdir(exist_ok=True, parents=True)
                shutil.copy(rfile, target_rfile)
                if force is False:
                    msg = f"Copied resource {target_rfile.name}"
                    logger.info(msg)
                else:
                    msg = f"Resource {target_rfile.name} has been overwritten"
                    logger.debug(msg)


def configure_logger() -> None:
    """Configure the root logger with a standard format and set the logging level.

    This function resets all logger handlers and applies a new stream handler with a
    consistent formatter. The log level is set to INFO if running under '/bin/uctl',
    otherwise it is set to DEBUG.
    """
    execution_traceback = [line.strip() for line in traceback.format_stack()]
    sh = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter(
        "%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s",
    )
    sh.setFormatter(formatter)
    logger = logging.getLogger(__name__)

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    logging.getLogger().addHandler(sh)
    if "/bin/uctl" in execution_traceback[0]:
        logging.getLogger().setLevel(level="INFO")
    else:
        logging.getLogger().setLevel(level="DEBUG")
        # so bad to have it hard-coded


def create_home_folder(home_dir_parent: str | os.PathLike) -> None:
    """Create the '.urgap' home directory at the specified parent path if it does not already exist.

    Args:
        home_dir_parent: Path to the parent folder where the '.urgap' home directory will be created.
    """
    home_dir = Path(home_dir_parent) / ".urgap"
    msg = f"Creating urgap home directory at {home_dir}"
    logger.info(msg)
    Path(home_dir).mkdir(exist_ok=True, parents=True)


def copy_config_if_needed(target_dir: str | os.PathLike) -> None:
    """Copy configuration JSON files from the default config directory to the target directory if not present.

    Args:
        target_dir: Path to the folder where the default configuration files should be copied.
    """
    config_defaults_path = urgap.package_dir / "config_defaults"
    for config_json in config_defaults_path.glob("**/*.json"):
        target_json_path = Path(
            str(config_json).replace(str(config_defaults_path), str(target_dir)),
        )
        if target_json_path.exists() is False:
            shutil.copy(config_json, target_json_path)
            msg = f"{target_json_path} has been copied from default to urgap home"
            logger.info(msg)


def read_config(home_dir: str | os.PathLike | None = None) -> dict:
    """Read and load the 'urgap.json' configuration file from the specified home directory.

    If the configuration file does not exist, it will be copied from the default config directory.
    Only key-value pairs where the value is a dictionary are loaded.

    Args:
        home_dir: Path to the home folder where 'urgap.json' is located. If None, uses the default urgap home directory.

    Returns:
        A dictionary of configuration values imported from 'urgap.json'.
    """
    config_root = Path(home_dir) if home_dir is not None else urgap.home
    config_path = Path(config_root) / "urgap.json"
    try:
        with config_path.open() as uj:
            config = json.load(uj)
    except FileNotFoundError:
        copy_config_if_needed(target_dir=config_root)
        with config_path.open() as uj:
            config = json.load(uj)
    return {k: v["value"] for k, v in config.items() if isinstance(v, dict)}


def load_certificates() -> None:
    """Load SSL certificate files from the 'certificates' directory in the urgap home directory.

    Loaded certificates are stored in 'urgap.config["certificates"]' with their stem as the key.
    A warning is logged for each loaded certificate.
    """
    urgap.config["certificates"] = {}
    cert_path = Path(urgap.home) / "certificates"
    cert_path.mkdir(exist_ok=True)
    for certificate in cert_path.glob("*"):
        cert_url = certificate.stem
        msg = (
            f"Using custom SSL certificate for {cert_url}."
            "Consider using a non-self-signed certificate."
        )
        logger.warning(msg)
        urgap.config["certificates"][cert_url] = certificate


def set_scratch_disk_path(
    path: Path | None = None,
    wid: str | None = None,
) -> os.PathLike:
    """Create and return a scratch disk path, creating the directory if necessary.

    If no path is provided, a temporary directory is created. If a wid is provided,
    it is used as a subfolder under the main path.

    Args:
        path: Path to the scratch disk. If None, a temporary directory is used.
        wid: Optional subfolder name to create under the scratch disk path.

    Returns:
        The path to the created scratch disk directory.
    """
    if path is None:
        if urgap.config.get("scratch_disk", None) is not None:
            path = Path(urgap.config.get("scratch_disk"))
        else:
            path = Path(tempfile.TemporaryDirectory().name)
    if wid is not None:
        path = path / wid
    path.mkdir(exist_ok=True, parents=True)
    return path


def show_banner() -> str:
    """Generate and return a random urgap banner with a unique anagram based on 'urgap'.

    The banner includes a randomly constructed anagram using lists from the urgap uwid_obj.
    Each banner is formatted to include words that start with each letter of 'urgap'.

    Returns:
        A formatted banner string with a unique anagram.
    """
    banners = [
        r"""

  .__.   .__________.__________.____________._________.______________.     .__.
   \__\   \_    \    \_     _.  \_    ______/_     _.  \_      _.     \.    \__\
            \    \     \    \'   /\    \__    \     \     \     \'    /
    ____    /     \     \        ‾‾\           \           \     \___/
    \___\   \____________\____\     \______     \_____\     \_____/        ______
                               \_____/     \_____/     \_____/             \_____\
    """,
        r"""

          ._____________________  _______________________________.
           \     |   \    __    \/      ____/    _    |     __    \
            |    |    |   |/    /\          |    _    |     |/____/
            |_________|___|\    \_\____|    |____|____|_____|
                            \_____/    |____|
        """,
        """

                ...   ... ........   ........  .......  ........
                :::   ::: :::...::' :::   ... :::...::: :::...::'
                `::...::' :::` `::. ::::::::: :::   ::: :::
                                          :::
        """,
    ]
    constellations = [
        [
            urgap.uwid_obj.adjectives,
            urgap.uwid_obj.nouns,
            urgap.uwid_obj.verbs,
            urgap.uwid_obj.adjectives,
            urgap.uwid_obj.nouns,
        ],
    ]
    con = constellations[0]
    urgap_anagram = []
    for i, letter in enumerate("urgap"):
        random_word = secrets.choice(
            [word for word in con[i] if word.startswith(letter)],
        )
        urgap_anagram.append(random_word)

    banner = secrets.choice(banners)
    return f"""{banner}
          {urgap_anagram[0]: ^8s}   {urgap_anagram[1]: ^8}   {urgap_anagram[2]: ^8}   {urgap_anagram[3]: ^8}   {urgap_anagram[4]: ^8}
    """
