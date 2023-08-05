Axes
====

..  contents::
    :local:
    :depth: 3


.. _fieldaxes:

.. _fieldaxis:

Field Axes
----------

..  contents::
    :local:
    :depth: 1

.. py:currentmodule:: tecplot.plot

Cartesian2DFieldAxes
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: Cartesian2DFieldAxes

    **Attributes**

    .. autosummary::
        :nosignatures:

        auto_adjust_ranges
        axis_mode
        grid_area
        precise_grid
        preserve_scale
        viewport
        x_axis
        xy_ratio
        y_axis

.. autoattribute:: Cartesian2DFieldAxes.auto_adjust_ranges
.. autoattribute:: Cartesian2DFieldAxes.axis_mode
.. autoattribute:: Cartesian2DFieldAxes.grid_area
.. autoattribute:: Cartesian2DFieldAxes.precise_grid
.. autoattribute:: Cartesian2DFieldAxes.preserve_scale
.. autoattribute:: Cartesian2DFieldAxes.viewport
.. autoattribute:: Cartesian2DFieldAxes.x_axis
.. autoattribute:: Cartesian2DFieldAxes.xy_ratio
.. autoattribute:: Cartesian2DFieldAxes.y_axis

.. py:currentmodule:: tecplot.plot

Cartesian2DFieldAxis
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: Cartesian2DFieldAxis

    **Attributes**

    .. autosummary::
        :nosignatures:

        grid_lines
        line
        log_scale
        marker_grid_line
        max
        min
        minor_grid_lines
        reverse
        show
        tick_labels
        ticks
        title
        variable
        variable_index

    **Methods**

    .. autosummary::

        adjust_range_to_nice
        fit_range
        fit_range_to_nice

.. automethod:: Cartesian2DFieldAxis.adjust_range_to_nice
.. automethod:: Cartesian2DFieldAxis.fit_range
.. automethod:: Cartesian2DFieldAxis.fit_range_to_nice
.. autoattribute:: Cartesian2DFieldAxis.grid_lines
.. autoattribute:: Cartesian2DFieldAxis.line
.. autoattribute:: Cartesian2DFieldAxis.log_scale
.. autoattribute:: Cartesian2DFieldAxis.marker_grid_line
.. autoattribute:: Cartesian2DFieldAxis.max
.. autoattribute:: Cartesian2DFieldAxis.min
.. autoattribute:: Cartesian2DFieldAxis.minor_grid_lines
.. autoattribute:: Cartesian2DFieldAxis.reverse
.. autoattribute:: Cartesian2DFieldAxis.show
.. autoattribute:: Cartesian2DFieldAxis.tick_labels
.. autoattribute:: Cartesian2DFieldAxis.ticks
.. autoattribute:: Cartesian2DFieldAxis.title
.. autoattribute:: Cartesian2DFieldAxis.variable
.. autoattribute:: Cartesian2DFieldAxis.variable_index

.. py:currentmodule:: tecplot.plot

Cartesian3DFieldAxes
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: Cartesian3DFieldAxes

    **Attributes**

    .. autosummary::
        :nosignatures:

        aspect_ratio_limit
        aspect_ratio_reset
        auto_edge_assignment
        axis_mode
        grid_area
        orientation_axis
        padding
        preserve_scale
        range_aspect_ratio_limit
        range_aspect_ratio_reset
        viewport
        x_axis
        xy_ratio
        xz_ratio
        y_axis
        z_axis

    **Methods**

    .. autosummary::

        reset_origin
        reset_range
        reset_scale

.. autoattribute:: Cartesian3DFieldAxes.aspect_ratio_limit
.. autoattribute:: Cartesian3DFieldAxes.aspect_ratio_reset
.. autoattribute:: Cartesian3DFieldAxes.auto_edge_assignment
.. autoattribute:: Cartesian3DFieldAxes.axis_mode
.. autoattribute:: Cartesian3DFieldAxes.grid_area
.. autoattribute:: Cartesian3DFieldAxes.orientation_axis
.. autoattribute:: Cartesian3DFieldAxes.padding
.. autoattribute:: Cartesian3DFieldAxes.preserve_scale
.. autoattribute:: Cartesian3DFieldAxes.range_aspect_ratio_limit
.. autoattribute:: Cartesian3DFieldAxes.range_aspect_ratio_reset
.. automethod:: Cartesian3DFieldAxes.reset_origin
.. automethod:: Cartesian3DFieldAxes.reset_range
.. automethod:: Cartesian3DFieldAxes.reset_scale
.. autoattribute:: Cartesian3DFieldAxes.viewport
.. autoattribute:: Cartesian3DFieldAxes.x_axis
.. autoattribute:: Cartesian3DFieldAxes.xy_ratio
.. autoattribute:: Cartesian3DFieldAxes.xz_ratio
.. autoattribute:: Cartesian3DFieldAxes.y_axis
.. autoattribute:: Cartesian3DFieldAxes.z_axis

.. py:currentmodule:: tecplot.plot

Cartesian3DFieldAxis
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: Cartesian3DFieldAxis

    **Attributes**

    .. autosummary::
        :nosignatures:

        grid_lines
        line
        marker_grid_line
        max
        min
        minor_grid_lines
        scale_factor
        show
        tick_labels
        ticks
        title
        variable
        variable_index

    **Methods**

    .. autosummary::

        adjust_range_to_nice
        fit_range
        fit_range_to_nice

.. automethod:: Cartesian3DFieldAxis.adjust_range_to_nice
.. automethod:: Cartesian3DFieldAxis.fit_range
.. automethod:: Cartesian3DFieldAxis.fit_range_to_nice
.. autoattribute:: Cartesian3DFieldAxis.grid_lines
.. autoattribute:: Cartesian3DFieldAxis.line
.. autoattribute:: Cartesian3DFieldAxis.marker_grid_line
.. autoattribute:: Cartesian3DFieldAxis.max
.. autoattribute:: Cartesian3DFieldAxis.min
.. autoattribute:: Cartesian3DFieldAxis.minor_grid_lines
.. autoattribute:: Cartesian3DFieldAxis.scale_factor
.. autoattribute:: Cartesian3DFieldAxis.show
.. autoattribute:: Cartesian3DFieldAxis.tick_labels
.. autoattribute:: Cartesian3DFieldAxis.ticks
.. autoattribute:: Cartesian3DFieldAxis.title
.. autoattribute:: Cartesian3DFieldAxis.variable
.. autoattribute:: Cartesian3DFieldAxis.variable_index

.. _lineaxes:

.. _lineaxis:

Line Axes
---------

..  contents::
    :local:
    :depth: 1

.. py:currentmodule:: tecplot.plot

XYLineAxes
^^^^^^^^^^

.. autoclass:: XYLineAxes

    **Attributes**

    .. autosummary::
        :nosignatures:

        auto_adjust_ranges
        axis_mode
        grid_area
        precise_grid
        preserve_scale
        viewport
        xy_ratio

    **Methods**

    .. autosummary::

        x_axis
        y_axis

.. autoattribute:: XYLineAxes.auto_adjust_ranges
.. autoattribute:: XYLineAxes.axis_mode
.. autoattribute:: XYLineAxes.grid_area
.. autoattribute:: XYLineAxes.precise_grid
.. autoattribute:: XYLineAxes.preserve_scale
.. autoattribute:: XYLineAxes.viewport
.. automethod:: XYLineAxes.x_axis
.. autoattribute:: XYLineAxes.xy_ratio
.. automethod:: XYLineAxes.y_axis

.. py:currentmodule:: tecplot.plot

XYLineAxis
^^^^^^^^^^

.. autoclass:: XYLineAxis

    **Attributes**

    .. autosummary::
        :nosignatures:

        grid_lines
        line
        log_scale
        marker_grid_line
        max
        min
        minor_grid_lines
        reverse
        show
        tick_labels
        ticks
        title

    **Methods**

    .. autosummary::

        adjust_range_to_nice
        fit_range
        fit_range_to_nice

.. automethod:: XYLineAxis.adjust_range_to_nice
.. automethod:: XYLineAxis.fit_range
.. automethod:: XYLineAxis.fit_range_to_nice
.. autoattribute:: XYLineAxis.grid_lines
.. autoattribute:: XYLineAxis.line
.. autoattribute:: XYLineAxis.log_scale
.. autoattribute:: XYLineAxis.marker_grid_line
.. autoattribute:: XYLineAxis.max
.. autoattribute:: XYLineAxis.min
.. autoattribute:: XYLineAxis.minor_grid_lines
.. autoattribute:: XYLineAxis.reverse
.. autoattribute:: XYLineAxis.show
.. autoattribute:: XYLineAxis.tick_labels
.. autoattribute:: XYLineAxis.ticks
.. autoattribute:: XYLineAxis.title

.. py:currentmodule:: tecplot.plot

PolarLineAxes
^^^^^^^^^^^^^

.. autoclass:: PolarLineAxes

    **Attributes**

    .. autosummary::
        :nosignatures:

        grid_area
        precise_grid
        preserve_scale
        r_axis
        theta_axis
        viewport

.. autoattribute:: PolarLineAxes.grid_area
.. autoattribute:: PolarLineAxes.precise_grid
.. autoattribute:: PolarLineAxes.preserve_scale
.. autoattribute:: PolarLineAxes.r_axis
.. autoattribute:: PolarLineAxes.theta_axis
.. autoattribute:: PolarLineAxes.viewport

.. py:currentmodule:: tecplot.plot

RadialLineAxis
^^^^^^^^^^^^^^

.. autoclass:: RadialLineAxis

    **Attributes**

    .. autosummary::
        :nosignatures:

        clip_data
        grid_lines
        line
        log_scale
        marker_grid_line
        max
        min
        minor_grid_lines
        origin
        reverse
        show
        tick_labels
        ticks
        title

    **Methods**

    .. autosummary::

        adjust_range_to_nice
        fit_range
        fit_range_to_nice
        reset_to_entire_circle

.. automethod:: RadialLineAxis.adjust_range_to_nice
.. autoattribute:: RadialLineAxis.clip_data
.. automethod:: RadialLineAxis.fit_range
.. automethod:: RadialLineAxis.fit_range_to_nice
.. autoattribute:: RadialLineAxis.grid_lines
.. autoattribute:: RadialLineAxis.line
.. autoattribute:: RadialLineAxis.log_scale
.. autoattribute:: RadialLineAxis.marker_grid_line
.. autoattribute:: RadialLineAxis.max
.. autoattribute:: RadialLineAxis.min
.. autoattribute:: RadialLineAxis.minor_grid_lines
.. autoattribute:: RadialLineAxis.origin
.. automethod:: RadialLineAxis.reset_to_entire_circle
.. autoattribute:: RadialLineAxis.reverse
.. autoattribute:: RadialLineAxis.show
.. autoattribute:: RadialLineAxis.tick_labels
.. autoattribute:: RadialLineAxis.ticks
.. autoattribute:: RadialLineAxis.title

.. py:currentmodule:: tecplot.plot

PolarAngleLineAxis
^^^^^^^^^^^^^^^^^^

.. autoclass:: PolarAngleLineAxis

    **Attributes**

    .. autosummary::
        :nosignatures:

        clip_data
        grid_lines
        line
        marker_grid_line
        max
        min
        minor_grid_lines
        mode
        origin
        period
        reverse
        show
        tick_labels
        ticks
        title

    **Methods**

    .. autosummary::

        adjust_range_to_nice
        fit_range
        fit_range_to_nice
        reset_to_entire_circle
        set_range_to_entire_circle

.. automethod:: PolarAngleLineAxis.adjust_range_to_nice
.. autoattribute:: PolarAngleLineAxis.clip_data
.. automethod:: PolarAngleLineAxis.fit_range
.. automethod:: PolarAngleLineAxis.fit_range_to_nice
.. autoattribute:: PolarAngleLineAxis.grid_lines
.. autoattribute:: PolarAngleLineAxis.line
.. autoattribute:: PolarAngleLineAxis.marker_grid_line
.. autoattribute:: PolarAngleLineAxis.max
.. autoattribute:: PolarAngleLineAxis.min
.. autoattribute:: PolarAngleLineAxis.minor_grid_lines
.. autoattribute:: PolarAngleLineAxis.mode
.. autoattribute:: PolarAngleLineAxis.origin
.. autoattribute:: PolarAngleLineAxis.period
.. automethod:: PolarAngleLineAxis.reset_to_entire_circle
.. autoattribute:: PolarAngleLineAxis.reverse
.. automethod:: PolarAngleLineAxis.set_range_to_entire_circle
.. autoattribute:: PolarAngleLineAxis.show
.. autoattribute:: PolarAngleLineAxis.tick_labels
.. autoattribute:: PolarAngleLineAxis.ticks
.. autoattribute:: PolarAngleLineAxis.title

Sketch Axes
-----------

.. py:currentmodule:: tecplot.plot

SketchAxes
^^^^^^^^^^

.. autoclass:: SketchAxes

    **Attributes**

    .. autosummary::
        :nosignatures:

        auto_adjust_ranges
        axis_mode
        grid_area
        precise_grid
        preserve_scale
        viewport
        x_axis
        xy_ratio
        y_axis

.. autoattribute:: SketchAxes.auto_adjust_ranges
.. autoattribute:: SketchAxes.axis_mode
.. autoattribute:: SketchAxes.grid_area
.. autoattribute:: SketchAxes.precise_grid
.. autoattribute:: SketchAxes.preserve_scale
.. autoattribute:: SketchAxes.viewport
.. autoattribute:: SketchAxes.x_axis
.. autoattribute:: SketchAxes.xy_ratio
.. autoattribute:: SketchAxes.y_axis

.. py:currentmodule:: tecplot.plot

SketchAxis
^^^^^^^^^^

.. autoclass:: SketchAxis

    **Attributes**

    .. autosummary::
        :nosignatures:

        grid_lines
        line
        log_scale
        marker_grid_line
        max
        min
        minor_grid_lines
        show
        tick_labels
        ticks
        title

    **Methods**

    .. autosummary::

        adjust_range_to_nice
        fit_range
        fit_range_to_nice

.. automethod:: SketchAxis.adjust_range_to_nice
.. automethod:: SketchAxis.fit_range
.. automethod:: SketchAxis.fit_range_to_nice
.. autoattribute:: SketchAxis.grid_lines
.. autoattribute:: SketchAxis.line
.. autoattribute:: SketchAxis.log_scale
.. autoattribute:: SketchAxis.marker_grid_line
.. autoattribute:: SketchAxis.max
.. autoattribute:: SketchAxis.min
.. autoattribute:: SketchAxis.minor_grid_lines
.. autoattribute:: SketchAxis.show
.. autoattribute:: SketchAxis.tick_labels
.. autoattribute:: SketchAxis.ticks
.. autoattribute:: SketchAxis.title

Axis Elements
-------------

..  contents::
    :local:
    :depth: 2


Axis Line
^^^^^^^^^

..  contents::
    :local:
    :depth: 1

.. py:currentmodule:: tecplot.plot

AxisLine2D
++++++++++

.. autoclass:: AxisLine2D

    **Attributes**

    .. autosummary::
        :nosignatures:

        alignment
        color
        line_thickness
        offset
        opposing_axis_value
        show

.. autoattribute:: AxisLine2D.alignment
.. autoattribute:: AxisLine2D.color
.. autoattribute:: AxisLine2D.line_thickness
.. autoattribute:: AxisLine2D.offset
.. autoattribute:: AxisLine2D.opposing_axis_value
.. autoattribute:: AxisLine2D.show

.. py:currentmodule:: tecplot.plot

Cartesian2DAxisLine
+++++++++++++++++++

.. autoclass:: Cartesian2DAxisLine

    **Attributes**

    .. autosummary::
        :nosignatures:

        alignment
        color
        line_thickness
        offset
        opposing_axis_value
        position
        show

.. autoattribute:: Cartesian2DAxisLine.alignment
.. autoattribute:: Cartesian2DAxisLine.color
.. autoattribute:: Cartesian2DAxisLine.line_thickness
.. autoattribute:: Cartesian2DAxisLine.offset
.. autoattribute:: Cartesian2DAxisLine.opposing_axis_value
.. autoattribute:: Cartesian2DAxisLine.position
.. autoattribute:: Cartesian2DAxisLine.show

.. py:currentmodule:: tecplot.plot

AxisLine3D
++++++++++

.. autoclass:: AxisLine3D

    **Attributes**

    .. autosummary::
        :nosignatures:

        color
        edge_assignment
        line_thickness
        show
        show_on_opposite_edge

.. autoattribute:: AxisLine3D.color
.. autoattribute:: AxisLine3D.edge_assignment
.. autoattribute:: AxisLine3D.line_thickness
.. autoattribute:: AxisLine3D.show
.. autoattribute:: AxisLine3D.show_on_opposite_edge

.. py:currentmodule:: tecplot.plot

RadialAxisLine2D
++++++++++++++++

.. autoclass:: RadialAxisLine2D

    **Attributes**

    .. autosummary::
        :nosignatures:

        alignment
        angle
        color
        line_thickness
        offset
        opposing_axis_value
        show
        show_both_directions
        show_perpendicular

.. autoattribute:: RadialAxisLine2D.alignment
.. autoattribute:: RadialAxisLine2D.angle
.. autoattribute:: RadialAxisLine2D.color
.. autoattribute:: RadialAxisLine2D.line_thickness
.. autoattribute:: RadialAxisLine2D.offset
.. autoattribute:: RadialAxisLine2D.opposing_axis_value
.. autoattribute:: RadialAxisLine2D.show
.. autoattribute:: RadialAxisLine2D.show_both_directions
.. autoattribute:: RadialAxisLine2D.show_perpendicular

Ticks and Labels
^^^^^^^^^^^^^^^^

..  contents::
    :local:
    :depth: 1

.. py:currentmodule:: tecplot.plot

Ticks2D
+++++++

.. autoclass:: Ticks2D

    **Attributes**

    .. autosummary::
        :nosignatures:

        auto_spacing
        direction
        length
        line_thickness
        minor_length
        minor_line_thickness
        minor_num_ticks
        show
        show_on_border_max
        show_on_border_min
        spacing
        spacing_anchor

.. autoattribute:: Ticks2D.auto_spacing
.. autoattribute:: Ticks2D.direction
.. autoattribute:: Ticks2D.length
.. autoattribute:: Ticks2D.line_thickness
.. autoattribute:: Ticks2D.minor_length
.. autoattribute:: Ticks2D.minor_line_thickness
.. autoattribute:: Ticks2D.minor_num_ticks
.. autoattribute:: Ticks2D.show
.. autoattribute:: Ticks2D.show_on_border_max
.. autoattribute:: Ticks2D.show_on_border_min
.. autoattribute:: Ticks2D.spacing
.. autoattribute:: Ticks2D.spacing_anchor

.. py:currentmodule:: tecplot.plot

Ticks3D
+++++++

.. autoclass:: Ticks3D

    **Attributes**

    .. autosummary::
        :nosignatures:

        auto_spacing
        direction
        length
        line_thickness
        minor_length
        minor_line_thickness
        minor_num_ticks
        show
        show_on_opposite_edge
        spacing
        spacing_anchor

.. autoattribute:: Ticks3D.auto_spacing
.. autoattribute:: Ticks3D.direction
.. autoattribute:: Ticks3D.length
.. autoattribute:: Ticks3D.line_thickness
.. autoattribute:: Ticks3D.minor_length
.. autoattribute:: Ticks3D.minor_line_thickness
.. autoattribute:: Ticks3D.minor_num_ticks
.. autoattribute:: Ticks3D.show
.. autoattribute:: Ticks3D.show_on_opposite_edge
.. autoattribute:: Ticks3D.spacing
.. autoattribute:: Ticks3D.spacing_anchor

.. py:currentmodule:: tecplot.plot

RadialTicks
+++++++++++

.. autoclass:: RadialTicks

    **Attributes**

    .. autosummary::
        :nosignatures:

        auto_spacing
        direction
        length
        line_thickness
        minor_length
        minor_line_thickness
        minor_num_ticks
        show
        show_on_all_radial_axes
        show_on_border_max
        show_on_border_min
        spacing
        spacing_anchor

.. autoattribute:: RadialTicks.auto_spacing
.. autoattribute:: RadialTicks.direction
.. autoattribute:: RadialTicks.length
.. autoattribute:: RadialTicks.line_thickness
.. autoattribute:: RadialTicks.minor_length
.. autoattribute:: RadialTicks.minor_line_thickness
.. autoattribute:: RadialTicks.minor_num_ticks
.. autoattribute:: RadialTicks.show
.. autoattribute:: RadialTicks.show_on_all_radial_axes
.. autoattribute:: RadialTicks.show_on_border_max
.. autoattribute:: RadialTicks.show_on_border_min
.. autoattribute:: RadialTicks.spacing
.. autoattribute:: RadialTicks.spacing_anchor

.. py:currentmodule:: tecplot.plot

TickLabels2D
++++++++++++

.. autoclass:: TickLabels2D

    **Attributes**

    .. autosummary::
        :nosignatures:

        alignment
        angle
        color
        font
        format
        offset
        show
        show_at_axis_intersection
        show_on_border_max
        show_on_border_min
        step
        transparent_background

.. autoattribute:: TickLabels2D.alignment
.. autoattribute:: TickLabels2D.angle
.. autoattribute:: TickLabels2D.color
.. autoattribute:: TickLabels2D.font
.. autoattribute:: TickLabels2D.format
.. autoattribute:: TickLabels2D.offset
.. autoattribute:: TickLabels2D.show
.. autoattribute:: TickLabels2D.show_at_axis_intersection
.. autoattribute:: TickLabels2D.show_on_border_max
.. autoattribute:: TickLabels2D.show_on_border_min
.. autoattribute:: TickLabels2D.step
.. autoattribute:: TickLabels2D.transparent_background

.. py:currentmodule:: tecplot.plot

TickLabels3D
++++++++++++

.. autoclass:: TickLabels3D

    **Attributes**

    .. autosummary::
        :nosignatures:

        alignment
        angle
        color
        font
        format
        offset
        show
        show_on_opposite_edge
        step

.. autoattribute:: TickLabels3D.alignment
.. autoattribute:: TickLabels3D.angle
.. autoattribute:: TickLabels3D.color
.. autoattribute:: TickLabels3D.font
.. autoattribute:: TickLabels3D.format
.. autoattribute:: TickLabels3D.offset
.. autoattribute:: TickLabels3D.show
.. autoattribute:: TickLabels3D.show_on_opposite_edge
.. autoattribute:: TickLabels3D.step

.. py:currentmodule:: tecplot.plot

RadialTickLabels
++++++++++++++++

.. autoclass:: RadialTickLabels

    **Attributes**

    .. autosummary::
        :nosignatures:

        alignment
        angle
        color
        font
        format
        offset
        show
        show_at_axis_intersection
        show_on_all_radial_axes
        show_on_border_max
        show_on_border_min
        step
        transparent_background

.. autoattribute:: RadialTickLabels.alignment
.. autoattribute:: RadialTickLabels.angle
.. autoattribute:: RadialTickLabels.color
.. autoattribute:: RadialTickLabels.font
.. autoattribute:: RadialTickLabels.format
.. autoattribute:: RadialTickLabels.offset
.. autoattribute:: RadialTickLabels.show
.. autoattribute:: RadialTickLabels.show_at_axis_intersection
.. autoattribute:: RadialTickLabels.show_on_all_radial_axes
.. autoattribute:: RadialTickLabels.show_on_border_max
.. autoattribute:: RadialTickLabels.show_on_border_min
.. autoattribute:: RadialTickLabels.step
.. autoattribute:: RadialTickLabels.transparent_background

Axis Title
^^^^^^^^^^

..  contents::
    :local:
    :depth: 1

.. py:currentmodule:: tecplot.plot

Axis2DTitle
+++++++++++

.. autoclass:: Axis2DTitle

    **Attributes**

    .. autosummary::
        :nosignatures:

        color
        font
        offset
        position
        show
        show_on_border_max
        show_on_border_min
        text

.. autoattribute:: Axis2DTitle.color
.. autoattribute:: Axis2DTitle.font
.. autoattribute:: Axis2DTitle.offset
.. autoattribute:: Axis2DTitle.position
.. autoattribute:: Axis2DTitle.show
.. autoattribute:: Axis2DTitle.show_on_border_max
.. autoattribute:: Axis2DTitle.show_on_border_min
.. autoattribute:: Axis2DTitle.text

.. py:currentmodule:: tecplot.plot

DataAxis2DTitle
+++++++++++++++

.. autoclass:: DataAxis2DTitle

    **Attributes**

    .. autosummary::
        :nosignatures:

        color
        font
        offset
        position
        show
        show_on_border_max
        show_on_border_min
        text
        title_mode

.. autoattribute:: DataAxis2DTitle.color
.. autoattribute:: DataAxis2DTitle.font
.. autoattribute:: DataAxis2DTitle.offset
.. autoattribute:: DataAxis2DTitle.position
.. autoattribute:: DataAxis2DTitle.show
.. autoattribute:: DataAxis2DTitle.show_on_border_max
.. autoattribute:: DataAxis2DTitle.show_on_border_min
.. autoattribute:: DataAxis2DTitle.text
.. autoattribute:: DataAxis2DTitle.title_mode

.. py:currentmodule:: tecplot.plot

DataAxis3DTitle
+++++++++++++++

.. autoclass:: DataAxis3DTitle

    **Attributes**

    .. autosummary::
        :nosignatures:

        color
        font
        offset
        position
        show
        show_on_opposite_edge
        text
        title_mode

.. autoattribute:: DataAxis3DTitle.color
.. autoattribute:: DataAxis3DTitle.font
.. autoattribute:: DataAxis3DTitle.offset
.. autoattribute:: DataAxis3DTitle.position
.. autoattribute:: DataAxis3DTitle.show
.. autoattribute:: DataAxis3DTitle.show_on_opposite_edge
.. autoattribute:: DataAxis3DTitle.text
.. autoattribute:: DataAxis3DTitle.title_mode

.. py:currentmodule:: tecplot.plot

RadialAxisTitle
+++++++++++++++

.. autoclass:: RadialAxisTitle

    **Attributes**

    .. autosummary::
        :nosignatures:

        color
        font
        offset
        position
        show
        show_on_all_radial_axes
        show_on_border_max
        show_on_border_min
        text
        title_mode

.. autoattribute:: RadialAxisTitle.color
.. autoattribute:: RadialAxisTitle.font
.. autoattribute:: RadialAxisTitle.offset
.. autoattribute:: RadialAxisTitle.position
.. autoattribute:: RadialAxisTitle.show
.. autoattribute:: RadialAxisTitle.show_on_all_radial_axes
.. autoattribute:: RadialAxisTitle.show_on_border_max
.. autoattribute:: RadialAxisTitle.show_on_border_min
.. autoattribute:: RadialAxisTitle.text
.. autoattribute:: RadialAxisTitle.title_mode

Grid Area
^^^^^^^^^

..  contents::
    :local:
    :depth: 1

.. py:currentmodule:: tecplot.plot

GridArea
++++++++

.. autoclass:: GridArea

    **Attributes**

    .. autosummary::
        :nosignatures:

        fill_color
        filled
        show_border

.. autoattribute:: GridArea.fill_color
.. autoattribute:: GridArea.filled
.. autoattribute:: GridArea.show_border

.. py:currentmodule:: tecplot.plot

Cartesian2DGridArea
+++++++++++++++++++

.. autoclass:: Cartesian2DGridArea

    **Attributes**

    .. autosummary::
        :nosignatures:

        border_color
        border_thickness
        fill_color
        filled
        show_border

.. autoattribute:: Cartesian2DGridArea.border_color
.. autoattribute:: Cartesian2DGridArea.border_thickness
.. autoattribute:: Cartesian2DGridArea.fill_color
.. autoattribute:: Cartesian2DGridArea.filled
.. autoattribute:: Cartesian2DGridArea.show_border

.. py:currentmodule:: tecplot.plot

Cartesian3DGridArea
+++++++++++++++++++

.. autoclass:: Cartesian3DGridArea

    **Attributes**

    .. autosummary::
        :nosignatures:

        fill_color
        filled
        show_border
        use_lighting_effect

.. autoattribute:: Cartesian3DGridArea.fill_color
.. autoattribute:: Cartesian3DGridArea.filled
.. autoattribute:: Cartesian3DGridArea.show_border
.. autoattribute:: Cartesian3DGridArea.use_lighting_effect

.. py:currentmodule:: tecplot.plot

PreciseGrid
+++++++++++

.. autoclass:: PreciseGrid

    **Attributes**

    .. autosummary::
        :nosignatures:

        color
        show
        size

.. autoattribute:: PreciseGrid.color
.. autoattribute:: PreciseGrid.show
.. autoattribute:: PreciseGrid.size

.. py:currentmodule:: tecplot.plot

GridLines
+++++++++

.. autoclass:: GridLines

    **Attributes**

    .. autosummary::
        :nosignatures:

        color
        line_pattern
        line_thickness
        pattern_length
        show

.. autoattribute:: GridLines.color
.. autoattribute:: GridLines.line_pattern
.. autoattribute:: GridLines.line_thickness
.. autoattribute:: GridLines.pattern_length
.. autoattribute:: GridLines.show

.. py:currentmodule:: tecplot.plot

GridLines2D
+++++++++++

.. autoclass:: GridLines2D

    **Attributes**

    .. autosummary::
        :nosignatures:

        color
        draw_last
        line_pattern
        line_thickness
        pattern_length
        show

.. autoattribute:: GridLines2D.color
.. autoattribute:: GridLines2D.draw_last
.. autoattribute:: GridLines2D.line_pattern
.. autoattribute:: GridLines2D.line_thickness
.. autoattribute:: GridLines2D.pattern_length
.. autoattribute:: GridLines2D.show

.. py:currentmodule:: tecplot.plot

MinorGridLines
++++++++++++++

.. autoclass:: MinorGridLines

    **Attributes**

    .. autosummary::
        :nosignatures:

        color
        line_pattern
        line_thickness
        pattern_length
        show

.. autoattribute:: MinorGridLines.color
.. autoattribute:: MinorGridLines.line_pattern
.. autoattribute:: MinorGridLines.line_thickness
.. autoattribute:: MinorGridLines.pattern_length
.. autoattribute:: MinorGridLines.show

.. py:currentmodule:: tecplot.plot

MinorGridLines2D
++++++++++++++++

.. autoclass:: MinorGridLines2D

    **Attributes**

    .. autosummary::
        :nosignatures:

        color
        draw_last
        line_pattern
        line_thickness
        pattern_length
        show

.. autoattribute:: MinorGridLines2D.color
.. autoattribute:: MinorGridLines2D.draw_last
.. autoattribute:: MinorGridLines2D.line_pattern
.. autoattribute:: MinorGridLines2D.line_thickness
.. autoattribute:: MinorGridLines2D.pattern_length
.. autoattribute:: MinorGridLines2D.show

.. py:currentmodule:: tecplot.plot

PolarAngleGridLines
+++++++++++++++++++

.. autoclass:: PolarAngleGridLines

    **Attributes**

    .. autosummary::
        :nosignatures:

        color
        draw_last
        line_pattern
        line_thickness
        pattern_length
        radial_cutoff
        show

.. autoattribute:: PolarAngleGridLines.color
.. autoattribute:: PolarAngleGridLines.draw_last
.. autoattribute:: PolarAngleGridLines.line_pattern
.. autoattribute:: PolarAngleGridLines.line_thickness
.. autoattribute:: PolarAngleGridLines.pattern_length
.. autoattribute:: PolarAngleGridLines.radial_cutoff
.. autoattribute:: PolarAngleGridLines.show

.. py:currentmodule:: tecplot.plot

PolarAngleMinorGridLines
++++++++++++++++++++++++

.. autoclass:: PolarAngleMinorGridLines

    **Attributes**

    .. autosummary::
        :nosignatures:

        color
        draw_last
        line_pattern
        line_thickness
        pattern_length
        radial_cutoff
        show

.. autoattribute:: PolarAngleMinorGridLines.color
.. autoattribute:: PolarAngleMinorGridLines.draw_last
.. autoattribute:: PolarAngleMinorGridLines.line_pattern
.. autoattribute:: PolarAngleMinorGridLines.line_thickness
.. autoattribute:: PolarAngleMinorGridLines.pattern_length
.. autoattribute:: PolarAngleMinorGridLines.radial_cutoff
.. autoattribute:: PolarAngleMinorGridLines.show

.. py:currentmodule:: tecplot.plot

MarkerGridLine
++++++++++++++

.. autoclass:: MarkerGridLine

    **Attributes**

    .. autosummary::
        :nosignatures:

        color
        line_pattern
        line_thickness
        pattern_length
        position
        position_by
        show

.. autoattribute:: MarkerGridLine.color
.. autoattribute:: MarkerGridLine.line_pattern
.. autoattribute:: MarkerGridLine.line_thickness
.. autoattribute:: MarkerGridLine.pattern_length
.. autoattribute:: MarkerGridLine.position
.. autoattribute:: MarkerGridLine.position_by
.. autoattribute:: MarkerGridLine.show

.. py:currentmodule:: tecplot.plot

MarkerGridLine2D
++++++++++++++++

.. autoclass:: MarkerGridLine2D

    **Attributes**

    .. autosummary::
        :nosignatures:

        color
        draw_last
        line_pattern
        line_thickness
        pattern_length
        position
        position_by
        show

.. autoattribute:: MarkerGridLine2D.color
.. autoattribute:: MarkerGridLine2D.draw_last
.. autoattribute:: MarkerGridLine2D.line_pattern
.. autoattribute:: MarkerGridLine2D.line_thickness
.. autoattribute:: MarkerGridLine2D.pattern_length
.. autoattribute:: MarkerGridLine2D.position
.. autoattribute:: MarkerGridLine2D.position_by
.. autoattribute:: MarkerGridLine2D.show

.. py:currentmodule:: tecplot.plot

PolarAngleMarkerGridLine
++++++++++++++++++++++++

.. autoclass:: PolarAngleMarkerGridLine

    **Attributes**

    .. autosummary::
        :nosignatures:

        color
        draw_last
        line_pattern
        line_thickness
        pattern_length
        position
        position_by
        radial_cutoff
        show

.. autoattribute:: PolarAngleMarkerGridLine.color
.. autoattribute:: PolarAngleMarkerGridLine.draw_last
.. autoattribute:: PolarAngleMarkerGridLine.line_pattern
.. autoattribute:: PolarAngleMarkerGridLine.line_thickness
.. autoattribute:: PolarAngleMarkerGridLine.pattern_length
.. autoattribute:: PolarAngleMarkerGridLine.position
.. autoattribute:: PolarAngleMarkerGridLine.position_by
.. autoattribute:: PolarAngleMarkerGridLine.radial_cutoff
.. autoattribute:: PolarAngleMarkerGridLine.show

.. py:currentmodule:: tecplot.plot

OrientationAxis
^^^^^^^^^^^^^^^

.. autoclass:: OrientationAxis

    **Attributes**

    .. autosummary::
        :nosignatures:

        color
        line_thickness
        position
        show
        show_variable_name
        size

.. autoattribute:: OrientationAxis.color
.. autoattribute:: OrientationAxis.line_thickness
.. autoattribute:: OrientationAxis.position
.. autoattribute:: OrientationAxis.show
.. autoattribute:: OrientationAxis.show_variable_name
.. autoattribute:: OrientationAxis.size
