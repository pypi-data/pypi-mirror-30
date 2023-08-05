.. _plot:

Plot
====

..  contents::
    :local:
    :depth: 2

tecplot.plot
------------

.. automodule:: tecplot.plot


Plots
-----

..  contents::
    :local:
    :depth: 1

.. py:currentmodule:: tecplot.plot

Cartesian2DFieldPlot
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: Cartesian2DFieldPlot

    **Attributes**

    .. autosummary::
        :nosignatures:

        active_fieldmap_indices
        active_fieldmaps
        axes
        draw_order
        num_fieldmaps
        num_solution_times
        scatter
        show_contour
        show_edge
        show_isosurfaces
        show_mesh
        show_scatter
        show_shade
        show_slices
        show_streamtraces
        show_vector
        solution_time
        solution_times
        solution_timestep
        streamtraces
        vector
        view

    **Methods**

    .. autosummary::

        activate
        activated
        contour
        fieldmap
        fieldmap_index
        fieldmaps
        isosurface
        slice

.. automethod:: Cartesian2DFieldPlot.activate
.. automethod:: Cartesian2DFieldPlot.activated
.. autoattribute:: Cartesian2DFieldPlot.active_fieldmap_indices
.. autoattribute:: Cartesian2DFieldPlot.active_fieldmaps
.. autoattribute:: Cartesian2DFieldPlot.axes
.. automethod:: Cartesian2DFieldPlot.contour
.. autoattribute:: Cartesian2DFieldPlot.draw_order
.. automethod:: Cartesian2DFieldPlot.fieldmap
.. automethod:: Cartesian2DFieldPlot.fieldmap_index
.. automethod:: Cartesian2DFieldPlot.fieldmaps
.. automethod:: Cartesian2DFieldPlot.isosurface
.. autoattribute:: Cartesian2DFieldPlot.num_fieldmaps
.. autoattribute:: Cartesian2DFieldPlot.num_solution_times
.. autoattribute:: Cartesian2DFieldPlot.scatter
.. autoattribute:: Cartesian2DFieldPlot.show_contour
.. autoattribute:: Cartesian2DFieldPlot.show_edge
.. autoattribute:: Cartesian2DFieldPlot.show_isosurfaces
.. autoattribute:: Cartesian2DFieldPlot.show_mesh
.. autoattribute:: Cartesian2DFieldPlot.show_scatter
.. autoattribute:: Cartesian2DFieldPlot.show_shade
.. autoattribute:: Cartesian2DFieldPlot.show_slices
.. autoattribute:: Cartesian2DFieldPlot.show_streamtraces
.. autoattribute:: Cartesian2DFieldPlot.show_vector
.. automethod:: Cartesian2DFieldPlot.slice
.. autoattribute:: Cartesian2DFieldPlot.solution_time
.. autoattribute:: Cartesian2DFieldPlot.solution_times
.. autoattribute:: Cartesian2DFieldPlot.solution_timestep
.. autoattribute:: Cartesian2DFieldPlot.streamtraces
.. autoattribute:: Cartesian2DFieldPlot.vector
.. autoattribute:: Cartesian2DFieldPlot.view

.. py:currentmodule:: tecplot.plot

Cartesian3DFieldPlot
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: Cartesian3DFieldPlot

    **Attributes**

    .. autosummary::
        :nosignatures:

        active_fieldmap_indices
        active_fieldmaps
        axes
        num_fieldmaps
        num_solution_times
        scatter
        show_contour
        show_edge
        show_isosurfaces
        show_mesh
        show_scatter
        show_shade
        show_slices
        show_streamtraces
        show_vector
        solution_time
        solution_times
        solution_timestep
        streamtraces
        use_lighting_effect
        use_translucency
        vector
        view

    **Methods**

    .. autosummary::

        activate
        activated
        contour
        fieldmap
        fieldmap_index
        fieldmaps
        isosurface
        slice

.. automethod:: Cartesian3DFieldPlot.activate
.. automethod:: Cartesian3DFieldPlot.activated
.. autoattribute:: Cartesian3DFieldPlot.active_fieldmap_indices
.. autoattribute:: Cartesian3DFieldPlot.active_fieldmaps
.. autoattribute:: Cartesian3DFieldPlot.axes
.. automethod:: Cartesian3DFieldPlot.contour
.. automethod:: Cartesian3DFieldPlot.fieldmap
.. automethod:: Cartesian3DFieldPlot.fieldmap_index
.. automethod:: Cartesian3DFieldPlot.fieldmaps
.. automethod:: Cartesian3DFieldPlot.isosurface
.. autoattribute:: Cartesian3DFieldPlot.num_fieldmaps
.. autoattribute:: Cartesian3DFieldPlot.num_solution_times
.. autoattribute:: Cartesian3DFieldPlot.scatter
.. autoattribute:: Cartesian3DFieldPlot.show_contour
.. autoattribute:: Cartesian3DFieldPlot.show_edge
.. autoattribute:: Cartesian3DFieldPlot.show_isosurfaces
.. autoattribute:: Cartesian3DFieldPlot.show_mesh
.. autoattribute:: Cartesian3DFieldPlot.show_scatter
.. autoattribute:: Cartesian3DFieldPlot.show_shade
.. autoattribute:: Cartesian3DFieldPlot.show_slices
.. autoattribute:: Cartesian3DFieldPlot.show_streamtraces
.. autoattribute:: Cartesian3DFieldPlot.show_vector
.. automethod:: Cartesian3DFieldPlot.slice
.. autoattribute:: Cartesian3DFieldPlot.solution_time
.. autoattribute:: Cartesian3DFieldPlot.solution_times
.. autoattribute:: Cartesian3DFieldPlot.solution_timestep
.. autoattribute:: Cartesian3DFieldPlot.streamtraces
.. autoattribute:: Cartesian3DFieldPlot.use_lighting_effect
.. autoattribute:: Cartesian3DFieldPlot.use_translucency
.. autoattribute:: Cartesian3DFieldPlot.vector
.. autoattribute:: Cartesian3DFieldPlot.view

.. py:currentmodule:: tecplot.plot

PolarLinePlot
^^^^^^^^^^^^^

.. autoclass:: PolarLinePlot

    **Attributes**

    .. autosummary::
        :nosignatures:

        active_linemap_indices
        active_linemaps
        axes
        legend
        num_linemaps
        show_lines
        show_symbols
        view

    **Methods**

    .. autosummary::

        activate
        activated
        add_linemap
        delete_linemaps
        linemap
        linemaps

.. automethod:: PolarLinePlot.activate
.. automethod:: PolarLinePlot.activated
.. autoattribute:: PolarLinePlot.active_linemap_indices
.. autoattribute:: PolarLinePlot.active_linemaps
.. automethod:: PolarLinePlot.add_linemap
.. autoattribute:: PolarLinePlot.axes
.. automethod:: PolarLinePlot.delete_linemaps
.. autoattribute:: PolarLinePlot.legend
.. automethod:: PolarLinePlot.linemap
.. automethod:: PolarLinePlot.linemaps
.. autoattribute:: PolarLinePlot.num_linemaps
.. autoattribute:: PolarLinePlot.show_lines
.. autoattribute:: PolarLinePlot.show_symbols
.. autoattribute:: PolarLinePlot.view

.. py:currentmodule:: tecplot.plot

XYLinePlot
^^^^^^^^^^

.. autoclass:: XYLinePlot

    **Attributes**

    .. autosummary::
        :nosignatures:

        active_linemap_indices
        active_linemaps
        axes
        legend
        num_linemaps
        show_bars
        show_error_bars
        show_lines
        show_symbols
        view

    **Methods**

    .. autosummary::

        activate
        activated
        add_linemap
        delete_linemaps
        linemap
        linemaps

.. automethod:: XYLinePlot.activate
.. automethod:: XYLinePlot.activated
.. autoattribute:: XYLinePlot.active_linemap_indices
.. autoattribute:: XYLinePlot.active_linemaps
.. automethod:: XYLinePlot.add_linemap
.. autoattribute:: XYLinePlot.axes
.. automethod:: XYLinePlot.delete_linemaps
.. autoattribute:: XYLinePlot.legend
.. automethod:: XYLinePlot.linemap
.. automethod:: XYLinePlot.linemaps
.. autoattribute:: XYLinePlot.num_linemaps
.. autoattribute:: XYLinePlot.show_bars
.. autoattribute:: XYLinePlot.show_error_bars
.. autoattribute:: XYLinePlot.show_lines
.. autoattribute:: XYLinePlot.show_symbols
.. autoattribute:: XYLinePlot.view

.. py:currentmodule:: tecplot.plot

SketchPlot
^^^^^^^^^^

.. autoclass:: SketchPlot

    **Attributes**

    .. autosummary::
        :nosignatures:

        axes

    **Methods**

    .. autosummary::

        activate
        activated

.. automethod:: SketchPlot.activate
.. automethod:: SketchPlot.activated
.. autoattribute:: SketchPlot.axes

.. _fieldmap:

Fieldmaps
---------

..  contents::
    :local:
    :depth: 1

.. py:currentmodule:: tecplot.plot

Cartesian2DFieldmap
^^^^^^^^^^^^^^^^^^^

.. autoclass:: Cartesian2DFieldmap

    **Attributes**

    .. autosummary::
        :nosignatures:

        contour
        edge
        effects
        group
        mesh
        points
        scatter
        shade
        show
        show_iso_surfaces
        show_slices
        show_streamtraces
        surfaces
        vector
        zones

.. autoattribute:: Cartesian2DFieldmap.contour
.. autoattribute:: Cartesian2DFieldmap.edge
.. autoattribute:: Cartesian2DFieldmap.effects
.. autoattribute:: Cartesian2DFieldmap.group
.. autoattribute:: Cartesian2DFieldmap.mesh
.. autoattribute:: Cartesian2DFieldmap.points
.. autoattribute:: Cartesian2DFieldmap.scatter
.. autoattribute:: Cartesian2DFieldmap.shade
.. autoattribute:: Cartesian2DFieldmap.show
.. autoattribute:: Cartesian2DFieldmap.show_iso_surfaces
.. autoattribute:: Cartesian2DFieldmap.show_slices
.. autoattribute:: Cartesian2DFieldmap.show_streamtraces
.. autoattribute:: Cartesian2DFieldmap.surfaces
.. autoattribute:: Cartesian2DFieldmap.vector
.. autoattribute:: Cartesian2DFieldmap.zones

.. py:currentmodule:: tecplot.plot

Cartesian3DFieldmap
^^^^^^^^^^^^^^^^^^^

.. autoclass:: Cartesian3DFieldmap

    **Attributes**

    .. autosummary::
        :nosignatures:

        contour
        edge
        effects
        group
        mesh
        points
        scatter
        shade
        show
        show_iso_surfaces
        show_slices
        show_streamtraces
        surfaces
        vector
        zones

.. autoattribute:: Cartesian3DFieldmap.contour
.. autoattribute:: Cartesian3DFieldmap.edge
.. autoattribute:: Cartesian3DFieldmap.effects
.. autoattribute:: Cartesian3DFieldmap.group
.. autoattribute:: Cartesian3DFieldmap.mesh
.. autoattribute:: Cartesian3DFieldmap.points
.. autoattribute:: Cartesian3DFieldmap.scatter
.. autoattribute:: Cartesian3DFieldmap.shade
.. autoattribute:: Cartesian3DFieldmap.show
.. autoattribute:: Cartesian3DFieldmap.show_iso_surfaces
.. autoattribute:: Cartesian3DFieldmap.show_slices
.. autoattribute:: Cartesian3DFieldmap.show_streamtraces
.. autoattribute:: Cartesian3DFieldmap.surfaces
.. autoattribute:: Cartesian3DFieldmap.vector
.. autoattribute:: Cartesian3DFieldmap.zones

.. py:currentmodule:: tecplot.plot

FieldmapContour
^^^^^^^^^^^^^^^

.. autoclass:: FieldmapContour

    **Attributes**

    .. autosummary::
        :nosignatures:

        contour_type
        flood_contour_group
        flood_contour_group_index
        line_color
        line_group
        line_group_index
        line_pattern
        line_thickness
        pattern_length
        show
        use_lighting_effect

.. autoattribute:: FieldmapContour.contour_type
.. autoattribute:: FieldmapContour.flood_contour_group
.. autoattribute:: FieldmapContour.flood_contour_group_index
.. autoattribute:: FieldmapContour.line_color
.. autoattribute:: FieldmapContour.line_group
.. autoattribute:: FieldmapContour.line_group_index
.. autoattribute:: FieldmapContour.line_pattern
.. autoattribute:: FieldmapContour.line_thickness
.. autoattribute:: FieldmapContour.pattern_length
.. autoattribute:: FieldmapContour.show
.. autoattribute:: FieldmapContour.use_lighting_effect

.. py:currentmodule:: tecplot.plot

FieldmapEdge
^^^^^^^^^^^^

.. autoclass:: FieldmapEdge

    **Attributes**

    .. autosummary::
        :nosignatures:

        color
        edge_type
        i_border
        j_border
        k_border
        line_thickness
        show

.. autoattribute:: FieldmapEdge.color
.. autoattribute:: FieldmapEdge.edge_type
.. autoattribute:: FieldmapEdge.i_border
.. autoattribute:: FieldmapEdge.j_border
.. autoattribute:: FieldmapEdge.k_border
.. autoattribute:: FieldmapEdge.line_thickness
.. autoattribute:: FieldmapEdge.show

.. py:currentmodule:: tecplot.plot

FieldmapEffects
^^^^^^^^^^^^^^^

.. autoclass:: FieldmapEffects

    **Attributes**

    .. autosummary::
        :nosignatures:

        clip_planes
        value_blanking

.. autoattribute:: FieldmapEffects.clip_planes
.. autoattribute:: FieldmapEffects.value_blanking

.. py:currentmodule:: tecplot.plot

FieldmapEffects3D
^^^^^^^^^^^^^^^^^

.. autoclass:: FieldmapEffects3D

    **Attributes**

    .. autosummary::
        :nosignatures:

        clip_planes
        lighting_effect
        surface_translucency
        use_translucency
        value_blanking

.. autoattribute:: FieldmapEffects3D.clip_planes
.. autoattribute:: FieldmapEffects3D.lighting_effect
.. autoattribute:: FieldmapEffects3D.surface_translucency
.. autoattribute:: FieldmapEffects3D.use_translucency
.. autoattribute:: FieldmapEffects3D.value_blanking

.. py:currentmodule:: tecplot.plot

FieldmapMesh
^^^^^^^^^^^^

.. autoclass:: FieldmapMesh

    **Attributes**

    .. autosummary::
        :nosignatures:

        color
        line_pattern
        line_thickness
        mesh_type
        pattern_length
        show

.. autoattribute:: FieldmapMesh.color
.. autoattribute:: FieldmapMesh.line_pattern
.. autoattribute:: FieldmapMesh.line_thickness
.. autoattribute:: FieldmapMesh.mesh_type
.. autoattribute:: FieldmapMesh.pattern_length
.. autoattribute:: FieldmapMesh.show

.. py:currentmodule:: tecplot.plot

FieldmapPoints
^^^^^^^^^^^^^^

.. autoclass:: FieldmapPoints

    **Attributes**

    .. autosummary::
        :nosignatures:

        points_to_plot
        step

.. autoattribute:: FieldmapPoints.points_to_plot
.. autoattribute:: FieldmapPoints.step

.. py:currentmodule:: tecplot.plot

FieldmapScatter
^^^^^^^^^^^^^^^

.. autoclass:: FieldmapScatter

    **Attributes**

    .. autosummary::
        :nosignatures:

        color
        fill_color
        fill_mode
        line_thickness
        show
        size
        size_by_variable
        symbol_type

    **Methods**

    .. autosummary::

        symbol

.. autoattribute:: FieldmapScatter.color
.. autoattribute:: FieldmapScatter.fill_color
.. autoattribute:: FieldmapScatter.fill_mode
.. autoattribute:: FieldmapScatter.line_thickness
.. autoattribute:: FieldmapScatter.show
.. autoattribute:: FieldmapScatter.size
.. autoattribute:: FieldmapScatter.size_by_variable
.. automethod:: FieldmapScatter.symbol
.. autoattribute:: FieldmapScatter.symbol_type

.. py:currentmodule:: tecplot.plot

GeometryScatterSymbol
^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: GeometryScatterSymbol

    **Attributes**

    .. autosummary::
        :nosignatures:

        shape

.. autoattribute:: GeometryScatterSymbol.shape

.. py:currentmodule:: tecplot.plot

TextScatterSymbol
^^^^^^^^^^^^^^^^^

.. autoclass:: TextScatterSymbol

    **Attributes**

    .. autosummary::
        :nosignatures:

        font_override
        text
        use_base_font

.. autoattribute:: TextScatterSymbol.font_override
.. autoattribute:: TextScatterSymbol.text
.. autoattribute:: TextScatterSymbol.use_base_font

.. py:currentmodule:: tecplot.plot

FieldmapShade
^^^^^^^^^^^^^

.. autoclass:: FieldmapShade

    **Attributes**

    .. autosummary::
        :nosignatures:

        color
        show

.. autoattribute:: FieldmapShade.color
.. autoattribute:: FieldmapShade.show

.. py:currentmodule:: tecplot.plot

FieldmapShade3D
^^^^^^^^^^^^^^^

.. autoclass:: FieldmapShade3D

    **Attributes**

    .. autosummary::
        :nosignatures:

        color
        show
        use_lighting_effect

.. autoattribute:: FieldmapShade3D.color
.. autoattribute:: FieldmapShade3D.show
.. autoattribute:: FieldmapShade3D.use_lighting_effect

.. py:currentmodule:: tecplot.plot

FieldmapSurfaces
^^^^^^^^^^^^^^^^

.. autoclass:: FieldmapSurfaces

    **Attributes**

    .. autosummary::
        :nosignatures:

        i_range
        j_range
        k_range
        surfaces_to_plot

.. autoattribute:: FieldmapSurfaces.i_range
.. autoattribute:: FieldmapSurfaces.j_range
.. autoattribute:: FieldmapSurfaces.k_range
.. autoattribute:: FieldmapSurfaces.surfaces_to_plot

.. py:currentmodule:: tecplot.plot

FieldmapVector
^^^^^^^^^^^^^^

.. autoclass:: FieldmapVector

    **Attributes**

    .. autosummary::
        :nosignatures:

        arrowhead_style
        color
        line_pattern
        line_thickness
        pattern_length
        show
        tangent_only
        vector_type

.. autoattribute:: FieldmapVector.arrowhead_style
.. autoattribute:: FieldmapVector.color
.. autoattribute:: FieldmapVector.line_pattern
.. autoattribute:: FieldmapVector.line_thickness
.. autoattribute:: FieldmapVector.pattern_length
.. autoattribute:: FieldmapVector.show
.. autoattribute:: FieldmapVector.tangent_only
.. autoattribute:: FieldmapVector.vector_type

.. _linemap:

Linemaps
--------

..  contents::
    :local:
    :depth: 1

.. py:currentmodule:: tecplot.plot

PolarLinemap
^^^^^^^^^^^^

.. autoclass:: PolarLinemap

    **Attributes**

    .. autosummary::
        :nosignatures:

        aux_data
        curve
        function_dependency
        index
        indices
        line
        name
        r_axis
        r_variable
        r_variable_index
        show
        show_in_legend
        sort_mode
        sort_variable
        sort_variable_index
        symbols
        theta_axis
        theta_variable
        theta_variable_index
        zone
        zone_index

.. autoattribute:: PolarLinemap.aux_data
.. autoattribute:: PolarLinemap.curve
.. autoattribute:: PolarLinemap.function_dependency
.. autoattribute:: PolarLinemap.index
.. autoattribute:: PolarLinemap.indices
.. autoattribute:: PolarLinemap.line
.. autoattribute:: PolarLinemap.name
.. autoattribute:: PolarLinemap.r_axis
.. autoattribute:: PolarLinemap.r_variable
.. autoattribute:: PolarLinemap.r_variable_index
.. autoattribute:: PolarLinemap.show
.. autoattribute:: PolarLinemap.show_in_legend
.. autoattribute:: PolarLinemap.sort_mode
.. autoattribute:: PolarLinemap.sort_variable
.. autoattribute:: PolarLinemap.sort_variable_index
.. autoattribute:: PolarLinemap.symbols
.. autoattribute:: PolarLinemap.theta_axis
.. autoattribute:: PolarLinemap.theta_variable
.. autoattribute:: PolarLinemap.theta_variable_index
.. autoattribute:: PolarLinemap.zone
.. autoattribute:: PolarLinemap.zone_index

.. py:currentmodule:: tecplot.plot

XYLinemap
^^^^^^^^^

.. autoclass:: XYLinemap

    **Attributes**

    .. autosummary::
        :nosignatures:

        aux_data
        bars
        curve
        error_bars
        function_dependency
        index
        indices
        line
        name
        show
        show_in_legend
        sort_mode
        sort_variable
        sort_variable_index
        symbols
        x_axis
        x_axis_index
        x_variable
        x_variable_index
        y_axis
        y_axis_index
        y_variable
        y_variable_index
        zone
        zone_index

.. autoattribute:: XYLinemap.aux_data
.. autoattribute:: XYLinemap.bars
.. autoattribute:: XYLinemap.curve
.. autoattribute:: XYLinemap.error_bars
.. autoattribute:: XYLinemap.function_dependency
.. autoattribute:: XYLinemap.index
.. autoattribute:: XYLinemap.indices
.. autoattribute:: XYLinemap.line
.. autoattribute:: XYLinemap.name
.. autoattribute:: XYLinemap.show
.. autoattribute:: XYLinemap.show_in_legend
.. autoattribute:: XYLinemap.sort_mode
.. autoattribute:: XYLinemap.sort_variable
.. autoattribute:: XYLinemap.sort_variable_index
.. autoattribute:: XYLinemap.symbols
.. autoattribute:: XYLinemap.x_axis
.. autoattribute:: XYLinemap.x_axis_index
.. autoattribute:: XYLinemap.x_variable
.. autoattribute:: XYLinemap.x_variable_index
.. autoattribute:: XYLinemap.y_axis
.. autoattribute:: XYLinemap.y_axis_index
.. autoattribute:: XYLinemap.y_variable
.. autoattribute:: XYLinemap.y_variable_index
.. autoattribute:: XYLinemap.zone
.. autoattribute:: XYLinemap.zone_index

.. py:currentmodule:: tecplot.plot

LinemapLine
^^^^^^^^^^^

.. autoclass:: LinemapLine

    **Attributes**

    .. autosummary::
        :nosignatures:

        color
        line_pattern
        line_thickness
        pattern_length
        show

.. autoattribute:: LinemapLine.color
.. autoattribute:: LinemapLine.line_pattern
.. autoattribute:: LinemapLine.line_thickness
.. autoattribute:: LinemapLine.pattern_length
.. autoattribute:: LinemapLine.show

.. py:currentmodule:: tecplot.plot

LinemapCurve
^^^^^^^^^^^^

.. autoclass:: LinemapCurve

    **Attributes**

    .. autosummary::
        :nosignatures:

        clamp_spline
        curve_type
        fit_range
        num_points
        polynomial_order
        spline_derivative_at_ends
        use_fit_range
        use_weight_variable
        weight_variable
        weight_variable_index

.. autoattribute:: LinemapCurve.clamp_spline
.. autoattribute:: LinemapCurve.curve_type
.. autoattribute:: LinemapCurve.fit_range
.. autoattribute:: LinemapCurve.num_points
.. autoattribute:: LinemapCurve.polynomial_order
.. autoattribute:: LinemapCurve.spline_derivative_at_ends
.. autoattribute:: LinemapCurve.use_fit_range
.. autoattribute:: LinemapCurve.use_weight_variable
.. autoattribute:: LinemapCurve.weight_variable
.. autoattribute:: LinemapCurve.weight_variable_index

.. py:currentmodule:: tecplot.plot

LinemapBars
^^^^^^^^^^^

.. autoclass:: LinemapBars

    **Attributes**

    .. autosummary::
        :nosignatures:

        fill_color
        fill_mode
        line_color
        line_thickness
        show
        size

.. autoattribute:: LinemapBars.fill_color
.. autoattribute:: LinemapBars.fill_mode
.. autoattribute:: LinemapBars.line_color
.. autoattribute:: LinemapBars.line_thickness
.. autoattribute:: LinemapBars.show
.. autoattribute:: LinemapBars.size

.. py:currentmodule:: tecplot.plot

LinemapErrorBars
^^^^^^^^^^^^^^^^

.. autoclass:: LinemapErrorBars

    **Attributes**

    .. autosummary::
        :nosignatures:

        bar_type
        color
        endcap_size
        line_thickness
        show
        step
        step_mode
        variable
        variable_index

.. autoattribute:: LinemapErrorBars.bar_type
.. autoattribute:: LinemapErrorBars.color
.. autoattribute:: LinemapErrorBars.endcap_size
.. autoattribute:: LinemapErrorBars.line_thickness
.. autoattribute:: LinemapErrorBars.show
.. autoattribute:: LinemapErrorBars.step
.. autoattribute:: LinemapErrorBars.step_mode
.. autoattribute:: LinemapErrorBars.variable
.. autoattribute:: LinemapErrorBars.variable_index

.. py:currentmodule:: tecplot.plot

LinemapIndices
^^^^^^^^^^^^^^

.. autoclass:: LinemapIndices

    **Attributes**

    .. autosummary::
        :nosignatures:

        i_range
        j_range
        k_range
        varying_index

.. autoattribute:: LinemapIndices.i_range
.. autoattribute:: LinemapIndices.j_range
.. autoattribute:: LinemapIndices.k_range
.. autoattribute:: LinemapIndices.varying_index

.. py:currentmodule:: tecplot.plot

LinemapSymbols
^^^^^^^^^^^^^^

.. autoclass:: LinemapSymbols

    **Attributes**

    .. autosummary::
        :nosignatures:

        color
        fill_color
        fill_mode
        line_thickness
        show
        size
        step
        step_mode
        symbol_type

    **Methods**

    .. autosummary::

        symbol

.. autoattribute:: LinemapSymbols.color
.. autoattribute:: LinemapSymbols.fill_color
.. autoattribute:: LinemapSymbols.fill_mode
.. autoattribute:: LinemapSymbols.line_thickness
.. autoattribute:: LinemapSymbols.show
.. autoattribute:: LinemapSymbols.size
.. autoattribute:: LinemapSymbols.step
.. autoattribute:: LinemapSymbols.step_mode
.. automethod:: LinemapSymbols.symbol
.. autoattribute:: LinemapSymbols.symbol_type

.. py:currentmodule:: tecplot.plot

GeometrySymbol
^^^^^^^^^^^^^^

.. autoclass:: GeometrySymbol

    **Attributes**

    .. autosummary::
        :nosignatures:

        shape

.. autoattribute:: GeometrySymbol.shape

.. py:currentmodule:: tecplot.plot

TextSymbol
^^^^^^^^^^

.. autoclass:: TextSymbol

    **Attributes**

    .. autosummary::
        :nosignatures:

        font_override
        text
        use_base_font

.. autoattribute:: TextSymbol.font_override
.. autoattribute:: TextSymbol.text
.. autoattribute:: TextSymbol.use_base_font
