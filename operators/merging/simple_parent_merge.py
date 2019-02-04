import bpy
from bgl import *
from bpy.props import *
from math import radians, degrees
from ... preferences import tool_overlays_enabled, Hops_display_time, Hops_fadeout_time
from ... utils.context import ExecutionContext
from ... overlay_drawer import show_custom_overlay, disable_active_overlays
from ... utils.blender_ui import get_location_in_current_3d_view
from ... overlay_drawer import show_custom_overlay, disable_active_overlays
from ... graphics.drawing2d import set_drawing_dpi, draw_horizontal_line, draw_boolean, draw_text
from ... utils.objects import get_objects_in_same_group, set_active, remove_object_from_scene, only_select
from . parent_merge import boolean_diff_objects, cstep_reset, check_status, get_prefixed_object, hide_child_objects

class SimpleParentMergeOperator(bpy.types.Operator):
    bl_idname = "hops.simple_parent_merge"
    bl_label = "Simple Parent Merge"
    bl_options = {'REGISTER', 'UNDO'} 
    
    text = "Objects Joined via merge "
    op_tag = "Merge"
    op_detail = "Objects have been merged"
    
    sharpen_mesh = BoolProperty(default = True)
    
    @classmethod
    def poll(self, context):
        return getattr(context.active_object, "type", "") == "MESH"
        return getattr(context.selected_objects, "AP") is not None

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
        hide_child_objects(False)
        target_object = context.active_object
        
        plane_object = get_prefixed_object(context.selected_objects, "AP")

        set_active(plane_object)
        bpy.ops.object.select_grouped(type = "CHILDREN_RECURSIVE")
        #bpy.ops.object.parent_clear(type = "CLEAR_KEEP_TRANSFORM")

        childrens = context.selected_objects
        bounding_box_object = get_prefixed_object(childrens, "BB")
        
        boolean_diff_objects(target_object, bounding_box_object)
        hide_child_objects(True)

        bpy.ops.object.select_all(action='DESELECT')
        set_active(plane_object)
        plane_object.select = True

        
        try: self.wake_up_overlay()
        except: pass

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