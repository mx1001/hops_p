import bpy
import math
from statistics import median
from mathutils import Vector
from ... utility import view3d, method_handler, modifier
from bpy.props import EnumProperty,StringProperty
from mathutils.geometry import intersect_point_line
from .... preferences import get_preferences
from .... graphics.drawing2d import draw_text


class HOPS_OT_MODS_bevel(bpy.types.Operator):
    bl_idname = "hops.mods_bevel"
    bl_label = "Adjust Bevel Modifier"
    bl_description = "Adjust Bevel Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING", "INTERNAL"}

    axis: EnumProperty(
        name = "Mode",
        description = "",
        items = [('C', "c", "Use c axis"),
                ('B', "b", "Use b axis"),
                ('D', "d", "Use d axis")],
        default = 'C')

    modname: StringProperty(
        name = "deform mod name",
        default = 'HOPS_twist_z')

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'MESH'


    def invoke(self, context, event):
        ob = context.active_object
        self.frontface, self.backface = self.faces(context, ob)

        self.mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        mouse3d = view3d.location2d_to_location3d(self.mouse[0], self.mouse[1], self.frontface)

        intersect = intersect_point_line(mouse3d, self.backface, self.frontface)
        p1_to_m3d = (self.backface - intersect[0]).length
        self.p1_to_p2 = (self.backface - self.frontface).length
        p2_to_m3d = (self.frontface - intersect[0]).length

        if self.axis in {'C', 'B', 'D'}:
            self.p2_to_m3d = p2_to_m3d / max(context.object.scale)

        if p1_to_m3d < self.p1_to_p2:
            self.p2_to_m3d = - self.p2_to_m3d

        modifier = ob.modifiers[self.modname]
        self.start = modifier.width
        self.width = modifier.width
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
        p1_to_m3d = (self.backface - intersect[0]).length

        if p1_to_m3d < self.p1_to_p2:
            p2_to_m3d = - p2_to_m3d
        else:
            if p1_to_m3d < p2_to_m3d:
                p2_to_m3d = - p2_to_m3d

        if self.axis in {'C', 'B', 'D'}:
            p2_to_m3d = p2_to_m3d / max(context.object.scale)

        if event.shift:
            if event.ctrl:
                width = ((self.offset) + (p2_to_m3d - (self.p2_to_m3d)))
                self.delta = width
                width = (round(width, 2))
                self.delta_mouse = intersect_point_line(mouse3d, self.backface, self.frontface)
            else:
                new_distace = ((self.delta_mouse[0] - intersect[0]).length)

                if intersect[1] < self.delta_mouse[1]:
                    new_distace = -new_distace

                width = ((self.delta) + (new_distace / 10))
                self.offset = width - ((p2_to_m3d) - (self.p2_to_m3d))
        else:
            width = ((self.offset) + (p2_to_m3d - (self.p2_to_m3d)))
            self.delta = width
            if self.ctrl:
                if event.ctrl:
                    if event.shift:
                        width = (round(width, 2))
                    else:
                        width = (round(width, 1))
            self.delta_mouse = intersect_point_line(mouse3d, self.backface, self.frontface)

        modifier.width = width
        self.width = modifier.width

        if self.ctrl is False:
            if event.type == "LEFT_CTRL":
                if event.value == 'RELEASE':
                    self.ctrl = True

        context.area.header_text_set("Hardops Bevel Modal:                Bevel width: {}".format(round(self.width, 4)))

        if event.type == 'LEFTMOUSE':
            context.area.header_text_set(text=None)
            self.remove_ui()
            return {'FINISHED'}

        if event.type in ("ESC", "RIGHTMOUSE"):
            context.area.header_text_set(text=None)
            self.remove_ui()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}


    def faces(self, context, ob):
        bbox_corners = [ob.matrix_world @ Vector(corner) for corner in modifier.unmodified_bounds(ob)]

        if self.axis is 'C':
            frontface = bbox_corners[2]
            backface = bbox_corners[4]
            # modname = 'HOPS_bevel_c'
        elif self.axis is 'D':
            frontface = bbox_corners[2]
            backface = bbox_corners[4]
            # modname = 'HOPS_bevel_d'
        elif self.axis is 'B':
            frontface = bbox_corners[2]
            backface = bbox_corners[4]
            # self.modname = 'HOPS_bevel_b'

        return frontface, backface


    def add_bevel_modifier(self, object):
        modifier = object.modifiers.new(name="Bevel", type="BEVEL")
        if bpy.app.version < (2, 90, 0):
            modifier.use_only_vertices = False
        else:
            modifier.affect = 'EDGES'
        modifier.limit_method = "ANGLE"
        modifier.angle_limit = math.radians(30)
        modifier.miter_outer = 'MITER_ARC'
        modifier.width = 0.02
        modifier.profile = get_preferences().property.bevel_profile
        modifier.segments = 3
        modifier.loop_slide = get_preferences().property.bevel_loop_slide
        modifier.use_clamp_overlap = False

        #smoothing
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = math.radians(30)


    def draw_ui(self, context):
        method_handler(self._draw_ui,
            arguments = (context, ),
            identifier = F'{self.bl_label} UI Shader',
            exit_method = self.remove_ui)


    def _draw_ui(self, context):
        if get_preferences().display.display_text:
            location2d = view3d.location3d_to_location2d(median([self.backface, self.frontface]))
            draw_text("{}".format(round(self.width, 4)),
                      location2d.x, location2d.y, size=get_preferences().display.display_text_size, color=get_preferences().color.Hops_hud_text_color)


    def remove_ui(self):
        if self.draw_handler:
            self.draw_handler = bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")


class HOPS_OT_MODS_bevel_step(bpy.types.Operator):
    bl_idname = "hops.mods_bevel_step"
    bl_label = "Adjust Bevel Modifier"
    bl_description = "Adjust Bevel Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING", "INTERNAL"}
    axis: EnumProperty(
        name = "Mode",
        description = "",
        items = [
            ('C', "c", "Use c axis"),
            ('B', "b", "Use b axis"),
            ('D', "d", "Use d axis")],
        default = 'C')

    modname: StringProperty(
        name = "deform mod name",
        default = 'HOPS_bevel')

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

        if self.axis in {'C', 'B', 'D'}:
            self.p2_to_m3d = p2_to_m3d / max(context.object.scale)

        if p1_to_m3d < self.p1_to_p2:
            self.p2_to_m3d = - self.p2_to_m3d

        modifier = ob.modifiers[self.modname]
        self.start = modifier.segments
        self.segments = modifier.segments
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
        p1_to_m3d = (self.backface - intersect[0]).length

        if p1_to_m3d < self.p1_to_p2:
            p2_to_m3d = - p2_to_m3d
        else:
            if p1_to_m3d < p2_to_m3d:
                p2_to_m3d = - p2_to_m3d

        if self.axis in {'C', 'B', 'D'}:
            p2_to_m3d = p2_to_m3d / max(context.object.scale)

        segments = ((self.offset) + (p2_to_m3d - (self.p2_to_m3d)) * 2)

        if segments > 24:
            segments = 24

        self.delta = segments

        segments = (round(segments, 1))
        self.delta_mouse = intersect_point_line(mouse3d, self.backface, self.frontface)

        modifier.segments = segments
        self.segments = modifier.segments

        if self.ctrl is False:
            if event.type == "LEFT_CTRL":
                if event.value == 'RELEASE':
                    self.ctrl = True

        context.area.header_text_set("Hardops Bevel Modal:                Bevel Segments: {}".format(modifier.segments))

        if event.type == 'LEFTMOUSE':
            context.area.header_text_set(text=None)
            self.remove_ui()
            return {'FINISHED'}

        if event.type in ("ESC", "RIGHTMOUSE"):
            context.area.header_text_set(text=None)
            self.remove_ui()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}


    def add_bevel_modifier(self, object):
        modifier = object.modifiers.new(name="Bevel", type="BEVEL")
        if bpy.app.version < (2, 90, 0):
            modifier.use_only_vertices = False
        else:
            modifier.affect = 'EDGES'
        modifier.limit_method = "ANGLE"
        modifier.angle_limit = math.radians(30)
        modifier.miter_outer = 'MITER_ARC'
        modifier.width = 0.02
        modifier.profile = get_preferences().property.bevel_profile
        modifier.segments = 3
        modifier.loop_slide = get_preferences().property.bevel_loop_slide
        modifier.use_clamp_overlap = False

        #smoothing
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = math.radians(30)


    def faces(self, context, ob):
        bbox_corners = [ob.matrix_world @ Vector(corner) for corner in modifier.unmodified_bounds(ob)]

        if self.axis is 'C':
            frontface = bbox_corners[2]
            backface = bbox_corners[4]
            # modname = 'HOPS_bevel_c'
        elif self.axis is 'D':
            frontface = bbox_corners[2]
            backface = bbox_corners[4]
            # modname = 'HOPS_bevel_d'
        elif self.axis is 'B':
            frontface = bbox_corners[2]
            backface = bbox_corners[4]
            # self.modname = 'HOPS_bevel_b'

        return frontface, backface


    def draw_ui(self, context):
        method_handler(self._draw_ui,
            arguments = (context, ),
            identifier = F'{self.bl_label} UI Shader',
            exit_method = self.remove_ui)


    def _draw_ui(self, context):
        if get_preferences().display.display_text:
            location2d = view3d.location3d_to_location2d(median([self.backface, self.frontface]))
            draw_text("{}".format(self.segments),
                      location2d.x, location2d.y, size=get_preferences().display.display_text_size, color=get_preferences().color.Hops_hud_text_color)


    def remove_ui(self):
        if self.draw_handler:
            self.draw_handler = bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
