
.. py:currentmodule:: pythreejs

Fog
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: Fog(color="white", near=1, far=1000, )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.ThreeWidget`.

    Three.js docs: https://threejs.org/docs/#api/scenes/Fog


    .. py:attribute:: name


        .. sourcecode:: python

            Unicode('', allow_none=False).tag(sync=True)

    .. py:attribute:: color


        .. sourcecode:: python

            Unicode("white", allow_none=False).tag(sync=True)

    .. py:attribute:: near


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: far


        .. sourcecode:: python

            CFloat(1000, allow_none=False).tag(sync=True)

