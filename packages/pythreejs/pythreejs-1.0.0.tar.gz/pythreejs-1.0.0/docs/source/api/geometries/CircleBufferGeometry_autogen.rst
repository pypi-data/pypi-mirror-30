
.. py:currentmodule:: pythreejs

CircleBufferGeometry
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: CircleBufferGeometry(radius=1, segments=8, thetaStart=0, thetaLength=6.283185307179586, )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.BaseBufferGeometry`.

    Three.js docs: https://threejs.org/docs/#api/geometries/CircleGeometry


    .. py:attribute:: radius


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: segments


        .. sourcecode:: python

            CInt(8, allow_none=False, min=3).tag(sync=True)

    .. py:attribute:: thetaStart


        .. sourcecode:: python

            CFloat(0, allow_none=False).tag(sync=True)

    .. py:attribute:: thetaLength


        .. sourcecode:: python

            CFloat(6.283185307179586, allow_none=False).tag(sync=True)

    .. py:attribute:: type


        .. sourcecode:: python

            Unicode("CircleBufferGeometry", allow_none=False).tag(sync=True)

