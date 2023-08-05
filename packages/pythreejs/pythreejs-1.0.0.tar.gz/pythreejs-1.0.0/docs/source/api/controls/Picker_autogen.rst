
.. py:currentmodule:: pythreejs

Picker
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: Picker(controlling=None, )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.Controls`.

    Three.js docs: https://threejs.org/docs/#api/controls/Picker


    .. py:attribute:: event

        The DOM MouseEvent type to trigger the pick

        .. sourcecode:: python

            Unicode("click", allow_none=False).tag(sync=True)

    .. py:attribute:: all

        Wether to send info on all object intersections beneath the picked point, or only the first one. See ``picked``.

        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: distance

        The distance from the camera of the picked point (null if no object picked)

        .. sourcecode:: python

            CFloat(None, allow_none=True).tag(sync=True)

    .. py:attribute:: point

        The coordinates of the picked point (all zero if no object picked)

        .. sourcecode:: python

            Vector3(default_value=[0,0,0]).tag(sync=True)

    .. py:attribute:: face

        The vertex indices of the picked face (all zero if no face picked)

        .. sourcecode:: python

            Vector3(default_value=[0,0,0]).tag(sync=True)

    .. py:attribute:: faceNormal

        The normal vector of the picked face (all zero if no face picked)

        .. sourcecode:: python

            Vector3(default_value=[0,0,0]).tag(sync=True)

    .. py:attribute:: faceVertices

        The three vertices that make up the picked face, as vectors (empty if no face picked)

        .. sourcecode:: python

            List(trait=List()).tag(sync=True)

    .. py:attribute:: faceIndex


        .. sourcecode:: python

            CInt(0, allow_none=False).tag(sync=True)

    .. py:attribute:: modifiers

        The keyboard modifiers held at the pick event in the following order: [SHIFT, CTRL, ALT, META]

        .. sourcecode:: python

            List().tag(sync=True)

    .. py:attribute:: object

        The picked object (null if no object picked)

        .. sourcecode:: python

            Instance(Object3D, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: picked

        The other fields on the picker will always be for the first object intersection. If ``all`` is set true, this field will be an array containing the same information for all intersections.

        .. sourcecode:: python

            List().tag(sync=True)

    .. py:attribute:: uv

        The UV coordinate picked (all zero if invalid pick)

        .. sourcecode:: python

            Vector2(default_value=[0,0]).tag(sync=True)

    .. py:attribute:: indices

        The vertex indices of the picked face (empty if no face picked)

        .. sourcecode:: python

            List().tag(sync=True)

