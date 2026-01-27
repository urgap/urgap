Please structure tests as following:

unittest folder structure should mirror the package, ie
unittests/         # containing top level urgap module tests
unittests/wrapper/ # containing tests for wrappers

within those folders create files with the following syntax
unittests/test_io_{function_name_within_io_py)

e.g. unittests/test_io_construct_exe_path.py
