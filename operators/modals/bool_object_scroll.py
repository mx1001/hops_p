import bpy
from . import infobar
from ... preferences import get_preferences
from ... ui_framework.master import Master
from ... ui_framework.utils.mods_list import get_mods_list
from ... utility.base_modal_controls import Base_Modal_Controls
from ... utils.toggle_view3d_panels import collapse_3D_view_panels


class HOPS_OT_BoolObjectScroll(bpy.types.Operator):
    bl_idname = "hops.bool_scroll_objects"
    bl_label = "Scroll Booleans"
    bl_description = "Use the scroll wheel to scroll through boolean modifiers on the selected object."

    running: bool = False


    def invoke(self, context, event):

        self.running = True
        self.original_visible = context.visible_objects[:]
        self.active = context.active_object
        self.modifiers = [mod for mod in context.active_object.modifiers if mod.type == "BOOLEAN"]
        if get_preferences().property.bool_scroll == 'ADDITIVE':
            self.obj_list = [{"object": mod.object, "hide": mod.object.hide_viewport, "override": True} for mod in self.modifiers if mod.object is not None and mod.object.hide_get() or mod.object.hide_viewport]
        else:
            self.obj_list = [{"object": mod.object, "hide": mod.object.hide_viewport, "override": True} for mod in self.modifiers if mod.object is not None]
        self.obj_index = 0
        self.obj_name = ""
        self.ctrl_a = True
        self.show_current = True

        if not self.obj_list:
            return{'CANCELLED'}

        in_cutters = False
        if 'Cutters' in bpy.data.collections:
            for obj in self.obj_list:
                if obj['object'].name in bpy.data.collections['Cutters'].objects:
                    in_cutters = True
                    break

        if in_cutters:
            objects = bpy.data.collections['Cutters'].objects[:]
            bpy.data.collections.remove(bpy.data.collections['Cutters'])

            context.scene.collection.children.link(bpy.data.collections.new(name='Cutters'))

            for obj in objects:
                bpy.data.collections['Cutters'].objects.link(obj)

        bpy.ops.object.hide_view_clear()

        for obj in [i['object'] for i in self.obj_list]:
            obj.hide_viewport = True

        for obj in context.visible_objects:
            obj.select_set(obj not in self.original_visible)

        bpy.ops.object.hide_view_set()

        self.active.select_set(True)
        context.view_layer.objects.active= self.active

        # Base Systems
        self.master = Master(context=context)
        self.master.only_use_fast_ui = True
        self.base_controls = Base_Modal_Controls(context, event)
        self.original_tool_shelf, self.original_n_panel = collapse_3D_view_panels()

        context.window_manager.modal_handler_add(self)
        infobar.initiate(self)
        return {'RUNNING_MODAL'}


    def modal(self, context, event):

        # Base Systems
        self.master.receive_event(event=event)
        self.base_controls.update(context, event)

        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        if self.base_controls.scroll:
            if event.shift:
                if self.base_controls.scroll ==1:
                    bpy.ops.object.modifier_move_up(modifier=self.modifiers[self.obj_index].name)
                elif  self.base_controls.scroll == -1:
                    bpy.ops.object.modifier_move_down(modifier=self.modifiers[self.obj_index].name)
            else:
                self.obj_index += self.base_controls.scroll

        if self.obj_index >= len(self.obj_list):
            self.obj_index = 0

        if self.obj_index < 0:
            self.obj_index = len(self.obj_list) - 1

        if not len(self.obj_list) > 0:
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            infobar.remove(self)
            return {'FINISHED'}

        obj = self.obj_list[self.obj_index]["object"]

        for data in self.obj_list:
            data["object"].hide_viewport = data["override"]

        override_value = self.obj_list[self.obj_index]["override"]

        if self.show_current:
            obj.hide_viewport = False

        self.obj_name = obj.name

        if event.type == 'F' and event.value == 'PRESS':
            for mod in self.modifiers:
                if mod.type == "BOOLEAN":
                    if mod.object == obj:
                        bpy.ops.object.modifier_apply(modifier=mod.name) # apply_as='DATA',
                        self.obj_list.remove(self.obj_list[self.obj_index])
                        if not event.shift:
                            bpy.data.objects.remove(obj)

        if event.type == 'A' and event.value == 'PRESS':
            self.obj_list[self.obj_index]["override"] = not override_value
            obj.hide_viewport = override_value

        if event.type == 'T' and event.value == 'PRESS':
            self.modifiers[self.obj_index].show_viewport = not self.modifiers[self.obj_index].show_viewport

        if event.ctrl: # ctrl+a to toggle object visibility
            if event.type == 'A' and event.value == 'PRESS':
                self.ctrl_a = not self.ctrl_a
                for data in self.obj_list:
                    data["override"] = self.ctrl_a

        if event.type == "W" and event.value == "PRESS" and event.shift  and not event.ctrl:
            #would be cooler with a for that also set the ones leading up to this to be toggled off or on as well.
            # for proxe later.
            if self.modifiers[self.obj_index] != None:
                active_mod = self.modifiers[self.obj_index]
                active_mod.show_render = not active_mod.show_render
                self.report({'INFO'}, F'Modifiers Renderability : {active_mod.show_render}')

        if event.type == "W" and event.value == "PRESS" and event.ctrl and not event.shift:
            for mod in self.modifiers:
                mod.show_render = not mod.show_render
            self.report({'INFO'}, F'Modifier Visibility Re-enabled : {len(self.modifiers)}')

        if event.type == "H" and event.value == "PRESS":
            get_preferences().property.hops_modal_help = not get_preferences().property.hops_modal_help

        if self.base_controls.confirm or event.type in { 'RET', 'NUMPAD_ENTER'}:
            self.finish(context)
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            infobar.remove(self)
            return {'FINISHED'}

        if self.base_controls.cancel or event.type in {'BACK_SPACE'}:
            self.finish(context, cancel=True)
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            infobar.remove(self)
            return {'CANCELLED'}

        self.draw_master(context=context)

        context.area.tag_redraw()

        return {'RUNNING_MODAL'}


    def finish(self, context, cancel=False):

        self.running = False

        for obj in self.obj_list:
            if obj['object'].hide_viewport:
                obj['object'].hide_viewport = False
                obj['object'].select_set(True)
            else:
                obj['object'].select_set(False)

        self.active.select_set(False)

        bpy.ops.object.hide_view_set()

        obj = self.obj_list[self.obj_index]["object"]
        context.view_layer.objects.active = obj
        obj.select_set(True)

        if cancel:
            bpy.ops.object.hide_view_clear()

            for obj in context.visible_objects:
                obj.select_set(obj not in self.original_visible)

            bpy.ops.object.hide_view_set()

            self.active.select_set(True)
            context.view_layer.objects.active = self.active


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
                win_list.append("{}".format(self.obj_index + 1))
                win_list.append("{}".format(self.obj_name))
                # try:
                #     win_list.append("{}".format(self.modifiers[self.obj_index].name))
                #
                # except:
                #     win_list.append("{}".format('APPLIED'))
            else:
                win_list.append("Bool Scroll")
                win_list.append("{}".format(self.obj_index + 1))
                win_list.append("{}".format(self.obj_name))

                try:
                    win_list.append("{}".format(self.modifiers[self.obj_index].name))

                except:
                    win_list.append("{}".format('APPLIED'))

            # Help
            help_list.append(["scroll",    "Change boolean visibility."])
            help_list.append(["A",         "Toggle current visibility"])
            help_list.append(["Ctrl + A",  "Toggle all visibility"])
            help_list.append(["F",         "Apply current object"])
            help_list.append(["shift + F", "Apply and keep current object"])
            help_list.append(["Shift + Scroll", "Move mod up/down"])
            help_list.append(["T",         "Toggle modifier visibility"])
            # help_list.append(["W",         "Toggle render visibility / Sort Lock toggle"])
            help_list.append(["M",         "Toggle mods list."])
            help_list.append(["H",         "Toggle help."])
            help_list.append(["~",         "Toggle viewport displays."])
            help_list.append(["O",         "Toggle viewport rendering"])

            # Mods
            if self.modifiers[self.obj_index] != None:
                active_mod = self.modifiers[self.obj_index].name
                
            mods_list = get_mods_list(mods=bpy.context.active_object.modifiers)

            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="Booleans", mods_list=mods_list, active_mod_name=active_mod)

        # Finished
        self.master.finished()
