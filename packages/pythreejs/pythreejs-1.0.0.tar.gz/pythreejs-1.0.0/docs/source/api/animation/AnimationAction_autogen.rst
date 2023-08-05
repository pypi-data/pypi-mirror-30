
.. py:currentmodule:: pythreejs

AnimationAction
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: AnimationAction(mixer=None, clip=None, localRoot=None, )
    :members:
    :undoc-members:

    This widget has some manual overrides on the Python side.

    Inherits :py:class:`~pythreejs.ThreeWidget`.

    Three.js docs: https://threejs.org/docs/#api/animation/AnimationAction


    .. py:attribute:: mixer


        .. sourcecode:: python

            Instance(AnimationMixer, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: clip


        .. sourcecode:: python

            Instance(AnimationClip, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: localRoot


        .. sourcecode:: python

            Instance(ThreeWidget, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: clampWhenFinished


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: enabled


        .. sourcecode:: python

            Bool(True, allow_none=False).tag(sync=True)

    .. py:attribute:: loop


        .. sourcecode:: python

            Enum(LoopModes, "LoopRepeat", allow_none=False).tag(sync=True)

    .. py:attribute:: paused


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: repititions


        .. sourcecode:: python

            CInt(float('inf'), allow_none=False).tag(sync=True)

    .. py:attribute:: time


        .. sourcecode:: python

            CFloat(0, allow_none=False).tag(sync=True)

    .. py:attribute:: timeScale


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: weigth


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: zeroSlopeAtEnd


        .. sourcecode:: python

            Bool(True, allow_none=False).tag(sync=True)

    .. py:attribute:: zeroSlopeAtStart


        .. sourcecode:: python

            Bool(True, allow_none=False).tag(sync=True)

