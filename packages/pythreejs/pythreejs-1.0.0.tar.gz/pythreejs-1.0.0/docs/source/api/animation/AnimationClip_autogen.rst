
.. py:currentmodule:: pythreejs

AnimationClip
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: AnimationClip(name=None, duration=-1, tracks=[], )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.ThreeWidget`.

    Three.js docs: https://threejs.org/docs/#api/animation/AnimationClip


    .. py:attribute:: name


        .. sourcecode:: python

            Unicode(None, allow_none=True).tag(sync=True)

    .. py:attribute:: duration


        .. sourcecode:: python

            CFloat(-1, allow_none=False).tag(sync=True)

    .. py:attribute:: tracks


        .. sourcecode:: python

            Tuple().tag(sync=True, **widget_serialization)

