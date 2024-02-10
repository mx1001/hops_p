import bpy

from bpy.types import PropertyGroup, Object, Mesh
from bpy.props import *


class Points(PropertyGroup):
    location3d: FloatVectorProperty()
    location2d: FloatVectorProperty(size=2)
    alpha: FloatProperty()
    highlight: BoolProperty()
    type: StringProperty()
    index: IntProperty()
    display: BoolProperty()
    color: StringProperty()
    description: StringProperty()


class option(PropertyGroup):
    points: CollectionProperty(type=Points)
    mod: StringProperty()
    description: StringProperty()
