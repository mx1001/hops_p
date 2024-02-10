import bpy
from bpy.types import Operator


class HARDFLOW_OT_dot_settings(Operator):
    bl_idname = 'hops.dot_settings'
    bl_label = 'Dot Settings'
    bl_description = 'Adjust setting of the datablock related to the active dot'


    def execute(self, context):
        hardflow = bpy.context.window_manager.hardflow

        types = {'array', 'screw', 'solidify', 'displace', 'simple_deform', 'bevel', 'wireframe'}
        mod = None

        obj = context.active_object

        for point in hardflow.dots.points:
            if point.highlight:
                _type = point.type[:-2]
                if _type in types:
                    mod = obj.modifiers[point.name]
                    hardflow.dots.mod = mod.name
                    hardflow.dots.description = point.description

        if mod and not mod.show_expanded:
            mod.show_expanded = True

        bpy.ops.wm.call_panel(name='HARDFLOW_PT_dots', keep_open=True)

        return {'FINISHED'}
