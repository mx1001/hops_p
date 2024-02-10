import bpy
from bpy.props import EnumProperty, StringProperty


class HOPS_OT_SELECT_hops_status(bpy.types.Operator):
    bl_idname = "hops.select_hops_status"
    bl_label = "select by Hardops Status"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """Select By Hardops Status"""

    def execute(self, context):

        active_status = context.active_object.hops.status
        bpy.ops.object.select_all(action='DESELECT')

        obj_to_display = [obj for obj in bpy.context.scene.objects if obj.hops.status == active_status]
        for obj in obj_to_display:
            obj.select_set(True)

        return {"FINISHED"}
