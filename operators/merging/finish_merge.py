import bpy
from bgl import *
from bpy.props import *
from math import radians, degrees
from ... utils.context import ExecutionContext
from ... preferences import tool_overlays_enabled, Hops_display_time, Hops_fadeout_time
from ... utils.blender_ui import get_location_in_current_3d_view
from .. utils import clear_ssharps, mark_ssharps, set_smoothing
from ... overlay_drawer import show_custom_overlay, disable_active_overlays
from ... graphics.drawing2d import set_drawing_dpi, draw_horizontal_line, draw_boolean, draw_text

class finish_setup(bpy.types.Operator):
    bl_idname = "hops.finish_setup"
    bl_label = "Finish Merge Setup"
    bl_description = "Finish Merging Meshes In Bool State"
    bl_options = {"REGISTER", 'UNDO'}

    text = "Boolean Applied"
    op_tag = StringProperty()
    op_detail = StringProperty()
    sharpen_mesh = BoolProperty(name = "Sharpen Mesh", default = True)

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "sharpen_mesh")

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
        return self.op_detail, self.op_tag, self.text, self.sharpen_mesh

    def execute(self, context):
        object = context.active_object
        if object.hops.status == "CSTEP":
            self.op_tag = "(C)Step"
            self.op_detail = "Boolean applied and Bevels recalculated - Mesh (C)Stepped"
        elif object.hops.status == "CSHARP":
            self.op_tag = "(C)Sharpen"
            self.op_detail = "Boolean applied and Bevels recalculated - Mesh (C)Sharpened"
        else:
            self.op_tag = "No Operation"
            self.op_detail = "The object has to be in cstep or csharpen mode"
        return {"FINISHED"}

def draw(display, parameter_getter):
    op_detail, op_tag, text, sharpen_mesh = parameter_getter()

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

    draw_text("Merge Complete", x - 120, y,
              align = "LEFT", size = 12, color = color)

    draw_text(text, x - 120, y - line_height,
              align = "LEFT", size = 12, color = color)

    # Middle
    ########################################################

    x, y = x - 120 * dpi_factor, y - 27 * dpi_factor
    line_length = 270

    line_width = 2 * dpi_factor
    draw_horizontal_line(x,  y, line_length * dpi_factor, color, width = line_width)

    draw_text(op_tag, x, y - 22 * dpi_factor,
              align = "LEFT", size = 16, color = color)

    draw_horizontal_line(x, y - 31 * dpi_factor, line_length * dpi_factor, color, width = line_width)

    draw_text(op_detail, x + line_length * dpi_factor, y - 42 * dpi_factor,
              align = "RIGHT", size = 9, color = color)


    # Last Part
    ########################################################

    x, y = x + 3 * dpi_factor, y - 50 * dpi_factor

    offset = 30 * dpi_factor

    draw_text("MESH SHARPENING", x + offset, y - line_height,
              align = "LEFT", color = color)

    draw_boolean(sharpen_mesh, x, y - line_height, size = 11, alpha = transparency)

    glDisable(GL_BLEND)
    glDisable(GL_LINE_SMOOTH)
