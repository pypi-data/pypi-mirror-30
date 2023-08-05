
.. py:currentmodule:: pythreejs

SpriteMaterial
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: SpriteMaterial()
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.Material`.

    Three.js docs: https://threejs.org/docs/#api/materials/SpriteMaterial


    .. py:attribute:: color


        .. sourcecode:: python

            Unicode("#ffffff", allow_none=False).tag(sync=True)

    .. py:attribute:: fog


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: lights


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: map


        .. sourcecode:: python

            Instance(Texture, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: rotation


        .. sourcecode:: python

            CFloat(0, allow_none=False).tag(sync=True)

    .. py:attribute:: type


        .. sourcecode:: python

            Unicode("SpriteMaterial", allow_none=False).tag(sync=True)

