import bpy

from bpy.types import Panel

from ... utility import active_tool, addon, names



class HARDFLOW_PT_display_miscs(Panel):
    bl_label = 'Misc'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Hops'

    @classmethod
    def poll(cls, context):
        return active_tool().idname == 'Hops'

    def draw(self, context):
        layout = self.layout

        preference = addon.preference()

        layout.operator("hops.mirror_gizmo", text="Mirror Gizmo", icon="MOD_MIRROR")

        # self.label_row(layout.row(), preference.display, 'display_corner', label='Dot Display Corner')

    def label_row(self, row, path, prop, label=''):
        row.label(text=label if label else names[prop])
        row.prop(path, prop, text='')
