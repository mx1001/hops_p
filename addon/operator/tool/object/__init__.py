import bpy

from bpy.utils import register_class, unregister_class

from . import ctrl, grab

classes = (
    ctrl.HARDFLOWOM_OT_display)


def register():
    # for cls in classes:
    register_class(ctrl.HARDFLOWOM_OT_display)
    # register_class(grab.HOPS_OT_dots_grab)


def unregister():
    # for cls in classes:
    unregister_class(ctrl.HARDFLOWOM_OT_display)
    # unregister_class(ctrl.HOPS_OT_dots_grab)
