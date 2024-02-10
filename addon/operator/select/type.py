import bpy
from bpy.props import EnumProperty, StringProperty


class HOPS_OT_SELECT_display_type(bpy.types.Operator):
    bl_idname = "hops.select_display_type"
    bl_label = "select by display type"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """Select By Display Type"""

    def execute(self, context):

        active_display = context.active_object.display_type
        bpy.ops.object.select_all(action='DESELECT')

        obj_to_display = [obj for obj in bpy.context.scene.objects if obj.display_type == active_display]
        for obj in obj_to_display:
            obj.select_set(True)

        return {"FINISHED"}
