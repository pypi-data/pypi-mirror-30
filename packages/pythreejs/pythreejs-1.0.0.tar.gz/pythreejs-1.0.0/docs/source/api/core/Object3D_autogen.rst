
.. py:currentmodule:: pythreejs

Object3D
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: Object3D()
    :members:
    :undoc-members:

    This widget has some manual overrides on the Python side.

    Inherits :py:class:`~pythreejs.ThreeWidget`.

    Three.js docs: https://threejs.org/docs/#api/core/Object3D


    .. py:attribute:: name


        .. sourcecode:: python

            Unicode('', allow_none=False).tag(sync=True)

    .. py:attribute:: type


        .. sourcecode:: python

            Unicode("Object3D", allow_none=False).tag(sync=True)

    .. py:attribute:: children


        .. sourcecode:: python

            Tuple().tag(sync=True, **widget_serialization)

    .. py:attribute:: up


        .. sourcecode:: python

            Vector3(default_value=[0,1,0]).tag(sync=True)

    .. py:attribute:: position


        .. sourcecode:: python

            Vector3(default_value=[0,0,0]).tag(sync=True)

    .. py:attribute:: rotation


        .. sourcecode:: python

            Euler(default_value=[0,0,0,"XYZ"]).tag(sync=True)

    .. py:attribute:: quaternion


        .. sourcecode:: python

            Vector4(default_value=[0,0,0,1]).tag(sync=True)

    .. py:attribute:: scale


        .. sourcecode:: python

            Vector3(default_value=[1,1,1]).tag(sync=True)

    .. py:attribute:: modelViewMatrix


        .. sourcecode:: python

            Matrix4(default_value=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]).tag(sync=True)

    .. py:attribute:: normalMatrix


        .. sourcecode:: python

            Matrix3(default_value=[1,0,0,0,1,0,0,0,1]).tag(sync=True)

    .. py:attribute:: matrix


        .. sourcecode:: python

            Matrix4(default_value=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]).tag(sync=True)

    .. py:attribute:: matrixWorld


        .. sourcecode:: python

            Matrix4(default_value=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]).tag(sync=True)

    .. py:attribute:: matrixAutoUpdate


        .. sourcecode:: python

            Bool(True, allow_none=False).tag(sync=True)

    .. py:attribute:: matrixWorldNeedsUpdate


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: visible


        .. sourcecode:: python

            Bool(True, allow_none=False).tag(sync=True)

    .. py:attribute:: castShadow


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: receiveShadow


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: frustumCulled


        .. sourcecode:: python

            Bool(True, allow_none=False).tag(sync=True)

    .. py:attribute:: renderOrder


        .. sourcecode:: python

            CInt(0, allow_none=False).tag(sync=True)

