import bpy
from . ui import view_3d_hud
from . import extend_bpy_types
from . icons import initialize_icons_collection, unload_icons
from . mesh_check import HopsMeshCheckCollectionGroup
from . brush_previews import unregister_and_unload_brushes
from . material import HopsMaterialOptions
from . ui.hops_helper import HopsHelperOptions, HopsButtonOptions


def register_all():
    register_properties()
    view_3d_hud.register()
    extend_bpy_types.register()
    initialize_icons_collection()
    # overlay_drawer.register_callbacks()
    # register_keymap()
    # bpy.app.handlers.load_post.append(brush_load_handler)
    # bpy.app.handlers.scene_update_post.append(brush_update_handler)


def unregister_all():
    unload_icons()
    unregister_properties()
    view_3d_hud.unregister()
    extend_bpy_types.unregister()
    # overlay_drawer.unregister_callbacks()
    # unregister_keymap()
    # bpy.app.handlers.load_post.remove(brush_load_handler)
    # bpy.app.handlers.scene_update_post.remove(brush_update_handler)
    unregister_and_unload_brushes()


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

    bpy.types.WindowManager.Hard_Ops_folder_name = bpy.props.StringProperty(default=__name__.partition('.')[0])
    bpy.types.WindowManager.m_check = bpy.props.PointerProperty(type=HopsMeshCheckCollectionGroup)
    bpy.types.WindowManager.Hard_Ops_material_options = bpy.props.PointerProperty(type=HopsMaterialOptions)
    bpy.types.WindowManager.Hard_Ops_helper_options = bpy.props.PointerProperty(type=HopsHelperOptions)
    bpy.types.WindowManager.Hard_Ops_button_options = bpy.props.PointerProperty(type=HopsButtonOptions)

    bpy.types.STATUSBAR_HT_header._draw_orig = bpy.types.STATUSBAR_HT_header.draw


def unregister_properties():

    del bpy.types.WindowManager.Hard_Ops_folder_name
    del bpy.types.WindowManager.m_check
    del bpy.types.WindowManager.Hard_Ops_material_options
    del bpy.types.WindowManager.Hard_Ops_helper_options
    del bpy.types.WindowManager.Hard_Ops_button_options


def add_primitive():

    # Primitives
    if bpy.context.window_manager.choose_primitive == 'cube':
        bpy.ops.mesh.primitive_cube_add(radius=1)

    # Cylinders
    elif bpy.context.window_manager.choose_primitive == "cylinder_8":
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1, depth=2)

    elif bpy.context.window_manager.choose_primitive == 'placeholder':
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1, depth=2)

    elif bpy.context.window_manager.choose_primitive == 'cylinder_24':
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=1, depth=2)

    elif bpy.context.window_manager.choose_primitive == "cylinder_32":
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1, depth=2)

    elif bpy.context.window_manager.choose_primitive == "cylinder_64":
        bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=1, depth=2)


def create_object_to_selection(self, context):

    if not bpy.context.object:
        add_primitive()
    #        bpy.ops.object.orientationvariable(variable="LOCAL")

    elif context.object.mode == 'EDIT':
        # Duplicate the mesh, apply his transform and perform the code to add object on it
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.duplicate_move()
        bpy.context.active_object.name = "Dummy"
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        list_insert_meshes = []
        obj = bpy.context.active_object
        saved_location = bpy.context.scene.cursor.location.copy()

        bm = bmesh.new()
        bm.from_mesh(obj.data)

        selected_faces = [f for f in bm.faces if f.select]

        for face in selected_faces:
            face_location = face.calc_center_median()
            loc_world_space = obj.matrix_world * Vector(face_location)
            z = Vector((0, 0, 1))
            angle = face.normal.angle(z)
            axis = z.cross(face.normal)

            bpy.context.scene.cursor.location = loc_world_space

            add_primitive()

            bpy.ops.transform.rotate(value=angle, axis=axis)

            list_insert_meshes.append(context.active_object.name)

        bm.to_mesh(obj.data)
        bm.free()
        bpy.context.scene.cursor.location = saved_location

        # Deselect all the objects, select the dummy object and delete it
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = bpy.data.objects["Dummy"]

        bpy.context.object.select_set(True)
        bpy.ops.object.delete(use_global=False)

        # Select inserted meshes
        for obj in list_insert_meshes:
            bpy.context.view_layer.objects.active = bpy.data.objects[obj]
            bpy.data.objects[obj].select_set(True)
            if len(list_insert_meshes) > 1:
                bpy.ops.object.make_links_data(type='OBDATA') # Make link

        del(list_insert_meshes[:])
    #        bpy.ops.object.orientationvariable(variable="LOCAL")

    else:
        saved_location = bpy.context.scene.cursor.location.copy()
        bpy.ops.view3d.snap_cursor_to_selected()

        add_primitive()

        bpy.context.scene.cursor.location = saved_location
    #        bpy.ops.object.orientationvariable(variable="LOCAL")"""
