# Purpose: classified tags
# Created: 30.04.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <me@mozman.at>"

from .tags import Tags,  DXFTag, NONE_TAG
from .const import DXFStructureError, DXFValueError, DXFKeyError
from .const import APP_DATA_MARKER, SUBCLASS_MARKER, XDATA_MARKER
from ..tools.c23 import isstring
from .tagger import internal_tag_compiler


class ExtendedTags(object):
    """ Manage Subclasses, AppData and Extended Data """
    __slots__ = ('subclasses', 'appdata', 'xdata', 'link')

    def __init__(self, iterable=None):
        if isstring(iterable):
            raise DXFValueError("use ExtendedTags.from_text() to create tags from a string.")

        self.appdata = list()  # code == 102, keys are "{<arbitrary name>", values are Tags()
        self.subclasses = list()  # code == 100, keys are "subclassname", values are Tags()
        self.xdata = list()  # code >= 1000, keys are "APPNAME", values are Tags()
        self.link = None  # link (as handle) to following entities like INSERT -> ATTRIB and POLYLINE -> VERTEX
        if iterable is not None:
            self._setup(iterable)

    def __copy__(self):
        """
        Shallow copy - linked entities are not duplicated!

        ExtendedTags() knows nothing about the entity database, and has no access to, so it is not possible for
        ExtendedTags() to do a deep copy, by also copying linked entities (VERTEX, ATTRIB, SEQEND).
        To do a deep copy you have to go one level up and use DXFEntity.copy()

        """
        def copy(tag_lists):
            return [tags.clone() for tags in tag_lists]

        clone = self.__class__()
        clone.appdata = copy(self.appdata)
        clone.subclasses = copy(self.subclasses)
        clone.xdata = copy(self.xdata)
        clone.link = self.link  # important for dxf importer!
        return clone
    clone = __copy__

    def __getitem__(self, index):
        return self.noclass[0]

    @property
    def noclass(self):
        return self.subclasses[0]

    def get_handle(self):
        return self.noclass.get_handle()

    def dxftype(self):
        return self.noclass[0].value

    def replace_handle(self, handle):
        self.noclass.replace_handle(handle)

    def _setup(self, iterable):
        tagstream = iter(iterable)

        def isappdata(tag):
            return tag.code == APP_DATA_MARKER and tag.value.startswith('{')

        def collect_subclass(starttag):
            """
            A subclass can contain appdata, but not xdata, ends with
            SUBCLASSMARKER or XDATACODE.

            """
            data = Tags() if starttag is None else Tags([starttag])
            try:
                while True:
                    tag = next(tagstream)
                    if isappdata(tag):
                        app_data_pos = len(self.appdata)
                        data.append(DXFTag(tag.code, app_data_pos))
                        collect_appdata(tag)
                    elif tag.code in (SUBCLASS_MARKER, XDATA_MARKER):
                        self.subclasses.append(data)
                        return tag
                    else:
                        data.append(tag)
            except StopIteration:
                pass
            self.subclasses.append(data)
            return NONE_TAG

        def collect_appdata(starttag):
            """
            Appdata, cannot contain xdata or subclasses.

            """
            data = Tags([starttag])
            closing_strings = ('}', starttag.value[1:] + '}')  # alternative closing tag 'APPID}'
            while True:
                try:
                    tag = next(tagstream)
                except StopIteration:
                    raise DXFStructureError("Missing closing (102, '}') tag for appdata structure.")
                data.append(tag)
                if (tag.code == APP_DATA_MARKER) and (tag.value in closing_strings):
                    break
                    # every other (102, ) tag is treated as usual tag
            self.appdata.append(data)

        def collect_xdata(starttag):
            """
            Xdata is always at the end of the entity and can not contain appdata or subclasses

            """
            data = Tags([starttag])
            try:
                while True:
                    tag = next(tagstream)
                    if tag.code == XDATA_MARKER:
                        self.xdata.append(data)
                        return tag
                    else:
                        data.append(tag)
            except StopIteration:
                pass
            self.xdata.append(data)
            return NONE_TAG

        tag = collect_subclass(None)  # preceding tags without a subclass
        while tag.code == SUBCLASS_MARKER:
            tag = collect_subclass(tag)
        while tag.code == XDATA_MARKER:
            tag = collect_xdata(tag)

        if tag is not NONE_TAG:
            raise DXFStructureError("Unexpected tag '%r' at end of entity." % tag)

    def __iter__(self):
        for subclass in self.subclasses:
            for tag in subclass:
                if tag.code == APP_DATA_MARKER and isinstance(tag.value, int):
                    for subtag in self.appdata[tag.value]:
                        yield subtag
                else:
                    yield tag

        for xdata in self.xdata:
            for tag in xdata:
                yield tag

    def get_subclass(self, name, pos=0):
        getpos = 0
        for subclass in self.subclasses:
            if len(subclass) and subclass[0].value == name and getpos >= pos:
                return subclass
            getpos += 1
        raise DXFKeyError("Subclass '%s' does not exist." % name)

    def has_xdata(self, appid):
        return any(xdata[0].value == appid for xdata in self.xdata)

    def get_xdata(self, appid):
        for xdata in self.xdata:
            if xdata[0].value == appid:
                return xdata
        raise DXFValueError("No extended data for APPID '%s'" % appid)

    def set_xdata(self, appid, tags):
        xdata = self.get_xdata(appid)
        xdata[1:] = (DXFTag(t[0], t[1]) for t in tags)

    def new_xdata(self, appid, tags=None):
        """
        Append a new xdata block.

        Assumes that no xdata block with the same appid already exists::

            try:
                xdata = tags.get_xdata('EZDXF')
            except ValueError:
                xdata = tags.new_xdata('EZDXF')
        """
        xtags = Tags([DXFTag(XDATA_MARKER, appid)])
        if tags is not None:
            xtags.extend(DXFTag(t[0], t[1]) for t in tags)
        self.xdata.append(xtags)
        return xtags

    def has_app_data(self, appid):
        return any(appdata[0].value == appid for appdata in self.appdata)

    def get_app_data(self, appid):
        """
        Get app data including first and last marker tag.

        """
        for appdata in self.appdata:
            if appdata[0].value == appid:
                return appdata
        raise DXFValueError("Application defined group '%s' does not exist." % appid)

    def get_app_data_content(self, appid):
        """
        Get app data without first and last marker tag.

        """
        return Tags(self.get_app_data(appid)[1:-1])

    def set_app_data_content(self, appid, tags):
        app_data = self.get_app_data(appid)
        app_data[1:-1] = tags

    def new_app_data(self, appid, tags=None, subclass_name=None):
        """
        Append a new app data block to subclass *subclass_name*.

        Assumes that no app data block with the same appid already exists::

            try:
                app_data = tags.get_app_data('{ACAD_REACTORS', tags)
            except ValueError:
                app_data = tags.new_app_data('{ACAD_REACTORS', tags)

        """
        if not appid.startswith('{'):
            raise DXFValueError("App data id has to start with '{'.")

        app_tags = Tags([
            DXFTag(APP_DATA_MARKER, appid),
            DXFTag(APP_DATA_MARKER, '}'),
        ])
        if tags is not None:
            app_tags[1:1] = tags

        if subclass_name is None:
            subclass = self.noclass
        else:
            subclass = self.get_subclass(subclass_name, 1)  # raises KeyError, if not exists
        app_data_pos = len(self.appdata)
        subclass.append(DXFTag(APP_DATA_MARKER, app_data_pos))
        self.appdata.append(app_tags)
        return app_tags

    @classmethod
    def from_text(cls, text):
        return cls(internal_tag_compiler(text))


LINKED_ENTITIES = {
    'INSERT': 'ATTRIB',
    'POLYLINE': 'VERTEX'
}


def get_xtags_linker():
    class PersistentVars(object):  # Python 2.7 has no nonlocal statement
        def __init__(self):
            self.prev = None
            self.expected = ""

    def xtags_linker(tags):
        handle = tags.get_handle()

        def attribs_follow():
            try:
                ref_tags = tags.get_subclass('AcDbBlockReference')
            except DXFKeyError:
                return False
            else:
                return bool(ref_tags.get_first_value(66, 0))

        dxftype = tags.dxftype()
        are_linked_tags = False  # INSERT & POLYLINE are not linked tags, they are stored in the entity space
        if vars.prev is not None:
            are_linked_tags = True  # VERTEX, ATTRIB & SEQEND are linked tags, they are NOT stored in the entity space
            if dxftype == 'SEQEND':
                vars.prev.link = handle
                vars.prev = None
            # check for valid DXF structure just VERTEX follows POLYLINE and just ATTRIB follows INSERT
            elif dxftype == vars.expected:
                vars.prev.link = handle
                vars.prev = tags
            else:
                raise DXFStructureError("expected DXF entity {} or SEQEND".format(dxftype))
        elif dxftype in ('INSERT', 'POLYLINE'):  # only these two DXF types have this special linked structure
            if dxftype == 'INSERT' and not attribs_follow():
                # INSERT must not have following ATTRIBS, ATTRIB can be a stand alone entity:
                #   INSERT with no ATTRIBS, attribs_follow == 0
                #   ATTRIB as stand alone entity
                #   ....
                #   INSERT with ATTRIBS, attribs_follow == 1
                #   ATTRIB as connected entity
                #   SEQEND
                #
                # Therefor a ATTRIB following an INSERT doesn't mean that these entities are connected.
                pass
            else:
                vars.prev = tags
                vars.expected = LINKED_ENTITIES[dxftype]
        return are_linked_tags  # caller should know, if *tags* should be stored in the entity space or not

    vars = PersistentVars()
    return xtags_linker
