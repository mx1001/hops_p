import bpy
from ... preferences import get_preferences
from ...ui_framework.operator_ui import Master
from ... utility import addon


class HOPS_OT_TP_PowerLinkInt(bpy.types.Operator):
    bl_idname = "hops.powerlink"
    bl_label = "PowerLink"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """PowerLink! 
    
LMB - Link Chosen Asset

"""
#CTRL - Create Link Collection Via HOPS

    called_ui = False

    link: bpy.props.BoolProperty(
        name='Link',
        description='Link assets instead of appending',
        default=True,
    )

    def __init__(self):
        HOPS_OT_TP_PowerLinkInt.called_ui = False

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        wm = context.window_manager
        powerlink = getattr(wm, 'powerlink', None)
        if hasattr(powerlink, 'powerlink'):
            status, info, number = powerlink.powerlink(link=self.link, hops=True)
        else:
            status, info, number = False, 'PowerLink is not installed', 0

        # Operator UI
        if not HOPS_OT_TP_PowerLinkInt.called_ui:
            HOPS_OT_TP_PowerLinkInt.called_ui = True

            if status:
                draw_data = [
                    ["PowerLink"],
                    [f"Collections {'Linked' if self.link else 'Appended'}", number],
                    *info,
                ]

            else:
                draw_data = [
                    ["PowerLink"],
                    [info],
                ]

            ui = Master()
            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return {"FINISHED"}
