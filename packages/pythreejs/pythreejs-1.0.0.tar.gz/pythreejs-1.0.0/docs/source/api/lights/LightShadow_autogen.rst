
.. py:currentmodule:: pythreejs

LightShadow
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: LightShadow(camera=UninitializedSentinel, )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.ThreeWidget`.

    Three.js docs: https://threejs.org/docs/#api/lights/LightShadow


    .. py:attribute:: camera


        .. sourcecode:: python

            Union([
                Instance(Uninitialized),
                Instance(Camera),
                ], default_value=UninitializedSentinel, allow_none=False).tag(sync=True, **unitialized_serialization)

    .. py:attribute:: bias


        .. sourcecode:: python

            CFloat(0, allow_none=False).tag(sync=True)

    .. py:attribute:: mapSize


        .. sourcecode:: python

            Vector2(default_value=[512,512]).tag(sync=True)

    .. py:attribute:: radius


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

