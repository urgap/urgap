.. _getting_started:

Quickstart
==========

Minimal pipeline: download a CSV and filter it
----------------------------------------------

This section walks through the smallest useful urgap pipeline:

#. Describe an input dataset with a UFile (here: a CSV hosted over HTTP).
#. Configure a node run with a URunDict.
#. Execute a node (here: :code:`FilterTabularToCSV`) to produce a new output file.

The same principles are used for larger pipelines.

.. code-block:: python

    import pandas as pd

    import urgap

    # 1) Define a remote input file
    #
    # UFile is Urgap's data abstraction: it stores “where” the data lives (URI),
    # *plus* metadata (uftype, tags, hashes, …).
    #
    # When a node needs the local path (or when you access `ufile.path` yourself),
    # Urgap downloads the data into a local scratch area automatically.
    csv = urgap.UFile(
        uri=(
            "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv"
            f"?uftype={urgap.uftypes.any.CSV}"
        )
    )

    out_dir = "/some/local/path_where_you_want_the_results"

    # 3) Configure and run a node
    #
    # A URunDict holds *execution parameters*.
    # - `parameters` are node-specific CLI parameters.
    # - `unode_parameters.storage_base_uri` is the common output base location.
    #
    # FilterTabularToCSV:1.0.0 uses a pandas query string.
    urun_dict = urgap.URunDict(
        {
            "parameters": {
                "FilterTabularToCSV:1.0.0": {
                    "-q": "`species` == 'setosa'",
                },
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{out_dir}",
            },
        }
    )

    filter_node = urgap.init_unode("FilterTabularToCSV:1.0.0")
    filtered = filter_node.run(ufiles=urgap.UFileList([csv]), urun_dict=urun_dict)

    # 4) Inspect the result
    #
    # `filtered` is a UFileList. The output file is again represented as a UFile.
    print(filtered)
    print("Output path:", filtered[0].path)

    df = pd.read_csv(filtered[0].path)
    print(df.head())


.. note::

    *What exactly happened?*

    - The input UFile points at an HTTP URL. When the node runs, it resolves
      :code:`UFile.path`, which triggers a download into a local scratch file.

    - The node writes its result under :code:`storage_base_uri`. In this example that’s a
      local :code:`file://...` URI, but the same pattern works for other backends.

    - The :code:`-q` parameter is interpreted by the node executable. In
      :code:`FilterTabularToCSV:1.0.0` it’s a pandas query string.


Executing example scripts
-------------------------

Urgap comes with a set of example scripts covering single node execution to fully-fledged pipelines.
Have a look in the example_scripts folder to get started with more advanced workflows.
Most example scripts come with a click interface, for help simply run python scriptXXX.py --help
