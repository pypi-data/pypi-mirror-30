
.. py:currentmodule:: pythreejs

Light
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: Light(color="#ffffff", intensity=1, )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.Object3D`.

    Three.js docs: https://threejs.org/docs/#api/lights/Light


    .. py:attribute:: color


        .. sourcecode:: python

            Unicode("#ffffff", allow_none=False).tag(sync=True)

    .. py:attribute:: intensity


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: type


        .. sourcecode:: python

            Unicode("Light", allow_none=False).tag(sync=True)

