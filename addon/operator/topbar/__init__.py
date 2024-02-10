import bpy

from bpy.utils import register_class, unregister_class
from . import activate

from ... utility import view3d

classes = (
    activate.Hardflow_OT_topbar_activate,
    )


def register():

    for cls in classes:
        register_class(cls)

    view3d.add_hops_headers()


def unregister():

    for cls in classes:
        unregister_class(cls)

    view3d.remove_hops_headers()
