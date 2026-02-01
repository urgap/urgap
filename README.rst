Urgap2 - node wrapping framework
=================================

Urgap is a node wrapping framework, containing abstraction layers for data and meta data, extensive
re-run skipping logic and data versioning. Urgap can be incorporated with any scheduling/pipelining
tool making pipeline development independent from business logic and data storage, while offering 
standardized logging and execution, which makes monitoring and debugging easy.

Urgap gives us the governance constraints required for a decentralized data domain autonomy as
Urgap will enforce shared common data IO for storage, a common meta data capturing process in form of
an interface thus can be plugged into any existing processes and finally global data lineages. 

|build-status-azure|

.. |build-status-azure| image:: https://dev.azure.com/DevOps-RD/RD-DSO/_apis/build/status%2Fgsk-tech.urgap?repoName=gsk-tech%2Furgap&branchName=refs%2Fpull%2F388%2Fmerge
   :target: https://dev.azure.com/DevOps-RD/RD-DSO/_build?definitionId=13513
   :alt: ADO CI status


How to Setup
------------

Prerequisites
~~~~~~~~~~~~~

We recommend using a virtual environment for Python projects. This guide uses `uv` for dependency management.

Installation
~~~~~~~~~~~~

**Basic Installation** (local file system access only):

.. code-block:: bash

    uv pip install -e .

**With Cloud Storage Support:**

.. code-block:: bash

    uv pip install -e ".[cloud]"

**With All Optional Dependencies:**

.. code-block:: bash

    uv pip install -e ".[all]"

Available extras include:

* ``cloud``: Azure and Google Cloud storage backends
* ``all``: All optional dependencies

Running Tests
~~~~~~~~~~~~~

Install test dependencies:

.. code-block:: bash

    uv pip install pytest

Run the test suite:

.. code-block:: bash

    pytest tests

Quickstart: Writing Your First Pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The best way to learn urgap is through a complete example. Check out the end-to-end filter CSV pipeline:

* **Location:** `tests/integrationtests/end2end/test_filter_csv_pipeline.py`
* **What it demonstrates:** Complete pipeline setup, node configuration, and execution
* **Requirements:** Everything needed to run this example is included in the repository

This example can be run entirely on your local machine without any external dependencies.

To run the example:

.. code-block:: bash

    pytest tests/integrationtests/end2end/test_filter_csv_pipeline.py


Writing a UNode
~~~~~~~~~~~~~~~

The UNode is the central piece of resource wrapping in our wrapping framework Urgap.

**UNode Location**

All UNodes are located in the following directory: `urgap/unodes/`


**Choose a Template**

The recommended starting point is the ``filter_tabular_to_csv`` UNode: `urgap/unodes/filter_tabular_to_csv/filter_tabular_to_csv.py`

Copy this implementation and adapt it for your use case.


**UNode Structure**

A UNode is a Python class that has the following components:

- ``META_INFO`` dictionary
- ``__init__`` method
- ``preflight`` method
- optional ``postflight`` method

**META_INFO Dictionary**

``name``
   Must match the class name.

``wrapper_version``
   Version of the wrapper implementation.

``versions``
   Defines versions of the wrapped resource or executable.

``exe_path`` must point to a file located in ``urgap/resources``.
If the wrapped resource is a system resource, prefix the path with ``$``:

.. code-block:: python

   "exe_path": "$fpreppy"


**Input and Output UFTypes**

Urgap identifies files using **uftypes**, which are file-type namespaces.

Uftypes are defined in: `urgap/uftypes.py`


**UFTYPE Rules**

- ``output_uftypes`` must be defined explicitly
- ``input_uftypes`` may use ``ANY`` namespaces
- Each uftype must define:
  
  - ``min``: minimum number of files
  - ``max``: maximum number of files (``-1`` means unlimited)

- Every output uftype must have ``min > 0``

**preflight Method**

The ``preflight`` method prepares the command-line execution.

- The command is stored in: `utrace.urun_dict.command_list`
- Build the command according to the resource CLI
- Input and output file paths can be accessed using: `utrace.output_files.get_path_objects_by_uftype(uftype)`
- Runtime parameters are available via: `utrace.urun_dict.parameters`

**postflight Method**

The optional ``postflight`` method is executed after the resource finishes and can:

- Map output files if not handled by the CLI
- Move or rename output files to expected output paths


Documentation
--------------

Please use sphinx in the docs folder


.. note::

    Currently CI does not include pushing the documentation to readthedocs, therefore please 
    #. checkout the repo
    #. pip install -e .
    #. cd docs
    #. make html
    #. open docs/build/index.html
