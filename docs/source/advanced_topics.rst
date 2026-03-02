.. _advanced_topics:

Advanced topics
===============

Dashboard
---------

pending...

UReport
-------

pending...

How to initialize
^^^^^^^^^^^^^^^^^

How to find your files
^^^^^^^^^^^^^^^^^^^^^^

How to visualize data flow in a jupyter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Programmatically accessing files using a wid 
--------------------------------------------

pending...

Implementing a new UNode
------------------------

pending...

How to use UNodes as remote services
------------------------------------

How to spin up a UNode as Microservice
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Urgap comes with a server that exposes UNodes as microservice. Each node has its own Port. The ports are calculated based on the number of UNode wrappers and are handled under the hood - no need to memorize any ports. However, it is therefore imperative that the microservice server and the executing client runs the same urgap version. In a nutshell, the ports are assigned based on teh sorted UNode names starting with 42000. Each Node allocates at least 10 ports with the port ending on "0" is reserved for "latest".

Starting a server exposing the UNodes is as simple as

.. code-block:: bash

   $ uctl run upi-server -n FilterTabularToCSV:1.0.0

How to access and trigger a UNode as Microservice
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Accessing the remote urgap server is as simple as adding a unode_parameter pointing to the remote instance, e.g.

.. code-block:: python

   import urgap

   ufiles = ["azure://dso.gsk.com/demo#data.csv"]
   # Initializing a list of ufiles with a URI string 
   urun_dict = urgap.URunDict(. # 
      # Run Config that contains two main configuration sections:
      parameters={
         "FilterTabularToCSV:1.0.0": {
               "-q": "`spectrum_id` > 3000",
         },
         # command line arguments for each processing node 
      },
      unode_parameters={
         "remote_url": "http://t2.eastus2.azmk8s.io",
         # Remote_url is the location of the microserice server..
      },
   )

How to expose UNodes as MCP servers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Starting a server exposing the UNodes as mcp server as well

.. code-block:: bash

   $ uctl run upi-server -n FilterTabularToCSV:1.0.0 --mcp <port_on_which_to_server_sse>


NOTE: we will be switching to streamable http soon.


How to use Urgap with different orchestration tools
---------------------------------------------------

Since urgap nodes require a URunDict, which can be serialized a json and list of uri string, any orchestration tool can be used. Sometimes, the Nodes need to be wrapped with a tiny layer of gluecode that turns the orchestration tool communciations into urgap node calls. E.g. Using ariflow, one would need to use XCOM to extract the output from the prior node as inputs for the next node and turn these then into a valid json and uri list. HEre you find some helper classes we wrote.

Using urgap in Prefect
^^^^^^^^^^^^^^^^^^^^^^

Using urgap in Apache Beam / GCP DataFlow
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using urgap in Nextflow
^^^^^^^^^^^^^^^^^^^^^^^

Using urgap in SnakeMake
^^^^^^^^^^^^^^^^^^^^^^^^
