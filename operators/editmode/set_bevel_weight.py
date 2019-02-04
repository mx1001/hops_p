import bpy
import bmesh
from bpy.props import *


class HopsSetEditSharpen(bpy.types.Operator):
    bl_idname = "hops.set_edit_sharpen"
    bl_label = "Hops Set Sharpen"
    bl_options = {'REGISTER', 'UNDO'} 


    dont_affect_bevel = BoolProperty(name = "Don't affect bevel weight",
                              description = "Don't affect bevel weight that was set manually",
                              default = False)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.prop(self, "dont_affect_bevel")
            

    def execute(self, context):


        obj = bpy.context.object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        bw = bm.edges.layers.bevel_weight.verify()
        cr = bm.edges.layers.crease.verify()
        me.show_edge_bevel_weight = True
        me.show_edge_crease = True
        me.show_edge_sharp = True
   
        selected = [ e for e in bm.edges if e.select ]


        if any(e[bw] == 1 for e in selected ):
            for e in selected:
                if self.dont_affect_bevel:
                    if e[bw] == 1:
                        e[bw] = 0
                    e[cr] = 0
                    e.smooth = True   
                else:    
                    e[bw] = 0
                    e[cr] = 0
                    e.smooth = True
        else:
            for e in selected:
                if self.dont_affect_bevel:
                    if e[bw] == 0:
                        e[bw] = 1
                    e[cr] = 1
                    e.smooth = False
                else:
                    e[bw] = 1
                    e[cr] = 1
                    e.smooth = False
      

        bmesh.update_edit_mesh(me)

        return {'FINISHED'}