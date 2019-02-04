import os
import bpy
from bpy.props import *
from . utils.previews import load_previews_in_directory, enum_items_from_previews

preview_collection = None
subsets_directory = os.path.join(os.path.dirname(__file__), "assets", "subsets_thumbnails")


insert_on_selection_change = True

# don't insert the subset when the selection changes
def change_selected_subset(name):
    global insert_on_selection_change
    insert_on_selection_change = False
    bpy.context.window_manager.sup_preview = name
    insert_on_selection_change = True

def selected_subset_changed(self, context):
    if insert_on_selection_change:
        bpy.ops.hops.insert_subset(subset_name = context.window_manager.sup_preview)

def register_and_load_subsets():
    global preview_collection

    preview_collection = bpy.utils.previews.new()
    load_previews_in_directory(preview_collection, subsets_directory)
    enum_items = enum_items_from_previews(preview_collection)

    bpy.types.WindowManager.sup_preview = EnumProperty(
            items = enum_items, update = selected_subset_changed)

def unregister_and_unload_subsets():
    global preview_collection

    del bpy.types.WindowManager.sup_preview
    bpy.utils.previews.remove(preview_collection)
    preview_collection = None
