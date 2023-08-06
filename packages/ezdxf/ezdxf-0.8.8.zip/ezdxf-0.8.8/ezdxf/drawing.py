# Created: 11.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from datetime import datetime
import io
import logging
from .database import EntityDB
from .lldxf.const import DXFVersionError, acad_release, BLK_XREF, BLK_EXTERNAL, DXFValueError
from .lldxf.loader import load_dxf_structure, fill_database
from .dxffactory import dxffactory
from .templates import TemplateLoader
from .options import options
from .tools.codepage import tocodepage, toencoding
from .sections import Sections
from .tools.juliandate import juliandate
from .lldxf import repair
from .tools import guid
from .tracker import Tracker
logger = logging.getLogger('ezdxf')


class Drawing(object):
    """
    The Central Data Object
    """
    def __init__(self, tagger):
        """
        Build a new DXF drawing from a steam of DXF tags.

        Args:
             tagger: generator or list of DXF tags as DXFTag() objects
        """
        def get_header(sections):
            from .sections.header import HeaderSection
            header_entities = sections.get('HEADER', [None])[0]  # all tags in the first DXF structure entity
            return HeaderSection(header_entities)
        self.tracker = Tracker()
        self._is_binary_data_compressed = False
        self._groups = None  # read only
        self.filename = None  # read/write
        self.entitydb = EntityDB()  # read only
        sections = load_dxf_structure(tagger)  # load complete DXF entity structure
        # create section HEADER
        header = get_header(sections)
        self.dxfversion = header.get('$ACADVER', 'AC1009')  # read only
        self.dxffactory = dxffactory(self)  # read only, requires self.dxfversion
        self.encoding = toencoding(header.get('$DWGCODEPAGE', 'ANSI_1252'))  # read/write
        # get handle seed
        seed = header.get('$HANDSEED', str(self.entitydb.handles))
        # setup handles
        self.entitydb.handles.reset(seed)
        # store all necessary DXF entities in the drawing database
        fill_database(self.entitydb, sections, dxffactory=self.dxffactory)
        # create sections: TABLES, BLOCKS, ENTITIES, CLASSES, OBJECTS
        self.sections = Sections(sections, drawing=self, header=header)

        if self.dxfversion > 'AC1009':
            self.rootdict = self.objects.rootdict
            self.objects.setup_objects_management_tables(self.rootdict)  # create missing tables
            if self.dxfversion in ('AC1012', 'AC1014'):  # releases R13 and R14
                repair.upgrade_to_ac1015(self)
            # some applications don't setup properly the model and paper space layouts
            repair.setup_layouts(self)
            self._groups = self.objects.groups()

        if self.dxfversion <= 'AC1009':  # do cleanup work, before building layouts
            if self.dxfversion < 'AC1009':  # legacy DXF version
                repair.upgrade_to_ac1009(self)  # upgrade to DXF format AC1009 (DXF R12)
            repair.cleanup_r12(self)
            # ezdxf puts automatically handles into all entities added to the entities database
            # new feature: write R12 without handles, if $HANDLING=0 is set by user
            self.header['$HANDLING'] = 1  # write handles by default

        self.layouts = self.dxffactory.get_layouts()
        if options.compress_binary_data:
            self.compress_binary_data()

    def compress_binary_data(self):
        if self.dxfversion > 'AC1009' and not self._is_binary_data_compressed:
            self.entitydb.compress_binary_data()
            self._is_binary_data_compressed = True

    @property
    def acad_release(self):
        return acad_release.get(self.dxfversion, "unknown")

    @property
    def _handles(self):
        return self.entitydb.handles

    @property
    def is_binary_data_compressed(self):
        return self._is_binary_data_compressed

    @property
    def header(self):
        return self.sections.header

    @property
    def layers(self):
        return self.sections.tables.layers

    @property
    def linetypes(self):
        return self.sections.tables.linetypes

    @property
    def styles(self):
        return self.sections.tables.styles

    @property
    def dimstyles(self):
        return self.sections.tables.dimstyles

    @property
    def ucs(self):
        return self.sections.tables.ucs

    @property
    def appids(self):
        return self.sections.tables.appids

    @property
    def views(self):
        return self.sections.tables.views

    @property
    def block_records(self):
        return self.sections.tables.block_records

    @property
    def viewports(self):
        return self.sections.tables.viewports

    @property
    def blocks(self):
        return self.sections.blocks

    @property
    def groups(self):
        if self._groups is not None:
            return self._groups
        else:
            raise DXFVersionError('Groups not supported in DXF version R12.')

    def modelspace(self):
        return self.layouts.modelspace()

    def layout(self, name=None):
        return self.layouts.get(name)

    def layout_names(self):
        return list(self.layouts.names())

    def delete_layout(self, name):
        if self.dxfversion > 'AC1009':
            if name not in self.layouts:
                raise DXFValueError("Layout '{}' does not exist.".format(name))
            else:
                self.layouts.delete(name)
        else:
            raise DXFVersionError('delete_layout() not supported for DXF version R12.')

    def new_layout(self, name, dxfattribs=None):
        if self.dxfversion > 'AC1009':
            if name in self.layouts:
                raise DXFValueError("Layout '{}' already exists.".format(name))
            else:
                return self.layouts.new(name, dxfattribs)
        else:
            raise DXFVersionError('new_layout() not supported for DXF version R12.')

    def get_active_layout_key(self):
        if self.dxfversion > 'AC1009':
            try:
                active_layout_block_record = self.block_records.get('*Paper_Space')  # block names are case insensitive
                return active_layout_block_record.dxf.handle
            except DXFValueError:
                return None
        else:
            return self.layout().layout_key  # AC1009 supports just one layout and this is the active one

    def get_active_entity_space_layout_keys(self):
        layout_keys = [self.modelspace().layout_key]
        active_layout_key = self.get_active_layout_key()
        if active_layout_key is not None:
            layout_keys.append(active_layout_key)
        return layout_keys

    @property
    def entities(self):
        return self.sections.entities

    @property
    def objects(self):
        return self.sections.objects

    def get_dxf_entity(self, handle):
        """
        Get entity by *handle* from entity database.

        Low level access to DXF entities database. Raises *KeyError* if handle don't exists.
        Returns DXFEntity() or inherited.

        If you just need the raw DXF tags use::

            tags = Drawing.entitydb[handle]  # raises KeyError, if handle don't exist
            tags = Drawing.entitydb.get(handle)  # returns a default value, if handle don't exist (None by default)

        type of tags: ExtendedTags()
        """
        return self.dxffactory.wrap_handle(handle)

    def add_image_def(self, filename, size_in_pixel, name=None):
        """
        Add an image definition to the objects section.

        For AutoCAD works best with absolute image paths but not good, you have to update external references manually
        in AutoCAD, which is not possible in TrueView. If you drawing units differ from 1 meter, you also have to use:
        Drawing.set_raster_variables().

        Args:
            filename: image file name (absolute path works best for AutoCAD)
            size_in_pixel: image size in pixel as (x, y) tuple
            name: image name for internal use, None for using filename as name (best for AutoCAD)

        """
        if self.dxfversion < 'AC1015':
            raise DXFVersionError('The IMAGE entity needs at least DXF version R2000 or later.')

        if 'ACAD_IMAGE_VARS' not in self.rootdict:
            self.objects.set_raster_variables(frame=0, quality=1, units=3)
        if name is None:
            name = filename
        return self.objects.add_image_def(filename, size_in_pixel, name)

    def set_raster_variables(self, frame=0, quality=1, units='m'):
        """
        Set raster variables.

        Args:
            frame: 0 = do not show image frame; 1 = show image frame
            quality: 0 = draft; 1 = high
            units: units for inserting images. This is what one drawing unit is equal to for the purpose of inserting
                   and scaling images with an associated resolution

                   'mm' = Millimeter
                   'cm' = Centimeter
                   'm' = Meter (ezdxf default)
                   'km' = Kilometer
                   'in' = Inch
                   'ft' = Foot
                   'yd' = Yard
                   'mi' = Mile
                   everything else is None

        """
        self.objects.set_raster_variables(frame=frame, quality=quality, units=units)

    def add_underlay_def(self, filename, format='ext', name=None):
        """
        Add an underlay definition to the objects section.

        Args:
            format: file format as string pdf|dwf|dgn or ext=get format from filename extension
            name: underlay name, None for an auto-generated name

        """
        if self.dxfversion < 'AC1015':
            raise DXFVersionError('The UNDERLAY entity needs at least DXF version R2000 or later.')
        if format == 'ext':
            format=filename[-3:]
        return self.objects.add_underlay_def(filename, format, name)

    def add_xref_def(self, filename, name, flags=BLK_XREF | BLK_EXTERNAL):
        """
        Add an external reference (xref) definition to the blocks section.

        Add xref to a layout by `layout.add_blockref(name, insert=(0, 0))`.

        Args:
            filename: external reference filename
            name: name of the xref block
            flags: block flags

        """
        self.blocks.new(name=name, dxfattribs={
            'flags': flags,
            'xref_path': filename
        })

    def _get_encoding(self):
        codepage = self.header.get('$DWGCODEPAGE', 'ANSI_1252')
        return toencoding(codepage)

    @staticmethod
    def new(dxfversion='AC1009'):
        from .lldxf.const import versions_supported_by_new, acad_release_to_dxf_version

        dxfversion = dxfversion.upper()
        dxfversion = acad_release_to_dxf_version.get(dxfversion, dxfversion)  # translates 'R12' -> 'AC1009'
        if dxfversion not in versions_supported_by_new:
            raise DXFVersionError("Can not create DXF drawings, unsupported DXF version '{}'.".format(dxfversion))
        finder = TemplateLoader(options.template_dir)
        stream = finder.getstream(dxfversion.upper())
        try:
            dwg = Drawing.read(stream)
        finally:
            stream.close()
        dwg._setup_metadata()
        return dwg

    def _setup_metadata(self):
        self.header['$TDCREATE'] = juliandate(datetime.now())

    @staticmethod
    def read(stream, legacy_mode=False, dxfversion=None):
        """ Open an existing drawing. """
        from .lldxf.tagger import low_level_tagger, tag_compiler

        tagger = low_level_tagger(stream)
        if legacy_mode:
            if dxfversion is not None and dxfversion <= 'AC1009':
                tagger = repair.filter_subclass_marker(tagger)
            tagger = repair.tag_reorder_layer(tagger)
        tagreader = tag_compiler(tagger)
        return Drawing(tagreader)

    def saveas(self, filename, encoding=None):
        self.filename = filename
        self.save(encoding=encoding)

    def save(self, encoding=None):
        # DXF R12, R2000, R2004 - ASCII encoding
        # DXF R2007 and newer - UTF-8 encoding
        if encoding is None:
            enc = 'utf-8' if self.dxfversion >= 'AC1021' else self.encoding
        else:  # override default encoding, for applications that handles encoding different than AutoCAD
            enc = encoding
        # in ASCII mode, unknown characters will be escaped as \U+nnnn unicode characters.
        with io.open(self.filename, mode='wt', encoding=enc, errors='dxfreplace') as fp:
            self.write(fp)

    def write(self, stream):
        from .lldxf.tagwriter import TagWriter
        if self.dxfversion == 'AC1009':
            handles = bool(self.header['$HANDLING'])
        else:
            handles = True
        if self.dxfversion > 'AC1009':
            self._register_required_classes()
        self._create_appids()
        self._update_metadata()
        tagwriter = TagWriter(stream, write_handles=handles)
        self.sections.write(tagwriter)

    def cleanup(self, groups=True):
        """
        Cleanup drawing. Call it before saving the drawing but only if necessary, the process could take a while.

        Args:
            groups (bool): removes deleted and invalid entities from groups
        """
        if groups and self.groups is not None:
            self.groups.cleanup()

    def auditor(self):
        """
        Get auditor for this drawing.

        Returns:
            Auditor() object

        """
        from ezdxf.audit.auditor import Auditor
        return Auditor(self)

    def validate(self, print_report=True):
        """
        Simple way to run an audit process.

        Args:
            print_report: print report to stdout

        Returns: True if no errors occurred else False

        """
        auditor = self.auditor()
        result = auditor.run()
        if len(result):
            if print_report:
                auditor.print_report()
            return False
        else:
            return True

    def update_class_instance_counters(self):
        if 'classes' in self.sections:
            self._register_required_classes()
            self.sections.classes.update_instance_counters()

    def _register_required_classes(self):
        register = self.sections.classes.register
        for dxftype in self.tracker.dxftypes:
            cls = self.dxffactory.get_wrapper_class(dxftype)
            if cls.CLASS is not None:
                register(cls.CLASS)

    def _update_metadata(self):
        now = datetime.now()
        self.header['$TDUPDATE'] = juliandate(now)
        self.header['$HANDSEED'] = str(self.entitydb.handles)
        self.header['$DWGCODEPAGE'] = tocodepage(self.encoding)
        self.reset_versionguid()

    def _create_appids(self):
        def create_appid_if_not_exist(name, flags=0):
            if name not in self.appids:
                self.appids.new(name, {'flags': flags})

        if 'HATCH' in self.tracker.dxftypes:
            create_appid_if_not_exist('HATCHBACKGROUNDCOLOR', 0)

    def reset_fingerprintguid(self):
        if self.dxfversion > 'AC1009':
            self.header['$FINGERPRINTGUID'] = guid()

    def reset_versionguid(self):
        if self.dxfversion > 'AC1009':
            self.header['$VERSIONGUID'] = guid()
