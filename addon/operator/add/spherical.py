import bpy
import math
import bmesh
from .... preferences import get_preferences
from ... property.preference import property


class HOPS_OT_ADD_sphere(bpy.types.Operator):
    bl_idname = "hops.add_sphere"
    bl_label = "Add smart Sphere"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """Create Smart Sphere"""

    def execute(self, context):
        verts = [(-1, -1, 0)]
        obj = bpy.data.objects.new("Sphere", bpy.data.meshes.new("Sphere"))

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
        self.add_decimate_modifier(obj, 'HOPS_decimate_c')
        self.add_bevel_modifier(obj, segments=16, width=15, clamp=True, angle=30, profie=0.5, name='HOPS_bevel_c')
        self.add_weld_modifier(obj, 'HOPS_weld')
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = math.radians(60)

        return {"FINISHED"}

    def add_weld_modifier(self, object, name='HOPS_weld'):
        if (2, 82, 4) < bpy.app.version:
            modifier = object.modifiers.new('HOPS_weld', 'WELD')
        else:
            pass

    def add_screw_modifier(self, object, axis='X', name='HOPS_screw_x', flip=False):
        screw_modifier = object.modifiers.new(name=name, type="SCREW")
        screw_modifier.angle = math.radians(0)
        screw_modifier.axis = axis
        screw_modifier.steps = 2
        screw_modifier.render_steps = 2
        screw_modifier.screw_offset = 2
        screw_modifier.iterations = 1
        screw_modifier.use_smooth_shade = True
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

    def add_bevel_modifier(self, object, segments, width, clamp, angle, profie, name='HOPS_bevel_c'):
        modifier = object.modifiers.new(name=name, type="BEVEL")
        if bpy.app.version < (2, 90, 0):
            modifier.use_only_vertices = False
        else:
            modifier.affect = 'EDGES'
        modifier.use_clamp_overlap = clamp
        modifier.limit_method = "ANGLE"
        modifier.angle_limit = math.radians(angle)
        modifier.miter_outer = 'MITER_ARC'
        modifier.width = width
        modifier.profile = profie
        modifier.segments = segments
        modifier.loop_slide = get_preferences().property.bevel_loop_slide
