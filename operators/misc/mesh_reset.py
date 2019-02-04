import os
import bpy
from bgl import *
from bpy.props import *
from math import radians, degrees
from ... utils.context import ExecutionContext
from ... preferences import tool_overlays_enabled
from ... utils.blender_ui import get_location_in_current_3d_view
from ... overlay_drawer import show_custom_overlay, disable_active_overlays
from ... graphics.drawing2d import set_drawing_dpi, draw_horizontal_line, draw_boolean, draw_text, draw_box, draw_logo_csharp
from ... preferences import tool_overlays_enabled, get_hops_preferences_colors_with_transparency, Hops_display_time, Hops_fadeout_time
from ... overlay_drawer import show_text_overlay

class reset_status(bpy.types.Operator):
    bl_idname = "hops.reset_status"
    bl_label = "Reset Status"
    bl_description = "Resets the Mesh Status For Workflow Realignment"
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        object = bpy.context.active_object
        object.hops.status = "UNDEFINED"
        
        try: self.wake_up_overlay()
        except: pass
        
        return {"FINISHED"}
    
    def invoke(self, context, event):
        self.execute(context)
        
        object = bpy.context.active_object
        if tool_overlays_enabled():
            disable_active_overlays()
            self.wake_up_overlay = show_custom_overlay(draw,
                #parameter_getter = self.parameter_getter,
                location = get_location_in_current_3d_view("CENTER", "BOTTOM", offset = (0, 130)),
                location_type = "CUSTOM",
                stay_time = Hops_display_time(),
                fadeout_time = Hops_fadeout_time())

        return {"FINISHED"}
        
# Overlay
###################################################################

def draw(display,):
#def draw(display, parameter_getter):
    #sharpness, auto_smooth_angle, additive_mode, sub_d_sharpening, segment_amount, bevelwidth = parameter_getter()
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


    draw_text("MESH RESET", x - 380 *dpi_factor , y -12*dpi_factor,
              align = "LEFT", size = 20 , color = color_text2)
              
    # Fitst Coloumn
    ########################################################
    x = x - 160 * dpi_factor
    r = 34 * dpi_factor

    draw_text("SSTATUS REMOVED",x + r, y,
              align = "LEFT", size = 11, color = color_text2)

    draw_text("SSTATUS SET TO UNDEFINED", x + r, y - line_height,
              align = "LEFT", size = 11, color = color_text2)
    
    glDisable(GL_BLEND)
    glDisable(GL_LINE_SMOOTH)