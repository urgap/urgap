.. _faq:

F.A.Q
#####

*What does urgap mean?*

urgap stands for unified resource governance and data provenance. The goal is to use urgap as an open-source foundation for file-based data engineering that facilitates standardized data provenance, aligns with FAIR principles, and addresses the increasingly distributed nature of data generation and consumption in rapidly developing environments.




*Why did you decide to use a hashtag / fragment in the uri?*

Object names can have nested folder strucutres. So for some uri, like google cloud storage (gcs) the definition of container name and object name is very explicit. The container name is the first "folder" in the uri.

.. code-block:: bash

    gcs://<container_name>/<object_name>


For other UFile schemata the definition is less explicit. For example, in the case of a minio installation, it depends where the entrypoint of the minio sits, e.g. in the case of a namespaced kubernets cluster, that would be

.. code-block:: bash

    minio://k8s-server/<namespace>/<container>/<object_name>

Thus determining what the container name is and what the object name is becomes difficult. The same holds true for  path (libcloud) or file (python).

Therefor, we decided to explicitly define the object name as a fragment in the uri.

.. code-block:: bash

    gcs://<container_name>#<object_name>
    minio://k8s-server/<namespace>/<container>#<object_name>




*Why do I get a workflow ID (WID) for each executed node?*

WIDs are created during init of a URunDict, so the problem could be that you initalize a new URunDict for each unode.run()?. 


