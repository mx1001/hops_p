import os
import bpy
from bpy.props import *
from . utils.previews import load_previews_in_directory, enum_items_from_previews

preview_collection = None
inserts_directory = os.path.join(os.path.dirname(__file__), "assets", "inserts_thumbnails")

insert_on_selection_change = True

# don't insert the insert when the selection changes
def change_selected_insert(name):
    global insert_on_selection_change
    insert_on_selection_change = False
    bpy.context.window_manager.Hard_Ops_previews = name
    insert_on_selection_change = True

def selected_asset_preview_changed(self, context):
    if insert_on_selection_change:
        bpy.ops.hops.insert_asset(asset_name = context.window_manager.Hard_Ops_previews)

def register_and_load_inserts():
    global preview_collection

    preview_collection = bpy.utils.previews.new()
    load_previews_in_directory(preview_collection, inserts_directory)
    enum_items = enum_items_from_previews(preview_collection)

    bpy.types.WindowManager.Hard_Ops_previews = EnumProperty(
            items = enum_items, update = selected_asset_preview_changed)

def unregister_and_unload_inserts():
    global preview_collection

    del bpy.types.WindowManager.Hard_Ops_previews
    bpy.utils.previews.remove(preview_collection)
    preview_collection = None
