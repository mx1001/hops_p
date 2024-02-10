
import bpy

#Insert Object
class HOPS_MT_Tool_grid(bpy.types.Menu):
    bl_idname = "HOPS_MT_Tool_grid"
    bl_label = "Grid Objects"

    def draw(self, context):
        layout = self.layout

        layout.operator("hops.add_grid_square", text="Square", icon="MESH_GRID")
        layout.operator("hops.add_grid_diamond", text="Diamond", icon='MESH_GRID')
        layout.operator("hops.add_grid_honey", text="Honeycomb", icon='MESH_GRID')
