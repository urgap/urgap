.. _getting_started:

Quickstart
==========

Running pytest
--------------

If you have installed from source / github, then you can test your installation by invoking pytest, e.g.

.. code-block:: bash

    pytest tests

If you need a fresh installation of all requirements including a fresh virtual environment, run

.. code-block:: bash

    rm -rf .venv && pip install -e ".[all]"



Executing example scripts
-------------------------

Urgap comes with a set of example scripts covering single node execution to fully-fledged pipelines.
Have a look in the example_scripts folder to get started with more advanced workflows.
Most example scripts come with a click interface, for help simply run python scriptXXX.py --help
