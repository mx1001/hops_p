import bpy
from bgl import *
from bpy.props import *

class RemoveMergeOperator(bpy.types.Operator):
    bl_idname = "hops.remove_merge"
    bl_label = "Remove Merge"
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context):
        remove_boolean()

        return {"FINISHED"}


def remove_boolean():

    objects = bpy.data.objects
    for obj in objects:
        if obj.type == "MESH":
            modifiers = obj.modifiers
            for mod in modifiers:
                if mod.type == 'BOOLEAN':
                    bpy.context.scene.objects.active = obj
                    bpy.ops.object.modifier_remove(modifier=mod.name)

