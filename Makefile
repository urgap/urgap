endif

RED=\033[0;31m
OFF=\033[0m

new-unode:
	@echo ""
	@echo "Please fill out the Questions"
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

tests:
	@echo "Running Unittests using pytest"
	pytest tests

zip-exes:
	@echo "Creating new zip files and calculating md5s for new exes"
	@echo "----[to be implemented ]----"

black: