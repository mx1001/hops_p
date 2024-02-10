import bpy

from bpy.utils import register_class, unregister_class

from . import grid, array

classes = (
    grid.HOPS_MT_Tool_grid,
    array.HOPS_MT_Tool_array)


def register():
    # for cls in classes:
    register_class(grid.HOPS_MT_Tool_grid)
    register_class(array.HOPS_MT_Tool_array)


def unregister():
    # for cls in classes:
    unregister_class(grid.HOPS_MT_Tool_grid)
    unregister_class(array.HOPS_MT_Tool_array)
