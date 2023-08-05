
.. py:currentmodule:: pythreejs

TorusGeometry
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: TorusGeometry(radius=1, tube=0.4, radialSegments=8, tubularSegments=6, arc=6.283185307179586, )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.BaseGeometry`.

    Three.js docs: https://threejs.org/docs/#api/geometries/TorusGeometry


    .. py:attribute:: radius


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: tube


        .. sourcecode:: python

            CFloat(0.4, allow_none=False).tag(sync=True)

    .. py:attribute:: radialSegments


        .. sourcecode:: python

            CInt(8, allow_none=False).tag(sync=True)

    .. py:attribute:: tubularSegments


        .. sourcecode:: python

            CInt(6, allow_none=False).tag(sync=True)

    .. py:attribute:: arc


        .. sourcecode:: python

            CFloat(6.283185307179586, allow_none=False).tag(sync=True)

    .. py:attribute:: type


        .. sourcecode:: python

            Unicode("TorusGeometry", allow_none=False).tag(sync=True)

