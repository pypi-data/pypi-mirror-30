
.. py:currentmodule:: pythreejs

Points
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: Points(geometry=None, material=None, )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.Object3D`.

    Three.js docs: https://threejs.org/docs/#api/objects/Points


    .. py:attribute:: material


        .. sourcecode:: python

            Instance(Material, allow_none=False).tag(sync=True, **widget_serialization)

    .. py:attribute:: geometry


        .. sourcecode:: python

            Union([
                Instance(BaseGeometry, allow_none=False),
                Instance(BaseBufferGeometry, allow_none=False)
            ]).tag(sync=True, **widget_serialization)

    .. py:attribute:: type


        .. sourcecode:: python

            Unicode("Points", allow_none=False).tag(sync=True)

