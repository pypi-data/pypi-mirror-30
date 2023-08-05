
.. py:currentmodule:: pythreejs

PointLight
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: PointLight(color="#ffffff", intensity=1, distance=0, decay=1, )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.Light`.

    Three.js docs: https://threejs.org/docs/#api/lights/PointLight


    .. py:attribute:: power


        .. sourcecode:: python

            CFloat(12.566370614359172, allow_none=False).tag(sync=True)

    .. py:attribute:: distance


        .. sourcecode:: python

            CFloat(0, allow_none=False).tag(sync=True)

    .. py:attribute:: decay


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: shadow


        .. sourcecode:: python

            Union([
                Instance(Uninitialized),
                Instance(LightShadow),
                ], default_value=UninitializedSentinel, allow_none=False).tag(sync=True, **unitialized_serialization)

    .. py:attribute:: type


        .. sourcecode:: python

            Unicode("PointLight", allow_none=False).tag(sync=True)

