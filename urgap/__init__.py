"""urgap2."""

import atexit
import logging
import os
import sys

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from types import SimpleNamespace

import urgap.ext

# Urgap imports
import urgap.uconvert
import urgap.ucore
import urgap.ufile
import urgap.uftypes
import urgap.uinit
import urgap.util
import urgap.utree

from .ucredentials.ucredentials import UCredentialManager
from .ufile.ufile import UFile
from .ufile.ufile_io_manager import UFileIOManager
from .ufile.uuri import UUri
from .ufile_list import UFileList

# Importing into namespace a level higher
from .umeta import io
from .umeta.umeta import UMeta
from .unode import UNodeBase
from .unode_manager import UNodeManager
from .ureport.ureport import UReport
from .urun_dict import URunDict
from .utelemetry import UTelemetry
from .utrace import UTrace
from .uwid import UWIDGenerator

__all__ = [
    "UCredentialManager",
    "UFile",
    "UFileIOManager",
    "UFileList",
    "UMeta",
    "UNodeBase",
    "UNodeManager",
    "UReport",
    "URunDict",
    "UTelemetry",
    "UTrace",
    "UUri",
    "UWIDGenerator",
    "io",
    "util",
]

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    __version__ = None

__version_str__ = str(__version__)
package_dir = Path(__file__).parent
if not hasattr(sys, "version_info") or sys.version_info < (3, 10):
    msg = "Urgap2 requires Python 3.10 or later."
    raise RuntimeError(msg)

logger = logging.getLogger(__name__)
uwid_obj = urgap.UWIDGenerator()

home = Path(os.getenv("URGAP_HOME", str(Path.home() / ".urgap")))
info_box = [urgap.uinit.show_banner()]
info_format_string = "  {k: <23}: {v}"
info_box.append(info_format_string.format(k="version", v=f"{urgap.__version__}"))

if urgap.home.exists() is False:
    urgap.uinit.create_home_folder(home_dir_parent=urgap.home.parent)
else:
    info_box.append(info_format_string.format(k="urgap home", v=f"{home}"))

project_folder = Path.cwd()
info_box.append(info_format_string.format(k="project_folder", v=f"{project_folder}"))
info_box.append(
    info_format_string.format(k="urgap config", v=f"{urgap.home}/urgap.json"),
)

urgap.config = urgap.uinit.read_config()
urgap.uinit.load_certificates()

urgap.session_uwid = uwid_obj.generate_wid()
scratch_disk_base = urgap.uinit.set_scratch_disk_path(wid=urgap.session_uwid)
scratch_disk = scratch_disk_base  # Temporary as we will update during run with WID
info_box.append(info_format_string.format(k="scratch disk", v=scratch_disk_base))
logger.info("\n".join([*info_box]))

urgap.uinit.copy_resources_if_needed(
    target_dir=urgap.home,
    force=urgap.config.get("update_resources", False),
)

# Instances
urgap.instances = SimpleNamespace()
urgap.instances.unode_manager = urgap.UNodeManager()
urgap.instances.ufile_io_manager = urgap.UFileIOManager()
urgap.instances.ucredential_manager = urgap.UCredentialManager()
urgap.instances.utelemetry_manager = urgap.UTelemetry()
urgap.utl = urgap.instances.utelemetry_manager
urgap.instances.utree_querier = urgap.utree.UTreeQuerier(namespace=urgap.uftypes)

urgap.init_node = urgap.instances.unode_manager.init_unode
urgap.init_unode = urgap.instances.unode_manager.init_unode

atexit.register(urgap.ucore.shutdown_local_upi_servers)
if urgap.config.get("clean_scratch_at_exit", True) is True:
    atexit.register(urgap.ucore.clean_up_scratch_space)

atexit.register(urgap.ucore.shutdown_telemetry)