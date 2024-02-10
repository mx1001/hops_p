import bpy
import math
import bmesh
from .... preferences import get_preferences
from ... property.preference import property


class HOPS_OT_ADD_bbox(bpy.types.Operator):
    bl_idname = "hops.add_bbox"
    bl_label = "Add smart bbox"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """Creates Smart Box

LMB - Rounded Smart Box
CTRL - Planar Smart Box

    """

    def invoke(self, context, event):
        verts = [(-1, -1, 0)]
        # verts = [(0, 0, 0)]
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

        self.add_screw_modifier(obj, 'X', 'HOPS_screw_x')
        self.add_screw_modifier(obj, 'Y', 'HOPS_screw_y', True)
        if get_preferences().behavior.add_mirror_to_boolshapes:
            self.add_mirror_modifier(obj, 'HOPS_mirror')
        self.add_decimate_modifier(obj, 'HOPS_decimate_c')

        if bpy.app.version < (2, 90, 0):
            affect_f = False
            affect_t = True
        else:
            affect_f = 'EDGES'
            affect_t = 'VERTICES'

        if event.ctrl:
            self.add_bevel_modifier(obj, affect_t, 1, 0.2, True, 30, 'HOPS_bevel_d')
        else:
            self.add_bevel_modifier(obj, affect_t, 12, 0.2, True, 30, 'HOPS_bevel_d')
        if (2, 82, 4) < bpy.app.version:
            self.add_weld_modifier(obj, 'HOPS_weld')
        self.add_solidify_modifier(obj, 'HOPS_solidify_z')
        if event.ctrl:
            self.add_bevel_modifier(obj, affect_f, 1, 0.07, True, 60, 'HOPS_bevel_b')
        else:
            self.add_bevel_modifier(obj, affect_f, 1, 0.07, True, 30, 'HOPS_bevel_b')
        if (2, 82, 4) < bpy.app.version:
            self.add_weld_modifier(obj, 'HOPS_weld')
        self.add_bevel_modifier(obj, affect_f, 6, 0.005, False, 30, 'HOPS_bevel_c')
        if get_preferences().behavior.add_WN_to_boolshapes:
            self.add_weighted_modifier(obj, 'HOPS_weighted')
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = math.radians(30)

        # Todo : Resize is problematic so is resize for dots
        # Todo : This needs bC
        if property.bc():
            property.bc().behavior.sort_decimate = False
            # property.bc().behavior.sort_bevel = True
            # property.bc().behavior.sort_last_bevel = True

        return {"FINISHED"}

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

    def add_weighted_modifier(self, object, name='HOPS_weighted'):
        modifier = object.modifiers.new('WeightedNormal', 'WEIGHTED_NORMAL')
        modifier.keep_sharp = True

    def add_weld_modifier(self, object, name='HOPS_weld'):
        if (2, 82, 4) < bpy.app.version:
            modifier = object.modifiers.new('HOPS_weld', 'WELD')
        else:
            pass

    def add_decimate_modifier(self, object, name='HOPS_decimate_c'):
        modifier = object.modifiers.new('Decimate', 'DECIMATE')
        modifier.angle_limit = math.radians(5)
        modifier.decimate_type = 'DISSOLVE'

    def add_bevel_modifier(self, object, affect, segments, width, clamp, angle, name='HOPS_bevel_c'):
        modifier = object.modifiers.new(name=name, type="BEVEL")
        if bpy.app.version < (2, 90, 0):
            modifier.use_only_vertices = affect
        else:
            modifier.affect = affect
        modifier.use_clamp_overlap = clamp
        modifier.limit_method = "ANGLE"
        modifier.angle_limit = math.radians(angle)
        modifier.miter_outer = 'MITER_ARC'
        modifier.width = width
        modifier.profile = .5
        modifier.segments = segments
        modifier.loop_slide = get_preferences().property.bevel_loop_slide

    def add_solidify_modifier(self, object, name='HOPS_solidify_z'):
        solidify_modifier = object.modifiers.new(name, "SOLIDIFY")
        solidify_modifier.thickness = 2
        solidify_modifier.offset = 1
        solidify_modifier.use_even_offset = True
        solidify_modifier.use_quality_normals = True
        solidify_modifier.use_rim_only = False
        solidify_modifier.show_on_cage = True

    def add_displace_modifier(self, object, axis='X', name='HOPS_displace_x'):
        displace_modifier = object.modifiers.new(name=name, type="DISPLACE")
        displace_modifier.direction = axis
        displace_modifier.strength = -1.0

    def add_mirror_modifier(self, object, name='HOPS_mirror'):
        mirror_modifier = object.modifiers.new(name=name, type="MIRROR")
        mirror_modifier.use_axis[0] = True
        mirror_modifier.use_axis[1] = True
        mirror_modifier.use_bisect_axis[0] = True
        mirror_modifier.use_bisect_axis[1] = True
        mirror_modifier.show_render = False
        #mirror_modifier.use_bisect_flip_axis[0] = True
        #mirror_modifier.use_bisect_flip_axis[1] = True

class HOPS_OT_ADD_box(bpy.types.Operator):
    bl_idname = "hops.add_box"
    bl_label = "Add smart Box"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """Create Smart box"""

    def execute(self, context):
        verts = [(-1, -1, 0)]
        obj = bpy.data.objects.new("Cube", bpy.data.meshes.new("Cube"))

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
        self.add_solidify_modifier(obj, 'HOPS_solidify_z')
        if get_preferences().behavior.add_mirror_to_boolshapes:
            self.add_mirror_modifier(obj, 'HOPS_mirror')
        self.add_decimate_modifier(obj, 'HOPS_decimate_c')
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = math.radians(60)

        return {"FINISHED"}

    def add_screw_modifier(self, object, axis='X', name='HOPS_screw_x', flip=False):
        screw_modifier = object.modifiers.new(name=name, type="SCREW")
        screw_modifier.angle = math.radians(0)
        screw_modifier.axis = axis
        screw_modifier.steps = 2
        screw_modifier.render_steps = 2
        screw_modifier.screw_offset = 2
        screw_modifier.iterations = 1
        screw_modifier.use_smooth_shade = False
        screw_modifier.use_merge_vertices = True
        screw_modifier.use_normal_flip = flip

    def add_displace_modifier(self, object, strength, axis='X', name='HOPS_displace_x'):
        displace_modifier = object.modifiers.new(name=name, type="DISPLACE")
        displace_modifier.direction = axis
        displace_modifier.strength = strength

    def add_solidify_modifier(self, object, name='HOPS_solidify_z'):
        solidify_modifier = object.modifiers.new(name, "SOLIDIFY")
        solidify_modifier.thickness = 2
        solidify_modifier.offset = 1
        solidify_modifier.use_even_offset = True
        solidify_modifier.use_quality_normals = True
        solidify_modifier.use_rim_only = False
        solidify_modifier.show_on_cage = True

    def add_mirror_modifier(self, object, name='HOPS_mirror'):
        mirror_modifier = object.modifiers.new(name=name, type="MIRROR")
        mirror_modifier.use_axis[0] = True
        mirror_modifier.use_axis[1] = True
        mirror_modifier.use_bisect_axis[0] = True
        mirror_modifier.use_bisect_axis[1] = True
        # mirror_modifier.use_bisect_flip_axis[1] = True

    def add_decimate_modifier(self, object, name='HOPS_decimate_c'):
        modifier = object.modifiers.new('Decimate', 'DECIMATE')
        modifier.angle_limit = math.radians(5)
        modifier.decimate_type = 'DISSOLVE'
