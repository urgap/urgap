ifeq ($(URGAP_HOME),)
	URGAP_HOME := $(HOME)
endif

RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[0;33m
OFF=\033[0m

help:
	@echo "Urgap MakeFile Options"
	@echo " - ${GREEN}new-unode${OFF}:   create a new unode"
	@echo " - ${GREEN}tests${OFF}:       run full testsuit"
	@echo " - ${GREEN}black${OFF}:       run black on src code with the right parameters and exclude certain files"
	@echo " - ${GREEN}sphinx-html${OFF}: create docu in docs folder. Requires pip install -e ./[docs]"

new-unode:
	@echo ""
	@echo "Please fill out the Questions"
	@echo "Will create urgap/wrapper/<your_tool_name>"
	@echo "Urgap Home is set to be ${URGAP_HOME}"
	@echo ""
	@echo ".------------------- ------ -- ---         -"
	@echo "| How to :"
	@echo "|"
	@echo "| wrapper_name:"
	@echo "|   The wrapper name should include the version name following"
	@echo "|   pep8 convention. ie should be importable as a python module"
	@echo "|"
	@echo "| tool:"
	@echo "|   Defining the wrapper name ${RED}without${OFF} version, which will be used"
	@echo "|   as a top level folder to group different versions of the same tool"
	@echo "|   This can also be used to group a type of wrapper into a folder for convenience,"	
	@echo "|   e.g. io for filter_csv or echo_to_file etc"	
	@echo "|"
	@echo "| version:"
	@echo "|   Any string"
	@echo "|"
	@echo "| release data:"
	@echo "|   Any string"
	@echo "|"
	@echo "| translation_style:"
	@echo "|   Tools will mostly keep their parameters over different versions."
	@echo "|   The translation style is in the format of {tool}_style_{X}"
	@echo "|"
	@echo "| exe_<platform>:"
	@echo "|   The executables are stored in ${URGAP_HOME}/<platform>/<architecture>"
	@echo "|   and the executable name should be defined here"
	@echo "|"
	@echo "| platform_independent: [True, False]"
	@echo "|"
	@echo "| engine_type: "
	@echo "|   ['db-search', 'open-search', 'denovo-search', 'converter', 'test_engine']"
	@echo "|"
	@echo "| citation: "
	@echo "|   Please be the appropriate citation! This is ${RED}very important${OFF} "
	@echo "|"
	@echo "| Note:"
	@echo "|   - Files will be overwritten if already exist"
	@echo "|"
	@echo "+------------------ ---- --    -"
	@echo ""
	cookiecutter -f urgap/wrapper_template -o urgap/wrappers

tests:
	@echo "Running Unittests using pytest"
	pytest tests

zip-exes:
	@echo "Creating new zip files and calculating md5s for new exes"
	@echo "----[to be implemented ]----"

black:
	black --line-length 88 --exclude '(urgap/wrapper_template/|.tox)' .


AUTO_GEN1 = /usr/bin/env python3 parse_example_scripts.py
AUTO_GEN2 = /usr/bin/env python3 parse_third_party.py
# You can set these variables from the command line.
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= cd docs;$(AUTO_GEN1);$(AUTO_GEN2);sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

sphinx-html:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
