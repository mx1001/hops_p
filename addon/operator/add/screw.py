import bpy
import math
import bmesh
from .... preferences import get_preferences


class HOPS_OT_ADD_circle(bpy.types.Operator):
    bl_idname = "hops.add_circle"
    bl_label = "Add smart circle"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """Create Smart circle"""

    def execute(self, context):
        verts = [(0, 0, 0)]
        obj = bpy.data.objects.new("Circle", bpy.data.meshes.new("Circle"))

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
        self.add_screw_modifier2(obj, 'Z', 'HOPS_screw', True)
        self.add_decimate_modifier(obj, 'HOPS_decimate_c')
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = math.radians(30)

        return {"FINISHED"}


    def add_screw_modifier(self, object, axis='X', name='HOPS_screw_x', flip=False):
        screw_modifier = object.modifiers.new(name=name, type="SCREW")
        screw_modifier.angle = math.radians(0)
        screw_modifier.axis = axis
        screw_modifier.steps = 2
        screw_modifier.render_steps = 2
        screw_modifier.screw_offset = 1
        screw_modifier.iterations = 1
        screw_modifier.use_smooth_shade = True
        screw_modifier.use_merge_vertices = True
        screw_modifier.use_normal_flip = flip


    def add_screw_modifier2(self, object, axis='X', name='HOPS_screw_x', flip=False):
        screw_modifier = object.modifiers.new(name=name, type="SCREW")
        screw_modifier.angle = math.radians(360)
        screw_modifier.axis = axis
        screw_modifier.steps = 36
        screw_modifier.render_steps = 36
        screw_modifier.screw_offset = 0
        screw_modifier.iterations = 1
        screw_modifier.use_smooth_shade = True
        screw_modifier.use_merge_vertices = True
        screw_modifier.use_normal_flip = flip


    def add_decimate_modifier(self, object, name='HOPS_decimate_c'):
        modifier = object.modifiers.new('Decimate', 'DECIMATE')
        modifier.angle_limit = math.radians(0.25)
        modifier.decimate_type = 'DISSOLVE'


class HOPS_OT_ADD_cylinder(bpy.types.Operator):
    bl_idname = "hops.add_cylinder"
    bl_label = "Add smart Cylinder"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """Create Smart Cylinder"""

    def execute(self, context):
        verts = [(0, 0, 0)]
        obj = bpy.data.objects.new("Cylinder", bpy.data.meshes.new("Cylinder"))

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
        self.add_screw_modifier2(obj, 'Z', 'HOPS_screw', True)
        self.add_solidify_modifier(obj, 'HOPS_solidify_z')
        self.add_decimate_modifier(obj, 'HOPS_decimate_c')
        self.add_bevel_modifier(context, obj, True, math.radians(30))
        if (2, 82, 4) < bpy.app.version:
            self.add_weld_modifier(obj, 'HOPS_weld')
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = math.radians(30)

        return {"FINISHED"}


    def add_screw_modifier(self, object, axis='X', name='HOPS_screw_x', flip=False):
        screw_modifier = object.modifiers.new(name=name, type="SCREW")
        screw_modifier.angle = math.radians(0)
        screw_modifier.axis = axis
        screw_modifier.steps = 2
        screw_modifier.render_steps = 2
        screw_modifier.screw_offset = 1
        screw_modifier.iterations = 1
        screw_modifier.use_smooth_shade = True
        screw_modifier.use_merge_vertices = True
        screw_modifier.use_normal_flip = flip


    def add_screw_modifier2(self, object, axis='X', name='HOPS_screw_x', flip=False):
        screw_modifier = object.modifiers.new(name=name, type="SCREW")
        screw_modifier.angle = math.radians(360)
        screw_modifier.axis = axis
        screw_modifier.steps = 32
        screw_modifier.render_steps = 32
        screw_modifier.screw_offset = 0
        screw_modifier.iterations = 1
        screw_modifier.use_smooth_shade = True
        screw_modifier.use_merge_vertices = True
        screw_modifier.use_normal_flip = flip

    def add_weld_modifier(self, object, name='HOPS_weld'):
        if (2, 82, 4) < bpy.app.version:
            modifier = object.modifiers.new('HOPS_weld', 'WELD')
        else:
            pass

    def add_solidify_modifier(self, object, name='HOPS_solidify_z'):
        solidify_modifier = object.modifiers.new(name, "SOLIDIFY")
        solidify_modifier.thickness = 2
        solidify_modifier.offset = 1
        solidify_modifier.use_even_offset = True
        solidify_modifier.use_quality_normals = True
        solidify_modifier.use_rim_only = False
        solidify_modifier.show_on_cage = True


    def add_bevel_modifier(self, context, object, clamp, angle):
        bevel_modifier = object.modifiers.new(name="HOPS_bevel_c", type="BEVEL")
        bevel_modifier.limit_method = "ANGLE"
        bevel_modifier.angle_limit = angle
        bevel_modifier.miter_outer = 'MITER_ARC'
        bevel_modifier.width = 0.15
        bevel_modifier.profile = 0.50
        bevel_modifier.segments = 1
        bevel_modifier.loop_slide = True
        bevel_modifier.use_clamp_overlap = clamp
        bpy.context.object.data.use_auto_smooth = True


    def add_displace_modifier(self, object, strength, axis='X', name='HOPS_displace_x'):
        displace_modifier = object.modifiers.new(name=name, type="DISPLACE")
        displace_modifier.direction = axis
        displace_modifier.strength = strength


    def add_decimate_modifier(self, object, name='HOPS_decimate_c'):
        modifier = object.modifiers.new('Decimate', 'DECIMATE')
        modifier.angle_limit = math.radians(0.25)
        modifier.decimate_type = 'DISSOLVE'


class HOPS_OT_ADD_cone(bpy.types.Operator):
    bl_idname = "hops.add_cone"
    bl_label = "Add smart Cone"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """Create Smart Cone"""


    def execute(self, context):
        verts = [(0, 0, 0)]
        obj = bpy.data.objects.new("Cone", bpy.data.meshes.new("Cone"))

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
        self.add_screw_modifier2(obj, 'Z', 'HOPS_screw', True)
        self.add_subsurf_modifier(obj, name='SUBSURF')
        self.add_solidify_modifier(obj, 'HOPS_solidify_z')
        self.add_deform_modifier(obj, 'HOPS_taper_z')
        self.add_decimate_modifier(obj, 'HOPS_decimate_c')
        self.add_bevel_modifier(context, obj, math.radians(30), True)
        if (2, 82, 4) < bpy.app.version:
            self.add_weld_modifier(obj, 'HOPS_weld')
        #self.add_bevel_modifier(context, obj, math.radians(60), True)

        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = math.radians(30)

        return {"FINISHED"}


    def add_subsurf_modifier(self, object, name='HOPS_deform_z'):
        subsurf_mod = object.modifiers.new(name=name, type="SUBSURF")
        subsurf_mod.subdivision_type = 'CATMULL_CLARK'
        subsurf_mod.levels = 2

    def add_weld_modifier(self, object, name='HOPS_weld'):
        if (2, 82, 4) < bpy.app.version:
            modifier = object.modifiers.new('HOPS_weld', 'WELD')
        else:
            pass

    def add_deform_modifier(self, object, name='HOPS_deform_z'):
        modifier = object.modifiers.new(name, "SIMPLE_DEFORM")
        modifier.factor = -0.8
        modifier.deform_method = 'TAPER'
        # modifier.deform_method = 'BEND'
        # modifier.deform_method = 'TAPER'
        # modifier.deform_method = 'STRETCH'
        modifier.deform_axis = 'Z'
        modifier.show_render = False


    def add_screw_modifier(self, object, axis='X', name='HOPS_screw_x', flip=False):
        screw_modifier = object.modifiers.new(name=name, type="SCREW")
        screw_modifier.angle = math.radians(0)
        screw_modifier.axis = axis
        screw_modifier.steps = 2
        screw_modifier.render_steps = 2
        screw_modifier.screw_offset = 0.738
        screw_modifier.iterations = 1
        screw_modifier.use_smooth_shade = True
        screw_modifier.use_merge_vertices = True
        screw_modifier.use_normal_flip = flip


    def add_screw_modifier2(self, object, axis='X', name='HOPS_screw_x', flip=False):
        screw_modifier = object.modifiers.new(name=name, type="SCREW")
        screw_modifier.angle = math.radians(360)
        screw_modifier.axis = axis
        screw_modifier.steps = 16
        screw_modifier.render_steps = 1
        screw_modifier.screw_offset = 0
        screw_modifier.iterations = 1
        screw_modifier.use_smooth_shade = True
        screw_modifier.use_merge_vertices = True
        screw_modifier.use_normal_flip = flip


    def add_solidify_modifier(self, object, name='HOPS_solidify_z'):
        solidify_modifier = object.modifiers.new(name, "SOLIDIFY")
        solidify_modifier.thickness = 2
        solidify_modifier.offset = 1
        solidify_modifier.use_even_offset = True
        solidify_modifier.use_quality_normals = True
        solidify_modifier.use_rim_only = False
        solidify_modifier.show_on_cage = True


    def add_bevel_modifier(self, context, object, angle, clamp):
        bevel_modifier = object.modifiers.new(name="HOPS_bevel_c", type="BEVEL")
        bevel_modifier.limit_method = "ANGLE"
        bevel_modifier.angle_limit = angle
        bevel_modifier.miter_outer = 'MITER_ARC'
        bevel_modifier.width = 0.028
        bevel_modifier.profile = 0.50
        bevel_modifier.segments =4
        bevel_modifier.loop_slide = True
        bevel_modifier.use_clamp_overlap = clamp
        bpy.context.object.data.use_auto_smooth = True


    def add_displace_modifier(self, object, strength, axis='X', name='HOPS_displace_x'):
        displace_modifier = object.modifiers.new(name=name, type="DISPLACE")
        displace_modifier.direction = axis
        displace_modifier.strength = strength
        displace_modifier.show_render = False

    def add_decimate_modifier(self, object, name='HOPS_decimate_c'):
        modifier = object.modifiers.new('Decimate', 'DECIMATE')
        modifier.angle_limit = math.radians(0.25)
        modifier.decimate_type = 'DISSOLVE'


class HOPS_OT_ADD_ring(bpy.types.Operator):
    bl_idname = "hops.add_ring"
    bl_label = "Add smart ring"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """Create Smart ring"""


    def execute(self, context):
        verts = [(0, 0, 0)]
        obj = bpy.data.objects.new("Ring", bpy.data.meshes.new("Ring"))

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

        self.add_displace_modifier(obj, "HOPS_displace_x")
        self.add_screw_modifier(obj, 'X', 'HOPS_screw_x')
        self.add_screw_modifier2(obj, 'Z', 'HOPS_screw', True)
        self.add_solidify_modifier(obj, 'HOPS_solidify_z')
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = math.radians(30)
        # self.add_bevel_modifier(context, obj, math.radians(30))
        # self.add_bevel_modifier2(context, obj, math.radians(30))

        return {"FINISHED"}


    def add_screw_modifier(self, object, axis='X', name='HOPS_screw_x', flip=False):
        screw_modifier = object.modifiers.new(name=name, type="SCREW")
        screw_modifier.angle = math.radians(0)
        screw_modifier.axis = axis
        screw_modifier.steps = 2
        screw_modifier.render_steps = 2
        screw_modifier.screw_offset = 0.5
        screw_modifier.iterations = 1
        screw_modifier.use_smooth_shade = True
        screw_modifier.use_merge_vertices = True
        screw_modifier.use_normal_flip = flip


    def add_screw_modifier2(self, object, axis='X', name='HOPS_screw_x', flip=False):
        screw_modifier = object.modifiers.new(name=name, type="SCREW")
        screw_modifier.angle = math.radians(360)
        screw_modifier.axis = axis
        screw_modifier.steps = 64
        screw_modifier.render_steps = 64
        screw_modifier.screw_offset = 0
        screw_modifier.iterations = 1
        screw_modifier.use_smooth_shade = True
        screw_modifier.use_merge_vertices = True
        screw_modifier.use_normal_flip = flip


    def add_displace_modifier(self, object, name="HOPS_displace_x",):
        modifier = object.modifiers.new(name=name, type="DISPLACE")
        modifier.direction = 'X'
        modifier.strength = 1
        modifier.space = 'LOCAL'


    def add_solidify_modifier(self, object, name='HOPS_solidify_z'):
        solidify_modifier = object.modifiers.new(name, "SOLIDIFY")
        solidify_modifier.thickness = 0.475
        solidify_modifier.offset = 1
        solidify_modifier.use_even_offset = True
        solidify_modifier.use_quality_normals = True
        solidify_modifier.use_rim_only = False
        solidify_modifier.show_on_cage = True


    def add_bevel_modifier(self, context, object, angle):
        bevel_modifier = object.modifiers.new(name="HOPS_bevel_a", type="BEVEL")
        bevel_modifier.limit_method = "ANGLE"
        bevel_modifier.angle_limit = angle
        bevel_modifier.miter_outer = 'MITER_ARC'
        bevel_modifier.width = 0.22
        bevel_modifier.profile = 0.50
        bevel_modifier.segments = 6
        bevel_modifier.loop_slide = True
        bevel_modifier.use_clamp_overlap = False
        bpy.context.object.data.use_auto_smooth = True


    def add_bevel_modifier2(self, context, object, angle):
        bevel_modifier = object.modifiers.new(name="HOPS_bevel_b", type="BEVEL")
        bevel_modifier.limit_method = "ANGLE"
        bevel_modifier.angle_limit = angle
        bevel_modifier.miter_outer = 'MITER_ARC'
        bevel_modifier.width = 0.1
        bevel_modifier.profile = 0.70
        bevel_modifier.segments = 6
        bevel_modifier.loop_slide = True
        bevel_modifier.use_clamp_overlap = False
        bpy.context.object.data.use_auto_smooth = True


class HOPS_OT_ADD_screw(bpy.types.Operator):
    bl_idname = "hops.add_screw"
    bl_label = "Add smart screw"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """Create Smart screw"""


    def execute(self, context):
        verts = [(0, 0, 0)]
        obj = bpy.data.objects.new("Plane", bpy.data.meshes.new("Plane"))

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


        self.add_displace_modifier(obj, "HOPS_displace_y",)
        self.add_screw_modifier(obj, 'Y', 'HOPS_screw_y', 2, math.radians(0))
        self.add_screw_modifier(obj, 'Z', 'HOPS_screw_z', 2, math.radians(0))
        self.add_decimate_modifier(obj, 'HOPS_decimate')
        self.add_screw_modifier(obj, 'Z', 'HOPS_screw_z2', offset=0.31)
        self.add_Subdivision_modifier(obj, 'CATMULL_CLARK')

        namey = "HOPS_screw_y"
        namez = "HOPS_screw_z"

        driver = obj.driver_add("modifiers[\"" + namez + "\"].screw_offset").driver
        driver.type = 'SCRIPTED'

        var = driver.variables.new()
        var.targets[0].id_type = 'OBJECT'
        var.targets[0].id = obj.id_data
        var.targets[0].data_path = "modifiers[\"" + namey + "\"].screw_offset"
        var.name = "HopsScrew"

        driver.expression = var.name


        return {"FINISHED"}


    def add_displace_modifier(self, object, name="HOPS_displace_y",):
        modifier = object.modifiers.new(name=name, type="DISPLACE")
        modifier.direction = 'Y'
        modifier.strength = 1.75
        modifier.space = 'LOCAL'


    def add_screw_modifier(self, object, axis='X', name='HOPS_screw_x', steps=32, angle=math.radians(720), offset=0.02, flip=False):
        screw_modifier = object.modifiers.new(name=name, type="SCREW")
        screw_modifier.angle = angle
        screw_modifier.axis = axis
        screw_modifier.steps = steps
        screw_modifier.render_steps = steps
        screw_modifier.screw_offset = offset
        screw_modifier.iterations = 6
        screw_modifier.use_smooth_shade = True
        screw_modifier.use_merge_vertices = True
        screw_modifier.use_normal_flip = flip


    def add_solidify_modifier(self, object, name='HOPS_solidify_z'):
        solidify_modifier = object.modifiers.new(name, "SOLIDIFY")
        solidify_modifier.thickness = 0.2
        solidify_modifier.offset = 0
        solidify_modifier.use_even_offset = True
        solidify_modifier.use_quality_normals = True
        solidify_modifier.use_rim_only = False
        solidify_modifier.show_on_cage = True


    def add_Subdivision_modifier(self, object, subtype='CATMULL_CLARK'):
        subsurf_mod = object.modifiers.new(name="Subdivision", type="SUBSURF")
        subsurf_mod.subdivision_type = subtype #'SIMPLE' or 'CATMULL_CLARK'
        subsurf_mod.levels = 2


    def add_decimate_modifier(self, object, name='HOPS_decimate_c'):
        modifier = object.modifiers.new('Decimate', 'DECIMATE')
        modifier.angle_limit = math.radians(0.25)
        modifier.decimate_type = 'DISSOLVE'