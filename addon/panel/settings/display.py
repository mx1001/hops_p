import bpy

from bpy.types import Panel

from ... utility import addon, names


class HARDFLOW_PT_display_settings(Panel):
    bl_label = 'Display'
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

        self.label_row(layout.row(), preference.display, 'dot_size', label='Dot Size')
        self.label_row(layout.row(), preference.display, 'dot_detect', label='Detect Size')
        self.label_row(layout.row(), preference.display, 'dot_side_offset', label='Dot Offset')
        self.label_row(layout.row(), preference.display, 'dot_corner_offset', label='Corner Offset')
        self.label_row(layout.row(), preference.property, 'dots_snap', label='Display')
        layout.separator()
        self.label_row(layout.row(), preference.display, 'dot_boolshape_fade_distance', label='Fade Distance')
        layout.separator()
        self.label_row(layout.row(), preference.display, 'display_smartshape', label='Display Smartshape Row')
        self.label_row(layout.row(), preference.display, 'display_modifiers', label='Display Modifiers Row')
        self.label_row(layout.row(), preference.display, 'display_misc', label='Display Misc Row')
        layout.separator()
        self.label_row(layout.row(), preference.color, 'Bool_Dots_Text', label='Display Text for Boolean Dots')
        self.label_row(layout.row(), preference.display, 'display_text', label='Display Text in Viewport')
        self.label_row(layout.row(), preference.display, 'display_text_size', label='Display Text Size')
        self.label_row(layout.row(), preference.display, 'display_text_size_for_dots', label='Display Dots Text Size')
        layout.separator()
        self.label_row(layout.row(), preference.display, 'use_label_factor', label='Fix Label Size')

        # self.label_row(layout.row(), preference.display, 'display_corner', label='Dot Display Corner')

    def label_row(self, row, path, prop, label=''):
        row.label(text=label if label else names[prop])
        row.prop(path, prop, text='')
