Steno3D Parser: .obj
********************

.. image:: https://travis-ci.org/seequent/steno3d-obj.svg?branch=master
    :target: https://travis-ci.org/seequent/steno3d-obj

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :alt: MIT License
    :target: https://github.com/seequent/steno3d-obj/blob/master/LICENSE

.. image:: https://img.shields.io/badge/download-PyPI-yellow.svg
    :target: https://pypi.python.org/pypi/steno3d_obj

Welcome to the .obj file parser plugin for `Steno3D <https://www.steno3d.com>`_
by `Seequent <https://www.seequent.com>`_. This repository supplements the
`Steno3D Python client library <https://github.com/seequent/steno3dpy>`_.

To install this parser, simply

.. code::

    pip install steno3d_obj

On import, this parser plugs in to the `steno3d.parsers` module. It can be
used as follows:

.. code:: python

    import steno3d
    import steno3d_obj
    parser = steno3d.parsers.obj('yourfile.obj')
    (obj_project,) = parser.parse()

Currently, this parser only supports basic faces, lines, and points.
Textures, normals, free-form curves/surfaces, groupings, and display attributes
are all ignored. Detailed .obj file documentation can be found
`here <http://www.cs.utah.edu/~boulos/cs3505/obj_spec.pdf>`_.

If you are interested in increased support you may
`submit an issue <https://github.com/seequent/steno3d-obj/issues>`_
or consider directly contributing to the
`github repository <https://github.com/seequent/steno3d-obj>`_. `Parser
guidelines <https://python.steno3d.com/en/latest/content/parsers.html>`_
are available online.

To learn more, about Steno3D, visit `steno3d.com <https://www.steno3d.com>`_, the
`Steno3D source repository <https://github.com/seequent/steno3dpy>`_, and our
`online documentation <https://steno3d.com/docs>`_.
