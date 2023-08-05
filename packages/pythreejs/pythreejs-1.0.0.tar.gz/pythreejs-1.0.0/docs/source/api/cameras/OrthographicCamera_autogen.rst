
.. py:currentmodule:: pythreejs

OrthographicCamera
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: OrthographicCamera(left=0, right=0, top=0, bottom=0, near=0.1, far=2000, )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.Camera`.

    Three.js docs: https://threejs.org/docs/#api/cameras/OrthographicCamera


    .. py:attribute:: zoom


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: left


        .. sourcecode:: python

            CFloat(0, allow_none=False).tag(sync=True)

    .. py:attribute:: right


        .. sourcecode:: python

            CFloat(0, allow_none=False).tag(sync=True)

    .. py:attribute:: top


        .. sourcecode:: python

            CFloat(0, allow_none=False).tag(sync=True)

    .. py:attribute:: bottom


        .. sourcecode:: python

            CFloat(0, allow_none=False).tag(sync=True)

    .. py:attribute:: near


        .. sourcecode:: python

            CFloat(0.1, allow_none=False).tag(sync=True)

    .. py:attribute:: far


        .. sourcecode:: python

            CFloat(2000, allow_none=False).tag(sync=True)

    .. py:attribute:: type


        .. sourcecode:: python

            Unicode("OrthographicCamera", allow_none=False).tag(sync=True)

