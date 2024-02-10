import bpy
import math
import bmesh
from .... preferences import get_preferences


class HOPS_OT_ADD_grid_square(bpy.types.Operator):
    bl_idname = "hops.add_grid_square"
    bl_label = "Add smart grid_square"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """Create Smart grid_square"""


    def execute(self, context):
        verts = [(-1, -1, 0)]
        obj = bpy.data.objects.new("Grid", bpy.data.meshes.new("Grid"))

        bpy.ops.object.select_all(action='DESELECT')
        context.collection.objects.link(obj)
        context.view_layer.objects.active = obj
        obj.select_set(True)

        bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)

        if get_preferences().behavior.cursor_boolshapes:
            obj.rotation_euler = bpy.context.scene.cursor.rotation_euler

        bm = bmesh.new()
        for v in verts:
            bm.verts.new(v)
        bm.to_mesh(context.object.data)
        bm.free()

        self.add_screw_modifier(obj, 'X', 'HOPS_screw_x')
        self.add_screw_modifier(obj, 'Y', 'HOPS_screw_y', True)
        # self.add_decimate_modifier(obj, 'HOPS_decimate')
        self.add_wireframe_modifier(obj)
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = math.radians(30)

        return {"FINISHED"}


    def add_wireframe_modifier(self, object):
        modifier = object.modifiers.new(name="HOPS_wireframe_c", type="WIREFRAME")
        modifier.thickness = 0.02
        modifier.use_even_offset = True
        modifier.use_relative_offset = False
        modifier.use_replace = True
        modifier.use_boundary = True


    def add_screw_modifier(self, object, axis='X', name='HOPS_screw_x', flip=False):
        screw_modifier = object.modifiers.new(name=name, type="SCREW")
        screw_modifier.angle = math.radians(0)
        screw_modifier.axis = axis
        screw_modifier.steps = 10
        screw_modifier.render_steps = 10
        screw_modifier.screw_offset = 2
        screw_modifier.iterations = 1
        screw_modifier.use_smooth_shade = True
        screw_modifier.use_merge_vertices = True
        screw_modifier.use_normal_flip = flip


    def add_displace_modifier(self, object, axis='X', name='HOPS_displace_x'):
        displace_modifier = object.modifiers.new(name=name, type="DISPLACE")
        displace_modifier.direction = axis
        displace_modifier.strength = -1.5


    def add_decimate_modifier(self, object, name='HOPS_decimate_c'):
        modifier = object.modifiers.new('Decimate', 'DECIMATE')
        modifier.angle_limit = math.radians(5)
        modifier.decimate_type = 'DISSOLVE'


class HOPS_OT_ADD_grid_diamond(bpy.types.Operator):
    bl_idname = "hops.add_grid_diamond"
    bl_label = "Add smart grid_diamond"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """Create Smart grid_diamond"""

    def execute(self, context):
        verts = [(-1, -1, 0)]
        obj = bpy.data.objects.new("Grid", bpy.data.meshes.new("Grid"))

        bpy.ops.object.select_all(action='DESELECT')
        context.collection.objects.link(obj)
        context.view_layer.objects.active = obj
        obj.select_set(True)

        bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
        if get_preferences().behavior.cursor_boolshapes:
            obj.rotation_euler = bpy.context.scene.cursor.rotation_euler

        bm = bmesh.new()
        for v in verts:
            bm.verts.new(v)
        bm.to_mesh(context.object.data)
        bm.free()

        self.add_screw_modifier(obj, 'X', 'HOPS_screw_x')
        self.add_screw_modifier(obj, 'Y', 'HOPS_screw_y', True)
        self.add_decimate_modifier(obj, 'DISSOLVE', 'HOPS_decimate')
        self.add_subsurf_modifier(obj, 'HOPS_subsurf')
        self.add_decimate_modifier(obj, 'UNSUBDIV', 'HOPS_unsubdiv')
        self.add_wireframe_modifier(obj)
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = math.radians(30)

        return {"FINISHED"}


    def add_subsurf_modifier(self, object, name='HOPS_deform_z'):
        subsurf_mod = object.modifiers.new(name=name, type="SUBSURF")
        subsurf_mod.subdivision_type = 'SIMPLE'
        subsurf_mod.levels = 4


    def add_wireframe_modifier(self, object):
        modifier = object.modifiers.new(name="HOPS_wireframe_c", type="WIREFRAME")
        modifier.thickness = 0.02
        modifier.use_even_offset = True
        modifier.use_relative_offset = False
        modifier.use_replace = True
        modifier.use_boundary = True


    def add_screw_modifier(self, object, axis='X', name='HOPS_screw_x', flip=False):
        screw_modifier = object.modifiers.new(name=name, type="SCREW")
        screw_modifier.angle = math.radians(0)
        screw_modifier.axis = axis
        screw_modifier.steps = 3
        screw_modifier.render_steps = 3
        screw_modifier.screw_offset = 2
        screw_modifier.iterations = 1
        screw_modifier.use_smooth_shade = True
        screw_modifier.use_merge_vertices = True
        screw_modifier.use_normal_flip = flip


    def add_displace_modifier(self, object, axis='X', name='HOPS_displace_x'):
        displace_modifier = object.modifiers.new(name=name, type="DISPLACE")
        displace_modifier.direction = axis
        displace_modifier.strength = -1.5


    def add_decimate_modifier(self, object, types, name='HOPS_decimate_c'):
        modifier = object.modifiers.new('Decimate', 'DECIMATE')
        modifier.angle_limit = math.radians(5)
        modifier.decimate_type = types
        modifier.iterations = 1


class HOPS_OT_ADD_grid_honey(bpy.types.Operator):
    bl_idname = "hops.add_grid_honey"
    bl_label = "Add smart grid_honey"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """Create Smart grid_honey"""

    def execute(self, context):
        verts = [(0, 0, 0)]
        obj = bpy.data.objects.new("Grid", bpy.data.meshes.new("Grid"))

        bpy.ops.object.select_all(action='DESELECT')
        context.collection.objects.link(obj)
        context.view_layer.objects.active = obj
        obj.select_set(True)

        bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
        if get_preferences().behavior.cursor_boolshapes:
            obj.rotation_euler = bpy.context.scene.cursor.rotation_euler

        bm = bmesh.new()
        for v in verts:
            bm.verts.new(v)
        bm.to_mesh(context.object.data)
        bm.free()

        self.add_displace_modifier(obj, 'X', 'HOPS_displace_x')
        self.add_screw_modifier(obj, 0, 'X', 'HOPS_screw_x', 0.02, 2)
        self.add_screw_modifier(obj, 360, 'Z', 'HOPS_screw_y', 0, 6, True)
        self.add_decimate_modifier(obj, 'DISSOLVE', 'HOPS_decimate')
        self.add_solidify_modifier(obj, 'HOPS_solidify_z')
        self.add_array_modifier(obj, 0, 1, 2, 'HOPS_array_1')
        self.add_array_modifier(obj, 0.75, 0.25, 2, 'HOPS_array_2')
        self.add_array_modifier(obj, 0.85, 0, 4, 'HOPS_array_3')
        self.add_array_modifier(obj, 0, 0.8, 3, 'HOPS_array_4')

        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = math.radians(30)

        return {"FINISHED"}


    def add_array_modifier(self, object, x, y, c, name='HOPS_array_z'):
        modifier = object.modifiers.new(name, "ARRAY")
        modifier.relative_offset_displace[0] = x
        modifier.relative_offset_displace[1] = y
        modifier.relative_offset_displace[2] = 0
        modifier.count = c
        modifier.merge_threshold = 0.01


    def add_subsurf_modifier(self, object, name='HOPS_deform_z'):
        subsurf_mod = object.modifiers.new(name=name, type="SUBSURF")
        subsurf_mod.subdivision_type = 'SIMPLE'
        subsurf_mod.levels = 2


    def add_wireframe_modifier(self, object):
        modifier = object.modifiers.new(name="HOPS_wireframe_c", type="WIREFRAME")
        modifier.thickness = 0.02
        modifier.use_even_offset = True
        modifier.use_relative_offset = False
        modifier.use_replace = True
        modifier.use_boundary = True


    def add_screw_modifier(self, object, angle=0, axis='X', name='HOPS_screw_x', offset=0.02, step=6, flip=False):
        screw_modifier = object.modifiers.new(name=name, type="SCREW")
        screw_modifier.angle = math.radians(angle)
        screw_modifier.axis = axis
        screw_modifier.steps = step
        screw_modifier.render_steps = step
        screw_modifier.screw_offset = offset
        screw_modifier.iterations = 1
        screw_modifier.use_smooth_shade = True
        screw_modifier.use_merge_vertices = True
        screw_modifier.use_normal_flip = flip


    def add_displace_modifier(self, object, axis='X', name='HOPS_displace_x'):
        displace_modifier = object.modifiers.new(name=name, type="DISPLACE")
        displace_modifier.direction = axis
        displace_modifier.strength = 0.20


    def add_decimate_modifier(self, object, types, name='HOPS_decimate_c'):
        modifier = object.modifiers.new('Decimate', 'DECIMATE')
        modifier.angle_limit = math.radians(5)
        modifier.decimate_type = types
        modifier.iterations = 1


    def add_solidify_modifier(self, object, name='HOPS_solidify_z'):
        solidify_modifier = object.modifiers.new(name, "SOLIDIFY")
        solidify_modifier.thickness = 0.02
        solidify_modifier.offset = 1
        solidify_modifier.use_even_offset = True
        solidify_modifier.use_quality_normals = True
        solidify_modifier.use_rim_only = False
        solidify_modifier.show_on_cage = True
