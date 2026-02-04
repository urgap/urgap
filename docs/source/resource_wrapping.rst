Writing a UNode
===============

The UNode is the central piece of resource wrapping in our wrapping framework Urgap.

UNode Location
--------------

All UNodes are located in the following directory: `urgap/unodes/`


Choose a Template
-----------------

The recommended starting point is the ``filter_tabular_to_csv`` UNode: `urgap/unodes/filter_tabular_to_csv/filter_tabular_to_csv.py`

Copy this implementation and adapt it for your use case.


UNode Structure
---------------

A UNode is a Python class that has the following components:

- ``META_INFO`` dictionary
- ``__init__`` method
- ``preflight`` method
- optional ``postflight`` method

META_INFO Dictionary
^^^^^^^^^^^^^^^^^^^^

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

preflight Method
^^^^^^^^^^^^^^^^

The ``preflight`` method prepares the command-line execution.

- The command is stored in: `utrace.urun_dict.command_list`
- Build the command according to the resource CLI
- Input and output file paths can be accessed using: `utrace.output_files.get_path_objects_by_uftype(uftype)`
- Runtime parameters are available via: `utrace.urun_dict.parameters`

postflight Method
^^^^^^^^^^^^^^^^^

The optional ``postflight`` method is executed after the resource finishes and can:

- Map output files if not handled by the CLI
- Move or rename output files to expected output paths