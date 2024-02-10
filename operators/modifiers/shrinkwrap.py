import bpy
from ... preferences import get_preferences
from ...ui_framework.operator_ui import Master


class HOPS_OT_MOD_Shrinkwrap(bpy.types.Operator):
    bl_idname = "hops.mod_shrinkwrap"
    bl_label = "Add shrinkwrap Modifier"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """LMB - Add shrinkwrap Modifier
LMB + CTRL - Add new shrinkwrap Modifier

"""
    called_ui = False

    def __init__(self):

        HOPS_OT_MOD_Shrinkwrap.called_ui = False

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    def invoke(self, context, event):
        active = context.active_object
        for object in [o for o in context.selected_objects if o.type == 'MESH']:
            if object is not active:
                if event.ctrl:
                    self.add_shrinkwrap_modifier(object, active)
                else:
                    if not self.shrinkwrap_modifiers(object):
                        self.add_shrinkwrap_modifier(object, active)

        # Operator UI
        if not HOPS_OT_MOD_Shrinkwrap.called_ui:
            HOPS_OT_MOD_Shrinkwrap.called_ui = True

            ui = Master()
            draw_data = [
                ["SHRINKWRAP"],
                ["Object B shrinkwrapped to Object A"]]
            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return {"FINISHED"}

    @staticmethod
    def shrinkwrap_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "SHRINKWRAP"]

    def add_shrinkwrap_modifier(self, object, obj):
        shrink_mod = object.modifiers.new(name="shrinkwrap", type="SHRINKWRAP")
        shrink_mod.cull_face = 'BACK'
        shrink_mod.offset = 0
        shrink_mod.target = obj
        shrink_mod.wrap_method = 'PROJECT'
        shrink_mod.wrap_mode = 'ON_SURFACE'
        shrink_mod.cull_face = 'OFF'
        shrink_mod.use_negative_direction = True
        shrink_mod.use_positive_direction = True
        shrink_mod.use_invert_cull = True
