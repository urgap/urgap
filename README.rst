Urgap2 - node wrapping framework
=================================

Urgap is a node wrapping framework, containing abstraction layers for data and meta data, extensive
re-run skipping logic and data versioning. Urgap can be incorporated with any scheduling/pipelining
tool making pipeline development independent from business logic and data storage, while offering 
standardized logging and execution, which makes monitoring and debugging easy.

Urgap gives us the governance constraints required for a decentralized data domain autonomy as
Urgap will enforce shared common data IO for storage, a common meta data capturing process in form of
an interface thus can be plugged into any existing processes and finally global data lineages. 

|build-status-azure|

.. |build-status-azure| image:: https://dev.azure.com/DevOps-RD/RD-DSO/_apis/build/status%2Fgsk-tech.urgap?repoName=gsk-tech%2Furgap&branchName=refs%2Fpull%2F388%2Fmerge
   :target: https://dev.azure.com/DevOps-RD/RD-DSO/_build?definitionId=13513
   :alt: ADO CI status


Documentation
--------------

Please use sphinx in the docs folder


.. note::

    Currently CI does not include pushing the documentation to readthedocs, therefore please 
    #. checkout the repo
    #. pip install -e .
    #. cd docs
    #. make html
    #. open docs/build/index.html
