import bpy
from bpy.props import BoolProperty
from ... preferences import get_preferences
from ...ui_framework.operator_ui import Master

class HOPS_OT_BoolToggle(bpy.types.Operator):
    bl_idname = "hops.bool_toggle_viewport"
    bl_label = "Modifier Toggle"
    bl_description = "Toggles viewport visibility of all modifiers on selected object."
    bl_options = {"REGISTER", "UNDO"}

    all_modifiers: BoolProperty(
        name="Hide All Modifiers",
        description="Hide all Modifiers",
        default=False)

    called_ui = False

    def __init__(self):

        HOPS_OT_BoolToggle.called_ui = False

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        col = layout.column(align=True)
        colrow = col.row(align=True).split(factor=0.6, align=True)
        colrow.prop(self, "all_modifiers", toggle=True)

    def execute(self, context):
        if context.object is not None:
            for obj in context.selected_objects:
                if self.all_modifiers:
                    for mod in obj.modifiers:
                        mod.show_viewport = not mod.show_viewport
                else:
                    for mod in obj.modifiers:
                        if mod.type == 'BOOLEAN':
                            mod.show_viewport = not mod.show_viewport

        # Operator UI
        if not HOPS_OT_BoolToggle.called_ui:
            HOPS_OT_BoolToggle.called_ui = True

            ui = Master()
            draw_data = [
                ["Modifier Toggle"],
                ["Booleans Only ", not self.all_modifiers]
                ]
            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return {"FINISHED"}
