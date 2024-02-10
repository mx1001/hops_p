import bpy, math
from mathutils import Vector
from ... preferences import get_preferences
from ... utility import modifier
from ... utility.base_modal_controls import Base_Modal_Controls
from ... ui_framework.master import Master
from ... ui_framework.utils.mods_list import get_mods_list

# Cursor Warp imports
from ... utils.toggle_view3d_panels import collapse_3D_view_panels
from ... utils.modal_frame_drawing import draw_modal_frame
from ... utils.cursor_warp import mouse_warp
from ... addon.utility import method_handler


class HOPS_OT_MOD_Screw(bpy.types.Operator):
    bl_idname = "hops.mod_screw"
    bl_label = "Adjust Screw Modifier"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}
    bl_description = """
LMB - Adjust Screw Modifier
LMB + CTRL - Add New Screw Modifier

Press H for help.
"""

    screw_objects = {}

    axis: bpy.props.EnumProperty(
        name="Axis",
        description="What axis screw / spin",
        items=[
            ('X', "X", "Screw X axis"),
            ('Y', "Y", "Screw Y axis"),
            ('Z', "Z", "Screw Z axis")
            ],
        default='X')

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    @staticmethod
    def screw_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "SCREW"]


    def invoke(self, context, event):

        self.objects = [o for o in context.selected_objects if o.type == 'MESH']
        self.segments_mode = False
        self.angle_mode = False
        self.screw_mode = True
        self.iterations_mode = False
        self.screw_objects = {}
        self.snap_buffer = 0
        self.snap_break = 0.05

        for object in self.objects:
            self.get_deform_modifier(object, event)

        self.active_screw_modifier = context.object.modifiers[self.screw_objects[context.object.name]["modifier"]]
        self.store_values()

        for object in self.objects:
            modifier.sort(object, sort_types=['WEIGHTED_NORMAL'])

        bpy.context.space_data.overlay.show_face_orientation = True
        #original_alpha_settings = []
        #self.original_alpha_settings = bpy.types.ThemeView3D.face_front
        bpy.types.ThemeView3D.face_front = [.6,1,1,0]

        # Base Systems
        self.master = Master(context=context)
        self.master.only_use_fast_ui = True
        self.base_controls = Base_Modal_Controls(context, event)
        self.original_tool_shelf, self.original_n_panel = collapse_3D_view_panels()
        self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.safe_draw_shader, (context,), 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}


    def modal(self, context, event):

        # Base Systems
        self.master.receive_event(event=event)
        self.base_controls.update(context, event)
        mouse_warp(context, event)

        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        context.area.header_text_set("Hardops Screw:     N : Smooth - {}     M : Merge - {}     X/Y/Z : AxiS - {}     F : Flip - {}      C : Calculate - {}".format(self.active_screw_modifier.use_smooth_shade, self.active_screw_modifier.use_merge_vertices, self.active_screw_modifier.axis, self.active_screw_modifier.use_normal_flip, self.active_screw_modifier.use_normal_calculate))

        for object_name in self.screw_objects:
            object = bpy.data.objects[object_name]
            modifier = object.modifiers[self.screw_objects[object_name]["modifier"]]

            if self.angle_mode:

                if event.shift:
                    modifier.angle += self.base_controls.mouse
                elif event.ctrl:
                    self.snap_buffer += self.base_controls.mouse
                    increment = math.radians(5)
                    if abs(self.snap_buffer)>self.snap_break:
                        modifier.angle += math.copysign(increment , self.snap_buffer)
                        modifier.angle = snap(modifier.angle, increment)
                        self.snap_buffer=0
                else:
                    self.snap_buffer += self.base_controls.mouse
                    increment = math.radians(45)
                    if abs(self.snap_buffer)>self.snap_break:
                        modifier.angle += math.copysign(increment , self.snap_buffer)
                        modifier.angle = snap(modifier.angle, increment)
                        self.snap_buffer=0

            if self.iterations_mode:
                self.snap_buffer += self.base_controls.mouse
                if abs(self.snap_buffer)>self.snap_break:
                    modifier.iterations += math.copysign(1, self.snap_buffer)
                    self.snap_buffer =0

            if self.screw_mode:
                self.snap_buffer += self.base_controls.mouse
                if abs(self.snap_buffer)>self.snap_break:
                    if event.shift:
                        increment = 0.01
                    elif event.ctrl:
                        increment = 1
                    else:
                        increment = 0.1
                    modifier.screw_offset += math.copysign(increment, self.snap_buffer)
                    modifier.screw_offset = snap(modifier.screw_offset, increment)
                    self.snap_buffer = 0

            if self.segments_mode:
                self.snap_buffer += self.base_controls.mouse
                if abs(self.snap_buffer)>self.snap_break:
                    increment = 1
                    modifier.steps += math.copysign(increment, self.snap_buffer)
                    modifier.steps = snap(modifier.steps, increment)
                    self.snap_buffer =0

            if event.type == "ONE" and event.value == "PRESS":
                modifier.angle = math.radians(360)
                modifier.steps = 12
                modifier.render_steps = 12
                modifier.screw_offset = 0
                modifier.use_merge_vertices = True
                modifier.use_smooth_shade = True
                modifier.use_normal_calculate = True
                if get_preferences().ui.Hops_extra_info:
                    bpy.ops.hops.display_notification(info=f'Screw - 12 Steps', name="")

            elif event.type == "TWO" and event.value == "PRESS":
                modifier.angle = math.radians(360)
                modifier.steps = 36
                modifier.render_steps = 36
                modifier.screw_offset = 0
                modifier.use_merge_vertices = True
                modifier.use_smooth_shade = True
                modifier.use_normal_calculate = False
                if get_preferences().ui.Hops_extra_info:
                    bpy.ops.hops.display_notification(info=f'Screw - 36 Steps', name="")

            elif event.type == "THREE" and event.value == "PRESS":
                modifier.angle = math.radians(0)
                modifier.steps = 2
                modifier.render_steps = 2
                modifier.screw_offset = 2.3
                modifier.use_merge_vertices = True
                modifier.use_smooth_shade = True
                modifier.use_normal_calculate = False
                modifier.axis = 'Z'
                if get_preferences().ui.Hops_extra_info:
                    bpy.ops.hops.display_notification(info=f'Extrude Mode', name="")

            elif event.type == "A" and event.value == "PRESS":

                if self.iterations_mode:
                    self.iterations_mode = False
                if self.screw_mode:
                    self.screw_mode = False
                if self.segments_mode:
                    self.segments_mode = False
                if self.angle_mode:
                    self.screw_mode = True
                self.angle_mode = not self.angle_mode

            elif event.type == "E" and event.value == "PRESS":

                if self.screw_mode:
                    self.screw_mode = False
                if self.segments_mode:
                    self.segments_mode = False
                if self.angle_mode:
                    self.angle_mode = False
                if self.iterations_mode:
                    self.screw_mode = True
                self.iterations_mode = not self.iterations_mode

            elif event.type == "S" and event.value == "PRESS":
                if self.screw_mode:
                    self.screw_mode = False
                if self.iterations_mode:
                    self.iterations_mode = False
                if self.angle_mode:
                    self.angle_mode = False
                if self.segments_mode:
                    self.screw_mode = True
                self.segments_mode = not self.segments_mode

            elif self.base_controls.scroll:
                if event.shift:
                    if self.base_controls.scroll ==1:
                        bpy.ops.object.modifier_move_up(modifier=modifier.name)
                    elif self.base_controls.scroll == -1:
                        bpy.ops.object.modifier_move_down(modifier=modifier.name)
                else:
                    modifier.iterations += self.base_controls.scroll

            elif event.type == "F" and event.value == "PRESS":
                modifier.use_normal_flip = not modifier.use_normal_flip

            elif event.type == 'X' and event.value == 'PRESS':
                self.axis = "YZX"["XYZ".find(self.axis)]
                modifier.axis = self.axis
                self.report({'INFO'}, f"Screw Axis: {self.axis}")

            elif event.type == "Y" and event.value == "PRESS":
                modifier.axis = "Y"

            elif event.type == "Z" and event.value == "PRESS" and not event.shift:
                modifier.axis = "Z"

            elif event.type == "M" and event.value == "PRESS" and event.shift == True:
                modifier.use_merge_vertices = not modifier.use_merge_vertices

            elif event.type == "C" and event.value == "PRESS":
                modifier.use_normal_calculate = not modifier.use_normal_calculate

            elif event.type == "N" and event.value == "PRESS":
                modifier.use_smooth_shade = not modifier.use_smooth_shade

            elif event.type == "H" and event.value == "PRESS":
                bpy.context.space_data.show_gizmo_navigate = True
                get_preferences().property.hops_modal_help = not get_preferences().property.hops_modal_help

            elif event.type == "Q" and event.value == "PRESS":
                bpy.ops.object.modifier_move_up(modifier=modifier.name)

            elif event.type == "W" and event.value == "PRESS":
                bpy.ops.object.modifier_move_down(modifier=modifier.name)

            elif event.type == "Z" and event.value == "PRESS" and event.shift:
                bpy.context.space_data.overlay.show_face_orientation = not bpy.context.space_data.overlay.show_face_orientation

            elif self.base_controls.cancel:
                self.restore()
                context.area.header_text_set(text=None)
                bpy.context.space_data.overlay.show_face_orientation = False
                self.remove_shader()
                collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
                self.master.run_fade()
                return {'CANCELLED'}

            elif self.base_controls.confirm:
                context.area.header_text_set(text=None)
                bpy.context.space_data.overlay.show_face_orientation = False
                self.remove_shader()
                collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
                self.master.run_fade()
                return {'FINISHED'}

        self.draw_master(context=context)

        context.area.tag_redraw()

        return {"RUNNING_MODAL"}


    def get_deform_modifier(self, object, event):
        if event.ctrl:
            self.add_deform_modifier(object)
        else:
            try: self.screw_objects.setdefault(object.name, {})["modifier"] = self.screw_modifiers(object)[-1].name
            except: self.add_deform_modifier(object)


    def add_deform_modifier(self, object):
        screw_modifier = object.modifiers.new(name="screw", type="SCREW")
        screw_modifier.angle = math.radians(360)
        screw_modifier.axis = 'Y'
        screw_modifier.steps = 36
        screw_modifier.render_steps = 36
        screw_modifier.screw_offset = 0
        screw_modifier.iterations = 1
        screw_modifier.use_smooth_shade = True
        screw_modifier.use_merge_vertices = True

        self.screw_objects.setdefault(object.name, {})["modifier"] = screw_modifier.name
        self.screw_objects[object.name]["added_modifier"] = True


    def store_values(self):
        for object_name in self.screw_objects:
            object = bpy.data.objects[object_name]
            modifier = object.modifiers[self.screw_objects[object_name]["modifier"]]
            self.screw_objects[object_name]["show_viewport"] = modifier.show_viewport
            self.screw_objects[object_name]["axis"] = modifier.axis
            self.screw_objects[object_name]["steps"] = modifier.steps
            self.screw_objects[object_name]["render_steps"] = modifier.render_steps
            self.screw_objects[object_name]["angle"] = modifier.angle
            self.screw_objects[object_name]["screw_offset"] = modifier.screw_offset
            self.screw_objects[object_name]["iterations"] = modifier.iterations
            self.screw_objects[object_name]["use_normal_flip"] = modifier.use_normal_flip
            self.screw_objects[object_name]["use_normal_calculate"] = modifier.use_normal_calculate
            self.screw_objects[object_name]["use_merge_vertices"] = modifier.use_merge_vertices
            self.screw_objects[object_name]["use_smooth_shade"] = modifier.use_smooth_shade


    def restore(self):
        for object_name in self.screw_objects:
            object = bpy.data.objects[object_name]
            if "added_modifier" in self.screw_objects[object_name]:
                object.modifiers.remove(object.modifiers[self.screw_objects[object_name]["modifier"]])
            else:
                modifier = object.modifiers[self.screw_objects[object_name]["modifier"]]
                modifier.show_viewport = self.screw_objects[object_name]["show_viewport"]
                modifier.axis = self.screw_objects[object_name]["axis"]
                modifier.steps = self.screw_objects[object_name]["steps"]
                modifier.render_steps = self.screw_objects[object_name]["render_steps"]
                modifier.angle = self.screw_objects[object_name]["angle"]
                modifier.screw_offset = self.screw_objects[object_name]["screw_offset"]
                modifier.iterations = self.screw_objects[object_name]["iterations"]
                modifier.use_normal_flip = self.screw_objects[object_name]["use_normal_flip"]
                modifier.use_normal_calculate = self.screw_objects[object_name]["use_normal_calculate"]
                modifier.use_merge_vertices = self.screw_objects[object_name]["use_merge_vertices"]
                modifier.use_smooth_shade = self.screw_objects[object_name]["use_smooth_shade"]


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
            if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1: #Fast Floating
                win_list.append(self.active_screw_modifier.steps)
                win_list.append("{:.0f}".format(math.degrees(self.active_screw_modifier.angle))+ "°")
                win_list.append("{}".format(round(self.active_screw_modifier.screw_offset, 4)))
                win_list.append("{}".format(self.active_screw_modifier.iterations))
            else:
                win_list.append("Screw")
                win_list.append("Steps: {}".format(self.active_screw_modifier.steps))
                win_list.append("Angle: {:.1f}".format(math.degrees(self.active_screw_modifier.angle))+ "°")
                win_list.append("Screw: {}".format(round(self.active_screw_modifier.screw_offset, 4)))
                win_list.append("It: {}".format(self.active_screw_modifier.iterations))
                win_list.append("[F] Flip")

            # Help
            help_list.append(["Move",      "Steps"])
            help_list.append(["A",         "Angle"])
            help_list.append(["S",         "Steps"])
            help_list.append(["E",         "Iterations"])
            help_list.append(["C",         "Use normal calculate"])
            help_list.append(["WHEEL",     "Change axis"])
            help_list.append(["M + Shift", "Merge vertices"])
            help_list.append(["N",         "Smooth shading"])
            help_list.append(["Q",         "Move mod DOWN"])
            help_list.append(["W",         "Move mod UP"])
            help_list.append(["Shift + Scroll", "Move mod up/down"])
            help_list.append(["N",         "Smooth shading"])
            help_list.append(["F",         "Use normal flip"])
            help_list.append(["Shift + Z", "Toggle Visual Orientation"])
            help_list.append(["X",         "Change Axis"])
            help_list.append(["Y",         "Set Axis to Y"])
            help_list.append(["Z",         "Set Axis to Z"])
            help_list.append(["3",         "Preset 3: Extrude"])
            help_list.append(["2",         "Preset 2: 36 Steps"])
            help_list.append(["1",         "Preset 1: 12 Steps"])
            help_list.append(["H",         "Toggle help."])
            help_list.append(["M",         "Toggle mods list."])
            help_list.append(["~",         "Toggle viewport displays."])
            help_list.append(["O",         "Toggle viewport rendering"])
            help_list.append([" ",         "Red means normals are flipped."])

            # Mods
            if self.active_screw_modifier != None:
                active_mod = self.active_screw_modifier.name
            else:
                active_mod = ""

            mods_list = get_mods_list(mods=bpy.context.active_object.modifiers)

            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="Twist", mods_list=mods_list, active_mod_name=active_mod)

        # Finished
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


def snap (value, increment):
        result = round (value/increment) * increment
        return result
