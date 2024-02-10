import bpy
from ... utils.context import ExecutionContext
from ... preferences import get_preferences
from ... preferences import get_preferences
from ...ui_framework.operator_ui import Master

class HOPS_OT_SphereCast(bpy.types.Operator):
    bl_idname = "hops.sphere_cast"
    bl_label = "Sphere / Cast"
    bl_description = "Adds subdivision and cast modifier to object making it a sphere"
    bl_options = {"REGISTER", "UNDO"}

    called_ui = False

    def __init__(self):

        HOPS_OT_SphereCast.called_ui = False

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        object = bpy.context.active_object
        sphereCast(object)

        # Operator UI
        if not HOPS_OT_SphereCast.called_ui:
            HOPS_OT_SphereCast.called_ui = True

            ui = Master()
            draw_data = [
                ["Spherecast"],
                ["Subdivision/Cast", "Added"],
                ["Converted To Sphere"]
                ]
            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)


        return {"FINISHED"}


def sphereCast(object):
    with ExecutionContext(mode="OBJECT", active_object=object):
        bpy.ops.object.subdivision_set(level=3)
        bpy.ops.object.modifier_add(type='CAST')
        bpy.context.object.modifiers["Cast"].factor = 1
