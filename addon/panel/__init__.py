import bpy

from bpy.types import Panel
from bpy.utils import register_class, unregister_class

from ... icons import get_icon_id
from . import button, settings, dots


def statusicon(self, context):
    object = bpy.context.active_object
    if object is None:
        return get_icon_id("logo_gray")
    else:
        if object.hops.status == "BOOLSHAPE":
            return get_icon_id("logo_blue")
        else:
            return get_icon_id("logo_gray")


def popover(self, context):
    layout = self.layout
    row = layout.row()
    row.popover('HOPS_PT_Button', text='', icon_value=statusicon(self, context))



classes = [
    button.HOPS_PT_Button,
    dots.HARDFLOW_PT_dots,
    settings.misc.HARDFLOW_PT_display_miscs,
    settings.smartshape.HARDFLOW_PT_display_smartshapes,
    settings.modifiers.HARDFLOW_PT_display_modifiers,
    settings.HOPS_PT_settings,
    settings.HARDFLOW_PT_settings,
    settings.display.HARDFLOW_PT_display_settings,
    settings.behavior.HARDFLOW_PT_behavior_settings,
    settings.sort_last.HOPS_PT_sort_last]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_editor_menus.append(popover)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.VIEW3D_MT_editor_menus.remove(popover)
