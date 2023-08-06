
ezdxf
=====

.. image:: https://readthedocs.org/projects/pip/badge/
   :target: https://ezdxf.readthedocs.io
   :alt: Read The Docs

Abstract
--------

A Python package to create and modify DXF drawings, independent from the DXF
version. You can open/save every DXF file without loosing any content (except comments),
Unknown tags in the DXF file will be ignored but preserved for saving. With this behavior
it is possible to open also DXF drawings that contains data from 3rd party applications.

Quick-Info
----------

- ezdxf is a Python package to create new DXF files and read/modify/write existing DXF files
- the intended audience are developers
- requires Python 2.7 or later, runs on CPython and pypy, maybe on IronPython and Jython
- OS independent
- additional required packages: `pyparsing <https://pypi.python.org/pypi/pyparsing/2.0.1>`_
- MIT-License
- read/write/new support for DXF versions: R12, R2000, R2004, R2007, R2010, R2013 and R2018
- additional read support for DXF versions R13/R14 (upgraded to R2000)
- additional read support for older DXF versions than R12 (upgraded to R12)
- preserves third-party DXF content
- additional fast DXF R12 writer, that creates just an ENTITIES section with support for the basic DXF entities

a simple example::

    import ezdxf

    drawing = ezdxf.new(dxfversion='AC1024')  # or use the AutoCAD release name ezdxf.new(dxfversion='R2010')
    modelspace = drawing.modelspace()
    modelspace.add_line((0, 0), (10, 0), dxfattribs={'color': 7})
    drawing.layers.new('TEXTLAYER', dxfattribs={'color': 2})
    # use set_pos() for proper TEXT alignment - the relations between halign, valign, insert and align_point are tricky.
    modelspace.add_text('Test', dxfattribs={'layer': 'TEXTLAYER'}).set_pos((0, 0.2), align='CENTER')
    drawing.saveas('test.dxf')

example for the *r12writer*, writes a simple DXF R12 file without in-memory structures::

    from random import random
    from ezdxf.r12writer import r12writer

    MAX_X_COORD = 1000.0
    MAX_Y_COORD = 1000.0
    CIRCLE_COUNT = 100000

    with r12writer("many_circles.dxf") as dxf:
        for i in range(CIRCLE_COUNT):
            dxf.add_circle((MAX_X_COORD*random(), MAX_Y_COORD*random()), radius=2)

The r12writer supports only the ENTITIES section of a DXF R12 drawing, no HEADER, TABLES or BLOCKS section is
present, except FIXED-TABLES are written, than some additional predefined text styles and line types are available.

Installation
============

Install with pip::

    pip install ezdxf

or from source::

    python setup.py install

Website
=======

https://ezdxf.mozman.at/

Documentation
=============

Documentation of development version at https://ezdxf.mozman.at/docs

Documentation of latest release at http://ezdxf.readthedocs.io/

The source code of ezdxf can be found at GitHub.com:

http://github.com/mozman/ezdxf.git

Feedback
========

Issue Tracker at:

http://github.com/mozman/ezdxf/issues

Questions and Feedback at Google Groups:

https://groups.google.com/d/forum/python-ezdxf

python-ezdxf@googlegroups.com

Feedback is greatly appreciated.

Manfred

Contact
=======

ezdxf@mozman.at

News
====

Version 0.8.8 - 2018-04-02

   * Release notes: https://ezdxf.mozman.at/release-v0-8-8.html
   * NEW: read/write support for GEODATA entity
   * NEW: read/(limited)write support for SURFACE, EXTRUDEDSURFACE, REVOLVEDSURFACE, LOFTEDSURFACE and SWEPTSURFACE entity
   * NEW: support for extension dictionaries
   * NEW: add_spline_control_frame(), create and add B-spline control frame from fit points
   * NEW: add_spline_approx(), approximate B-spline by a reduced count of control points
   * NEW: ezdxf.setup_linetypes(dwg), setup standard line types
   * NEW: ezdxf.setup_styles(dwg), setup standard text styles
   * NEW: LWPolyline.vertices() yields all points as (x, y) tuples in OCS, LWPolyline.dxf.elevation is the z-axis value
   * NEW: LWPolyline.vertices_in_wcs() yields all points as (x, y, z) tuples in WCS
   * NEW: basic __str__()  and __repr__() support for DXF entities, returns just DXF type and handle
   * NEW: bulge related function in module ezdxf.algebra.bulge
   * NEW: Object Coordinate System support by DXFEntity.ocs() and OCS() class in module ezdxf.algebra
   * NEW: User Coordinate System support by UCS() class in module ezdxf.algebra
   * CHANGE: DXFEntity.set_app_data() and Entity.set_xdata accept also list of tuples as tags, DXFTag() is not required
   * BUGFIX: entity structure validator excepts group code >= 1000 before XDATA section (used in AutoCAD Civil 3D and AutoCAD Map 3D)

Version 0.8.7 - 2018-03-04

   * Release notes: https://ezdxf.mozman.at/release-v0-8-7.html
   * NEW: entity.get_layout() returns layout in which entity resides or None if unassigned
   * NEW: copy any DXF entity by entity.copy() without associated layout, add copy to any layout you want, by
     layout.add_entity().
   * NEW: copy entity to another layout by entity.copy_to_layout(layout)
   * NEW: move entity from actual layout to another layout by entity.move_to_layout(layout)
   * NEW: support for splines by control points: add_open_spline(), add_closed_spline(), add_rational_spline(),
     add_closed_rational_spline()
   * NEW: bspline_control_frame() calculates B-spline control points from fit points, but not the same as AutoCAD
   * NEW: R12Spline add-on, 2d B-spline with control frame support by AutoCAD, but curve is just an approximated POLYLINE
   * NEW: added entity.get_flag_state() and entity.set_flag_state() for easy access to binary coded flags
   * NEW: set new $FINGERPRINTGUID for new drawings
   * NEW: set new $VERSIONGUID on saving a drawing
   * NEW: improved IMAGE support, by adding RASTERVARIABLES entity, use Drawing.set_raster_variables(frame, quality, units)
   * BUGFIX: closing user defined image boundary path automatically, else AutoCAD crashes

Version 0.8.6 - 2018-02-17

   * Release notes: https://ezdxf.mozman.at/release-v0-8-6.html
   * NEW: ezdxf project website: https://ezdxf.mozman.at/
   * CHANGE: create all missing tables of the TABLES sections for DXF R12
   * BUGFIX: entities on new layouts will be saved
   * NEW: Layout.page_setup() and correct 'main' viewport for DXF R2000+; For DXF R12 page_setup() exists, but does not
     provide useful results. Page setup for DXF R12 is still a mystery to me.
   * NEW: Table(), MText(), Ellipse(), Spline(), Bezier(), Clothoid(), LinearDimension(), RadialDimension(),
     ArcDimension() and AngularDimension() composite objects from dxfwrite as add-ons, these add-ons support DXF R12
   * NEW: geometry builder as add-ons: MeshBuilder(), MeshVertexMerger(), MengerSponge(), SierpinskyPyramid(), these
     add-ons require DXF R2000+ (MESH entity)
   * BUGFIX: fixed invalid implementation of context manager for r12writer

Version 0.8.5 - 2018-01-28

   * Release notes: https://ezdxf.mozman.at/release-v0-8-5.html
   * CHANGE: block names are case insensitive 'TEST' == 'Test' (like AutoCAD)
   * CHANGE: table entry (layer, linetype, style, dimstyle, ...) names are case insensitive 'TEST' == 'Test' (like AutoCAD)
   * CHANGE: raises DXFInvalidLayerName() for invalid characters in layer names: <>/\":;?*|=`
   * CHANGE: audit process rewritten
   * CHANGE: skip all comments, group code 999
   * CHANGE: removed compression for unused sections (THUMBNAILSECTION, ACDSDATA)
   * NEW: write DXF R12 files without handles: set dwg.header['$HANDLING']=0, default value is 1
   * added subclass marker filter for R12 and prior files in legacy_mode=True (required for malformed DXF files)
   * removed special check for Leica Disto Unit files, use readfile(filename, legacy_mode=True) (malformed DXF R12 file,
     see previous point)

Version 0.8.4 - 2018-01-14

  * Release notes: https://ezdxf.mozman.at/release-v0-8-4.html
  * NEW: Support for complex line types with text or shapes
  * NEW: DXF file structure validator at SECTION level, tags outside of sections will be removed
  * NEW: Basic read support for DIMENSION
  * CHANGE: improved exception management, in the future ezdxf should only raise exceptions inherited from DXFError for
    DXF related errors, previous exception classes still work

    - DXFValueError(DXFError, ValueError)
    - DXFKeyError(DXFError, KeyError)
    - DXFAttributeError(DXFError, AttributeError)
    - DXFIndexError(DXFError, IndexError)
    - DXFTableEntryError(DXFValueError)

  * speedup low level tag reader around 5%, and speedup tag compiler around 5%

Version 0.8.3 - 2018-01-02

  * CHANGE: Lwpolyline - suppress yielding z coordinates if they exists (DXFStructureError: z coordinates are not defined in the DXF standard)
  * NEW: setup creates a script called 'dxfpp' (DXF Pretty Printer) in the Python script folder
  * NEW: basic support for DXF format AC1032 introduced by AutoCAD 2018
  * NEW: ezdxf use logging and writes all logs to a logger called 'ezdxf'. Logging setup is the domain of the application!
  * NEW: warns about multiple block definitions with the same name in a DXF file. (DXFStructureError)
  * NEW: legacy_mode parameter in ezdxf.read() and ezdxf.readfile(): tries do fix coordinate order in LINE
    entities (10, 11, 20, 21) by the cost of around 5% overall speed penalty at DXF file loading

Version 0.8.2 - 2017-05-01

  * NEW: Insert.delete_attrib(tag) - delete ATTRIB entities from the INSERT entity
  * NEW: Insert.delete_all_attribs() - delete all ATTRIB entities from the INSERT entity
  * BUGFIX: setting attribs_follow=1 at INSERT entity before adding an attribute entity works

Version 0.8.1 - 2017-04-06

  * NEW: added support for constant ATTRIB/ATTDEF to the INSERT (block reference) entity
  * NEW: added ATTDEF management methods to BlockLayout (has_attdef, get_attdef, get_attdef_text)
  * NEW: added (read/write) properties to ATTDEF/ATTRIB for setting flags (is_const, is_invisible, is_verify, is_preset)

Version 0.8.0 - 2017-03-28

  * added groupby(dxfattrib='', key=None) entity query function, it is supported by all layouts and the query result
    container: Returns a dict, where entities are grouped by a dxfattrib or the result of a key function.
  * added ezdxf.audit() for DXF error checking for drawings created by ezdxf - but not very capable yet
  * dxfattribs in factory functions like add_line(dxfattribs=...), now are copied internally and stay unchanged, so they
    can be reused multiple times without getting modified by ezdxf.
  * removed deprecated Drawing.create_layout() -> Drawing.new_layout()
  * removed deprecated Layouts.create() -> Layout.new()
  * removed deprecated Table.create() -> Table.new()
  * removed deprecated DXFGroupTable.add() -> DXFGroupTable.new()
  * BUFIX in EntityQuery.extend()

Version 0.7.9 - 2017-01-31

  * BUGFIX: lost data if model space and active layout are called \*MODEL_SPACE and \*PAPER_SPACE

Version 0.7.8 - 2017-01-22

  * BUGFIX: HATCH accepts SplineEdges without defined fit points
  * BUGFIX: fixed universal line ending problem in ZipReader()
  * Moved repository to GitHub: https://github.com/mozman/ezdxf.git

Version 0.7.7 - 2016-10-22

  * NEW: repairs malformed Leica Disto DXF R12 files, ezdxf saves a valid DXF R12 file.
  * NEW: added Layout.unlink(entity) method: unlinks an entity from layout but does not delete entity from the drawing database.
  * NEW: added Drawing.add_xref_def(filename, name) for adding external reference definitions
  * CHANGE: renamed parameters for EdgePath.add_ellipse() - major_axis_vector -> major_axis; minor_axis_length -> ratio
    to be consistent to the ELLIPSE entity
  * UPDATE: Entity.tags.new_xdata() and Entity.tags.set_xdata() accept tuples as tags, no import of DXFTag required
  * UPDATE: EntityQuery to support both 'single' and "double" quoted strings - Harrison Katz <harrison@neadwerx.com>
  * improved DXF R13/R14 compatibility



