import bpy, bmesh
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


class HOPS_OT_AdjustBevelWeightOperator(bpy.types.Operator):
    bl_idname = "hops.bevel_weight"
    bl_label = "Adjust Bevel Weight"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}
    bl_description = """Adjust the bevel weight of selected edges
Press H for help"""


    @classmethod
    def poll(cls, context):
        object = context.active_object
        return(object.type == 'MESH' and context.mode == 'EDIT_MESH')

    def invoke(self, context, event):

        self.value = 0
        self.start_value = self.detect(context)
        self.offset = 0

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


        self.offset += self.base_controls.mouse
        self.offset = 1 if self.offset> 1 else self.offset
        self.offset = -1 if self.offset< -1 else self.offset
        self.value_base = float("{:.2f}".format(self.start_value + self.offset))
        self.value = max(self.value_base, 0) and min(self.value_base, 1)

        if not event.ctrl and not event.shift:
            self.value = round(self.value, 1)

        obj = bpy.context.object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        bw = bm.edges.layers.bevel_weight.verify()

        selected = [e for e in bm.edges if e.select]
        for e in selected:
            e[bw] = self.value

        bmesh.update_edit_mesh(me)

        if self.base_controls.cancel:
            for e in selected:
                e[bw] = self.start_value
            bmesh.update_edit_mesh(me)
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            return {'CANCELLED'}

        if self.base_controls.confirm:
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            return {'FINISHED'}

        if event.type == 'A' and event.value == 'PRESS' and event.ctrl:
            selectedbw = [e for e in bm.edges if e[bw] > 0]
            for e in selectedbw:
                e.select_set(True)

        elif event.type == 'A' and event.value == 'PRESS' and not event.ctrl:
            bpy.ops.mesh.select_linked(delimit=set())
            selectedbw = [e for e in bm.edges if e[bw] == 0]

            for e in selectedbw:
                e.select_set(False)
                for elem in reversed(bm.select_history):
                    if isinstance(elem, bmesh.types.BMEdge):
                        elem.select_set(True)

        self.draw_master(context=context)

        context.area.tag_redraw()

        return {"RUNNING_MODAL"}


    def detect(self, context):

        obj = bpy.context.object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        bw = bm.edges.layers.bevel_weight.verify()

        selected = [e for e in bm.edges if e.select]

        bmesh.update_edit_mesh(me)

        if len(selected) > 0:
            return selected[-1][bw]
        else:
            return 0


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
            if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1:
                win_list.append(self.value)
            else:
                win_list.append("Bevel Weight")
                win_list.append(self.value)

            # Help
            help_list.append(["A",        "Select all weights in mesh"])
            help_list.append(["Ctrl + A", "Select all weights"])
            help_list.append(["H",         "Toggle help."])
            #help_list.append(["M",         "Toggle mods list."])

            # Mods
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