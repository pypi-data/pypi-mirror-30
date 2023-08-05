
.. py:currentmodule:: pythreejs

Sprite
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: Sprite(material=None, )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.Object3D`.

    Three.js docs: https://threejs.org/docs/#api/objects/Sprite


    .. py:attribute:: material


        .. sourcecode:: python

            Instance(SpriteMaterial, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: center


        .. sourcecode:: python

            Vector2(default_value=[0.5,0.5]).tag(sync=True)

    .. py:attribute:: type


        .. sourcecode:: python

            Unicode("Sprite", allow_none=False).tag(sync=True)

