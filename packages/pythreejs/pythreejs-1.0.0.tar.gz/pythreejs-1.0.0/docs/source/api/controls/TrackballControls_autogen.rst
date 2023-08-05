
.. py:currentmodule:: pythreejs

TrackballControls
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: TrackballControls(controlling=None, )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.Controls`.

    Three.js docs: https://threejs.org/docs/#api/controls/TrackballControls


    .. py:attribute:: enabled


        .. sourcecode:: python

            Bool(True, allow_none=False).tag(sync=True)

    .. py:attribute:: minDistance


        .. sourcecode:: python

            CFloat(0, allow_none=False).tag(sync=True)

    .. py:attribute:: maxDistance


        .. sourcecode:: python

            CFloat(float('inf'), allow_none=False).tag(sync=True)

    .. py:attribute:: rotateSpeed


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: zoomSpeed


        .. sourcecode:: python

            CFloat(1.2, allow_none=False).tag(sync=True)

    .. py:attribute:: panSpeed


        .. sourcecode:: python

            CFloat(0.3, allow_none=False).tag(sync=True)

    .. py:attribute:: staticMoving


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: dynamicDampingFactor


        .. sourcecode:: python

            CFloat(0.2, allow_none=False).tag(sync=True)

    .. py:attribute:: noRotate


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: noZoom


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: noPan


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: noRoll


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: target


        .. sourcecode:: python

            Vector3(default_value=[0,0,0]).tag(sync=True)

