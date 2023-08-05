
.. py:currentmodule:: pythreejs

Material
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: Material()
    :members:
    :undoc-members:

    This widget has some manual overrides on the Python side.

    Inherits :py:class:`~pythreejs.ThreeWidget`.

    Three.js docs: https://threejs.org/docs/#api/materials/Material


    .. py:attribute:: alphaTest


        .. sourcecode:: python

            CFloat(0, allow_none=False).tag(sync=True)

    .. py:attribute:: blendDst


        .. sourcecode:: python

            Enum(BlendFactors, "OneMinusSrcAlphaFactor", allow_none=False).tag(sync=True)

    .. py:attribute:: blendDstAlpha


        .. sourcecode:: python

            CFloat(0, allow_none=False).tag(sync=True)

    .. py:attribute:: blending


        .. sourcecode:: python

            Enum(BlendingMode, "NormalBlending", allow_none=False).tag(sync=True)

    .. py:attribute:: blendSrc


        .. sourcecode:: python

            Enum(BlendFactors, "SrcAlphaFactor", allow_none=False).tag(sync=True)

    .. py:attribute:: blendSrcAlpha


        .. sourcecode:: python

            CFloat(0, allow_none=False).tag(sync=True)

    .. py:attribute:: blendEquation


        .. sourcecode:: python

            Enum(Equations, "AddEquation", allow_none=False).tag(sync=True)

    .. py:attribute:: blendEquationAlpha


        .. sourcecode:: python

            CFloat(0, allow_none=False).tag(sync=True)

    .. py:attribute:: clipIntersection


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: clippingPlanes


        .. sourcecode:: python

            Tuple().tag(sync=True, **widget_serialization)

    .. py:attribute:: clipShadows


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: colorWrite


        .. sourcecode:: python

            Bool(True, allow_none=False).tag(sync=True)

    .. py:attribute:: defines


        .. sourcecode:: python

            Dict(default_value=None, allow_none=True).tag(sync=True)

    .. py:attribute:: depthFunc


        .. sourcecode:: python

            Enum(DepthMode, "LessEqualDepth", allow_none=False).tag(sync=True)

    .. py:attribute:: depthTest


        .. sourcecode:: python

            Bool(True, allow_none=False).tag(sync=True)

    .. py:attribute:: depthWrite


        .. sourcecode:: python

            Bool(True, allow_none=False).tag(sync=True)

    .. py:attribute:: dithering


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: flatShading


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: fog


        .. sourcecode:: python

            Bool(True, allow_none=False).tag(sync=True)

    .. py:attribute:: lights


        .. sourcecode:: python

            Bool(True, allow_none=False).tag(sync=True)

    .. py:attribute:: name


        .. sourcecode:: python

            Unicode('', allow_none=False).tag(sync=True)

    .. py:attribute:: opacity


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: overdraw


        .. sourcecode:: python

            CFloat(0, allow_none=False).tag(sync=True)

    .. py:attribute:: polygonOffset


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: polygonOffsetFactor


        .. sourcecode:: python

            CFloat(0, allow_none=False).tag(sync=True)

    .. py:attribute:: polygonOffsetUnits


        .. sourcecode:: python

            CFloat(0, allow_none=False).tag(sync=True)

    .. py:attribute:: precision


        .. sourcecode:: python

            Unicode(None, allow_none=True).tag(sync=True)

    .. py:attribute:: premultipliedAlpha


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: shadowSide


        .. sourcecode:: python

            Enum(Side, None, allow_none=True).tag(sync=True)

    .. py:attribute:: side


        .. sourcecode:: python

            Enum(Side, "FrontSide", allow_none=False).tag(sync=True)

    .. py:attribute:: transparent


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: type


        .. sourcecode:: python

            Unicode("Material", allow_none=False).tag(sync=True)

    .. py:attribute:: vertexColors


        .. sourcecode:: python

            Enum(Colors, "NoColors", allow_none=False).tag(sync=True)

    .. py:attribute:: visible


        .. sourcecode:: python

            Bool(True, allow_none=False).tag(sync=True)

