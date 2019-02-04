import bpy
import bmesh
from bgl import *
from bpy.props import *
from math import radians, degrees
from . uv_draw import hops_draw_uv
from ... utils.objects import obj_quads_to_tris
from ... utils.bmesh import selectSmoothEdges
from ... utils.context import ExecutionContext
from ... preferences import tool_overlays_enabled, Hops_display_time, Hops_fadeout_time
from ... overlay_drawer import show_text_overlay
from ... utils.blender_ui import get_location_in_current_3d_view
from .. utils import clear_ssharps, mark_ssharps, set_smoothing
from ... overlay_drawer import show_custom_overlay, disable_active_overlays
from ... graphics.drawing2d import set_drawing_dpi, draw_horizontal_line, draw_boolean, draw_text
from ... overlay_drawer import show_text_overlay

class XUnwrap_F(bpy.types.Operator):
    bl_idname = "hops.xunwrap"
    bl_label = "XUnwrap"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "This is a cunwrap with OSD POC"

    angle_limit = FloatProperty(name = "Angle limit", 
                              default = 30,
                              min = 0.0, 
                              max = 90)

    rmargin = FloatProperty(name = "Margin", 
                              default = 0.02,
                              min = 0.0, 
                              max = 1)
    user_area_weight = FloatProperty(name = "User area weight", 
                              default = 0.03,
                              min = 0.0, 
                              max = 1)

    rmethod = BoolProperty(default = True)
    bweight_as_seams = BoolProperty(default = True)                                           

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.prop(self, "angle_limit")
        box.prop( self, 'bweight_as_seams', text = "convert bevel weight to seams")
        box.prop(self, "rmargin")
        box.prop(self, "user_area_weight")
        box.prop( self, 'rmethod', text = "use smart method")
        
    def invoke(self, context, event):
        self.execute(context)    
        hops_draw_uv()

        if tool_overlays_enabled():
            disable_active_overlays()
            hops_draw_uv()
            self.wake_up_overlay = show_custom_overlay(draw,
                parameter_getter = self.parameter_getter,
                location = get_location_in_current_3d_view("CENTER", "BOTTOM", offset = (0, 280)),
                location_type = "CUSTOM",
                stay_time = Hops_display_time(),
                fadeout_time = Hops_fadeout_time())
         
        return {"FINISHED"}

    def parameter_getter(self):
        return self.rmargin

    def execute(self, context):
        if self.bweight_as_seams:
            for obj in bpy.context.selected_objects:      
                bpy.context.scene.objects.active = obj
                me = obj.data
                me.show_edge_crease = True

                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.mesh.select_all(action = 'DESELECT')
                bpy.ops.mesh.select_mode(type="EDGE")
                selectSmoothEdges(self, me)
                bpy.ops.mesh.mark_seam(clear=False)
                bpy.ops.mesh.select_all(action = 'SELECT')
                bpy.ops.object.mode_set(mode = 'OBJECT')

        if self.rmethod:
            bpy.ops.uv.smart_project(angle_limit=self.angle_limit, island_margin=self.rmargin, user_area_weight=self.user_area_weight)

        else:
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=self.rmargin)
            bpy.ops.object.mode_set(mode = 'OBJECT')
        
        try: self.wake_up_overlay()
        except: pass

        return {"FINISHED"}  


# Overlay
###################################################################

def draw(display, parameter_getter):
    rmargin = parameter_getter()
    object = bpy.context.active_object
    
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
    
#    draw_text("Status:", x, y,
#              align = "RIGHT", size = 12, color = color)
#    
#    draw_text(object.hops.status, x + 30 * dpi_factor, y,
#              align = "RIGHT", size = 12, color = color)

    draw_text("Margin:", x, y - line_height,
              align = "RIGHT", size = 12, color = color)

    draw_text("{}".format('%.2f'%(rmargin)), x + 30 * dpi_factor, y - line_height,
              align = "RIGHT", size = 12, color = color)


    # Middle
    ########################################################

    x, y = x - 120 * dpi_factor, y - 27 * dpi_factor
    line_length = 270

    line_width = 2 * dpi_factor
    draw_horizontal_line(x,  y, line_length * dpi_factor, color, width = line_width)

    draw_text("C/UNWRAP", x, y - 22 * dpi_factor,
              align = "LEFT", size = 16, color = color)

    draw_horizontal_line(x, y - 31 * dpi_factor, line_length * dpi_factor, color, width = line_width)

    draw_text("Mesh UVed", x + line_length * dpi_factor, y - 42 * dpi_factor,
              align = "RIGHT", size = 9, color = color)


    # Last Part
    ########################################################

    x, y = x + 3 * dpi_factor, y - 50 * dpi_factor

    offset = 30 * dpi_factor

    """draw_text("ADDITIVE MODE", x + offset, y,
              align = "LEFT", color = color)

    draw_boolean(additive_mode, x, y, size = 11, alpha = transparency)

    draw_text("SUB D SHARPENING", x + offset, y - line_height,
              align = "LEFT", color = color)

    draw_boolean(sub_d_sharpening, x, y - line_height, size = 11, alpha = transparency)"""

    glDisable(GL_BLEND)
    glDisable(GL_LINE_SMOOTH)
