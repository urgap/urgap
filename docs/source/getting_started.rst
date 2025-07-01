Getting started
===============


Installation (stable version)
-----------------------------

Installation from pypi
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    user@localhost:~$ pip install urgap2

Installation from github
^^^^^^^^^^^^^^^^^^^^^^^^

TODO
    #. Clone github 
    #. Checkout master
    #. install following dev description below
    #. enjoy latest pypi release 



Installation (development environment)
--------------------------------------

Installation from source
^^^^^^^^^^^^^^^^^^^^^^^^

1. Download Urgap using `GitHub`_ **or** the zip file:

* GitHub version: Starting from your command line, the easiest way is to clone the GitHub repo.

.. code-block:: bash

    user@localhost:~$ git clone https://github.com/fu/urgap2.git

* ZIP version: Alternatively, download and extract the `urgap zip file`_

.. _GitHub:
   https://github.com/fu/urgap2

.. _urgap zip file:
   https://github.com/fu/urgap2/archive/master.zip

2. Next, navigate into the Urgap2 folder and install the requirements. Use virtualenv for maximum convenience.

.. code-block:: bash

    user@localhost:~$ cd urgap2
    user@localhost:~/urgap$ pip install -r requirements.txt


You might need administrator privileges to write in the Python site-package folder.
On Linux or OS X, use ``"sudo python3 -m pip install ."`` or write into a user folder
by using this command ``"python3 -m pip install . --user"``. On Windows, you have to
start the command line with administrator privileges.

Setting up mongoDB and/or minio
-------------------------------

Setting up a local minio on bare metal
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

on macOS
""""""""

Installing the server

.. code-block:: bash

    brew install minio


Installing the client, required to interact with thte server, e.g configure it

.. code-block:: bash

    brew install minio/stable/mc


Starting the server and pointing it to urgap test data folder.

.. code-block:: bash

    minio server <your_path_to_urgap>/urgap/tests


Adding our test server to the client 

.. code-block:: bash

    mc config host add test http://127.0.0.1:9000 minioadmin minioadmin


Note: url and root login and password are displayed when the server is started

Adding test user to the server and assigning the right policy

.. code-block:: bash

    mc admin user add test minio_anyone minio_anyone
    mc admin policy set test readwrite user=minio_anyone

Adding login and password to your shell login 

.. code-block:: bash

    export uuser_minio=minio_anyone
    export upassword_minio=minio_anyone

Note: After setting up the server, policies and user credentials are stored inside minio, 
so restart does not require the above to be done.


Using Docker
^^^^^^^^^^^^

mongoDB
""""""""

.. code-block:: bash

    docker run \
        -p 27017:27017 \
        -v ~/mongo/data:/data/db \
        --name urgap-mongo \
        mongo:latest


MinIO
"""""

.. code-block:: bash

    export uuser_minio="admin1"
    export upassword_minio="$uper$3cureP4ssw0rd"

    docker run \
        -p 9000:9000 \
        -p 9001:9001 \
        -e "MINIO_ROOT_USER=$uuser_minio" \
        -e "MINIO_ROOT_PASSWORD=$upassword_minio" \
        --name urgap-minio \
        -v ~/minio/data:/data \
        quay.io/minio/minio server /data \
        --console-address ":9001"