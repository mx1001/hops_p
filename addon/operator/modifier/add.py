
import bpy
import math
from mathutils import Vector
from bpy.props import *
from .... preferences import get_preferences
from .... utility import collections
from .... ui_framework.operator_ui import Master

class HOPS_OT_ADD_MOD_circle_array(bpy.types.Operator):
    bl_idname = "hops.add_mod_circle_array"
    bl_label = "Circle Array Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """LMB - Add Circle Array Modifier
LMB + shift - Call Array Menu
LMB + Ctrl - Use 3D Cursor As Origin

"""

    axis: EnumProperty(name="Mode",
                       description="",
                       items=[('X', "x", "Use x axis"),
                              ('Y', "y", "Use y axis"),
                              ('Z', "z", "Use z axis")],
                       default='X')

    displace_amount: FloatProperty(name="sets amount of displacement",
                                   default=2,
                                   min=-10,
                                   max=20)

    array_count: IntProperty(name="amount of array",
                             default = 3,
                             min = 2,
                             max = 50)

    swap: BoolProperty(name="swap", default=True)


    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    def invoke(self, context, event):
        active = context.active_object
        if event.shift:
            bpy.ops.wm.call_menu(name="HOPS_MT_Tool_array")
            return {"FINISHED"}
        if event.ctrl:
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
            #todo needs to use an empty and rotate around an empty instead preserving origin and scale etc.
        empty = bpy.data.objects.new("empty", None)
        context.collection.objects.link(empty)
        empty.empty_display_size = 0.35
        empty.empty_display_type = 'SPHERE'
        empty.parent = active

        displace = active.modifiers.new(name='Hops array displace', type="DISPLACE")
        displace.direction = self.axis
        if event.ctrl:
            displace.strength = 0
        else:
            displace.strength = self.displace_amount
        displace.space = 'LOCAL'
        displace.mid_level = 0
        displace.show_in_editmode = False
        if event.ctrl:
            displace.show_viewport = False
            displace.show_render = False
        array = active.modifiers.new(name='Array', type="ARRAY")
        array.use_relative_offset = False
        array.use_constant_offset = False
        array.use_object_offset = True
        array.offset_object = empty
        array.count = self.array_count
        array.show_in_editmode = False



        if self.axis == "X":
            if self.swap:
                number = 2
                bracket = '[0]'
                namefix = '1'
            else:
                number = 1
                bracket = '[0]'
                namefix = '2'
            array.relative_offset_displace = Vector((1, 0, 0))
        elif self.axis == "Y":
            if self.swap:
                number = 2
                bracket = '[1]'
                namefix = '3'
            else:
                number = 0
                bracket = '[1]'
                namefix = '4'
            array.relative_offset_displace = Vector((0, 1, 0))
        elif self.axis == "Z":
            if self.swap:
                number = 0
                bracket = '[2]'
                namefix = '5'
            else:
                number = 1
                bracket = '[2]'
                namefix = '6'
            array.relative_offset_displace = Vector((0, 0, 1))

        displace.name = displace.name + namefix
        array.name = array.name + namefix

        driver = empty.driver_add('rotation_euler', number).driver
        driver.type = 'SCRIPTED'

        var = driver.variables.new()
        var.targets[0].id_type = 'OBJECT'
        var.targets[0].id = active.id_data
        var.targets[0].data_path = "modifiers[\"" + array.name + "\"].count"
        var.name = "HopsArray" + namefix

        driver.expression = '6.28319 /' + var.name

        driver2 = active.driver_add("modifiers[\"" + displace.name + "\"].strength").driver
        driver2.type = 'SCRIPTED'

        var = driver2.variables.new()
        var.targets[0].id_type = 'OBJECT'
        var.targets[0].id = active.id_data
        var.targets[0].data_path = "modifiers[\"" + array.name + "\"].relative_offset_displace" + bracket
        var.name = "HopsArrayDisplace" + var.name

        driver2.expression = var.name


        if event.shift:
            return bpy.ops.hops.mod_displace('INVOKE_DEFAULT')

        return {"FINISHED"}


class HOPS_OT_ADD_MOD_array(bpy.types.Operator):
    bl_idname = "hops.add_mod_array"
    bl_label = "Array Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """
LMB - Add Array Modifier
"""

    axis: EnumProperty(name="Mode",
                       description="",
                       items=[('X', "x", "Use x axis"),
                              ('Y', "y", "Use y axis"),
                              ('Z', "z", "Use z axis")],
                       default='X')

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    def execute(self, context):
        selected = [o for o in context.selected_objects if o.type == 'MESH']

        if self.axis is 'X':
            name = 'HOPS_array_x'
            x = 2
            y = 0
            z = 0
        elif self.axis is 'Y':
            name = 'HOPS_array_y'
            x = 0
            y = 2
            z = 0
        elif self.axis is 'Z':
            name = 'HOPS_array_z'
            x = 0
            y = 0
            z = 2

        for obj in selected:
            modifier = obj.modifiers.new(name=name, type="ARRAY")
            modifier.relative_offset_displace[0] = x
            modifier.relative_offset_displace[1] = y
            modifier.relative_offset_displace[2] = z
            modifier.count = 3


        return {"FINISHED"}


class HOPS_OT_ADD_MOD_displace(bpy.types.Operator):
    bl_idname = "hops.add_mod_displace"
    bl_label = "Move Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """
LMB - Add Displace Modifier
"""

    axis: EnumProperty(name="Mode",
                       description="",
                       items=[('X', "x", "Use x axis"),
                              ('Y', "y", "Use y axis"),
                              ('Z', "z", "Use z axis")],
                       default='X')

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    def execute(self, context):
        selected = [o for o in context.selected_objects if o.type == 'MESH']

        if self.axis is 'X':
            name = 'HOPS_displace_x'
        elif self.axis is 'Y':
            name = 'HOPS_displace_y'
        elif self.axis is 'Z':
            name = 'HOPS_displace_z'

        for obj in selected:
            modifier = obj.modifiers.new(name=name, type="DISPLACE")
            modifier.direction = self.axis
            modifier.strength = 0.1
            modifier.space = 'LOCAL'
            modifier.mid_level = 0


        return {"FINISHED"}


class HOPS_OT_ADD_MOD_extrude(bpy.types.Operator):
    bl_idname = "hops.add_mod_extrude"
    bl_label = "Extrude Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """
LMB - Add Screw Modifier for verts/edges extrusion use
"""

    axis: EnumProperty(name="Mode",
                       description="",
                       items=[('X', "x", "Use x axis"),
                              ('Y', "y", "Use y axis"),
                              ('Z', "z", "Use z axis")],
                       default='X')

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    def execute(self, context):
        selected = [o for o in context.selected_objects if o.type == 'MESH']

        if self.axis is 'X':
            name = 'HOPS_screw_x'
        elif self.axis is 'Y':
            name = 'HOPS_screw_y'
        elif self.axis is 'Z':
            name = 'HOPS_screw_z'

        for obj in selected:
            modifier = obj.modifiers.new(name=name, type="SCREW")
            modifier.angle = math.radians(0)
            modifier.axis = self.axis
            modifier.steps = 2
            modifier.render_steps = 2
            modifier.screw_offset = 0.5
            modifier.iterations = 6
            modifier.use_smooth_shade = True
            modifier.use_merge_vertices = True
            modifier.use_normal_flip = False

        return {"FINISHED"}


class HOPS_OT_ADD_MOD_screw(bpy.types.Operator):
    bl_idname = "hops.add_mod_screw"
    bl_label = "Screw Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """
LMB - Add Screw Modifier
"""

    axis: EnumProperty(name="Mode",
                       description="",
                       items=[('X', "x", "Use x axis"),
                              ('Y', "y", "Use y axis"),
                              ('Z', "z", "Use z axis")],
                       default='X')

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    def execute(self, context):
        selected = [o for o in context.selected_objects if o.type == 'MESH']

        if self.axis is 'X':
            name = 'HOPS_screw_x'
        elif self.axis is 'Y':
            name = 'HOPS_screw_y'
        elif self.axis is 'Z':
            name = 'HOPS_screw_z'

        for obj in selected:
            modifier = obj.modifiers.new(name=name, type="SCREW")
            modifier.angle = math.radians(360)
            modifier.axis = self.axis
            modifier.steps = 48
            modifier.render_steps = 48
            modifier.screw_offset = 0
            modifier.iterations = 1
            modifier.use_smooth_shade = True
            modifier.use_merge_vertices = True
            modifier.use_normal_flip = False

        return {"FINISHED"}


class HOPS_OT_ADD_MOD_solidify(bpy.types.Operator):
    bl_idname = "hops.add_mod_solidify"
    bl_label = "Solidify Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """
LMB - Add Solidify Modifier
"""

    axis: EnumProperty(name="Mode",
                       description="",
                       items=[('X', "x", "Use x axis"),
                              ('Y', "y", "Use y axis"),
                              ('Z', "z", "Use z axis"),
                              ('C', "c", "Use y axis")],
                       default='X')

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    def execute(self, context):
        selected = [o for o in context.selected_objects if o.type == 'MESH']

        if self.axis is 'X':
            name = 'HOPS_solidify_x'
        elif self.axis is 'Y':
            name = 'HOPS_solidify_y'
        elif self.axis is 'Z':
            name = 'HOPS_solidify_z'
        elif self.axis is 'C':
            name = 'HOPS_solidify_c'

        for obj in selected:
            modifier = obj.modifiers.new(name, "SOLIDIFY")
            modifier.thickness = 1
            modifier.offset = 1
            modifier.use_even_offset = True
            modifier.use_quality_normals = True
            modifier.use_rim_only = False
            modifier.show_on_cage = True

        return {"FINISHED"}


class HOPS_OT_ADD_MOD_decimate(bpy.types.Operator):
    bl_idname = "hops.add_mod_decimate"
    bl_label = "Add Decimate Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """
LMB - Add Decimate Modifier
"""

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    def execute(self, context):
        selected = [o for o in context.selected_objects if o.type == 'MESH']

        for obj in selected:
            modifier = obj.modifiers.new('Decimate', 'DECIMATE')
            modifier.angle_limit = math.radians(5)
            modifier.decimate_type = 'DISSOLVE'

        return {"FINISHED"}

class HOPS_OT_ADD_MOD_bevel_chamfer(bpy.types.Operator):
    bl_idname = "hops.add_mod_bevel_chamfer"
    bl_label = "Chamfer Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """
LMB - Add 1 step Bevel Modifier
CTrl + LMB - use 60 angle instead of 30
"""

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    def invoke(self, context, event):

        if event.ctrl:
            self.angle = math.radians(60)
        else:
            self.angle = math.radians(30)
        self.execute(context)

        return {"FINISHED"}

    def execute(self, context):
        selected = [o for o in context.selected_objects if o.type == 'MESH']

        for obj in selected:
            modifier = obj.modifiers.new(name="HOPS_bevel_b", type="BEVEL")
            if bpy.app.version < (2, 90, 0):
                modifier.use_only_vertices = False
            else:
                modifier.affect = 'EDGES'
            modifier.limit_method = "ANGLE"
            modifier.angle_limit = self.angle
            modifier.miter_outer = 'MITER_ARC'
            modifier.width = 0.04
            modifier.profile = get_preferences().property.bevel_profile
            modifier.segments = 1
            modifier.loop_slide = get_preferences().property.bevel_loop_slide
            modifier.use_clamp_overlap = False

            #smoothing
            obj.data.use_auto_smooth = True
            obj.data.auto_smooth_angle = math.radians(30)
            for f in obj.data.polygons:
                f.use_smooth = True

        return {"FINISHED"}

class HOPS_OT_ADD_MOD_bevel(bpy.types.Operator):
    bl_idname = "hops.add_mod_bevel"
    bl_label = "Bevel Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """
LMB - Add Bevel w/ Angle 30
CTrl + LMB - use 60 angle instead of 30
"""

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    def invoke(self, context, event):
        if event.ctrl:
            self.angle = math.radians(60)
        else:
            self.angle = math.radians(30)
        self.execute(context)
        return {"FINISHED"}

    def execute(self, context):
        selected = [o for o in context.selected_objects if o.type == 'MESH']

        for obj in selected:
            modifier = obj.modifiers.new(name="HOPS_bevel_c", type="BEVEL")
            if bpy.app.version < (2, 90, 0):
                modifier.use_only_vertices = False
            else:
                modifier.affect = 'EDGES'
            modifier.limit_method = "ANGLE"
            modifier.angle_limit = self.angle
            modifier.miter_outer = 'MITER_ARC'
            modifier.width = 0.02
            modifier.profile = get_preferences().property.bevel_profile
            modifier.segments = 3
            modifier.loop_slide = get_preferences().property.bevel_loop_slide
            modifier.use_clamp_overlap = False

            #smoothing
            obj.data.use_auto_smooth = True
            obj.data.auto_smooth_angle = math.radians(30)
            for f in obj.data.polygons:
                f.use_smooth = True

        return {"FINISHED"}


class HOPS_OT_ADD_MOD_bevel_corners(bpy.types.Operator):
    bl_idname = "hops.add_mod_bevel_corners"
    bl_label = "Bevel Corners Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """
LMB - Add Bevel Corners Modifier with Angle 30
CTrl + LMB - use 60 angle instead of 30
"""

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    def invoke(self, context, event):
        if event.ctrl:
            self.angle = math.radians(60)
        else:
            self.angle = math.radians(30)
        self.execute(context)
        return {"FINISHED"}

    def execute(self, context):
        selected = [o for o in context.selected_objects if o.type == 'MESH']

        for obj in selected:
            modifier = obj.modifiers.new(name="HOPS_bevel_2d", type="BEVEL")
            if bpy.app.version < (2, 90, 0):
                modifier.use_only_vertices = True
            else:
                modifier.affect = 'VERTICES'
            modifier.limit_method = "ANGLE"
            modifier.angle_limit = self.angle
            modifier.miter_outer = 'MITER_ARC'
            modifier.width = 0.4
            modifier.profile = 0.5 #get_preferences().property.bevel_profile
            modifier.segments = 7
            modifier.loop_slide = get_preferences().property.bevel_loop_slide
            modifier.use_clamp_overlap = False
            if bpy.app.version[1] >= 82:
                modifier.use_clamp_overlap = True
                modifier = obj.modifiers.new(name="HOPS_weld_2d", type="WELD")
                modifier.show_render = False



        return {"FINISHED"}


class HOPS_OT_ADD_MOD_wireframe(bpy.types.Operator):
    bl_idname = "hops.add_mod_wireframe"
    bl_label = "Wireframe Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """
LMB - Add Wireframe Modifier
"""

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    def execute(self, context):
        selected = [o for o in context.selected_objects if o.type == 'MESH']

        for obj in selected:
            modifier = obj.modifiers.new(name="HOPS_wireframe_c", type="WIREFRAME")
            modifier.thickness = 0.2
            modifier.use_even_offset = True
            modifier.use_relative_offset = False
            modifier.use_replace = True
            modifier.use_boundary = True

        return {"FINISHED"}


class HOPS_OT_ADD_MOD_triangulate(bpy.types.Operator):
    bl_idname = "hops.add_mod_triangulate"
    bl_label = "Triangulate Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """
LMB - Add triangulate Modifier
"""

    called_ui = False

    def __init__(self):

        HOPS_OT_ADD_MOD_triangulate.called_ui = False

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    def execute(self, context):
        selected = [o for o in context.selected_objects if o.type == 'MESH']

        for obj in selected:
            tri_mod = obj.modifiers.new(name="Triangulate", type="TRIANGULATE")
            tri_mod.min_vertices = 5

        # Operator UI
        if not HOPS_OT_ADD_MOD_triangulate.called_ui:
            HOPS_OT_ADD_MOD_triangulate.called_ui = True

            ui = Master()
            draw_data = [
                ["TRIANGULATE"],
                ["Min Vertices : ", tri_mod.min_vertices]]
            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return {"FINISHED"}


class HOPS_OT_ADD_MOD_subsurf(bpy.types.Operator):
    bl_idname = "hops.add_mod_subsurf"
    bl_label = "Subsurf Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """
LMB - Add Subsurf Modifier
"""

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    def execute(self, context):
        selected = [o for o in context.selected_objects if o.type == 'MESH']

        for obj in selected:
            subsurf_mod = obj.modifiers.new(name="Subdivision", type="SUBSURF")
            # subsurf_mod.subdivision_type = 'SIMPLE'
            subsurf_mod.subdivision_type = 'CATMULL_CLARK'
            subsurf_mod.levels = 2


        return {"FINISHED"}


class HOPS_OT_ADD_MOD_deform(bpy.types.Operator):
    bl_idname = "hops.add_mod_deform"
    bl_label = "Twist Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """
LMB - Add twist Modifier
"""

    axis: EnumProperty(name="Mode",
                       description="",
                       items=[('X', "x", "Use x axis"),
                              ('Y', "y", "Use y axis"),
                              ('Z', "z", "Use z axis")],
                       default='X')

    mode: EnumProperty(name="Mode",
                       description="",
                       items=[('TWIST', "twist", "Use twist axis"),
                              ('BEND', "bend", "Use bend axis"),
                              ('TAPER', "taper", "Use taper axis"),
                              ('STRETCH', "strech", "Use strech axis")],
                       default='TWIST')

    name: StringProperty(name="deform mod name", default='HOPS_twist_x')


    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    def execute(self, context):
        selected = [o for o in context.selected_objects if o.type == 'MESH']

        for obj in selected:
            modifier = obj.modifiers.new(self.name, "SIMPLE_DEFORM")
            # modifier.angle = 0.3
            modifier.factor = 0.3
            modifier.deform_method = self.mode
            # modifier.deform_method = 'BEND'
            # modifier.deform_method = 'TAPER'
            # modifier.deform_method = 'STRETCH'
            modifier.deform_axis = self.axis

        return {"FINISHED"}


class HOPS_OT_ADD_MOD_lattice(bpy.types.Operator):
    bl_idname = "hops.add_mod_lattice"
    bl_label = "Lattice Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """
LMB - Add Lattice Modifier
"""

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    def execute(self, context):
        object = context.active_object
        lattice_object = self.add_lattice_obj(context, object)
        self.add_lattice_modifier(context, object, lattice_object)
        return {"FINISHED"}

    @staticmethod
    def lattice_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "LATTICE"]

    def add_lattice_modifier(self, context, object, lattice_object):
        lattice_modifier = object.modifiers.new(name="Lattice", type="LATTICE")
        lattice_modifier.object = lattice_object
        if context.mode == 'EDIT_MESH':
            vg = object.vertex_groups.new(name='HardOps')
            bpy.ops.object.vertex_group_assign()
            lattice_modifier.vertex_group = vg.name

    def add_lattice_obj(self, context, object):
        lattice_data = bpy.data.lattices.new('lattice')
        lattice_obj = bpy.data.objects.new('lattice', lattice_data)
        collection = collections.find_collection(context, object)
        collection.objects.link(lattice_obj)

        lattice_obj.location = object.location
        lattice_obj.rotation_euler = object.rotation_euler
        lattice_obj.dimensions = object.dimensions

        return lattice_obj

    @staticmethod
    def scale(coordinates):
        x = [coordinate[0] for coordinate in coordinates]
        y = [coordinate[1] for coordinate in coordinates]
        z = [coordinate[2] for coordinate in coordinates]
        minimum = math.Vector((min(x), min(y), min(z)))
        maximum = math.Vector((max(x), max(y), max(z)))
        scale = maximum - minimum

        return scale

        return {"FINISHED"}


class HOPS_OT_ADD_MOD_curve(bpy.types.Operator):
    bl_idname = "hops.add_mod_curve"
    bl_label = "Curve Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """
LMB - Add Curve Modifier
"""

    axis: EnumProperty(name="Mode",
                       description="",
                       items=[('X', "x", "Use x axis"),
                              ('Y', "y", "Use y axis"),
                              ('Z', "z", "Use z axis")],
                       default='X')

    @classmethod
    def poll(cls, context):
        if any(o.type == 'MESH' for o in context.selected_objects) and any(o.type == 'CURVE' for o in context.selected_objects):
            return True

    def execute(self, context):
        selected = [obj for obj in context.selected_objects if obj.type == "MESH"]
        curves = [obj for obj in context.selected_objects if obj.type == "CURVE"]

        for obj in selected:
            obj.location = curves[0].location
            modifier = obj.modifiers.new(name='HOPS_curve', type="CURVE")
            modifier.deform_axis = 'POS_Z'
            modifier.object = curves[0]
            
        bpy.ops.hops.display_notification(info="Curve Modifier Added")
        return {"FINISHED"}


class HOPS_OT_ADD_MOD_weld(bpy.types.Operator):
    bl_idname = "hops.add_mod_weld"
    bl_label = "Weld Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """
LMB - Add Weld Modifier
"""
    weld_amount: bpy.props.FloatProperty(
        name="Weld Level",
        description="Weld Amount",
        default=0.001)

    called_ui = False

    def __init__(self):

        HOPS_OT_ADD_MOD_weld.called_ui = False

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    def draw(self, context):
        self.layout.prop(self, "weld_amount")

    def execute(self, context):
        selected = [obj for obj in context.selected_objects if obj.type == "MESH"]

        if (2, 82, 4) < bpy.app.version:
            for obj in selected:
                self.mod = obj.modifiers.new(name='HOPS_weld', type="WELD")
                self.mod.merge_threshold = self.weld_amount
                obj.data.update()
        else:
            pass

        # Operator UI
        if not HOPS_OT_ADD_MOD_weld.called_ui:
            HOPS_OT_ADD_MOD_weld.called_ui = True

            ui = Master()
            draw_data = [
                ["WELD"],
                ["Weld Threshold : ", self.weld_amount]]
            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return {"FINISHED"}


class HOPS_OT_ADD_MOD_split(bpy.types.Operator):
    bl_idname = "hops.add_mod_split"
    bl_label = "Edge Split Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """
LMB - Add Edge Split Modifier
"""

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    def execute(self, context):
        selected = [obj for obj in context.selected_objects if obj.type == "MESH"]

        for obj in selected:
            obj.modifiers.new(name='HOPS_split', type="EDGE_SPLIT")
            obj.data.update()

        return {"FINISHED"}
