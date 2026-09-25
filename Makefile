ifeq ($(URGAP_HOME),)
	URGAP_HOME := $(HOME)
endif

RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[0;33m
OFF=\033[0m

help:
	@echo "Urgap MakeFile Options"
	@echo " - ${GREEN}tests${OFF}:       run full testsuit"
	@echo " - ${GREEN}sphinx-html${OFF}: create docu in docs folder. Requires pip install -e ./[docs]"

tests:
	@echo "Running Unittests using pytest"
	uv run --extra dev pytest tests

zip-exes:
	@echo "Creating new zip files and calculating md5s for new exes"
	@echo "----[to be implemented ]----"

UV_DOCS = uv run --extra docs --extra cloud
AUTO_GEN1 = $(UV_DOCS) python3 parse_example_scripts.py
AUTO_GEN2 = $(UV_DOCS) python3 parse_third_party.py
# You can set these variables from the command line.
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= cd docs;$(AUTO_GEN1);$(AUTO_GEN2);$(UV_DOCS) sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

sphinx-html:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
