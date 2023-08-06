pygalmesh
=========

A Python frontend to `CGAL <https://www.cgal.org/>`__'s `3D mesh
generation
capabilities <https://doc.cgal.org/latest/Mesh_3/index.html>`__.

|CircleCI| |Codacy grade| |PyPi Version| |GitHub stars|

pygalmesh makes it easy to create high-quality 3D volume and surface
meshes.

Background
~~~~~~~~~~

CGAL offers two different approaches for mesh generation:

1. Meshes defined implicitly by level sets of functions.
2. Meshes defined by a set of bounding planes.

pygalmesh provides a front-end to the first approach, which has the
following advantages and disadvantages:

-  All boundary points are guaranteed to be in the level set within any
   specified residual. This results in smooth curved surfaces.
-  Sharp intersections of subdomains (e.g., in unions or differences of
   sets) need to be specified manually (via feature edges, see below),
   which can be tedious.

On the other hand, the bounding-plane approach (realized by
`mshr <https://bitbucket.org/fenics-project/mshr>`__), has the following
properties:

-  Smooth, curved domains are approximated by a set of bounding planes,
   resulting in more of less visible edges.
-  Intersections of domains can be computed automatically, so domain
   unions etc. have sharp edges where they belong.

Other Python mesh generators are
`pygmsh <https://github.com/nschloe/pygmsh>`__ (a frontend to
`gmsh <http://gmsh.info/>`__) and
`MeshPy <https://github.com/inducer/meshpy>`__.
`meshzoo <https://github.com/nschloe/meshzoo>`__ provides some basic
canonical meshes.

Examples
~~~~~~~~

A simple ball
^^^^^^^^^^^^^

.. figure:: https://nschloe.github.io/pygalmesh/ball.png
   :alt: Ball

   Ball

.. code:: python

    import pygalmesh

    s = pygalmesh.Ball([0, 0, 0], 1.0)
    pygalmesh.generate_mesh(s, 'out.mesh', cell_size=0.2)

CGAL's mesh generator returns Medit-files, which can be processed by,
e.g., `meshio <https://github.com/nschloe/meshio>`__.

.. code:: python

    import meshio
    vertices, cells, _, _, _ = meshio.read('out.mesh')

The mesh generation comes with many more options, described
`here <https://doc.cgal.org/latest/Mesh_3/>`__. Try, for example,

.. code:: python

    pygalmesh.generate_mesh(
        s,
        'out.mesh',
        cell_size=0.2,
        edge_size=0.1,
        odt=True,
        lloyd=True,
        verbose=False
        )

Other primitive shapes
^^^^^^^^^^^^^^^^^^^^^^

.. figure:: https://nschloe.github.io/pygalmesh/tetra.png
   :alt: Tetrahedron

   Tetrahedron

pygalmesh provides out-of-the-box support for balls, cuboids,
ellipsoids, tori, cones, cylinders, and tetrahedra. Try for example

.. code:: python

    import pygalmesh

    s0 = pygalmesh.Tetrahedron(
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0]
            )
    pygalmesh.generate_mesh(
            s0, 'out.mesh', cell_size=0.1, edge_size=0.1
            )

Domain combinations
^^^^^^^^^^^^^^^^^^^

.. figure:: https://nschloe.github.io/pygalmesh/ball-difference.png
   :alt: Balls difference

   Balls difference

Supported are unions, intersections, and differences of all domains. As
mentioned above, however, the sharp intersections between two domains
are not automatically handled. Try for example

.. code:: python

    import pygalmesh

    radius = 1.0
    displacement = 0.5
    s0 = pygalmesh.Ball([displacement, 0, 0], radius)
    s1 = pygalmesh.Ball([-displacement, 0, 0], radius)
    u = pygalmesh.Difference(s0, s1)

To sharpen the intersection circle, add it as a feature edge polygon
line, e.g.,

.. code:: python

    a = numpy.sqrt(radius**2 - displacement**2)
    edge_size = 0.15
    n = int(2*numpy.pi*a / edge_size)
    circ = [
        [
            0.0,
            a * numpy.cos(i * 2*numpy.pi / n),
            a * numpy.sin(i * 2*numpy.pi / n)
        ] for i in range(n)
        ]
    circ.append(circ[0])

    pygalmesh.generate_mesh(
            u,
            'out.mesh',
            feature_edges=[circ],
            cell_size=0.15,
            edge_size=edge_size,
            facet_angle=25,
            facet_size=0.15,
            cell_radius_edge_ratio=2.0
            )

Note that the length of the polygon legs are kept in sync with the
``edge_size`` of the mesh generation. This makes sure that it fits in
nicely with the rest of the mesh.

Domain deformations
^^^^^^^^^^^^^^^^^^^

.. figure:: https://nschloe.github.io/pygalmesh/egg.png
   :alt: Egg

   Egg

You can of course translate, rotate, scale, and stretch any domain. Try,
for example,

.. code:: python

    import pygalmesh

    s = pygalmesh.Stretch(
            pygalmesh.Ball([0, 0, 0], 1.0),
            [1.0, 2.0, 0.0]
            )

    pygalmesh.generate_mesh(
            s,
            'out.mesh',
            cell_size=0.1
            )

Extrusion of 2D polygons
^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: https://nschloe.github.io/pygalmesh/triangle-rotated.png
   :alt: triangle rotated

   triangle rotated

pygalmesh lets you extrude any polygon into a 3D body. It even supports
rotation alongside!

.. code:: python

    import pygalmesh

    p = pygalmesh.Polygon2D([[-0.5, -0.3], [0.5, -0.3], [0.0, 0.5]])
    edge_size = 0.1
    domain = pygalmesh.Extrude(
            p,
            [0.0, 0.0, 1.0],
            0.5 * 3.14159265359,
            edge_size
            )
    pygalmesh.generate_mesh(
            domain,
            'out.mesh',
            cell_size=0.1,
            edge_size=edge_size,
            verbose=False
            )

Feature edges are automatically preserved here, which is why an edge
length needs to be given to ``pygalmesh.Extrude``.

Rotation bodies
^^^^^^^^^^^^^^^

.. figure:: https://nschloe.github.io/pygalmesh/circle-rotate-extr.png
   :alt: triangle ring extruded

   triangle ring extruded

Polygons in the x-z-plane can also be rotated around the z-axis to yield
a rotation body.

.. code:: python

    import pygalmesh

    p = pygalmesh.Polygon2D([[0.5, -0.3], [1.5, -0.3], [1.0, 0.5]])
    edge_size = 0.1
    domain = pygalmesh.ring_extrude(p, edge_size)
    pygalmesh.generate_mesh(
            domain,
            'out.mesh',
            cell_size=0.1,
            edge_size=edge_size,
            verbose=False
            )

Your own custom level set function
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: https://nschloe.github.io/pygalmesh/heart.png
   :alt: triangle ring extruded

   triangle ring extruded

If all of the variety is not enough for you, you can define your own
custom level set function. You simply need to subclass
``pygalmesh.DomainBase`` and specify a function, e.g.,

.. code:: python

    import pygalmesh
    class Heart(pygalmesh.DomainBase):
        def __init__(self):
            super(Heart, self).__init__()
            return

        def eval(self, x):
            return (x[0]**2 + 9.0/4.0 * x[1]**2 + x[2]**2 - 1)**3 \
                - x[0]**2 * x[2]**3 - 9.0/80.0 * x[1]**2 * x[2]**3

        def get_bounding_sphere_squared_radius(self):
            return 10.0

    d = Heart()
    pygalmesh.generate_mesh(d, 'out.mesh', cell_size=0.1)

Note that you need to specify the square of a bounding sphere radius,
used as an input to CGAL's mesh generator.

Surface meshes
^^^^^^^^^^^^^^

If you're only after the surface of a body, pygalmesh has
``generate_surface_mesh`` for you. It offers fewer options (obviously,
``cell_size`` is gone), but otherwise works the same way:

.. code:: python

    import pygalmesh

    s = pygalmesh.Ball([0, 0, 0], 1.0)
    pygalmesh.generate_surface_mesh(
            s,
            'out.off',
            angle_bound=30,
            radius_bound=0.1,
            distance_bound=0.1
            )

The output format is
`OFF <http://segeval.cs.princeton.edu/public/off_format.html>`__ which
again is handled by `meshio <https://github.com/nschloe/meshio>`__.

Refer to `CGAL's
documention <https://doc.cgal.org/latest/Surface_mesher/index.html>`__
for the options.

Meshes from OFF files
^^^^^^^^^^^^^^^^^^^^^

.. figure:: https://nschloe.github.io/pygalmesh/elephant.png
   :alt: elephant

   elephant

If you have an OFF file at hand (like
`elephant.off <https://raw.githubusercontent.com/CGAL/cgal-swig-bindings/master/examples/data/elephant.off>`__
or
`these <https://github.com/CGAL/cgal/tree/master/Surface_mesher/demo/Surface_mesher/inputs>`__),
pygalmesh generates the mesh via

.. code:: python

    import pygalmesh

    pygalmesh.generate_from_off(
            'elephant.off',
            'out.mesh',
            facet_angle=25.0,
            facet_size=0.15,
            facet_distance=0.008,
            cell_radius_edge_ratio=3.0,
            verbose=False
            )

Installation
~~~~~~~~~~~~

For installation, pygalmesh needs `CGAL <https://www.cgal.org/>`__ and
`Eigen <http://eigen.tuxfamily.org/index.php?title=Main_Page>`__
installed on your system. They are typically available on your Linux
distribution, e.g., on Ubuntu

::

    sudo apt install libcgal-dev libeigen3-dev

After that, pygalmesh can be `installed from the Python Package
Index <https://pypi.python.org/pypi/pygalmesh/>`__, so with

::

    pip install -U pygalmesh

you can install/upgrade.

`meshio <https://github.com/nschloe/meshio>`__
(``sudo -H pip install meshio``) can be helpful in processing the
meshes.

Manual installation
^^^^^^^^^^^^^^^^^^^

For manual installation (if you're a developer or just really keen on
getting the bleeding edge version of pygalmesh), there are two
possibilities:

-  Get the sources, type ``sudo python setup.py install``. This does the
   trick most the time.
-  As a fallback, there's a CMake-based installation. Simply go
   ``cmake    /path/to/sources/`` and ``make``.

Testing
~~~~~~~

To run the pygalmesh unit tests, check out this repository and type

::

    pytest

Distribution
~~~~~~~~~~~~

To create a new release

1. bump the ``__version__`` number (in ``setup.py`` *and*
   ``src/pygalmesh.i``)

2. publish to PyPi and GitHub:

   ::

       make publish

License
~~~~~~~

pygalmesh is published under the `MIT
license <https://en.wikipedia.org/wiki/MIT_License>`__.

.. |CircleCI| image:: https://img.shields.io/circleci/project/github/nschloe/pygalmesh/master.svg
   :target: https://circleci.com/gh/nschloe/pygalmesh/tree/master
.. |Codacy grade| image:: https://img.shields.io/codacy/grade/26d491d592134f438c6175a250290915.svg
   :target: https://app.codacy.com/app/nschloe/pygalmesh/dashboard
.. |PyPi Version| image:: https://img.shields.io/pypi/v/pygalmesh.svg
   :target: https://pypi.python.org/pypi/pygalmesh
.. |GitHub stars| image:: https://img.shields.io/github/stars/nschloe/pygalmesh.svg?style=social&label=Stars&logo=github
   :target: https://github.com/nschloe/pygalmesh
