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


How to extend
--------------

How to build a new UNode
~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Location**

   All UNodes are located in the ``urgap/unodes`` subfolder

2. **Configure META_INFO dictionary**

   * ``name``: Must match the class name exactly
   * ``versions``: List of supported resource/executable versions

     * ``exe_path``: Path to the resource (stored in ``urgap/resources`` folder)
     * For system-level resources: prefix ``exe_path`` with ``$`` (urgap automatically locates it using ``which``)

3. **Define input and output file types**

   All files in urgap require a defined type called ``uftype`` (defined in ``urgap/uftype.py``).

   * Specify minimum and maximum file counts for each type
   * Use ``-1`` for unlimited files

   **input_uftypes**:

   * Can use the ``ANY`` namespace for flexible matching

   **output_uftypes**:

   * At least one output type must have a minimum count > 0

4. **Implement the preflight method**

   Executes before running the resource:

   * Validate inputs and perform setup checks
   * Generate configuration files as needed
   * Build the command list according to the resource's CLI
   * Store the command list in ``utrace.urun_dict.command_list``

5. **Implement the postflight method**

   Executes after running the resource:

   * Perform post-processing operations
   * Move or rename output files as required
   * Ensure output files are placed at the expected ``output_file`` paths


Extending UFiles
~~~~~~~~~~~~~~~~

How to add a new I/O file class
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**1. Location**

   All file I/O classes are located in the ``urgap/ufile/io`` folder

**2. Implement required methods**

   Your new I/O class must implement these methods:

   * ``download``: Download files from remote storage
   * ``upload``: Upload files to remote storage
   * ``remote_object_exists``: Check if a remote object exists
   * ``list_container_items``: List items in a container

**3. Register the new schema**

   After creating your I/O class, register it in three locations:

   * ``urgap/ufile/ufile_io_manager.py``:
     Add schema mapping in the ``__init__`` method

   * ``urgap/ufile/uuri.py``:
     Add schema to the ``check_uri_scheme_exists`` method

   * ``urgap/ufile/ufile.py``:
     Add schema to the ``init_io_class`` method


Add new uftypes
~~~~~~~~~~~~~~~

**What are uftypes?**

Uftypes define file type identifiers in urgap. They are organized into namespaces using Python's ``SimpleNamespace`` and are defined in ``urgap/uftypes.py``.

**Structure**

Uftypes follow a hierarchical naming convention:

* Format: ``namespace.subnamespace.UFTYPE_NAME = ".extension"``
* Example: ``proteomics.dbsearch.COMET_MZID = ".comet.mzid"``

**How to add a new uftype**

1. **Choose or create a namespace**

   Existing namespaces include:

   * ``proteomics``: Mass spectrometry proteomics data
   * ``transcriptomics``: RNA sequencing and gene expression data
   * ``flow_cytometry``: Flow cytometry data and analysis
   * ``ms``: General mass spectrometry data
   * ``mx``: Metabolomics data
   * ``beacon``: Imaging data
   * ``molecular_structure``: Protein and molecular structure files
   * ``interdock``: Molecular docking files
   * ``compression``: Archive formats
   * ``exp_design``: Experimental design metadata
   * ``any``: Generic file types

   Create a new namespace if your file types don't fit existing categories:

   ```python
   my_namespace = types.SimpleNamespace()
