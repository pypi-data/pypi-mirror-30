
.. py:currentmodule:: pythreejs

WireframeGeometry
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: WireframeGeometry(geometry=None, )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.BaseGeometry`.

    Three.js docs: https://threejs.org/docs/#api/geometries/WireframeGeometry


    .. py:attribute:: geometry


        .. sourcecode:: python

            Union([
                Instance(BaseGeometry, allow_none=True),
                Instance(BaseBufferGeometry, allow_none=True)
            ]).tag(sync=True, **widget_serialization)

    .. py:attribute:: type


        .. sourcecode:: python

            Unicode("WireframeGeometry", allow_none=False).tag(sync=True)

