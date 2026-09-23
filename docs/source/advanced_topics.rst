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
         # Remote_url is the location of the microservice ...
      },
   )

How to expose UNodes as MCP servers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Starting a server exposing the UNodes as mcp server as well

.. code-block:: bash

   $ uctl run upi-server -n FilterTabularToCSV:1.0.0 --mcp <port_on_which_sse_is_served>


NOTE: we will be switching to streamable http soon.


How to use Urgap with different orchestration tools
---------------------------------------------------

Since urgap nodes require a URunDict, which can be serialized a json and list of uri string, any orchestration tool can be used. Sometimes, the Nodes need to be wrapped with a tiny layer of gluecode that turns the orchestration tool communciations into urgap node calls. E.g. Using ariflow, one would need to use XCOM to extract the output from the prior node as inputs for the next node and turn these then into a valid json and uri list. Here you find some helper classes we wrote.

Using urgap in Prefect
^^^^^^^^^^^^^^^^^^^^^^

Using urgap in Apache Beam / GCP DataFlow
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using urgap in Nextflow
^^^^^^^^^^^^^^^^^^^^^^^

Using urgap in SnakeMake
^^^^^^^^^^^^^^^^^^^^^^^^

Relocating files without processing them
----------------------------------------

Sometimes a file only needs to move from one storage location to another, with
no UNode touching its content. A UFile keeps its storage location and its
object name as separate parts of its UUri, so rebasing a UFile onto a new
storage base UUri relocates it while keeping its name:

.. code-block:: python

   import urgap

   ufiles = urgap.UFileList.from_uri_list(
      ["azure://account-a.gsk.com/container#experiment_42/data.csv"],
   )
   ufiles.rebase(storage_base_uri="azure://account-b.gsk.com/container")
   # -> azure://account-b.gsk.com/container#experiment_42/data.csv

The same is available on the command line, the target storage base UUri comes
first and is followed by any number of source UUris:

.. code-block:: bash

   $ uctl rebase uris azure://account-b.gsk.com/container \
        azure://account-a.gsk.com/container#experiment_42/data.csv

The source is left untouched, a copy is placed at the target under the very
same object name. The ``uftype`` tag survives, so the relocated UFile stays
consumable by every UNode that accepts it, while dynamic tags such as hashes
and ``parent_*`` provenance are dropped: a rebase is a transfer and not a run,
so nothing is recorded in UMeta.

NOTE: rebasing downloads the file to the scratch disk and uploads it to the
target, so a large file is pulled through the machine performing the rebase.

Pulling work from a message bus
-------------------------------

Instead of being called directly, urgap can wait for work on a message bus.
Two workers ship with urgap:

.. code-block:: bash

   # run a UNode whenever a message asks for it
   $ uctl run upi-server -n FilterTabularToCSV:1.0.0 \
        --via-message-bus azure-servicebus://my-namespace.servicebus.windows.net

   # relocate files whenever a message asks for it
   $ uctl run rebase-worker --via-message-bus gcp-pubsub://my-gcp-project --stay-alive

Both take a message bus ucredentials key whose **scheme selects the transport**,
so the same worker code runs on either cloud:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Transport
     - cred_key
   * - Azure Service Bus
     - ``azure-servicebus://<namespace>.servicebus.windows.net``
   * - GCP Pub/Sub
     - ``gcp-pubsub://<project-id>``

The worker creates its topic and subscription if they do not exist yet and
attaches a filter on the ``subscription_key`` so it only receives the messages
meant for it. A message that is handled successfully is settled and a message
whose handler failed is released back to the subscription for redelivery.

Message format
^^^^^^^^^^^^^^

The routing key lives at the top level, next to the payload the worker needs:

.. code-block:: json

   {
      "uuid": "a-correlation-id",
      "subscription_key": "urgap_rebase",
      "consumer_kwargs": {
         "input_uris": ["azure://account-a.gsk.com/container#experiment_42/data.csv"],
         "storage_base_uri": "azure://account-b.gsk.com/container",
         "config": {},
         "ucredentials": []
      }
   }

``subscription_key`` is ``urgap_rebase`` for the rebase worker and the
``unode_full_identifier`` (e.g. ``FilterTabularToCSV:1.0.0``) for the UNode
worker, which expects ``wid``, ``unode_full_identifier``, ``urun_dict``,
``input_uris``, ``config`` and ``ucredentials`` in its ``consumer_kwargs``. Any
``config`` and ``ucredentials`` a message brings along are applied before the
work starts, so a worker does not need the credentials of both storage
locations baked into its own environment.

When a completion topic is configured, every handled message is echoed to it
with the resulting URIs added, so a producer can wait for the result:

.. code-block:: json

   {
      "uuid": "a-correlation-id",
      "subscription_key": "urgap_rebase",
      "consumer_kwargs": {"...": "..."},
      "custom_message": {
         "output_uris": ["azure://account-b.gsk.com/container#experiment_42/data.csv"]
      }
   }

Configuration
^^^^^^^^^^^^^

The topics come from the urgap config and can be overridden per worker with
``--topic`` and ``--completion-topic``:

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - Config key
     - Meaning
   * - ``service_bus_topic``
     - Topic work is pulled from
   * - ``service_bus_completion_topic``
     - Topic completions are sent to
   * - ``service_bus_exit_after_first_message``
     - Exit once one message is done
   * - ``service_bus_max_autorenewal_minutes``
     - How long to hold a message lock

The keys are named after Service Bus for historical reasons but apply to every
transport. The UNode worker exits after its first message by default, which
suits a job that is scheduled per message. The rebase worker keeps polling by
default, since it is a long lived relay, and ``--exit-after-first`` switches it
to the one shot behaviour.

Two transport differences are worth knowing. A Pub/Sub subscription filter is
**immutable**, so a subscription that already exists with a different filter is
used as it is and the worker logs a warning: recreate the subscription if it
should only see its own messages. And where Service Bus renews a message lock
in the background, Pub/Sub extends the ack deadline once, capped at 10 minutes,
so a handler running longer than that gets its message redelivered instead of
held.

Adding another transport
^^^^^^^^^^^^^^^^^^^^^^^^

Transports are discovered like UFile IO backends: subclass
:class:`urgap.umessagebus.io._base.UMessageBusBase`, set ``SCHEMA`` to the
cred_key scheme and drop the module into ``urgap/umessagebus/io/``. The
UMessageBusManager picks it up automatically, and a transport whose
dependencies are missing is skipped rather than breaking the import.
