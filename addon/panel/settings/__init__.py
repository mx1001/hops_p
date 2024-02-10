import bpy

from bpy.types import Panel

from . import behavior, display, modifiers, smartshape, misc, sort_last
from ... utility import active_tool, addon, names


class HOPS_PT_settings(Panel):
    bl_label = 'Settings'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Hops'


    @classmethod
    def poll(cls, context):
        return active_tool().idname == 'Hops'

    def draw(self, context):
        layout = self.layout

        # wm = context.window_manager
        preference = addon.preference()

        if self.is_popover:
            self.header_row(layout.row(align=True), 'display', label='Display')
            if preference.expand.display:
                display.HARDFLOW_PT_display_settings.draw(self, context)

            self.header_row(layout.row(align=True), 'behavior', label='Behavior')
            if preference.expand.behavior:
                behavior.HARDFLOW_PT_behavior_settings.draw(self, context)


    def header_row(self, row, prop, label='', emboss=False):
        preference = addon.preference()
        icon = 'DISCLOSURE_TRI_RIGHT' if not getattr(preference.expand, prop) else 'DISCLOSURE_TRI_DOWN'
        row.alignment = 'LEFT'
        row.prop(preference.expand, prop, text='', emboss=emboss)

        sub = row.row(align=True)
        sub.scale_x = 0.25
        sub.prop(preference.expand, prop, text='', icon=icon, emboss=emboss)
        row.prop(preference.expand, prop, text=F'{label}', emboss=emboss)

        sub = row.row(align=True)
        sub.scale_x = 0.75
        sub.prop(preference.expand, prop, text=' ', icon='BLANK1', emboss=emboss)


    def label_row(self, row, path, prop, label=''):
        row.label(text=label if label else names[prop])
        row.prop(path, prop, text='')


class HARDFLOW_PT_settings(Panel):
    bl_label = 'Settings'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Hardflow'


    @classmethod
    def poll(cls, context):
        return active_tool().idname == 'Hardflow'

    def draw(self, context):
        layout = self.layout

        # wm = context.window_manager
        preference = addon.preference()

        if self.is_popover:
            self.header_row(layout.row(align=True), 'display', label='Display')
            if preference.expand.display:
                display.HARDFLOW_PT_display_settings.draw(self, context)

            self.header_row(layout.row(align=True), 'behavior', label='Behavior')
            if preference.expand.behavior:
                behavior.HARDFLOW_PT_behavior_settings.draw(self, context)

    def header_row(self, row, prop, label='', emboss=False):
        preference = addon.preference()
        icon = 'DISCLOSURE_TRI_RIGHT' if not getattr(preference.expand, prop) else 'DISCLOSURE_TRI_DOWN'
        row.alignment = 'LEFT'
        row.prop(preference.expand, prop, text='', emboss=emboss)

        sub = row.row(align=True)
        sub.scale_x = 0.25
        sub.prop(preference.expand, prop, text='', icon=icon, emboss=emboss)
        row.prop(preference.expand, prop, text=F'{label}', emboss=emboss)

        sub = row.row(align=True)
        sub.scale_x = 0.75
        sub.prop(preference.expand, prop, text=' ', icon='BLANK1', emboss=emboss)


    def label_row(self, row, path, prop, label=''):
        row.label(text=label if label else names[prop])
        row.prop(path, prop, text='')
