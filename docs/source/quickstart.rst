.. _getting_started:

Quickstart
==========

Running pytest
--------------





Using UFiles, the data abstraction layer
----------------------------------------

.. code-block:: python

    uri = "https://www.tagesschau.de/multimedia/bilder#ukraine436~_v-gross20x9.jpg"
    # initalizes UFile with remote location
    print(ufile.path)
    # Accessing the path attribute automatically downloads the file
    
    # Update tags locally

    from pathlib import Path

    ufile.rebase(f"file://{Path.home()}/Desktop/")
    # changing ufile schema to file (Python) and location to ~/Desktop

    ufile.upload()
    # uploads scratch file to new rebased destination 





Executing example scripts
-------------------------
