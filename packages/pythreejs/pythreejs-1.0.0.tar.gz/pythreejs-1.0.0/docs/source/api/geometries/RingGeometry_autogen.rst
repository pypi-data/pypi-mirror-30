
.. py:currentmodule:: pythreejs

RingGeometry
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: RingGeometry(innerRadius=0.5, outerRadius=1, thetaSegments=8, phiSegments=8, thetaStart=0, thetaLength=6.283185307179586, )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.BaseGeometry`.

    Three.js docs: https://threejs.org/docs/#api/geometries/RingGeometry


    .. py:attribute:: innerRadius


        .. sourcecode:: python

            CFloat(0.5, allow_none=False).tag(sync=True)

    .. py:attribute:: outerRadius


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: thetaSegments


        .. sourcecode:: python

            CInt(8, allow_none=False, min=3).tag(sync=True)

    .. py:attribute:: phiSegments


        .. sourcecode:: python

            CInt(8, allow_none=False, min=1).tag(sync=True)

    .. py:attribute:: thetaStart


        .. sourcecode:: python

            CFloat(0, allow_none=False).tag(sync=True)

    .. py:attribute:: thetaLength


        .. sourcecode:: python

            CFloat(6.283185307179586, allow_none=False).tag(sync=True)

    .. py:attribute:: type


        .. sourcecode:: python

            Unicode("RingGeometry", allow_none=False).tag(sync=True)

