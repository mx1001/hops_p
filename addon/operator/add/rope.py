import bpy, bmesh, math
from .... preferences import get_preferences
from .... utils.objects import set_active


class HOPS_OT_ADD_rope(bpy.types.Operator):
    bl_idname = 'hops.add_rope'
    bl_label = 'Add Smart Rope'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = '''Creates a Smart Rope
LMB - Regular Smart Rope
SHIFT - Subdivided Smart Rope
CTRL - Alternative Smart Rope'''

    use_subd: bpy.props.BoolProperty(
        name='Use Subdivision',
        description='Add a Subdivision Surface modifier to the rope',
        default=False,
    )

    use_center: bpy.props.BoolProperty(
        name='Use Center',
        description='Thicken the curve and push the surrounding strands out',
        default=False,
    )

    count: bpy.props.IntProperty(
        name='Count',
        description='Amount of strands for this rope',
        default=4,
        min=1, max=1000,
        soft_max=20,
    )


    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'


    def invoke(self, context, event):
        self.use_subd = event.shift
        self.use_center = event.ctrl
        return self.execute(context)


    def execute(self, context):
        active = context.active_object
        rope = self.add_object(context, active, 'Rope', 'Rope Mesh')
        rope_array = self.add_empty(context, rope, 'Rope Array', 'SPHERE', 0.25)
        rope_twist = self.add_empty(context, rope, 'Rope Twist', 'SPHERE', 0.5)
        rope_guide = self.add_curve(context, active, rope, 'Rope Guide', 'Rope Curve')

        thickness_displace = self.add_mod(rope, 'Thickness Displace', 'DISPLACE', direction='X', mid_level=0.0, strength=0.02)
        segments_screw = self.add_mod(rope, 'Segments Screw', 'SCREW', axis='Z', steps=8, render_steps=8, use_merge_vertices=True, merge_threshold=0.001)
        radial_displace = self.add_mod(rope, 'Radial Displace', 'DISPLACE', direction='X', mid_level=(0.0 if self.use_center else 0.55))
        radial_array = self.add_mod(rope, 'Radial Array', 'ARRAY', count=self.count, use_relative_offset=False, use_object_offset=True, offset_object=rope_array)
        extrusion_screw = self.add_mod(rope, 'Extrusion Screw', 'SCREW', axis='Z', steps=2, render_steps=2, use_normal_calculate=True, screw_offset=0.04)
        curve_array = self.add_mod(rope, 'Curve Array', 'ARRAY', fit_type='FIT_CURVE', curve=rope_guide, relative_offset_displace=(0, 0, 1),
            use_object_offset=True, offset_object=rope_twist, use_merge_vertices=True, use_merge_vertices_cap=True, merge_threshold=0.001)
        curve_deform = self.add_mod(rope, 'Curve Deform', 'CURVE', deform_axis='POS_Z', object=rope_guide)
        subdivision = self.add_mod(rope, 'Subdivision', 'SUBSURF', levels=1, render_levels=1) if self.use_subd else None

        self.add_driver_array(rope_array, rope)
        self.add_driver_displace(radial_displace, rope)
        self.add_driver_screw(extrusion_screw, rope_twist)

        rope_array.hide_viewport = True
        rope_twist.rotation_euler[2] = math.radians(15 if self.use_center else 30)
        rope_guide.show_in_front = not self.use_center
        return {'FINISHED'}


    def add_object(self, context, active, obj_name, mesh_name):
        mesh = bpy.data.meshes.new(mesh_name)
        obj = bpy.data.objects.new(obj_name, mesh)
        context.collection.objects.link(obj)

        bm = bmesh.new()
        bm.verts.new((0, 0, 0))
        bm.to_mesh(mesh)
        bm.free()

        if active and active.type == 'CURVE':
            obj.location = active.location
            obj.rotation_euler = active.rotation_euler
            obj.parent = active.parent

        else:
            obj.location = context.scene.cursor.location
            if get_preferences().behavior.cursor_boolshapes:
                obj.rotation_euler = context.scene.cursor.rotation_euler

        set_active(obj, only_select=True)
        self.lock_transforms(obj, only_scale=True)
        return obj


    def add_empty(self, context, parent, name, display, size):
        empty = bpy.data.objects.new(name, None)
        context.collection.objects.link(empty)
        empty.parent = parent

        empty.empty_display_type = display
        empty.empty_display_size = size

        self.lock_transforms(empty, rotation_z=False)
        return empty


    def add_curve(self, context, active, parent, obj_name, curve_name):
        if active and active.type == 'CURVE':
            set_active(active, only_select=True)

            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True, properties=False)
            bpy.ops.object.shade_smooth()

            active.location = (0, 0, 0)
            active.rotation_euler = (0, 0, 0)
            active.scale = (1, 1, 1)

            active.parent = parent
            active.data.bevel_depth = 0.04 if self.use_center else 0

            self.lock_transforms(active)
            return active

        else:
            curve = bpy.data.curves.new(curve_name, 'CURVE')
            spline = curve.splines.new('BEZIER')
            spline.bezier_points.add(1)

            point_one = spline.bezier_points[0]
            point_one.handle_left_type = 'ALIGNED'
            point_one.handle_right_type = 'ALIGNED'

            point_one.co = (-1.0, 0.0, 0.0)
            point_one.handle_left = (-1.5, -0.5, 0.0)
            point_one.handle_right = (-0.5, 0.5, 0.0)

            point_two = spline.bezier_points[1]
            point_two.handle_left_type = 'ALIGNED'
            point_two.handle_right_type = 'ALIGNED'

            point_two.co = (1.0, 0.0, 0.0)
            point_two.handle_left = (0.0, 0.0, 0.0)
            point_two.handle_right = (2.0, 0.0, 0.0)

            curve.dimensions = '3D'
            curve.resolution_u = 128

            obj = bpy.data.objects.new(obj_name, curve)
            context.collection.objects.link(obj)
            obj.parent = parent

            if self.use_center:
                curve.bevel_depth = 0.04

            self.lock_transforms(obj)
            return obj


    def lock_transforms(self, obj, rotation_z=True, only_scale=False):
        obj.lock_scale = (True, True, True)
        if not only_scale:
            obj.lock_location = (True, True, True)
            obj.lock_rotation = (True, True, rotation_z)


    def add_mod(self, obj, name, kind, **kwargs):
        mod = obj.modifiers.new(name=name, type=kind)
        mod.show_expanded = False

        for key, value in kwargs.items():
            setattr(mod, key, value)

        return mod


    def add_driver_array(self, target, source):
        driver = target.driver_add('rotation_euler', 2).driver

        count = driver.variables.new()
        count.name = 'count'

        count.targets[0].id_type = 'OBJECT'
        count.targets[0].id = source
        count.targets[0].data_path = 'modifiers["Radial Array"].count'

        driver.expression = 'radians(360 / count)'


    def add_driver_displace(self, target, source):
        driver = target.driver_add('strength').driver

        strength = driver.variables.new()
        strength.name = 'strength'

        strength.targets[0].id_type = 'OBJECT'
        strength.targets[0].id = source
        strength.targets[0].data_path = 'modifiers["Thickness Displace"].strength'

        count = driver.variables.new()
        count.name = 'count'

        count.targets[0].id_type = 'OBJECT'
        count.targets[0].id = source
        count.targets[0].data_path = 'modifiers["Radial Array"].count'

        driver.expression = '2 * strength / sin(pi / count) if count > 1 else 0'


    def add_driver_screw(self, target, source):
        driver = target.driver_add('angle').driver

        angle = driver.variables.new()
        angle.name = 'angle'

        angle.targets[0].id_type = 'OBJECT'
        angle.targets[0].id = source
        angle.targets[0].data_path = 'rotation_euler[2]'

        driver.expression = 'angle'
