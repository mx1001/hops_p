import bpy
from bpy.props import BoolProperty
import bpy.utils.previews
from ... preferences import get_preferences
from ...ui_framework.operator_ui import Master
from .. meshtools.applymod import apply_mod

class HOPS_OT_ScrollMulti(bpy.types.Operator):
    bl_idname = "hops.scroll_multi"
    bl_label = "Bool / Modifier Management system"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """Bool/Mod Management Multi-tool
    
LMB - Bool Cutter Scroll
LMB + SHIFT - Modifier Scroll
LMB + CTRL - Toggle Modifiers Off / On
LMB + ALT - Smart Apply

CTRL + SHIFT - Smart Apply

"""
    header = "nothing"
    text = "nothing"

    def __init__(self):

        HOPS_OT_ScrollMulti.called_ui = False

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def invoke(self, context, event):
        if event.ctrl and event.shift:
            for object in [o for o in context.selected_objects if o.type == 'MESH']:
                header = "Smart Apply"
                apply_mod(self, object, clear_last=False)
                bpy.ops.hops.display_notification(info=f'Smart Apply', name="")
                self.report({'INFO'}, F'Smart Applied')
        elif event.alt and event.ctrl:
            self.report({'INFO'}, F'Other Case Worked')
        elif event.shift:
            #Additive Scroll
            header = "Modifier Scroll"
            bpy.ops.hops.modifier_scroll('INVOKE_DEFAULT',all=True, additive=True)
            self.report({'INFO'}, F'Modifier Scroll')
        elif event.ctrl:
            header = "Modifier Toggle"
            bpy.ops.hops.bool_toggle_viewport('INVOKE_DEFAULT', all_modifiers=True)
            self.report({'INFO'}, F'Modifier Toggle')
        elif event.alt:
            header = "Smart Apply"
            for object in [o for o in context.selected_objects if o.type == 'MESH']:
                apply_mod(self, object, clear_last=False)
            bpy.ops.hops.display_notification(info=f'Smart Apply', name="")
            self.report({'INFO'}, F'Smart Applied')
        else:
            #Object Scroll
            header = "Bool Scroll"
            bpy.ops.hops.bool_scroll_objects('INVOKE_DEFAULT')
            self.report({'INFO'}, F'Object Scroll')

        # Operator UI
        if get_preferences().ui.Hops_extra_info:
            if not HOPS_OT_ScrollMulti.called_ui:
                HOPS_OT_ScrollMulti.called_ui = True

                ui = Master()

                draw_data = [
                    [header]
                ]

                ui.receive_draw_data(draw_data=draw_data)
                ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return {'FINISHED'}
