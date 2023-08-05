
.. py:currentmodule:: pythreejs

FlyControls
====================================================

.. Use autoclass to fill any memebers not manually specified.
   This ensures it picks up any members in overridden classes.

.. autohastraits:: FlyControls(controlling=None, )
    :members:
    :undoc-members:


    Inherits :py:class:`~pythreejs.Controls`.

    Three.js docs: https://threejs.org/docs/#api/controls/FlyControls


    .. py:attribute:: moveVector


        .. sourcecode:: python

            Vector3(default_value=[0,0,0]).tag(sync=True)

    .. py:attribute:: rotationVector


        .. sourcecode:: python

            Vector3(default_value=[0,0,0]).tag(sync=True)

    .. py:attribute:: movementSpeed


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

    .. py:attribute:: rollSpeed


        .. sourcecode:: python

            CFloat(0.05, allow_none=False).tag(sync=True)

    .. py:attribute:: syncRate


        .. sourcecode:: python

            CFloat(1, allow_none=False).tag(sync=True)

