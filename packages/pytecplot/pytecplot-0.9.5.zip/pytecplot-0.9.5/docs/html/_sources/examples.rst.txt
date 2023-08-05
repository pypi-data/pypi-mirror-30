Examples
========

..  contents::
    :local:
    :depth: 1

.. _hello_world:

Hello World
-----------

A simple "Hello, World!" adds text to the active frame and exports the frame to
an image file.

.. figure:: /_static/images/hello_world.png
    :width: 300px
    :figwidth: 300px

.. literalinclude:: ../../examples/00_hello_world.py

Loading Layouts
---------------

Layouts can be loaded with the `tecplot.load_layout()` method. This will accept
both ``lay`` and ``lpk`` (packaged) files. The exported image interprets the
image type by the extension you give it. See `tecplot.export.save_png()` for
more details. Notice in this example, we turn on logging down to the ``DEBUG``
level which is extremely verbose. This is useful for debugging the connection
between the script and |Tecplot 360|.

.. figure:: /_static/images/layout_example.png
    :width: 300px
    :figwidth: 300px

.. literalinclude:: ../../examples/01_load_layout_save_image.py

Extracting Slices
-----------------

This script produces two images: a 3D view of the wing and a simplified pressure coefficient plot half-way down the wing:

.. figure:: /_static/images/wing.png
    :width: 300px
    :figwidth: 300px
.. figure:: /_static/images/wing_pressure_coefficient.png
    :width: 300px
    :figwidth: 300px

.. literalinclude:: ../../examples/03_slices_along_wing.py

Numpy Integration
-----------------

.. note:: Numpy, SciPy Required

    This example requires both `numpy <http://www.numpy.org>`_ and `scipy
    <http://www.numpy.org/>`_ installed. SciPy, in turn, requires a conforming
    linear algebra system such as OpenBLAS, LAPACK, ATLAS or MKL. It is
    recommended to use your operating system's package manager to do this.
    Windows users and/or users that do not have root access to their machines
    might consider using `Anaconda <https://www.continuum.io/>`_ to setup a
    virtual environment where they can install python, numpy, scipy and all of
    its dependencies.

The spherical harmonic ``(n,m) = (5,4)`` is calculated at unit radius. The magnitude is then used to create a 3D shape. The plot-style is modified and the following image is exported and the layout is saved in "packaged format."

.. figure:: /_static/images/spherical_harmonic_4_5.png
    :width: 300px
    :figwidth: 300px

.. literalinclude:: ../../examples/04_spherical_harmonic.py

Execute Equation
----------------

This example illustrates altering data through equations in two zones. For
complete information on the |Tecplot Engine| "data alter" syntax, see Chapter
21, *Data Operations*, in the |Tecplot 360| User's Manual. This script
outputs the original data followed by the same image where we've modified the
scaling of ``Nj`` only on the wings.

.. figure:: /_static/images/F18_orig.png
    :width: 300px
    :figwidth: 300px

.. figure:: /_static/images/F18_altered.png
    :width: 300px
    :figwidth: 300px

.. literalinclude:: ../../examples/07_execute_equation.py

Line Plots
----------

This example shows how to set the style for a plot of three lines. The y-axis
label and legend labels are changed and the axes are adjusted to fit the data.

.. figure:: /_static/images/linemap.png
    :width: 300px
    :figwidth: 300px

.. literalinclude:: ../../examples/11_linemaps.py

Creating Slices
---------------

This example illustrates reading a dataset then creating and showing arbitrary
slices of the dataset. A primary slice, start, end, and 3 intermediate slices
are shown.

.. figure:: /_static/images/slice_example.png
    :width: 300px
    :figwidth: 300px

.. literalinclude:: ../../examples/12_slices.py

Creating Iso-surfaces
---------------------

This example illustrates reading a dataset, then creating and showing
isosurfaces.

.. figure:: /_static/images/isosurface_example.png
    :width: 300px
    :figwidth: 300px

.. literalinclude:: ../../examples/14_isosurface.py

Wing Surface Slices
-------------------

This example illustrates reading a dataset and showing surface slices with
colored mesh on the Onera M6 Wing. Seven surface slices are shown, colored by
the distance along the Y axis.

.. figure:: /_static/images/wing_slices.png
    :width: 300px
    :figwidth: 300px

.. literalinclude:: ../../examples/13_wing_slices.py

Mach Iso-surfaces
-----------------

This example illustrates using contour group properties to define multiple
Iso-surfaces. In this case, multiple Mach values are shown as Iso-surfaces.

.. figure:: /_static/images/wing_iso.png
    :width: 300px
    :figwidth: 300px

.. literalinclude:: ../../examples/15_wing_mach_iso.py

Exception Handling
------------------

It is the policy of the |PyTecplot| Python module to raise exceptions on any failure. It is the user's job to catch them or otherwise prevent them by ensuring the |Tecplot Engine| is properly setup to the task you ask of it. Aside from exceptions raised by the underlying Python core libraries, |PyTecplot| may raise a subclass of `TecplotError`, the most common being `TecplotRuntimeError`.

.. figure:: /_static/images/spaceship.png
    :width: 300px
    :figwidth: 300px

.. literalinclude:: ../../examples/02_exception_handling.py

Streamtraces
------------

Using the transient Vortex Shedding layout a rake of 2D streamtrace lines are added.

.. figure:: /_static/images/streamtrace_2D.png
    :width: 300px
    :figwidth: 300px

.. literalinclude:: ../../examples/19_streamtrace_2D.py


This example illustrates adding a rake of streamtraces.

.. figure:: /_static/images/streamtrace_line_example.png
    :width: 300px
    :figwidth: 300px

.. literalinclude:: ../../examples/17_streamtrace_line.py


This example illustrates adding ribbon streamtrace.

.. figure:: /_static/images/streamtrace_ribbon_example.png
    :width: 300px
    :figwidth: 300px

.. literalinclude:: ../../examples/18_streamtrace_ribbon.py

Line Legend
-----------

This example illustrates displaying an XY line legend and changing its attributes.

.. figure:: /_static/images/legend_line.png
    :width: 300px
    :figwidth: 300px

.. literalinclude:: ../../examples/20_legend_line.py

Contour Legend
--------------

This example illustrates displaying a contour legend and changing its attributes.

.. figure:: /_static/images/legend_contour.png
    :width: 300px
    :figwidth: 300px

.. literalinclude:: ../../examples/21_legend_contour.py

3D View
-------

This example illustrates changing the attributes of the 3D view.

.. figure:: /_static/images/3D_view.png
    :width: 300px
    :figwidth: 300px

.. literalinclude:: ../../examples/22_view_3D.py
