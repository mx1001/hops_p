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


#_____________________________________________________________clear ssharps (OBJECT MODE)________________________
class un_sharpOperator(bpy.types.Operator):
    '''Clear Off Sharps And Bevels In Object Mode'''
    bl_idname = "clean.sharps"
    bl_label = "Remove Ssharps"
    bl_options = {'REGISTER', 'UNDO'}

    removeMods = BoolProperty(default = True)
    clearsharps = BoolProperty(default = True)
    clearbevel = BoolProperty(default = True)
    clearcrease = BoolProperty(default = True)

    text = "SSharps Removed"
    op_tag = "Clean Ssharp"
    op_detail = "Selected Ssharps Removed"

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        # DRAW YOUR PROPERTIES IN A BOX
        box.prop( self, 'removeMods', text = "RemoveModifiers?")
        box.prop( self, 'clearsharps', text = "Clear Sharps")
        box.prop( self, 'clearbevel', text = "Clear Bevels")
        box.prop( self, 'clearcrease', text = "Clear Crease")

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
        return self.clearsharps, self.clearbevel, self.clearcrease, self.op_tag, self.op_detail

    def execute(self, context):
        clear_ssharps_active_object(
            self.removeMods,
            self.clearsharps,
            self.clearbevel,
            self.clearcrease,
            self.text)

        try: self.wake_up_overlay()
        except: pass

        return {'FINISHED'}



#_____________________________________________________________clear ssharps________________________
def clear_ssharps_active_object(removeMods, clearsharps, clearbevel, clearcrease, text):
    remove_mods_shadeflat(removeMods)
    clear_sharps(clearsharps,
                clearbevel,
                clearcrease)
    #show_message(text)
    object = bpy.context.active_object
    object.hops.status = "UNDEFINED"
    bpy.ops.object.shade_flat()

def clear_sharps(clearsharps, clearbevel, clearcrease):
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')

    if clearsharps == True:
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_all(action='TOGGLE')

        bpy.ops.mesh.mark_sharp(clear=True)
    if clearbevel == True:
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_all(action='TOGGLE')
        bpy.ops.transform.edge_bevelweight(value=-1)
    if clearcrease == True:
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_all(action='TOGGLE')

        bpy.ops.transform.edge_crease(value=-1)
    bpy.ops.object.editmode_toggle()

def remove_mods_shadeflat(removeMods):
    if removeMods:
        bpy.ops.object.modifier_remove(modifier="Bevel")
        bpy.ops.object.modifier_remove(modifier="Solidify")

    else:
        bpy.context.object.modifiers["Bevel"].limit_method = 'ANGLE'
        bpy.context.object.modifiers["Bevel"].angle_limit = 0.7

def show_message(text):
    pass



def draw(display, parameter_getter):
    clearsharps, clearbevel, clearcrease, op_detail, op_tag = parameter_getter()
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


    draw_text("SSHARPS CLEARED", x - 380 *dpi_factor , y -12*dpi_factor,
              align = "LEFT", size = 20 , color = color_text2)
              

    # Fitst Coloumn
    ########################################################

    x = x - 160 * dpi_factor
    r = 34 * dpi_factor
    
    draw_text("Clear Sharps", x + r, y,
              align = "LEFT",size = 11, color = color_text2)

    draw_boolean(clearsharps, x, y ,size = 11, alpha = transparency)

    draw_text("Clear Bevelweight", x + r + 120, y - line_height,
              align = "LEFT",size = 11, color = color_text2)

    draw_boolean(clearbevel, x + 120, y - line_height, size = 12, alpha = transparency)

    draw_text("Clear Crease", x + r, y - line_height,
              align = "LEFT",size = 11, color = color_text2)

    draw_boolean(clearcrease, x, y - line_height, size = 12, alpha = transparency)


    # Last Part
    ########################################################

    x = x + 320 * dpi_factor
        
    draw_text(op_tag, x, y  * dpi_factor,
              align = "LEFT", size = 11, color = color_text2)


    draw_text(op_detail, x + r, y - line_height,
              align = "LEFT", size = 11, color = color_text2)

    glDisable(GL_BLEND)
    glDisable(GL_LINE_SMOOTH)
