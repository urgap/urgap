.. _umeta:

UMeta Class
###########

.. autoclass:: urgap.umeta.umeta.UMeta
   :members:

   .. automethod:: __init__

UMeta IO Classes
################

.. autoclass:: urgap.umeta.io._base.UMetaIOBase
   :members:

   .. automethod:: __init__
   .. automethod:: __deepcopy__

.. autoclass:: urgap.umeta.io._sqalchemy_base.UcfsStorageLocation
   :members:

.. autoclass:: urgap.umeta.io._sqalchemy_base.ExecutionConfigurations
   :members:

.. autoclass:: urgap.umeta.io._sqalchemy_base.InputUFiles
   :members:

.. autoclass:: urgap.umeta.io._sqalchemy_base.OutputUFiles
   :members:

.. autoclass:: urgap.umeta.io._sqalchemy_base.ExecutionInputLink
   :members:

.. autoclass:: urgap.umeta.io._sqalchemy_base.ExecutionOutputLink
   :members:

.. autoclass:: urgap.umeta.io._sqalchemy_base.ExecutionHistory
   :members:

.. autoclass:: urgap.umeta.io._sqalchemy_base.UserDicts
   :members:

.. autoclass:: urgap.umeta.io._sqalchemy_base.SQLAlchemyBaseUMeta
   :members:

   .. automethod:: __init__

.. autoclass:: urgap.umeta.io.dummy.UMeta
   :members:

   .. automethod:: __init__

.. autoclass:: urgap.umeta.io.gcpsql.UMeta
   :members:

   .. automethod:: __init__

.. autoclass:: urgap.umeta.io.postgresql.UMeta
   :members:

   .. automethod:: __init__

.. autoclass:: urgap.umeta.io.sqlite3.UMeta
   :members:

   .. automethod:: __init__