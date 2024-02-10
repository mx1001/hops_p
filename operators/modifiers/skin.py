import bpy
from ... preferences import get_preferences
from ...ui_framework.operator_ui import Master


class HOPS_OT_MOD_Skin(bpy.types.Operator):
    bl_idname = "hops.mod_skin"
    bl_label = "Add skin Modifier"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """LMB - Add skin Modifier
LMB + CTRL - Add new skin Modifier

"""
    called_ui = False

    def __init__(self):

        HOPS_OT_MOD_Skin.called_ui = False

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    def invoke(self, context, event):
        for object in [o for o in context.selected_objects if o.type == 'MESH']:
            if event.ctrl:
                self.add_skin_modifier(object)
            else:
                if not self.skin_modifiers(object):
                    self.add_skin_modifier(object)

        # Operator UI
        if not HOPS_OT_MOD_Skin.called_ui:
            HOPS_OT_MOD_Skin.called_ui = True

            ui = Master()
            draw_data = [
                ["SKIN"],
                ["Skin Modifier added"]]
            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return {"FINISHED"}

    @staticmethod
    def skin_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "SKIN"]

    def add_skin_modifier(self, object):
        skin_mod = object.modifiers.new(name="skin", type="SKIN")
        skin_mod.branch_smoothing = 0
        skin_mod.use_smooth_shade = True
        skin_mod.use_x_symmetry = False
        skin_mod.use_y_symmetry = False
        skin_mod.use_z_symmetry = False
