import bpy

from bpy.utils import register_class, unregister_class

from . import ctrl

classes = (
    ctrl.HARDFLOW_OT_display)


def register():
    # for cls in classes:
    register_class(ctrl.HARDFLOW_OT_display)


def unregister():
    # for cls in classes:
    unregister_class(ctrl.HARDFLOW_OT_display)
