import bpy
from bpy.types import Panel

from ... preferences import get_preferences


class HOPS_PT_operators(Panel):
    bl_label = 'Operators'
    bl_space_type = 'VIEW_3D'
    bl_category = 'HardOps'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        preference = get_preferences().property

        column = layout.column(align=True)
