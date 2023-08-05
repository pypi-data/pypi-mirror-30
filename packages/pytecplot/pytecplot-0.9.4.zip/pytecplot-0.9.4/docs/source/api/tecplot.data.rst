Data
====

..  contents::
    :local:
    :depth: 2

tecplot.data
------------

.. automodule:: tecplot.data


Loading Data
------------

..  contents::
    :local:
    :depth: 1

data.load_tecplot()
^^^^^^^^^^^^^^^^^^^

.. autofunction:: tecplot.data.load_tecplot

data.load_tecplot_szl()
^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: tecplot.data.load_tecplot_szl

data.load_cgns()
^^^^^^^^^^^^^^^^

.. autofunction:: tecplot.data.load_cgns

data.load_fluent()
^^^^^^^^^^^^^^^^^^

.. autofunction:: tecplot.data.load_fluent

data.load_plot3d()
^^^^^^^^^^^^^^^^^^

.. autofunction:: tecplot.data.load_plot3d


Saving Data
-----------

..  contents::
    :local:
    :depth: 1

data.save_tecplot_ascii()
^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: tecplot.data.save_tecplot_ascii

data.save_tecplot_plt()
^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: tecplot.data.save_tecplot_plt

data.save_tecplot_szl()
^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: tecplot.data.save_tecplot_szl


Data Queries
------------

data.query.probe_at_position()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: tecplot.data.query.probe_at_position

data.query.probe_on_surface()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: tecplot.data.query.probe_on_surface


Data Operations
---------------

..  contents::
    :local:
    :depth: 1

data.operate.Range()
^^^^^^^^^^^^^^^^^^^^

.. autofunction:: tecplot.data.operate.Range

data.operate.execute_equation()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: tecplot.data.operate.execute_equation

data.operate.interpolate_linear()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: tecplot.data.operate.interpolate_linear

data.operate.interpolate_inverse_distance()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: tecplot.data.operate.interpolate_inverse_distance

data.operate.interpolate_kriging()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: tecplot.data.operate.interpolate_kriging


Data Extractions
----------------

data.extract.extract_slice()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: tecplot.data.extract.extract_slice


.. _data_access:

Data Access
-----------

..  contents::
    :local:
    :depth: 2

.. py:currentmodule:: tecplot.data

Dataset
^^^^^^^

.. autoclass:: Dataset

    **Attributes**

    .. autosummary::
        :nosignatures:

        VariablesNamedTuple
        aux_data
        num_solution_times
        num_variables
        num_zones
        solution_times
        title

    **Methods**

    .. autosummary::

        add_fe_zone
        add_ordered_zone
        add_poly_zone
        add_variable
        add_zone
        branch_connectivity
        branch_variables
        copy_zones
        delete_variables
        delete_zones
        share_connectivity
        share_variables
        variable
        variables
        zone
        zones

.. autoattribute:: Dataset.VariablesNamedTuple
.. automethod:: Dataset.add_fe_zone
.. automethod:: Dataset.add_ordered_zone
.. automethod:: Dataset.add_poly_zone
.. automethod:: Dataset.add_variable
.. automethod:: Dataset.add_zone
.. autoattribute:: Dataset.aux_data
.. automethod:: Dataset.branch_connectivity
.. automethod:: Dataset.branch_variables
.. automethod:: Dataset.copy_zones
.. automethod:: Dataset.delete_variables
.. automethod:: Dataset.delete_zones
.. autoattribute:: Dataset.num_solution_times
.. autoattribute:: Dataset.num_variables
.. autoattribute:: Dataset.num_zones
.. automethod:: Dataset.share_connectivity
.. automethod:: Dataset.share_variables
.. autoattribute:: Dataset.solution_times
.. autoattribute:: Dataset.title
.. automethod:: Dataset.variable
.. automethod:: Dataset.variables
.. automethod:: Dataset.zone
.. automethod:: Dataset.zones

.. py:currentmodule:: tecplot.data

Variable
^^^^^^^^

.. autoclass:: Variable

    **Attributes**

    .. autosummary::
        :nosignatures:

        aux_data
        index
        name
        num_zones

    **Methods**

    .. autosummary::

        max
        min
        minmax
        values

.. autoattribute:: Variable.aux_data
.. autoattribute:: Variable.index
.. automethod:: Variable.max
.. automethod:: Variable.min
.. automethod:: Variable.minmax
.. autoattribute:: Variable.name
.. autoattribute:: Variable.num_zones
.. automethod:: Variable.values

Zones
^^^^^

..  contents::
    :local:
    :depth: 1

tecplot.data.zone
+++++++++++++++++

.. automodule:: tecplot.data.zone


.. py:currentmodule:: tecplot.data

OrderedZone
+++++++++++

.. autoclass:: OrderedZone

    **Attributes**

    .. autosummary::
        :nosignatures:

        aux_data
        dimensions
        face_neighbors
        index
        name
        num_elements
        num_faces
        num_faces_per_element
        num_points
        num_points_per_element
        num_variables
        rank
        solution_time
        strand
        zone_type

    **Methods**

    .. autosummary::

        copy
        values

.. autoattribute:: OrderedZone.aux_data
.. automethod:: OrderedZone.copy
.. autoattribute:: OrderedZone.dimensions
.. autoattribute:: OrderedZone.face_neighbors
.. autoattribute:: OrderedZone.index
.. autoattribute:: OrderedZone.name
.. autoattribute:: OrderedZone.num_elements
.. autoattribute:: OrderedZone.num_faces
.. autoattribute:: OrderedZone.num_faces_per_element
.. autoattribute:: OrderedZone.num_points
.. autoattribute:: OrderedZone.num_points_per_element
.. autoattribute:: OrderedZone.num_variables
.. autoattribute:: OrderedZone.rank
.. autoattribute:: OrderedZone.solution_time
.. autoattribute:: OrderedZone.strand
.. automethod:: OrderedZone.values
.. autoattribute:: OrderedZone.zone_type

.. py:currentmodule:: tecplot.data

ClassicFEZone
+++++++++++++

.. autoclass:: ClassicFEZone

    **Attributes**

    .. autosummary::
        :nosignatures:

        aux_data
        face_neighbors
        index
        name
        nodemap
        num_elements
        num_faces
        num_faces_per_element
        num_points
        num_points_per_element
        num_variables
        rank
        shared_connectivity
        solution_time
        strand
        zone_type

    **Methods**

    .. autosummary::

        copy
        values

.. autoattribute:: ClassicFEZone.aux_data
.. automethod:: ClassicFEZone.copy
.. autoattribute:: ClassicFEZone.face_neighbors
.. autoattribute:: ClassicFEZone.index
.. autoattribute:: ClassicFEZone.name
.. autoattribute:: ClassicFEZone.nodemap
.. autoattribute:: ClassicFEZone.num_elements
.. autoattribute:: ClassicFEZone.num_faces
.. autoattribute:: ClassicFEZone.num_faces_per_element
.. autoattribute:: ClassicFEZone.num_points
.. autoattribute:: ClassicFEZone.num_points_per_element
.. autoattribute:: ClassicFEZone.num_variables
.. autoattribute:: ClassicFEZone.rank
.. autoattribute:: ClassicFEZone.shared_connectivity
.. autoattribute:: ClassicFEZone.solution_time
.. autoattribute:: ClassicFEZone.strand
.. automethod:: ClassicFEZone.values
.. autoattribute:: ClassicFEZone.zone_type

.. py:currentmodule:: tecplot.data

PolyFEZone
++++++++++

.. autoclass:: PolyFEZone

    **Attributes**

    .. autosummary::
        :nosignatures:

        aux_data
        facemap
        index
        name
        num_elements
        num_faces
        num_points
        num_variables
        rank
        shared_connectivity
        solution_time
        strand
        zone_type

    **Methods**

    .. autosummary::

        copy
        values

.. autoattribute:: PolyFEZone.aux_data
.. automethod:: PolyFEZone.copy
.. autoattribute:: PolyFEZone.facemap
.. autoattribute:: PolyFEZone.index
.. autoattribute:: PolyFEZone.name
.. autoattribute:: PolyFEZone.num_elements
.. autoattribute:: PolyFEZone.num_faces
.. autoattribute:: PolyFEZone.num_points
.. autoattribute:: PolyFEZone.num_variables
.. autoattribute:: PolyFEZone.rank
.. autoattribute:: PolyFEZone.shared_connectivity
.. autoattribute:: PolyFEZone.solution_time
.. autoattribute:: PolyFEZone.strand
.. automethod:: PolyFEZone.values
.. autoattribute:: PolyFEZone.zone_type

.. py:currentmodule:: tecplot.data

Array
^^^^^

.. autoclass:: Array

    **Attributes**

    .. autosummary::
        :nosignatures:

        c_type
        data_type
        location
        passive
        shape
        shared_zones

    **Methods**

    .. autosummary::

        as_numpy_array
        copy
        max
        min
        minmax

.. automethod:: Array.as_numpy_array
.. autoattribute:: Array.c_type
.. automethod:: Array.copy
.. autoattribute:: Array.data_type
.. autoattribute:: Array.location
.. automethod:: Array.max
.. automethod:: Array.min
.. automethod:: Array.minmax
.. autoattribute:: Array.passive
.. autoattribute:: Array.shape
.. autoattribute:: Array.shared_zones

.. py:currentmodule:: tecplot.data

Nodemap
^^^^^^^

.. autoclass:: Nodemap

    **Attributes**

    .. autosummary::
        :nosignatures:

        array
        c_type
        num_points_per_element
        shape
        size

    **Methods**

    .. autosummary::

        assignment
        element
        num_elements

.. autoattribute:: Nodemap.array
.. automethod:: Nodemap.assignment
.. autoattribute:: Nodemap.c_type
.. automethod:: Nodemap.element
.. automethod:: Nodemap.num_elements
.. autoattribute:: Nodemap.num_points_per_element
.. autoattribute:: Nodemap.shape
.. autoattribute:: Nodemap.size

.. py:currentmodule:: tecplot.data

Facemap
^^^^^^^

.. autoclass:: Facemap

    **Attributes**

    .. autosummary::
        :nosignatures:

        element_c_type
        node_c_type
        num_unique_nodes

    **Methods**

    .. autosummary::

        alloc
        assignment
        boundary_connection
        face
        left_element
        node
        num_boundary_connections
        num_faces
        num_nodes
        right_element
        set_boundary_connections
        set_elementmap
        set_elements
        set_mapping
        set_nodes

.. automethod:: Facemap.alloc
.. automethod:: Facemap.assignment
.. automethod:: Facemap.boundary_connection
.. autoattribute:: Facemap.element_c_type
.. automethod:: Facemap.face
.. automethod:: Facemap.left_element
.. automethod:: Facemap.node
.. autoattribute:: Facemap.node_c_type
.. automethod:: Facemap.num_boundary_connections
.. automethod:: Facemap.num_faces
.. automethod:: Facemap.num_nodes
.. autoattribute:: Facemap.num_unique_nodes
.. automethod:: Facemap.right_element
.. automethod:: Facemap.set_boundary_connections
.. automethod:: Facemap.set_elementmap
.. automethod:: Facemap.set_elements
.. automethod:: Facemap.set_mapping
.. automethod:: Facemap.set_nodes

.. py:currentmodule:: tecplot.data

FaceNeighbors
^^^^^^^^^^^^^

.. autoclass:: FaceNeighbors

    **Attributes**

    .. autosummary::
        :nosignatures:

        c_type
        mode

    **Methods**

    .. autosummary::

        add_local_neighbors
        add_neighbors
        assignment
        is_obscured
        neighbors
        set_neighbors

.. automethod:: FaceNeighbors.add_local_neighbors
.. automethod:: FaceNeighbors.add_neighbors
.. automethod:: FaceNeighbors.assignment
.. autoattribute:: FaceNeighbors.c_type
.. automethod:: FaceNeighbors.is_obscured
.. autoattribute:: FaceNeighbors.mode
.. automethod:: FaceNeighbors.neighbors
.. automethod:: FaceNeighbors.set_neighbors

Auxiliary Data
--------------

.. py:currentmodule:: tecplot.session

AuxData
^^^^^^^

.. autoclass:: AuxData

    **Methods**

    .. autosummary::

        as_dict
        clear
        index
        items
        key
        keys
        update
        values

.. automethod:: AuxData.as_dict
.. automethod:: AuxData.clear
.. automethod:: AuxData.index
.. automethod:: AuxData.items
.. automethod:: AuxData.key
.. automethod:: AuxData.keys
.. automethod:: AuxData.update
.. automethod:: AuxData.values
