import bpy

from bpy.utils import register_class, unregister_class

from . import add, array, bevel, screw, solidify, displace, dots, wireframe, deform, profile

classes = (
    add.HOPS_OT_ADD_MOD_split,
    add.HOPS_OT_ADD_MOD_array,
    add.HOPS_OT_ADD_MOD_displace,
    add.HOPS_OT_ADD_MOD_screw,
    add.HOPS_OT_ADD_MOD_extrude,
    add.HOPS_OT_ADD_MOD_solidify,
    add.HOPS_OT_ADD_MOD_decimate,
    add.HOPS_OT_ADD_MOD_bevel,
    add.HOPS_OT_ADD_MOD_bevel_corners,
    add.HOPS_OT_ADD_MOD_bevel_chamfer,
    add.HOPS_OT_ADD_MOD_wireframe,
    add.HOPS_OT_ADD_MOD_triangulate,
    add.HOPS_OT_ADD_MOD_subsurf,
    add.HOPS_OT_ADD_MOD_lattice,
    add.HOPS_OT_ADD_MOD_deform,
    add.HOPS_OT_ADD_MOD_circle_array,
    add.HOPS_OT_ADD_MOD_curve,
    add.HOPS_OT_ADD_MOD_weld,
    bevel.HOPS_OT_MODS_bevel,
    bevel.HOPS_OT_MODS_bevel_step,
    screw.HOPS_OT_MODS_screw,
    screw.HOPS_OT_MODS_screw_step,
    wireframe.HOPS_OT_MODS_wireframe,
    solidify.HOPS_OT_MODS_solidify,
    dots.HARDFLOW_OT_dot_settings,
    displace.HOPS_OT_MODS_displace,
    deform.HOPS_OT_MODS_deform,
    array.HOPS_OT_MODS_array,
    array.HOPS_OT_MODS_array_step,
    profile.SaveBevelProfile,
    profile.LoadBevelProfile,
)


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in classes:
        unregister_class(cls)
