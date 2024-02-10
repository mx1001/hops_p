import bpy
from ... preferences import get_preferences
from ...ui_framework.operator_ui import Master

class HOPS_OT_MOD_Triangulate(bpy.types.Operator):
    bl_idname = "hops.mod_triangulate"
    bl_label = "Add Triangulate Modifier"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """LMB - Add Triangulate Modifier
LMB + CTRL - Add new Triangulate Modifier
"""
    called_ui = False

    def __init__(self):

        HOPS_OT_MOD_Triangulate.called_ui = False

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    def invoke(self, context, event):
        for object in [o for o in context.selected_objects if o.type == 'MESH']:
            if event.ctrl:
                self.add_triangulate_modifier(object)
            else:
                if not self.triangulate_modifiers(object):
                    self.add_triangulate_modifier(object)
                else:
                    return {"CANCELLED"}

        # Operator UI
        if not HOPS_OT_MOD_Triangulate.called_ui:
            HOPS_OT_MOD_Triangulate.called_ui = True

            ui = Master()
            draw_data = [
                ["TRIANGULATE"],
                ["Min Vertices : ", self.tri_mod.min_vertices]]
            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return {"FINISHED"}

    @staticmethod
    def triangulate_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "TRIANGULATE"]

    def add_triangulate_modifier(self, object):
        self.tri_mod = object.modifiers.new(name="Triangulate", type="TRIANGULATE")
        self.tri_mod.min_vertices = 5
        self.tri_mod.show_in_editmode = False
