import bpy
from bpy.props import BoolProperty
from ... preferences import get_preferences
from ...ui_framework.operator_ui import Master


class HOPS_OT_Shrinkwrap(bpy.types.Operator):
    bl_idname = "hops.shrinkwrap"
    bl_label = "Hops Shrinkwrap"
    bl_description = "Shrinkwrap selected mesh"
    bl_options = {"REGISTER", "UNDO"}

    called_ui = False

    def __init__(self):

        HOPS_OT_Shrinkwrap.called_ui = False

    @classmethod
    def poll(cls, context):
        object = context.active_object
        if object is None: return False
        if object.mode == "OBJECT" and object.type == "MESH":
            return True

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        object = context.active_object

        bpy.ops.object.add(type='MESH', view_align=True, enter_editmode=False)
        bpy.context.object.name = 'LOW_POLY'

        new = context.active_object.modifiers.new("Shrinkwrap", "SHRINKWRAP")
        new.target = object

        bpy.ops.object.mode_set(mode='EDIT')

        # Operator UI
        if not HOPS_OT_Shrinkwrap.called_ui:
            HOPS_OT_Shrinkwrap.called_ui = True

            ui = Master()
            draw_data = [
                ["SHRINKWRAP"],
                ["Object B shrinkwrapped to Object A"]]
            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)


        return {"FINISHED"}


class HOPS_OT_ShrinkwrapRefresh(bpy.types.Operator):
    bl_idname = "hops.shrinkwrap_refresh"
    bl_label = "Hops Shrinkwrap Refresh"
    bl_description = "Refresh Hard Ops shrinkwrap"
    bl_options = {"REGISTER", "UNDO"}

    sculpt : BoolProperty(name="Sculpt Mode",
                          description="use in Sculpt mode",
                          default=False)

    @classmethod
    def poll(cls, context):
        object = context.active_object
        if object is None: return False
        if (object.mode == "EDIT" or object.mode == "SCULPT") and object.type == "MESH":
            return True

    def draw(self, context):
        layout = self.layout

    def execute(self, context):

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.modifier_copy(modifier="Shrinkwrap")
        bpy.ops.object.modifier_apply(modifier="Shrinkwrap") # apply_as='DATA',
        bpy.context.object.modifiers["Shrinkwrap.001"].name = "Shrinkwrap"
        if self.sculpt:
            bpy.ops.object.mode_set(mode='SCULPT')
        else:
            bpy.ops.object.mode_set(mode='EDIT')

        return {"FINISHED"}
