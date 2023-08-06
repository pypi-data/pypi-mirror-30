# Created: 12.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from ..legacy import LegacyDXFFactory
from . import tableentries
from . import graphics
from . import solid3d
from . import surface
from .mesh import Mesh
from .spline import Spline
from .mtext import MText
from .hatch import Hatch
from .viewport import Viewport
from .image import Image
from .image import ImageDef, ImageDefReactor, RasterVariables
from .underlay import PdfDefinition, PdfUnderlay
from .underlay import DwfDefinition, DwfUnderlay
from .underlay import DgnDefinition, DgnUnderlay
from .dxflayout import DXFPlotSettings, DXFLayout
from .dimension import Dimension

from . import dxfobjects
from .geodata import GeoData
from .groups import DXFGroup
from .layouts import Layouts, BlockLayout
from ..tools.handle import ImageKeyGenerator, UnderlayKeyGenerator
from ..lldxf.const import DXFKeyError

UPDATE_ENTITY_WRAPPERS = {
    # DXF Objects
    'DICTIONARY': dxfobjects.DXFDictionary,
    'CLASS': dxfobjects.DXFClass,
    'ACDBDICTIONARYWDFLT': dxfobjects.DXFDictionaryWithDefault,
    'DICTIONARYVAR': dxfobjects.DXFDictionaryVar,
    'PLOTSETTINGS': DXFPlotSettings,
    'LAYOUT': DXFLayout,
    'XRECORD': dxfobjects.XRecord,
    'DATATABLE': dxfobjects.DXFDataTable,
    'GROUP': DXFGroup,
    'ACDBPLACEHOLDER': dxfobjects.ACDBPlaceHolder,
    'IMAGEDEF': ImageDef,
    'IMAGEDEF_REACTOR': ImageDefReactor,
    'PDFDEFINITION': PdfDefinition,
    'DWFDEFINITION': DwfDefinition,
    'DGNDEFINITION': DgnDefinition,
    'RASTERVARIABLES': RasterVariables,
    'GEODATA': GeoData,
    # DXF Table Entries
    'LAYER': tableentries.Layer,
    'STYLE': tableentries.Style,
    'LTYPE': tableentries.Linetype,
    'DIMSTYLE': tableentries.DimStyle,
    'VIEW': tableentries.View,
    'VPORT': tableentries.VPort,
    'UCS': tableentries.UCS,
    'APPID': tableentries.AppID,
    'BLOCK_RECORD': tableentries.BlockRecord,
    # DXF Entities
    'LINE': graphics.Line,
    'POINT': graphics.Point,
    'CIRCLE': graphics.Circle,
    'ARC': graphics.Arc,
    'TRACE': graphics.Trace,
    'SOLID': graphics.Solid,
    '3DFACE': graphics.Face,
    'TEXT': graphics.Text,
    'MTEXT': MText,
    'POLYLINE': graphics.Polyline,
    'VERTEX': graphics.Vertex,
    'SEQEND': graphics.SeqEnd,
    'LWPOLYLINE': graphics.LWPolyline,
    'BLOCK': graphics.Block,
    'ENDBLK': graphics.EndBlk,
    'INSERT': graphics.Insert,
    'ATTDEF': graphics.Attdef,
    'ATTRIB': graphics.Attrib,
    'ELLIPSE': graphics.Ellipse,
    'RAY': graphics.Ray,
    'XLINE': graphics.XLine,
    'SHAPE': graphics.Shape,
    'SPLINE': Spline,
    'BODY': solid3d.Body,
    'REGION': solid3d.Region,
    '3DSOLID': solid3d.Solid3d,
    'SURFACE': surface.Surface,
    'EXTRUDEDSURFACE': surface.ExtrudedSurface,
    'LOFTEDSURFACE': surface.LoftedSurface,
    'REVOLVEDSURFACE': surface.RevolvedSurface,
    'SWEPTSURFACE': surface.SweptSurface,
    'MESH': Mesh,
    'HATCH': Hatch,
    'VIEWPORT': Viewport,
    'IMAGE': Image,
    'PDFUNDERLAY': PdfUnderlay,
    'DWFUNDERLAY': DwfUnderlay,
    'DGNUNDERLAY': DgnUnderlay,
    'DIMENSION': Dimension,
}


class ModernDXFFactory(LegacyDXFFactory):
    """ DXf factory for DXF version AC1015 and later. (changed 04.05.2014)
    """
    DEFAULT_WRAPPER = graphics.ModernGraphicEntity

    def __init__(self, drawing):
        super(ModernDXFFactory, self).__init__(drawing)
        self.ENTITY_WRAPPERS.update(UPDATE_ENTITY_WRAPPERS)
        self.image_key_generator = ImageKeyGenerator()
        self.underlay_key_generator = UnderlayKeyGenerator()

    @property
    def rootdict(self):
        return self.drawing.rootdict

    @property
    def block_records(self):
        return self.drawing.sections.tables.block_records

    def create_block_entry_in_block_records_table(self, block_layout):
        # required for DXFVERSION > ac1009: Entry in the BLOCK_RECORDS section
        block_record = self.block_records.new(block_layout.name)
        block_layout.set_block_record_handle(block_record.dxf.handle)

    def get_layouts(self):
        return Layouts(self.drawing)

    def new_block_layout(self, block_handle, endblk_handle):
        # Warning: Do not call create_block_entry_in_block_records_table() from this point, this will not work!
        return BlockLayout(self.entitydb, self, block_handle, endblk_handle)

    def copy_layout(self, source_entity, target_entity):
        # Place target_entity in same layout as source_entity
        target_entity.dxf.paperspace = source_entity.dxf.paperspace
        target_entity.dxf.owner = source_entity.dxf.owner

    def post_read_tags_fixer(self, tags):
        if tags.dxftype() == 'VERTEX':
            graphics.Vertex.fix_tags(tags)

    def next_image_key(self, checkfunc=lambda k: True):
        while True:
            key = self.image_key_generator.next()
            if checkfunc(key):
                return key

    def next_underlay_key(self, checkfunc=lambda k: True):
        while True:
            key = self.underlay_key_generator.next()
            if checkfunc(key):
                return key

    def get_layout_for_entity(self, entity):
        if entity.dxf.owner not in self.entitydb:
            return None

        dwg = self.drawing
        try:
            layout = dwg.layouts.get_layout_for_entity(entity)
        except DXFKeyError:
            block_rec = dwg.dxffactory.wrap_handle(entity.dxf.owner)
            block_name = block_rec.dxf.name
            layout = dwg.blocks.get(block_name)
        return layout
