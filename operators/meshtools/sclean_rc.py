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
from ... utils.blender_ui import get_location_in_current_3d_view
from ... overlay_drawer import show_custom_overlay, disable_active_overlays, show_text_overlay
from ... graphics.drawing2d import set_drawing_dpi, draw_horizontal_line, draw_boolean, draw_text, draw_box, draw_logo_csharp
from ... preferences import tool_overlays_enabled, get_hops_preferences_colors_with_transparency, Hops_display_time, Hops_fadeout_time

class cleanReOrigin(bpy.types.Operator):
    "RemovesDoubles/RecenterOrgin/ResetGeometry"
    bl_idname = "clean.reorigin"
    bl_label = "CleanRecenter"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"
    
    def invoke(self, context, event):
        self.execute(context)

        if tool_overlays_enabled():
            disable_active_overlays()
            self.wake_up_overlay = show_custom_overlay(draw,
                #parameter_getter = self.parameter_getter,
                location = get_location_in_current_3d_view("CENTER", "BOTTOM", offset = (0, 130)),
                location_type = "CUSTOM",
                stay_time = Hops_display_time(),
                fadeout_time = Hops_fadeout_time())

        return {"FINISHED"}
    
    def execute(self, context):
        s_clean_rc()
        
        try: self.wake_up_overlay()
        except: pass
            
        return {'FINISHED'}

def s_clean_rc():
    object = bpy.context.active_object    
    #maybe convert to mesh then recenter
    bpy.ops.object.modifier_remove(modifier="Bevel")
    bpy.ops.object.convert(target='MESH')    
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_all(action='TOGGLE')
    bpy.ops.mesh.remove_doubles()
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
    bpy.ops.object.location_clear()
    object.hops.status = "UNDEFINED"


    
### DRAWing system ###



def draw(display): #, parameter_getter):
    #dissolve_angle, remove_threshold, unhide_behavior, op_detail, op_tag = parameter_getter()
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


    draw_text("SCLEAN RECENTER", x - 380 *dpi_factor , y -12*dpi_factor,
              align = "LEFT", size = 20 , color = color_text2)
              

    # Fitst Coloumn
    ########################################################

    x = x - 160 * dpi_factor
    r = 34 * dpi_factor
    
    draw_text("Origin Reset", x + r, y,
              align = "LEFT",size = 11, color = color_text2)

    #draw_text("{}°".format(round(degrees(dissolve_angle))), x, y ,size = 11, color = color_text2)

    draw_text("Array And Simple Deform Applied", x + r + 120, y - line_height,
              align = "LEFT",size = 11, color = color_text2)

    #draw_text("{:.3f}".format(remove_threshold), x + + r + 260, y - line_height, size = 12, color = color_text2)

    draw_text("SStatus Reset", x + r, y - line_height,
              align = "LEFT",size = 11, color = color_text2)

    #draw_boolean(unhide_behavior, x, y - line_height, size = 12, alpha = transparency)


    # Last Part
    ########################################################

    x = x + 320 * dpi_factor
    """    
    draw_text(op_tag, x + r, y  * dpi_factor,
              align = "LEFT", size = 11, color = color_text2)


    draw_text(op_detail, x + r, y - line_height,
              align = "LEFT", size = 11, color = color_text2)
    """
    
    glDisable(GL_BLEND)
    glDisable(GL_LINE_SMOOTH)
