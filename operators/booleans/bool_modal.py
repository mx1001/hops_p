import bpy
import gpu

from . import operator
from . editmode_intersect import edit_bool_intersect
from . editmode_union import edit_bool_union
from . editmode_difference import edit_bool_difference
from . editmode_slash import edit_bool_slash
from . editmode_inset import edit_bool_inset
from . editmode_knife import edit_bool_knife
from ... preferences import get_preferences
from ... ui_framework.master import Master
from ...ui_framework.utils.mods_list import get_mods_list
from ... utility.base_modal_controls import Base_Modal_Controls
from ... utils.toggle_view3d_panels import collapse_3D_view_panels

class HOPS_OT_BoolModal(bpy.types.Operator):
    bl_idname = "hops.bool_modal"
    bl_label = "Bool Modal"
    bl_options = {'REGISTER', 'UNDO', 'BLOCKING', 'GRAB_CURSOR'}
    bl_description = """Bool Modal
LMB - Create a new boolean relationship
LMB + Ctrl - Ignore sort and keep bevel modifiers on inset objects if they don't use vertex groups or bevel weight"""


    operation: bpy.props.EnumProperty(
        name="Operation",
        description="What kind of boolean operation to change to",
        items=[
            ('INTERSECT', "Intersect", "Peform an intersect operation"),
            ('UNION', "Union", "Peform a union operation"),
            ('DIFFERENCE', "Difference", "Peform a difference operation"),
            ('SLASH', "Slash", "Peform a slash operation"),
            ('INSET', "Inset", "Peform an inset operation"),
            ('OUTSET', "Outset", "Peform an outset operation"),
            ('KNIFE_BOOLEAN', "Knife Boolean", "Peform a knife boolean operation"),
            ('KNIFE_PROJECT', "Knife Project", "Peform a knife project operation")],
        default='DIFFERENCE')


    thickness: bpy.props.FloatProperty(
        name="Thickness",
        description="How deep the inset should cut",
        default=0.10,
        min=0.00,
        #soft_max=10.0,
        #step=1,
        precision=3)


    keep_bevels: bpy.props.BoolProperty(
        name="Keep Bevels",
        description="Keep Bevel modifiers on inset objects enabled if they don't use vertex groups or bevel weight",
        default=False)


    ignore_sort: bpy.props.BoolProperty(
        name="Ignore Sort",
        description="Ignore modifier sorting for this bool operation",
        default=False)


    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.mode in {'OBJECT', 'EDIT'}


    def draw(self, context):
        self.layout.prop(self, "operation")

        if self.operation in ('INSET', 'OUTSET'):
            self.layout.prop(self, "thickness")

            if context.active_object.mode == 'OBJECT':
                row = self.layout.row()
                row.prop(self, "keep_bevels")
                row.prop(self, "ignore_sort")

        elif context.active_object.mode == 'OBJECT':
            self.layout.prop(self, "ignore_sort")


    def invoke(self, context, event):

        # Unlike bool_shift, it is not necessary to push an undo step here

        try:
            kc = context.window_manager.keyconfigs
            km = kc.user.keymaps["3D View"]
            kmi = km.keymap_items["hops.bev_multi"]
            hotkey = kmi.type

        except:
            hotkey = None

        if event.type != hotkey:
            self.keep_bevels = event.ctrl
            self.ignore_sort = event.ctrl

            if event.shift:
                if self.operation == 'INSET':
                    self.operation = 'OUTSET'

                if self.operation == 'KNIFE_BOOLEAN':
                    self.operation = 'KNIFE_PROJECT'

        self.report_info(self.operation)
        self.get_overlays(context)
        self.execute(context)
        self.thick_adjust = False
        #UI System
        self.master = Master(context=context)
        self.master.only_use_fast_ui = True
        self.timer = context.window_manager.event_timer_add(0.025, window=context.window)
        self.base_controls = Base_Modal_Controls(context, event)
        self.original_tool_shelf, self.original_n_panel = collapse_3D_view_panels()
        context.window_manager.modal_handler_add(self)
        self.solidfy_list = []
        return {"RUNNING_MODAL"}


    def modal(self, context, event):

        # UI
        self.master.receive_event(event=event)
        self.base_controls.update(context, event)
        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        elif event.type == 'Z' and (event.shift or event.alt):
            return {'PASS_THROUGH'}

        elif self.base_controls.confirm:
            self.report_info('FINISHED')
            self.reset_overlays(context)
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            return {'FINISHED'}

        elif self.base_controls.cancel:
            self.report_info('CANCELLED')
            self.reset_overlays(context)
            self.cancel(context)
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            return {'CANCELLED'}

        elif event.type == 'T' and event.value == 'PRESS' :
            self.thick_adjust = not self.thick_adjust
        elif self.base_controls.mouse and self.thick_adjust and self.operation in {'INSET', 'OUTSET'}:
            self.thickness +=self.base_controls.mouse

            for mod in self.solidfy_list:
                mod.thickness = self.thickness
        
        elif self.base_controls.scroll or (event.type in {'X', 'Z'} and event.value == 'PRESS'):
            if event.type == 'X':
                self.scroll(1)
            elif event.type == 'Z':
                self.scroll(-1)
            else:
                self.scroll(self.base_controls.scroll)
            self.report_info(self.operation)
            self.cancel(context)
            self.execute(context)

        self.draw_modal(context)

        return {"RUNNING_MODAL"}


    def execute(self, context):

        if context.active_object.mode == 'OBJECT':

            if self.operation in {'INTERSECT', 'UNION', 'DIFFERENCE', 'SLASH', 'INSET'}:
                self.solidfy_list = operator.add(context, self.operation, sort=not self.ignore_sort, outset=False, thickness=self.thickness)
                self.reset_overlays(context)

            elif self.operation == 'OUTSET':
                self.solidfy_list = operator.add(context, 'INSET', sort=not self.ignore_sort, outset=True, thickness=self.thickness)
                self.reset_overlays(context)

            elif self.operation == 'KNIFE_BOOLEAN':
                operator.knife(context, False)
                self.set_overlays(context)

            elif self.operation == 'KNIFE_PROJECT':
                operator.knife(context, True, material_cut=True)
                self.set_overlays(context)

        elif context.active_object.mode == 'EDIT':
            if self.operation == 'INTERSECT':
                edit_bool_intersect(context, False)
                self.reset_overlays(context)

            elif self.operation == 'UNION':
                edit_bool_union(context, False)
                self.reset_overlays(context)

            elif self.operation == 'DIFFERENCE':
                edit_bool_difference(context, False)
                self.reset_overlays(context)

            elif self.operation == 'SLASH':
                edit_bool_slash(context, False)
                self.reset_overlays(context)

            elif self.operation == 'INSET':
                edit_bool_inset(context, False, False, self.thickness)
                self.reset_overlays(context)

            elif self.operation == 'OUTSET':
                edit_bool_inset(context, False, True, self.thickness)
                self.reset_overlays(context)

            elif self.operation == 'KNIFE_BOOLEAN':
                edit_bool_knife(context, False, False)
                self.reset_overlays(context)

            elif self.operation == 'KNIFE_PROJECT':
                edit_bool_knife(context, False, True)
                self.reset_overlays(context)

        return {'FINISHED'}


    def cancel(self, context):
        bpy.ops.ed.undo_push()
        bpy.ops.ed.undo()


    def report_info(self, info):
        words = [w.capitalize() for w in str(info).split("_")]
        self.report({'INFO'}, " ".join(words))


    def get_overlays(self, context):
        self.overlays = context.space_data.overlay.show_overlays
        self.wireframes = context.space_data.overlay.show_wireframes


    def set_overlays(self, context):
        context.space_data.overlay.show_overlays = True
        context.space_data.overlay.show_wireframes = True


    def reset_overlays(self, context):
        context.space_data.overlay.show_overlays = self.overlays
        context.space_data.overlay.show_wireframes = self.wireframes


    def scroll(self, direction):
        operations = ('INTERSECT', 'UNION', 'DIFFERENCE', 'SLASH', 'INSET', 'OUTSET', 'KNIFE_BOOLEAN', 'KNIFE_PROJECT')
        index = (operations.index(self.operation) + direction) % len(operations)
        self.operation = operations[index]


    def draw_modal(self, context):

        # Make the operation text look nice
        operation = " ".join([w.capitalize() for w in str(self.operation).split("_")])

        # Start
        self.master.setup()

        ########################
        #   Fast UI
        ########################

        if self.master.should_build_fast_ui():

            win_list = []
            help_list = []

            # Main
            if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1:
                win_list.append(operation)
                if self.operation in ('INSET', 'OUTSET'):
                    win_list.append(f"{self.thickness:.3f}")
            else:
                win_list.append("Interactive Boolean")
                win_list.append(f"Mode : {operation}")
                if self.operation in ('INSET', 'OUTSET'):
                    win_list.append(f"Thickness : {self.thickness:.3f}")
                    if context.active_object.mode == 'OBJECT':
                        win_list.append(f"Keep Bevels : {self.keep_bevels}")
                        win_list.append(f"Ignore Sort : {self.ignore_sort}")
                elif context.active_object.mode == 'OBJECT':
                    win_list.append(f"Ignore Sort : {self.ignore_sort}")

            # Help
            help_list.append(["T",  "Thickness Adjust"])
            help_list.append(["Wheel",  "Switch Operation"])
            help_list.append(["X / Z",  "Switch Operation"])
            help_list.append(["H",     "Toggle help."])
            help_list.append(["~",     "Toggle viewport displays."])

            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="InteractiveBoolean")

        # Finished
        self.master.finished()
