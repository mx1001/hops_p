import os
import bpy
import bmesh
from bgl import *
from bpy.props import *
from math import radians, degrees
from .. utils import update_bevel_modifier_if_necessary
from ... utils.context import ExecutionContext
from . soft_sharpen import soft_sharpen_object
from ... preferences import tool_overlays_enabled, get_hops_preferences_colors_with_transparency, Hops_display_time, Hops_fadeout_time
from ... utils.blender_ui import get_location_in_current_3d_view
from ... utils.objects import get_modifier_with_type, apply_modifiers
from ... overlay_drawer import show_custom_overlay, disable_active_overlays, show_text_overlay
from ... graphics.drawing2d import set_drawing_dpi, draw_horizontal_line, draw_boolean, draw_text, draw_box, draw_logo_csharp

mod_types = [
    ("BOOLEAN", "Boolean", ""),
    ("MIRROR", "Mirror", ""),
    ("BEVEL", "Bevel", ""),
    ("SOLIDIFY", "Solidify", ""),
    ("ARRAY", "Array", ""),]

class ComplexSharpenOperator(bpy.types.Operator):
    bl_idname = "hops.complex_sharpen"
    bl_label = "C-Sharp"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Sharpen the mesh while bevelling on sharp edges"
    
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
    reveal_mesh = True

    @classmethod
    def poll(cls, context):
        object = context.active_object
        if object is None: return False
        return object.type == "MESH" and object.mode == "OBJECT"

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column()
        object = bpy.context.active_object
        if object.hops.status != "CSTEP":
            col.label("Modifiers Applied By Csharp")
            col.prop(self, "modifier_types", expand=True)
            
            col.label("")
            col.label("General Parameters")
            col.prop(self, "sharpness")
            col.prop(self, "auto_smooth_angle")
            col.prop(self, "segment_amount")
            col.prop(self, "bevelwidth")
            
            col.label("")
            col.label("Sharpening Parameters")
            box.prop(self, "additive_mode")
            box.prop(self, "sub_d_sharpening")

    def invoke(self, context, event):
        self.execute(context)
        
        object = bpy.context.active_object
        if object.hops.status != "CSTEP":
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
        return self.sharpness, self.auto_smooth_angle, self.additive_mode, self.sub_d_sharpening, self.segment_amount, self.bevelwidth

    def execute(self, context):
        active = bpy.context.active_object
        
        object = bpy.context.active_object
        if object.hops.status == "CSTEP":
            self.sharpness = radians(40)
            self.additive_mode = True
            if tool_overlays_enabled():
                text = "Don't Csharpen Cstepped Meshes!"
                show_text_overlay(text = text, font_size = 16, stay_time = Hops_display_time(), fadeout_time = Hops_fadeout_time())
        
        if object.hops.status != "CSTEP":
            if object.hops.status == "CSHARP":
                soft_sharpen_object(
                context.active_object, 
                self.sharpness, 
                self.auto_smooth_angle, 
                self.additive_mode, 
                self.sub_d_sharpening, 
                self.reveal_mesh)
                              
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

def complex_sharpen_active_object(object, sharpness, auto_smooth_angle, additive_mode, sub_d_sharpening, modifier_types, segment_amount, bevelwidth, reveal_mesh):
    with ExecutionContext(mode = "OBJECT", active_object = object):
        apply_modifiers(object, modifier_types)
        if sub_d_sharpening == False:
            soft_sharpen_object(object, sharpness, auto_smooth_angle, additive_mode, sub_d_sharpening, reveal_mesh)    
        if object.hops.status == "SUBSHARP":
            sub_d_sharpening == True
            soft_sharpen_object(object, sharpness, auto_smooth_angle, additive_mode, sub_d_sharpening, reveal_mesh)    
        
        object = bpy.context.active_object
        if sub_d_sharpening == True:
            object.hops.status = "SUBSHARP"
        
        else:
            if object.hops.status != "CSTEP":
                object.hops.status = "CSHARP"

# Overlay
###################################################################

def draw(display, parameter_getter):
    sharpness, auto_smooth_angle, additive_mode, sub_d_sharpening, segment_amount, bevelwidth = parameter_getter()
    scale_factor = 0.9

    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)

    set_drawing_dpi(display.get_dpi() * scale_factor)
    dpi_factor = display.get_dpi_factor() * scale_factor
    line_height = 18 * dpi_factor
    line_length = 270

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


    draw_text("CSHARPEN", x - 380 *dpi_factor , y -12*dpi_factor,
              align = "LEFT", size = 20 , color = color_text2)

    # Fitst Coloumn
    ########################################################
    x = x - 160 * dpi_factor
    r = 34 * dpi_factor

    #do we use it ?
    '''draw_text("BEVELS WERE ADDED", x + line_length * dpi_factor, y - 42 * dpi_factor,
                          align = "RIGHT", size = 9, color = color_text2)'''


    draw_text("ADDITIVE MODE", x + r, y,
              align = "LEFT", color = color_text2)

    draw_boolean(additive_mode, x, y , size = 11, alpha = transparency)

    draw_text("SUB D SHARPENING", x + r, y - line_height,
              align = "LEFT", color = color_text2)
        
    draw_boolean(sub_d_sharpening, x, y - line_height, size = 11, alpha = transparency)


    # Second Column
    ########################################################

    x = x + 300 * dpi_factor

    draw_text("SHARPNESS:", x, y,
              align = "RIGHT", size = 12, color = color_text2)

    draw_text("{}°".format(round(degrees(sharpness))), x + 30 * dpi_factor, y,
              align = "RIGHT", size = 12, color = color_text2)

    draw_text("SMOOTHING ANGLE:", x, y - line_height,
              align = "RIGHT", size = 12, color = color_text2)

    draw_text("{}°".format(round(degrees(auto_smooth_angle))), x + 30 * dpi_factor, y - line_height,
              align = "RIGHT", size = 12, color = color_text2)

    # Third Coloumn
    ########################################################
    x = x + 160 * dpi_factor

    draw_text("BEVEL SEGMENTS:", x , y,
             align = "RIGHT", size = 12, color = color_text2)

    draw_text("{}".format(segment_amount), x + r, y,
             align = "RIGHT", size = 12, color = color_text2)

    draw_text("BEVEL WIDTH:", x , y - line_height,
             align = "RIGHT", size = 12, color = color_text2)

    draw_text("{}".format('%.2f'%(bevelwidth)), x + r, y - line_height,
             align = "RIGHT", size = 12, color = color_text2)
        

    glDisable(GL_BLEND)
    glDisable(GL_LINE_SMOOTH)  
      
