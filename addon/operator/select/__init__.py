import bpy

from bpy.utils import register_class, unregister_class

from . import boolshape, type, status

classes = (
    boolshape.HOPS_OT_SELECT_boolshape,
    type.HOPS_OT_SELECT_display_type,
    status.HOPS_OT_SELECT_hops_status)


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in classes:
        unregister_class(cls)
