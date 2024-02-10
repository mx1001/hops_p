import bpy, math
from mathutils import Vector
from ... preferences import get_preferences
from ... utility import modifier
from ... utility.base_modal_controls import Base_Modal_Controls
from ... ui_framework.utils.mods_list import get_mods_list
from ... ui_framework.master import Master

# Cursor Warp imports
from ... utils.toggle_view3d_panels import collapse_3D_view_panels
from ... utils.modal_frame_drawing import draw_modal_frame
from ... utils.cursor_warp import mouse_warp
from ... addon.utility import method_handler


class HOPS_OT_MOD_Displace(bpy.types.Operator):
    bl_idname = "hops.mod_displace"
    bl_label = "Adjust Displace Modifier"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}
    bl_description = """
LMB - Adjust Displace Modifier
LMB + CTRL - Add new Displace Modifier

Press H for help."""

    displace_objects = {}

    axis: bpy.props.EnumProperty(
        name="Axis",
        description="What axis to array around",
        items=[
            ('X', "X", "Displace X axis"),
            ('Y', "Y", "Displace Y axis"),
            ('Z', "Z", "Displace Z axis")
            ],
        default='X')


    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    @staticmethod
    def displace_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "DISPLACE"]


    def invoke(self, context, event):

        self.objects = [o for o in context.selected_objects if o.type == 'MESH']
        self.modal_scale = get_preferences().ui.Hops_modal_scale
        self.displace_objects = {}

        for object in self.objects:
            self.get_deform_modifier(object, event)

        self.active_displace_modifier = context.object.modifiers[self.displace_objects[context.object.name]["modifier"]]
        self.store_values()

        for object in self.objects:
            modifier.sort(object, sort_types=['WEIGHTED_NORMAL'])

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

        context.area.header_text_set("Hardops Displace:     Space: {}".format(self.active_displace_modifier.space))

        for object_name in self.displace_objects:
            object = bpy.data.objects[object_name]
            modifier = object.modifiers[self.displace_objects[object_name]["modifier"]]

            if get_preferences().property.modal_handedness == 'LEFT':
                if event.ctrl:
                    modifier.mid_level -= self.base_controls.mouse / 10
                else:
                    modifier.strength -= self.base_controls.mouse
            else:
                if event.ctrl:
                    modifier.mid_level += self.base_controls.mouse / 10
                else:
                    modifier.strength += self.base_controls.mouse

            if self.base_controls.scroll:
                if event.shift:
                    if self.base_controls.scroll == 1:
                        bpy.ops.object.modifier_move_up(modifier=modifier.name)
                    else:
                        bpy.ops.object.modifier_move_down(modifier=modifier.name)
                else:
                    direction_types = ["X", "Y", "Z", "NORMAL", "CUSTOM_NORMAL", "RGB_TO_XYZ"]
                    modifier.direction = direction_types[(direction_types.index(modifier.direction) + self.base_controls.scroll) % len(direction_types)]
                    if get_preferences().ui.Hops_extra_info:
                        bpy.ops.hops.display_notification(info=f"{modifier.direction}", name="")

            if event.type == "Q" and event.value == "PRESS" and event.shift:
                space_types = ["GLOBAL", "LOCAL"]
                modifier.space = space_types[(space_types.index(modifier.space) + 1) % len(space_types)]

            # if event.type == "X" and event.value == "PRESS":
            #     modifier.direction = "X"
            elif event.type == 'X' and event.value == 'PRESS':
                #self.direction = "YZX"["XYZ".find(self.direction)]
                #self.displace_mod.direction = self.direction
                self.axis = "YZX"["XYZ".find(self.axis)]
                modifier.direction = self.axis
                self.report({'INFO'}, f"Displace Axis: {self.axis}")
                if get_preferences().ui.Hops_extra_info:
                    bpy.ops.hops.display_notification(info=f"Displace Axis: {self.axis}", name="")

            elif event.type == "Y" and event.value == "PRESS":
                modifier.direction = "Y"

            elif event.type == "Z" and event.value == "PRESS":
                modifier.direction = "Z"

            elif event.type == "N" and event.value == "PRESS":
                modifier.direction = "NORMAL"

            elif event.type == "Q" and event.value == "PRESS":
                bpy.ops.object.modifier_move_up(modifier=modifier.name)

            elif event.type == "W" and event.value == "PRESS":
                bpy.ops.object.modifier_move_down(modifier=modifier.name)
            
            elif event.type in {'ZERO', 'NUMPAD_0'} and event.value == "PRESS":
                 modifier.strength = 0
                 if get_preferences().ui.Hops_extra_info:
                     bpy.ops.hops.display_notification(info=F'Strength : 0', name="")

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
            try: self.displace_objects.setdefault(object.name, {})["modifier"] = self.displace_modifiers(object)[-1].name
            except: self.add_deform_modifier(object)


    def add_deform_modifier(self, object):
        displace_modifier = object.modifiers.new(name="Displace", type="DISPLACE")
        displace_modifier.direction = "X"
        displace_modifier.space = "LOCAL"
        displace_modifier.mid_level = 0
        displace_modifier.strength = 0

        self.displace_objects.setdefault(object.name, {})["modifier"] = displace_modifier.name
        self.displace_objects[object.name]["added_modifier"] = True


    def store_values(self):
        for object_name in self.displace_objects:
            object = bpy.data.objects[object_name]
            modifier = object.modifiers[self.displace_objects[object_name]["modifier"]]
            self.displace_objects[object_name]["show_viewport"] = modifier.show_viewport
            self.displace_objects[object_name]["strength"] = modifier.strength
            self.displace_objects[object_name]["mid_level"] = modifier.mid_level
            self.displace_objects[object_name]["direction"] = modifier.direction
            self.displace_objects[object_name]["space"] = modifier.space


    def restore(self):
        for object_name in self.displace_objects:
            object = bpy.data.objects[object_name]
            if "added_modifier" in self.displace_objects[object_name]:
                object.modifiers.remove(object.modifiers[self.displace_objects[object_name]["modifier"]])
            else:
                modifier = object.modifiers[self.displace_objects[object_name]["modifier"]]
                modifier.show_viewport = self.displace_objects[object_name]["show_viewport"]
                modifier.strength = self.displace_objects[object_name]["strength"]
                modifier.mid_level = self.displace_objects[object_name]["mid_level"]
                modifier.direction = self.displace_objects[object_name]["direction"]
                modifier.space = self.displace_objects[object_name]["space"]


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
                win_list.append("{}".format(self.active_displace_modifier.direction))
                win_list.append("{:.3f}".format(self.active_displace_modifier.strength))
                win_list.append("{:.3f}".format(self.active_displace_modifier.mid_level))
            else:
                win_list.append("Displace")
                win_list.append("Str: {:.3f}".format(self.active_displace_modifier.strength))
                win_list.append("Mid: {:.3f}".format(self.active_displace_modifier.mid_level))
                win_list.append("Direction: {}".format(self.active_displace_modifier.direction))

            # Help
            help_list.append(["move",           "Set strength"])
            help_list.append(["ctrl",           "Set Offset"])
            help_list.append(["WHEEL",          "Direction"])
            help_list.append(["Shift + Scroll", "Move mod up/down"])
            help_list.append(["Shift + Q",      "Space"])
            help_list.append(["0",              "Strength to 0."])
            help_list.append(["Q",              "Move mod DOWN"])
            help_list.append(["W",              "Move mod UP"])
            help_list.append(["M",              "Toggle mods list."])
            help_list.append(["H",              "Toggle help."])
            help_list.append(["~",              "Toggle viewport displays."])
            help_list.append(["O",              "Toggle viewport rendering"])

            # Mods
            if self.active_displace_modifier != None:
                active_mod = self.active_displace_modifier.name

            mods_list = get_mods_list(mods=bpy.context.active_object.modifiers)

            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="BevelMultiply", mods_list=mods_list, active_mod_name=active_mod)

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