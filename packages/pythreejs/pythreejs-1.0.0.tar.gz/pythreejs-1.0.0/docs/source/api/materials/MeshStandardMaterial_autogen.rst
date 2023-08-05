
.. py:currentmodule:: pythreejs

MeshStandardMaterial
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: MeshStandardMaterial()
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.Material`.

    Three.js docs: https://threejs.org/docs/#api/materials/MeshStandardMaterial


    .. py:attribute:: alphaMap


        .. sourcecode:: python

            Instance(Texture, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: aoMap


        .. sourcecode:: python

            Instance(Texture, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: aoMapIntensity


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: bumpMap


        .. sourcecode:: python

            Instance(Texture, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: bumpScale


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: color


        .. sourcecode:: python

            Unicode("#ffffff", allow_none=False).tag(sync=True)

    .. py:attribute:: defines


        .. sourcecode:: python

            Dict(default_value={"STANDARD":""}, allow_none=True).tag(sync=True)

    .. py:attribute:: displacementMap


        .. sourcecode:: python

            Instance(Texture, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: displacementScale


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: displacementBias


        .. sourcecode:: python

            CFloat(0, allow_none=False).tag(sync=True)

    .. py:attribute:: emissive


        .. sourcecode:: python

            Unicode("#000000", allow_none=False).tag(sync=True)

    .. py:attribute:: emissiveMap


        .. sourcecode:: python

            Instance(Texture, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: emissiveIntensity


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: envMap


        .. sourcecode:: python

            Instance(CubeTexture, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: envMapIntensity


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: lightMap


        .. sourcecode:: python

            Instance(Texture, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: lightMapIntensity


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: map


        .. sourcecode:: python

            Instance(Texture, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: metalness


        .. sourcecode:: python

            CFloat(0.5, allow_none=False).tag(sync=True)

    .. py:attribute:: metalnessMap


        .. sourcecode:: python

            Instance(Texture, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: morphTargets


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: morphNormals


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: normalMap


        .. sourcecode:: python

            Instance(Texture, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: normalScale


        .. sourcecode:: python

            Vector2(default_value=[1,1]).tag(sync=True)

    .. py:attribute:: refractionRatio


        .. sourcecode:: python

            CFloat(0.98, allow_none=False).tag(sync=True)

    .. py:attribute:: roughness


        .. sourcecode:: python

            CFloat(0.5, allow_none=False).tag(sync=True)

    .. py:attribute:: roughnessMap


        .. sourcecode:: python

            Instance(Texture, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: skinning


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: wireframe


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: wireframeLinecap


        .. sourcecode:: python

            Unicode("round", allow_none=False).tag(sync=True)

    .. py:attribute:: wireframeLinejoin


        .. sourcecode:: python

            Unicode("round", allow_none=False).tag(sync=True)

    .. py:attribute:: wireframeLinewidth


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: type


        .. sourcecode:: python

            Unicode("MeshStandardMaterial", allow_none=False).tag(sync=True)

