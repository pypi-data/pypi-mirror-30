Layout
======

..  contents::
    :local:
    :depth: 1

tecplot.layout
--------------

.. automodule:: tecplot.layout

active_frame()
--------------

.. autofunction:: tecplot.active_frame

active_page()
-------------

.. autofunction:: tecplot.active_page

add_page()
----------

.. autofunction:: tecplot.add_page

delete_page()
-------------

.. autofunction:: tecplot.delete_page

next_page()
-----------

.. autofunction:: tecplot.next_page

new_layout()
------------

.. autofunction:: tecplot.new_layout

load_layout()
-------------

.. autofunction:: tecplot.load_layout

page()
------

.. autofunction:: tecplot.page

pages()
-------

.. autofunction:: tecplot.pages

save_layout()
-------------

.. autofunction:: tecplot.save_layout

layout.aux_data()
-----------------

.. autofunction:: tecplot.layout.aux_data


.. py:currentmodule:: tecplot.layout

Frame
-----

.. autoclass:: Frame

    **Attributes**

    .. autosummary::
        :nosignatures:

        active
        aux_data
        background_color
        border_thickness
        dataset
        has_dataset
        header_background_color
        height
        name
        page
        plot_type
        position
        show_border
        show_header
        size_pos_units
        transparent
        width

    **Methods**

    .. autosummary::

        activate
        activated
        active_zones
        add_text
        create_dataset
        delete_text
        geometries
        images
        load_stylesheet
        move_to_bottom
        move_to_top
        plot
        save_stylesheet
        texts

.. automethod:: Frame.activate
.. automethod:: Frame.activated
.. autoattribute:: Frame.active
.. automethod:: Frame.active_zones
.. automethod:: Frame.add_text
.. autoattribute:: Frame.aux_data
.. autoattribute:: Frame.background_color
.. autoattribute:: Frame.border_thickness
.. automethod:: Frame.create_dataset
.. autoattribute:: Frame.dataset
.. automethod:: Frame.delete_text
.. automethod:: Frame.geometries
.. autoattribute:: Frame.has_dataset
.. autoattribute:: Frame.header_background_color
.. autoattribute:: Frame.height
.. automethod:: Frame.images
.. automethod:: Frame.load_stylesheet
.. automethod:: Frame.move_to_bottom
.. automethod:: Frame.move_to_top
.. autoattribute:: Frame.name
.. autoattribute:: Frame.page
    :annotation:
.. automethod:: Frame.plot
.. autoattribute:: Frame.plot_type
.. autoattribute:: Frame.position
.. automethod:: Frame.save_stylesheet
.. autoattribute:: Frame.show_border
.. autoattribute:: Frame.show_header
.. autoattribute:: Frame.size_pos_units
.. automethod:: Frame.texts
.. autoattribute:: Frame.transparent
.. autoattribute:: Frame.width

.. py:currentmodule:: tecplot.layout

Page
----

.. autoclass:: Page

    **Attributes**

    .. autosummary::
        :nosignatures:

        active
        aux_data
        exists
        name
        paper
        position

    **Methods**

    .. autosummary::

        activate
        activated
        active_frame
        add_frame
        delete_frame
        frame
        frames
        tile_frames

.. automethod:: Page.activate
.. automethod:: Page.activated
.. autoattribute:: Page.active
.. automethod:: Page.active_frame
.. automethod:: Page.add_frame
.. autoattribute:: Page.aux_data
.. automethod:: Page.delete_frame
.. autoattribute:: Page.exists
.. automethod:: Page.frame
.. automethod:: Page.frames
.. autoattribute:: Page.name
.. autoattribute:: Page.paper
.. autoattribute:: Page.position
.. automethod:: Page.tile_frames

.. py:currentmodule:: tecplot.layout

Paper
-----

.. autoclass:: Paper

    **Attributes**

    .. autosummary::
        :nosignatures:

        dimensions

.. autoattribute:: Paper.dimensions
