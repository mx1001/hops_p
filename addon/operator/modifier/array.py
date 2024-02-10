import bpy
import math
from statistics import median
from mathutils import Vector
from ... utility import view3d, method_handler, modifier
from .... graphics.drawing2d import draw_text
from .... preferences import get_preferences
from bpy.props import EnumProperty, StringProperty
from mathutils.geometry import intersect_point_line


class HOPS_OT_MODS_array(bpy.types.Operator):
    bl_idname = "hops.mods_array"
    bl_label = "Adjust Array Modifier"
    bl_description = "Adjust Array Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING", "INTERNAL"}

    axis: EnumProperty(
        name = "Mode",
        description = "",
        items = [
            ('X', "x", "Use x axis"),
            ('Y', "y", "Use y axis"),
            ('Z', "z", "Use z axis")],
        default = 'X')

    modname: StringProperty(
        name = "array mod name",
        default = 'Array')

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)


    def invoke(self, context, event):
        self.objects = [o for o in context.selected_objects if o.type == 'MESH']
        self.object = context.active_object if context.active_object.type == 'MESH' else self.objects[0]

        self.frontface, self.backface = self.faces(context, self.object)

        self.mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        mouse3d = view3d.location2d_to_location3d(self.mouse[0], self.mouse[1], self.frontface)

        intersect = intersect_point_line(mouse3d, self.backface, self.frontface)
        p1_to_m3d = (self.backface - intersect[0]).length
        self.p1_to_p2 = (self.backface - self.frontface).length
        p2_to_m3d = (self.frontface - intersect[0]).length

        modifier = self.object.modifiers[self.modname]

        self.dimensions = (1, 1, 1)

        self.modifier_count = (modifier.count - 1) if modifier.use_object_offset is False and modifier.count - 1 > 0 else 1

        if modifier.use_constant_offset is True and modifier.use_relative_offset is False:
            mod_displace = modifier.constant_offset_displace
        else:
            mod_displace = modifier.relative_offset_displace
            modifier.show_viewport = False
            self.dimensions = self.object.dimensions
            modifier.show_viewport = True

        if self.axis is 'X':
            self.p2_to_m3d = p2_to_m3d / self.object.scale[0]
            self.start = (mod_displace[0] * self.dimensions[0]) * self.modifier_count
            self.offset_displace = mod_displace[0] * self.dimensions[0] * self.modifier_count
        elif self.axis is 'Y':
            self.p2_to_m3d = p2_to_m3d / self.object.scale[1]
            self.start = (mod_displace[1] * self.dimensions[1]) * self.modifier_count
            self.offset_displace = mod_displace[1] * self.dimensions[1] * self.modifier_count
        elif self.axis in {'Z'}:
            self.p2_to_m3d = p2_to_m3d / self.object.scale[2]
            self.start = (mod_displace[2] * self.dimensions[2]) * self.modifier_count
            self.offset_displace = mod_displace[2] * self.dimensions[2] * self.modifier_count

        self.factor = 1
        if p1_to_m3d < p2_to_m3d:
            self.factor = -1
        if p1_to_m3d < self.p1_to_p2:
            self.p2_to_m3d = - self.p2_to_m3d

        self.delta = 0
        self.origin = 0
        self.delta_mouse = intersect_point_line(mouse3d, self.backface, self.frontface)
        self.offset = self.start
        self.ctrl = False

        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_ui, (context, ), "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}


    def modal(self, context, event):
        self.mouse = Vector((event.mouse_region_x, event.mouse_region_y))

        frontface, _ = self.faces(context, self.object)

        modifier = self.object.modifiers[self.modname]

        if self.axis is 'X':
            origin_vector = Vector((self.origin, 0, 0))
        elif self.axis is 'Y':
            origin_vector = Vector((0, self.origin, 0))
        elif self.axis is 'Z':
            origin_vector = Vector((0, 0, self.origin))

        new_point = self.object.matrix_world @ (self.object.matrix_world.inverted() @ frontface + origin_vector)
        mouse3d = view3d.location2d_to_location3d(self.mouse[0], self.mouse[1], new_point)

        if modifier.use_constant_offset is True and modifier.use_relative_offset is False:
            mod_displace = modifier.constant_offset_displace
        else:
            mod_displace = modifier.relative_offset_displace

        intersect = intersect_point_line(mouse3d, self.backface, self.frontface)
        p2_to_m3d = (self.frontface - intersect[0]).length
        p1_to_m3d = (self.backface - intersect[0]).length

        if p1_to_m3d < self.p1_to_p2:
            p2_to_m3d = - p2_to_m3d

        else:
            if p1_to_m3d < p2_to_m3d:
                p2_to_m3d = - p2_to_m3d

        if self.axis is 'X':
            p2_to_m3d = p2_to_m3d / self.object.scale[0]
        elif self.axis is 'Y':
            p2_to_m3d = p2_to_m3d / self.object.scale[1]
        elif self.axis is 'Z':
            p2_to_m3d = p2_to_m3d / self.object.scale[2]

        if event.shift:
            if event.ctrl:
                offset_displace = ((self.offset) + (p2_to_m3d - (self.p2_to_m3d)))
                self.delta = offset_displace
                if self.axis is 'X':
                    offset_displace = (offset_displace / self.dimensions[0]) / self.modifier_count
                elif self.axis is 'Y':
                    offset_displace = (offset_displace / self.dimensions[1]) / self.modifier_count
                elif self.axis is 'Z':
                    offset_displace = (offset_displace / self.dimensions[2]) / self.modifier_count

                offset_displace = (round(offset_displace, 2))
                self.delta_mouse = intersect_point_line(mouse3d, self.backface, self.frontface)
            else:
                new_distace = ((self.delta_mouse[0] - intersect[0]).length)

                if intersect[1] < self.delta_mouse[1]:
                    new_distace = -new_distace

                offset_displace = ((self.delta) + (new_distace / 10))
                self.offset = offset_displace - ((p2_to_m3d) - (self.p2_to_m3d))
                if self.axis is 'X':
                    offset_displace = (offset_displace / self.dimensions[0]) / self.modifier_count
                elif self.axis is 'Y':
                    offset_displace = (offset_displace / self.dimensions[1]) / self.modifier_count
                elif self.axis is 'Z':
                    offset_displace = (offset_displace / self.dimensions[2]) / self.modifier_count

        else:
            offset_displace = ((self.offset) + (p2_to_m3d - self.factor * (self.p2_to_m3d)))
            self.delta = offset_displace

            if self.axis is 'X':
                dimension = self.dimensions[0] if self.dimensions[0] > 0 else 1
                offset_displace = (offset_displace / dimension) / self.modifier_count
            elif self.axis is 'Y':
                dimension = self.dimensions[1] if self.dimensions[1] > 0 else 1
                offset_displace = (offset_displace / dimension) / self.modifier_count
            elif self.axis is 'Z':
                dimension = self.dimensions[2] if self.dimensions[2] > 0 else 1
                offset_displace = (offset_displace / dimension) / self.modifier_count

            if self.ctrl:
                if event.ctrl:
                    if event.shift:
                        offset_displace = (round(offset_displace, 2))
                    else:
                        offset_displace = (round(offset_displace, 1))
            self.delta_mouse = intersect_point_line(mouse3d, self.backface, self.frontface)

        self.offset_displace = offset_displace
        if self.axis is 'X':
            mod_displace[0] = self.offset_displace
        elif self.axis is 'Y':
            mod_displace[1] = self.offset_displace
        elif self.axis is 'Z':
            mod_displace[2] = self.offset_displace

        self.origin = (p2_to_m3d - self.factor * (self.p2_to_m3d))

        if self.ctrl is False:
            if event.type == "LEFT_CTRL":
                if event.value == 'RELEASE':
                    self.ctrl = True

        if event.type == 'LEFTMOUSE':
            context.area.header_text_set(text=None)
            self.remove_ui()
            return {'FINISHED'}

        if event.type in ("ESC", "RIGHTMOUSE"):
            context.area.header_text_set(text=None)
            self.remove_ui()
            return {'CANCELLED'}

        if event.type == 'ONE' and event.value == 'PRESS':
            if self.axis is 'X':
                mod_displace[0] = 1
            elif self.axis is 'Y':
                mod_displace[1] = 1
            elif self.axis is 'Z':
                mod_displace[2] = 1
            context.area.header_text_set(text=None)
            self.remove_ui()
            return {'FINISHED'}

        context.area.header_text_set("Hardops Array Modal:                Array Offset: X:{} Y:{} Z:{}".format(round(mod_displace[0], 4), round(mod_displace[1], 4), round(mod_displace[2], 4)))
        return {'RUNNING_MODAL'}


    def add_deform_modifier(self, object, name='HOPS_array_z'):
        modifier = object.modifiers.new(name, "ARRRAY")
        mod_displace = modifier.constant_offset_displace

        mod_displace[0] = 1.6
        mod_displace[1] = 0.1
        mod_displace[2] = 0.1
        modifier.count = 3


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

        return frontface, backface


    def draw_ui(self, context):
        method_handler(self._draw_ui,
            arguments = (context, ),
            identifier = F'{self.bl_label} UI Shader',
            exit_method = self.remove_ui)


    def _draw_ui(self, context):
        if get_preferences().display.display_text:
            location2d = view3d.location3d_to_location2d(median([self.backface, self.frontface]))
            draw_text("{}".format(round(self.offset_displace, 4)),
                      location2d.x, location2d.y, size=get_preferences().display.display_text_size, color=get_preferences().color.Hops_hud_text_color)


    def remove_ui(self):
        if self.draw_handler:
            self.draw_handler = bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")


class HOPS_OT_MODS_array_step(bpy.types.Operator):
    bl_idname = "hops.mods_array_step"
    bl_label = "Adjust Array Modifier"
    bl_description = "Adjust Array Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING", "INTERNAL"}

    axis: EnumProperty(
        name = "Mode",
        description = "",
        items = [
            ('X', "x", "Use x axis"),
            ('Y', "y", "Use y axis"),
            ('Z', "z", "Use z axis")],
        default = 'X')

    modname: StringProperty(
        name = "array mod name",
        default = 'Array')

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)


    def invoke(self, context, event):
        self.objects = [o for o in context.selected_objects if o.type == 'MESH']
        self.object = context.active_object if context.active_object.type == 'MESH' else self.objects[0]

        self.frontface, self.backface = self.faces(context, self.object)

        self.mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        mouse3d = view3d.location2d_to_location3d(self.mouse[0], self.mouse[1], self.frontface)

        intersect = intersect_point_line(mouse3d, self.backface, self.frontface)
        p1_to_m3d = (self.backface - intersect[0]).length
        self.p1_to_p2 = (self.backface - self.frontface).length
        p2_to_m3d = (self.frontface - intersect[0]).length
        modifier = self.object.modifiers[self.modname]

        if self.axis is 'X':
            self.p2_to_m3d = p2_to_m3d / self.object.scale[0]
        elif self.axis is 'Y':
            self.p2_to_m3d = p2_to_m3d / self.object.scale[1]
        elif self.axis in {'Z'}:
            self.p2_to_m3d = p2_to_m3d / self.object.scale[2]

        self.start = modifier.count
        self.count = modifier.count

        if p1_to_m3d < self.p1_to_p2:
            self.p2_to_m3d = - self.p2_to_m3d

        # modifier = ob.modifiers[self.modname]
        # if modifier.deform_method in{'TWIST', 'BEND'}:
        #     self.start = modifier.angle
        # else:
        self.delta = 0
        self.delta_mouse = intersect_point_line(mouse3d, self.backface, self.frontface)
        self.offset = self.start
        self.ctrl = False
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_ui, (context, ), "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}


    def modal(self, context, event):
        self.mouse = Vector((event.mouse_region_x, event.mouse_region_y))

        frontface, backface = self.faces(context, self.object)

        mouse3d = view3d.location2d_to_location3d(self.mouse[0], self.mouse[1], frontface)

        modifier = self.object.modifiers[self.modname]

        intersect = intersect_point_line(mouse3d, self.backface, self.frontface)
        p2_to_m3d = (self.frontface - intersect[0]).length
        p2_to_m3d2 = (self.frontface - intersect[0]).length
        p1_to_m3d = (self.backface - intersect[0]).length

        if p1_to_m3d < self.p1_to_p2:
            p2_to_m3d = - p2_to_m3d
        else:
            if p1_to_m3d < p2_to_m3d2:
                p2_to_m3d = - p2_to_m3d

        if self.axis is 'X':
            p2_to_m3d = p2_to_m3d / self.object.scale[0]
        elif self.axis is 'Y':
            p2_to_m3d = p2_to_m3d / self.object.scale[1]
        elif self.axis in {'Z'}:
            p2_to_m3d = p2_to_m3d / self.object.scale[2]

        count = ((self.offset) + (p2_to_m3d - (self.p2_to_m3d)))
        self.delta = count
        count = (round(count, 1))

        modifier.count = count
        self.count = (round(count))

        if self.ctrl is False:
            if event.type == "LEFT_CTRL":
                if event.value == 'RELEASE':
                    self.ctrl = True

        context.area.header_text_set("Hardops Array Modal:                Array Count: {}".format(modifier.count))

        if event.type == 'LEFTMOUSE':
            context.area.header_text_set(text=None)
            self.remove_ui()
            return {'FINISHED'}

        if event.type in ("ESC", "RIGHTMOUSE"):
            context.area.header_text_set(text=None)
            self.remove_ui()
            return {'CANCELLED'}

        if event.type == 'ONE' and event.value == 'PRESS':
            modifier.count = 1

        if event.type == 'TWO' and event.value == 'PRESS':
            modifier.count = 2

        if event.type == 'THREE' and event.value == 'PRESS':
            modifier.count = 3
        return {'RUNNING_MODAL'}


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

        return frontface, backface


    def draw_ui(self, context):
        method_handler(self._draw_ui,
            arguments = (context, ),
            identifier = F'{self.bl_label} UI Shader',
            exit_method = self.remove_ui)


    def _draw_ui(self, context):
        if get_preferences().display.display_text:
            location2d = view3d.location3d_to_location2d(median([self.backface, self.frontface]))
            draw_text("{}".format(round(self.count, 4)),
                      location2d.x, location2d.y, size=get_preferences().display.display_text_size, color=get_preferences().color.Hops_hud_text_color)


    def remove_ui(self):
        if self.draw_handler:
            self.draw_handler = bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
