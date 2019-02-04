import bpy
from . import overlay_drawer
from . ui import view_3d_hud
from . import extend_bpy_types
from . keymap import register_keymap, unregister_keymap
from . icons import initialize_icons_collection, unload_icons
from . add_object_to_selection import create_object_to_selection
from . mesh_check import meshCheckCollectionGroup, updateDisplayColor
from . inserts_previews import register_and_load_inserts, unregister_and_unload_inserts
from . subsets_previews import register_and_load_subsets, unregister_and_unload_subsets
from . material import material_options
from . ui.hops_helper import helper_options

def register_all():
    register_keymap()
    register_properties()
    view_3d_hud.register()
    register_and_load_inserts()
    register_and_load_subsets()
    extend_bpy_types.register()
    initialize_icons_collection()
    overlay_drawer.register_callbacks()

def unregister_all():
    unload_icons()
    unregister_keymap()
    unregister_properties()
    view_3d_hud.unregister()
    unregister_and_unload_inserts()
    unregister_and_unload_subsets()
    extend_bpy_types.unregister()
    overlay_drawer.unregister_callbacks()


def register_properties():
    bpy.types.WindowManager.choose_primitive = bpy.props.EnumProperty(
        items=(('cube', 'Cube', '', 'MESH_CUBE', 1),
               ('cylinder_8', 'Cylinder 8', '', 'MESH_CYLINDER', 2),
               ('cylinder_16', "Cylinder 16", '', 'MESH_CYLINDER', 3),
               ('cylinder_24', "Cylinder 24", '', 'MESH_CYLINDER', 4),
               ('cylinder_32', "Cylinder 32", '', 'MESH_CYLINDER', 5),
               ('cylinder_64', "Cylinder 64", '', 'MESH_CYLINDER', 6)),
               default='cylinder_24',
               update=create_object_to_selection)

    bpy.types.WindowManager.m_check = bpy.props.PointerProperty(type = meshCheckCollectionGroup)
    bpy.types.WindowManager.Hard_Ops_material_options = bpy.props.PointerProperty(type = material_options)
    bpy.types.WindowManager.Hard_Ops_helper_options = bpy.props.PointerProperty(type = helper_options)

def unregister_properties():
    m_check = bpy.context.window_manager.m_check

    if m_check.meshcheck_enabled:
        if updateDisplayColor in bpy.app.handlers:
            bpy.app.handlers.scene_update_post.remove(updateDisplayColor)

    del bpy.types.WindowManager.m_check
    del bpy.types.WindowManager.Hard_Ops_material_options
    del bpy.types.WindowManager.Hard_Ops_helper_options
