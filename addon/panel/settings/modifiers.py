import bpy

from bpy.types import Panel

from ... topbar import modifier_operators
from ... utility import active_tool, addon, names
from .... icons import get_icon_id

class HARDFLOW_PT_display_modifiers(Panel):
    bl_label = 'Modifiers'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Hops'

    @classmethod
    def poll(cls, context):
        return active_tool().idname == 'Hops'

    def draw(self, context):
        layout = self.layout

        modifier_operators(context, layout, labels=True)
