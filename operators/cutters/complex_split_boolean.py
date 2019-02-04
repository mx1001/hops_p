import bpy
from bgl import *
from bpy.props import *
from math import radians, degrees
from ... utils.context import ExecutionContext
from ... overlay_drawer import show_custom_overlay, disable_active_overlays
from ... utils.blender_ui import get_location_in_current_3d_view
from ... overlay_drawer import show_custom_overlay, disable_active_overlays
from ... utils.objects import link_object_to_scene, move_modifier_up, apply_modifier, new_deep_object_copy, join_objects, only_select, set_active
from ... material import assign_material

#updated Drawing Imports Hops 8
from ... graphics.drawing2d import set_drawing_dpi, draw_horizontal_line, draw_boolean, draw_text, draw_box, draw_logo_csharp
from ... preferences import tool_overlays_enabled, get_hops_preferences_colors_with_transparency, Hops_display_time, Hops_fadeout_time

class ComplexSplitBooleanOperator(bpy.types.Operator):
    bl_idname = "hops.complex_split_boolean"
    bl_label = "Complex Split Boolean"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = ""

    split_mesh = BoolProperty(name = "Split Mesh",
                              description = "Separate the mesh after CSplit",
                              default = True)

    text = "Meshes Separated"
    op_tag = "(C)Slice"
    op_detail = "Meshes split"

    use_bmesh = BoolProperty(name = "Use Bmesh Boolean",
                             description = "Use new bmesh boolean",
                             default = False)

    sub_d_sharpening = BoolProperty(name = "Sub-D Sharpening",
                                    description = "For subdivision use",
                                    default = False)

    @classmethod
    def poll(cls, context):
        if len(cls.get_cutter_objects()) == 0: return False
        if getattr(context.active_object, "type", "") != "MESH": return False
        if getattr(context.active_object, "mode", "") != "OBJECT": return False
        return getattr(context.active_object, "type", "") == "MESH"
        return True

    def draw(self, context):
        layout = self.layout

        layout.prop(self, "split_mesh")
        layout.prop(self, "use_bmesh")
        layout.prop(self, "sub_d_sharpening")

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
        return self.use_bmesh, self.split_mesh, self.op_tag, self.text, self.op_detail

    def execute(self, context):
        original_mesh_objects = [object for object in bpy.data.objects if object.type == 'MESH' and object != context.active_object]
        target = context.active_object
        target_bounds = [coord[:] for coord in target.bound_box]
        cutters = self.get_cutter_objects()
        for cutter in cutters:
            cutter.draw_type = "WIRE"
            assign_material(context, cutter, csplit=True)
            self.split(target, cutter, self.use_bmesh, self.sub_d_sharpening)
        if self.split_mesh:
            self.separate_mesh_by_looseparts(target)
        split_objects = [object for object in [object for object in bpy.data.objects if object.type == 'MESH'] if object not in original_mesh_objects]
        target = self.get_target_object(split_objects, target_bounds)
        split_objects.remove(target)
        for object in split_objects:
            assign_material(context, object, replace=True)
        only_select(cutters)
        return {'FINISHED'}

    def split(self, object, cutter, use_bmesh, sub_d_sharpening, margin = 0.0001):
        if margin != 0:
            solidify = cutter.modifiers.new(name = "temp", type = "SOLIDIFY")
            solidify.thickness = margin
            solidify.offset = 1
        if not object.hops.is_pending_boolean:
            self.cut_object(object, cutter, "DIFFERENCE", use_bmesh)
        if object.hops.status == "CSTEP":
            bpy.ops.step.sstep()
        elif object.hops.status == "SUBSHARP":
            bpy.ops.hops.complex_sharpen(sub_d_sharpening=True)
        elif object.hops.status == "UNDEFINED":
            pass
        else:
            bpy.ops.hops.complex_sharpen(sub_d_sharpening=sub_d_sharpening)
        if margin != 0:
            cutter.modifiers.remove(solidify)

    @staticmethod
    def get_cutter_objects():
        selection = bpy.context.selected_objects
        active = bpy.context.active_object
        return [object for object in selection if object != active and object.type == "MESH"]

    @staticmethod
    def separate_mesh_by_looseparts(object):
        set_active(object)
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.separate(type='LOOSE')
        bpy.ops.object.mode_set(mode = 'OBJECT')

    @staticmethod
    def get_target_object(split_objects, target_bounds):
        bound_differences = []
        for object in split_objects:
            object_bounds = [coord[:] for coord in object.bound_box]
            bounds_difference = [abs(object_bounds[i][0] - target_bounds[i][0]) + abs(object_bounds[i][1] - target_bounds[i][1]) + abs(object_bounds[i][2] - target_bounds[i][2]) for i in range(len(object_bounds))]
            bound_differences.append(sum(bounds_difference))
        return split_objects[bound_differences.index(min(bound_differences))]

    @staticmethod
    def cut_object(object, cutter, operation, use_bmesh):
        modifier = object.modifiers.new(name = "temp", type = "BOOLEAN")
        modifier.operation = operation
        if use_bmesh:
            modifier.solver = 'BMESH'
        else:
            modifier.solver = 'CARVE'

        modifier.object = cutter
        move_modifier_up(modifier)
        apply_modifier(modifier)


# Overlay
###################################################################

def draw(display, parameter_getter):
    use_bmesh, split_mesh, op_detail, op_tag, text = parameter_getter()
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

    draw_text("CSPLIT", x - 380 *dpi_factor , y -12*dpi_factor,
              align = "LEFT", size = 20 , color = color_text2)


    # First Coloumn
    ########################################################
    x = x - 160 * dpi_factor
    r = 120 * dpi_factor
    offset = r

    draw_text("Result:", x, y,
              align = "LEFT", color = color_text2)

    if split_mesh == True:
        draw_text(text, x + r , y,
                  align = "LEFT", size = 12, color = color_text2)
    else:
        draw_text("Meshes Not Separated", x + r , y,
                  align = "LEFT", size = 12, color = color_text2)


    # Last Part
    ########################################################

    x = x + 300 * dpi_factor

    draw_text("Split Mesh :", x + offset, y,
              align = "RIGHT", color = color_text2)

    draw_boolean(split_mesh, x, y, size = 11, alpha = transparency)

    draw_text("B-Mesh Boolean", x + offset, y - line_height,
              align = "RIGHT", color = color_text2)

    draw_boolean(use_bmesh, x, y - line_height, size = 11, alpha = transparency)

    glDisable(GL_BLEND)
    glDisable(GL_LINE_SMOOTH)
