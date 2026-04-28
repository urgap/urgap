"""Addon uftypes (filetypes) for the urgap workflow.

This module allows users to define additional or custom uftypes that extend or override the default types in urgap.uftypes.
Place your custom filetype definitions here to have them automatically merged into the urgap type tree at runtime.
"""

import types

# Urgap addon ===============================================================
addon = types.SimpleNamespace()
addon.ANY = "addon.ANY"
addon.TEST_FILE1 = ".addon.test_file1"
