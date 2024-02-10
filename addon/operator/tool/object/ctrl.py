import platform
import time
import string

import bpy
import bmesh

from math import radians, sqrt
from statistics import median

from mathutils import Matrix, Vector
from itertools import combinations

from bpy.types import Operator

from .. shader import dots
from .. dots import update
from .... utility import addon, view3d, screen
from ..... utils.blender_ui import get_dpi_factor


descriptions = {
    'screw_x': "Adjust Screw X",
    'screw_y': "Adjust Screw Y",
    'screw_z': "Adjust Screw Z",
    'solidify_x': "Adjust Solidify",
    'solidify_y': "Adjust Solidify",
    'solidify_z': "Adjust Solidify",
    'solidify_c': "Adjust Solidify",
    'displace_x': "Adjust Displace X",
    'displace_y': "Adjust Displace Y",
    'displace_z': "Adjust Displace Z",
    'simple_deform_x': "Adjust Deform X",
    'simple_deform_y': "Adjust Deform Y",
    'simple_deform_z': "Adjust Deform Z",
    'array_x': "Adjust Array X",
    'array_y': "Adjust Array Y",
    'array_z': "Adjust Array Z",
    'bevel_c': "Adjust Bevel",
    'wireframe_c': "Adjust Wireframe Thickness",
    'boolshape': "Display BoolShape",
    'Grab': "Grab Manipulator",
    'Cut': "Cut Shape",
    'Union': "Union Shape",
    'Slash': "Slash Shape",
    'Inset': "Inset Shape",
    'Intersect': "Intersect Shape",
    'Knife': "Knife Shape"
}


class HARDFLOWOM_OT_display(Operator):
    bl_idname = 'hardflow_om.display'
    bl_label = 'ctrl'
    bl_description = 'Display Hardflow Dots'
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    def invoke(self, context, event):
        if not context.active_object or context.active_object.type != 'MESH':
            return {'CANCELLED'}

        self.system = 'WINLIN' if platform.system() != 'Darwin' else 'MAC'
        self.unhide_collection = False
        hardflow = bpy.context.window_manager.hardflow
        hardflow.running = True
        # self.bm = bmesh.from_edit_mesh(context.active_object.data)
        # preference = addon.preference()
        self.original_region = bpy.context.region
        self.original_active = bpy.data.objects[bpy.context.active_object.name]
        self.mouse = self.start_mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        self.release = False
        self.start_time = 0.0
        self.tooltip = False

        context.window_manager.modal_handler_add(self)
        # hardflow.dots.points.clear()

        if addon.preference().behavior.display_gizmo:
            bpy.context.space_data.show_gizmo_context = False

        self.collect(context)

        update(self, context, hardflow.dots, self.mouse)

        dots.handler = bpy.types.SpaceView3D.draw_handler_add(dots, (self, context), 'WINDOW', 'POST_PIXEL')

        context.area.tag_redraw()
        return {'RUNNING_MODAL'}


    def modal(self, context, event):
        hardflow = bpy.context.window_manager.hardflow
        standard = set(string.ascii_uppercase + string.digits + string.punctuation)

        if not hardflow.running or context.region != self.original_region:
            self.exit(context)
            return {'CANCELLED'}

        if context.active_object != self.original_active:
            self.original_active = bpy.data.objects[bpy.context.active_object.name]
            self.collect(context)

        if event.value == 'RELEASE' and not self.release:

            self.release = True
            self.collect(context)

        if event.type == 'MOUSEMOVE':
            self.mouse = Vector((event.mouse_region_x, event.mouse_region_y))
            update(self, context, hardflow.dots, self.mouse)

        held = event.ctrl or (event.oskey and self.system == 'MAC')
        if held:
            if event.type == 'LEFTMOUSE':
                if event.value == 'PRESS':
                    self.release = False
                    hardflow.dots.points.clear()
                    if self.highlight:
                        self.start_time = time.time()
                        if event.shift:
                            self.step_mod()
                        else:
                            self.use_mod(context)

            elif event.type == 'RIGHTMOUSE':
                if event.value == 'PRESS':
                    if self.highlight:
                        popover_types = {'screw', 'array', 'solidify', 'displace', 'simple_deform', 'bevel', 'wireframe'}
                        if self.highlight_type[:-2] in popover_types:
                            bpy.ops.hops.dot_settings()

            elif event.type == 'MIDDLEMOUSE':
                if event.value == 'PRESS':
                    self.release = False
                    hardflow.dots.points.clear()

            elif event.type in standard:
                self.exit(context)
                hardflow.dots.points.clear()
                return {'PASS_THROUGH'}


        else:

            if addon.preference().behavior.display_gizmo:
                bpy.context.space_data.show_gizmo_context = True
            self.exit(context)
            hardflow.dots.points.clear()
            return {'CANCELLED'}

        context.area.tag_redraw()

        return {'PASS_THROUGH'}

    def exit(self, context):
        hardflow = context.window_manager.hardflow
        hardflow.running = False
        hardflow.dots.display = False

        if dots.handler:
            dots.remove(dots)

        self.active_point = None

        hardflow.dots.hit = False
        hardflow.dots.location = (0.0, 0.0, 0.0)
        hardflow.dots.normal = Vector()
        hardflow.dots.object = None

        hardflow.dots.mesh = None
        hardflow.dots.index = int()
        hardflow.dots.points.clear()


    def unmodified_bounds(self, obj, exclude={'ARRAY'}):
        disabled = []
        for mod in obj.modifiers:
            if mod.type in exclude and mod.show_viewport:
                disabled.append(mod)
                mod.show_viewport = False

        bpy.context.view_layer.update()

        bounds = [Vector(point[:]) for point in obj.bound_box[:]]

        for mod in disabled:
            mod.show_viewport = True

        del disabled

        return bounds

    def collect(self, context):
        hardflow = bpy.context.window_manager.hardflow

        if not hardflow.running:
            return

        hardflow.dots.points.clear()

        ob = context.active_object

        Xgizmos = []
        Ygizmos = []
        Zgizmos = []
        Cgizmos = []

        offset = addon.preference().display.dot_side_offset / 100
        offsetc = addon.preference().display.dot_corner_offset / 100

        mod_types = {
            'SCREW',
            'SOLIDIFY',
            'DISPLACE',
            'SIMPLE_DEFORM',
            'ARRAY',
            'BEVEL',
            'WIREFRAME'}

        c_types = {'BEVEL', 'WIREFRAME'}
        both_types = {'SOLIDIFY'}

        if addon.preference().behavior.display_dots:

            for mod in ob.modifiers:
                if mod.type in mod_types and not mod.name.startswith('Hops array displace'):
                    axis = 'C' if mod.type in c_types else ''

                    # c type append
                    if axis:
                        Cgizmos.append(self.collect_c_types(context, ob, mod, offsetc, Cgizmos))

                    # by type
                    elif mod.type == 'ARRAY':
                        displace = mod.relative_offset_displace
                        displace_axis = [displace[i] != 0 for i in range(3)]
                        index = displace_axis.index(True) if True in displace_axis else 0
                        axis = 'XYZ'[index]

                    # by attr
                    elif hasattr(mod, 'axis'):
                        axis = mod.axis

                    elif hasattr(mod, 'direction'):
                        if mod.direction not in {'X', 'Y', 'Z'}:
                            axis = 'Z'
                        else:
                            axis = mod.direction

                    elif hasattr(mod, 'deform_axis'):
                        axis = mod.deform_axis

                    # both type fallthrough
                    elif mod.type in both_types and not axis:
                        if len([m for m in ob.modifiers if m.type == mod.type]) > 1:
                            axis = 'C'
                            Cgizmos.append(self.collect_c_types(context, ob, mod, offsetc, Cgizmos))
                        else:
                            axis = 'Z'

                    # axis type append
                    if axis and axis != 'C':
                        gizmos = locals()[F'{axis}gizmos']
                        _type = self.collect_axis_types(context, ob, mod, offset, axis, gizmos)
                        gizmos.append(_type)

        if addon.preference().behavior.display_boolshapes:
            if addon.preference().behavior.display_boolshapes_for_all:
                boolshapes = [obj for obj in context.view_layer.objects if obj.hops.status == "BOOLSHAPE" and not obj.visible_get()]
            else:
                boolshapes = [mod.object for mod in ob.modifiers if mod.type == "BOOLEAN" and mod.object and not mod.object.visible_get()]
            for obj in boolshapes:
                self.collect_bbox_origin(context, obj, 'boolshape', 'blue', obj.name)

        if addon.preference().behavior.display_operators:
            if len(context.selected_objects) > 1:
                factor = get_dpi_factor()
                if addon.preference().property.dots_snap == 'FIXED':
                    self.collect_origins(context, 'Grab', 'black', Vector((0.0, 0.0)))
                self.collect_origins(context, 'Cut', 'red', Vector((-20.0 * factor, 0.0 * factor)))
                self.collect_origins(context, 'Union', 'green', Vector((-11.0 * factor, 20.0 * factor)))
                self.collect_origins(context, 'Slash', 'yellow', Vector((-11.0 * factor, -20.0 * factor)))
                self.collect_origins(context, 'Knife', 'blue', Vector((11.0 * factor, -20.0 * factor)))
                self.collect_origins(context, 'Intersect', 'orange', Vector((11.0 * factor, 20.0 * factor)))
                self.collect_origins(context, 'Inset', 'purple', Vector((20.0 * factor, 0.0 * factor)))

    def collect_c_types(self, context, ob, mod, offset, Cgizmos):
        factor = 1 if bpy.context.space_data.region_3d.is_perspective else 6
        v_to_origin = (context.region_data.view_matrix@ob.location).length * factor

        _type = F'{mod.type.lower()}_c'
        pos = (
            -(len(Cgizmos) * offset * v_to_origin),
            len(Cgizmos) * offset * v_to_origin,
            len(Cgizmos) * offset * v_to_origin)

        self.collect_bbox_cross(context, ob, _type, mod.name, Vector(pos), _type)
        return mod.type.lower()

    def collect_axis_types(self, context, ob, mod, offset, axis, gizmos):
        factor = 1 if bpy.context.space_data.region_3d.is_perspective else 6
        v_to_origin = (context.region_data.view_matrix@ob.location).length * factor

        bbox_collect = F'collect_bbox_{axis.lower()}face'
        _type = F'{mod.type.lower()}_{axis.lower()}'
        offs = len(gizmos) * offset * v_to_origin
        index = ['X', 'Y', 'Z'].index(axis)
        pos = [0, 0, 0]
        pos[index] = offs

        getattr(self, bbox_collect)(context, ob, _type, mod.name, Vector(pos), _type)
        return mod.type.lower()

    # FACES
    def collect_bbox_origin(self, context, ob, types, color, obj_name):
        hardflow = context.window_manager.hardflow
        bbox_corners = [(ob.matrix_world @ (Vector(corner))) for corner in ob.bound_box]
        new = hardflow.dots.points.add()
        new.location3d = median([bbox_corners[0], bbox_corners[1], bbox_corners[2], bbox_corners[3], bbox_corners[4], bbox_corners[5], bbox_corners[6], bbox_corners[7]])
        new.type = types
        new.color = color
        new.name = obj_name
        new.description = descriptions[types]

    def collect_bbox_cross(self, context, ob, types, mod_name, offset=Vector((0, 0, 0)), color='main'):
        hardflow = context.window_manager.hardflow
        locmat = Matrix.Translation(Vector((0, 0, 0))) @ ob.rotation_euler.to_matrix().to_4x4() @ (Matrix.Scale(1, 4, (1, 0, 0)) @ Matrix.Scale(1, 4, (0, 1, 0)) @ Matrix.Scale(1, 4, (0, 0, 1)))
        bbox_corners = [(ob.matrix_world @ (Vector(corner))) + (locmat @ offset) for corner in self.unmodified_bounds(ob)]
        new = hardflow.dots.points.add()
        new.location3d = bbox_corners[2]
        new.type = types
        new.color = color
        new.name = mod_name
        new.description = descriptions[types]

    def collect_bbox_yface(self, context, ob, types, mod_name, offset=Vector((0, 0, 0)), color='main'):
        hardflow = context.window_manager.hardflow
        locmat = Matrix.Translation(Vector((0, 0, 0))) @ ob.rotation_euler.to_matrix().to_4x4() @ (Matrix.Scale(1, 4, (1, 0, 0)) @ Matrix.Scale(1, 4, (0, 1, 0)) @ Matrix.Scale(1, 4, (0, 0, 1)))
        bbox_corners = [(ob.matrix_world @ (Vector(corner))) + (locmat @ offset) for corner in self.unmodified_bounds(ob)]
        new = hardflow.dots.points.add()
        new.location3d = median([bbox_corners[2], bbox_corners[3], bbox_corners[6], bbox_corners[7]])
        new.type = types
        new.color = color
        new.name = mod_name
        new.description = descriptions[types]

    def collect_bbox_zface(self, context, ob, types, mod_name, offset=Vector((0, 0, 0)), color='main'):
        hardflow = context.window_manager.hardflow
        locmat = Matrix.Translation(Vector((0, 0, 0))) @ ob.rotation_euler.to_matrix().to_4x4() @ (Matrix.Scale(1, 4, (1, 0, 0)) @ Matrix.Scale(1, 4, (0, 1, 0)) @ Matrix.Scale(1, 4, (0, 0, 1)))
        bbox_corners = [(ob.matrix_world @ (Vector(corner))) + (locmat @ offset) for corner in self.unmodified_bounds(ob)]
        new = hardflow.dots.points.add()
        new.location3d = median([bbox_corners[1], bbox_corners[2], bbox_corners[5], bbox_corners[6]])
        new.type = types
        new.color = color
        new.name = mod_name
        new.description = descriptions[types]

    def collect_bbox_xface(self, context, ob, types, mod_name, offset=Vector((0, 0, 0)), color='main'):
        hardflow = context.window_manager.hardflow
        locmat = Matrix.Translation(Vector((0, 0, 0))) @ ob.rotation_euler.to_matrix().to_4x4() @ (Matrix.Scale(1, 4, (1, 0, 0)) @ Matrix.Scale(1, 4, (0, 1, 0)) @ Matrix.Scale(1, 4, (0, 0, 1)))
        bbox_corners = [(ob.matrix_world @ (Vector(corner))) + (locmat @ offset) for corner in self.unmodified_bounds(ob)]
        new = hardflow.dots.points.add()
        new.location3d = median([bbox_corners[4], bbox_corners[5], bbox_corners[7], bbox_corners[6]])
        new.type = types
        new.color = color
        new.name = mod_name
        new.description = descriptions[types]

    def collect_bbox_ybface(self, context, ob, types, mod_name, offset=Vector((0, 0, 0))):
        hardflow = context.window_manager.hardflow
        locmat = Matrix.Translation(Vector((0, 0, 0))) @ ob.rotation_euler.to_matrix().to_4x4() @ (Matrix.Scale(1, 4, (1, 0, 0)) @ Matrix.Scale(1, 4, (0, 1, 0)) @ Matrix.Scale(1, 4, (0, 0, 1)))
        bbox_corners = [(ob.matrix_world @ (Vector(corner))) + (locmat @ offset) for corner in self.unmodified_bounds(ob)]
        new = hardflow.dots.points.add()
        new.location3d = median([bbox_corners[0], bbox_corners[1], bbox_corners[4], bbox_corners[5]])
        new.type = types
        new.name = mod_name
        new.description = descriptions[types]

    def collect_bbox_zbface(self, context, ob, types, mod_name, offset=Vector((0, 0, 0))):
        hardflow = context.window_manager.hardflow
        locmat = Matrix.Translation(Vector((0, 0, 0))) @ ob.rotation_euler.to_matrix().to_4x4() @ (Matrix.Scale(1, 4, (1, 0, 0)) @ Matrix.Scale(1, 4, (0, 1, 0)) @ Matrix.Scale(1, 4, (0, 0, 1)))
        bbox_corners = [(ob.matrix_world @ (Vector(corner))) + (locmat @ offset) for corner in self.unmodified_bounds(ob)]
        new = hardflow.dots.points.add()
        new.location3d = median([bbox_corners[3], bbox_corners[4], bbox_corners[7], bbox_corners[0]])
        new.type = types
        new.name = mod_name
        new.description = descriptions[types]

    def collect_bbox_xbface(self, context, ob, types, mod_name, offset=Vector((0, 0, 0))):
        hardflow = context.window_manager.hardflow
        locmat = Matrix.Translation(Vector((0, 0, 0))) @ ob.rotation_euler.to_matrix().to_4x4() @ (Matrix.Scale(1, 4, (1, 0, 0)) @ Matrix.Scale(1, 4, (0, 1, 0)) @ Matrix.Scale(1, 4, (0, 0, 1)))
        bbox_corners = [(ob.matrix_world @ (Vector(corner))) + (locmat @ offset) for corner in self.unmodified_bounds(ob)]
        new = hardflow.dots.points.add()
        new.location3d = median([bbox_corners[0], bbox_corners[1], bbox_corners[2], bbox_corners[3]])
        new.type = types
        new.name = mod_name
        new.description = descriptions[types]

    # EDGES
    def collect_bbox_xedge(self, context, ob, types, mod_name, offset=Vector((0, 0, 0))):
        hardflow = context.window_manager.hardflow
        locmat = Matrix.Translation(Vector((0, 0, 0))) @ ob.rotation_euler.to_matrix().to_4x4() @ (Matrix.Scale(1, 4, (1, 0, 0)) @ Matrix.Scale(1, 4, (0, 1, 0)) @ Matrix.Scale(1, 4, (0, 0, 1)))
        bbox_corners = [(ob.matrix_world @ (Vector(corner))) + (locmat @ offset) for corner in self.unmodified_bounds(ob)]
        new = hardflow.dots.points.add()
        new.location3d = median([bbox_corners[4], bbox_corners[7]])
        new.type = types
        new.name = mod_name
        new.description = descriptions[types]

    def collect_bbox_yedge(self, context, ob, types, mod_name, offset=Vector((0, 0, 0))):
        hardflow = context.window_manager.hardflow
        locmat = Matrix.Translation(Vector((0, 0, 0))) @ ob.rotation_euler.to_matrix().to_4x4() @ (Matrix.Scale(1, 4, (1, 0, 0)) @ Matrix.Scale(1, 4, (0, 1, 0)) @ Matrix.Scale(1, 4, (0, 0, 1)))
        bbox_corners = [(ob.matrix_world @ (Vector(corner))) + (locmat @ offset) for corner in self.unmodified_bounds(ob)]
        new = hardflow.dots.points.add()
        new.location3d = median([bbox_corners[3], bbox_corners[7]])
        new.type = types
        new.name = mod_name
        new.description = descriptions[types]

    def collect_bbox_zedge(self, context, ob, types, mod_name, offset=Vector((0, 0, 0))):
        hardflow = context.window_manager.hardflow
        locmat = Matrix.Translation(Vector((0, 0, 0))) @ ob.rotation_euler.to_matrix().to_4x4() @ (Matrix.Scale(1, 4, (1, 0, 0)) @ Matrix.Scale(1, 4, (0, 1, 0)) @ Matrix.Scale(1, 4, (0, 0, 1)))
        bbox_corners = [(ob.matrix_world @ (Vector(corner))) + (locmat @ offset) for corner in self.unmodified_bounds(ob)]
        new = hardflow.dots.points.add()
        new.location3d = median([bbox_corners[1], bbox_corners[2]])
        new.type = types
        new.name = mod_name
        new.description = descriptions[types]

    def collect_origins(self, context, types, color, offset):
        hardflow = context.window_manager.hardflow
        selected = context.selected_objects
        origins = [obj.location for obj in selected]


        if addon.preference().property.dots_snap == 'CURSOR':
            d2 = Vector((addon.preference().property.dots_x_cursor + self.start_mouse[0], addon.preference().property.dots_y_cursor + self.start_mouse[1]))
        elif addon.preference().property.dots_snap == 'FIXED':

            if addon.preference().property.dots_x < 40:
                addon.preference().property.dots_x = 40
            elif addon.preference().property.dots_x > (context.region.width - 40):
                addon.preference().property.dots_x = (context.region.width - 40)

            if addon.preference().property.dots_y < 40:
                addon.preference().property.dots_y = 40
            elif addon.preference().property.dots_y > (context.region.height - 40):
                addon.preference().property.dots_y = (context.region.height - 40)

            d2 = Vector((addon.preference().property.dots_x, addon.preference().property.dots_y))
        elif addon.preference().property.dots_snap == 'ORIGIN':
            d2 = view3d.location3d_to_location2d(median(origins))

        d2 = d2 + offset
        d3 = view3d.location2d_to_location3d(d2[0], d2[1], median(origins))
        new = hardflow.dots.points.add()
        new.location3d = d3
        new.type = types
        new.color = color
        new.description = descriptions[types]

    def collect_bbox_verts(self, context, ob):
        hardflow = context.window_manager.hardflow
        self.unmodified_bounds(ob)

        for v in ob.bound_box:
            new = hardflow.dots.points.add()
            new.location3d = v

    def step_mod(self):
        step_types = {'bevel', 'screw', 'array'}
        axis = self.highlight_type[-1].upper()
        _type = self.highlight_type[:-2]

        if _type not in step_types:
            return

        ot = F'mods_{_type}_step'
        getattr(bpy.ops.hops, ot)('INVOKE_DEFAULT', axis=axis, modname=self.highlight_modname)

    def use_mod(self, context):
        types = {'array', 'screw', 'solidify', 'displace', 'simple_deform', 'bevel', 'wireframe'}
        hardflow = bpy.context.window_manager.hardflow
        axis = self.highlight_type[-1].upper()
        _type = self.highlight_type[:-2]

        # booleans
        if addon.preference().property.dots_snap == 'FIXED':
            if self.highlight_type == "Grab":
                bpy.ops.hops.dots_grab('INVOKE_DEFAULT')

        none_mesh_count = len([o for o in context.selected_objects if o.type != 'MESH'])
        if none_mesh_count == 0:
            if self.highlight_type == "Cut":
                bpy.ops.hops.bool_difference_hotkey('INVOKE_DEFAULT')

            elif self.highlight_type == "Union":
                bpy.ops.hops.bool_union_hotkey('INVOKE_DEFAULT')

            elif self.highlight_type == "Slash":
                bpy.ops.hops.slash_hotkey('INVOKE_DEFAULT')

            elif self.highlight_type == "Inset":
                bpy.ops.hops.bool_inset('INVOKE_DEFAULT')

            elif self.highlight_type == "Intersect":
                bpy.ops.hops.bool_intersect_hotkey('INVOKE_DEFAULT')

            elif self.highlight_type == "Knife":
                bpy.ops.hops.bool_knife('INVOKE_DEFAULT')


        if _type not in types and _type[:4] != 'bool':
            return

        if _type[:4] not in {'bool'}:
            ot = F'mods_{_type}'
            getattr(bpy.ops.hops, ot)('INVOKE_DEFAULT', axis=axis, modname=self.highlight_modname)

            return

        elif self.highlight_type == 'wireframe_c':
            bpy.ops.hops.mods_wireframe('INVOKE_DEFAULT', modname=self.highlight_modname)

        elif self.highlight_type == "boolshape":
            bpy.ops.hops.select_boolshape(obj_name=self.highlight_modname)

            return


        hardflow.dots.points.clear()
