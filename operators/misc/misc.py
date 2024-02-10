import bpy

from bpy.props import FloatProperty

class HOPS_OT_EnableTopbar(bpy.types.Operator):
    bl_idname = "hops.show_topbar"
    bl_label = "Show Blender Topbar"
    bl_description = "Show Blender topbar"
    bl_options = {"REGISTER"}

    def execute(self, context):
        bpy.context.space_data.show_region_tool_header = True
        return {"FINISHED"}
