.. _utree:

UTree Class
###########

.. autoclass:: urgap.utree.UTreeQuerier
   :members:

   .. automethod:: __init__

Uftypes Namespace Structure
==========================

The uftypes system is organized as a folder-based namespace. Each filetype namespace is a separate Python module in the ``urgap/uftypes/`` folder.

To add or extend filetypes, simply create a new module (e.g., ``mytype.py``) in the ``urgap/uftypes/`` folder and define your types as attributes or nested namespaces.

Example structure:

.. code-block:: text

    urgap/
        uftypes/
            __init__.py
            any.py
            test.py
            mytype.py

Example module (mytype.py):

.. code-block:: python

    import types
    mytype = types.SimpleNamespace()
    mytype.ANY = "mytype.ANY"
    mytype.SPECIAL = ".mytype.special"

All modules in this folder are automatically loaded and merged into the uftype tree at runtime.
