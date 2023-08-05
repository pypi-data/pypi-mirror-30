
.. py:currentmodule:: pythreejs

DepthTexture
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: DepthTexture(width=0, height=0, type="UnsignedShortType", wrapS="ClampToEdgeWrapping", wrapT="ClampToEdgeWrapping", magFilter="NearestFilter", minFilter="NearestFilter", anisotropy=1, format="DepthFormat", )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.Texture`.

    Three.js docs: https://threejs.org/docs/#api/textures/DepthTexture


    .. py:attribute:: width


        .. sourcecode:: python

            CInt(0, allow_none=False).tag(sync=True)

    .. py:attribute:: height


        .. sourcecode:: python

            CInt(0, allow_none=False).tag(sync=True)

    .. py:attribute:: format


        .. sourcecode:: python

            Enum(DepthFormats, "DepthFormat", allow_none=False).tag(sync=True)

    .. py:attribute:: type


        .. sourcecode:: python

            Enum(DataTypes, "UnsignedShortType", allow_none=False).tag(sync=True)

    .. py:attribute:: minFilter


        .. sourcecode:: python

            Enum(Filters, "NearestFilter", allow_none=False).tag(sync=True)

    .. py:attribute:: magFilter


        .. sourcecode:: python

            Enum(Filters, "NearestFilter", allow_none=False).tag(sync=True)

    .. py:attribute:: flipY


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: generateMipmaps


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

