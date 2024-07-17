"""Unode Manager class.

This module defines the UNode Manager class which is used to initialize UNodes
and check if their requirements are met, so they can actually be run.
"""

import importlib
import inspect
import logging
import re
import subprocess
from collections import UserDict



class UNodeManager(UserDict):

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



        Args:
        """
        if external_resource_test_dict is not None:
            self._3rd_party_test_commands = external_resource_test_dict

        self.wrapper_lookup = self.generate_wrapper_lookup()

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

        try:
        except importlib.metadata.PackageNotFoundError:
            return None

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

    def generate_wrapper_lookup(self) -> dict:


        Returns:
        """
        lookup = {}
        return lookup




        Returns:
        """



        Args:
        """
        module = importlib.import_module(module_path)
        unode_class = getattr(module, class_name)


    def check_unode_dependencies(
        self,
        unode: str,

        Args:

        Returns:
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

            is_available = self.check_requirements(requirements, unode)
            tmp[unode]["requirements_available_by_uftype"][uftype] = is_available

        if len(tmp[unode]["requirements_available_by_uftype"].keys()) == 0:
            tmp[unode]["has_3rd_party_requirements"] = False
        else:
            tmp[unode]["has_3rd_party_requirements"] = True

        tmp[unode]["requirements_available"] = all(
        )

    def check_requirements(
        self,
        requirements: dict,
    ) -> bool:

        Args:

        Returns:
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
                if operator in pypackage:
                    with_operator = True
                    pypackage_clean, required_pypackage_version = pypackage.split(
                    )
                    package_version = self._check_for_module(pypackage_clean)
                    break
            if with_operator is False:
                package_version = self._check_for_module(pypackage)
                if package_version is not None:
                    self.availability["python_packages"][pypackage] = True
            availabilities.append(self.availability["python_packages"][pypackage])
        return availabilities

        for resource in requirements.get("other_dependencies", []):
                    f"Wrapper {unode} contains requirements {resource} and we don't"
                    " know how to validate this. Please reach out to the dev team "
                    f" Currently, availabililty can be tested for {self._3rd_party_test_commands.keys()}"
                )
                is_available = None
            else:
                    command_list = self._3rd_party_test_commands[resource]["command"]
                    regex_pattern = self._3rd_party_test_commands[resource].get(
                    )
                    is_available = self._test_command(
                    )
                    self.availability["other_dependencies"][resource] = is_available
                availabilities.append(self.availability["other_dependencies"][resource])
        return availabilities