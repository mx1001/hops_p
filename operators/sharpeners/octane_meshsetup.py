import os
import bpy
import bmesh
from bgl import *
from bpy.props import *
from math import radians, degrees
from .. utils import update_bevel_modifier_if_necessary
from ... utils.context import ExecutionContext
from . soft_sharpen import soft_sharpen_object
from ... preferences import tool_overlays_enabled, Hops_display_time, Hops_fadeout_time
from ... utils.blender_ui import get_location_in_current_3d_view
from ... utils.objects import get_modifier_with_type, apply_modifiers
from ... overlay_drawer import show_custom_overlay, disable_active_overlays
from ... graphics.drawing2d import set_drawing_dpi, draw_horizontal_line, draw_boolean, draw_text

#Adds EdgeSplit To Meshes Only For Octane

class add_edge_split(bpy.types.Operator):
    bl_idname = "add.edge_split"
    bl_label = "Add Edge Split"
    bl_description = "Add Edge Split Modifier To All Selected Meshes"
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll(cls, context):
        return True
    
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
                    
    def execute(self, context):
        for obj in bpy.context.selected_objects:
            new_mod = obj.modifiers.new(type='EDGE_SPLIT', name='EdgeSplit')
            if object.hops.status == "CSTEP":    
                object.hops.status = "CSTEP (EdgeSplit)"
            if object.hops.status == "CSHARP":    
                object.hops.status = "CSHARP (EdgeSplit)"
            else:
                object.hops.status = "UNDEFINED (EdgeSplit)"
            
            if tool_overlays_enabled():
                text = "EdgeSplit Added"
                show_text_overlay(text = text, font_size = 16, stay_time = 1, fadeout_time = 1)            
                
        return {"FINISHED"}

        
# Overlay
###################################################################

def draw(display):
    scale_factor = 0.9

    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)

    set_drawing_dpi(display.get_dpi() * scale_factor)
    dpi_factor = display.get_dpi_factor() * scale_factor
    line_height = 18 * dpi_factor

    transparency = display.transparency
    color = (1, 1, 1, 0.5 * transparency)


    # First Part
    ########################################################

    location = display.location
    x, y = location.x, location.y

    draw_text("EDGE SPLITTING", x, y,
              align = "RIGHT", size = 12, color = color)

    draw_text("ADDED SUCCESSFULLY", x, y - line_height,
              align = "RIGHT", size = 12, color = color)

    # Middle
    ########################################################

    x, y = x - 120 * dpi_factor, y - 27 * dpi_factor
    line_length = 270

    line_width = 2 * dpi_factor
    draw_horizontal_line(x,  y, line_length * dpi_factor + 65, color, width = line_width)

    draw_text("OCTANE - EDGE SPLITTING", x, y - 22 * dpi_factor,
              align = "LEFT", size = 16, color = color)

    draw_horizontal_line(x, y - 31 * dpi_factor, line_length * dpi_factor + 65, color, width = line_width)

    draw_text("EDGE SPLIT ADDED", x + line_length * dpi_factor, y - 42 * dpi_factor,
              align = "RIGHT", size = 9, color = color)


    # Last Part
    ########################################################

    x, y = x + 3 * dpi_factor, y - 50 * dpi_factor

    offset = 30 * dpi_factor

    draw_text("Ready For Export", x + offset, y,
              align = "LEFT", color = color)

    draw_text("Do Not Boolean With Disabling Edge Split", x + offset, y - line_height,
              align = "LEFT", color = color)

    glDisable(GL_BLEND)
    glDisable(GL_LINE_SMOOTH)
