
.. py:currentmodule:: pythreejs

Camera
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: Camera()
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.Object3D`.

    Three.js docs: https://threejs.org/docs/#api/cameras/Camera


    .. py:attribute:: matrixWorldInverse


        .. sourcecode:: python

            Matrix4(default_value=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]).tag(sync=True)

    .. py:attribute:: projectionMatrix


        .. sourcecode:: python

            Matrix4(default_value=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]).tag(sync=True)

    .. py:attribute:: type


        .. sourcecode:: python

            Unicode("Camera", allow_none=False).tag(sync=True)

