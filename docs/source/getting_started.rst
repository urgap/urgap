Getting started
===============


Installation (stable version)
-----------------------------

Installation from pypi
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    user@localhost:~$ pip install urgap


Installation from source
^^^^^^^^^^^^^^^^^^^^^^^^

1. Download urgap using `GitHub`_ **or** the zip file:

* GitHub version: Starting from your command line, the easiest way is to clone the GitHub repo.

.. code-block:: bash

    user@localhost:~$ git clone https://github.com/urgap/urgap.git

* ZIP version: Alternatively, download and extract the `urgap zip file`_

.. _GitHub:
   https://github.com/urgap/urgap

.. _urgap zip file:
   https://github.com/urgap/urgap/archive/main.zip

2. Next, navigate into the urgap folder and install the requirements. Use virtualenv for maximum convenience. We recommend using uv for the installation, but pip can be used as well.

* uv version

.. code-block:: bash

    user@localhost:~$ cd urgap
    # base version
    user@localhost:~/urgap$ uv sync
    # with doc dependencies
    user@localhost:~/urgap$ uv sync --extra docs
    # with every runtime extra
    user@localhost:~/urgap$ uv sync --extra all
    # everything, including the test and doc toolchains (contributor setup)
    user@localhost:~/urgap$ uv sync --all-extras

* pip version

.. code-block:: bash

    user@localhost:~$ cd urgap
    # base version
    user@localhost:~/urgap$ pip install .
    # with doc dependencies
    user@localhost:~/urgap$ pip install ".[docs]"
    # with every runtime extra
    user@localhost:~/urgap$ pip install ".[all]"
    # everything, including the test and doc toolchains (contributor setup)
    user@localhost:~/urgap$ pip install ".[all,dev,docs]"
    