
.. py:currentmodule:: pythreejs

TubeGeometry
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: TubeGeometry(path=None, segments=64, radius=1, radiusSegments=8, close=False, )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.BaseGeometry`.

    Three.js docs: https://threejs.org/docs/#api/geometries/TubeGeometry


    .. py:attribute:: path


        .. sourcecode:: python

            Instance(Curve, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: segments


        .. sourcecode:: python

            CInt(64, allow_none=False).tag(sync=True)

    .. py:attribute:: radius


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: radiusSegments


        .. sourcecode:: python

            CInt(8, allow_none=False).tag(sync=True)

    .. py:attribute:: close


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: type


        .. sourcecode:: python

            Unicode("TubeGeometry", allow_none=False).tag(sync=True)

