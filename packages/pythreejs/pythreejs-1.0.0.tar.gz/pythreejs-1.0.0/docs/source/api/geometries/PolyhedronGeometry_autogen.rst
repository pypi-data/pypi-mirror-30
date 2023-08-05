
.. py:currentmodule:: pythreejs

PolyhedronGeometry
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: PolyhedronGeometry(vertices=[], faces=[], radius=1, detail=0, )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.BaseGeometry`.

    Three.js docs: https://threejs.org/docs/#api/geometries/PolyhedronGeometry


    .. py:attribute:: vertices


        .. sourcecode:: python

            List().tag(sync=True)

    .. py:attribute:: indices


        .. sourcecode:: python

            List().tag(sync=True)

    .. py:attribute:: radius


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: detail


        .. sourcecode:: python

            CFloat(0, allow_none=False).tag(sync=True)

    .. py:attribute:: faces


        .. sourcecode:: python

            List().tag(sync=True)

    .. py:attribute:: type


        .. sourcecode:: python

            Unicode("PolyhedronGeometry", allow_none=False).tag(sync=True)

