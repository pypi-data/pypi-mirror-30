
.. py:currentmodule:: pythreejs

StereoCamera
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: StereoCamera()
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.ThreeWidget`.

    Three.js docs: https://threejs.org/docs/#api/cameras/StereoCamera


    .. py:attribute:: aspect


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: eyeSep


        .. sourcecode:: python

            CFloat(0.064, allow_none=False).tag(sync=True)

    .. py:attribute:: cameraL


        .. sourcecode:: python

            Instance(PerspectiveCamera, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: cameraR


        .. sourcecode:: python

            Instance(PerspectiveCamera, allow_none=True).tag(sync=True, **widget_serialization)

