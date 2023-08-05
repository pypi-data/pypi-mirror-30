
.. py:currentmodule:: pythreejs

KeyframeTrack
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: KeyframeTrack(name='', times=None, values=None, interpolation="InterpolateLinear", )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.ThreeWidget`.

    Three.js docs: https://threejs.org/docs/#api/animation/KeyframeTrack


    .. py:attribute:: name


        .. sourcecode:: python

            Unicode('', allow_none=False).tag(sync=True)

    .. py:attribute:: times


        .. sourcecode:: python

            WebGLDataUnion().tag(sync=True)

    .. py:attribute:: values


        .. sourcecode:: python

            WebGLDataUnion().tag(sync=True)

    .. py:attribute:: interpolation


        .. sourcecode:: python

            Enum(InterpolationModes, "InterpolateLinear", allow_none=False).tag(sync=True)

