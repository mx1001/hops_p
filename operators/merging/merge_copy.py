import bpy
from ... utils.objects import set_active
from . parent_merge import hide_child_objects, get_prefixed_object


class CopyMergeOperator(bpy.types.Operator):
    bl_idname = "hops.copy_merge"
    bl_label = "Copy Merge"
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context):

        hide_child_objects(False)
        plane_object = context.active_object
        set_active(plane_object)
        bpy.ops.object.select_grouped(type = "CHILDREN_RECURSIVE")
        plane_object.select = True
        bpy.ops.object.duplicate_move()
        hide_child_objects(True)
        bpy.ops.object.select_all(action='DESELECT')
        set_active(plane_object)
        plane_object.select = True


        return {"FINISHED"}