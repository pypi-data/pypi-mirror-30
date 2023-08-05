
.. py:currentmodule:: pythreejs

DirectionalLight
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: DirectionalLight(color="#ffffff", intensity=1, )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.Light`.

    Three.js docs: https://threejs.org/docs/#api/lights/DirectionalLight


    .. py:attribute:: target


        .. sourcecode:: python

            Union([
                Instance(Uninitialized),
                Instance(Object3D),
                ], default_value=UninitializedSentinel, allow_none=False).tag(sync=True, **unitialized_serialization)

    .. py:attribute:: shadow


        .. sourcecode:: python

            Union([
                Instance(Uninitialized),
                Instance(LightShadow),
                ], default_value=UninitializedSentinel, allow_none=False).tag(sync=True, **unitialized_serialization)

    .. py:attribute:: type


        .. sourcecode:: python

            Unicode("DirectionalLight", allow_none=False).tag(sync=True)

