
.. py:currentmodule:: pythreejs

Geometry
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: Geometry()
    :members:
    :undoc-members:

    This widget has some manual overrides on the Python side.

    Inherits :py:class:`~pythreejs.BaseGeometry`.

    Three.js docs: https://threejs.org/docs/#api/core/Geometry


    .. py:attribute:: vertices


        .. sourcecode:: python

            List(trait=List()).tag(sync=True)

    .. py:attribute:: colors


        .. sourcecode:: python

            List(trait=Unicode(), default_value=["#ffffff"]).tag(sync=True)

    .. py:attribute:: faces


        .. sourcecode:: python

            Tuple(trait=Face3()).tag(sync=True)

    .. py:attribute:: faceVertexUvs


        .. sourcecode:: python

            List().tag(sync=True)

    .. py:attribute:: lineDistances


        .. sourcecode:: python

            List().tag(sync=True)

    .. py:attribute:: morphTargets


        .. sourcecode:: python

            List().tag(sync=True)

    .. py:attribute:: morphNormals


        .. sourcecode:: python

            List().tag(sync=True)

    .. py:attribute:: skinWeights


        .. sourcecode:: python

            List(trait=List()).tag(sync=True)

    .. py:attribute:: skinIndices


        .. sourcecode:: python

            List(trait=List()).tag(sync=True)

    .. py:attribute:: _ref_geometry


        .. sourcecode:: python

            Instance(BaseGeometry, allow_none=True).tag(sync=True, **widget_serialization)

    .. py:attribute:: _store_ref


        .. sourcecode:: python

            Bool(False, allow_none=False).tag(sync=True)

    .. py:attribute:: type


        .. sourcecode:: python

            Unicode("Geometry", allow_none=False).tag(sync=True)

