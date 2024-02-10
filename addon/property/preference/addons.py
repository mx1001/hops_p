import bpy
import textwrap

from bpy.types import PropertyGroup
from bpy.props import BoolProperty, IntProperty

from ... utility import names, screen
from .... ui.addon_checker import draw_addon_diagnostics


def draw(preference, context, layout):

    draw_addon_diagnostics(layout, columns=4)
