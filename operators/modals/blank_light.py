import bpy, math, random, os, json
from datetime import datetime
from pathlib import Path
from enum import Enum
from math import cos, sin, pi, radians, degrees
from mathutils import Matrix, Vector, geometry, Quaternion
from ... ui_framework.master import Master
from ... preferences import get_preferences
from ... utility.base_modal_controls import Base_Modal_Controls
from ... utils.event import Event_Clone
from ... ui_framework.presets.ui_forms import Mods_Panel_Form, Main_Panel_Form

# Input system
from ... addon.utility.screen import dpi_factor
from ... ui_framework.graphics.draw import render_quad, render_geo, render_text, draw_border_lines
from ... ui_framework.utils.geo import get_blf_text_dims

# Cursor Warp imports
from ... utils.toggle_view3d_panels import collapse_3D_view_panels
from ... utils.modal_frame_drawing import draw_modal_frame
from ... utils.cursor_warp import mouse_warp
from ... addon.utility import method_handler

# Save system
invalid = {'\\', '/', ':', '*', '?', '"', '<', '>', '|', '.'}
completed = {'LEFTMOUSE', 'RET', 'NUMPAD_ENTER'}
cancel = {'RIGHTMOUSE', 'ESC'}


class Edit_State(Enum):

    LIGHT_RIG = 0
    SINGLE_LIGHT = 1
    WORLD_EDIT = 2
    NON_ADDITIVE = 3
    JSON_EDIT = 4


description = """Blank Light
Creates a randomized light rig
    
LMB   - Blank Light Rig Scroll
Shift - Expanded Mode (Tab) 
Ctrl  - Non Destructive Scroll
(keeps previous light placements and count)

Press H for help
"""

class HOPS_OT_Blank_Light(bpy.types.Operator):

    """Blank Light Rig"""
    bl_idname = "hops.blank_light"
    bl_label = "Blank Light"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}
    bl_description = description


    def invoke(self, context, event):

        # Props
        self.master = None
        self.base_controls = None
        self.empty = None
        self.lights = []
        self.active_light = None
        self.edit_state = Edit_State.LIGHT_RIG if not event.ctrl else Edit_State.NON_ADDITIVE
        self.mouse_active = True
        self.available_light_types = {'AREA', 'SUN'}
        self.exit_to_viewport_adjust = False
        self.ran_world_setup = False

        # JSON Props
        self.json_data = None                           # Current loaded json data
        self.json_current_file = None                   # Current json file path
        self.json_file_dirs = self.get_json_file_dirs() # The current list of file directories
        self.json_files = []                            # All the file names
        self.json_current_file_name = ""                # Used for UI
        self.json_file_name = None                      # Last saved file name
        self.json_getting_file_name = False             # If inputing file name
        self.setup_json_draw_elements(context)          # Setup input system

        # Setup
        self.capture_initial_state(context=context)
        self.base_controls = Base_Modal_Controls(context=context, event=event)
        self.sudo_event = Event_Clone(event)
        self.original_tool_shelf, self.original_n_panel = collapse_3D_view_panels()
        self.get_light_empty(context)
        self.get_lights()
        if self.lights == []:
            self.randomize_all_lights(context)

        # Safe guard from switching to full light rig mode
        self.start_mode = self.edit_state

        # UI : Expanded or Fast
        if event.shift == True:
            self.master = Master(context=context, show_fast_ui=False)
        else:
            self.master = Master(context=context, show_fast_ui=True)

        self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.safe_draw_shader, (context,), 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


    def modal(self, context, event):

        # Getting JSON file name (Shift S sets this.)
        if self.json_getting_file_name == True:
            self.save_json_file_with_user_input(context=context, event=event)
            return {'RUNNING_MODAL'}

        self.sudo_event.update(event)
        event = self.sudo_event
        self.master.receive_event(event=event)
        self.base_controls.update(context=context, event=event)
        
        if self.mouse_active:
            mouse_warp(context, event)
            if self.edit_state != Edit_State.NON_ADDITIVE:
                angle = self.base_controls.mouse * 2 
                if abs(angle) > 0:
                    self.rotate_light_rig(angle)

        # Navigation
        if self.base_controls.pass_through:
            if not self.master.is_mouse_over_ui():
                return {'PASS_THROUGH'}

        # Confirm
        elif self.base_controls.confirm:
            if not self.master.is_mouse_over_ui():
                self.master.run_fade()
                self.remove_shader()
                collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
                if self.exit_to_viewport_adjust == True:
                    bpy.context.space_data.shading.use_scene_world = False
                    bpy.ops.hops.adjust_viewport('INVOKE_DEFAULT')
                return {'FINISHED'}

        # Cancel
        elif self.base_controls.cancel:
            if not self.master.is_mouse_over_ui():
                self.restore_initial_state(context=context)
                self.master.run_fade()
                self.remove_shader()
                collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
                return {'CANCELLED'}

        # Randomize / Scale / Switch Lights
        elif event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} and event.value == 'PRESS':
            if not self.master.is_mouse_over_ui():
                if self.edit_state == Edit_State.LIGHT_RIG:
                    if event.ctrl == True:
                        self.switch_light_types(context)
                    elif event.shift == False:
                        self.randomize_all_lights(context)
                    elif event.shift == True:
                        if event.type == 'WHEELUPMOUSE':
                            self.scale_rig(.25)
                        else:
                            self.scale_rig(-.25)

                elif self.edit_state == Edit_State.NON_ADDITIVE:
                    self.randomize_all_lights_non_additive(context)

                elif self.edit_state == Edit_State.JSON_EDIT:
                    if event.type == 'WHEELUPMOUSE':
                        self.get_next_json_configuration(context, forward=True)
                    else:
                        self.get_next_json_configuration(context, forward=False)

        # Set all colors to white
        elif event.type == 'W' and event.value == 'PRESS':
            if self.edit_state in {Edit_State.LIGHT_RIG, Edit_State.NON_ADDITIVE, Edit_State.JSON_EDIT}:
                self.set_all_colors_to_white()
            elif self.edit_state == Edit_State.WORLD_EDIT:
                self.randomize_fog()

        # Toggle Extra Lights
        elif event.type == 'E' and event.value == 'PRESS':
            if self.edit_state in {Edit_State.LIGHT_RIG, Edit_State.NON_ADDITIVE, Edit_State.JSON_EDIT, Edit_State.SINGLE_LIGHT}:
                if self.available_light_types == {'AREA'}:
                    self.available_light_types = {'AREA', 'SUN'}
                elif self.available_light_types == {'AREA', 'SUN'}:
                    self.available_light_types = {'AREA', 'SUN', 'POINT'}
                elif self.available_light_types == {'AREA', 'SUN', 'POINT'}:
                    self.available_light_types = {'AREA'}

                if self.master.should_build_fast_ui():
                    types = ""
                    for light_type in self.available_light_types:
                        types += str(light_type) + "  "
                    bpy.ops.hops.display_notification(info=f'{types}')

        # Increase light energy
        elif event.type in self.base_controls.keyboard_increment:
            if event.value == 'PRESS':
                if self.edit_state in {Edit_State.LIGHT_RIG, Edit_State.NON_ADDITIVE, Edit_State.JSON_EDIT}:
                    self.adjust_light_energy(increase=True)
                elif self.edit_state == Edit_State.SINGLE_LIGHT:
                    self.adjust_active_light_energy(True)
                elif self.edit_state == Edit_State.WORLD_EDIT:
                    self.world_opacity(.1)
            
        # Decrease light energy
        elif event.type in self.base_controls.keyboard_decrement:
            if event.value == 'PRESS':
                if self.edit_state in {Edit_State.LIGHT_RIG, Edit_State.NON_ADDITIVE, Edit_State.JSON_EDIT}:
                    self.adjust_light_energy(increase=False)
                elif self.edit_state == Edit_State.SINGLE_LIGHT:
                    self.adjust_active_light_energy(False)
                elif self.edit_state == Edit_State.WORLD_EDIT:
                    self.world_opacity(-.1)

        # Desaturate colors
        elif event.type == 'D' and event.value == 'PRESS':
            if self.edit_state in {Edit_State.LIGHT_RIG, Edit_State.NON_ADDITIVE, Edit_State.JSON_EDIT}:
                self.desaturate_light_colors()
            elif self.edit_state == Edit_State.SINGLE_LIGHT:
                self.adjust_saturation_active_light_colors(True)
            
        # Saturate colors / Save
        elif event.type == 'S' and event.value == 'PRESS':

            # Save JSON
            if event.shift == True:
                self.json_file_name = None
                self.json_getting_file_name = True

            if self.edit_state in {Edit_State.LIGHT_RIG, Edit_State.NON_ADDITIVE, Edit_State.JSON_EDIT}:
                self.saturate_light_colors()
            elif self.edit_state == Edit_State.SINGLE_LIGHT:
                self.adjust_saturation_active_light_colors(False)

        # Randomize colors
        elif event.type == 'C' and event.value == 'PRESS':
            if self.edit_state in {Edit_State.LIGHT_RIG, Edit_State.NON_ADDITIVE, Edit_State.JSON_EDIT}:
                self.randomize_light_colors()
            elif self.edit_state == Edit_State.SINGLE_LIGHT:
                self.set_random_light_color(self.active_light)
            elif self.edit_state == Edit_State.WORLD_EDIT:
                self.randomize_world_color()

        # Orbit colors / Set to light rig edit
        elif event.type == 'R' and event.value == 'PRESS':
            if self.edit_state == Edit_State.SINGLE_LIGHT:
                self.orbit_light_around_center(self.active_light, 18)
            elif self.edit_state == Edit_State.WORLD_EDIT:
                if event.shift == False:
                    self.rotate_world(-18)
                else:
                    self.rotate_world(18)
            elif self.edit_state == Edit_State.JSON_EDIT:
                self.edit_state = Edit_State.LIGHT_RIG

        # Adjust the Z height
        elif event.type == 'Z' and event.value == 'PRESS':
            if self.edit_state == Edit_State.SINGLE_LIGHT:
                if event.shift == False:
                    self.adjust_z_height(self.active_light, .5)
                else:
                    self.adjust_z_height(self.active_light, -.5)
            if self.edit_state == Edit_State.WORLD_EDIT:
                if event.shift == False:
                    self.z_location_world(-1)
                else:
                    self.z_location_world(1)

        # Add Eevee Bloom
        elif event.type == 'Q' and event.value == 'PRESS':
            bpy.context.scene.eevee.use_bloom = not bpy.context.scene.eevee.use_bloom
            bpy.context.scene.eevee.bloom_intensity = 1.04762
            bpy.context.scene.eevee.bloom_threshold = 1.94286
            self.report({'INFO'}, F'Bloom: {bpy.context.scene.eevee.use_bloom}')

        # Exit to viewport adjust
        elif event.type == 'V' and event.value == 'PRESS':
            self.exit_to_viewport_adjust = True

        # Toggle Ortho / Perspective
        elif event.type in {'P', 'NUMPAD_5'} and event.value == 'PRESS':
            bpy.ops.view3d.view_persportho()

        # Toggle volumetrics
        elif event.type == 'F' and event.value == 'PRESS':
            self.toggle_world_fog(context)

        # Switch to JSON Scroll
        elif event.type == 'J' and event.value == 'PRESS':
            self.switch_to_json_edit_mode(context=context)

        self.build_ui(context=context)

        return {'RUNNING_MODAL'}


    def build_ui(self, context):

        self.master.setup()

        #--- Fast UI ---#
        if self.master.should_build_fast_ui():

            win_list = []
            help_list = []
            mods_list = []
            active_mod = ""

            # Main
            point_lights = 0
            area_lights = 0
            sun_lights = 0

            for light in self.lights:
                if light.data.type == 'POINT':
                    point_lights += 1
                elif light.data.type == 'AREA':
                    area_lights += 1
                elif light.data.type == 'SUN':
                    sun_lights += 1

            if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1:
                win_list.append(f'P : {point_lights}')
                win_list.append(f'A : {area_lights}')
                win_list.append(f'S : {sun_lights}')
            else:
                win_list.append(f'Point Lights: {point_lights}')
                win_list.append(f'Area Lights: {area_lights}')
                win_list.append(f'Sun Lights: {sun_lights}')
            
            if self.exit_to_viewport_adjust:
                win_list.append(f'[V] To_Viewport {self.exit_to_viewport_adjust}')

            # Help
            #help_list.append(["V", "Exit to viewport adjust"])
            help_list.append(['V',              f'To_Viewport - {self.exit_to_viewport_adjust}'])
            help_list.append(["W",              "Set all lights to White"])
            help_list.append(["+ -",            "Adjust energy"])
            help_list.append(["D",              "Desaturate colors"])
            help_list.append(["S",              "Saturate colors"])
            help_list.append(['Q',              'Bloom'])
            help_list.append(['J',              'Cycle Configuration'])
            help_list.append(['Shift + S',      'Save Configuration'])
            help_list.append(["C",              "Randomize light colors"])
            help_list.append(["M",              "Toggle lights list"])
            help_list.append(["E",              "Toggle additional lights"])
            help_list.append(["5 / P",          "Toggle Ortho"])
            help_list.append(['F',              "Toggle Fog"])
            help_list.append(["H",              "Toggle help"])
            help_list.append(["Scroll",         "Next Blank Rig"])
            help_list.append(["Ctrl + Scroll",  "Switch light types"])
            help_list.append(["Shift + Scroll", "Adjust Scale"])
            help_list.append(["~",              "Toggle viewport displays"])
            help_list.append(["O",              "Toggle viewport rendering"])

            # Mods
            for light in self.lights:
                mods_list.append([light.name, ""])

            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="ArrayCircle", mods_list=mods_list, active_mod_name=active_mod)

        #--- Expanded ---#
        else:

            # Remove cursor warp
            if self.mouse_active == True:
                self.mouse_active = False
                self.remove_shader()
                
            #--- Main ---#
            main_win_form = Main_Panel_Form()

            if self.edit_state in {Edit_State.LIGHT_RIG, Edit_State.JSON_EDIT}:

                main_win_form.one_ON = True
                main_win_form.one_width_percent = 25
                main_win_form.one_image = "big_dice"
                main_win_form.one_func = self.randomize_all_lights
                main_win_form.one_positive_args = (context,)
                main_win_form.one_negative_args = (context,)
                main_win_form.one_drag = True

                main_win_form.two_ON = False

                main_win_form.three_ON = True
                main_win_form.three_width_percent = 37.5
                main_win_form.three_text = "Energy"
                main_win_form.three_func = self.sudo_event.alter_event
                main_win_form.three_positive_args = ('NUMPAD_PLUS', 'PRESS')
                main_win_form.three_negative_args = ('NUMPAD_MINUS', 'PRESS')
                main_win_form.three_drag = True

                main_win_form.four_ON = True
                main_win_form.four_text = "Saturation"
                main_win_form.four_func = self.sudo_event.alter_event
                main_win_form.four_positive_args = ('S', 'PRESS')
                main_win_form.four_negative_args = ('D', 'PRESS')
                main_win_form.four_drag = True

                main_win_form.five_ON = True
                main_win_form.five_width_percent = 37.5
                main_win_form.five_text = "White Out"
                main_win_form.five_func = self.sudo_event.alter_event
                main_win_form.five_positive_args = ('W', 'PRESS')

                main_win_form.six_ON = True
                main_win_form.six_text = "Colorize"
                main_win_form.six_func = self.sudo_event.alter_event
                main_win_form.six_positive_args = ('C', 'PRESS')
                main_win_form.six_negative_args = ('C', 'PRESS')
                main_win_form.six_drag = True

            elif self.edit_state == Edit_State.SINGLE_LIGHT:
                if self.active_light != None:

                    main_win_form.one_ON = True
                    main_win_form.one_width_percent = 25
                    main_win_form.one_image = "big_dice"
                    main_win_form.one_func = self.set_random_light_color
                    main_win_form.one_positive_args = (self.active_light,)
                    main_win_form.one_negative_args = (self.active_light,)
                    main_win_form.one_drag = True

                    main_win_form.two_ON = False

                    main_win_form.three_ON = True
                    main_win_form.three_width_percent = 37.5
                    main_win_form.three_text = "{:.0f}".format(self.active_light.data.energy)
                    main_win_form.three_image = ""
                    main_win_form.three_func = self.adjust_active_light_energy
                    main_win_form.three_positive_args = (True,)
                    main_win_form.three_negative_args = (False,)
                    main_win_form.three_drag = True

                    main_win_form.four_ON = True
                    main_win_form.four_text = "Saturation"
                    main_win_form.four_image = ""
                    main_win_form.four_func = self.adjust_saturation_active_light_colors
                    main_win_form.four_positive_args = (False,)
                    main_win_form.four_negative_args = (True,)
                    main_win_form.four_drag = True

                    z = "{:.2f}".format(self.active_light.location.z)
                    main_win_form.five_ON = True
                    main_win_form.five_width_percent = 37.5
                    main_win_form.five_text = f'Height: {z}'
                    main_win_form.five_image = ""
                    main_win_form.five_func = self.adjust_z_height
                    main_win_form.five_positive_args = (self.active_light, .5)
                    main_win_form.five_negative_args = (self.active_light, -.5)
                    main_win_form.five_drag = True

                    main_win_form.six_ON = True
                    main_win_form.six_text = "Orbit"
                    main_win_form.six_image = ""
                    main_win_form.six_func = self.orbit_light_around_center
                    main_win_form.six_positive_args = (self.active_light, 18)
                    main_win_form.six_negative_args = (self.active_light, -18)
                    main_win_form.six_drag = True

            elif self.edit_state == Edit_State.WORLD_EDIT:

                main_win_form.one_ON = True
                main_win_form.one_width_percent = 25
                main_win_form.one_text = ""
                main_win_form.one_image = "big_dice"
                main_win_form.one_func = self.randomize_fog
                main_win_form.one_positive_args = ("",)
                main_win_form.one_negative_args = ("",)
                main_win_form.one_drag = True

                main_win_form.two_ON = False

                main_win_form.three_ON = True
                main_win_form.three_width_percent = 37.5
                main_win_form.three_text = "Colorize"
                main_win_form.three_image = ""
                main_win_form.three_func = self.randomize_world_color
                main_win_form.three_positive_args = ("",)
                main_win_form.three_negative_args = ("",)
                main_win_form.three_drag = True

                main_win_form.four_ON = True
                main_win_form.four_text = "Rotate"
                main_win_form.four_image = ""
                main_win_form.four_func = self.rotate_world
                main_win_form.four_positive_args = (18,)
                main_win_form.four_negative_args = (-18,)
                main_win_form.four_drag = True

                main_win_form.five_ON = True
                main_win_form.five_width_percent = 37.5
                main_win_form.five_text = "Location"
                main_win_form.five_image = ""
                main_win_form.five_func = self.z_location_world
                main_win_form.five_positive_args = (1,)
                main_win_form.five_negative_args = (-1,)
                main_win_form.five_drag = True

                main_win_form.six_ON = True
                main_win_form.six_text = "Opacity"
                main_win_form.six_image = ""
                main_win_form.six_func = self.world_opacity
                main_win_form.six_positive_args = (.01,)
                main_win_form.six_negative_args = (-.01,)
                main_win_form.six_drag = True

            elif self.edit_state == Edit_State.NON_ADDITIVE:

                main_win_form.one_ON = True
                main_win_form.one_width_percent = 25
                main_win_form.one_image = "big_dice"
                main_win_form.one_func = self.randomize_all_lights_non_additive
                main_win_form.one_positive_args = (context,)
                main_win_form.one_negative_args = (context,)
                main_win_form.one_drag = True

                main_win_form.two_ON = False

                main_win_form.three_ON = True
                main_win_form.three_width_percent = 37.5
                main_win_form.three_text = "Energy"
                main_win_form.three_func = self.sudo_event.alter_event
                main_win_form.three_positive_args = ('NUMPAD_PLUS', 'PRESS')
                main_win_form.three_negative_args = ('NUMPAD_MINUS', 'PRESS')
                main_win_form.three_drag = True

                main_win_form.four_ON = True
                main_win_form.four_text = "Saturation"
                main_win_form.four_func = self.sudo_event.alter_event
                main_win_form.four_positive_args = ('S', 'PRESS')
                main_win_form.four_negative_args = ('D', 'PRESS')
                main_win_form.four_drag = True

                main_win_form.five_ON = True
                main_win_form.five_width_percent = 37.5
                main_win_form.five_text = "White Out"
                main_win_form.five_func = self.sudo_event.alter_event
                main_win_form.five_positive_args = ('W', 'PRESS')

                main_win_form.six_ON = True
                main_win_form.six_text = "Colorize"
                main_win_form.six_func = self.sudo_event.alter_event
                main_win_form.six_positive_args = ('C', 'PRESS')
                main_win_form.six_negative_args = ('C', 'PRESS')
                main_win_form.six_drag = True

            self.master.receive_main(win_dict={}, win_form=main_win_form)

            #--- Help ---#
            hot_keys_dict = {}
            if self.edit_state == Edit_State.LIGHT_RIG or self.edit_state == Edit_State.NON_ADDITIVE:
                hot_keys_dict["W"] = ["Set all lights to White", self.sudo_event.alter_event, ('W', 'PRESS')]
                hot_keys_dict["-"] = ["Subtract energy", self.sudo_event.alter_event, ('NUMPAD_MINUS', 'PRESS')]
                hot_keys_dict["+"] = ["Add energy", self.sudo_event.alter_event, ('NUMPAD_PLUS', 'PRESS')]
                hot_keys_dict["D"] = ["Desaturate colors", self.sudo_event.alter_event, ('D', 'PRESS')]
                hot_keys_dict["S"] = ["Saturate colors", self.sudo_event.alter_event, ('S', 'PRESS')]
                hot_keys_dict["C"] = ["Randomize light colors", self.sudo_event.alter_event, ('C', 'PRESS')]
                hot_keys_dict["E"] = ["Toggle extra lights", self.sudo_event.alter_event, ('E', 'PRESS')]
            
            elif self.edit_state == Edit_State.SINGLE_LIGHT:
                hot_keys_dict["Z + Shift"] = ["Adjust the height", self.sudo_event.alter_event, ('Z', 'PRESS', [('shift', True)])]
                hot_keys_dict["Z"] = ["Adjust the height", self.sudo_event.alter_event, ('Z', 'PRESS')]
                hot_keys_dict["-"] = ["Subtract energy", self.sudo_event.alter_event, ('NUMPAD_MINUS', 'PRESS')]
                hot_keys_dict["+"] = ["Add energy", self.sudo_event.alter_event, ('NUMPAD_PLUS', 'PRESS')]
                hot_keys_dict["D"] = ["Desaturate color", self.sudo_event.alter_event, ('D', 'PRESS')]
                hot_keys_dict["S"] = ["Saturate color", self.sudo_event.alter_event, ('S', 'PRESS')]
                hot_keys_dict["C"] = ["Randomize light color", self.sudo_event.alter_event, ('C', 'PRESS')]
                hot_keys_dict["R"] = ["Rotate 'Orbit' light", self.sudo_event.alter_event, ('R', 'PRESS')]
                hot_keys_dict["E"] = ["Toggle extra lights", self.sudo_event.alter_event, ('E', 'PRESS')]

            elif self.edit_state == Edit_State.WORLD_EDIT:
                hot_keys_dict["-"] = ["Subtract world opacity", self.sudo_event.alter_event, ('NUMPAD_MINUS', 'PRESS')]
                hot_keys_dict["+"] = ["Add world opacity", self.sudo_event.alter_event, ('NUMPAD_PLUS', 'PRESS')]
                hot_keys_dict["R + Shift"] = ["Rotate world counter clockwise", self.sudo_event.alter_event, ('R', 'PRESS', [('shift', True)])]
                hot_keys_dict["R"] = ["Rotate world clockwise", self.sudo_event.alter_event, ('R', 'PRESS')]
                hot_keys_dict["C"] = ["Colorize world", self.sudo_event.alter_event, ('C', 'PRESS')]
                hot_keys_dict["W"] = ["Randomize world", self.sudo_event.alter_event, ('W', 'PRESS')]
                hot_keys_dict["Z + Shift"] = ["Move world down", self.sudo_event.alter_event, ('Z', 'PRESS', [('shift', True)])]
                hot_keys_dict["Z"] = ["Move world up", self.sudo_event.alter_event, ('Z', 'PRESS')]

            elif self.edit_state == Edit_State.JSON_EDIT:
                hot_keys_dict["Scroll"] = ["Scroll files", self.sudo_event.alter_event, ('WHEELUPMOUSE', 'PRESS')]
                hot_keys_dict["R"] = ["Go to light rig edit", self.sudo_event.alter_event, ('R', 'PRESS')]

            # Add base help
            hot_keys_dict["J"] = ["JSON Configuration mode", self.sudo_event.alter_event, ('J', 'PRESS')]
            hot_keys_dict["Shift + S"] = ["Save Configuration", self.sudo_event.alter_event, ('S', 'PRESS', [('shift', True)])]
            hot_keys_dict["V"] = ["Exit to Viewport adjust", self.sudo_event.alter_event, ('V', 'PRESS')]
            hot_keys_dict["M"] = ["Toggle lights list", self.sudo_event.alter_event, ('M', 'PRESS')]
            hot_keys_dict["5 / P"] = ["Toggle Ortho", bpy.ops.view3d.view_persportho]
            hot_keys_dict["F"] = ["Toggle Fog", self.sudo_event.alter_event, ('F', 'PRESS')]
            hot_keys_dict["H"] = "Toggle help"
            hot_keys_dict["~"] = ["Toggle viewport overlays", self.sudo_event.alter_event, ('ACCENT_GRAVE', 'PRESS', [('shift', True)])]
            hot_keys_dict["O"] = ["Toggle viewport display", self.sudo_event.alter_event, ('O', 'PRESS', [('shift', True)])]
            self.master.receive_help(hot_keys_dict=hot_keys_dict)

            #--- Mods ---#
            win_dict = {}
            active_mod = ""
            if self.edit_state == Edit_State.SINGLE_LIGHT:
                active_mod = self.active_light.name
            if self.edit_state == Edit_State.JSON_EDIT:
                active_mod = self.json_current_file_name

            # Show regular lights list
            if self.edit_state != Edit_State.JSON_EDIT:
                for index, light in enumerate(self.lights):

                    mod_form = Mods_Panel_Form()

                    on_off_text = "O"
                    if light.hide_viewport:
                        on_off_text = "X"

                    mod_form.left_text = on_off_text
                    mod_form.left_func = self.toggle_light_hide
                    mod_form.left_positive_args = (light,)
                    mod_form.left_negative_args = None
                    mod_form.left_drag = False

                    mod_form.center_text = light.name
                    mod_form.center_func = self.set_edit_modes
                    mod_form.center_positive_args = (context, Edit_State.SINGLE_LIGHT, light)
                    mod_form.center_negative_args = (context, Edit_State.SINGLE_LIGHT, light)
                    mod_form.center_drag = True

                    mod_form.right_text = "{:.0f}".format(light.data.energy)
                    mod_form.right_func = self.adjust_active_light_energy
                    mod_form.right_positive_args = (True, light)
                    mod_form.right_negative_args = (False, light)
                    mod_form.right_drag = True

                    win_dict[light.name] = mod_form

            # Show json files
            else:
                for f_name in self.json_files:
                    mod_form = Mods_Panel_Form()
                    mod_form.left_text = f_name
                    mod_form.left_width_percent = 100
                    mod_form.left_func = self.load_specified_json_file
                    mod_form.left_positive_args = (context, f_name,)
                    mod_form.left_negative_args = None
                    mod_form.left_drag = False
                    win_dict[f_name] = mod_form

            if self.edit_state == Edit_State.LIGHT_RIG or self.edit_state == Edit_State.NON_ADDITIVE:
                active_mod = "Light Rig Edit"
            elif self.edit_state == Edit_State.WORLD_EDIT:
                active_mod = "World Edit"

            # Edit rig
            mod_form = Mods_Panel_Form()
            mod_form.left_width_percent = 33.33
            mod_form.left_text = "Rig Rotation"
            mod_form.left_func = self.rotate_rig
            mod_form.left_positive_args = (18, )
            mod_form.left_negative_args = (-18, )
            mod_form.left_drag = True

            mod_form.center_width_percent = 33.33
            mod_form.center_text = "Rig Scale"
            mod_form.center_func = self.scale_rig
            mod_form.center_positive_args = (.125,)
            mod_form.center_negative_args = (-.125,)
            mod_form.center_drag = True

            mod_form.right_width_percent = 33.33
            mod_form.right_text = "Rig Loc"
            mod_form.right_func = self.loc_z_rig
            mod_form.right_positive_args = (.25,)
            mod_form.right_negative_args = (-.25,)
            mod_form.right_drag = True

            win_dict["RigEdit"] = mod_form

            # Edit modes
            mod_form = Mods_Panel_Form()
            mod_form.left_width_percent = 33.333
            mod_form.left_text = "Light Rig"
            mod_form.left_func = self.set_edit_modes
            mod_form.left_positive_args = (context, Edit_State.LIGHT_RIG, )
            mod_form.left_negative_args = None
            mod_form.left_drag = False

            mod_form.center_width_percent = 33.333
            mod_form.center_text = "World"
            mod_form.center_func = self.set_edit_modes
            mod_form.center_positive_args = (context, Edit_State.WORLD_EDIT, )
            mod_form.center_negative_args = None
            mod_form.center_drag = False

            mod_form.right_width_percent = 33.333
            mod_form.right_text = "Configs"
            mod_form.right_func = self.switch_to_json_edit_mode
            mod_form.right_positive_args = (context, )
            mod_form.right_negative_args = None
            mod_form.right_drag = False

            win_dict["EditModes"] = mod_form

            # Use this to prevent scrolling up while triggering buttons
            body_scroll = True
            if self.edit_state == Edit_State.SINGLE_LIGHT:
                body_scroll = False

            self.master.receive_mod(win_dict=win_dict, active_mod_name=active_mod, rename_window="Lights", body_scroll=body_scroll)

        self.master.finished()

    ####################################################
    #   CURSOR WARP
    ####################################################

    def safe_draw_shader(self, context):
        method_handler(self.draw_shader,
            arguments = (context,),
            identifier = 'UI Framework',
            exit_method = self.remove_shader)


    def remove_shader(self):
        '''Remove shader handle.'''

        if self.draw_handle:
            self.draw_handle = bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle, "WINDOW")


    def draw_shader(self, context):
        '''Draw shader handle.'''

        draw_modal_frame(context)

    ####################################################
    #   EXPANDED MODE FUNCTIONS
    ####################################################

    def set_edit_modes(self, context, mode, light=None):
        '''Set the edit mode Params: mode = Edit_State'''

        if self.sudo_event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            if self.edit_state == Edit_State.SINGLE_LIGHT:
                if self.active_light != None:
                    self.toggle_single_light_type(light=self.active_light)

        # Lock out light rig edit
        if self.start_mode == Edit_State.NON_ADDITIVE:
            if mode == Edit_State.LIGHT_RIG:
                self.edit_state = Edit_State.NON_ADDITIVE
            else:
                self.edit_state = mode
        else:
            self.edit_state = mode

        # Setup for single light mode
        if mode == Edit_State.SINGLE_LIGHT:
            if light != None:
                for t_light in self.lights:
                    t_light.select_set(False)

                context.view_layer.update()
                light.select_set(True)
                context.view_layer.objects.active = light
                self.active_light = light
        # Deselect lights when not in light edit mode
        else:
            self.active_light = None
            for t_light in self.lights:
                t_light.select_set(False)
            context.view_layer.objects.active = None

        # Setup for world edit
        if mode == Edit_State.WORLD_EDIT:
            self.setup_world_edit_mode(context)

    #--- World Edit Mode ---#
    def setup_world_edit_mode(self, context: bpy.context):
        '''Creates the initial world setup.'''

        if self.ran_world_setup:
            return

        bpy.context.scene.eevee.use_volumetric_lights = True
        bpy.context.scene.eevee.use_volumetric_shadows = True
        bpy.context.scene.world.use_nodes = True
        bpy.context.space_data.shading.use_scene_lights = True
        bpy.context.space_data.shading.use_scene_world = True

        # Data
        group_name = "HOPS WORLD"
        world_output = None

        # Search for the node group and remove it if found
        node_tree = context.scene.world.node_tree
        nodes = node_tree.nodes
        for node in nodes:
            if node.type == 'GROUP':
                if node.name == group_name:
                    node_tree.nodes.remove(node)
                    break

        # Remove the node group from the blend data
        for tree in bpy.data.node_groups:
            if tree.name == group_name:
                bpy.data.node_groups.remove(tree)

        # Get the world output
        for node in nodes:
            if node.type == 'OUTPUT_WORLD':
                world_output = node

        # If the world output was not found
        if world_output == None:
            node_tree.nodes.new('ShaderNodeOutputWorld')

        # Create the node group
        self.create_volume_node_group(group_name=group_name)

        # Insert node group into world node tree
        volume_group = node_tree.nodes.new("ShaderNodeGroup")
        volume_group.node_tree = bpy.data.node_groups[group_name]
        volume_group.location = (world_output.location[0] - 250, world_output.location[1] - 100)
        volume_group.name = group_name

        # Link : Volume -> World
        node_tree.links.new(volume_group.outputs['shader_out'], world_output.inputs['Volume'])

        self.ran_world_setup = True


    def create_volume_node_group(self, group_name=""):
        '''Creates the volume node group and insert it into the blend data'''

        # Create : Group
        node_group = bpy.data.node_groups.new(group_name, 'ShaderNodeTree')

        # Create : Group Outputs
        group_outputs = node_group.nodes.new('NodeGroupOutput')
        group_outputs.location = (700,0)
        node_group.outputs.new('NodeSocketShader','shader_out')
        
        # Create : Group Inputs
        group_inputs = node_group.nodes.new('NodeGroupInput')
        group_inputs.location = (-700,200)
        node_group.inputs.new('NodeSocketFloat','density')
        node_group.inputs.new('NodeSocketFloat','scale_one')
        node_group.inputs.new('NodeSocketFloat','scale_two')

        node_group.inputs['density'].min_value = 0
        node_group.inputs['density'].max_value = 1
        node_group.inputs['density'].default_value = 1

        node_group.inputs['scale_one'].min_value = 0
        node_group.inputs['scale_one'].max_value = 2
        node_group.inputs['scale_one'].default_value = .05

        node_group.inputs['scale_two'].min_value = 0
        node_group.inputs['scale_two'].max_value = 2
        node_group.inputs['scale_two'].default_value = .25

        # Create : Texture Coords
        text_coords_node = node_group.nodes.new('ShaderNodeTexCoord')
        text_coords_node.location = (-700,0)

        # Create : Mapping
        mapping_node = node_group.nodes.new('ShaderNodeMapping')
        mapping_node.inputs['Scale'].default_value = (.2, .2, 1)
        mapping_node.location = (-500,0)

        # Create : Musgrave One
        musgrave_node_one = node_group.nodes.new('ShaderNodeTexMusgrave')
        musgrave_node_one.musgrave_type = 'RIDGED_MULTIFRACTAL'
        musgrave_node_one.inputs['Scale'].default_value = .05
        musgrave_node_one.inputs['Offset'].default_value = .25
        musgrave_node_one.location = (-300,-200)

        # Create : Musgrave Two
        musgrave_node_two = node_group.nodes.new('ShaderNodeTexMusgrave')
        musgrave_node_two.musgrave_type = 'RIDGED_MULTIFRACTAL'
        musgrave_node_two.inputs['Scale'].default_value = .25
        musgrave_node_two.inputs['Offset'].default_value = .3
        musgrave_node_two.location = (-300,200)

        # Create : Mix
        mix_node = node_group.nodes.new('ShaderNodeMixRGB')
        mix_node.blend_type = 'MIX'
        mix_node.inputs['Color2'].default_value = (.2,.2,.2,1)
        mix_node.location = (0,0)

        # Create : Mix Density
        mix_density = node_group.nodes.new('ShaderNodeMixRGB')
        mix_density.blend_type = 'MIX'
        mix_density.inputs['Color1'].default_value = (0,0,0,1)
        mix_density.location = (250,0)

        # Create : Volume Scatter
        volume_node = node_group.nodes.new('ShaderNodeVolumeScatter')
        volume_node.location = (450,0)

        # Links
        node_group.links.new(text_coords_node.outputs['Generated'], mapping_node.inputs['Vector'])
        node_group.links.new(mapping_node.outputs['Vector'], musgrave_node_two.inputs['Vector'])
        node_group.links.new(mapping_node.outputs['Vector'], musgrave_node_one.inputs['Vector'])
        node_group.links.new(musgrave_node_one.outputs['Fac'], mix_node.inputs['Color1'])
        node_group.links.new(musgrave_node_two.outputs['Fac'], mix_node.inputs['Fac'])
        node_group.links.new(mix_node.outputs['Color'], mix_density.inputs['Color2'])
        node_group.links.new(mix_density.outputs['Color'], volume_node.inputs['Density'])
        node_group.links.new(volume_node.outputs['Volume'], group_outputs.inputs['shader_out'])
        # Inputs
        node_group.links.new(group_inputs.outputs['density'], mix_density.inputs['Fac'])
        node_group.links.new(group_inputs.outputs['scale_one'], musgrave_node_one.inputs['Scale'])
        node_group.links.new(group_inputs.outputs['scale_two'], musgrave_node_two.inputs['Scale'])


    def randomize_fog(self, dummy=""):
        '''Randomize the fog.'''

        node_tree = bpy.context.scene.world.node_tree
        nodes = node_tree.nodes
        hops_group = nodes['HOPS WORLD']

        for node in hops_group.node_tree.nodes:
            if node.name == 'Mapping':
                node.inputs['Scale'].default_value = (random.uniform(.25, 1), random.uniform(.25, 1), 1)
            elif node.name == "Group Input":
                node.outputs['scale_one'].default_value = random.uniform(.001, .1)
                node.outputs['scale_two'].default_value = random.uniform(.001, .3)
            elif node.name == 'Musgrave Texture':
                node.inputs['Offset'].default_value = random.uniform(.05, .35)
            elif node.name == 'Musgrave Texture.001':
                node.inputs['Offset'].default_value = random.uniform(.001, .4)
            elif node.name == 'Mix':
                col = random.uniform(.05, .5)
                node.inputs['Color2'].default_value = (col,col,col,1)
            elif node.name == 'Volume Scatter':
                col = random.uniform(.05, .5)
                node.inputs['Color'].default_value = (col,col,col,1)
                node.inputs['Anisotropy'].default_value = random.uniform(0, .8)


    def randomize_world_color(self, dummy=""):
        '''Randomize the world color.'''

        node_tree = bpy.context.scene.world.node_tree
        nodes = node_tree.nodes
        hops_group = nodes['HOPS WORLD']

        for node in hops_group.node_tree.nodes:
            if node.name == 'Volume Scatter':
                node.inputs['Color'].default_value = (random.uniform(.5, 1), random.uniform(.5, 1), random.uniform(.5, 1) ,1)
                break


    def rotate_world(self, rot=18):
        '''Rotate the fog.'''

        node_tree = bpy.context.scene.world.node_tree
        nodes = node_tree.nodes
        hops_group = nodes['HOPS WORLD']

        for node in hops_group.node_tree.nodes:
            if node.name == 'Mapping':
                node.inputs['Rotation'].default_value.z += rot
                break


    def z_location_world(self, z_loc=5):
        '''Adjust the z location of the world.'''

        node_tree = bpy.context.scene.world.node_tree
        nodes = node_tree.nodes
        hops_group = nodes['HOPS WORLD']

        for node in hops_group.node_tree.nodes:
            if node.name == 'Mapping':
                node.inputs['Location'].default_value.z += z_loc
                break

    
    def world_opacity(self, opacity=.1):
        '''Adjust the opacity of the world.'''

        node_tree = bpy.context.scene.world.node_tree
        nodes = node_tree.nodes
        hops_group = nodes['HOPS WORLD']

        for node in hops_group.node_tree.nodes:
            if node.name == 'Volume Scatter':
                node.inputs['Color'].default_value[0] += opacity
                node.inputs['Color'].default_value[1] += opacity
                node.inputs['Color'].default_value[2] += opacity
                break

    #--- Single Light Edit Mode ---#
    def set_active_light_to_white(self):
        '''Sets active light color values to white.'''

        if self.active_light != None:
            self.active_light.data.color = (1, 1, 1)        


    def orbit_light_around_center(self, light, orbit_angle=18):
        '''Orbit the light around the center of the empty.'''

        vec_2 = Vector((
            light.location.x,
            light.location.y))
        
        offset = vec_2.magnitude

        vec_2.normalize()

        radius = vec_2.magnitude
        light_angle = math.degrees(math.atan2( vec_2[1], vec_2[0] ))

        if light_angle < 0:
            light_angle = 360 + light_angle

        light_angle += orbit_angle

        x = offset * math.cos(math.radians(light_angle))
        y = offset * math.sin(math.radians(light_angle))
        
        light.location.x = x
        light.location.y = y

        # Rotation
        up_vec = Vector((0, 0, 1))
        euler_rot = up_vec.rotation_difference(light.location).to_euler()
        light.rotation_euler = euler_rot


    def toggle_light_hide(self, light):
        '''Toggle the light visibility.'''

        light.hide_viewport = not light.hide_viewport
        light.hide_render = light.hide_viewport


    def adjust_z_height(self, light, z_offset=0):
        '''Moves the light up or down.'''

        light.location.z += z_offset

        location = light.location
        up_vec = Vector((0, 0, 1))
        euler_rot = up_vec.rotation_difference(location).to_euler()
        light.rotation_euler = euler_rot


    def adjust_active_light_energy(self, increase=True, other_light=None):
        '''Increase the energy of each light based on increase.'''

        light = None
        if other_light != None:
            light = other_light
        else:
            light = self.active_light

        if light != None:

            if light.data.type == 'POINT':
                value = 100 if increase else -(light.data.energy / 15)
                light.data.energy += value

            elif light.data.type == 'AREA':
                value = 100 if increase else -(light.data.energy / 15)
                light.data.energy += value

            elif light.data.type == 'SUN':
                value = .25 if increase else -(light.data.energy / 15)
                light.data.energy += value

            if light.data.energy < 0:
                light.data.energy = 0


    def adjust_saturation_active_light_colors(self, desaturate=False):
        '''Saturate the light colors by moving values to its closer side.'''

        if desaturate == True:
            if self.active_light != None:
                for index, value in enumerate(self.active_light.data.color):
                    diff = 1 - value
                    if diff > 0:
                        self.active_light.data.color[index] += diff / 10

        else:
            if self.active_light != None:
                if self.active_light.data.color.s < 1:
                    diff = 1 - self.active_light.data.color.s
                    self.active_light.data.color.s += diff / 10


    def toggle_single_light_type(self, light=None):
        '''Toggle the single light type.'''

        types = list(self.available_light_types)

        if light.data.type in types:
            index = types.index(light.data.type)
            light.data.type = types[(index + 1) % len(types)]
        else:
            light.data.type = types[0]

        if light.data.type == 'POINT':
            light.name = "HOPS_LIGHT_POINT"
            light.data.energy = random.uniform(50, 1000)
            light.data.shadow_soft_size = .25

        elif light.data.type == 'AREA':
            light.name = "HOPS_LIGHT_AREA"
            light.data.size = random.uniform(1, 10)
            light.data.energy = random.uniform(50, 7000)

        elif light.data.type == 'SUN':
            light.name = "HOPS_LIGHT_SUN"
            light.data.energy = random.uniform(1, 5)    

    #--- Rig Editor ---#
    def rotate_rig(self, amount=18):
        '''Rotate the rig empty.'''

        if self.empty != None:
            self.empty.rotation_euler.z += math.radians(amount)


    def scale_rig(self, scale=1):
        '''Rotate the rig empty.'''

        if self.empty != None:
            self.empty.scale += Vector((scale, scale, scale))


    def loc_z_rig(self, amount=1):
        '''Rotate the rig empty.'''

        if self.empty != None:
            self.empty.location.z += amount

    ####################################################
    #   HIGH LEVEL -RIG- FUNCTIONS
    ####################################################

    def get_light_empty(self, context, with_create_new=True, at_cursor=False):
        '''Get the light collection or return the exsisting one.'''

        empty_name = "HOPS Light Empty"
        new_empty = None
        collection = context.collection

        # Check if the empty exsist
        for obj in collection.objects:
            if obj.name[:16] == empty_name:
                new_empty = obj
                break

        # Used for initial data storing
        if with_create_new == False:
            if new_empty == None:
                return None
            else:
                return new_empty

        # If no empty was in the collection make a new empty
        if new_empty == None:
            new_empty = bpy.data.objects.new(empty_name, None )
            context.collection.objects.link(new_empty)
            new_empty.empty_display_size = .5
            new_empty.empty_display_type = 'SPHERE'

        # Store it
        self.empty = new_empty

        # Locate it
        if self.edit_state != Edit_State.NON_ADDITIVE:
            self.empty.location = context.scene.cursor.location


    def get_lights(self):
        '''Get all the light objects on parent object.'''

        new_lights = []

        for obj in self.empty.children:
            if obj.type == 'LIGHT':
                new_lights.append(obj)

        self.lights = new_lights


    def randomize_all_lights(self, context):
        '''Delete all the lights and rebuild everything randomly.'''

        for light in self.lights:
            bpy.data.lights.remove(light.data)

        self.lights = []

        for light_type in self.available_light_types:

            # Add random area lights
            if light_type == 'AREA':
                self.lights += self.add_random_area_lights(context)

            # Add random sun lights
            elif light_type == 'SUN':
                self.lights += self.add_random_sun_lights(context)

            # Add random point lights
            elif light_type == 'POINT':
                self.lights += self.add_random_point_lights(context)


    def randomize_all_lights_non_additive(self, context):
        '''Randomize all the lights in non additive mode.'''

        self.switch_light_types(context, use_random=True)
        for light in self.lights:
            self.set_random_light_color(light)


    def switch_light_types(self, context, use_random=False):
        '''Keeps the lights in place but switches there type and resets the energy.'''


        for light in self.lights:

            types = list(self.available_light_types)

            # Remove the current light from the list
            if use_random == False:
                if len(types) > 1:
                    if light.data.type in types:
                        index = types.index(light.data.type)
                        light.data.type = types[(index + 1) % len(types)]
                    else:
                        light.data.type = types[0]
            else:
                if len(types) > 1:
                    ran_index = random.randint(0, len(types) - 1)

                    # Make it harder for a sun to happen
                    if types[ran_index] == 'SUN':
                        pick = random.randint(0, 20)
                        if pick < 7:
                            light.data.type = 'SUN'
                        else:
                            light.data.type = 'AREA'

                    else:
                        light.data.type = types[ran_index]


                elif len(types) == 1:
                    light.data.type = types[0]

            if light.data.type == 'POINT':
                light.name = "HOPS_LIGHT_POINT"
                light.data.energy = random.uniform(50, 1000)
                light.data.shadow_soft_size = .25

            elif light.data.type == 'AREA':
                light.name = "HOPS_LIGHT_AREA"
                light.data.size = random.uniform(1, 10)
                light.data.energy = random.uniform(50, 7000)

            elif light.data.type == 'SUN':
                light.name = "HOPS_LIGHT_SUN"
                light.data.energy = random.uniform(1, 5)   


    def add_random_point_lights(self, context):
        '''Create point lights.'''

        lights = []

        light_count = random.randint(0, 6)
        radius = random.uniform(10, 30)

        # Place in circle
        for i in range(light_count):

            # Sweep angle
            angle = i * math.pi * 2 / light_count
            angle += random.uniform(-.5, .5)

            # Location
            x_loc = cos(angle) * radius
            y_loc = sin(angle) * radius
            z_loc = random.uniform(2, 6)
            location = (x_loc, y_loc, z_loc)

            # Create light
            new_light = self.add_light(context, location=location, light_type='POINT')

            # Color
            self.set_random_light_color(new_light)

            # Energy
            new_light.data.energy = random.uniform(50, 1000)

            # Store
            lights.append(new_light)

        return lights


    def add_random_sun_lights(self, context):
        '''Create sun lights.'''

        lights = []

        light_count = 0
        if len(self.available_light_types) > 2:
            light_count = random.randint(0, 3)
        else:
            light_count = random.randint(0, 1)

        radius = random.uniform(15, 20)

        # Place in circle
        for i in range(light_count):

            # Sweep angle
            angle = i * math.pi * 2 / light_count
            angle += random.uniform(-.5, .5)

            # Location
            x_loc = cos(angle) * radius
            y_loc = sin(angle) * radius
            z_loc = random.uniform(.5, 30)
            location = (x_loc, y_loc, z_loc)

            # Create light
            new_light = self.add_light(context, location=location, light_type='SUN')

            # Color
            self.set_random_light_color(new_light)

            # Energy
            new_light.data.energy = random.uniform(1, 5)

            # Rotation
            up_vec = Vector((0, 0, 1))
            euler_rot = up_vec.rotation_difference(location).to_euler()
            new_light.rotation_euler = euler_rot

            # Store
            lights.append(new_light)

        return lights


    def add_random_area_lights(self, context):
        '''Create sun lights.'''

        lights = []

        light_count = random.randint(1, 4)
        radius = random.uniform(15, 20)

        # Place in circle
        for i in range(light_count):

            # Sweep angle
            angle = i * math.pi * 2 / light_count
            angle += random.uniform(-.5, .5)

            # Location
            x_loc = cos(angle) * radius
            y_loc = sin(angle) * radius
            z_loc = random.uniform(.5, 30)
            location = (x_loc, y_loc, z_loc)

            # Create light
            new_light = self.add_light(context, location=location, light_type='AREA')

            # Color
            self.set_random_light_color(new_light)

            # Energy
            new_light.data.energy = random.uniform(50, 7000)

            # Size
            new_light.data.size = random.uniform(1, 10)

            # Rotation
            up_vec = Vector((0, 0, 1))
            euler_rot = up_vec.rotation_difference(location).to_euler()
            new_light.rotation_euler = euler_rot

            # Store
            lights.append(new_light)

        return lights


    def rotate_light_rig(self, angle=0):
        '''Rotate the light rig.'''

        if self.empty != None:
            self.empty.rotation_euler.z += angle

    ####################################################
    #   LOWER LEVEL FUNCTIONS
    ####################################################

    def add_light(self, context, location=(0,0,0), look_target=(0,0,0), light_type='POINT'):
        '''Create a new light, return light ID.'''

        light_data = bpy.data.lights.new(name='HOPS_Light_Data', type=light_type)
        light_obj = bpy.data.objects.new(f'HOPS_LIGHT_{light_type}', object_data=light_data)
        light_obj.location = location
        light_obj.data.use_contact_shadow = True
        context.collection.objects.link(light_obj)
        light_obj.parent = self.empty

        if get_preferences().property.to_light_constraint:
            con = light_obj.constraints.new(type='TRACK_TO')
            con.target = self.empty
            con.up_axis = 'UP_Y'
            con.track_axis = 'TRACK_NEGATIVE_Z'

        return light_obj


    def set_random_light_color(self, light):
        '''Set light color.'''

        r = random.uniform(0, 1)
        g = random.uniform(0, 1)
        b = random.uniform(0, 1)
        light.data.color = (r, g, b)


    def set_all_colors_to_white(self):
        '''Sets all the color values to white.'''

        for light in self.lights:
            light.data.color = (1, 1, 1)
            

    def adjust_light_energy(self, increase=True):
        '''Increase the energy of each light based on increase.'''

        for light in self.lights:

            if light.data.type == 'POINT':
                value = 100 if increase else -(light.data.energy / 15)
                light.data.energy += value

            elif light.data.type == 'AREA':
                value = 100 if increase else -(light.data.energy / 15)
                light.data.energy += value

            elif light.data.type == 'SUN':
                value = .25 if increase else -(light.data.energy / 15)
                light.data.energy += value

            if light.data.energy < 0:
                light.data.energy = 0


    def desaturate_light_colors(self):
        '''Desaturate the light colors by moving values to white.'''

        for light in self.lights:
            for index, value in enumerate(light.data.color):
                diff = 1 - value
                if diff > 0:
                    light.data.color[index] += diff / 10


    def saturate_light_colors(self):
        '''Saturate the light colors by moving values to its closer side.'''

        for light in self.lights:
            if light.data.color.s < 1:
                diff = 1 - light.data.color.s
                light.data.color.s += diff / 10


    def randomize_light_colors(self):
        '''Randomize the light colors.'''

        for light in self.lights:
            self.set_random_light_color(light)


    def toggle_world_fog(self, context):
        '''Toggle the world fog values.'''

        if hasattr(self, 'set_fog_off') == False:
            self.set_fog_off = True

        node_tree = bpy.context.scene.world.node_tree
        nodes = node_tree.nodes
        if 'HOPS WORLD' in nodes:
            hops_group = nodes['HOPS WORLD']

            for node in hops_group.node_tree.nodes:
                if node.name == 'Volume Scatter':
                    node.inputs['Color'].default_value[0] = 0 if self.set_fog_off else 1
                    node.inputs['Color'].default_value[1] = 0 if self.set_fog_off else 1
                    node.inputs['Color'].default_value[2] = 0 if self.set_fog_off else 1
                    break

        else:
            self.setup_world_edit_mode(context=context)
            self.set_fog_off = False

        self.set_fog_off = not self.set_fog_off

    ####################################################
    #   RECOVERY FUNCTIONS
    ####################################################

    def capture_initial_state(self, context):
        '''Capture all the settings from the intitial build.'''

        self.initial_light_data = []
        self.initial_empty_data = None
        empty = self.get_light_empty(context, with_create_new=False)

        # No light empty was found : will remove every thing on cancel
        if empty == None:
            return
        else:
            class Empty_Data:
                def __init__(self):
                    self.name = None
                    self.loc = None
                    self.scale = None
                    self.rot = None

            self.initial_empty_data = Empty_Data()
            self.initial_empty_data.name = empty.name
            self.initial_empty_data.loc = (empty.location[0], empty.location[1], empty.location[2])
            self.initial_empty_data.scale = (empty.scale[0], empty.scale[1], empty.scale[2])
            self.initial_empty_data.rot = (empty.rotation_euler[1], empty.rotation_euler[1], empty.rotation_euler[2])
                
        # Copy light data from original lights
        for obj in empty.children:
            if obj.type == 'LIGHT':
                light_data = self.get_initial_light_data(obj)
                if light_data != None:
                    self.initial_light_data.append(light_data)


    def restore_initial_state(self, context):
        '''Revert back all the changes made in the modal on cancel.'''

        # Delete everything since it started with nothing
        if self.initial_empty_data == None:
            for light in self.lights:
                bpy.data.lights.remove(light.data)
            bpy.data.objects.remove(self.empty)

        # Revert back to original state
        else:
            # Make sure no errors occured
            if self.empty == None:
                return

            # Revert the empty
            self.empty.name = self.initial_empty_data.name
            self.empty.location = self.initial_empty_data.loc
            self.empty.scale = self.initial_empty_data.scale
            self.empty.rotation_euler = self.initial_empty_data.rot

            # Remove all the modified lights
            for light in self.lights:
                bpy.data.lights.remove(light.data)

            # Add back the original lights
            for light_data in self.initial_light_data:
                light = self.add_light(
                    context,
                    location=light_data.loc,
                    look_target=self.empty.location,
                    light_type=light_data.type)

                light.name = light_data.name
                light.data.energy = light_data.energy
                light.data.color = light_data.color
                # create a location matrix
                mat_loc = Matrix.Translation(light_data.loc)
                # create an identitiy matrix
                mat_sca = Matrix.Scale(1, 4, light_data.scale)
                # create a rotation matrix
                mat_rot = light_data.rot.to_matrix()
                mat_rot = mat_rot.to_4x4()

                # combine transformations
                mat_out = mat_loc @ mat_rot @ mat_sca

                light.matrix_local = mat_out


    def get_initial_light_data(self, light):
        '''Create a copy of all the light data for the light.'''

        # Validate type and data members
        validated = False
        if hasattr(light, 'type'):
            if light.type == 'LIGHT':
                if hasattr(light, 'data'):
                    if hasattr(light.data, 'energy'):
                        if hasattr(light.data, 'color'):
                            validated = True

        if validated == False:
            return None

        class Light_Data:
            def __init__(self):
                self.name = None
                self.type = None
                self.energy = None
                self.color = None
                self.loc = None
                self.scale = None
                self.rot = None

        light_data = Light_Data()
        light_data.name = light.name
        light_data.type = light.data.type
        light_data.energy = light.data.energy
        light_data.color = (light.data.color[0], light.data.color[1], light.data.color[2])
        light_data.loc = (light.location[0], light.location[1], light.location[2])
        light_data.scale = (light.scale[0], light.scale[1], light.scale[2])
        light_data.rot = light.matrix_local.decompose()[1]
        return light_data

    ####################################################
    #   JSON FUNCTIONS
    ####################################################

    #--- MODAL CONTROLS ---#
    def switch_to_json_edit_mode(self, context):
        '''Save the current light rig configuration and switch to first json file object.'''

        self.json_files = self.get_json_file_names()
        if self.json_files == []:
            bpy.ops.hops.display_notification(info="No Light files found : Shift + S to save lights.")
            return

        self.edit_state = Edit_State.JSON_EDIT
        self.json_data = None
        self.get_next_json_configuration(context=context)


    def get_next_json_configuration(self, context, forward=True):
        '''Get the next configuration from the json file.'''

        # Validate file dirs
        self.json_file_dirs = self.get_json_file_dirs()
        if len(self.json_file_dirs) < 1:
            bpy.ops.hops.display_notification(info='No Light files.')
            return

        # Set current file
        if self.json_current_file == None:
            self.json_current_file = self.json_file_dirs[0]

        # Go to next file
        else:
            # Keep moving
            if self.json_current_file in self.json_file_dirs:
                index = self.json_file_dirs.index(self.json_current_file)
                increment = 1 if forward else -1
                self.json_current_file = self.json_file_dirs[(index + increment) % len(self.json_file_dirs)]
            # File was not there restart
            else:
                self.json_current_file = self.json_file_dirs[0]

        # Set the file name
        file_with_extension = os.path.basename(self.json_current_file)
        self.json_current_file_name = file_with_extension.split('.')[0]

        # Open file for write
        self.json_data = None 
        with open(self.json_current_file, 'r') as json_file:
            self.json_data = json.load(json_file)

        # Load data
        if self.json_data != None:
            self.setup_rig_to_match_json_data(context, self.json_data)
            head, tail = file_name = os.path.split(self.json_current_file)
            if self.master.should_build_fast_ui():
                bpy.ops.hops.display_notification(info=F'{tail.split(".")[0]}')
        else:
            bpy.ops.hops.display_notification(info=F'ERROR: Bad Data @ {self.json_current_file}')


    def setup_rig_to_match_json_data(self, context, data={}):
        '''Setup the light rig to math the json data.'''

        # Clear the lights out
        for light in self.lights:
            bpy.data.lights.remove(light.data)
        self.lights = []

        for light_name, props_dict in data.items():
            if type(props_dict) != dict:
                print("Props for key are invalid")
                continue

            # Validate
            validated = False
            if "type" in props_dict:
                if "loc" in props_dict:
                    validated = True
            if validated == False:
                continue

            light = self.add_light(
                context,
                location=props_dict['loc'],
                look_target=self.empty.location,
                light_type=props_dict['type'])

            # Validate
            validated = False
            if "rot" in props_dict:
                if "scale" in props_dict:
                    if "color" in props_dict:
                        if "energy" in props_dict:
                            if "size" in props_dict:
                                validated = True
            if validated == False:
                continue

            light.rotation_euler = props_dict['rot']
            light.scale = props_dict['scale']
            light.data.color = props_dict['color']
            light.data.energy = props_dict['energy']

            if hasattr(light.data, 'size'):
                light.data.size = props_dict['size']

            self.lights.append(light)

    #--- JSON FILE SAVE SYSTEMS ---#
    def save_json_file_with_user_input(self, context, event):
        '''Freeze the modal and take input.'''

        # Add draw handle
        if not hasattr(self, 'json_draw_handle'):
            self.json_draw_handle = None
            
        if self.json_draw_handle == None:
            self.json_draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.safe_draw_file_name, (context,), 'WINDOW', 'POST_PIXEL')

        # Cancelled
        if event.type in cancel and event.value == 'PRESS':
            self.json_getting_file_name = False
            # Remove shader
            self.remove_file_name_shader()
            bpy.ops.hops.display_notification(info="Cancelled")
            return

        # Finished
        if event.type in completed and event.value == 'PRESS':
            if self.json_file_name == None or self.json_file_name == "":
                form = '%B %d %Y - %H %M %S %f'
                self.json_file_name = datetime.now().strftime(form)
            self.json_getting_file_name = False

        # Append
        elif event.ascii not in invalid and event.value == 'PRESS':
            if self.json_file_name == None:
                self.json_file_name = ""
            
            self.json_file_name += event.ascii

        # Backspace
        if event.type == 'BACK_SPACE' and event.value == 'PRESS':
            if self.json_file_name != None:
                self.json_file_name = self.json_file_name[:len(self.json_file_name)-1]
            else:
                self.json_file_name = ""

        # Completed Input : SAVE FILE
        if self.json_getting_file_name == False:
            # Remove shader
            self.remove_file_name_shader()
            # Save the file
            self.save_rig_to_json(context=context)
            bpy.ops.hops.display_notification(info="File Saved!")

        # Set text to draw
        if self.json_file_name == None:
            self.json_shader_file_text = "Auto"
        else:
           self.json_shader_file_text = self.json_file_name

        # Hack for the UI
        self.sudo_event.update(event)
        event = self.sudo_event
        event.type = None
        self.master.receive_event(event=event)
        self.build_ui(context=context)


    def setup_json_draw_elements(self, context):
        '''Setup json drawing data from invoke.'''

        factor = dpi_factor(min=.25)
        self.json_shader_file_text = ""
        self.json_shader_help_text = "Type in file name or Return for Date Time formatting."
        self.screen_width = context.area.width
        self.screen_height = context.area.height


    def safe_draw_file_name(self, context):
        method_handler(self.draw_file_name_shader,
            arguments = (context,),
            identifier = 'UI Framework',
            exit_method = self.remove_file_name_shader)


    def remove_file_name_shader(self):
        '''Remove shader handle.'''

        if self.json_draw_handle:
            self.json_draw_handle = bpy.types.SpaceView3D.draw_handler_remove(self.json_draw_handle, "WINDOW")
            self.json_draw_handle = None


    def draw_file_name_shader(self, context):
        '''Draw shader handle.'''

        factor = dpi_factor()

        help_text_size = 18
        file_text_size = 24

        sample_y = get_blf_text_dims("XyZ`Qq", file_text_size)[1]
        help_text_dims = get_blf_text_dims(self.json_shader_help_text, help_text_size)
        file_text_dims = get_blf_text_dims(self.json_shader_file_text, file_text_size)

        center_x = self.screen_width * .5
        center_y = self.screen_height * .5

        text_padding_y = 30 * factor
        text_padding_x = 20 * factor

        total_height = text_padding_y * 3 + sample_y + sample_y
        widest_text = help_text_dims[0] if help_text_dims[0] > file_text_dims[0] else file_text_dims[0]
        total_width = text_padding_x * 2 + widest_text

        # TL, BL, TR, BR
        verts = [
            (center_x - total_width * .5, center_y + total_height * .5),
            (center_x - total_width * .5, center_y - total_height * .5),
            (center_x + total_width * .5, center_y + total_height * .5),
            (center_x + total_width * .5, center_y - total_height * .5)]

        render_quad(
            quad=verts,
            color=(0,0,0,.5))

        draw_border_lines(
            vertices=verts,
            width=2,
            color=(0,0,0,.75))

        x_loc = center_x - help_text_dims[0] * .5
        y_loc = center_y - help_text_dims[1] * .5 + file_text_size * factor
        render_text(
            text=self.json_shader_help_text, 
            position=(x_loc, y_loc), 
            size=help_text_size, 
            color=(1,1,1,1))

        x_loc = center_x - file_text_dims[0] * .5
        y_loc = center_y - file_text_dims[1] * .5 - file_text_size * factor
        render_text(
            text=self.json_shader_file_text, 
            position=(x_loc, y_loc), 
            size=file_text_size, 
            color=(1,1,1,1))

    #--- JSON FILE UTILS ---#
    def save_rig_to_json(self, context):
        '''Save the rig to a json file.'''

        # Get path to light folder
        folder_path = self.get_json_folder_path()
        if folder_path == None:
            return

        # Validate json file name
        if self.json_file_name == "" or self.json_file_name == None:
            return

        # Get the rig data as a dict
        rig_data = self.get_light_rig_data_for_json()
        if rig_data == None:
            return

        # Save the file
        self.save_json_file(folder_path=folder_path, rid_data=rig_data)


    def get_json_folder_path(self):
        '''Return the folder path for the JSON files.'''

        prefs = get_preferences()
        folder = Path(prefs.property.lights_folder).resolve()
        
        if os.path.exists(folder):
            return folder
        
        try:
            folder.mkdir(parents=True, exist_ok=True)
            return folder
        except:
            print(f'Unable to create {folder}')
            return None


    def ensure_json_file_name(self, folder_path=""):
        '''Makes sure no other file with the same name exsist.'''

        if folder_path == "":
            return None
        
        file_path = os.path.join(folder_path, self.json_file_name + '.json')
        if os.path.exists(file_path):
            form = ' %B %d %Y - %H %M %S %f'
            self.json_file_name += datetime.now().strftime(form)


    def get_json_file_names(self):
        '''Get all the json file names.'''

        # Check for json files
        folder = self.get_json_folder_path()
        if folder == None:
            return

        all_files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        json_files = []

        for f in all_files:
            filename, file_extension = os.path.splitext(f)
            if file_extension == '.json':
                json_files.append(filename)

        if json_files == []:
            bpy.ops.hops.display_notification(info='Save a light first: Shift + S')

        return json_files


    def get_json_file_dirs(self):
        '''Set the list of file directories.'''

        # Check for json files
        folder = self.get_json_folder_path()
        if folder == None:
            return

        all_files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        json_files = []

        for f in all_files:
            filename, file_extension = os.path.splitext(f)
            if file_extension == '.json':
                json_files.append(os.path.join(folder, f))

        return json_files


    def get_light_rig_data_for_json(self):
        '''Capture the light rig data as a json ready dictionary.'''

        # Validate
        if self.empty == None:
            return None

        config = {}
        for obj in self.empty.children:
            if obj.type == 'LIGHT':
                config[obj.name] = {
                    'loc'    : (obj.location[0], obj.location[1], obj.location[2]),
                    'rot'    : (obj.rotation_euler[0], obj.rotation_euler[1], obj.rotation_euler[2]),
                    'scale'  : (obj.scale[0], obj.scale[1], obj.scale[2]),
                    'color'  : (obj.data.color[0], obj.data.color[1], obj.data.color[2]),
                    'energy' : obj.data.energy,
                    'type'   : obj.data.type,
                    'size'   : obj.data.size if hasattr(obj.data, 'size') else 0
                }

        return config


    def save_json_file(self, folder_path="", rid_data={}):
        '''Save the rig data to the file.'''

        # Make sure the file wont write over and exsisting file
        self.ensure_json_file_name(folder_path=folder_path)

        # Create file and dump jason into it
        file_path = os.path.join(folder_path, self.json_file_name + '.json')
        with open(file_path, 'w') as json_file:
            json.dump(rid_data, json_file, indent=4)

        # Update the directories list
        self.json_file_dirs = self.get_json_file_dirs()

        # Update files
        self.json_files = self.get_json_file_names()


    def load_specified_json_file(self, context, file_name=""):
        '''Load the specified file name.'''

        # Check if the files are loaded
        if self.json_file_dirs == [] or self.json_file_dirs == None:
            bpy.ops.hops.display_notification(info="Could not load file.")
            return

        # Get file dir
        load_dir = ""
        for f_name in self.json_file_dirs:
            if file_name in f_name:
                load_dir = f_name
                break
        if load_dir == "":
            bpy.ops.hops.display_notification(info="Could not load file.")
            return

        self.json_data = None
        self.json_current_file = load_dir

        # Open file for write
        self.json_data = None 
        with open(self.json_current_file, 'r') as json_file:
            self.json_data = json.load(json_file)

        # Load data
        if self.json_data != None:
            self.setup_rig_to_match_json_data(context, self.json_data)
        else:
            bpy.ops.hops.display_notification(info=F'ERROR: Bad Data @ {self.json_current_file}')

        self.json_current_file_name = file_name


