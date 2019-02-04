import bpy
from bgl import *
from bpy.props import *
from math import radians, degrees
from ... utils.context import ExecutionContext
from ... preferences import tool_overlays_enabled, get_hops_preferences_colors_with_transparency, Hops_display_time, Hops_fadeout_time
from ... utils.blender_ui import get_location_in_current_3d_view
from .. utils import clear_ssharps, mark_ssharps, set_smoothing
from ... overlay_drawer import show_custom_overlay, disable_active_overlays, show_text_overlay
from ... graphics.drawing2d import set_drawing_dpi, draw_horizontal_line, draw_boolean, draw_text, draw_box, draw_logo_csharp

class SoftSharpenOperator(bpy.types.Operator):
    bl_idname = "hops.soft_sharpen"
    bl_label = "Soft Sharpen"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Sharpen the mesh without bevelling on sharp edges"

    sharpness = FloatProperty(name = "Sharpness", default = radians(30),
                              min = radians(1), max = radians(180), subtype = "ANGLE")

    auto_smooth_angle = FloatProperty(name = "Auto Smooth Angle", default = radians(60),
                              min = 0.0, max = radians(180), subtype = "ANGLE")

    additive_mode = BoolProperty(name = "Additive Mode",
                              description = "Don't clear existing edge properties",
                              default = True)

    sub_d_sharpening = BoolProperty(name = "Sub-D Sharpening",
                                default = False)

    reveal_mesh = True
    
    message = "NO!"

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def draw(self, context):
        layout = self.layout
        
        object = bpy.context.active_object
        if object.hops.status != "CSTEP":
            layout.prop(self, "sharpness")
            layout.prop(self, "auto_smooth_angle")
            layout.prop(self, "additive_mode")
            layout.prop(self, "sub_d_sharpening")
        else:
            layout.label("Do Not Ssharp Cstepped Meshes")
        
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
        
        else:
            if tool_overlays_enabled():
                message = self.message
                show_text_overlay(text = message, 
                                font_size = 60, 
                                color = (1, 0, 0),
                                stay_time = Hops_display_time(), 
                                fadeout_time = Hops_fadeout_time())     
        return {"FINISHED"}

    def parameter_getter(self):
        return self.sharpness, self.auto_smooth_angle, self.additive_mode, self.sub_d_sharpening

    def execute(self, context):
        
        #Vitaliy!
        bpy.context.object.data.show_edge_crease = True
        
        object = bpy.context.active_object
        if object.hops.status == "CSTEP":
            self.sharpness = radians(40)
            self.additive_mode = True
            self.reveal_mesh = False
        
        if object.hops.status != "CSTEP":    
            soft_sharpen_object(
                context.active_object,
                self.sharpness,
                self.auto_smooth_angle,
                self.additive_mode,
                self.sub_d_sharpening,
                self.reveal_mesh)

            try: self.wake_up_overlay()
            except: pass

        return {"FINISHED"}

def soft_sharpen_object(object, sharpness, auto_smooth_angle, additive_mode, sub_d_sharpening, reveal_mesh):
    with ExecutionContext(mode = "EDIT", active_object = object):
        unhide_mesh = reveal_mesh
        
        if unhide_mesh == True:
            bpy.ops.mesh.reveal()

        if not additive_mode: clear_ssharps(object)
        mark_ssharps(object, sharpness, sub_d_sharpening)
        set_smoothing(object, auto_smooth_angle, sub_d_sharpening)

# Overlay
###################################################################

def draw(display, parameter_getter):
    sharpness, auto_smooth_angle, additive_mode, sub_d_sharpening = parameter_getter()
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


    draw_text("SSHARPEN", x - 380 *dpi_factor , y -12*dpi_factor,
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

  



    glDisable(GL_BLEND)
    glDisable(GL_LINE_SMOOTH)
