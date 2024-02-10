import bpy

class HOPS_MT_SelectGrouped(bpy.types.Menu):
    bl_idname = "HOPS_MT_SelectGrouped"
    bl_label = "Select Grouped"

    def draw(self, context):
        layout = self.layout
        layout.operator_enum("object.select_grouped", "type")
        layout.operator("hops.select_display_type", text="Display Type")
        layout.operator("hops.select_hops_status", text="Hardops Status")