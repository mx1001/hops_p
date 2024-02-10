import bpy, math
from mathutils import Vector
from bpy.props import IntProperty, FloatProperty
from . import infobar
from ... preferences import get_preferences
from ... ui_framework.master import Master
from ... ui_framework.utils.mods_list import get_mods_list
from ... utility.base_modal_controls import Base_Modal_Controls

# Cursor Warp imports
from ... utils.toggle_view3d_panels import collapse_3D_view_panels
from ... utils.modal_frame_drawing import draw_modal_frame
from ... utils.cursor_warp import mouse_warp
from ... addon.utility import method_handler


class HOPS_OT_AdjustCurveOperator(bpy.types.Operator):
    bl_idname = "hops.adjust_curve"
    bl_label = "Adjust Curve"
    bl_description = "Interactive Curve adjustment. 1/2/3 provides presets for curves"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}

    first_mouse_x: IntProperty()
    first_value: FloatProperty()
    second_value: IntProperty()

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "CURVE"


    def invoke(self, context, event):

        self.back_dict = {}
        self.active_curve = context.active_object
        
        if self.active_curve:
            self.active_curve.select_set(True)

        self.slected_curves = [c for c in context.selected_objects if c.type == 'CURVE' and c.data.splines]
        self.back_objects() 
        self.master = None

        self.fill_type_3d = ["FULL", "BACK", "FRONT", "HALF"]
        self.fill_type_2d = ["NONE", "BACK", "FRONT", "BOTH"] 
        self.spline_type = ["POLY", "NURBS", "BEZIER"]

        if not self.active_curve or not self.active_curve.data.splines:
            if self.slected_curves:
                self.active_curve = self.slected_curves[0]

            else:

                self.active_curve = None
        
        if self.active_curve:
            
            if not self.active_curve.data.splines.active:
                self.active_curve.data.splines.active =  self.active_curve.data.splines[0]

            self.start_fill_mode = self.active_curve.data.fill_mode
            self.start_spline_type = self.active_curve.data.splines.active.type
            self.spline_type_index = self.spline_type.index(self.start_spline_type) 
            self.fill_index = self.fill_type_3d.index(self.start_fill_mode) if self.active_curve.data.dimensions == '3D' else  self.fill_type_2d.index(self.start_fill_mode)
            self.start_show_wire = self.active_curve.show_wire
            # Base Systems
            self.master = Master(context=context)
            self.master.only_use_fast_ui = True
            self.base_controls = Base_Modal_Controls(context, event)
            self.original_tool_shelf, self.original_n_panel = collapse_3D_view_panels()
            self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.safe_draw_shader, (context,), 'WINDOW', 'POST_PIXEL')


            context.window_manager.modal_handler_add(self)
            infobar.initiate(self)
            return {"RUNNING_MODAL"}

        else:
            self.report({'WARNING'}, "No valid curve objects in selection, could not finish")
            return {'CANCELLED'}


    def modal(self, context, event):

        # Base Systems
        self.master.receive_event(event=event)
        self.base_controls.update(context, event)
        mouse_warp(context, event)

        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        if self.base_controls.mouse:
            for curve in self.slected_curves:
                curve.data.bevel_depth += self.base_controls.mouse

        if self.base_controls.scroll:
            #bevel res
            if event.ctrl :
                for curve in self.slected_curves:
                    curve.data.resolution_u += self.base_controls.scroll
                    curve.data.render_resolution_u = curve.data.resolution_u
                self.report({'INFO'}, F'Curve Resolution : {self.active_curve.data.resolution_u}')
            #curve order
            elif event.shift :
                for curve in self.slected_curves:
                    self.splines_add(curve.data.splines, "order_u", self.base_controls.scroll)# spline.order_u += self.base_controls.scroll
                self.report({'INFO'}, F'Spline order:{self.active_curve.data.splines.active.order_u }')
            #bevel res
            else:
                for curve in self.slected_curves:
                    curve.data.bevel_resolution += self.base_controls.scroll
                    self.report({'INFO'}, F'Curve Bevel Resolution : {self.active_curve.data.bevel_resolution}')

        if event.type == 'S' and event.value == 'PRESS':

            if not event.shift:
                for curve in self.slected_curves:
                    for spline in curve.data.splines:
                        spline.use_smooth = not spline.use_smooth
                smooth = self.active_curve.data.splines.active.use_smooth
                shade ={True:"Smooth", False:"Flat"}
                self.report({'INFO'}, F'Shade {shade[smooth]}')
            else:
                use_smooth = self.active_curve.data.splines.active.use_smooth
                for curve in self.slected_curves:
                    self.splines_set(curve.data.splines, "use_smooth", use_smooth)                    
                self.report({'INFO'}, F'Shading Synced')

        edgeSplit = [mod.name for mod in self.active_curve.modifiers if mod.type == 'EDGE_SPLIT']

        if event.type == 'C' and event.value == 'PRESS':
            for curve in self.slected_curves:
                for spline in curve.data.splines:
                    length_limit = False
                    if spline.type == 'BEZIER'and len(spline.bezier_points)>1 :
                        length_limit = True
                    elif len(spline.points) >2:
                        length_limit = True
                    spline.use_cyclic_u = not spline.use_cyclic_u if length_limit else False
            self.report({'INFO'}, F'Toggled Cyclic')

        if event.type == 'W' and event.value == 'PRESS':
            for curve in self.slected_curves:
                curve.show_wire = not curve.show_wire
            wire ={True:"ON", False:"OFF"}
            self.report({'INFO'}, F'Wireframe:{wire[self.active_curve.show_wire]}')

        if event.type == 'F' and event.value == 'PRESS':
            self.fill_index= self.fill_index+1 if self.fill_index<3 else 0
            for curve in self.slected_curves:
                curve.data.fill_mode = self.fill_type_3d[self.fill_index] if curve.data.dimensions == '3D' else self.fill_type_2d[self.fill_index]
            self.report({'INFO'}, F'Fill Mode:{self.active_curve.data.fill_mode}')

        if event.type == 'V' and event.value == 'PRESS':
            self.spline_type_index = self.spline_type_index+1 if self.spline_type_index<2 else 0
            self.active_curve.data.splines.active.type = self.spline_type[self.spline_type_index]
            if self.active_curve.data.splines.active.type != 'BEZIER' and self.spline_type_index == 2:
                self.spline_type_index =0
            for curve in self.slected_curves:
                for spline in curve.data.splines:
                    spline.type = self.spline_type[self.spline_type_index]
                    self.spline_type[self.spline_type_index]
                curve.data.splines.update()
            if get_preferences().ui.Hops_extra_info:
                bpy.ops.hops.display_notification(info=F'Spline Type : {self.active_curve.data.splines.active.type}', name="")
            self.report({'INFO'}, F'Spline type:{self.active_curve.data.splines.active.type}')

        if event.type == 'ONE' and event.value == 'PRESS':
            for curve in self.slected_curves:
                curve.data.resolution_u = 6
                curve.data.render_resolution_u = 12
                curve.data.bevel_resolution = 6
                curve.data.fill_mode = 'FULL'
            self.report({'INFO'}, F'Resolution : 6')

            for name in edgeSplit:
                bpy.ops.object.modifier_remove(modifier=name)

        if event.type == 'TWO' and event.value == 'PRESS':
            for curve in self.slected_curves:
                curve.data.resolution_u = 64
                curve.data.render_resolution_u = 64
                curve.data.bevel_resolution = 16
                curve.data.fill_mode = 'FULL'
            self.report({'INFO'}, F'Resolution : 64')

            for name in edgeSplit:
                bpy.ops.object.modifier_remove(modifier=name)

        if event.type == 'THREE' and event.value == 'PRESS':
            for curve in self.slected_curves:
                curve.data.resolution_u = 64
                curve.data.render_resolution_u = 64
                curve.data.bevel_resolution = 0
                curve.data.fill_mode = 'FULL'
            if not len(edgeSplit):
                bpy.ops.object.modifier_add(type='EDGE_SPLIT')
                self.active_curve.modifiers["EdgeSplit"].split_angle = math.radians(60)
            self.report({'INFO'}, F'Resolution : 64 / Edge Split Added')

        if self.base_controls.tilde and event.shift == True:
            bpy.context.space_data.overlay.show_overlays = not bpy.context.space_data.overlay.show_overlays

        if self.base_controls.confirm:
            if not self.start_show_wire:
                for curve in self.slected_curves:
                    curve.show_wire = False
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            infobar.remove(self)
            return {'FINISHED'}

        if event.type == 'X' and event.value == 'PRESS':
            for curve in self.slected_curves:
                curve.data.bevel_depth = 0.0
            self.report({'INFO'}, F'Depth Set To 0 - exit')
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            infobar.remove(self)
            return {'FINISHED'}

        if self.base_controls.cancel:
            #self.reset_object()
            self.restore_objects()
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            infobar.remove(self)
            return {'CANCELLED'}

        self.draw_master(context=context)

        context.area.tag_redraw()

        return {"RUNNING_MODAL"}


    # def reset_object(self):
    #     self.active_curve.show_wire = self.start_show_wire
    #     self.active_curve.data.fill_mode = self.start_fill_mode
    #     self.active_curve.data.bevel_depth = self.start_bevel_depth
    #     for spline in self.active_curve.data.splines:
    #         spline.type = self.start_spline_type
    #         spline.order_u =self.start_order_u

    def back_objects(self):
        
        for curve in self.slected_curves:
            back = {}
            back["show_wire"]= curve.show_wire
            back["fill_mode"]= curve.data.fill_mode
            back["bevel_depth"]= curve.data.bevel_depth
            back["bevel_resolution"]= curve.data.bevel_resolution
            back["resolution_u"] = curve.data.resolution_u 
            back["render_resolution_u"] = curve.data.render_resolution_u
            back["spline_type"] = [spline.type for spline in curve.data.splines]
            back["spline_order_u"] = [spline.order_u for spline in curve.data.splines]
            back["use_cyclic_u"] = [spline.use_cyclic_u for spline in curve.data.splines]
            self.back_dict.update({curve:back})

    def restore_objects(self):
        
        for curve, back in self.back_dict.items():
            curve.show_wire = back["show_wire"]
            curve.data.fill_mode = back["fill_mode"]
            curve.data.bevel_depth = back["bevel_depth"]
            curve.data.bevel_resolution = back["bevel_resolution"]
            curve.data.resolution_u = back["resolution_u"]
            curve.data.render_resolution_u = back["render_resolution_u"]
            for spline , spline_type, spline_order, use_cyclic_u in zip(
                curve.data.splines, back["spline_type"], back["spline_order_u"], back["use_cyclic_u"] ):
                spline.type = spline_type
                spline.order_u = spline_order
                spline.use_cyclic_u = use_cyclic_u


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
                win_list.append("{:.2f}".format(self.active_curve.data.bevel_depth))
                win_list.append("{:.0f}".format(self.active_curve.data.render_resolution_u))
                win_list.append("{:.0f}".format(self.active_curve.data.bevel_resolution))
            else:
                win_list.append("Curve Adjust")
                win_list.append(self.active_curve.data.splines.active.type)
                win_list.append(F"Fill type: {self.active_curve.data.fill_mode}")
                win_list.append("Width - {:.3f}".format(self.active_curve.data.bevel_depth))
                win_list.append("Segments (ctrl) - {:.0f}".format(self.active_curve.data.render_resolution_u))
                win_list.append("Profile:{:.0f}".format(self.active_curve.data.bevel_resolution))
                win_list.append("Order:{:.0f}".format(self.active_curve.data.splines.active.order_u))
            # Help
            help_list.append(["X",             "Set Depth to 0 and end"])
            help_list.append(["C",             "Toggle cyclic"])
            help_list.append(["V",             "Cycle spline type"])
            help_list.append(["SHIFT+S",       "Sync spline shading"])
            help_list.append(["S",             "Toggle smooth shading"])
            help_list.append(["W",             "Toggle Wireframe"])
            help_list.append(["F",             "Cycle Fill Mode"])
            help_list.append(["3",             "Set profile 64 x 4 (Box)"])
            help_list.append(["2",             "Set profile 64 x 16"])
            help_list.append(["1",             "Set profile 12 x 6"])
            help_list.append(["Shift + Scroll", "Set  order"])
            help_list.append(["Ctrl + Scroll", "Set segments"])
            help_list.append(["Scroll",        "Set resolution"])
            help_list.append(["Mouse",          "Adjust Bevel Depth"])
            help_list.append(["M",             "Toggle mods list."])
            help_list.append(["H",             "Toggle help."])
            help_list.append(["~",             "Toggle viewport displays."])
            help_list.append(["O",             "Toggle viewport rendering"])

            # Mods
            mods_list = get_mods_list(mods=bpy.context.active_object.modifiers)

            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="Curve", mods_list=mods_list, active_mod_name=active_mod)

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


    def splines_set (self, splines=[], attr = "", val = None ):
        for spline in splines:
            setattr(spline, attr, val )
    
    def splines_add (self, splines=[], attr = "", val = None ):
        for spline in splines:
            current = getattr(spline, attr)
            setattr(spline, attr, current+val )