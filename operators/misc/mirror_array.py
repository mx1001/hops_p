import bpy
from bpy.props import BoolProperty
import bpy.utils.previews

class HOPS_OT_Mirror_Array(bpy.types.Operator):
    bl_idname = "hops.mirror_array"
    bl_label = "Activates Mirror / Array Gizmo"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """LMB - Mirror Gizmo
LMB + CTRL - Array Gizmo
"""

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def invoke(self, context, event):
        if event.ctrl:
            bpy.ops.hops.array_gizmo('INVOKE_DEFAULT')
            self.report({'INFO'}, F'Array Gizmo')
        elif event.shift:
            bpy.ops.hops.array_gizmo('INVOKE_DEFAULT')
            self.report({'INFO'}, F'Array Gizmo')
        elif event.alt:
            bpy.ops.hops.array_gizmo('INVOKE_DEFAULT')
            self.report({'INFO'}, F'Array Gizmo')
        elif event.ctrl and event.shift:
            bpy.ops.hops.array_gizmo('INVOKE_DEFAULT')
            self.report({'INFO'}, F'Array Gizmo')
        else:
            bpy.ops.hops.mirror_gizmo('INVOKE_DEFAULT')
            self.report({'INFO'}, F'Mirror')

        return {'FINISHED'}
