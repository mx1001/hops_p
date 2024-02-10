import bpy
from mathutils import Vector
from bpy.types import Operator
from bpy.props import IntProperty, FloatProperty
from bgl import *
from gpu_extras.batch import batch_for_shader
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... graphics.drawing2d import draw_text, set_drawing_dpi, draw_box
from ... preferences import get_preferences
from ...ui_framework.master import Master
from ...ui_framework.utils.mods_list import get_mods_list
from . import infobar

class HOPS_OT_CurveStretch(Operator):
    bl_idname = "mesh.curve_stretch"
    bl_label = "Curve Stretch Helper"
    bl_description = "Preconfiguration for Mira Tools Curve Stretch"
    bl_options = {"REGISTER", "GRAB_CURSOR", "BLOCKING"}

    first_mouse_x : IntProperty()
    first_value : FloatProperty()
    second_value : IntProperty()

    def __init__(self):

        # Modal UI
        self.master = None


    def modal(self, context, event):

        curve = context.scene.mi_cur_stretch_settings

        # UI
        self.master.receive_event(event=event)

        self.mouse = [event.mouse_region_x, event.mouse_region_y]
        # offset_x = event.mouse_region_x - self.last_mouse_x

        if event.type == 'WHEELUPMOUSE':

            if curve.points_number < 12:

                curve.points_number += 1
                self.report({'INFO'}, F'Curve Points: {curve.points_number}')

        if event.type == 'WHEELDOWNMOUSE':

            if curve.points_number > 2:

                curve.points_number -= 1
                self.report({'INFO'}, F'Curve Points: {curve.points_number}')

        if event.type in {'LEFTMOUSE', 'RET', 'NUMPAD_ENTER'}:
            bpy.ops.mira.curve_stretch('INVOKE_DEFAULT')
            context.window_manager.event_timer_remove(self.timer)
            self.master.run_fade()
            infobar.remove(self)
            return {'FINISHED'}

        if event.type in {'RIGHTMOUSE', 'ESC', 'BACK_SPACE'}:
            context.window_manager.event_timer_remove(self.timer)
            self.master.run_fade()
            infobar.remove(self)
            return {'CANCELLED'}

        self.draw_master(context=context)

        self.last_mouse_x = event.mouse_region_x
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.report({'INFO'}, F'HOPS: Frontend for Mira CurveStretch. Scroll to adjust count. Click to proceed')
        self.last_mouse_x = event.mouse_region_x
        self.start_mouse_position = Vector((event.mouse_region_x, event.mouse_region_y))

        #UI System
        self.master = Master(context=context)
        self.master.only_use_fast_ui = True
        self.timer = context.window_manager.event_timer_add(0.025, window=context.window)

        context.window_manager.modal_handler_add(self)
        infobar.initiate(self)
        return {'RUNNING_MODAL'}


    def draw_master(self, context):

        # Start
        self.master.setup()
        curve = context.scene.mi_cur_stretch_settings

        ########################
        #   Fast UI
        ########################


        if self.master.should_build_fast_ui():

            win_list = []
            help_list = []
            mods_list = []
            active_mod = ""

            # Main
            if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1: #Fast Floating
                win_list.append(curve.points_number)
            else:
                win_list.append("Mira Curve Setup")
                win_list.append(curve.points_number)

            # Help
            help_list.append(["Scroll",  "Adust Mira Curve"])
            help_list.append(["LMB",     "Proceed To Curve"])
            help_list.append(["ESC",     "Cancel"])

            # Mods
            mods_list = get_mods_list(mods=bpy.context.active_object.modifiers)

            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="BevelAll", mods_list=mods_list, active_mod_name=active_mod)

        # Finished
        self.master.finished()
