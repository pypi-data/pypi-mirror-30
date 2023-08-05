
.. py:currentmodule:: pythreejs

Mesh
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: Mesh(geometry=None, material=[], )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.Object3D`.

    Three.js docs: https://threejs.org/docs/#api/objects/Mesh


    .. py:attribute:: material


        .. sourcecode:: python

            Union([Instance(Material), Tuple()]).tag(sync=True, **widget_serialization)

    .. py:attribute:: geometry


        .. sourcecode:: python

            Union([
                Instance(BaseGeometry, allow_none=False),
                Instance(BaseBufferGeometry, allow_none=False)
            ]).tag(sync=True, **widget_serialization)

    .. py:attribute:: drawMode


        .. sourcecode:: python

            Enum(DrawModes, "TrianglesDrawMode", allow_none=False).tag(sync=True)

    .. py:attribute:: morphTargetInfluences


        .. sourcecode:: python

            List().tag(sync=True)

    .. py:attribute:: type


        .. sourcecode:: python

            Unicode("Mesh", allow_none=False).tag(sync=True)

