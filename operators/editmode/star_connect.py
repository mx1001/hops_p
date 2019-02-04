import bpy
import bmesh

class HopsStarConnect(bpy.types.Operator):
    bl_idname = "hops.star_connect"
    bl_label = "Hops Star Connect"
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context):

        #bmesh version of MACHIN3's star connect 

        obj = bpy.context.object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)

        #check if at least 2 verts are selected
        selected = [v.index for v in bm.verts if v.select]
        if len(selected) < 2:
            return {'FINISHED'}

        bpy.ops.mesh.select_mode(type="VERT")

        # uses active vert from history (should be faster) or last selected if it doesn't exist
        try: 
            av = bm.select_history.active
            av.select = False
        except:
            lastvert = selected[-1]
            av = bm.verts[lastvert]
            av.select = False

        verts = []

        # conects all selected verts to active one
        for v in bm.verts:
            if v.select:
                verts.append(v)
                verts.append(av)
                bm.select_history.add(av)
                bmesh.ops.connect_verts(bm, verts=verts)
                verts[:] = []

        av.select = True

        bmesh.update_edit_mesh(me)

        return {'FINISHED'}
