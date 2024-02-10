import bpy
import pathlib
from ... preferences import get_preferences
from ...ui_framework.operator_ui import Master
from ... utility import addon

class HOPS_OT_TP_PowerSaveInt(bpy.types.Operator):
    bl_idname = "hops.powersave"
    bl_label = "PowerSave"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """PowerSave! 
    
Save this blend file with the name in the text field below.
If no name is provided, generate one based on the date and time.
If this blend has never been saved, put it in the PowerSave folder

Ctrl - Go into a save prompt
"""

    called_ui = False

    def __init__(self):
        HOPS_OT_TP_PowerSaveInt.called_ui = False

    def invoke(self, context, event):
        
        if event.ctrl:
            bpy.ops.hops.power_save_dialog('INVOKE_DEFAULT')
            return {"FINISHED"}

        return self.execute(context)

    def execute(self, context):

        try:
            bpy.ops.powersave.powersave()
        except:
            pass

        # Operator UI
        if not HOPS_OT_TP_PowerSaveInt.called_ui:
            HOPS_OT_TP_PowerSaveInt.called_ui = True

            path = pathlib.Path(bpy.data.filepath).resolve()
            folder, name = str(path.parent), path.stem

            ui = Master()
            draw_data = [
                ["PowerSave"],
                [folder, " "],
                [name, " "],
                ["Now saving ... ", " "]
            ]
            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return {"FINISHED"}
