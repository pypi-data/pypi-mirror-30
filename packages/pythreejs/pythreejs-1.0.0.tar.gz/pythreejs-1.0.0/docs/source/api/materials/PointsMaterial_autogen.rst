
.. py:currentmodule:: pythreejs

PointsMaterial
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: PointsMaterial()
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.Material`.

    Three.js docs: https://threejs.org/docs/#api/materials/PointsMaterial


    .. py:attribute:: color


        .. sourcecode:: python

            Unicode("#ffffff", allow_none=False).tag(sync=True)

    .. py:attribute:: lights


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: map


        .. sourcecode:: python

            Instance(Texture, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: size


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: sizeAttenuation


        .. sourcecode:: python

            Bool(True, allow_none=False).tag(sync=True)

    .. py:attribute:: type


        .. sourcecode:: python

            Unicode("PointsMaterial", allow_none=False).tag(sync=True)

