import bpy

from bpy.utils import register_class, unregister_class

from . import box, plane, screw, grid, spherical, misc, rope

classes = (
    misc.HOPS_OT_ADD_vertex,
    spherical.HOPS_OT_ADD_sphere,
    box.HOPS_OT_ADD_box,
    box.HOPS_OT_ADD_bbox,
    grid.HOPS_OT_ADD_grid_square,
    grid.HOPS_OT_ADD_grid_diamond,
    grid.HOPS_OT_ADD_grid_honey,
    plane.HOPS_OT_ADD_plane,
    screw.HOPS_OT_ADD_circle,
    screw.HOPS_OT_ADD_cylinder,
    screw.HOPS_OT_ADD_cone,
    screw.HOPS_OT_ADD_ring,
    screw.HOPS_OT_ADD_screw,
    rope.HOPS_OT_ADD_rope,
)


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in classes:
        unregister_class(cls)
