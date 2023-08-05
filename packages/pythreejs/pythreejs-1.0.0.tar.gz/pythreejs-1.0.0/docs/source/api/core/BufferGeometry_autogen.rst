
.. py:currentmodule:: pythreejs

BufferGeometry
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: BufferGeometry()
    :members:
    :undoc-members:

    This widget has some manual overrides on the Python side.

    Inherits :py:class:`~pythreejs.BaseBufferGeometry`.

    Three.js docs: https://threejs.org/docs/#api/core/BufferGeometry


    .. py:attribute:: index


        .. sourcecode:: python

            Union([
                Instance(BufferAttribute, allow_none=True),
                Instance(InterleavedBufferAttribute, allow_none=True)
            ]).tag(sync=True, **widget_serialization)

    .. py:attribute:: attributes


        .. sourcecode:: python

            Dict(Union([
                Instance(BufferAttribute),
                Instance(InterleavedBufferAttribute)
            ])).tag(sync=True, **widget_serialization)

    .. py:attribute:: morphAttributes


        .. sourcecode:: python

            Dict(Tuple(Union([
                Instance(BufferAttribute),
                Instance(InterleavedBufferAttribute)
            ]))).tag(sync=True, **widget_serialization)

    .. py:attribute:: MaxIndex


        .. sourcecode:: python

            CInt(65535, allow_none=False).tag(sync=True)

    .. py:attribute:: _ref_geometry


        .. sourcecode:: python

            Union([
                Instance(BaseGeometry, allow_none=True),
                Instance(BaseBufferGeometry, allow_none=True)
            ]).tag(sync=True, **widget_serialization)

    .. py:attribute:: _store_ref


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: type


        .. sourcecode:: python

            Unicode("BufferGeometry", allow_none=False).tag(sync=True)

