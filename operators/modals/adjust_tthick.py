import bpy
from mathutils import Vector
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... graphics.drawing2d import draw_horizontal_line, draw_text, set_drawing_dpi, draw_box
from ... preferences import Hops_text_color, Hops_text2_color, Hops_border_color, Hops_border2_color

class AdjustTthickOperator(bpy.types.Operator):
    bl_idname = "hops.adjust_tthick"
    bl_label = "Adjust Tthick"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = "Change the thicknes of the active object solidify mod"

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def invoke(self, context, event):
        self.object = context.active_object
        self.solidify = self.get_solidify_modifier()
        self.start_mouse_position = Vector((event.mouse_region_x, event.mouse_region_y))
        self.start_solidify_thickness = self.solidify.thickness
        self.start_solidify_offset = self.solidify.offset
        self.start_solidify_use_rim_only = self.solidify.use_rim_only
        self.thickess_offset = 0
        self.solidify_offset = 0
        self.last_mouse_x = event.mouse_region_x

        args = (context, )
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw, args, "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def get_solidify_modifier(self):
        object = bpy.context.active_object
        solidify_modifier = None
        for modifier in object.modifiers:
            if modifier.type == "SOLIDIFY":
                solidify_modifier = modifier
                self.created_solidify_modifier = False
        if solidify_modifier is None:
            solidify_modifier = object.modifiers.new("Solidify", "SOLIDIFY")
            solidify_modifier.thickness = 0
            solidify_modifier.use_even_offset = True
            solidify_modifier.use_quality_normals = True
            solidify_modifier.use_rim_only = False
            solidify_modifier.show_on_cage = True
            self.created_solidify_modifier = True

        return solidify_modifier


    def modal(self, context, event):
        divisor = 10000 if event.shift else 10000000 if event.ctrl else 1000
        divisor_profile = 500 if event.ctrl else 100000000000
        offset_x = event.mouse_region_x - self.last_mouse_x
        self.thickess_offset -= offset_x / divisor / get_dpi_factor()
        self.solidify.thickness = self.start_solidify_thickness - self.thickess_offset
        self.solidify_offset -= offset_x / divisor_profile / get_dpi_factor()

        if event.type == 'ONE' and event.value=='PRESS':
            self.solidify.offset = -1
            self.solidify_offset = 0

        if event.type == 'TWO' and event.value=='PRESS':
            self.solidify.offset = 0
            self.solidify_offset = -1

        if event.type == 'THREE' and event.value=='PRESS':
            self.solidify.offset = 1
            self.solidify_offset = -2

        if event.ctrl:
            self.solidify.offset = self.start_solidify_offset - self.solidify_offset

        if event.type == 'R' and event.value=='PRESS':
            if bpy.context.object.modifiers["Solidify"].use_rim_only == False:
                self.solidify.use_rim_only = True
            else:
                self.solidify.use_rim_only = False

        if event.type in ("ESC", "RIGHTMOUSE"):
            self.reset_object()
            return self.finish()

        if event.type in ("SPACE", "LEFTMOUSE"):
            return self.finish()

        self.last_mouse_x = event.mouse_region_x
        context.area.tag_redraw()
        return {"RUNNING_MODAL"}

    def reset_object(self):
        self.solidify.thickness = self.start_solidify_thickness
        self.solidify.offset = self.start_solidify_offset
        if self.created_solidify_modifier:
            self.object.modifiers.remove(self.solidify)

    def finish(self):
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
        return {"FINISHED"}

    def draw(self, context):
        x, y = self.start_mouse_position
        solidify = self.solidify

        set_drawing_dpi(get_dpi())
        factor = get_dpi_factor()
        color_text1 = Hops_text_color()
        color_text2 = Hops_text2_color()
        color_border = Hops_border_color()
        color_border2 = Hops_border2_color()

        draw_box(x -14 * factor, y + 8 * factor, 224 * factor , 34* factor, color = color_border2)

        draw_box(x + 68 * factor, y + 8 * factor, 140 * factor , 30 * factor, color = color_border)

        if solidify.thickness < 0:
            draw_text("{:.3f}".format(solidify.thickness),  x -12 * factor, y, size = 23, color = color_text1)
        else:
            draw_text("{:.3f}".format(solidify.thickness),  x -4 * factor, y, size = 23, color = color_text1)

        draw_text("(R)im    -   {}".format(solidify.use_rim_only),
                 x + 70 * factor, y + 9 * factor , size = 12, color = color_text2)

        draw_text("(O)ffset -  {:.3f}".format(solidify.offset),
                  x + 70 * factor, y - 4 * factor, size = 12, color = color_text2)

        #draw_text(self.get_description_text(), x, y - 63 * factor,
                  #size = 12, color = color)
