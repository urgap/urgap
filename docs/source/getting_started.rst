Getting started
===============


Installation (stable version)
-----------------------------

Installation from pypi
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash


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


* GitHub version: Starting from your command line, the easiest way is to clone the GitHub repo.

.. code-block:: bash



.. _GitHub:



.. code-block:: bash



You might need administrator privileges to write in the Python site-package folder.
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



.. code-block:: bash



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

        -p 27017:27017 \
        -v ~/mongo/data:/data/db \
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
        -v ~/minio/data:/data \
        quay.io/minio/minio server /data \
        --console-address ":9001"