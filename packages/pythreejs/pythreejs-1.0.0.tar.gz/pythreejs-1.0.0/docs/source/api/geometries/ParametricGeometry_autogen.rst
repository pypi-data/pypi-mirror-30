
.. py:currentmodule:: pythreejs

ParametricGeometry
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: ParametricGeometry(func, slices=3, stacks=3, )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.BaseGeometry`.

    Three.js docs: https://threejs.org/docs/#api/geometries/ParametricGeometry


    .. py:attribute:: func


        .. sourcecode:: python

            Unicode('function (u,v) { return THREE.Vector3(); }').tag(sync=True)

    .. py:attribute:: slices


        .. sourcecode:: python

            CInt(3, allow_none=False).tag(sync=True)

    .. py:attribute:: stacks


        .. sourcecode:: python

            CInt(3, allow_none=False).tag(sync=True)

    .. py:attribute:: type


        .. sourcecode:: python

            Unicode("ParametricGeometry", allow_none=False).tag(sync=True)

