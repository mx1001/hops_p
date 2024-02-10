import bpy

from bpy.types import PropertyGroup
from bpy.props import PointerProperty

from . import mirror


class operators(PropertyGroup):

    mirror: PointerProperty(type=mirror.props)