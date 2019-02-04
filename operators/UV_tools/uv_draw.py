import bpy
import bmesh
from ... utils.objects import obj_quads_to_tris

class HopsDrawUV(bpy.types.Operator):
        '''Tooltip'''
        bl_description = "draw uv in 3d view"
        bl_idname = "hops.draw_uv"
        bl_label = "Draw UV"
        bl_options = {'REGISTER', 'UNDO'}

        def execute(self, context):
        	
            try :
                hops_draw_uv()
            except RuntimeError :
                bpy.ops.ed.undo()

            return {"FINISHED"}

def hops_draw_uv():

    bpy.ops.ed.undo_push()
    bpy.ops.ed.undo_push()
    obj_quads_to_tris()
    bpy.ops.hops.draw_object_uvs()
    bpy.ops.ed.undo()