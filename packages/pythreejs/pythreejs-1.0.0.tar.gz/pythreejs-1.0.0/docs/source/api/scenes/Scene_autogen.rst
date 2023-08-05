
.. py:currentmodule:: pythreejs

Scene
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: Scene()
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.Object3D`.

    Three.js docs: https://threejs.org/docs/#api/scenes/Scene


    .. py:attribute:: fog


        .. sourcecode:: python

            Instance(Fog, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: overrideMaterial


        .. sourcecode:: python

            Instance(Material, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: autoUpdate


        .. sourcecode:: python

            Bool(True, allow_none=False).tag(sync=True)

    .. py:attribute:: background


        .. sourcecode:: python

            Unicode("#ffffff", allow_none=True).tag(sync=True)

    .. py:attribute:: type


        .. sourcecode:: python

            Unicode("Scene", allow_none=False).tag(sync=True)

