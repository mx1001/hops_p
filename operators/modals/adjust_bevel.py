import bpy
import math
import pathlib
from pathlib import Path
from math import radians, degrees
from bpy.props import BoolProperty
from mathutils import Vector
from . import infobar
from ... utils.objects import apply_scale
from ... utility import modifier
from ... utility.base_modal_controls import Base_Modal_Controls
from ... preferences import get_preferences
from ... ui_framework.master import Master
from ... ui_framework.utils.mods_list import get_mods_list, custom_profile
from ... addon.utility.profile import save_bevel_profile, load_bevel_profile, get_bevel_profile, set_bevel_profile

# Cursor Warp imports
from ... utils.toggle_view3d_panels import collapse_3D_view_panels
from ... utils.modal_frame_drawing import draw_modal_frame
from ... utils.cursor_warp import mouse_warp
from ... addon.utility import method_handler


class HOPS_OT_AdjustBevelOperator(bpy.types.Operator):
    bl_idname = "hops.adjust_bevel"
    bl_label = "Adjust Bevel"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}
    bl_description = """Add / Adjust Bevel 

LMB               - Adjust Bevel Modifier
CTRL              - Add new Bevel (30º)
CTRL + Shift  - Add new Bevel (60º)
Shift               - Bypass Scale

Press H for help"""

    mods: list = []

    bevel_objects = {}

    ignore_ctrl: BoolProperty(
        name='Ignore Ctrl',
        default=False,
        description='Ignore Ctrl keypress')

    use_workflow: BoolProperty(
        name='Use Worflow Pref',
        default=True,
        description='Use workflow pref')

    flag: BoolProperty(
        name='Use Bevel Special Behavior',
        default=False,
        description='Ignore Ctrl keypress')

    text = "nothing"

    def __init__(self):

        # Modal UI
        self.master = None

    @classmethod
    def poll(cls, context):
        return any(o.type in {'MESH', 'CURVE'} for o in context.selected_objects)

    @staticmethod
    def bevel_modifiers(object):

        return [modifier for modifier in object.modifiers if modifier.type == "BEVEL"]

    def invoke(self, context, event):

        self.objects = [o for o in context.selected_objects if o.type in {'MESH', 'CURVE'}]
        self.object = context.active_object if context.active_object else self.objects[0]
        self.scaleapply = True
        self.segments_mode = False
        self.profile_mode = False
        self.angle_mode = False
        self.snap_break = 0.05
        self.snap_buffer = 0

        # Must prepare profile scroll before calling self.store_values()
        self.support_profile_scroll = False
        self.profile_folder = Path(get_preferences().property.profile_folder).resolve()

        if self.profile_folder.is_dir():
            self.profile_files = [x for x in self.profile_folder.glob('*.json') if x.is_file()]

            if self.profile_files:
                self.profile_index = 0
                self.scrolling_profiles = False
                self.support_profile_scroll = True

        # self.ignore_ctrl = False
        self.adaptivemode = get_preferences().property.adaptivemode
        #  self.modal_percent_scale = get_preferences().property.Hops_modal_percent_scale
        self.mods = []
        self.bevel_objects = {}

        for object in self.objects:
            self.get_bevel_modifier(context, object, event)

        self.active_bevel_modifier = self.object.modifiers[self.bevel_objects[self.object.name]["modifier"]]
        self.store_values()

        self.percent_mode = False

        # apply the scale, keep child transformations and bevel width as well as fix DECALmachine backup matrices
        if context.mode == 'OBJECT': # doesnt work in object mode
            if event.shift and not event.ctrl:
                self.scaleapply = False
            if self.scaleapply:
                apply_scale([bpy.data.objects[name] for name in self.bevel_objects if self.bevel_objects[name].get("scaled")])
        else:
            self.scaleapply = False

        for object in self.objects:

            if "added_modifier" in self.bevel_objects[object.name]:
                wn_mods =  [wn for wn in object.modifiers if wn.type == 'WEIGHTED_NORMAL' ]
                
                for mod in wn_mods:
                    stored = modifier.stored(mod)
                    object.modifiers.remove(mod)
                    modifier.new(object, mod = stored)

        # Base Systems
        self.master = Master(context=context)
        self.master.only_use_fast_ui = True
        self.base_controls = Base_Modal_Controls(context, event)
        self.original_tool_shelf, self.original_n_panel = collapse_3D_view_panels()
        self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.safe_draw_shader, (context,), 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)
        infobar.initiate(self)

        return {"RUNNING_MODAL"}

    def modal(self, context, event):

        # Base Systems
        self.master.receive_event(event=event)
        self.base_controls.update(context, event)
        mouse_warp(context, event)

        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        # DO ONCE
        for object_name in self.bevel_objects:
            # print(self.bevel_objects)
            object = bpy.data.objects[object_name]
            # print(object.modifiers[:])
            modifier = object.modifiers[self.bevel_objects[object_name]["modifier"]]

            if event.type == "MOUSEMOVE":
                if self.angle_mode:
                    angle_offset = self.base_controls.mouse
                    if event.ctrl:
                        self.snap_buffer += angle_offset
                        if abs(self.snap_buffer) > self.snap_break:
                            increment = radians(5)
                            modifier.angle_limit = snap(modifier.angle_limit + math.copysign(increment, self.snap_buffer), increment)
                            self.snap_buffer = 0
                    else:
                        modifier.angle_limit += angle_offset

                elif self.segments_mode:
                    self.snap_buffer += self.base_controls.mouse
                    if abs(self.snap_buffer) > self.snap_break:
                        modifier.segments += math.copysign(1, self.snap_buffer)
                        self.snap_buffer = 0

                elif self.profile_mode:
                    self.snap_buffer += self.base_controls.mouse
                    if abs(self.snap_buffer) > self.snap_break:
                        modifier.profile = round(modifier.profile + math.copysign(0.1, self.snap_buffer), 1)
                        self.snap_buffer = 0

                else:
                    bevel_offset = self.base_controls.mouse
                    multiplier = 10 if modifier.offset_type == 'PERCENT' else 1
                    if event.ctrl and event.shift:
                        self.snap_buffer += bevel_offset
                        if abs(self.snap_buffer) > self.snap_break:
                            modifier.width = round(modifier.width + math.copysign(0.1 * multiplier, self.snap_buffer), 1)
                            self.snap_buffer = 0
                    else:
                        modifier.width += bevel_offset * multiplier
                if self.adaptivemode:
                    self.adaptivesegments = int(modifier.width * get_preferences().property.adaptiveoffset) + object.hops.adaptivesegments
                    modifier.segments = self.adaptivesegments

            if self.base_controls.scroll:
                if self.support_profile_scroll and self.scrolling_profiles:
                    keys = list(self.bevel_objects.keys())

                    # This is lame but it works
                    if keys.index(object_name) == 0:
                        i = self.profile_index
                        l = len(self.profile_files)
                        s = self.base_controls.scroll
                        self.profile_index = (i + s + l) % l

                    current = self.profile_files[self.profile_index]
                    load_bevel_profile(modifier, str(current), False)

                elif self.adaptivemode:
                    if event.ctrl:
                        get_preferences().property.adaptiveoffset += 0.5 * self.base_controls.scroll
                    elif event.shift:
                        if self.base_controls.scroll == 1:
                            modifier = self.change_bevel(object, modifier)
                        elif self.base_controls.scroll == -1:
                            modifier = self.change_bevel(object, modifier, neg=True)
                    else:
                        object.hops.adaptivesegments += self.base_controls.scroll
                elif event.shift:
                    if self.base_controls.scroll == 1:
                        bpy.ops.object.modifier_move_up(modifier=modifier.name)
                    elif self.base_controls.scroll == -1:
                        bpy.ops.object.modifier_move_down(modifier=modifier.name)
                elif event.ctrl:
                        if self.base_controls.scroll == 1:
                            modifier = self.change_bevel(object, modifier)
                        elif self.base_controls.scroll == -1:
                            modifier = self.change_bevel(object, modifier, neg=True)

                elif event.alt:
                    modifier.angle_limit += radians(self.base_controls.scroll)
                else:
                    if self.angle_mode:
                        modifier.angle_limit += radians(self.base_controls.scroll)

                    else:
                        modifier.segments += self.base_controls.scroll

            if event.type == "ONE" and event.value == "PRESS":
                if round(object.data.auto_smooth_angle, 4) == round(radians(60), 4):
                    object.data.use_auto_smooth = True
                    if context.mode == 'OBJECT':
                        bpy.ops.object.shade_smooth()
                    object.data.auto_smooth_angle = radians(30)
                    modifier.harden_normals = False
                    if bpy.app.version < (2, 90, 0):
                        modifier.use_only_vertices = False
                    else:
                        modifier.affect = 'EDGES'
                    if modifier.segments == 2:
                        modifier.segments = 4
                else:
                    object.data.use_auto_smooth = True
                    if context.mode == 'OBJECT':
                        bpy.ops.object.shade_smooth()
                        object.data.auto_smooth_angle = radians(60)
                    modifier.harden_normals = False
                    if bpy.app.version < (2, 90, 0):
                        modifier.use_only_vertices = False
                    else:
                        modifier.affect = 'EDGES'
                    if modifier.segments == 2:
                        modifier.segments = 4
                if context.mode == 'EDIT_MESH':
                    if modifier.profile == 0.5:
                        modifier.profile = 0.05
                    else:
                        modifier.profile = 0.5
                    self.report({'INFO'}, F'Profile set to: {round(modifier.profile, 4)}')
                else:
                    modifier.profile = 0.5
                    if get_preferences().ui.Hops_extra_info:
                        bpy.ops.hops.display_notification(info=F'Autosmooth : {round(degrees(object.data.auto_smooth_angle), 4)}', name="")
                    self.report({'INFO'}, F'Autosmooth : {round(degrees(object.data.auto_smooth_angle), 4)} / Harden Normals : {modifier.harden_normals}')

            if event.type == "TWO" and event.value == "PRESS":
                # modifier.limit_method = "NONE"
                if bpy.app.version < (2, 90, 0):
                    modifier.use_only_vertices = True
                else:
                    modifier.affect = 'VERTICES'
                if context.mode == 'EDIT_MESH':
                    if modifier.profile == 0.5:
                        modifier.profile = 0.05
                    else:
                        modifier.profile = 0.5
                else:
                    modifier.profile = 0.5
                if get_preferences().ui.Hops_extra_info:
                    bpy.ops.hops.display_notification(info=F'Vert Bevel', name="")
                self.report({'INFO'}, F'Vert Bevel')

            if event.type == "THREE" and event.value == "PRESS":
                if bpy.app.version < (2, 90, 0):
                    modifier.use_only_vertices = False
                else:
                    modifier.affect = 'EDGES'
                modifier.harden_normals = False
                modifier.profile = 1.0
                modifier.segments = 2
                object.show_wire = False if object.show_wire else True
                object.show_all_edges = True if object.show_wire else False
                if get_preferences().ui.Hops_extra_info:
                    bpy.ops.hops.display_notification(info= F'Conversion Bevel', name="")
                self.report({'INFO'}, F'Conversion Bevel')

            if event.type == "A":
                if event.value == "PRESS":

                    # SHIFT
                    if event.shift:
                        self.adaptivemode = not self.adaptivemode
                        get_preferences().property.adaptivemode = not get_preferences().property.adaptivemode
                        self.report({'INFO'}, F'Adaptive Mode : {self.adaptivemode}')

                    # CTRL
                    elif event.ctrl:
                        modifier.limit_method = 'ANGLE' if not 'VGROUP' else 'ANGLE'
                        angle_types = [60, 30, degrees(object.data.auto_smooth_angle)]

                        if int(degrees(modifier.angle_limit)) not in angle_types:
                            modifier.angle_limit = radians(angle_types[0])
                        else:
                            index = angle_types.index(int(degrees(modifier.angle_limit)))
                            modifier.angle_limit = radians(angle_types[index + 1 if index + 1 < len(angle_types) else 0])
                        self.report({'INFO'}, F'Bevel Mod Angle : {int(degrees(modifier.angle_limit))}')

                    # ALT
                    elif event.alt:
                        if context.mode == 'OBJECT':
                            context.area.header_text_set(text=None)
                            self.remove_shader()
                            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
                            self.master.run_fade()
                            modifier.show_viewport = False if modifier.show_viewport else True
                            bpy.ops.hops.adjust_auto_smooth("INVOKE_DEFAULT", flag=True)
                            self.report({'INFO'}, F'Autosmooth Adjustment')
                            self.finished = True
                            return {'FINISHED'}
                        else:
                            self.report({'INFO'}, F'Unavailable')
                            pass

                    # ELSE
                    else:
                        if modifier.limit_method == 'ANGLE':
                            self.angle_mode = not self.angle_mode
                            if self.angle_mode:
                                self.profile_mode = False
                            break

            if event.type == "Q":
                if event.value == "PRESS":

                    # SHIFT
                    if event.shift:
                        bpy.ops.object.modifier_move_up(modifier=modifier.name)
                    # ELSE
                    else:
                        modifier = self.change_bevel(object, modifier, neg=True)

            if event.type == "E":
                if event.value == "PRESS":

                    # SHIFT
                    if event.shift:
                        bpy.ops.object.modifier_move_down(modifier=modifier.name)
                    # ELSE
                    else:
                        modifier = self.change_bevel(object, modifier)

            if event.type == "C" and event.value == "PRESS" and event.shift:
                modifier.loop_slide = not modifier.loop_slide
                self.report({'INFO'}, F'Loop Slide : {modifier.loop_slide}')

            if event.type == "C" and event.value == "PRESS":
                modifier.use_clamp_overlap = not modifier.use_clamp_overlap
                self.report({'INFO'}, F'Clamp Overlap : {modifier.use_clamp_overlap}')

            if event.type == "L" and event.value == "PRESS":
                limit_methods = ["NONE", "ANGLE", "WEIGHT", "VGROUP"]
                modifier.limit_method = limit_methods[(limit_methods.index(modifier.limit_method) + 1) % len(limit_methods)]
                if get_preferences().ui.Hops_extra_info:
                    bpy.ops.hops.display_notification(info=F'Limit Method : {modifier.limit_method}', name="")
                self.report({'INFO'}, F'Limit Method : {modifier.limit_method}')

            if event.type == "M" and event.value == "PRESS" and event.shift == True:
                modifier.harden_normals = not modifier.harden_normals
                self.report({'INFO'}, F'Harden Normals : {modifier.harden_normals}')

            if event.type == "N" and event.value == "PRESS":
                if context.mode == 'EDIT_MESH':
                    bpy.ops.mesh.flip_normals()
                else:
                    modifier.harden_normals = not modifier.harden_normals
                    self.report({'INFO'}, F'Harden Normals : {modifier.harden_normals}')

            # Must go before event.type == "P" 
            if event.type == 'P' and event.value == 'PRESS' and event.shift:
                self.segments_mode = False
                if self.support_profile_scroll:
                    if get_preferences().ui.Hops_extra_info:
                        bpy.ops.hops.display_notification(info=F'Profile Scroll: {self.support_profile_scroll}', name="")
                    self.profile_mode = False
                    self.segments_mode = False
                    self.scrolling_profiles = not self.scrolling_profiles
                    action = 'Started' if self.scrolling_profiles else 'Stopped'
                    self.report({'INFO'}, f'{action} scrolling profiles')
                    break
                else:
                   if get_preferences().ui.Hops_extra_info:
                        bpy.ops.hops.display_notification(info=F'No Profiles Found', name="") 
                    
            if event.type == 'P' and event.value == 'PRESS' and event.ctrl:
                if bpy.app.version < (2, 90, 0):
                    modifier.use_custom_profile = not modifier.use_custom_profile
                    self.report({'INFO'}, F'Custom Profile : {modifier.use_custom_profile}')
                else:
                    if modifier.profile_type == 'CUSTOM':
                        modifier.profile_type = 'SUPERELLIPSE'
                    else:
                        modifier.profile_type = 'CUSTOM'
                    self.report({'INFO'}, F'Custom Profile : {modifier.profile_type}')


            if event.type == "P" and event.value == "PRESS":
                self.segments_mode = False
                self.scrolling_profiles = False
                self.profile_mode = not self.profile_mode
                break

            if event.type == "S":
                if event.value == "PRESS":

                    # SHIFT
                    if event.shift:
                        if context.mode == 'OBJECT':
                            object.data.use_auto_smooth = True
                            bpy.ops.object.shade_smooth()
                    # ELSE
                    else:
                        self.profile_mode = False
                        self.scrolling_profiles = False
                        self.segments_mode = not self.segments_mode
                        break
                        # self.report({'INFO'}, 'Modal Segments Toggled')

            if event.type == "W" and event.value == "PRESS" and event.alt:
                offset_types = ["OFFSET", "WIDTH", "DEPTH", "PERCENT"]
                modifier.offset_type = offset_types[(offset_types.index(modifier.offset_type) + 1) % len(offset_types)]
                self.report({'INFO'}, F'Offset Type : {modifier.offset_type}')

            if event.type == "W" and event.value == "PRESS" and event.shift and not event.ctrl:
                modifier.show_render = not modifier.show_render
                self.report({'INFO'}, F'Modifiers Renderability : {modifier.show_render}')

            if event.type == "V" and event.value == "PRESS":
                modifier.show_viewport = False if modifier.show_viewport else True
                self.report({'INFO'}, F'Toggle Bevel : {modifier.show_viewport}')

            if event.type == "X" and event.value == "PRESS":

                bevel_widths = [mod.width for mod in context.object.modifiers if mod.type == 'BEVEL']
                if not len(bevel_widths):
                    return {"RUNNING_MODAL"}
                lw = bevel_widths[-1]
                if len(bevel_widths) > 1 and not event.alt:
                    lw = bevel_widths[-2]
                lw = lw * 0.5 if not event.shift else lw * 2
                modifier.width = lw
                if get_preferences().ui.Hops_extra_info:
                    bpy.ops.hops.display_notification(info=F'Bevel Set to: {lw:.3f}', name="")
                self.report({'INFO'}, F'Width Set to half: {lw:.3f}')
                context.area.header_text_set(text=None)
                self.finished = True
                self.remove_shader()
                collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
                self.master.run_fade()
                infobar.remove(self)
                return {'FINISHED'}

            if event.type == "Z" and event.value == "PRESS":
                bpy.context.space_data.overlay.show_overlays = True
                object.show_wire = False if object.show_wire else True
                object.show_all_edges = True if object.show_wire else False
                # self.report({'INFO'}, F'Show Wire : {object.show_all_edges}')

            if self.base_controls.cancel:
                self.restore()
                context.area.header_text_set(text=None)
                self.remove_shader()
                collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
                self.master.run_fade()
                infobar.remove(self)
                return {'CANCELLED'}

            if self.base_controls.confirm or event.type in ( "RET", "NUMPAD_ENTER"):

                if event.type in ("RET", "NUMPAD_ENTER") and event.shift:
                    if context.mode == 'EDIT_MESH':
                        bpy.ops.object.editmode_toggle()
                    if context.mode == 'OBJECT':
                        bpy.ops.object.modifier_apply(modifier=modifier.name) # apply_as='DATA',
                        if get_preferences().ui.Hops_extra_info:
                            bpy.ops.hops.display_notification(info=f'{modifier.name} : Applied', name="")
                        # self.report({'INFO'}, 'Bevel Modifier: Applied')
                context.area.header_text_set(text=None)
                bpy.context.space_data.overlay.show_overlays = True
                object.show_wire = False
                # self.report({'INFO'}, 'Done')
                self.remove_shader()
                collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
                self.master.run_fade()
                infobar.remove(self)
                return {'FINISHED'}

        self.active_bevel_modifier = self.object.modifiers[self.bevel_objects[self.object.name]["modifier"]]
        context.area.header_text_set("Hardops Adjust Bevel,                Current modifier: - {}".format(self.active_bevel_modifier.name))

        self.draw_ui(context=context)

        context.area.tag_redraw()

        return {'RUNNING_MODAL'}

    def draw_ui(self, context):

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
            # win_list.append("Name : "   + str(self.active_bevel_modifier.name))
            if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1:
                win_list.append(self.active_bevel_modifier.segments)
                win_list.append("%.3f" % self.active_bevel_modifier.width)
                if self.active_bevel_modifier.limit_method == 'ANGLE':
                    win_list.append("%.0f" % (degrees(self.active_bevel_modifier.angle_limit)) + "°")
                if self.support_profile_scroll and self.scrolling_profiles:
                    win_list.append(self.active_bevel_modifier.segments)
                    win_list.append(self.profile_files[self.profile_index].name[:-5])
                # win_list.append("%.2f" % self.active_bevel_modifier.profile)
                # win_list.append("Profile : "  + "%.4f" % self.active_bevel_modifier.profile)
                # win_list.append("Offset : "   + str(self.active_bevel_modifier.offset_type))
            else:
                win_list.append(self.active_bevel_modifier.name)
                if self.text != "nothing" and get_preferences().property.workflow_mode == 'ANGLE' and self.active_bevel_modifier.limit_method == 'ANGLE':
                    # win_list.append("%.0f" % (degrees(self.active_bevel_modifier.angle_limit)) + "° " + self.text)
                    win_list.append(self.text)
                win_list.append("Segments : " + str(self.active_bevel_modifier.segments))
                win_list.append("Width : "    + "%.3f" % self.active_bevel_modifier.width)
                if self.support_profile_scroll and self.scrolling_profiles:
                    win_list.append("Custom Profile : " + str(self.profile_files[self.profile_index].name[:-5]))
                else:
                    if custom_profile(self.active_bevel_modifier):
                        win_list.append("Custom Profile")
                    else:
                        win_list.append("Profile : "  + "%.2f" % self.active_bevel_modifier.profile)
                win_list.append("Limit : "   + str(self.active_bevel_modifier.limit_method))
                if self.active_bevel_modifier.limit_method == 'ANGLE':
                    win_list.append("Angle : "+ "%.0f" % (degrees(self.active_bevel_modifier.angle_limit)) + "°" + " (alt)")
                if self.support_profile_scroll and self.scrolling_profiles:
                    win_list.append(str(self.profile_files[self.profile_index].name[:-5]))
                # win_list.append("Harden Normals : "   + str(self.active_bevel_modifier.harden_normals))
                # win_list.append("Offset : "   + str(self.active_bevel_modifier.offset_type))

            # Help
            #help_list.append([" ", "[H] Help [M] Toggle mods list"])
            help_list.append(["Shift + Enter",  "Apply the current modifier"])
            #help_list.append(["Shift + A",      f"Adaptive Segment mode: {self.adaptivemode}"])
            #help_list.append(["Alt + A",        "Jump to autosmooth"])
            help_list.append(["Ctrl + Shift",   "Mouse move snap"])
            #help_list.append(["Shift + Scroll", "Move mod up/down"])
            #help_list.append(["Shift + E / Q",  "Move mod up/down"])
            help_list.append(["Ctrl + Scroll",  "Move mod up/down"])
            #help_list.append(["Shift + ~",      "Toggle viewport displays"])
            help_list.append(["Alt + W",        "Adjust the offset algorithm [shift] sort toggle"])
            help_list.append(["Ctrl + A",       "Change angle to bevel at to 30 / 60"])
            #help_list.append(["Shift + W",      "Toggle render visibility / Sort Lock"])
            #help_list.append(["Ctrl + A",       "Change angle to bevel at to 30 / 60"])
            #help_list.append(["V",              "Toggle visibility in the viewport"])
            help_list.append(["C",              "Toggle Clamp Overlap"])
            help_list.append(["3",              "Profile 1.0 / Segment 1 - Sub-d Conversion"])
            help_list.append(["2",              "Profile .5 / Toggle vertex bevel"])
            help_list.append(["1",              "Profile .5 / Autosmooth 30 / 60 / Harden Normals Off"])
            help_list.append(["S",              "Modal Segment Toggle"])
            help_list.append(["L",              f"Change limit method - {self.active_bevel_modifier.limit_method}"])
            help_list.append(["X",              f"Set bevel to 50% of current (half-bevel)"])
            
            if context.mode == 'OBJECT':
                if self.angle_mode:
                    help_list.append(["A",              "Return to segments"])
                else:
                    help_list.append(["A",              f"Adjust Bevel Angle [shift] Adaptive Mode "])

            if self.profile_mode: # FIXME : This does not take into account that Shift + P should also say "Return to segments" when it's toggled on
                help_list.append(["P",              "Return to segments"])
            else:
                help_list.append(["P",              "Adjust the Profile [shift] scroll [ctrl] toggle"])

            # if self.support_profile_scroll:
            #     if self.scrolling_profiles:
            #         help_list.append(["Shift + P",      "Return to segments"])
            #     else:
            #         help_list.append(["Shift + P",      "Scroll through saved custom profiles"])

            if context.mode == 'EDIT_MESH':
                help_list.append(["N",          "Flip Normal"])
            else:
                help_list.append(["N",          "Harden normal toggle"])

            if self.angle_mode:
                help_list.append(["Scroll",         "Adjust angle of modifier"])
            else:
                help_list.append(["Scroll",         "Add bevel segments to modifier"])

            help_list.append(["Q / E",          "Change mod being adjusted [shift] move [ctrl] change"])

            if self.profile_mode:
                help_list.append(["Move",           "Adjust the profile of bevel modifier"])
            elif self.angle_mode:
                help_list.append(["Move",           "Adjust the angle of bevel modifier"])
            elif self.segments_mode:
                help_list.append(["Move",           "Adjust segments of bevel modifier"])
            else:
                help_list.append(["Move",           "Adjust width of bevel modifier"])
            
            help_list.append(["Z",  "Toggle the wireframe display"])
            help_list.append(["V",  "Toggle visibility in the viewport"])
            help_list.append(["M", "Toggle modifier list"])
            help_list.append(["H", "Toggle help"])
            help_list.append(["~", "Toggle UI Display / [shift] Toggle Overlay"])
            help_list.append(["O", "Toggle Viewport rendering"])

            # Mods
            if self.active_bevel_modifier != None:
                active_mod = self.active_bevel_modifier.name
            else:
                active_mod = ""

            mods_list = get_mods_list(mods=bpy.context.active_object.modifiers)

            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="AdjustBevel", mods_list=mods_list, active_mod_name=active_mod)

        # Finished
        self.master.finished()

    def restore(self):

        scale_vectors = []
        for object_name in self.bevel_objects:
            object = bpy.data.objects[object_name]
            object.show_wire = self.bevel_objects[object_name]["show_wire"]
            if "scaled" in self.bevel_objects[object_name]:
                scale_vector = self.bevel_objects[object_name]["scaled"]
                scale_vectors.append(scale_vector)
            if "added_modifier" in self.bevel_objects[object_name]:
                object.modifiers.remove(object.modifiers[self.bevel_objects[object_name]["modifier"]])
            else:
                modifier = object.modifiers[self.bevel_objects[object_name]["modifier"]]
                modifier.show_viewport = self.bevel_objects[object_name]["show_viewport"]
                modifier.width = self.bevel_objects[object_name]["width"]
                modifier.profile = self.bevel_objects[object_name]["profile"]
                modifier.segments = self.bevel_objects[object_name]["segments"]
                modifier.limit_method = self.bevel_objects[object_name]["limit_method"]
                modifier.angle_limit = self.bevel_objects[object_name]["angle_limit"]
                if bpy.app.version < (2, 90, 0):
                    modifier.use_only_vertices = self.bevel_objects[object_name]["use_only_vertices"]
                else:
                    modifier.affect = self.bevel_objects[object_name]["affect"]
                modifier.use_clamp_overlap = self.bevel_objects[object_name]["use_clamp_overlap"]
                modifier.offset_type = self.bevel_objects[object_name]["offset_type"]

                if self.support_profile_scroll:
                    set_bevel_profile(modifier, self.bevel_objects[object_name]["profile_backup"], False)

        # reversed scale application, by passing in the scale_vectors
        if self.scaleapply:
            apply_scale([bpy.data.objects[name] for name in self.bevel_objects if self.bevel_objects[name].get("scaled")], scale_vectors=scale_vectors)

    def get_bevel_modifier(self, context, object, event):
        angle = 15
        if event.ctrl and not event.shift and not self.ignore_ctrl:
            angle = 30
            val = add_bevel_modifier(context, object, radians(angle))
            self.bevel_objects.setdefault(object.name, {})["modifier"] = val[0]
            self.bevel_objects[object.name]["added_modifier"] = val[1]
            self.text = "30° Bevel Added"
        if event.ctrl and event.shift and not self.ignore_ctrl:
            angle = 60
            val = add_bevel_modifier(context, object, radians(angle))
            self.bevel_objects.setdefault(object.name, {})["modifier"] = val[0]
            self.bevel_objects[object.name]["added_modifier"] = val[1]
            self.text = "60° Bevel Added"
        else:
            try:
                self.bevel_objects.setdefault(object.name, {})["modifier"] = self.bevel_modifiers(object)[-1].name
            except:
                val = add_bevel_modifier(context, object, radians(30))
                self.bevel_objects.setdefault(object.name, {})["modifier"] = val[0]
                self.bevel_objects[object.name]["added_modifier"] = val[1]

    def store_values(self, obj=None, mod=None):

        if not obj:
            for object_name in self.bevel_objects:
                object = bpy.data.objects[object_name]
                self.bevel_objects[object_name]["show_wire"] = object.show_wire
                if object.scale != Vector((1.0, 1.0, 1.0)):
                    self.bevel_objects[object_name]["scaled"] = object.scale[:]
                modifier = object.modifiers[self.bevel_objects[object_name]["modifier"]]
                self.bevel_objects[object_name]["show_viewport"] = modifier.show_viewport
                self.bevel_objects[object_name]["width"] = modifier.width
                self.bevel_objects[object_name]["profile"] = modifier.profile
                self.bevel_objects[object_name]["segments"] = modifier.segments
                self.bevel_objects[object_name]["limit_method"] = modifier.limit_method
                self.bevel_objects[object_name]["angle_limit"] = modifier.angle_limit
                if bpy.app.version < (2, 90, 0):
                    self.bevel_objects[object_name]["use_only_vertices"] = modifier.use_only_vertices
                else:
                    self.bevel_objects[object_name]["affect"] = modifier.affect
                self.bevel_objects[object_name]["use_clamp_overlap"] = modifier.use_clamp_overlap
                self.bevel_objects[object_name]["offset_type"] = modifier.offset_type
                self.bevel_objects[object_name]["loop_slide"] = modifier.loop_slide
                self.bevel_objects[object_name]["start_width"] = modifier.width
                self.bevel_objects[object_name]["harden_normals"] = modifier.harden_normals

                if self.support_profile_scroll:
                    self.bevel_objects[object_name]["profile_backup"] = get_bevel_profile(modifier)

            return

        modifier = obj.modifiers[mod.name]
        self.bevel_objects[obj.name]["modifier"] = modifier.name
        self.bevel_objects[obj.name]["show_viewport"] = modifier.show_viewport
        self.bevel_objects[obj.name]["width"] = modifier.width
        self.bevel_objects[obj.name]["profile"] = modifier.profile
        self.bevel_objects[obj.name]["segments"] = modifier.segments
        self.bevel_objects[obj.name]["limit_method"] = modifier.limit_method
        self.bevel_objects[obj.name]["angle_limit"] = modifier.angle_limit
        if bpy.app.version < (2, 90, 0):
            self.bevel_objects[obj.name]["use_only_vertices"] = modifier.use_only_vertices
        else:
            self.bevel_objects[obj.name]["affect"] = modifier.affect
        self.bevel_objects[obj.name]["use_clamp_overlap"] = modifier.use_clamp_overlap
        self.bevel_objects[obj.name]["offset_type"] = modifier.offset_type
        self.bevel_objects[obj.name]["loop_slide"] = modifier.loop_slide
        self.bevel_objects[obj.name]["start_width"] = modifier.width
        self.bevel_objects[obj.name]["harden_normals"] = modifier.harden_normals

        if self.support_profile_scroll:
            self.bevel_objects[obj.name]["profile_backup"] = get_bevel_profile(modifier)

    def change_bevel(self, object, modifier, neg=False):

        bevels = [mod for mod in object.modifiers if mod.type == 'BEVEL']
        if neg:
            index = [mod.name for mod in bevels].index(modifier.name)
            self.store_values(obj=object, mod=bevels[index - 1])

            return object.modifiers[self.bevel_objects[object.name]["modifier"]]

        else:
            index = [mod.name for mod in bevels].index(modifier.name)
            if index + 1 < len(bevels):
                self.store_values(obj=object, mod=bevels[index + 1])
            else:
                self.store_values(obj=object, mod=bevels[0])

            return object.modifiers[self.bevel_objects[object.name]["modifier"]]

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


def add_bevel_modifier(context, object, angle):
    bevel_modifier = object.modifiers.new(name="Bevel", type="BEVEL")
    bevels = [mod for mod in object.modifiers if mod.type == 'BEVEL']
    if get_preferences().ui.Hops_extra_info:
        if get_preferences().property.workflow_mode == 'ANGLE':
            bpy.ops.hops.display_notification(info=f'Bevel Added {"%.1f"%(degrees(angle))}° - Total : {len(bevels)}', name="")
        else:
            bpy.ops.hops.display_notification(info=f'Bevel Added - Total : {len(bevels)}', name="")
    bevel_modifier.limit_method = get_preferences().property.workflow_mode

    bevel_modifier.angle_limit = angle
    bevel_modifier.miter_outer = 'MITER_ARC'
    bevel_modifier.width = 0.01

    if bpy.app.version > (2, 89, 0):
        bevel_modifier.affect = 'EDGES'

    bevel_modifier.profile = get_preferences().property.bevel_profile
    bevel_modifier.loop_slide = get_preferences().property.bevel_loop_slide
    bevel_modifier.use_clamp_overlap = False
    bevel_modifier.segments = 3
    if object.dimensions[2] == 0 or object.dimensions[1] == 0 or object.dimensions[0] == 0:
        bevel_modifier.segments = 6
        if bpy.app.version < (2, 90, 0):
            bevel_modifier.use_only_vertices = True
        else:
            bevel_modifier.affect = 'VERTICES'
        bevel_modifier.use_clamp_overlap = True
        if get_preferences().ui.Hops_extra_info:
            bpy.ops.hops.display_notification(info=f'2d Bevel Added', name="")
    elif object.hops.status == "BOOLSHAPE":
        bevel_modifier.harden_normals = False
    elif get_preferences().property.use_harden_normals:
        bevel_modifier.harden_normals = True
    object.show_all_edges = True

    if object.type == 'MESH':
        if not object.data.use_auto_smooth:
            object.data.use_auto_smooth = True
            object.data.auto_smooth_angle = radians(60)
        if context.mode == 'EDIT_MESH':
            vg = object.vertex_groups.new(name='HardOps')
            bpy.ops.object.vertex_group_assign()
            if get_preferences().property.adjustbevel_use_1_segment:
                if context.tool_settings.mesh_select_mode[2] and object.hops.status == "BOOLSHAPE":
                    bevel_modifier.segments = 1
                    bevel_modifier.harden_normals = False
                    bpy.ops.mesh.flip_normals()
            bevel_modifier.limit_method = 'VGROUP'
            bevel_modifier.vertex_group = vg.name
            bpy.ops.mesh.faces_shade_smooth()
            if get_preferences().ui.Hops_extra_info:
                bpy.ops.hops.display_notification(info=f'Vgroup Bevel Added', name="")
        else:
            bpy.ops.object.shade_smooth()

    # self.bevel_objects.setdefault(object.name, {})["modifier"] = bevel_modifier.name
    # self.bevel_objects[object.name]["added_modifier"] = True

    return (bevel_modifier.name, True)


def snap(value, increment):
        result = round(value / increment) * increment
        return result
