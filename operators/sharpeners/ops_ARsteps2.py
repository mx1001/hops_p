import os
import bpy
import bmesh
from bgl import *
from bpy.props import *
from bpy.props import *
import bpy.utils.previews
from random import choice
from math import pi, radians
from math import radians, degrees
from ... operators.utils import update_bevel_modifier_if_necessary
from ... utils.context import ExecutionContext
from ... utils.blender_ui import get_location_in_current_3d_view
from ... overlay_drawer import show_custom_overlay, disable_active_overlays
from ... graphics.drawing2d import set_drawing_dpi, draw_horizontal_line, draw_boolean, draw_text, draw_box, draw_logo_csharp
from ... utils.objects import get_modifier_with_type, apply_modifiers
from . complex_sharpen import complex_sharpen_active_object
from ... preferences import tool_overlays_enabled, get_hops_preferences_colors_with_transparency, Hops_display_time, Hops_fadeout_time

mod_types = [
    ("BOOLEAN", "Boolean", ""),
    ("MIRROR", "Mirror", ""),
    ("BEVEL", "Bevel", ""),
    ("SOLIDIFY", "Solidify", ""),
    ("ARRAY", "Array", ""),]

class SstepOperator(bpy.types.Operator):
    bl_idname = "step.sstep"
    bl_label = "Sstep Operator"
    bl_description = "Bake Modifiers And Recalculate"
    bl_options = {"REGISTER", "UNDO"}
    
    text = "(S)Step - New bevels calculated."
    op_tag = "SSTEP"
    op_detail = "No new bevels were baked - Bools Baked"

    items = [(x.identifier, x.name, x.description, x.icon) 
                 for x in bpy.types.Modifier.bl_rna.properties['type'].enum_items]

    modifier_types = EnumProperty(name = "Modifier Types", default = {'BOOLEAN', 'SOLIDIFY'},
            options = {"ENUM_FLAG"}, items = mod_types)

    segment_amount = IntProperty(name="Segments", description = "Segments For Bevel", default = 3, min = 1, max = 12)

    bevelwidth = FloatProperty(name="Bevel Width Amount",
                               description="Set Bevel Width",
                               default=0.0200,
                               min = 0.002,
                               max =1.50)

    sharpness = FloatProperty(name = "Sharpness", default = radians(30),
                              min = radians(1), max = radians(180), subtype = "ANGLE")

    auto_smooth_angle = FloatProperty(name = "Auto Smooth Angle", default = radians(60),
                              min = 0.0, max = radians(180), subtype = "ANGLE")

    additive_mode = BoolProperty(name = "Additive Mode",
                              description = "Don't clear existing edge properties",
                              default = True)

    sub_d_sharpening = BoolProperty(name = "Sub-D Sharpening")

    profile_value = 0.70

    reveal_mesh = False

    
    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"    

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        col = box.column()
        
        col.prop(self, "modifier_types", expand=True)
        box.prop( self, 'sharpness', text = "(S)Step Angle" )
    
    def invoke(self, context, event):
        self.execute(context)

        if tool_overlays_enabled():
            disable_active_overlays()
            self.wake_up_overlay = show_custom_overlay(draw,
                parameter_getter = self.parameter_getter,
                location = get_location_in_current_3d_view("CENTER", "BOTTOM", offset = (0, 130)),
                location_type = "CUSTOM",
                stay_time = Hops_display_time(),
                fadeout_time = Hops_fadeout_time())

        return {"FINISHED"}

    def parameter_getter(self):
        return self.auto_smooth_angle, self.segment_amount, self.bevelwidth, self.op_detail, self.op_tag, self.text

    
    def execute(self, context):
        active = bpy.context.active_object

        complex_sharpen_active_object(
            context.active_object,
            self.sharpness,
            self.auto_smooth_angle,
            self.additive_mode,
            self.sub_d_sharpening,
            self.modifier_types,
            self.segment_amount,
            self.bevelwidth,
            self.reveal_mesh)

        update_bevel_modifier_if_necessary(
            context.active_object,
            self.segment_amount, 
            self.bevelwidth,
            self.profile_value)

        bpy.ops.object.select_all(action='DESELECT')
        active.select = True

        try: self.wake_up_overlay()
        except: pass
    
        return {"FINISHED"}


class CstepOperator(bpy.types.Operator):
    bl_idname = "step.cstep"
    bl_label = "Cstep Operator"
    bl_description = "Bake Modifiers And Add New Bevel"
    bl_options = {"REGISTER", "UNDO"}
    
    text = "(C)Step - New bevels calculated."
    op_tag = "CSTEP"
    op_detail = "Bevels were baked and re-added"
    
    items = [(x.identifier, x.name, x.description, x.icon) 
                 for x in bpy.types.Modifier.bl_rna.properties['type'].enum_items]

    modifier_types = EnumProperty(name = "Modifier Types", default = {'BEVEL'},
            options = {"ENUM_FLAG"}, items = mod_types)

    auto_smooth_angle = FloatProperty(name="AutoSmooth Angle",
                          description="Set AutoSmooth angle",
                          default= radians(60.0),
                          min = 0.0,
                          max = radians(180.0),
                          subtype='ANGLE')

    ssharpangle = FloatProperty(name="SSharpening Angle", 
                                description="Set SSharp Angle", 
                                default= 30.0, 
                                min = 0.0, 
                                max = 180.0)
    bevelwidth = FloatProperty(name="Bevel Width Amount", description="Set Bevel Width", default= 0.01, min = 0.002, max = 0.25)

    segment_amount = IntProperty(name="Segments", description = "Segments For Bevel", default = 6, min = 1, max = 12)

    bevelwidth = FloatProperty(name="Bevel Width Amount",
                               description="Set Bevel Width",
                               default=0.0200,
                               min = 0.002,
                               max =1.50)

    hide_mesh =  BoolProperty(name = "Hide Mesh",
                              description = "Hide Mesh",
                              default = True)

    set_status =  BoolProperty(name = "Set Cstep Status",
                              description = "Set Cstep Status",
                              default = True)

    profile_value = 0.70
    
    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"    

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column()
        
        col.prop(self, "modifier_types", expand=True)
        box.prop( self, 'ssharpangle', text = "(C)Step Angle" )
        box.prop( self, 'set_status', text = "set (C)Step Status" )
        box.prop( self, 'hide_mesh', text = "Hide Mesh" )
    
    def invoke(self, context, event):
        self.execute(context)
        
        if tool_overlays_enabled():
            disable_active_overlays()
            self.wake_up_overlay = show_custom_overlay(draw,
                parameter_getter = self.parameter_getter,
                location = get_location_in_current_3d_view("CENTER", "BOTTOM", offset = (0, 130)),
                location_type = "CUSTOM",
                stay_time = Hops_display_time(),
                fadeout_time = Hops_fadeout_time())
                
        return {"FINISHED"}
    
    def parameter_getter(self):
        return self.auto_smooth_angle, self.segment_amount, self.bevelwidth, self.op_detail, self.op_tag, self.text,

    def execute(self, context):
        self.c_step_active_object(context.active_object,
            self.modifier_types)

        update_bevel_modifier_if_necessary(
            context.active_object,
            self.segment_amount, 
            self.bevelwidth,
            self.profile_value)

        if self.set_status:
            object = bpy.context.active_object
            object.hops.status = "CSTEP"
                
        try: self.wake_up_overlay()
        except: pass
    
        return {"FINISHED"}
    
    def c_step_active_object(self, object, modifier_types):
        with ExecutionContext(mode = "OBJECT", active_object = object):
            apply_modifiers(object, modifier_types)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.transform.edge_bevelweight(value=-1)
        bpy.ops.transform.edge_crease(value=-1)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_all(action='SELECT')
        if self.set_status:
            if self.hide_mesh :
                bpy.ops.mesh.hide()
        bpy.ops.object.editmode_toggle()
                                    
    
def draw(display, parameter_getter):
    auto_smooth_angle, segment_amount, bevelwidth, op_detail, op_tag, text = parameter_getter()    
        
    scale_factor = 0.9

    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)

    set_drawing_dpi(display.get_dpi() * scale_factor)
    dpi_factor = display.get_dpi_factor() * scale_factor
    line_height = 18 * dpi_factor

    transparency = display.transparency
    color_text1, color_text2, color_border, color_border2 = get_hops_preferences_colors_with_transparency(transparency)
    region_width = bpy.context.region.width

        # Box
    ########################################################

    location = display.location
    x, y = location.x - 60* dpi_factor, location.y - 118* dpi_factor

    draw_box(0, 43 *dpi_factor, region_width, -4 * dpi_factor, color = color_border2)
    draw_box(0, 0, region_width, -82 * dpi_factor, color = color_border)

    draw_logo_csharp(color_border2)


    # Name
    ########################################################


    draw_text(op_tag, x - 380 *dpi_factor , y -12*dpi_factor,
              align = "LEFT", size = 20 , color = color_text2)


    # First Coloumn
    ########################################################
    x = x - 160 * dpi_factor
    r = 120 * dpi_factor

    #do we use it ?
    '''draw_text("BEVELS WERE ADDED", x + line_length * dpi_factor, y - 42 * dpi_factor,
                          align = "RIGHT", size = 9, color = color_text2)'''

    draw_text("Segment Amount:", x, y,
              align = "LEFT", color = color_text2)

    draw_text(format(segment_amount), x + r , y,
              align = "LEFT", size = 12, color = color_text2)

    draw_text("Auto_Smooth Angle:", x, y - line_height,
              align = "LEFT", size = 12, color = color_text2)

    draw_text("{}°".format(round(degrees(auto_smooth_angle))), x + r, y - line_height,
              align = "LEFT", size = 12, color = color_text2)


    # Second Column
    ########################################################

    x = x + 300 * dpi_factor
    r = 40 * dpi_factor

    draw_text("Bevel Segments:", x, y,
              align = "RIGHT", size = 12, color = color_text2)

    draw_text("{}".format(segment_amount), x + r, y,
              align = "RIGHT", size = 12, color = color_text2)

    draw_text("Bevel Width:", x, y - line_height,
              align = "RIGHT", size = 12, color = color_text2)

    draw_text("{}".format('%.2f'%(bevelwidth)), x + r, y - line_height,
              align = "RIGHT", size = 12, color = color_text2)
              
    # Final Column
    ########################################################
    
    x = x + 300 * dpi_factor
    
    draw_text(op_detail, x + r, y,
              align = "RIGHT", size = 12, color = color_text2)
        
    glDisable(GL_BLEND)
    glDisable(GL_LINE_SMOOTH)