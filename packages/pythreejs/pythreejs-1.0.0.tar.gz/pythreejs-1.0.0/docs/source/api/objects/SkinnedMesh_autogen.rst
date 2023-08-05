
.. py:currentmodule:: pythreejs

SkinnedMesh
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: SkinnedMesh(geometry=None, material=[], )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.Mesh`.

    Three.js docs: https://threejs.org/docs/#api/objects/SkinnedMesh


    .. py:attribute:: bindMode


        .. sourcecode:: python

            Unicode("attached", allow_none=False).tag(sync=True)

    .. py:attribute:: bindMatrix


        .. sourcecode:: python

            Matrix4(default_value=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]).tag(sync=True)

    .. py:attribute:: skeleton


        .. sourcecode:: python

            Instance(Skeleton, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: type


        .. sourcecode:: python

            Unicode("SkinnedMesh", allow_none=False).tag(sync=True)

