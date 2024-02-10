import bpy
import bmesh
import gpu
from bgl import *
from gpu_extras.batch import batch_for_shader
from bpy.props import *
from mathutils import Vector
from collections import OrderedDict
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... graphics.drawing2d import draw_text, set_drawing_dpi, draw_box
from ... preferences import get_preferences
from ...ui_framework.master import Master
from ...ui_framework.utils.mods_list import get_mods_list
from . import infobar
from ... utility.base_modal_controls import Base_Modal_Controls


class HOPS_OT_ResetAxisModal(bpy.types.Operator):
    bl_idname = "hops.reset_axis_modal"
    bl_label = "Hops Reset Axis"
    bl_description = """ Reset / Flatten
    
    Reset object on selected axis.

    Object - Resets object axis globally
        *two object axis supported*
    Edit - flatten selection to axis or snap to cursor
    
    """
    bl_options = {"REGISTER", "UNDO"}

    def __init__(self):

        # Modal UI
        self.master = None


    def invoke(self, context, event):

        self.base_controls = Base_Modal_Controls(context, event)

        if context.active_object.mode == "EDIT":
            self.bm = bmesh.from_edit_mesh(context.active_object.data)
            self.original_verts = [[i for i in vert.co] for vert in self.bm.verts]
        self.active_obj_original_location = [i for i in context.active_object.location]
        self.original_locations = [[i for i in obj.location] for obj in context.selected_objects]
        self.axises = []
        self.set_axis = ""
        self.xyz = ["X", "Y", "Z"]
        self.xyz_index = -1

        #UI System
        self.master = Master(context=context)
        self.master.only_use_fast_ui = True
        self.timer = context.window_manager.event_timer_add(0.025, window=context.window)

        context.window_manager.modal_handler_add(self)
        infobar.initiate(self)
        return {"RUNNING_MODAL"}


    def modal(self, context, event):

        # UI
        self.master.receive_event(event=event)
        self.base_controls.update(context, event)

        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        if self.base_controls.scroll:
            self.reset_object()
            self.xyz_index -= self.base_controls.scroll
            self.xyz_index = min(max(-1, self.xyz_index), 2)
            if self.xyz_index == -1:
                self.set_axis = "RESET"
            else:
                self.set_axis = self.xyz[self.xyz_index]

        if not event.shift and event.type == "C" and event.value == "PRESS":
            if self.set_axis == "C":
                self.set_axis = "RESET"
            else:
                self.set_axis = "C"
                #context.view_layer.objects.active.select_set(False)
                bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
                context.view_layer.objects.active.select_set(True)
                self.report({'INFO'}, F'Snapped to: Cursor')

        if event.shift and event.type == "C" and event.value == "PRESS":
            if self.set_axis == "CO":
                self.set_axis = "RESET"
            else:
                self.set_axis = "CO"
                #context.view_layer.objects.active.select_set(False)
                bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
                context.view_layer.objects.active.select_set(True)
                self.report({'INFO'}, F'Snapped to: Cursor (offset)')

        if event.type == "X" and event.value == "PRESS":
            if self.set_axis == "X":
                self.set_axis = "RESET"
            else:
                self.set_axis = "X"
                self.report({'INFO'}, F'Snapped to: X Axis')
            self.axises.append("X")

        if event.type == "Y" and event.value == "PRESS":
            if self.set_axis == "Y":
                self.set_axis = "RESET"
            else:
                self.set_axis = "Y"
                self.report({'INFO'}, F'Snapped to: Y Axis')
            self.axises.append("Y")

        if self.base_controls.tilde and event.shift == True:
            bpy.context.space_data.overlay.show_overlays = not bpy.context.space_data.overlay.show_overlays

        if event.type == "Z" and event.value == "PRESS":
            if self.set_axis == "Z":
                self.set_axis = "RESET"
            else:
                self.set_axis = "Z"
                self.report({'INFO'}, F'Snapped to: Z Axis')
            self.axises.append("Z")

        if context.active_object.mode == "OBJECT":

            for obj in context.selected_objects:

                reset_to = [0, 0, 0]
                if len(context.selected_objects) > 1:
                    reset_to = self.active_obj_original_location
                # if obj.name == context.active_object.name:
                #     reset_to = context.space_data.cursor.location

                if self.set_axis == "X":
                    obj.location[0] = reset_to[0]
                elif self.set_axis == "Y":
                    obj.location[1] = reset_to[1]
                elif self.set_axis == "Z":
                    obj.location[2] = reset_to[2]

        elif context.active_object.mode == "EDIT":
            if self.set_axis == "X":
                bpy.ops.transform.resize(value=(0, 1, 1), orient_type='GLOBAL', orient_matrix_type='GLOBAL', constraint_axis=(True, False, False))
                # if get_preferences().ui.Hops_extra_info:
                #     bpy.ops.hops.display_notification(info=f"{self.set_axis}", name="")
            elif self.set_axis == "Y":
                bpy.ops.transform.resize(value=(1, 0, 1), orient_type='GLOBAL', orient_matrix_type='GLOBAL', constraint_axis=(False, True, False))
                # if get_preferences().ui.Hops_extra_info:
                #     bpy.ops.hops.display_notification(info=f"{self.set_axis}", name="")
            elif self.set_axis == "Z":
                bpy.ops.transform.resize(value=(1, 1, 0), orient_type='GLOBAL', orient_matrix_type='GLOBAL', constraint_axis=(False, False, True))
                # if get_preferences().ui.Hops_extra_info:
                #     bpy.ops.hops.display_notification(info=f"{self.set_axis}", name="")

        if self.set_axis == "RESET":
            self.reset_object()

        if self.base_controls.cancel:
            self.reset_object()
            context.window_manager.event_timer_remove(self.timer)
            self.master.run_fade()
            infobar.remove(self)
            return {'CANCELLED'}

        if self.base_controls.confirm:
            context.window_manager.event_timer_remove(self.timer)
            self.master.run_fade()
            infobar.remove(self)
            return {'FINISHED'}


        self.draw_master(context=context)

        context.area.tag_redraw()

        return {"RUNNING_MODAL"}


    def reset_object(self):
        if bpy.context.active_object.mode == "EDIT":
            for count, vert in enumerate(self.bm.verts):
                vert.co = self.original_verts[count]
            bpy.ops.mesh.normals_make_consistent(inside=False)
        else:
            for count, obj in enumerate(bpy.context.selected_objects):
                obj.location = self.original_locations[count]


    def draw_master(self, context):

        # Start
        self.master.setup()


        ########################
        #   Fast UI
        ########################


        if self.master.should_build_fast_ui():

            win_list = []
            help_list = []
            mods_list = []
            active_mod = ""

            # Main
            axis = self.set_axis
            if axis == "RESET":
                axis = ""
                self.axises = []
            if len(axis) > 1:
                axis = axis[0]

            if axis == "":
                axis = "None"

            if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1: #Fast Floating
                win_list.append(axis)
                win_list.append(format(", ".join(list(OrderedDict.fromkeys(self.axises)))))
            else:
                win_list.append("Reset Axis")
                win_list.append(axis)
                win_list.append("Axis - {}".format(", ".join(list(OrderedDict.fromkeys(self.axises)))))

            # Help
            help_list.append(["X",         "Reset x axis"])
            help_list.append(["Y",         "Reset y axis"])
            help_list.append(["Z",         "Reset z axis"])
            help_list.append(["C",         "Snap to cursor"])
            help_list.append(["C + Shift", "Snap to cursor offset"])
            help_list.append(["Scroll",    "Change axis"])
            help_list.append(["M",         "Toggle mods list."])
            help_list.append(["H",         "Toggle help."])
            help_list.append(["~",         "Toggle viewport displays."])

            # Mods
            mods_list = get_mods_list(mods=bpy.context.active_object.modifiers)

            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="Xslap", mods_list=mods_list, active_mod_name=active_mod)

        # Finished
        self.master.finished()
