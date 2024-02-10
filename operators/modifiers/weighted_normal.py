import bpy
from ... preferences import get_preferences
from ...ui_framework.operator_ui import Master


class HOPS_OT_MOD_Weighted_Normal(bpy.types.Operator):
    bl_idname = "hops.mod_weighted_normal"
    bl_label = "Add Weighted Normal Modifier"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """LMB - Add Weighted Normal Modifier
LMB + SHIFT - Add Weighted Normal Modifier without Keep Sharp option"""

    keep_sharp: bpy.props.BoolProperty(
        name="Keep Sharp",
        description="",
        default=True)

    called_ui = False

    def __init__(self):

        HOPS_OT_MOD_Weighted_Normal.called_ui = False

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    def draw(self, context):
        self.layout.prop(self, "keep_sharp")

    def invoke(self, context, event):
        self.keep_sharp = False if event.shift else True
        return self.execute(context)

    def execute(self, context):
        for obj in [o for o in context.selected_objects if o.type == 'MESH']:
            obj.data.use_auto_smooth = True
            for f in obj.data.polygons:
                f.use_smooth = True

            for mod in obj.modifiers:
                if mod.type == 'WEIGHTED_NORMAL':
                    obj.modifiers.remove(mod)

            if obj.hops.status != 'BOOLSHAPE':
                mod = obj.modifiers.new(name="Weighted Normal", type='WEIGHTED_NORMAL')
                mod.keep_sharp = self.keep_sharp

        # Operator UI
        if not HOPS_OT_MOD_Weighted_Normal.called_ui:
            HOPS_OT_MOD_Weighted_Normal.called_ui = True

            ui = Master()
            draw_data = [
                ["WEIGHTED NORMAL"],
                ["Keep Sharp", self.keep_sharp]]
            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)


        return {"FINISHED"}
