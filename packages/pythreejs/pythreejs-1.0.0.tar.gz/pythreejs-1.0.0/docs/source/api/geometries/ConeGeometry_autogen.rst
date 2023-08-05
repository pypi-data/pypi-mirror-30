
.. py:currentmodule:: pythreejs

ConeGeometry
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: ConeGeometry(radius=20, height=100, radialSegments=8, heightSegments=1, openEnded=False, thetaStart=0, thetaLength=6.283185307179586, )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.BaseGeometry`.

    Three.js docs: https://threejs.org/docs/#api/geometries/ConeGeometry


    .. py:attribute:: radius


        .. sourcecode:: python

            CFloat(20, allow_none=False).tag(sync=True)

    .. py:attribute:: height


        .. sourcecode:: python

            CFloat(100, allow_none=False).tag(sync=True)

    .. py:attribute:: radialSegments


        .. sourcecode:: python

            CInt(8, allow_none=False).tag(sync=True)

    .. py:attribute:: heightSegments


        .. sourcecode:: python

            CInt(1, allow_none=False).tag(sync=True)

    .. py:attribute:: openEnded


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: thetaStart


        .. sourcecode:: python

            CFloat(0, allow_none=False).tag(sync=True)

    .. py:attribute:: thetaLength


        .. sourcecode:: python

            CFloat(6.283185307179586, allow_none=False).tag(sync=True)

    .. py:attribute:: type


        .. sourcecode:: python

            Unicode("ConeGeometry", allow_none=False).tag(sync=True)

