.. _getting_started:

Quickstart
==========

Running pytest
--------------

If you have installed from source / github, then you can test your installation by invoking tox, e.g.

.. code-block:: bash

    tox -e py39

If you need a fresh installation of all requirements, run

.. code-block:: bash

    tox -r -e py39


Using UFiles, the data abstraction layer
----------------------------------------

.. code-block:: python

    import urgap
    uri = "https://www.tagesschau.de/multimedia/bilder#ukraine436~_v-gross20x9.jpg"
    ufile = urgap.UFile(uri=uri)
    # initalizes UFile with remote location
    print(ufile.path)
    # Accessing the path attribute automatically downloads the file
    
    ufile.tags.update({"source": "tagesschau.de"})
    # Update tags locally

    from pathlib import Path

    ufile.rebase(f"file://{Path.home()}/Desktop/")
    # changing ufile schema to file (Python) and location to ~/Desktop

    ufile.upload()
    # uploads scratch file to new rebased destination 

.. note::

    Please refer to :ref:`ufile` for more details on, e.g.
    
    #. Why is there a # in uri?
    #. How are tags handled 



Executing example scripts
-------------------------

Urgap comes with a set of example scripts covering single node execution to fully-fledged pipelines.
Have a look in the example_scripts folder to get started with more advanced workflows.
Most example scripts come with a click interface, for help simply run python scriptXXX.py --help
