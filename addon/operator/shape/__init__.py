import bpy

from bpy.utils import register_class, unregister_class

from . import sharpen

classes = (
    sharpen.HOPS_OT_Sharpen
)


def register():
    # for cls in classes:
    register_class(sharpen.HOPS_OT_Sharpen)


def unregister():
    # for cls in classes:
    unregister_class(sharpen.HOPS_OT_Sharpen)
