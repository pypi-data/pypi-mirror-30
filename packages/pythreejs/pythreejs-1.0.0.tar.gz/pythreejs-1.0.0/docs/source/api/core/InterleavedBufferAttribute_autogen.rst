
.. py:currentmodule:: pythreejs

InterleavedBufferAttribute
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: InterleavedBufferAttribute(data=None, itemSize=0, offset=0, normalized=True, )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.ThreeWidget`.

    Three.js docs: https://threejs.org/docs/#api/core/InterleavedBufferAttribute


    .. py:attribute:: data


        .. sourcecode:: python

            Instance(InterleavedBuffer, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: itemSize


        .. sourcecode:: python

            CInt(0, allow_none=False).tag(sync=True)

    .. py:attribute:: offset


        .. sourcecode:: python

            CInt(0, allow_none=False).tag(sync=True)

    .. py:attribute:: normalized


        .. sourcecode:: python

            Bool(True, allow_none=False).tag(sync=True)

