import bpy
from bpy.props import *
from .. utils.blender_ui import get_dpi_factor
from .. subsets_previews import change_selected_subset
from .. inserts_previews import change_selected_insert

class AssetScrollerWindow(bpy.types.Operator):
    bl_idname = "view3d.asset_scroller_window"
    bl_label = "Asset Cycle"
    bl_description = ""
    bl_options = {"REGISTER"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 150 * get_dpi_factor())

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout

        # Subsets

        col = layout.column()
        col.template_icon_view(context.window_manager, "sup_preview")

        row = col.row(align = True)
        props = row.operator("hops.move_assets_preview_selection", icon = "TRIA_LEFT", text = "")
        props.property_name = "sup_preview"
        props.move_amount = -1

        row.operator("hops.insert_subset", text = "Insert").subset_name = context.window_manager.sup_preview

        props = row.operator("hops.move_assets_preview_selection", icon = "TRIA_RIGHT", text = "")
        props.property_name = "sup_preview"
        props.move_amount = 1

        # Inserts

        col = layout.column()
        col.template_icon_view(context.window_manager, "Hard_Ops_previews")

        row = col.row(align = True)
        props = row.operator("hops.move_assets_preview_selection", icon = "TRIA_LEFT", text = "")
        props.property_name = "Hard_Ops_previews"
        props.move_amount = -1

        row.operator("hops.insert_asset", text = "Insert").asset_name = context.window_manager.Hard_Ops_previews

        props = row.operator("hops.move_assets_preview_selection", icon = "TRIA_RIGHT", text = "")
        props.property_name = "Hard_Ops_previews"
        props.move_amount = 1

    def execute(self, context):
        return {"FINISHED"}

class MoveAssetsPreviewSelection(bpy.types.Operator):
    bl_idname = "hops.move_assets_preview_selection"
    bl_label = "Select Next"

    property_name = StringProperty()
    move_amount = IntProperty()

    def execute(self, context):
        wm = context.window_manager
        current_item = getattr(wm, self.property_name)
        enum_items = [item.identifier for item in wm.bl_rna.properties[self.property_name].enum_items]
        new_index = (enum_items.index(current_item) + self.move_amount) % len(enum_items)
        self.set_new_item(enum_items[new_index])
        return {"FINISHED"}

    def set_new_item(self, item):
        if self.property_name == "sup_preview":
            change_selected_subset(item)
        if self.property_name == "Hard_Ops_previews":
            change_selected_insert(item)
