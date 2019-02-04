import os
import bpy
from bpy.props import *
from . overlay_drawer import show_text_overlay
from . preferences import tool_overlays_enabled, Hops_display_time, Hops_fadeout_time
from . utils.blender_ui import open_error_message
from . utils.libraries import load_group_from_other_file
from . utils.objects import link_objects_to_scene, deselect_all, set_active

class InsertSubset(bpy.types.Operator):
    bl_idname = "hops.insert_subset"
    bl_label = "Insert Subset"

    subset_name = StringProperty()

    def execute(self, context):
        insert_subset(self.subset_name)
        context.area.tag_redraw()
        return {"FINISHED"}


current_path = os.path.dirname(os.path.realpath(__file__))
assets_filepath = os.path.join(current_path, "assets", "subsets.blend")

def insert_subset(group_name):
    group = insert_subset_group(group_name)
    if group is None: return

    if bpy.context.active_object is not None:
        bpy.ops.object.mode_set(mode = "OBJECT")

    only_select_ap_object(group)
    setup_tool_settings(bpy.context.scene)

    if tool_overlays_enabled():
        text = "Subset Insert Added: '{}' - Snap With Ctrl".format(group_name)
        show_text_overlay(text = text, font_size = 16, stay_time = Hops_display_time(), fadeout_time = Hops_fadeout_time())

def insert_subset_group(group_name):
    try:
        group = load_group_from_other_file(assets_filepath, group_name)
        link_objects_to_scene(group.objects)
        return group
    except NameError:
        open_error_message("The group '{}' does not exist in the assets file".format(group_name))
    except OSError:
        open_error_message("The file does not exist: {}".format(assets_filepath))

def setup_tool_settings(scene):
    settings = scene.tool_settings
    settings.snap_element = 'FACE'
    settings.use_snap_align_rotation = True
    settings.use_snap_project = True

def only_select_ap_object(group):
    deselect_all()
    for object in group.objects:
        if object.name.startswith("AP"): set_active(object, select = True)
