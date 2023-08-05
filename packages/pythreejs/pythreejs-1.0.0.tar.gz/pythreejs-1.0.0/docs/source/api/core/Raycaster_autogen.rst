
.. py:currentmodule:: pythreejs

Raycaster
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: Raycaster(origin=[0,0,0], direction=[0,0,0], near=0, far=1000000, )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.ThreeWidget`.

    Three.js docs: https://threejs.org/docs/#api/core/Raycaster


    .. py:attribute:: origin


        .. sourcecode:: python

            Vector3(default_value=[0,0,0]).tag(sync=True)

    .. py:attribute:: direction


        .. sourcecode:: python

            Vector3(default_value=[0,0,0]).tag(sync=True)

    .. py:attribute:: near


        .. sourcecode:: python

            CFloat(0, allow_none=False).tag(sync=True)

    .. py:attribute:: far


        .. sourcecode:: python

            CFloat(1000000, allow_none=False).tag(sync=True)

    .. py:attribute:: ray


        .. sourcecode:: python

            Instance(Ray, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: linePrecision


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

