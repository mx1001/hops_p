import bpy
import math


class HOPS_OT_MOD_Decimate(bpy.types.Operator):
    bl_idname = "hops.mod_decimate"
    bl_label = "Add decimate Modifier"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """LMB - Add Decimate Modifier
LMB + SHIFT - Use Unsubdiv Decimate
LMB + CTRL - Add new Decimate Modifier

"""

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    def invoke(self, context, event):
        for object in [o for o in context.selected_objects if o.type == 'MESH']:
            if event.ctrl:
                self.add_decimate_modifier(context, object, event)
            else:
                if not self.decimate_modifiers(object):
                    self.add_decimate_modifier(context, object, event)
        return {"FINISHED"}

    @staticmethod
    def decimate_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "DECIMATE"]

    def add_decimate_modifier(self, context, object, event):
        decim_mod = object.modifiers.new(name="decimate", type="DECIMATE")
        if event.shift:
            decim_mod.decimate_type = 'UNSUBDIV'
            decim_mod.iterations = 1
            bpy.ops.hops.display_notification(info="Decimate - Unsubdivided")
        else:
            decim_mod.decimate_type = 'DISSOLVE'
            decim_mod.angle_limit = math.radians(.05)
            bpy.ops.hops.display_notification(info="Decimate - Planar Dissolve")
        #decim_mod.angle_limit = 0.000872665
        decim_mod.delimit = {'NORMAL', 'SHARP'}
        if context.mode == 'EDIT_MESH':
            decim_mod.decimate_type = 'COLLAPSE'
            vg = object.vertex_groups.new(name='HardOps')
            bpy.ops.object.vertex_group_assign()
            decim_mod.vertex_group = vg.name
