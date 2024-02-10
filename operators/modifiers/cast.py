import bpy, math
from mathutils import Vector
from ... preferences import get_preferences
from ... ui_framework.master import Master
from ... ui_framework.utils.mods_list import get_mods_list
from ... utility.base_modal_controls import Base_Modal_Controls

# Cursor Warp imports
from ... utils.toggle_view3d_panels import collapse_3D_view_panels
from ... utils.modal_frame_drawing import draw_modal_frame
from ... utils.cursor_warp import mouse_warp
from ... addon.utility import method_handler


class HOPS_OT_MOD_Cast(bpy.types.Operator):
    bl_idname = "hops.mod_cast"
    bl_label = "Adjust Cast Modifier"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}
    bl_description = """
LMB - Adjust Cast Modifier
LMB + CTRL - Add New cast Modifier

Press H for help."""

    cast_objects = {}

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    @staticmethod
    def cast_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "CAST"]

    def invoke(self, context, event):

        self.factor_mode = True
        self.snap_buffer = 0
        self.size_mode = False
        self.radius_mode = False
        self.modal_scale = get_preferences().ui.Hops_modal_scale
        self.cast_objects = {}
        self.snap_break = 0.1

        for object in [o for o in context.selected_objects if o.type == 'MESH']:
            self.get_deform_modifier(object, event)

        self.active_cast_modifier = context.object.modifiers[self.cast_objects[context.object.name]["modifier"]]
        self.store_values()

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

        context.area.header_text_set("Hardops Cast:     X : Use x - {}    Y : Usey - {}     Z : Use z - {}     Q : radius as size - {}".format(self.active_cast_modifier.use_x, self.active_cast_modifier.use_y, self.active_cast_modifier.use_z, self.active_cast_modifier.use_radius_as_size))

        for object_name in self.cast_objects:
            object = bpy.data.objects[object_name]
            modifier = object.modifiers[self.cast_objects[object_name]["modifier"]]

            if self.radius_mode:
                self.snap_buffer += self.base_controls.mouse
                if abs(self.snap_buffer) > self.snap_break:
                    radius_offset = math.copysign(1, self.snap_buffer)
                    modifier.radius = int(modifier.radius + radius_offset)
                    self.snap_buffer = 0

            if self.size_mode:
                self.snap_buffer += self.base_controls.mouse
                if abs(self.snap_buffer) > self.snap_break:
                    size_offset = math.copysign(1, self.snap_buffer)
                    modifier.size = int(modifier.size + size_offset)
                    self.snap_buffer = 0

            if self.factor_mode:
                self.snap_buffer += self.base_controls.mouse
                if abs(self.snap_buffer) > self.snap_break:
                    factor_offset = math.copysign(1, self.snap_buffer)
                    modifier.factor = int(modifier.factor + factor_offset)
                    self.snap_buffer = 0

            if event.type == "R" and event.value == "PRESS":
                self.stop_radius = modifier.radius
                if self.size_mode:
                    self.size_mode = False
                if self.factor_mode:
                    self.factor_mode = False
                if self.radius_mode:
                    self.factor_mode = True
                self.radius_mode = not self.radius_mode

            if event.type == "S" and event.value == "PRESS":
                self.stop_size = modifier.size
                if self.factor_mode:
                    self.factor_mode = False
                if self.radius_mode:
                    self.radius_mode = False
                if self.size_mode:
                    self.factor_mode = True
                self.size_mode = not self.size_mode

            if self.base_controls.scroll:
                if event.shift:
                    if self.base_controls.scroll == 1:
                        bpy.ops.object.modifier_move_up(modifier=modifier.name)
                    else:
                        bpy.ops.object.modifier_move_down(modifier=modifier.name)
                else:
                    cast_type = ["SPHERE", "CUBOID", "CYLINDER"]
                    modifier.cast_type = cast_type[(cast_type.index(modifier.cast_type) + self.base_controls.scroll) % len(cast_type)]


            if event.type == "X" and event.value == "PRESS":
                modifier.use_x = not modifier.use_x

            if event.type == "Y" and event.value == "PRESS":
                modifier.use_y = not modifier.use_y

            if event.type == "Z" and event.value == "PRESS":
                modifier.use_z = not modifier.use_z

            if event.type == "Q" and event.value == "PRESS" and event.shift == True:
                modifier.use_radius_as_size = not modifier.use_radius_as_size

            if event.type == "Q" and event.value == "PRESS":
                bpy.ops.object.modifier_move_up(modifier=modifier.name)

            if event.type == "W" and event.value == "PRESS":
                bpy.ops.object.modifier_move_down(modifier=modifier.name)

            if self.base_controls.cancel:
                self.restore()
                context.area.header_text_set(text=None)
                self.remove_shader()
                collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
                self.master.run_fade()
                return {'CANCELLED'}

            if self.base_controls.confirm:
                context.area.header_text_set(text=None)
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
            try: self.cast_objects.setdefault(object.name, {})["modifier"] = self.cast_modifiers(object)[-1].name
            except: self.add_deform_modifier(object)


    def add_deform_modifier(self, object):
        cast_modifier = object.modifiers.new(name="cast", type="CAST")
        cast_modifier.factor = 1.0
        cast_modifier.radius = 0
        cast_modifier.size = 0
        cast_modifier.cast_type = "SPHERE"
        cast_modifier.use_y = True
        cast_modifier.use_x = True
        cast_modifier.use_z = True
        cast_modifier.use_radius_as_size = True

        self.cast_objects.setdefault(object.name, {})["modifier"] = cast_modifier.name
        self.cast_objects[object.name]["added_modifier"] = True


    def store_values(self):
        for object_name in self.cast_objects:
            object = bpy.data.objects[object_name]
            modifier = object.modifiers[self.cast_objects[object_name]["modifier"]]
            self.cast_objects[object_name]["show_viewport"] = modifier.show_viewport
            self.cast_objects[object_name]["factor"] = modifier.factor
            self.cast_objects[object_name]["radius"] = modifier.radius
            self.cast_objects[object_name]["size"] = modifier.size
            self.cast_objects[object_name]["cast_type"] = modifier.cast_type
            self.cast_objects[object_name]["use_y"] = modifier.use_y
            self.cast_objects[object_name]["use_z"] = modifier.use_z
            self.cast_objects[object_name]["use_x"] = modifier.use_x
            self.cast_objects[object_name]["use_radius_as_size"] = modifier.use_radius_as_size


    def restore(self):
        for object_name in self.cast_objects:
            object = bpy.data.objects[object_name]
            if "added_modifier" in self.cast_objects[object_name]:
                object.modifiers.remove(object.modifiers[self.cast_objects[object_name]["modifier"]])
            else:
                modifier = object.modifiers[self.cast_objects[object_name]["modifier"]]
                modifier.show_viewport = self.cast_objects[object_name]["show_viewport"]
                modifier.factor = self.cast_objects[object_name]["factor"]
                modifier.radius = self.cast_objects[object_name]["radius"]
                modifier.size = self.cast_objects[object_name]["size"]
                modifier.cast_type = self.cast_objects[object_name]["cast_type"]
                modifier.use_y = self.cast_objects[object_name]["use_y"]
                modifier.use_z = self.cast_objects[object_name]["use_z"]
                modifier.use_x = self.cast_objects[object_name]["use_x"]
                modifier.use_radius_as_size = self.cast_objects[object_name]["use_radius_as_size"]


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
                win_list.append(self.active_cast_modifier.factor)
                win_list.append(self.active_cast_modifier.radius)
                win_list.append(self.active_cast_modifier.size)
                win_list.append(self.active_cast_modifier.cast_type)
            else:
                win_list.append("Cast")
                win_list.append("Factor: {}".format(self.active_cast_modifier.factor))
                win_list.append("Radius: {:.1f}".format(self.active_cast_modifier.radius))
                win_list.append("Size: {}".format(self.active_cast_modifier.size))
                win_list.append("Cast: {}".format(self.active_cast_modifier.cast_type))

            # Help
            help_list.append(["move",  "Factor"])
            help_list.append(["R",     "Radius"])
            help_list.append(["S",     "Size"])
            help_list.append(["Scroll", "Cast type"])
            help_list.append(["Shift + Scroll", "Move mod up/down"])
            help_list.append(["X",     "Use x"])
            help_list.append(["Y",     "Use y"])
            help_list.append(["Z",     "Use z"])
            help_list.append(["Shift + Q",     "Use radius as size"])
            help_list.append(["Q",          "Move mod DOWN"])
            help_list.append(["W",          "Move mod UP"])
            help_list.append(["M",     "Toggle mods list."])
            help_list.append(["H",     "Toggle help."])
            help_list.append(["~",     "Toggle viewport displays."])
            help_list.append(["O",         "Toggle viewport rendering"])
            
            # Mods
            if self.active_cast_modifier != None:
                active_mod = self.active_cast_modifier.name

            mods_list = get_mods_list(mods=bpy.context.active_object.modifiers)

            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="AdjustBevel", mods_list=mods_list, active_mod_name=active_mod)

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