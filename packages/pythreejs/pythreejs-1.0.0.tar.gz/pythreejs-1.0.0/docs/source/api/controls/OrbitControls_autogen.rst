
.. py:currentmodule:: pythreejs

OrbitControls
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: OrbitControls(controlling=None, )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.Controls`.

    Three.js docs: https://threejs.org/docs/#api/controls/OrbitControls


    .. py:attribute:: enabled


        .. sourcecode:: python

            Bool(True, allow_none=False).tag(sync=True)

    .. py:attribute:: minDistance


        .. sourcecode:: python

            CFloat(0, allow_none=False).tag(sync=True)

    .. py:attribute:: maxDistance


        .. sourcecode:: python

            CFloat(float('inf'), allow_none=False).tag(sync=True)

    .. py:attribute:: minZoom


        .. sourcecode:: python

            CFloat(0, allow_none=False).tag(sync=True)

    .. py:attribute:: maxZoom


        .. sourcecode:: python

            CFloat(float('inf'), allow_none=False).tag(sync=True)

    .. py:attribute:: minPolarAngle


        .. sourcecode:: python

            CFloat(0, allow_none=False).tag(sync=True)

    .. py:attribute:: maxPolarAngle


        .. sourcecode:: python

            CFloat(3.141592653589793, allow_none=False).tag(sync=True)

    .. py:attribute:: minAzimuthAngle


        .. sourcecode:: python

            CFloat(-float('inf'), allow_none=False).tag(sync=True)

    .. py:attribute:: maxAzimuthAngle


        .. sourcecode:: python

            CFloat(float('inf'), allow_none=False).tag(sync=True)

    .. py:attribute:: enableDamping


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: dampingFactor


        .. sourcecode:: python

            CFloat(0.25, allow_none=False).tag(sync=True)

    .. py:attribute:: enableZoom


        .. sourcecode:: python

            Bool(True, allow_none=False).tag(sync=True)

    .. py:attribute:: zoomSpeed


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: enableRotate


        .. sourcecode:: python

            Bool(True, allow_none=False).tag(sync=True)

    .. py:attribute:: rotateSpeed


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: enablePan


        .. sourcecode:: python

            Bool(True, allow_none=False).tag(sync=True)

    .. py:attribute:: keyPanSpeed


        .. sourcecode:: python

            CFloat(7, allow_none=False).tag(sync=True)

    .. py:attribute:: autoRotate


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: autoRotateSpeed


        .. sourcecode:: python

            CFloat(2, allow_none=False).tag(sync=True)

    .. py:attribute:: enableKeys


        .. sourcecode:: python

            Bool(True, allow_none=False).tag(sync=True)

    .. py:attribute:: target


        .. sourcecode:: python

            Vector3(default_value=[0,0,0]).tag(sync=True)

