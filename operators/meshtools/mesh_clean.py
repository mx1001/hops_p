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


#_____________________________________________________________clean mesh (OBJECT MODE)________________________
class clean_MeshOperator(bpy.types.Operator):
    '''Remove Doubles / Limited Disolve'''
    bl_idname = "view3d.clean_mesh"
    bl_label = "Limited Dissolve"
    bl_options = {'REGISTER', 'UNDO'}

    dissolve_angle = FloatProperty(name = "Limited Dissolve Angle", default = radians(0.5),
                              min = radians(0), max = radians(30), subtype = "ANGLE")                              
    remove_threshold = FloatProperty(name="Remove Threshold Amount",
                               description="Remove Double Amount",
                               default=0.001,
                               min = 0.0001,
                               max =1.00)
    unhide_behavior = BoolProperty(default = True)
    
    delete_interior = BoolProperty(default = False)

    text = "Limited Dissolve Removed"
    op_tag = "Limited Dissolve / Remove Doubles"
    op_detail = "Angled Doubles Dissolved"

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        # DRAW YOUR PROPERTIES IN A BOX
        box.prop( self, 'dissolve_angle', text = "Limited Disolve Angle")
        box.prop( self, 'remove_threshold', text = "Remove Threshold")
        box.prop( self, 'unhide_behavior', text = "Unhide Mesh")
        box.prop( self, 'delete_interior', text = "Delete Interior Faces")

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
        return self.dissolve_angle, self.remove_threshold, self.unhide_behavior, self.op_tag, self.op_detail

    def execute(self, context):
        clean_mesh_active_object(
            self.dissolve_angle,
            self.remove_threshold,
            self.unhide_behavior,
            self.delete_interior,
            self.text)

        try: self.wake_up_overlay()
        except: pass

        return {'FINISHED'}
    
#_____________________________________________________________clean mesh________________________
def clean_mesh_active_object(dissolve_angle, remove_threshold, unhide_behavior, delete_interior, text):
    clean_mesh(dissolve_angle,
                remove_threshold,
                unhide_behavior,
                delete_interior)
    #show_message(text)
    object = bpy.context.active_object

def clean_mesh(dissolve_angle, remove_threshold, unhide_behavior, delete_interior):
    #EditMode Unhide / Select All
    object = bpy.context.active_object
    bpy.ops.object.mode_set(mode='EDIT')
    if unhide_behavior == True:
        bpy.ops.mesh.reveal()
    
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
        
    #Select All
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_all(action='TOGGLE')

    #Remove Doubles / Limited Dissolve
    bpy.ops.mesh.dissolve_limited(angle_limit=dissolve_angle)
    bpy.ops.mesh.remove_doubles(threshold=remove_threshold)
    
    if delete_interior == True:
        delete_interior_faces()
            
    #Cstep Return
    if object.hops.status == "CSTEP":
        bpy.ops.mesh.hide(unselected=False)
    
    #Back To Object Mode
    bpy.ops.object.editmode_toggle()
    
def delete_interior_faces():
    #bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_interior_faces()
    bpy.ops.mesh.delete(type='FACE')
    

def show_message(text):
    pass



def draw(display, parameter_getter):
    dissolve_angle, remove_threshold, unhide_behavior, op_detail, op_tag = parameter_getter()
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


    draw_text("MESH CLEANED", x - 380 *dpi_factor , y -12*dpi_factor,
              align = "LEFT", size = 20 , color = color_text2)
              

    # Fitst Coloumn
    ########################################################

    x = x - 160 * dpi_factor
    r = 34 * dpi_factor
    
    draw_text("Dissolve Angle", x + r, y,
              align = "LEFT",size = 11, color = color_text2)

    draw_text("{}°".format(round(degrees(dissolve_angle))), x, y ,size = 11, color = color_text2)

    draw_text("Remove Double Threshold", x + r + 120, y - line_height,
              align = "LEFT",size = 11, color = color_text2)

    draw_text("{:.3f}".format(remove_threshold), x + + r + 260, y - line_height, size = 12, color = color_text2)

    draw_text("Unhide Mesh", x + r, y - line_height,
              align = "LEFT",size = 11, color = color_text2)

    draw_boolean(unhide_behavior, x, y - line_height, size = 12, alpha = transparency)


    # Last Part
    ########################################################

    x = x + 320 * dpi_factor
        
    draw_text(op_tag, x + r, y  * dpi_factor,
              align = "LEFT", size = 11, color = color_text2)


    draw_text(op_detail, x + r, y - line_height,
              align = "LEFT", size = 11, color = color_text2)

    glDisable(GL_BLEND)
    glDisable(GL_LINE_SMOOTH)