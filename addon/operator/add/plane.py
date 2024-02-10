import bpy
import math
import bmesh
from .... preferences import get_preferences


class HOPS_OT_ADD_plane(bpy.types.Operator):
    bl_idname = "hops.add_plane"
    bl_label = "Add smart plane"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """Create Smart plane"""


    def execute(self, context):
        verts = [(-1, -1, 0)]
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
        self.add_decimate_modifier(obj, 'HOPS_decimate')
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = math.radians(30)

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


    def add_displace_modifier(self, object, axis='X', name='HOPS_displace_x'):
        displace_modifier = object.modifiers.new(name=name, type="DISPLACE")
        displace_modifier.direction = axis
        displace_modifier.strength = -1.5


    def add_decimate_modifier(self, object, name='HOPS_decimate_c'):
        modifier = object.modifiers.new('Decimate', 'DECIMATE')
        modifier.angle_limit = math.radians(5)
        modifier.decimate_type = 'DISSOLVE'


    def add_mirror_modifier(self, object, name='HOPS_mirror'):
        mirror_modifier = object.modifiers.new(name=name, type="MIRROR")
        mirror_modifier.use_axis[0] = True
        mirror_modifier.use_axis[1] = True
        mirror_modifier.use_bisect_axis[0] = True
        mirror_modifier.use_bisect_axis[1] = True
