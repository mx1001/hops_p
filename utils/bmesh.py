import bpy
import bmesh

def selectSmoothEdges(self, me):

    bm = bmesh.from_edit_mesh(me)
    for e in bm.edges:
        if not e.smooth:
            e.select = True