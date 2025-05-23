"""Unode Manager class.

This module defines the UNode Manager class which is used to initialize UNodes
and check if their requirements are met, so they can actually be run.
"""

import copy
import importlib
import inspect
import logging
import re
import subprocess

from collections import UserDict
from pathlib import Path

from packaging.version import Version




class UNodeManager(UserDict):

    Responsible for initialization, requirement checking, and lookup of all UNodes and wrappers.
    """

    _3rd_party_test_commands = {
        "java": {
            "command": ["java", "-version"],
            "regex_pattern": None,
        },
        "dotnet": {
            "command": ["dotnet", "--list-sdks"],
            "regex_pattern": None,
        },
        "dotnet5": {
            "command": ["dotnet", "--list-sdks"],
            "regex_pattern": r"^5\.[0-9]*\.[0-9]* ",
        },
        "dotnet6": {
            "command": ["dotnet", "--list-sdks"],
            "regex_pattern": r"^6\.[0-9]*\.[0-9]* ",
        },
        "mono": {
            "command": ["mono", "--version"],
            "regex_pattern": r"compiler version 6\.[0-9]*\.[0-9]*",
        },
        "R-4.x.x": {
            "command": ["R", "--version"],
            "regex_pattern": r"^R version 4\.[0-9]*\.[0-9]* ",
        },
        "R-3.x.x": {
            "command": ["R", "--version"],
            "regex_pattern": r"^R version 3\.[0-9]*\.[0-9]* ",
        },
    }

    def __init__(self, external_resource_test_dict: dict | None = None) -> None:
        r"""Initialize the UNodeManager.

        Tracks availability of 3rd party installations, such as dotnet, java, mono, etc.
        Also tracks python and R package dependencies.

        Note:
            For example::
                {
                    "java": {
                        "command": ["java", "-version"],
                        "regex_pattern": None,
                    },
                    "dotnet5": {
                        "command": ["dotnet", "--list-sdks"],
                        "regex_pattern": r"^5\.[0-9]*\.[0-9]* ",
                    }
                }
            The key is used as lookup. Wrappers can specify their requirements in META_INFO, e.g::
                {
                    "requires": {
                        "other_uftypes": {
                            "other_dependencies": ("java",),
                            "python_packages: ["pymzml", "pyqms"]
                        },
                }
            The requirements are tracked based on specific input_file uftypes or for all other
            uftypes under `other_uftypes`.

        Args:
            external_resource_test_dict: Dictionary mapping external tools to commands and regexes.
                This can be used to override the default _3rd_party_test_commands mapping.
        """
        if external_resource_test_dict is not None:
            self._3rd_party_test_commands = external_resource_test_dict

        self.wrapper_lookup = self.generate_wrapper_lookup()
        self.assign_unode_ports()

        super().__init__()
        self.data = {
            "all": {},
            "by_type": {},
            "dev": {},
        }
        self.availability = {
            "python_packages": {},
            "r_packages": {},
            "other_dependencies": {},
        }
        self.node_availability_lookup = {}
        self._module_not_installed = set()
        self._requirements_not_met = set()

    def _check_for_module(self, pypackage: str) -> str | None:
        """Check if a Python package is installed and return its version.

        Args:
            pypackage: Name of the Python package.

        Returns:
            The installed version as a string, or None if not found.
        """
        try:
            return importlib.metadata.version(pypackage)
        except importlib.metadata.PackageNotFoundError:
            return None

    def _test_command(
    ) -> bool:
        """Test whether a system command runs successfully and matches a pattern.

        Args:
            command_list: List of command arguments to run.
            regex_pattern: Optional regex to match in the command output.

        Returns:
            True if the command runs (and matches regex, if given); otherwise False.
        """
        is_available = False
        try:
            proc = subprocess.run(
                command_list,
                text=True,
                capture_output=True,
                check=False,
            )
            if proc.returncode == 0:
                if regex_pattern is not None:
                    for line in proc.stdout.split("\n"):
                        if re.search(regex_pattern, line) is not None:
                            is_available = True
                else:
                    is_available = True
        except FileNotFoundError:
            pass
        return is_available

    def assign_unode_ports(self) -> None:
        """Assign ports to UNodes for remote serving in a deterministic fashion.

        Port assignments are stored in self.unode_port_mapping.
        """
        self.unode_port_mapping = {}
        last_assigned_port = first_port - 1
        for node_name in sorted(self.wrapper_lookup.keys(), key=sort_versions):
            if ":" not in node_name:
                continue
            if node_name.startswith("TestNode"):
                continue
            last_assigned_port = get_next_port(
            )
            self.unode_port_mapping[node_name] = last_assigned_port

    def generate_wrapper_lookup(self) -> dict:
        """Generate lookup for available wrappers and UNodes.

        Discovers all wrappers and unodes from the package directory.

        Returns:
            Dictionary mapping node_name or node_name:version to (module_path, class_name).
        """
        lookup = {}
        for _path in [wrapper_path, unode_path]:
            for wrapper in _path.glob("**/*.py"):
                if wrapper.stem.startswith("_"):
                    continue
                self._add_to_lookup(
                    lookup=lookup,
                    wrapper=wrapper,
                )
        return lookup

    def _add_to_lookup(
        self,
        lookup: dict,
        wrapper: Path,
    ) -> None:
        """Add a discovered wrapper or unode Python file to the lookup.

        Args:
            lookup: The lookup dictionary being constructed.
            wrapper: Path to the .py file for the wrapper/unode.
        """
        class_path_string = str(
        )
        spec = importlib.util.spec_from_file_location("node", wrapper)
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except ImportError:
            msg = f"Cannot import {mod} due to missing dependencies."
            return
        classes = inspect.getmembers(mod, inspect.isclass)
        node_name = None
        class_name = None
        for name, cls in classes:
            if mod.__name__ == cls.__module__:
                try:
                    meta_info = cls.META_INFO
                except AttributeError:
                    meta_info = cls().META_INFO
                node_name = meta_info["name"]
                class_name = name
                versions = meta_info.get("versions", None)
                break
        if versions is not None:
            version_objects = sorted(
            )
            for n, v in enumerate(version_objects):
                lookup[f"{node_name}:{v}"] = class_path_string, class_name
                if n == 0 and meta_info.get("is_old", None) is None:
                    lookup[f"{node_name}:latest"] = (
                        class_path_string,
                        class_name,
                    )
        else:
            lookup[node_name] = class_path_string, class_name

    def init_unode(self, unode: str) -> None:
        """Initialize a UNode and check its requirements.

        Imports the UNode/wrapper and checks for 3rd party and resource requirements.
        Import and requirement results are cached in self.data and self.node_availability_lookup.

        Args:
            unode: Name of the UNode or wrapper.

        Returns:
            Instance of the initialized UNode/wrapper class, or None if not found or requirements are missing.
        """
        if unode in self.wrapper_lookup:
            unode_obj = self.import_class(unode)
            if (
                self.node_availability_lookup[unode]["has_3rd_party_requirements"]
                and not self.node_availability_lookup[unode]["requirements_available"]
            ):
                msg = f"UNode {unode} could not be initialized because requirements are missing."
            if self.node_availability_lookup[unode]["resource_available"] is False:
                msg = f"UNode {unode} could not be initialized the resource/executable are missing."
            return unode_obj
        msg = f"UNode {unode} not available."
        for available_unode in self.data["all"]:
            if unode.upper() in available_unode.upper():
                msg = f"Did you mean {available_unode}?"
        )
        return None

        """Import and return the class for a given wrapper/unode.

        Updates self.data and checks dependencies via self.check_unode_dependencies.

        Args:
            unode: Name of the UNode or wrapper.

        Returns:
            The imported class for the UNode/wrapper.
        """
        class_path_string, class_name = self.wrapper_lookup[unode]
        module = importlib.import_module(module_path)
        unode_class = getattr(module, class_name)

        self.data["all"][unode] = unode_class
        try:
            engine_types = unode_class.META_INFO["engine_type"]
        except AttributeError:
            engine_types = unode_class().META_INFO["engine_type"]
        for engine_type in engine_types:
            if engine_type not in self.data["by_type"]:
                self.data["by_type"][engine_type] = {}
            self.data["by_type"][engine_type][unode] = unode_class
        unode_obj, node_availability_lookup = self.check_unode_dependencies(unode)
        self.node_availability_lookup.update(node_availability_lookup)
        return unode_obj

    def check_unode_dependencies(
        self,
        unode: str,
    ) -> tuple:
        """Check if all resource and dependency requirements are met for a UNode.

        Args:
            unode: Name of the UNode/wrapper.

        Returns:
            Tuple of (instance of the node class, requirements dict) in the form::

                {
                    <unode> : {
                        "resource_available": True,
                        "has_3rd_party_requirements": True,
                        "requirements_available": True,
                        "requirements_available_by_uftype": {
                            <uftype>: True,
                            <uftype2>: False,
                            "other_uftypes": True,
                        }
                    }
                }
        """
        tmp = {
            unode: {
                "resource_available": False,
                "requirements_available": False,
                "has_3rd_party_requirements": False,
                "requirements_available_by_uftype": {},
        }
        unode_obj = self.data["all"][unode]()
        unode_obj.META_INFO = copy.deepcopy(self.data["all"][unode].META_INFO)
        if ":" in unode:
            unode_name, unode_version = unode.split(":")
            unode_obj.META_INFO["unode_version"] = unode_version
            unode_obj.META_INFO["unode_name"] = unode_name
            unode_obj.META_INFO["unode_full_identifier"] = unode
        else:
            unode_obj.META_INFO["unode_version"] = None
            unode_obj.META_INFO["unode_name"] = unode
            unode_obj.META_INFO["unode_full_identifier"] = unode

        if unode_obj.META_INFO["unode_version"] == "latest":
                "to be supplied by "
            )
            # exe_path supplied by urun_dict['unode_parameters']['latest_exe_paths']
            tmp[unode]["resource_available"] = None
        elif unode_obj.exe_path is not None:
            tmp[unode]["resource_available"] = (
                unode_obj.exe_path.exists() and unode_obj.exe_path.is_file()
            )

        for uftype, requirements in unode_obj.META_INFO.get("requires", {}).items():
            is_available = self.check_requirements(requirements, unode)
            tmp[unode]["requirements_available_by_uftype"][uftype] = is_available

        if len(tmp[unode]["requirements_available_by_uftype"].keys()) == 0:
            tmp[unode]["has_3rd_party_requirements"] = False
        else:
            tmp[unode]["has_3rd_party_requirements"] = True

        tmp[unode]["requirements_available"] = all(
            v for k, v in tmp[unode]["requirements_available_by_uftype"].items()
        )
        return unode_obj, tmp

    def check_requirements(
        self,
        requirements: dict,
        unode: str | None = None,
    ) -> bool:
        """Check if all requirements for the given wrapper are satisfied on the system.

        Args:
            requirements: Dictionary with requirement keys, e.g., from META_INFO["requires"][<uftype>].
            unode: UNode name (optional, used for debug logging).

        Returns:
            True if all requirements are met, otherwise False.
        """
        availabilities = []
        availabilities = self._check_python_packages(
            availabilities=availabilities,
            requirements=requirements,
        )
        availabilities = self._check_other_dependencies(
            availabilities=availabilities,
            requirements=requirements,
            unode=unode,
        )
        return all(availabilities)

    def _check_python_packages(self, availabilities: list, requirements: dict) -> list:
        """Check if all required Python packages are installed and of a compatible version.

        Args:
            availabilities: List of booleans (for cumulative status).
            requirements: Requirements dict with 'python_packages' key.

        Returns:
            Updated list of booleans indicating status for each Python package.
        """
        for pypackage in requirements.get("python_packages", []):
            self.availability["python_packages"][pypackage] = False
            with_operator = False
            operators = {
                "==": lambda version: version.__eq__,
                ">=": lambda version: version.__ge__,
                "<=": lambda version: version.__le__,
                ">": lambda version: version.__gt__,
                "<": lambda version: version.__lt__,
                "!=": lambda version: version.__ne__,
            }
            for operator, version_function in operators.items():
                if operator in pypackage:
                    with_operator = True
                    pypackage_clean, required_pypackage_version = pypackage.split(
                    )
                    package_version = self._check_for_module(pypackage_clean)
                    self.availability["python_packages"][pypackage] = version_function(
                    )(required_pypackage_version)
                    break
            if with_operator is False:
                package_version = self._check_for_module(pypackage)
                if package_version is not None:
                    self.availability["python_packages"][pypackage] = True
            availabilities.append(self.availability["python_packages"][pypackage])
        return availabilities

    def _check_other_dependencies(
    ) -> list:
        """Check if all other (non-Python) dependencies are available.

        Args:
            availabilities: List of booleans (for cumulative status).
            requirements: Requirements dict with 'other_dependencies' key.
            unode: UNode name (for debug logging).

        Returns:
            Updated list of booleans indicating status for each dependency.
        """
        for resource in requirements.get("other_dependencies", []):
            if resource not in self._3rd_party_test_commands:
                msg = (
                    f"Wrapper {unode} contains requirements {resource} and we don't"
                    " know how to validate this. Please reach out to the dev team "
                    f" Currently, availabililty can be tested for {self._3rd_party_test_commands.keys()}"
                )
                is_available = None
            else:
                if resource not in self.availability["other_dependencies"]:
                    command_list = self._3rd_party_test_commands[resource]["command"]
                    regex_pattern = self._3rd_party_test_commands[resource].get(
                    )
                    is_available = self._test_command(
                    )
                    self.availability["other_dependencies"][resource] = is_available
                availabilities.append(self.availability["other_dependencies"][resource])
        return availabilities