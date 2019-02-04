import bpy
import os
from bgl import *
from bpy.props import *
from math import radians, degrees
from ... utils.context import ExecutionContext
from ... utils.blender_ui import get_location_in_current_3d_view
from .. utils import clear_ssharps, mark_ssharps, set_smoothing
from ... overlay_drawer import show_custom_overlay, disable_active_overlays, show_text_overlay
from ... graphics.drawing2d import set_drawing_dpi, draw_horizontal_line, draw_boolean, draw_text, draw_box, draw_logo_csharp
from ... preferences import tool_overlays_enabled, get_hops_preferences_colors_with_transparency, Hops_display_time, Hops_fadeout_time

class symmetrizeMesh(bpy.types.Operator):
    bl_idname = "view3d.symmetrize"
    bl_label = "Symmetrize Mesh"
    bl_description = "Mesh Symmetrize"
    bl_options = {"REGISTER","UNDO"}

    type = "Default"

    is_cstep = BoolProperty(name = "Is Cstep Mesh",
                              description = "Hide Mesh If Cstep",
                              default = True)

    symmetryTypeItems = [
        ("NEGATIVE_X", "-X", ""),
        ("POSITIVE_X",  "X", ""),
        ("NEGATIVE_Y", "-Y", ""),
        ("POSITIVE_Y",  "Y", ""),
        ("NEGATIVE_Z", "-Z", ""),
        ("POSITIVE_Z",  "Z", ""),
        ]

    symtype = EnumProperty( name = "Symmetry Axis",
                            items = symmetryTypeItems,
                            description = "Axis For Symmetrize",
                            default = "NEGATIVE_X")

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def draw(self, context):
        layout = self.layout

        layout.prop(self, "symtype")

    def invoke(self, context, event):
        self.execute(context)

        object = bpy.context.active_object
        self.type = object.hops.status

        if tool_overlays_enabled():
            disable_active_overlays()
            self.wake_up_overlay = show_custom_overlay(draw,
                parameter_getter = self.parameter_getter,
                location = get_location_in_current_3d_view("CENTER", "BOTTOM", offset = (0, 130)),
                location_type = "CUSTOM",
                stay_time = Hops_display_time(),
                fadeout_time = Hops_fadeout_time())

            if self.type == "CSTEP":
                message = "Mesh Hidden"
            else:
                message = "Symmetrize Complete"
            show_text_overlay(text = message, font_size = 10, color = (1, 1, 1),
                          stay_time = Hops_display_time(), fadeout_time = Hops_fadeout_time())
        return {"FINISHED"}

    def parameter_getter(self):
        return self.type, self.symtype, self.is_cstep

    def execute(self, context):
        object = bpy.context.active_object
        old_mode = object.mode

        setup_mesh(object)
        sym_mesh(object, self.symtype)

        self.type = object.hops.status
        self.is_cstep = self.type == "CSTEP"

        if self.is_cstep:
            cstep_reset(object)
            bpy.ops.object.mode_set(mode = "OBJECT")
        else:
            bpy.ops.object.mode_set(mode = old_mode)

        try: self.wake_up_overlay()
        except: pass

        return {"FINISHED"}

def setup_mesh(object):
    object = bpy.context.active_object
    if bpy.context.active_object.mode == 'OBJECT':
        bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_all(action='TOGGLE')

def sym_mesh(object,symtype):
    bpy.ops.mesh.symmetrize(direction = symtype)
    bpy.ops.object.editmode_toggle()

def cstep_reset(object):
    object = bpy.context.active_object
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_all(action='TOGGLE')
    bpy.ops.mesh.hide(unselected=False)
    bpy.ops.object.editmode_toggle()


# Overlay
###################################################################

def draw(display, parameter_getter):
    type, symtype, is_cstep = parameter_getter()
    scale_factor = 0.9

    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)

    set_drawing_dpi(display.get_dpi() * scale_factor)
    dpi_factor = display.get_dpi_factor() * scale_factor
    line_height = 18 * dpi_factor

    transparency = display.transparency
    color_text1, color_text2, color_border, color_border2 = get_hops_preferences_colors_with_transparency(transparency)
    region_width = bpy.context.region.width
    
    if "NEGATIVE" in symtype:
        color2 = (1, 0, 0, 0.5 * transparency)
    else:
        color2 = (0, 1, 0, 0.5 * transparency)

    # Box
    ########################################################

    location = display.location
    x, y = location.x - 60* dpi_factor, location.y - 118* dpi_factor

    draw_box(0, 43 *dpi_factor, region_width, -4 * dpi_factor, color = color_border2)
    draw_box(0, 0, region_width, -82 * dpi_factor, color = color_border)

    draw_logo_csharp(color_border2)
    
    # Name
    ########################################################


    draw_text("SYMMETRIZE", x - 380 *dpi_factor , y -12*dpi_factor,
              align = "LEFT", size = 20 , color = color_text2)


    # First Part
    ########################################################

    x = x - 160 * dpi_factor
    r = 110 * dpi_factor

    draw_text("MESH STATUS",x , y,
              align = "LEFT", size = 12, color = color_text2)

    draw_text(type,  x + r, y ,
              align = "LEFT", size = 12, color = color_text2)

    draw_text("SYMMETRY AXIS:", x, y - line_height,
              align = "LEFT", size = 12, color = color_text2)

    draw_text(symtype, x + r, y - line_height,
              align = "LEFT", size = 12, color = color_text2)


    # Last Part
    # Second Column
    ########################################################

    x = x + 320 * dpi_factor

    if type == "CSTEP":
        draw_text("CSTEP Edit Mode Hiding", x, y,
                  align = "RIGHT", color = color_text2)

        draw_boolean(is_cstep, x, y - line_height, size = 11, alpha = transparency)
    else:
        draw_text(type,  x, y,
                  align = "RIGHT", size = 16, color = color_text2)



    glDisable(GL_BLEND)
    glDisable(GL_LINE_SMOOTH)
