import bpy

from bpy.types import PropertyGroup
from bpy.props import BoolProperty


class hardflow(PropertyGroup):

    display: BoolProperty(
        name = 'Expand Display',
        default = False)

    behavior: BoolProperty(
        name = 'Expand Behavior',
        default = False)


