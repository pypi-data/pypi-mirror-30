# Created: 10.03.2011
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
version = (0, 8, 8)  # also update VERSION in setup.py
VERSION = "%d.%d.%d" % version
__version__ = VERSION
__author__ = "mozman <me@mozman.at>"
import sys
if sys.version_info[:2] < (2, 7):
    raise ImportError("Package 'ezdxf' requires Python 2.7 or later!")
import codecs
from .lldxf.encoding import dxfbackslashreplace
codecs.register_error('dxfreplace', dxfbackslashreplace)  # setup DXF unicode encoder -> '\U+nnnn'
# name space imports
from .options import options  # example: ezdxf.options.template_dir = 'c:\templates'
from .tools.importer import Importer
from .tools import transparency2float, float2transparency  # convert transparency integer values to floats 0..1
from .tools.rgb import int2rgb, rgb2int
from .tools.pattern import PATTERN
from .lldxf import const  # restore module structure ezdxf.const
from .lldxf.validator import is_dxf_file, is_dxf_stream
from .filemanagement import new, read, readfile, readzip
from .tools.standards import setup_linetypes, setup_styles
# exceptions
from .lldxf.const import DXFError  # base error exception
from .lldxf.const import DXFStructureError, DXFVersionError, DXFTableEntryError, DXFAppDataError, DXFXDataError
from .lldxf.const import DXFAttributeError, DXFValueError, DXFKeyError, DXFIndexError, DXFTypeError, DXFInvalidLayerName
