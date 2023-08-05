PyTecplot
=========

The pytecplot library is a high level API that connects your Python script
to the power of the |Tecplot 360| visualization engine. It offers line
plotting, 2D and 3D surface plots in a variety of formats, and 3D volumetric
visualization. Familiarity with |Tecplot 360| and the |Tecplot 360|
macro language is helpful, but not required.

Documentation
-------------

The full documentation is here: http://www.tecplot.com/docs/pytecplot

.. note::
    |PyTecplot| supports 64-bit Python versions 2.7 and 3.4+. |PyTecplot|
    does not support 32 bit Python. Please refer to INSTALL.rst for
    installation instructions and environment setup. For the best
    experience, developers are encouraged to use the **latest version of
    Python**.

Quick Start
-----------

Please refer to the documentation for detailed installation instructions and
environment setup. The short of it is something like this::

    pip install pytecplot

Linux and OSX users may have to set ``LD_LIBRARY_PATH`` or
``DYLD_LIBRARY_PATH`` to the directories containing the |Tecplot 360|
dynamic libraries. Please refer to the documentation at
http://www.tecplot.com/docs/pytecplot for detailed information regarding setup
and use. In addition, the web page
http://www.tecplot.com/support/faqs/pytecplot contains a list of answered
questions you may have about |PyTecplot| in general.

.. |Tecplot 360| replace:: `Tecplot 360 <http://www.tecplot.com/products/tecplot-360/>`__
.. |PyTecplot| replace:: `PyTecplot <http://www.tecplot.com/docs/pytecplot>`__

Change Log
----------

PyTecplot 0.9.4
^^^^^^^^^^^^^^^

Released with Tecplot 360 2018 R1

* New feature: tp.data.query.probe_on_surface()
* Dataset.add_poly_zone() now requires the num_faces parameter (was optional).
* More efficient and reliable array handling when connected to running 360
* Minor documentation updates

PyTecplot 0.9.3
^^^^^^^^^^^^^^^

* Added IsosurfaceVector style access
* probe_at_position() now returns None when the point is outside the data volume
* Added tp.layout.num_pages() to get the number pages in a layout
* Bug fix: DataSet.add_zone() family of functions now obeys the strand argument
* Several documentation corrections

PyTecplot 0.9.1
^^^^^^^^^^^^^^^

Released with Tecplot 360 2017 R3 December Maintenance Release

* Recording of save layout, data and stylesheet commands

PyTecplot 0.9.0
^^^^^^^^^^^^^^^

Released with Tecplot 360 2017 R3

* TecUtil Server (PyTecplot Connections) stability and performance enhancements
* PyTecplot script recording via 360
* Added vector image export methods: save_ps(), save_wmf()
* pyzmq and flatbuffers are now installed by default when installing PyTecplot
  with pip
* Macro execute extended command
* Several documentation enhancements and internal bug fixes
* Dataset solution time access now requires Tecplot 2017.3 or later due to bug
  in engine
* Plot.fieldmaps() became function requiring parentheses
* New methods: Variable min(), max() and minmax()
* Zone min(), max() and minmax() became functions requiring parentheses
* When exporting images: width now defaults to 800, super sample defaults to 3
* Streamtrace.add_on_zone_surface() now uses the active zones by default
* CGNS loader will load boundary conditions by default
* Localization fix for roaming using non-en_US license servers
* Rename: axes.edge_auto_reset to axes.auto_edge_assignment
* Fixed exporting mpeg4 animations via macro language

PyTecplot 0.8.2
^^^^^^^^^^^^^^^

* Several bug fixes for 3rd party data loaders
* Connect to TecUtilServer (RPC) substantially more capable
* Aux data can now be cleared with AuxData.clear()
* Lots of documentation updates
* Can now control frame position and dimensions
* Sharing and branching variables and connectivity across zones has been added
* Passiveness for Arrays was added.
* Added support for RAWDATA when executing macro commands from python
* ``Array.__len__()`` now returning the length of the flattened array
* Data loaders now use ReadDataOption instead of the boolean append parameter
* Saving layout with '.lpk' extension implicitly includes data now
* Setting contour variable now implicitly resets the contour levels to nice
* More information is given on start-up errors

PyTecplot 0.8.1
^^^^^^^^^^^^^^^

Released with Tecplot 360 2017 R2

* Defaults change: allowing interpolation using all source zones by default
* Documentation fixes
* Unittests now handle out-of-date SDK with Python optimization
* Documentation text replacement tags now available

PyTecplot 0.8.0
^^^^^^^^^^^^^^^

* Interpolation methods: linear, inverse distance and krigging
* "Additional Quantities" loadable from Fluent data
* Legend style control
* Vector in 2D and 3D plot styles
* Reference vector
* Subzone load-on-demand (SZL) file loader
* rename: save_tecplot_binary() -> save_tecplot_plt()
* Aux data now accessible
* View and zooming control for 3D plots
* rename: tecinterprocess -> tecutil_connector
* Slice zone extraction from arbitrary point and normal
* Solution time and strand accessors for plots and datasets
* Orientation reference axis style and placement control
* More examples
* Lots of documentation added
* Many bug fixes

PyTecplot 0.7.0
^^^^^^^^^^^^^^^

* FaceNeighbors, Facemap and Nodemap.
* Streamlines
* Many doc updates and fixes.
* Streamtrace examples updates.
* "Working with datasets" examples.
* Streamtrace add functions.
* Continuous colormap min/max properties.
* Can now delete text annotations with Frame.delete_text()
* New script for 360 distribution: tec3560-env for easy setup of pytecplot.

PyTecplot 0.6.1
^^^^^^^^^^^^^^^

Released with Tecplot 360 2017 R1

* Better roaming, licensing and exception handling.
* Many documentation updates.
* Many minor bug fixes.
* Fluent loader.
* Reworked installation instructions.
* Better CGNS support.
* Zone.rank/dimensions rework.
* Zone class split into OrderedZone, ClassicFEZone and PolyFEZone.
* rename: font_family --> typeface.

PyTecplot 0.3.4
^^^^^^^^^^^^^^^

* Isosurface style control.
* Slice style control.
* Actions for Axes and Axis.
* Dataset, Zone, Variable and Array fully documented and unittested.
* Many internal bug fixes.
* rename in API: Zone.variable() --> Zone.values()
* rename in API: Variable.zone() --> variable.values()
* Minor bug fixes for Mac

PyTecplot 0.3.2
^^^^^^^^^^^^^^^

* Lots of bug fixes, both internal and external.
* Mostly internal testing and packaging updates.

PyTecplot 0.3.1
^^^^^^^^^^^^^^^

* First public release of PyTecplot
* Tecplot exceptions have been reworked and extended.
* tecplot.data.load_tecplot() fully implemented and now supports multiple input
  files in both binary and ASCII.
* Axis classes have been reworked and cleaned up along with examples and
  unittests.
* User's get "tecplot 360 out-of-date" error if tecinterprocess.so can't be
  loaded.
* Lot's of internal consistency testing.
* Text annotations.
* Fieldmap accessed by zone.
* Plot-level style control.
