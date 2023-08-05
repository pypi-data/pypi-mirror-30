
.. py:currentmodule:: pythreejs

Texture
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: Texture()
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.ThreeWidget`.

    Three.js docs: https://threejs.org/docs/#api/textures/Texture


    .. py:attribute:: name


        .. sourcecode:: python

            Unicode('', allow_none=False).tag(sync=True)

    .. py:attribute:: mapping


        .. sourcecode:: python

            Enum(MappingModes, "UVMapping", allow_none=False).tag(sync=True)

    .. py:attribute:: wrapS


        .. sourcecode:: python

            Enum(WrappingModes, "ClampToEdgeWrapping", allow_none=False).tag(sync=True)

    .. py:attribute:: wrapT


        .. sourcecode:: python

            Enum(WrappingModes, "ClampToEdgeWrapping", allow_none=False).tag(sync=True)

    .. py:attribute:: magFilter


        .. sourcecode:: python

            Enum(Filters, "LinearFilter", allow_none=False).tag(sync=True)

    .. py:attribute:: minFilter


        .. sourcecode:: python

            Enum(Filters, "LinearMipMapLinearFilter", allow_none=False).tag(sync=True)

    .. py:attribute:: format


        .. sourcecode:: python

            Enum(PixelFormats, "RGBAFormat", allow_none=False).tag(sync=True)

    .. py:attribute:: type


        .. sourcecode:: python

            Enum(DataTypes, "UnsignedByteType", allow_none=False).tag(sync=True)

    .. py:attribute:: anisotropy


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: repeat


        .. sourcecode:: python

            Vector2(default_value=[1,1]).tag(sync=True)

    .. py:attribute:: offset


        .. sourcecode:: python

            Vector2(default_value=[0,0]).tag(sync=True)

    .. py:attribute:: generateMipmaps


        .. sourcecode:: python

            Bool(True, allow_none=False).tag(sync=True)

    .. py:attribute:: premultiplyAlpha


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: flipY


        .. sourcecode:: python

            Bool(True, allow_none=False).tag(sync=True)

    .. py:attribute:: unpackAlignment


        .. sourcecode:: python

            CInt(4, allow_none=False).tag(sync=True)

    .. py:attribute:: encoding


        .. sourcecode:: python

            Enum(TextureEncodings, "LinearEncoding", allow_none=False).tag(sync=True)

    .. py:attribute:: version


        .. sourcecode:: python

            CInt(0, allow_none=False).tag(sync=True)

    .. py:attribute:: rotation


        .. sourcecode:: python

            CFloat(0, allow_none=False).tag(sync=True)

