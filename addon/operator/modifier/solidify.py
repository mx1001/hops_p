import bpy
import math
from statistics import median
from mathutils import Vector
from ... utility import view3d, method_handler, modifier
from bpy.props import EnumProperty, StringProperty
from mathutils.geometry import intersect_point_line
from .... preferences import get_preferences
from .... graphics.drawing2d import draw_text


class HOPS_OT_MODS_solidify(bpy.types.Operator):
    bl_idname = "hops.mods_solidify"
    bl_label = "Adjust Solidify Modifier"
    bl_description = "Adjust Solidify Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING", "INTERNAL"}
    axis: EnumProperty(
        name = "Mode",
        description = "",
        items = [
            ('X', "x", "Use x axis"),
            ('Y', "y", "Use y axis"),
            ('Z', "z", "Use z axis"),
            ('C', "c", "Use all axis")],
        default = 'X')

    modname: StringProperty(
        name = "deform mod name",
        default = 'HOPS_solidify_z')

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"


    def invoke(self, context, event):
        ob = context.active_object

        self.frontface, self.backface = self.faces(context, ob)

        self.mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        mouse3d = view3d.location2d_to_location3d(self.mouse[0], self.mouse[1], self.frontface)

        intersect = intersect_point_line(mouse3d, self.backface, self.frontface)
        p1_to_m3d = (self.backface - intersect[0]).length
        self.p1_to_p2 = (self.backface - self.frontface).length
        p2_to_m3d = (self.frontface - intersect[0]).length
        if self.axis is 'X':
            self.p2_to_m3d = p2_to_m3d / context.object.scale[0]
        elif self.axis is 'Y':
            self.p2_to_m3d = p2_to_m3d / context.object.scale[1]
        elif self.axis in {'Z', 'C'}:
            self.p2_to_m3d = p2_to_m3d / context.object.scale[2]

        if p1_to_m3d < self.p1_to_p2:
            self.p2_to_m3d = - self.p2_to_m3d

        modifier = ob.modifiers[self.modname]
        self.start = modifier.thickness
        self.thickness = modifier.thickness
        self.delta = 0
        self.delta_mouse = intersect_point_line(mouse3d, self.backface, self.frontface)
        self.offset = self.start
        self.ctrl = False
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_ui, (context, ), "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}


    def modal(self, context, event):
        self.mouse = Vector((event.mouse_region_x, event.mouse_region_y))

        ob = context.active_object
        frontface, backface = self.faces(context, ob)

        mouse3d = view3d.location2d_to_location3d(self.mouse[0], self.mouse[1], frontface)

        object = bpy.data.objects[context.active_object.name]
        modifier = object.modifiers[self.modname]

        intersect = intersect_point_line(mouse3d, self.backface, self.frontface)
        p2_to_m3d = (self.frontface - intersect[0]).length
        # p2_to_m3d = (self.frontface - intersect[0]).length
        p1_to_m3d = (self.backface - intersect[0]).length

        if p1_to_m3d < self.p1_to_p2:
            p2_to_m3d = - p2_to_m3d
        else:
            if p1_to_m3d < p2_to_m3d:
                p2_to_m3d = - p2_to_m3d

        if self.axis is 'X':
            p2_to_m3d = p2_to_m3d / context.object.scale[0]
        elif self.axis is 'Y':
            p2_to_m3d = p2_to_m3d / context.object.scale[1]
        elif self.axis in {'Z', 'C'}:
            p2_to_m3d = p2_to_m3d / context.object.scale[2]

        if event.shift:
            if event.ctrl:
                thickness = ((self.offset) + (p2_to_m3d - (self.p2_to_m3d)))
                self.delta = thickness
                thickness = (round(thickness, 2))
                self.delta_mouse = intersect_point_line(mouse3d, self.backface, self.frontface)
            else:
                new_distace = ((self.delta_mouse[0] - intersect[0]).length)

                if intersect[1] < self.delta_mouse[1]:
                    new_distace = -new_distace

                thickness = ((self.delta) + (new_distace / 10))
                self.offset = thickness - ((p2_to_m3d) - (self.p2_to_m3d))
        else:
            thickness = ((self.offset) + (p2_to_m3d - (self.p2_to_m3d)))
            self.delta = thickness
            if self.ctrl:
                if event.ctrl:
                    if event.shift:
                        thickness = (round(thickness, 2))
                    else:
                        thickness = (round(thickness, 1))
            self.delta_mouse = intersect_point_line(mouse3d, self.backface, self.frontface)

        modifier.thickness = thickness
        self.thickness = thickness

        if self.ctrl is False:
            if event.type == "LEFT_CTRL":
                if event.value == 'RELEASE':
                    self.ctrl = True

        context.area.header_text_set("Hardops Solidify Modal:                Solidify thickness: {}".format(round(thickness, 4)))

        if event.type == 'LEFTMOUSE':
            context.area.header_text_set(text=None)
            self.remove_ui()
            return {'FINISHED'}

        if event.type in ("ESC", "RIGHTMOUSE"):
            context.area.header_text_set(text=None)
            self.remove_ui()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}


    def add_solidify_modifier(self, object, name='HOPS_solidify_z'):
        solidify_modifier = object.modifiers.new(name, "SOLIDIFY")
        solidify_modifier.thickness = 1
        solidify_modifier.offset = 1
        solidify_modifier.use_even_offset = True
        solidify_modifier.use_quality_normals = True
        solidify_modifier.use_rim_only = False
        solidify_modifier.show_on_cage = True


    def faces(self, context, ob):
        bbox_corners = [ob.matrix_world @ Vector(corner) for corner in modifier.unmodified_bounds(ob)]

        if self.axis is 'X':
            frontface = median([bbox_corners[4], bbox_corners[5], bbox_corners[7], bbox_corners[6]])
            backface = ob.matrix_world @ (ob.matrix_world.inverted() @ frontface + Vector((-1, 0, 0)))
        elif self.axis is 'Z':
            frontface = median([bbox_corners[1], bbox_corners[2], bbox_corners[5], bbox_corners[6]])
            backface = ob.matrix_world @ (ob.matrix_world.inverted() @ frontface + Vector((0, 0, -1)))
        elif self.axis is 'Y':
            frontface = median([bbox_corners[2], bbox_corners[3], bbox_corners[6], bbox_corners[7]])
            backface = ob.matrix_world @ (ob.matrix_world.inverted() @ frontface + Vector((0, -1, 0)))
        elif self.axis is 'C':
            frontface = median([bbox_corners[1], bbox_corners[2], bbox_corners[5], bbox_corners[6]])
            backface = ob.matrix_world @ (ob.matrix_world.inverted() @ frontface + Vector((0, 0, -1)))

        return frontface, backface


    def draw_ui(self, context):
        method_handler(self._draw_ui,
            arguments = (context, ),
            identifier = F'{self.bl_label} UI Shader',
            exit_method = self.remove_ui)


    def _draw_ui(self, context):
        if get_preferences().display.display_text:
            location2d = view3d.location3d_to_location2d(median([self.backface, self.frontface]))
            draw_text("{}".format(round(self.thickness, 4)),
                      location2d.x, location2d.y, size=get_preferences().display.display_text_size, color=get_preferences().color.Hops_hud_text_color)


    def remove_ui(self):
        if self.draw_handler:
            self.draw_handler = bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
