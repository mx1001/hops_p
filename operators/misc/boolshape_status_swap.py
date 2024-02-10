import bpy
from bpy.props import BoolProperty


class HOPS_OT_BoolshapeStatusSwap(bpy.types.Operator):
    bl_idname = "hops.boolshape_status_swap"
    bl_label = "Hops Boolshape Status Swap"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """Set Boolshape Status"""

    @classmethod
    def poll(cls, context):
        object = context.active_object
        if object is None: return False
        return object.type == "MESH" and object.mode == "OBJECT"

    def execute(self, context):
        selected = context.selected_objects

        for obj in selected:
            obj.hops.status = "BOOLSHAPE"

        context.area.tag_redraw()

        return {'FINISHED'}
