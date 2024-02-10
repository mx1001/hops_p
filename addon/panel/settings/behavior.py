import bpy

from bpy.types import Panel

from ... utility import active_tool, addon, names


class HARDFLOW_PT_behavior_settings(Panel):
    bl_label = 'Behavior'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Hardflow'
    bl_parent_id = 'HOPS_PT_settings'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.region.type == 'UI'

    def draw(self, context):
        layout = self.layout

        preference = addon.preference()

        option = None
        for tool in context.workspace.tools:
            if tool.idname == 'Hardflow':
                self.label_row(layout.row(), preference.behavior, 'quick_execute')

            elif tool.idname == 'Hops':
                self.label_row(layout.row(), preference.behavior, 'display_gizmo', label='Hide gizmo on Ctrl')
                self.label_row(layout.row(), preference.behavior, 'display_dots', label='Display dots on Ctrl')
                self.label_row(layout.row(), preference.behavior, 'display_operators', label='Display Operators on Ctrl')
                self.label_row(layout.row(), preference.behavior, 'display_boolshapes', label='Display booleans on Ctrl')
                self.label_row(layout.row(), preference.behavior, 'display_boolshapes_for_all', label='Display booleans for All Objects')
                self.label_row(layout.row(), preference.behavior, 'add_mirror_to_boolshapes', label='Add mirror to boolshapes')
                self.label_row(layout.row(), preference.behavior, 'add_WN_to_boolshapes', label='Add WN to boolshapes')
                self.label_row(layout.row(), preference.behavior, 'cursor_boolshapes', label='Orient boolshapes to cursor')

    def label_row(self, row, path, prop, label=''):
        row.label(text=label if label else names[prop])
        row.prop(path, prop, text='')
