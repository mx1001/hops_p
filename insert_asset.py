import os
import bpy
import bmesh
from bpy.props import *
from mathutils import Matrix
from . overlay_drawer import show_text_overlay
from . utils.blender_ui import open_error_message
from . utils.libraries import load_object_from_other_file
from . utils.operations import invoke_individual_resizing
from . utils.objects import (link_object_to_scene,
                             link_objects_to_scene,
                             link_objects_to_group,
                             get_or_create_group,
                             only_select,
                             set_active)


class InsertAsset(bpy.types.Operator):
    bl_idname = "hops.insert_asset"
    bl_label = "Insert Asset"

    asset_name = StringProperty()

    def execute(self, context):
        insert_asset(self.asset_name)
        invoke_individual_resizing()
        context.area.tag_redraw()
        return {"FINISHED"}


current_path = os.path.dirname(os.path.realpath(__file__))
assets_filepath = os.path.join(current_path, "assets", "inserts.blend")

def insert_asset(object_name):
    asset = load_asset_object(object_name)
    if asset is None: return

    group_name = "Inserts"
    target = bpy.context.active_object

    mode = getattr(target, "mode", "OBJECT")
    if mode == "OBJECT":
        link_object_to_scene(asset)
        place_object_at_3d_cursor(asset)
        set_active(asset, only_select = True)
        group = get_or_create_group(group_name)
        group.objects.link(asset)

    if mode == "EDIT":
        instances = place_instances_at_selected_faces(source = asset, target = target)
        bpy.ops.object.mode_set(mode = "OBJECT")
        group = get_or_create_group(group_name)
        link_objects_to_group(group, instances)
        link_objects_to_scene(instances)
        only_select(instances)

    message = "Insert(s) added to '{}' group: '{}'".format(group_name, object_name)
    show_text_overlay(text = message, font_size = 13, color = (1, 1, 1),
                      stay_time = 1, fadeout_time = 1)

def load_asset_object(object_name):
    try:
        return load_object_from_other_file(assets_filepath, object_name)
    except NameError:
        open_error_message("The object '{}' does not exist in the inserts.blend file".format(object_name))
    except OSError:
        open_error_message("The file does not exist: {}".format(assets_filepath))

def place_object_at_3d_cursor(object):
    object.location = bpy.context.space_data.cursor_location

def place_instances_at_selected_faces(source, target):
    instances = []

    bm = bmesh.from_edit_mesh(target.data)
    for face in bm.faces:
        if face.select:
            instance = new_transformed_instance(source, target, face)
            instances.append(instance)

    return instances

def new_transformed_instance(source, target, face):
    center = face.calc_center_median()
    rotation = face.normal.to_track_quat("Z", "X")
    transformation = target.matrix_world * Matrix.Translation(center) * rotation.to_matrix().to_4x4()

    instance = new_instance(source)
    instance.matrix_world = transformation
    return instance

def new_instance(source):
    instance = source.copy()
    instance.show_name = False
    return instance
