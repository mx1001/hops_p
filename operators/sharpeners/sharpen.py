import bpy
from bpy.props import BoolProperty
import bpy.utils.previews
from ... preferences import get_preferences
from math import radians


class HOPS_OT_Sharpen(bpy.types.Operator):
    bl_idname = "hops.sharp_n"
    bl_label = "Performs Sharpening"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """LMB - Mark Sharp Edges (ssharp)
LMB + CTRL - Add Bevel / Apply Boolean /  Mark Sharp Edges (csharp)
LMB + SHIFT - Recalculate Sharp Edges (re-sharp)
LMB + ALT - Weighted Sort
LMB + CTRL + SHIFT - Remove Sharp Edges / Bevel Mod (clear-sharp)
LMB + ALT + CTRL - Sharp Manager (sharp manager)
"""

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def invoke(self, context, event):

        if event.ctrl and event.shift:
            bpy.ops.clean.sharps()
            self.report({'INFO'}, F'Sharps Unmarked')

        elif event.alt and event.ctrl:
            bpy.ops.hops.sharp_manager('INVOKE_DEFAULT',take_sharp_from={'SEAM'},apply_sharp_to={'CREASE', 'BWEIGHT', 'SEAM', 'SHARP'})
            self.report({'INFO'}, F'Seams Converted To Sharp Markings')

        elif event.ctrl:
            bpy.ops.hops.complex_sharpen('INVOKE_DEFAULT', is_global=True, auto_smooth_angle=get_preferences().property.auto_smooth_angle, to_bwidth=True)
            self.report({'INFO'}, F'CSharpened ')

        elif event.alt:
            bpy.ops.hops.mod_weighted_normal(keep_sharp=True)
            self.report({'INFO'}, F'Weighted Normalize')
            return {'FINISHED'}

        elif event.shift:
            bpy.ops.hops.soft_sharpen('INVOKE_DEFAULT', additive_mode=False)
            self.report({'INFO'}, F'Re-Sharpened')

        else:
            bpy.ops.hops.soft_sharpen('INVOKE_DEFAULT', additive_mode=True, is_global=True, auto_smooth_angle=get_preferences().property.auto_smooth_angle)
            self.report({'INFO'}, F'SSharpened')

        return {'FINISHED'}
