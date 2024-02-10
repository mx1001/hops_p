import bpy
from bpy.props import FloatProperty, BoolProperty
from ... preferences import get_preferences


class HOPS_OT_VoxelizerOperator(bpy.types.Operator):
    bl_idname = "view3d.voxelizer"
    bl_label = "Object Mode Voxelization"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Voxelizes Objects From Object Mode"

    # voxsize: FloatProperty(name="Vox Size", description="Size Of Voxelization", default=0.1, min=0.01, max=10)

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def draw(self, context):
        layout = self.layout

        data = context.active_object.data
        layout.prop(data, 'remesh_voxel_size', text='')

        # box = layout.box()

        # box.prop(self, 'voxsize', text="Voxelization Size")

    def execute(self, context):
        data = context.active_object.data
        try:
            voxelize(context.active_object, data.remesh_voxel_size)
            bpy.ops.hops.display_notification(info=f"Voxelized: {data.remesh_voxel_size:.3f}")
        except:
            bpy.ops.hops.display_notification(info=f"Nice Try")
        return {"FINISHED"}

def voxelize(object, voxsize):
    bpy.ops.object.convert(target='MESH')
    bpy.context.object.data.remesh_voxel_size = voxsize
    bpy.ops.object.voxel_remesh()
