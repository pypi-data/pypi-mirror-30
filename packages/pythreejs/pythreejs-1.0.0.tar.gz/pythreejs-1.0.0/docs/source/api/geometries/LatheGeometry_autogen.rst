
.. py:currentmodule:: pythreejs

LatheGeometry
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: LatheGeometry(points=[], segments=12, phiStart=0, phiLength=6.283185307179586, )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.BaseGeometry`.

    Three.js docs: https://threejs.org/docs/#api/geometries/LatheGeometry


    .. py:attribute:: points


        .. sourcecode:: python

            List(trait=List()).tag(sync=True)

    .. py:attribute:: segments


        .. sourcecode:: python

            CInt(12, allow_none=False).tag(sync=True)

    .. py:attribute:: phiStart


        .. sourcecode:: python

            CFloat(0, allow_none=False).tag(sync=True)

    .. py:attribute:: phiLength


        .. sourcecode:: python

            CFloat(6.283185307179586, allow_none=False).tag(sync=True)

    .. py:attribute:: type


        .. sourcecode:: python

            Unicode("LatheGeometry", allow_none=False).tag(sync=True)

