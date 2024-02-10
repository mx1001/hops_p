import bpy
from bpy.props import BoolProperty
from . import infobar
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


class HOPS_OT_AdjustArrayOperator(bpy.types.Operator):
    bl_idname = "hops.adjust_array"
    bl_label = "Adjust Array"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}
    bl_description = """Classic Array Modal
    
    Adds an array on the mesh. Supports multiple modifiers. Press H for help
    *newer arrays can be opted into via the opt-in panel*
    
    """

    x: BoolProperty(name="X Axis",
                    description="X Axis",
                    default=True)

    y: BoolProperty(name="Y Axis",
                    description="Y Axis",
                    default=False)

    z: BoolProperty(name="Z Axis",
                    description="Z Axis",
                    default=False)

    is_relative: BoolProperty(name="Is relative",
                              description="Is relatives",
                              default=True)

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)


    def invoke(self, context, event):

        self.objects = [o for o in context.selected_objects if o.type == 'MESH']
        self.object = context.active_object if context.active_object.type == 'MESH' else self.objects[0]
        self.modal_scale = get_preferences().ui.Hops_modal_scale

        obj = bpy.context.active_object
        if obj.dimensions[2] == 0 or obj.dimensions[1] == 0 or obj.dimensions[0] == 0:
            self.x = False
            self.y = False
            self.z = True

        if get_preferences().property.force_array_apply_scale_on_init:
            for obj in self.objects:
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        self.arrays = {}
        self.get_array_modifier("Array")
        self.using_array = "Array"
        self.new_dir = "X"

        for obj in self.arrays:
            mods = self.arrays[obj]["arrays"]
            for mod in mods:
                relative = self.arrays[obj]["start_array_relative_offset_displace"]
                constant = self.arrays[obj]["start_array_constant_offset_displace"]
                if not relative:
                    self.arrays[obj]["start_array_count"] = mod.count
                    relative.update({mod.name: [i for i in mod.relative_offset_displace]})
                    constant.update({mod.name: [i for i in mod.constant_offset_displace]})

        self.offset_x = 0
        self.offset_y = 0
        self.offset_z = 0

        if get_preferences().property.force_array_reset_on_init:
            for obj in self.arrays:
                mods = self.arrays[obj]["arrays"]
                mod.use_constant_offset = True
                for mod in mods:
                    mod.relative_offset_displace = [0, 0, 0]
                    mod.constant_offset_displace = [0, 0, 0]

        self.set_init_constant = False
        if len(self.objects) > 1:
            self.set_init_constant = True

        for object in self.objects:
            modifier.sort(object, sort_types=['WEIGHTED_NORMAL'])

        # Base Systems
        self.master = Master(context=context)
        self.master.only_use_fast_ui = True
        self.base_controls = Base_Modal_Controls(context, event)
        self.original_tool_shelf, self.original_n_panel = collapse_3D_view_panels()
        self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.safe_draw_shader, (context,), 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)
        infobar.initiate(self)
        return {"RUNNING_MODAL"}


    def get_array_modifier(self, name):
        '''Create or get array modifier on all selected mesh objects.'''

        for count, obj in enumerate(self.objects):
            if obj not in self.arrays:
                self.arrays.update({obj: {"arrays": [], "start_array_relative_offset_displace": {}, "start_array_constant_offset_displace": {}, "created_array_modifier": False, "start_array_count": 2}})
            mods = obj.modifiers
            if name in mods:
                if obj.modifiers[name] not in self.arrays[obj]["arrays"]:
                    self.arrays[obj]["arrays"].append(obj.modifiers[name])
            else:#if did not get one this iteration, create it
                array_modifier = obj.modifiers.new(name, "ARRAY")
                self.array = array_modifier
                self.arrays[obj]["arrays"].append(array_modifier)
                array_modifier.count = 2
                if not obj.dimensions[2] == 0 or obj.dimensions[1] == 0 or obj.dimensions[0] == 0:
                    array_modifier.relative_offset_displace = [1, 0, 0]
                relative = self.arrays[obj]["start_array_relative_offset_displace"]
                relative.update({self.array.name: [i for i in self.array.relative_offset_displace]})
                constant = self.arrays[obj]["start_array_constant_offset_displace"]
                constant.update({self.array.name: [i for i in self.array.constant_offset_displace]})
                self.arrays[obj]["created_array_modifier"] = True


    def modal(self, context, event):
        
        # Base Systems
        self.master.receive_event(event=event)
        self.base_controls.update(context, event)
        mouse_warp(context, event)

        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        active_object = bpy.context.active_object
        if get_preferences().property.modal_handedness == 'LEFT':
            self.offset_x -= self.base_controls.mouse
            self.offset_y -= self.base_controls.mouse
            self.offset_z -= self.base_controls.mouse
        else:
            self.offset_x += self.base_controls.mouse
            self.offset_y += self.base_controls.mouse
            self.offset_z += self.base_controls.mouse

        #Override For Planes
        if active_object.dimensions[2] == 0 or active_object.dimensions[1] == 0 or active_object.dimensions[0] == 0:
            for obj in self.arrays:
                mods = self.arrays[obj]["arrays"]
                for mod in mods:
                    self.array = mod

                    self.array.use_constant_offset = True
                    self.array.use_relative_offset = False
                    self.is_relative = False

        for obj in self.arrays:
            mods = self.arrays[obj]["arrays"]
            for mod in mods:
                self.array = mod

                relative = self.arrays[obj]["start_array_relative_offset_displace"]
                constant = self.arrays[obj]["start_array_constant_offset_displace"]

                if self.array.name == self.using_array:

                    if self.is_relative:
                        if mod.name in relative:
                            if self.x:
                                self.array.relative_offset_displace[0] = float("{:.2f}".format(relative[mod.name][0] + self.offset_x))
                            if self.y:
                                self.array.relative_offset_displace[1] = float("{:.2f}".format(relative[mod.name][1] + self.offset_y))
                            if self.z:
                                self.array.relative_offset_displace[2] = float("{:.2f}".format(relative[mod.name][2] + self.offset_z))
                    else:

                        if mod.name in constant:
                            if self.x:
                                self.array.constant_offset_displace[0] = float("{:.2f}".format(constant[mod.name][0] + self.offset_x))
                            if self.y:
                                self.array.constant_offset_displace[1] = float("{:.2f}".format(constant[mod.name][1] + self.offset_y))
                            if self.z:
                                self.array.constant_offset_displace[2] = float("{:.2f}".format(constant[mod.name][2] + self.offset_z))


                    if event.type == "X" and event.value == "PRESS" or self.new_dir == "X":
                        if event.shift:
                            self.x = not self.x
                        else:
                            if self.is_relative:
                                self.array.relative_offset_displace = [1, 0, 0]
                                self.offset_x = 0
                            else:
                                self.array.constant_offset_displace = [0, 0, 0]
                                self.offset_x = 0
                            self.x = True
                            self.y = False
                            self.z = False

                    if event.type == "Y" and event.value == "PRESS" or self.new_dir == "Y":
                        if event.shift:
                            self.y = not self.y
                        else:
                            if self.is_relative:
                                self.array.relative_offset_displace = [0, 1, 0]
                                self.offset_y = -1
                            else:
                                self.array.constant_offset_displace = [0, 0, 0]
                                self.offset_y = 0
                            self.x = False
                            self.y = True
                            self.z = False

                    if event.type == "Z" and event.value == "PRESS" or self.new_dir == "Z":
                        if event.shift:
                            self.z = not self.z
                        else:
                            if self.is_relative:
                                self.array.relative_offset_displace = [0, 0, 1]
                                self.offset_z = -1
                            else:
                                self.array.constant_offset_displace = [0, 0, 0]
                                self.offset_z = 0
                            self.x = False
                            self.y = False
                            self.z = True

                    if self.base_controls.scroll:
                        if event.shift:
                            if self.base_controls.scroll == 1:
                                bpy.ops.object.modifier_move_up(modifier=self.array.name)
                            else:
                                bpy.ops.object.modifier_move_down(modifier=self.array.name)
                        else:
                            self.array.count += self.base_controls.scroll
                            self.report({'INFO'}, F'Count : {self.array.count}')

                    if event.type == "C" and event.value == "PRESS" or self.set_init_constant:
                        self.array.use_constant_offset = True
                        self.array.use_relative_offset = False
                        self.is_relative = False
                        self.array.constant_offset_displace = [0, 0, 0]
                        self.report({'INFO'}, F'Constant Offset')

                    if event.type == "Q" and event.value == "PRESS":
                        bpy.ops.object.modifier_move_up(modifier=self.array.name)

                    if event.type == "W" and event.value == "PRESS":
                        bpy.ops.object.modifier_move_down(modifier=self.array.name)

                    if event.type == "R" and event.value == "PRESS":
                        self.array.use_constant_offset = False
                        self.array.use_relative_offset = True
                        self.is_relative = True
                        self.array.relative_offset_displace = [1, 0, 0]
                        self.report({'INFO'}, F'Relative Offset')

        self.set_init_constant = False
        self.new_dir = ""

        if event.type == "ONE" and event.value == "PRESS":
            self.get_array_modifier("Array")
            self.offset_x = 0
            self.offset_y = 0
            self.offset_z = 0
            self.set_init_constant = True
            self.using_array = "Array"
            self.new_dir = "X"

        if event.type == "TWO" and event.value == "PRESS":
            self.get_array_modifier("Array1")
            self.offset_x = 0
            self.offset_y = 0
            self.offset_z = 0
            self.set_init_constant = True
            self.using_array = "Array1"
            self.new_dir = "Y"

        if event.type == "THREE" and event.value == "PRESS":
            self.get_array_modifier("Array2")
            self.offset_x = 0
            self.offset_y = 0
            self.offset_z = 0
            self.set_init_constant = True
            self.using_array = "Array2"
            self.new_dir = "Z"

        if event.type == "S" and event.value == "PRESS":
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        if self.base_controls.cancel:
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.restore()
            self.master.run_fade()
            infobar.remove(self)
            return {'CANCELLED'}

        if self.base_controls.confirm:
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            infobar.remove(self)
            return {'FINISHED'}

        self.draw_master(context=context)

        context.area.tag_redraw()

        return {"RUNNING_MODAL"}


    def restore(self):
        for obj in self.arrays:
            mods = self.arrays[obj]["arrays"]
            for mod in mods:
                self.array = mod
                self.array.count = self.arrays[obj]["start_array_count"]
                self.array.relative_offset_displace = self.arrays[obj]["start_array_relative_offset_displace"][mod.name]
                self.array.constant_offset_displace = self.arrays[obj]["start_array_constant_offset_displace"][mod.name]
                if self.arrays[obj]["created_array_modifier"]:
                    if self.array.name in obj.modifiers:
                        obj.modifiers.remove(self.array)


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
            self.array = self.objects[0].modifiers[self.using_array]
            relative = self.array.relative_offset_displace
            constant = self.array.constant_offset_displace

            if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1: #Fast Floating
                win_list.append(str(self.array.count))
                if self.is_relative:
                    win_list.append(" {:.2f} {:.2f} {:.2f} ".format(relative[0], relative[1], relative[2]))
                else:
                    win_list.append(" {:.2f} {:.2f} {:.2f} ".format(constant[0], constant[1], constant[2]))
            else:
                win_list.append("Name : " + str(self.array.name))
                win_list.append("Count : " + str(self.array.count))
                if self.is_relative:
                    win_list.append("  X: {:.3f}  Y: {:.3f}  Z: {:.3f} ".format(relative[0], relative[1], relative[2]))
                else:
                    win_list.append("  X: {:.3f}  Y: {:.3f}  Z: {:.3f} ".format(constant[0], constant[1], constant[2]))

            # Help
            help_list.append(["X",         "set x axis"])
            help_list.append(["Y",         "set y axis"])
            help_list.append(["Z",         "set z axis"])
            help_list.append(["shift + X", "on/off x axis"])
            help_list.append(["shift + Y", "on/off y axis"])
            help_list.append(["shift + Z", "on/off z axis"])
            help_list.append(["Shift + Scroll",    "Move mod up/down"])
            help_list.append(["Scroll",    "change array count"])
            help_list.append(["R",         "use relative offset"])
            help_list.append(["C",         "use constant offset"])
            help_list.append(["1",         "jump to 1st modifier"])
            help_list.append(["2",         "create/jump to 2nd modifier"])
            help_list.append(["3",         "create/jump to 3rd modifier"])
            help_list.append(["S",         "apply scale"])
            help_list.append(["Q",         "Move mod DOWN"])
            help_list.append(["W",         "Move mod UP"])
            help_list.append(["M",         "Toggle mods list."])
            help_list.append(["H",         "Toggle help."])
            help_list.append(["~",         "Toggle viewport displays."])
            help_list.append(["O",         "Toggle viewport rendering"])

            # Mods
            if self.array != None:
                active_mod = self.array.name

            mods_list = get_mods_list(mods=bpy.context.active_object.modifiers)

            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="Array", mods_list=mods_list, active_mod_name=active_mod)

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