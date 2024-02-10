import bpy
import gpu
from bgl import *
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... utils.event import Event_Clone
from ... utility import modifier
from ... utility.base_modal_controls import Base_Modal_Controls
from ... utils.toggle_view3d_panels import collapse_3D_view_panels
from ... preferences import get_preferences
from ... ui_framework.master import Master
from ... ui_framework.utils.mods_list import get_mods_list
from . import infobar
# Cursor Warp imports
from ... utils.cursor_warp import mouse_warp
from ... utils.modal_frame_drawing import draw_modal_frame
from ... addon.utility import method_handler


class HOPS_OT_AdjustTthickOperator(bpy.types.Operator):
    bl_idname = "hops.adjust_tthick"
    bl_label = "Adjust Tthick"
    bl_description = """LMB - Adjust SOLIDIFY modifier
LMB + Ctrl - Add New SOLIDIFY modifier

Press H for help"""
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}


    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    @staticmethod
    def solidify_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "SOLIDIFY"]


    def invoke(self, context, event):

        self.base_controls = Base_Modal_Controls(context, event)
        self.original_tool_shelf, self.original_n_panel = collapse_3D_view_panels()
        self.sudo_event = Event_Clone(event)
        self.mouse_active = True
        self.objects = [o for o in context.selected_objects if o.type == 'MESH']
        self.object = context.active_object if context.active_object.type == 'MESH' else self.objects[0]

        for obj in self.objects:
            modifier.sort(obj, sort_types=['WEIGHTED_NORMAL'])

        self.solidify_mods = {}
        self.solidify = self.get_solidify_modifier(event)

        for obj in self.solidify_mods:
            self.solidify_mods[obj]["start_solidify_thickness"] = self.solidify_mods[obj]["solidify"].thickness
            self.solidify_mods[obj]["start_solidify_offset"] = self.solidify_mods[obj]["solidify"].offset

        self.master = Master(context=context, use_warp_mode=True)
        self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.safe_draw_shader, (context,), 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        infobar.initiate(self)
        return {"RUNNING_MODAL"}


    def get_solidify_modifier(self, event):

        for obj in self.objects:
            if obj not in self.solidify_mods:
                self.solidify_mods.update({obj: {"solidify": None, "start_solidify_thickness": 0, "start_solidify_offset": 0, "solidify_offset": 0, "thickness_offset": 0, "created_solidify_modifier": False}})
            mods = obj.modifiers
            if event.ctrl:
                solidify_modifier = obj.modifiers.new("Solidify", "SOLIDIFY")
                self.solidify_mods[obj]["solidify"] = solidify_modifier
                self.solidify_mods[obj]["created_solidify_modifier"] = True
                if get_preferences().property.force_thick_reset_solidify_init or self.solidify_mods[obj]["created_solidify_modifier"]:
                    solidify_modifier.thickness = 0
                    solidify_modifier.use_even_offset = True
                    solidify_modifier.use_quality_normals = True
                    solidify_modifier.use_rim_only = False
                    solidify_modifier.show_on_cage = True
            else:
                if "Solidify" in mods:
                    self.solidify_mods[obj]["solidify"] = obj.modifiers["Solidify"]
                    solidify_modifier = obj.modifiers["Solidify"]
                else:# if did not get one this iteration, create it
                    solidify_modifier = obj.modifiers.new("Solidify", "SOLIDIFY")
                    self.solidify_mods[obj]["solidify"] = solidify_modifier
                    self.solidify_mods[obj]["created_solidify_modifier"] = True
                if get_preferences().property.force_thick_reset_solidify_init or self.solidify_mods[obj]["created_solidify_modifier"]:
                    solidify_modifier.thickness = 0
                    solidify_modifier.use_even_offset = True
                    solidify_modifier.use_quality_normals = True
                    solidify_modifier.use_rim_only = False
                    solidify_modifier.show_on_cage = True


    def modal(self, context, event):

        self.sudo_event.update(event)
        event = self.sudo_event

        self.master.receive_event(event=event)
        if self.mouse_active:
            mouse_warp(context, event)
        self.base_controls.update(context, event)

        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        elif self.base_controls.cancel:
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.reset_object()
            context.area.header_text_set(text=None)
            self.master.run_fade()
            infobar.remove(self)
            return {'CANCELLED'}

        elif self.base_controls.confirm:
            if not self.master.is_mouse_over_ui():
                self.remove_shader()
                collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
                context.area.header_text_set(text=None)
                self.master.run_fade()
                infobar.remove(self)
                return {'FINISHED'}

        elif event.type == 'X' and event.value == 'PRESS':
            self.mouse_active = not self.mouse_active

        offset_x = self.base_controls.mouse if self.mouse_active else 0
        context.area.header_text_set("Hardops Adjust Thickness")

        for obj in self.solidify_mods:
            self.solidify = self.solidify_mods[obj]["solidify"]
            self.solidify_mods[obj]["thickness_offset"] += offset_x
            if event.ctrl:
                self.solidify.thickness = round(self.solidify_mods[obj]["start_solidify_thickness"] + self.solidify_mods[obj]["thickness_offset"], 1)
            else:
                self.solidify.thickness = self.solidify_mods[obj]["start_solidify_thickness"] + self.solidify_mods[obj]["thickness_offset"]

            if event.type == 'ONE' and event.value == 'PRESS':
                self.solidify.offset = -1
                self.solidify_mods[obj]["solidify_offset"] = 0
                self.report({'INFO'}, F'Solidify Offset : 0')

            if event.type == 'TWO' and event.value == 'PRESS':
                self.solidify.offset = 0
                self.solidify_mods[obj]["solidify_offset"] = -1
                self.report({'INFO'}, F'Solidify Offset : -1')

            if event.type == 'THREE' and event.value == 'PRESS':
                self.solidify.offset = 1
                self.solidify_mods[obj]["solidify_offset"] = -2
                self.report({'INFO'}, F'Solidify Offset : -2')

            if event.type == "Q" and event.value == "PRESS":
                bpy.ops.object.modifier_move_up(modifier=self.solidify.name)

            if event.type == "E" and event.value == "PRESS":
                bpy.ops.object.modifier_move_down(modifier=self.solidify.name)

            if event.type == 'R' and event.value == 'PRESS':
                self.solidify.use_rim_only = not self.solidify.use_rim_only
                self.report({'INFO'}, F'Rim Only : {self.solidify.use_rim_only}')

            if event.shift:
                if self.base_controls.scroll==1:
                    bpy.ops.object.modifier_move_up(modifier=self.solidify.name)
                if self.base_controls.scroll == -1:
                    bpy.ops.object.modifier_move_down(modifier=self.solidify.name)

            # solidify mode is 2.82 specific feature
            if (2, 82, 4)<bpy.app.version and event.type == 'FOUR' and event.value == 'PRESS':
                if self.solidify.solidify_mode == 'EXTRUDE':
                    self.solidify.solidify_mode = 'NON_MANIFOLD'
                else:
                    self.solidify.solidify_mode = 'EXTRUDE'
                self.report({'INFO'}, F'Mode : {self.solidify.solidify_mode}')



        self.draw_master(context=context, event=event)

        context.area.tag_redraw()

        return {"RUNNING_MODAL"}


    def reset_object(self):

        for obj in self.solidify_mods:
            self.solidify = self.solidify_mods[obj]["solidify"]
            self.solidify.thickness = self.solidify_mods[obj]["start_solidify_thickness"]
            self.solidify.offset = self.solidify_mods[obj]["start_solidify_offset"]
            if self.solidify_mods[obj]["created_solidify_modifier"]:
                obj.modifiers.remove(self.solidify)

        self.solidify = None


    def finish(self, context):

        context.area.header_text_set(text=None)
        self.remove_ui()
        infobar.remove(self)
        return {"FINISHED"}


    def remove_shader(self):
        '''Remove shader handle.'''

        if self.draw_handle:
            self.draw_handle = bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle, "WINDOW")


    def safe_draw_shader(self, context):
        method_handler(self.draw_shader,
            arguments = (context,),
            identifier = 'UI Framework',
            exit_method = self.remove_shader)


    def draw_shader(self, context):
        '''Draw shader handle.'''

        draw_modal_frame(context)


    def draw_master(self, context, event):

        # Start
        self.master.setup()

        #--- Fast UI ---#
        if self.master.should_build_fast_ui():
            win_list = []
            help_list = []
            mods_list = []
            active_mod = ""

            # Main
            if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1: #Fast Floating
                if self.solidify != None:
                    win_list.append("{:.2f}".format(self.solidify.thickness))
                    win_list.append("{}".format(self.solidify.use_rim_only))
                    win_list.append("{:.2f}".format(self.solidify.offset))
                else:
                    win_list.append("0")
                    win_list.append("Rim: Removed")
                    win_list.append("Offset: Removed")
            else:
                win_list.append("Solidify")
                if self.solidify != None:
                    win_list.append("{:.3f}".format(self.solidify.thickness))
                    win_list.append("Rim: {}".format(self.solidify.use_rim_only))
                    win_list.append("Offset: {:.2f}".format(self.solidify.offset))
                else:
                    win_list.append("0")
                    win_list.append("Rim: Removed")
                    win_list.append("Offset: Removed")

            # Help
            help_list.append(["R",              "Turn rim on/off"])
            help_list.append(["Ctrl",           "Set thickness (snap)"])
            help_list.append(["Shift + Scroll", "Move mod up/down"])
            help_list.append(["1",              "Set offset to -1"])
            help_list.append(["2",              "Set offset to 0"])
            help_list.append(["3",              "Set offset to 1"])
            if self.solidify != None:
                help_list.append(["4", F"Solidify Mode: {self.solidify.solidify_mode.capitalize()}"])
            help_list.append(["E / Q",  "Move mod up/down"])
            help_list.append(["M",      "Toggle mods list"])
            help_list.append(["H",      "Toggle help"])
            help_list.append(["~",      "Toggle viewport displays"])
            help_list.append(["O",      "Toggle viewport Rendering"])
            help_list.append(["X",      "Pause mouse"])

            # Mods
            if self.solidify != None:
                active_mod = self.solidify.name
            else:
                active_mod = ""
            mods_list = get_mods_list(mods=bpy.context.active_object.modifiers)
            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="Tthick", mods_list=mods_list, active_mod_name=active_mod)

        #--- Expanded ---#
        else:
            # Main
            main_window = {
                "main_count" : [],
                "header_sub_text" : [],
                "last_col_cell_1" : [],
                "last_col_cell_2" : [],
                "last_col_cell_3" : []}

            main_window["main_count"] = ["{:.2f}".format(self.solidify.thickness), self.add_thickness, (context, event, .1,), (context, event, -.1,), True]
            main_window["header_sub_text"] = [f'Rim : {self.solidify.use_rim_only}', self.sudo_event.alter_event, ('R', 'PRESS'), False]
            main_window["last_col_cell_1"] = [f'Offset: {self.solidify.offset}', self.toggle_offset_presets]
            main_window["last_col_cell_2"] = ["Move mod up", self.sudo_event.alter_event, ('Q', 'PRESS'), False]
            main_window["last_col_cell_3"] = ["Move mod down", self.sudo_event.alter_event, ('E', 'PRESS'), False]
            self.master.receive_main(win_dict=main_window)

            # Help
            hot_keys_dict = {}
            quick_ops_dict = {}
            hot_keys_dict["R"] =         ["Turn rim on/off", self.sudo_event.alter_event, ('R', 'PRESS')]
            hot_keys_dict["Ctrl"] =      "Set thickness (snap)"
            hot_keys_dict["E / Minus"] = ["Move mod down", self.sudo_event.alter_event, ('NUMPAD_MINUS', 'PRESS')]
            hot_keys_dict["Q / Plus"] =  ["Move mod up", self.sudo_event.alter_event, ('NUMPAD_PLUS', 'PRESS')]
            hot_keys_dict["1"] =         ["Set offset to -1"]
            hot_keys_dict["2"] =         ["Set offset to 0"]
            hot_keys_dict["3"] =         ["Set offset to 1"]
            if self.solidify != None:
                hot_keys_dict["4"] = [F"Solidify Mode: {self.solidify.solidify_mode.capitalize()}"]
            hot_keys_dict["~"] =     ["Toggle viewport overlays", self.sudo_event.alter_event, ('ACCENT_GRAVE', 'PRESS', [('shift', True)])]
            hot_keys_dict["O"] =     ["Toggle viewport display", self.sudo_event.alter_event, ('O', 'PRESS', [('shift', True)])]
            hot_keys_dict["X"] =     ["Pause Mouse", self.sudo_event.alter_event, ('X', 'PRESS', [('shift', True)])]
            self.master.receive_help(hot_keys_dict=hot_keys_dict, quick_ops_dict={})

            # Mods
            win_dict = {}
            for mod in reversed(context.active_object.modifiers):
                win_dict[mod.name] = str(mod.type)
            if self.solidify != None:
                active_mod = self.solidify.name
            else:
                active_mod = ""
            self.master.receive_mod(win_dict=win_dict, active_mod_name=active_mod)

        # Finished
        self.master.finished()


    # Functions for expanded UI

    def toggle_offset_presets(self):
        '''Toggle the offset presets.'''

        for obj in self.solidify_mods:
            if self.solidify.offset == -1:
                self.solidify.offset = 0
                self.solidify_mods[obj]["solidify_offset"] = -1
                self.report({'INFO'}, F'Solidify Offset : -1')
            elif self.solidify.offset == 0:
                self.solidify.offset = 1
                self.solidify_mods[obj]["solidify_offset"] = -2
                self.report({'INFO'}, F'Solidify Offset : -2')
            elif self.solidify.offset == 1:
                self.solidify.offset = -1
                self.solidify_mods[obj]["solidify_offset"] = 0
                self.report({'INFO'}, F'Solidify Offset : 0')
            else:
                self.solidify.offset = 0
                self.solidify_mods[obj]["solidify_offset"] = -1
                self.report({'INFO'}, F'Solidify Offset : -1')                

    
    def add_thickness(self, context, event, thickness):
        '''Add thickness to the objects.'''

        offset_x = thickness
        context.area.header_text_set("Hardops Adjust Thickness")

        for obj in self.solidify_mods:
            self.solidify = self.solidify_mods[obj]["solidify"]
            self.solidify_mods[obj]["thickness_offset"] += offset_x
            if event.ctrl:
                self.solidify.thickness = round(self.solidify_mods[obj]["start_solidify_thickness"] + self.solidify_mods[obj]["thickness_offset"], 1)
            else:
                self.solidify.thickness = self.solidify_mods[obj]["start_solidify_thickness"] + self.solidify_mods[obj]["thickness_offset"]
