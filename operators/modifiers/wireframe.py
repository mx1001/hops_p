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


class HOPS_OT_MOD_Wireframe(bpy.types.Operator):
    bl_idname = "hops.mod_wireframe"
    bl_label = "Adjust Wireframe Modifier"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}
    bl_description = """
LMB - Adjust Wireframe Modifier
LMB + CTRL - Add new Wireframe Modifier

Press H for help.
"""

    wireframe_objects = {}

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    @staticmethod
    def wireframe_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "WIREFRAME"]


    def invoke(self, context, event):

        self.modal_scale = get_preferences().ui.Hops_modal_scale
        self.wireframe_objects = {}

        for object in [o for o in context.selected_objects if o.type == 'MESH']:
            self.get_deform_modifier(object, event)

        self.active_wireframe_modifier = context.object.modifiers[self.wireframe_objects[context.object.name]["modifier"]]
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

        offset = self.base_controls.mouse
        context.area.header_text_set("Hardops Wireframe:      B : use_boundary - {}      C : use_crease - {}      Q : use_even_offset - {}      W : use_relative_offset - {}".format(self.active_wireframe_modifier.use_boundary, self.active_wireframe_modifier.use_crease, self.active_wireframe_modifier.use_even_offset, self.active_wireframe_modifier.use_relative_offset))

        for object_name in self.wireframe_objects:
            object = bpy.data.objects[object_name]
            modifier = object.modifiers[self.wireframe_objects[object_name]["modifier"]]

            if self.base_controls.scroll:
                if event.shift:
                    if self.base_controls.scroll ==1:
                        bpy.ops.object.modifier_move_up(modifier=modifier.name)
                    else:
                        bpy.ops.object.modifier_move_down(modifier=modifier.name)

            if event.ctrl:
                modifier.offset = modifier.offset + offset
            else:
                modifier.thickness = modifier.thickness + offset

            if event.type == "Q" and event.value == "PRESS":
                modifier.use_even_offset = not modifier.use_even_offset

            if event.type == "W" and event.value == "PRESS":
                modifier.use_relative_offset = not modifier.use_relative_offset

            if event.type == "E" and event.value == "PRESS":
                modifier.use_replace = not modifier.use_replace

            if event.type == "B" and event.value == "PRESS":
                modifier.use_boundary = not modifier.use_boundary

            if event.type == "C" and event.value == "PRESS":
                modifier.use_crease = not modifier.use_crease

            if event.type == "Q" and event.value == "PRESS":
                bpy.ops.object.modifier_move_up(modifier=modifier.name)

            if event.type == "W" and event.value == "PRESS":
                bpy.ops.object.modifier_move_down(modifier=modifier.name)

            if event.type == "H" and event.value == "PRESS":
                bpy.context.space_data.show_gizmo_navigate = True

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
            try: self.wireframe_objects.setdefault(object.name, {})["modifier"] = self.wireframe_modifiers(object)[-1].name
            except: self.add_deform_modifier(object)


    def add_deform_modifier(self, object):
        wireframe_modifier = object.modifiers.new(name="Wireframe", type="WIREFRAME")
        wireframe_modifier.thickness = 0.2
        wireframe_modifier.use_even_offset = True
        wireframe_modifier.use_relative_offset = False
        wireframe_modifier.use_replace = True
        wireframe_modifier.use_boundary = True

        self.wireframe_objects.setdefault(object.name, {})["modifier"] = wireframe_modifier.name
        self.wireframe_objects[object.name]["added_modifier"] = True


    def store_values(self):
        for object_name in self.wireframe_objects:
            object = bpy.data.objects[object_name]
            modifier = object.modifiers[self.wireframe_objects[object_name]["modifier"]]
            self.wireframe_objects[object_name]["show_viewport"] = modifier.show_viewport
            self.wireframe_objects[object_name]["thickness"] = modifier.thickness
            self.wireframe_objects[object_name]["offset"] = modifier.offset
            self.wireframe_objects[object_name]["use_even_offset"] = modifier.use_even_offset
            self.wireframe_objects[object_name]["use_relative_offset"] = modifier.use_relative_offset
            self.wireframe_objects[object_name]["use_replace"] = modifier.use_replace
            self.wireframe_objects[object_name]["use_boundary"] = modifier.use_boundary
            self.wireframe_objects[object_name]["use_crease"] = modifier.use_crease


    def restore(self):
        for object_name in self.wireframe_objects:
            object = bpy.data.objects[object_name]
            if "added_modifier" in self.wireframe_objects[object_name]:
                object.modifiers.remove(object.modifiers[self.wireframe_objects[object_name]["modifier"]])
            else:
                modifier = object.modifiers[self.wireframe_objects[object_name]["modifier"]]
                modifier.show_viewport = self.wireframe_objects[object_name]["show_viewport"]
                modifier.thickness = self.wireframe_objects[object_name]["thickness"]
                modifier.offset = self.wireframe_objects[object_name]["offset"]
                modifier.use_even_offset = self.wireframe_objects[object_name]["use_even_offset"]
                modifier.use_relative_offset = self.wireframe_objects[object_name]["use_relative_offset"]
                modifier.use_replace = self.wireframe_objects[object_name]["use_replace"]
                modifier.use_boundary = self.wireframe_objects[object_name]["use_boundary"]
                modifier.use_crease = self.wireframe_objects[object_name]["use_crease"]


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
                win_list.append("{:.3f}".format(self.active_wireframe_modifier.thickness))
                win_list.append("{:.3f}".format(self.active_wireframe_modifier.offset))
                win_list.append("{}".format(self.active_wireframe_modifier.use_replace))
            else:
                win_list.append("Wireframe")
                win_list.append("Thick: {:.3f}".format(self.active_wireframe_modifier.thickness))
                win_list.append("Offset: {:.3f}".format(self.active_wireframe_modifier.offset))
                win_list.append("Replace: {}".format(self.active_wireframe_modifier.use_replace))

            # Help
            help_list.append(["Move",           "set thickness"])
            help_list.append(["Ctrl",           "set offset"])
            help_list.append(["Q",              "Use even offset"])
            help_list.append(["W",              "Use relative offset"])
            help_list.append(["E",              "Use replace"])
            help_list.append(["C",              "Use crease"])
            help_list.append(["B",              "Use boundary"])
            help_list.append(["Q",              "Move mod DOWN"])
            help_list.append(["W",              "Move mod UP"])
            help_list.append(["Shift + Scroll", "Move mod up/down"])
            help_list.append(["M",              "Toggle mods list."])
            help_list.append(["H",              "Toggle help."])
            help_list.append(["~",              "Toggle viewport displays."])
            help_list.append(["O",              "Toggle viewport rendering"])

            # Mods
            if self.active_wireframe_modifier != None:
                active_mod = self.active_wireframe_modifier.name

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