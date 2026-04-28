Addon uftypes for urgap
=======================

This document describes how to use the `uftypes_addon.py` file to extend or override filetypes (uftypes) in the urgap workflow.

Purpose
-------
The `uftypes_addon.py` module allows users to define additional or custom uftypes that are automatically merged into the urgap type tree at runtime. This is useful for supporting new filetypes or overriding existing ones without modifying the core `uftypes.py`.

Usage
-----
1. Open or create the `urgap/uftypes_addon.py` file in your urgap installation.
2. Define your custom filetypes as attributes or namespaces, following the structure used in `uftypes.py`.
3. When urgap runs, your custom types will be merged with the core types.

Example
-------
.. code-block:: python

    import types
    addon = types.SimpleNamespace()
    addon.ANY = "addon.ANY"
    addon.TEST_FILE1 = ".addon.test_file1"

Notes
-----
- Only public attributes (not starting with an underscore) are merged.
- Addon types override core types with the same name.
- This mechanism allows for flexible extension of supported filetypes.

