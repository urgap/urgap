.. _faq:

F.A.Q
#####


It is mongolian and means little stream




*Why did you decide to use a hashtag / fragment in the uri?*

Object names can have nested folder strucutres. So for some uri, like google cloud storage (gcs) the definition of container name and object name is very explicit. The container name is the first "folder" in the uri.

.. code-block:: bash

    gcs://<container_name>/<object_name>


For other UFile schemata the definition is less explicit. For example, in the case of a minio installation, it depends where the entrypoint of the minio sits, e.g. in the case of a namespaced kubernets cluster, that would be

.. code-block:: bash

    minio://k8s-server/<namespace>/<container>/<object_name>


Therefor, we decided to explicitly define the object name as a fragment in the uri.

.. code-block:: bash

    gcs://<container_name>#<object_name>
    minio://k8s-server/<namespace>/<container>#<object_name>
