import bpy, bmesh
from . preferences import get_preferences
from bpy.types import PropertyGroup, Operator
from bpy.props import EnumProperty, StringProperty, BoolProperty, FloatProperty, FloatVectorProperty, IntProperty
from .operators.modals.material_scroll import random_principled
import random


class HopsMaterialOptions(PropertyGroup):

    material_mode: EnumProperty(
        name = 'Mode',
        items = [
            ('ALL', 'All', 'Look for all materials'),
            ('OBJECT', 'Object', 'Look for materials on the active object'),
            ('BLANK', 'Blank', 'Create new material oneach cut')],
        default = 'ALL')

    active_material: StringProperty(
        name = 'Select Material',
        description = 'Assign the secondary material for bool operations',
        default = '')

    force: BoolProperty(
        name = 'Force',
        description = 'Force this material as the only material for cutting objects',
        default = True)

    color_prob: FloatProperty(
        name = 'Color Probability',
        description = 'Color Probability',
        default = 0.0,
        min = 0,
        max =1)

def blank_cutting_mat ():
    option = bpy.context.window_manager.Hard_Ops_material_options

    mat_name = random_principled(color_prob=option.color_prob).name

    option.active_material = mat_name

def assign_material(context, obj, replace=False, csplit=False):
    option = context.window_manager.Hard_Ops_material_options
    if option.material_mode == 'BLANK':

        blank_cutting_mat()

    if option.active_material:
        if obj:
            if replace:
                obj.data.materials.clear()
                obj.data.materials.append(bpy.data.materials[option.active_material])

            else:
                prepare(context, option, obj)
                if not csplit:
                    add_material(context, context.active_object, bpy.data.materials[option.active_material])


def prepare(context, option, obj):

    if option.force:
        obj.data.materials.clear()

    obj.data.materials.append(bpy.data.materials[option.active_material])


def add_material(context, obj, mat=None, option=None):

    if not mat and option:
        mat = bpy.materials[option.active_material]

    elif not mat:

        mat = bpy.data.materials.new("Material")

    if mat not in [s.material for s in obj.material_slots]:
        obj.data.materials.append(mat)

    return mat


def add(context, obj, mat=None, mats=[], append=True, viewport=False, view_grayscale=False, view_alpha=False):

    if not append and obj.mode != 'EDIT':

        obj.data.materials.clear()

    if mat:

        obj.data.materials.append(mat)
        index = len(obj.data.materials) -1
        obj.active_material_index = index

        if obj.mode == 'EDIT':
            bm = bmesh.from_edit_mesh(obj.data)
            for f in bm.faces:
                if f.select:
                    f.material_index = index
            bmesh.update_edit_mesh(obj.data)
        if viewport:
            mat.diffuse_color = random_color(view_alpha, view_grayscale)

    elif mats:
        for mat in mats:

            obj.data.materials.append(mat)

            if viewport:
                mat.diffuse_color = random_color(view_alpha, view_grayscale)
        
        obj.active_material_index = len(obj.data.materials) -1

    else:
        mat = add_material(context, obj)
        if viewport:
            mat.diffuse_color = random_color(1.0 if view_alpha else False, view_grayscale)



def clamp_value(value, clamp_min=0.0, clamp_max=1.0):
    return max(min(value, clamp_max), clamp_min)


def random_color(alpha=False, grayscale=False, clamp=False, clamp_min=0.0, clamp_max=0.10):
    color = [0,0,0]

    if not grayscale:
        color[0] = random.randint(1000, 8000) * 0.0001
        color[1] = random.randint(1000, 8000) * 0.0001
        color[2] = random.randint(1000, 8000) * 0.0001

    else:
        value = random.randint(100, 4000) * 0.0001
        color[0] = value
        color[1] = value
        color[2] = value

    if clamp:
        color[0] = clamp_value(color[0], clamp_min, clamp_max)
        color[1] = clamp_value(color[1], clamp_min, clamp_max)
        color[2] = clamp_value(color[2], clamp_min, clamp_max)

    return (*color, random.randint(1000, 9000) * 0.0001 if alpha else 1.0)


class MATERIAL_OT_hops_new(Operator):
    bl_idname = 'material.hops_new'
    bl_label = 'Blank Material'
    bl_description = '''Add a new blank random material

    Ctrl - Unique Material per object
    Shift - Glass Material per object
    Alt - Emission Material per object

    '''
    bl_options = {'REGISTER', 'UNDO'}

    type: EnumProperty(
        name = 'Type',
        description = 'Material type',
        items = [
            ('PRINCIPLED', 'Principled', ''),
            ('GLASS', 'Glass', ''),
            ('EMISSION', 'Emission', ''),
            ('CARPAINT', 'CarPaint', ''),
            ('GENERAL', 'General', ''),
        ],
        default = 'PRINCIPLED',
    )

    unique: BoolProperty(
        name = 'Unique Material',
        description = 'Give unique material per object',
        default = False,
    )

    pulse: BoolProperty(
        name = 'Pulse',
        description = 'Give a pulsing material',
        default = True,
    )

    frequency: FloatProperty(
        name = 'Frequency',
        description = 'Control pulse frequency',
        min = 0.01,
        soft_max = 2.0,
        default = 1.0,
    )

    grayscale: BoolProperty(
        name = 'grayscale',
        description = 'Randomize values and not color',
        default = True,
    )

    colorize: BoolProperty(
        name = 'colorize',
        description = 'Mix an RGB Color in for varying shades of color',
        default = False,
    )

    clearcoat: BoolProperty(
        name = 'clearcoat',
        description = "Whether or not to have random clearcoats included",
        default = False,
    )

    colorize_rgb: FloatVectorProperty(
        name = 'colorize_rgb',
        description = 'RGB Color to mixin for colorize',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.785, 0.276225, 0.123828, 1.0),
    )

    clamp: BoolProperty(
        name = 'Clamp',
        description = 'Clamp Min/Max Grayscale Values',
        default = True,
    )

    clamp_expand: BoolProperty(
        name = 'Expand Clamp',
        description = 'Expand Advanced Clamp Options',
        default = False,
    )

    clamp_min_nonmetals: FloatProperty(
        name = 'Min Clamp Value (non-metals)',
        description = 'Minimum Clamp Value for non-metals',
        min = 0.0,
        soft_max = 1.0,
        default = 0.0,
    )

    clamp_max_nonmetals: FloatProperty(
        name = 'Max Clamp Value (non-metals)',
        description = 'Maximum Clamp Value for non-metals',
        min = 0.0,
        soft_max = 1.0,
        default = 0.10,
    )

    clamp_min_metals: FloatProperty(
        name = 'Min Clamp Value (metals)',
        description = 'Minimum Clamp Value for metals',
        min = 0.0,
        soft_max = 1.0,
        default = 0.0,
    )

    clamp_max_metals: FloatProperty(
        name = 'Max Clamp Value (metals)',
        description = 'Maximum Clamp Value for metals',
        min = 0.0,
        soft_max = 1.0,
        default = 0.50,
    )

    ### BEGIN rampbased variables
    rampbased_ramp_start: FloatVectorProperty(
        name = 'rampbased_ramp_start',
        description = 'RGB Color to Start Ramp at',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.03, 0.03, 0.03, 1.0),
    )

    rampbased_ramp_end: FloatVectorProperty(
        name = 'rampbased_ramp_end',
        description = 'RGB Color to End Ramp at',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.25, 0.25, 0.25, 1.0),
    )

    rampbased_ramp_spread: FloatProperty(
        name = 'rampbased_ramp_spread',
        description = 'Ramp Spread Distance',
        min = 0.0,
        soft_max = 1.0,
        default = 0.4,
    )

    rampbased_roughness_min: FloatProperty(
        name = 'rampbased_roughness_min',
        description = 'Minimum roughness',
        min = 0.0,
        max = 1.0,
        default = 0.15,
    )

    rampbased_roughness_max: FloatProperty(
        name = 'rampbased_roughness_max',
        description = 'Maximum roughness',
        min = 0.0,
        max = 1.0,
        default = 0.40,
    )

    rampbased_metal_probability: FloatProperty(
        name = 'rampbased_metal_probability',
        description = 'Metal Probability',
        min = 0.0,
        max = 100.0,
        default = 85.0,
        subtype = 'PERCENTAGE',
    )

    rampbased_clearcoat_probability: FloatProperty(
        name = 'rampbased_metal_probability',
        description = 'Clearcoat Probability',
        min = 0.0,
        max = 100.0,
        default = 20.0,
        subtype = 'PERCENTAGE',
    )

    rampbased_carpaint_probability: FloatProperty(
        name = 'rampbased_carpaint_probability',
        description = 'Car Paint Probability',
        min = 0.0,
        max = 100.0,
        default = 0.0,
        subtype = 'PERCENTAGE',
    )

    rampbased_carpaint_metallic: BoolProperty(
        name = 'rampbased_carpaint_metallic',
        description = 'Carpaint Metallic',
        default = True,
    )

    carpaint_hue_shift: FloatProperty(
        name = 'carpaint_hue_shift',
        description = 'Car Paint Hue Shift',
        min = 0.0,
        max = 1.0,
        default = 0.8,
    )

    carpaint_hue_variation: FloatProperty(
        name = 'carpaint_hue_variation',
        description = 'Carpaint Hue Variation',
        min = 0.0,
        max = 100.0,
        default = 0.0,
        subtype = 'PERCENTAGE',
    )

    carpaint_saturation: FloatProperty(
        name = 'carpaint_saturation',
        description = 'Carpaint Saturation',
        min = 0.0,
        max = 1.0,
        default = 1.0,
    )

    carpaint_value_brightness: FloatProperty(
        name = 'carpaint_value_brightness',
        description = 'Carpaint Brightness',
        min = 0.0,
        max = 1.0,
        default = 0.3,
    )

    carpaint_expand_advanced: BoolProperty(
        name = 'carpaint_expand_advanced',
        description = 'Expand Advanced Carpaint Options',
        default = False,
    )

    carpaint_colorramp_start_color: FloatVectorProperty(
        name = 'carpaint_colorramp_start_color',
        description = 'RGB Color to start Carpaint Ramp',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.553429, 0.151442, 0.051457, 1.000000),
    )

    carpaint_colorramp_end_color: FloatVectorProperty(
        name = 'carpaint_colorramp_end_color',
        description = 'RGB Color to end Carpaint Ramp',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (1.000000, 0.023302, 0.014752, 1.000000),
    )

    carpaint_roughness_scale: FloatProperty(
        name = 'carpaint_roughness_scale',
        description = 'Car Paint Roughness Scale',
        min = 0.0,
        max = 30000.0,
        default = 4000.0,
    )

    carpaint_roughness_ramp_start: FloatVectorProperty(
        name = 'carpaint_roughness_ramp_start',
        description = 'Carpaint Roughness Start',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.05, 0.05, 0.05, 1.000000),
    )

    carpaint_roughness_ramp_end: FloatVectorProperty(
        name = 'carpaint_roughness_ramp_end',
        description = 'Carpaint Roughness Start',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.75, 0.75, 0.75, 1.000000),
    )
    ### END rampbased variables

    cleanup: BoolProperty(
        name = 'Remove Zero User Materials',
        description = 'Remove Zero User Materials',
        default = True,
    )

    helper_call: BoolProperty(
        name = 'Call from HOPS helper',
        description = 'Internal helper',
        default = False,
    )

    bevel_shader: BoolProperty(
        name = 'Bevel Shader',
        description = 'Add Bevel Shader node. Requires Cycles to do anything',
        default = False,
    )

    bevel_shader_radius: FloatProperty(
        name = 'Radius',
        description = 'Radius value. Or whatever it means to blender',
        default = 0.015,
    )

    bevel_shader_samples: IntProperty(
        name = 'Samples',
        description = 'Number of samples ',
        default =4,
    )


    @staticmethod
    def new(name='Material', blend_method='OPAQUE'):
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True

        mat.blend_method = blend_method

        return mat


    @staticmethod
    def new_node(tree, x=300, y=300, bl_idname='ShaderNodeOutputMaterial'):
        new = tree.nodes.new(type=bl_idname)
        new.location.x = x
        new.location.y = y

        return new
        # return tree.nodes.new(type=bl_idname)


    @staticmethod
    def node(tree, bl_idname='ShaderNodeOutputMaterial', index=-1, name=None):
        nodes = [node for node in tree.nodes if node.bl_idname == bl_idname]
        if name:
            for node in nodes:
                if node.name == name:
                    return node

        node = nodes[index] if nodes else None

        return node


    @staticmethod
    def socket(node, type='outputs', socket_type='SHADER', index=0, path_id=''):
        socket = [socket for socket in getattr(node, type) if socket.type == socket_type][index]

        if not path_id:
            return socket

        else:
            return socket.path_from_id(path_id)


    def socket_connect(self, tree, node_from, node_to, index_from=0, index_to=0, socket_type='SHADER', socket_to_type=''):
        socket_out = self.socket(node_from, socket_type=socket_type, index=index_from)
        socket_in = self.socket(node_to, type='inputs', socket_type=socket_type if not socket_to_type else socket_to_type, index=index_to)

        tree.links.new(socket_out, socket_in)


    def connected_nodes(self, node, nodes):
        if not node:
            return []

        for socket in node.inputs:
            if socket.is_linked:
                self.connected_nodes(socket.links[0].from_node, nodes)

        if node not in nodes:
            nodes.append(node)

        return nodes


    def principled(self, tree, clear=True):
        output = self.node(tree)
        principled = self.node(tree, bl_idname='ShaderNodeBsdfPrincipled')
        rgb_picker = self.node(tree, bl_idname='ShaderNodeRGB')
        rgb_mix_node = self.node(tree, bl_idname='ShaderNodeMixRGB')

        if not principled:
            principled = self.new_node(tree,
                bl_idname = 'ShaderNodeBsdfPrincipled',
                x = output.location.x-180,
                y = output.location.y)

            self.socket_connect(tree, principled, output)

        if self.colorize:
            if not rgb_mix_node:
                rgb_mix_node = self.new_node(tree,
                    bl_idname = 'ShaderNodeMixRGB',
                    x = output.location.x-460,
                    y = output.location.y,
                )
                self.socket_connect(tree, rgb_mix_node, principled, socket_type='RGBA')
            if not rgb_picker:
                rgb_picker = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeRGB',
                    x = output.location.x-620,
                    y = output.location.y,
                )
                rgb_picker.outputs[0].default_value = self.colorize_rgb
                self.socket_connect(tree, rgb_picker, rgb_mix_node, socket_type='RGBA')

        if not clear:

            metallic = principled.inputs[4]
            metallic.default_value = round(random.uniform(0.4, 0.99), 0)

            color = principled.inputs[0]
            if self.clamp:
                if metallic.default_value == 1.0:
                    tmp_clamp_min = self.clamp_min_metals
                    tmp_clamp_max = self.clamp_max_metals
                else:
                    tmp_clamp_min = self.clamp_min_nonmetals
                    tmp_clamp_max = self.clamp_max_nonmetals


                color.default_value = random_color(
                    grayscale=self.grayscale,
                    clamp=self.clamp,
                    clamp_min=tmp_clamp_min,
                    clamp_max=tmp_clamp_max,
                )
            else:
                color.default_value = random_color(
                    grayscale=self.grayscale,
                    clamp=self.clamp,
                )
            if self.colorize:
                # here we set the random grayscale in the mixRGB Color2
                rgb_mix_node.inputs[2].default_value = color.default_value

            roughness = principled.inputs[7]
            roughness.default_value = random.uniform(0.1, 0.6)

            clearcoat = principled.inputs[12]
            if self.clearcoat:
                clearcoat.default_value = random.randint(0, 1)
            else:
                clearcoat.default_value = 0

            if self.bevel_shader:
                bevel = tree.nodes.new('ShaderNodeBevel')

                bevel.location = (-170, -170)

                bevel.samples = self.bevel_shader_samples
                bevel.inputs['Radius'].default_value = self.bevel_shader_radius
                tree.links.new(bevel.outputs[0], principled.inputs['Normal'])
                

            return

        if principled:
            tree.nodes.remove(principled)


    def carpaint(self, tree, clear=True):
        output = self.node(tree)
        principled_carpaint = self.node(tree, bl_idname='ShaderNodeBsdfPrincipled')
        carpaint_ramp = self.node(tree, bl_idname='ShaderNodeValToRGB', name='carpaint_ramp')
        carpaint_rgb_to_bw = self.node(tree, bl_idname='ShaderNodeRGBToBW', name='carpaint_rgb_to_bw')
        carpaint_round = self.node(tree, bl_idname='ShaderNodeMath', name='carpaint_round')
        carpaint_hsv = self.node(tree, bl_idname='ShaderNodeHueSaturation', name='carpaint_hsv')
        carpaint_shift_mix = self.node(tree, bl_idname='ShaderNodeMixRGB', name='carpaint_shift_mix')
        carpaint_shift_value = self.node(tree, bl_idname='ShaderNodeValue', name='carpaint_shift_value')
        carpaint_shift_ramp = self.node(tree, bl_idname='ShaderNodeValToRGB', name='carpaint_shift_ramp')
        object_info = self.node(tree, bl_idname='ShaderNodeObjectInfo', name='object_info')
        carpaint_colorramp = self.node(tree, bl_idname='ShaderNodeValToRGB', name='carpaint_colorramp')
        carpaint_layerweight = self.node(tree, bl_idname='ShaderNodeLayerWeight', name='carpaint_layerweight')
        carpaint_roughness_rgb_to_bw = self.node(tree, bl_idname='ShaderNodeRGBToBW', name='carpaint_roughness_rgb_to_bw')
        carpaint_roughness_ramp = self.node(tree, bl_idname='ShaderNodeValToRGB', name='carpaint_roughness_ramp')
        carpaint_roughness_voronoi = self.node(tree, bl_idname='ShaderNodeTexVoronoi', name='carpaint_roughness_voronoi')
        tex_coord = self.node(tree, bl_idname='ShaderNodeTexCoord', name='tex_coord')
        carpaint_metallic_value = self.node(tree, bl_idname='ShaderNodeValue', name='carpaint_metallic_value')

        self.carpaint_hue_shift = random.uniform(0,1)

        if not clear:
            # CARPAINT BEGIN
            if not principled_carpaint:
                principled_carpaint = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeBsdfPrincipled',
                    x = output.location.x,
                    y = output.location.y-400,
                )
                principled_carpaint.name = 'principled_carpaint'
                principled_carpaint.label = 'principled_carpaint'
            self.socket_connect(tree, principled_carpaint, output, 0, 0, socket_type='SHADER')
            principled_carpaint.inputs[12].default_value = 1.0 # set clearcoat
            principled_carpaint.inputs[12].default_value = 0.05 # set clearcoat roughness

            if not carpaint_metallic_value:
                carpaint_metallic_value = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeValue',
                    x = principled_carpaint.location.x-275,
                    y = principled_carpaint.location.y-300,
                )
                carpaint_metallic_value.name = 'carpaint_metallic_value'
                carpaint_metallic_value.label = 'carpaint_metallic_value'
            self.socket_connect(tree, carpaint_metallic_value, principled_carpaint, 0, 1, socket_type='VALUE')
            if self.rampbased_carpaint_metallic:
                carpaint_metallic_value.outputs[0].default_value = 1.0
            else:
                carpaint_metallic_value.outputs[0].default_value = 0.0

            if not carpaint_hsv:
                carpaint_hsv = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeHueSaturation',
                    x = principled_carpaint.location.x-275,
                    y = principled_carpaint.location.y,
                )
                carpaint_hsv.name = 'carpaint_hsv'
                carpaint_hsv.label = 'carpaint_hsv'
            self.socket_connect(tree, carpaint_hsv, principled_carpaint, 0, 0, socket_type='RGBA')
            carpaint_hsv.inputs['Hue'].default_value = self.carpaint_hue_shift
            carpaint_hsv.inputs['Saturation'].default_value = self.carpaint_saturation
            carpaint_hsv.inputs['Value'].default_value = self.carpaint_value_brightness

            if not carpaint_shift_mix:
                carpaint_shift_mix = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeMixRGB',
                    x = carpaint_hsv.location.x-275,
                    y = carpaint_hsv.location.y-300,
                )
                carpaint_shift_mix.name = 'carpaint_shift_mix'
                carpaint_shift_mix.label = 'carpaint_shift_mix'
            self.socket_connect(tree, carpaint_shift_mix, carpaint_hsv, 0, 0, socket_type='RGBA', socket_to_type='VALUE')
            carpaint_shift_mix.inputs['Fac'].default_value = self.carpaint_hue_variation / 100.0

            if not carpaint_shift_value:
                carpaint_shift_value = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeValue',
                    x = carpaint_shift_mix.location.x-275,
                    y = carpaint_shift_mix.location.y+100,
                )
                carpaint_shift_value.name = 'carpaint_shift_value'
                carpaint_shift_value.label = 'carpaint_shift_value'
            self.socket_connect(tree, carpaint_shift_value, carpaint_shift_mix, 0, 0, socket_type='VALUE', socket_to_type='RGBA')
            carpaint_shift_value.outputs[0].default_value = self.carpaint_hue_shift

            if not carpaint_shift_ramp:
                carpaint_shift_ramp = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeValToRGB',
                    x = carpaint_shift_value.location.x-275,
                    y = carpaint_shift_value.location.y-100,
                )
                carpaint_shift_ramp.name = 'carpaint_shift_ramp'
                carpaint_shift_ramp.label = 'carpaint_shift_ramp'
            self.socket_connect(tree, carpaint_shift_ramp, carpaint_shift_mix, 0, 1, socket_type='RGBA')

            if not object_info:
                object_info = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeObjectInfo',
                    x = carpaint_shift_ramp.location.x-250,
                    y = carpaint_shift_ramp.location.y,
                )
                object_info.name = 'object_info'
                object_info.label = 'object_info'
            self.socket_connect(tree, object_info, carpaint_shift_ramp, 2, 0, socket_type='VALUE')

            if not carpaint_colorramp:
                carpaint_colorramp = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeValToRGB',
                    x = carpaint_hsv.location.x-275,
                    y = carpaint_hsv.location.y,
                )
                carpaint_colorramp.name = 'carpaint_colorramp'
                carpaint_colorramp.label = 'carpaint_colorramp'
            self.socket_connect(tree, carpaint_colorramp, carpaint_hsv, 0, 0, socket_type='RGBA')
            carpaint_colorramp.color_ramp.elements[0].color = self.carpaint_colorramp_start_color
            carpaint_colorramp.color_ramp.elements[1].color = self.carpaint_colorramp_end_color
            carpaint_colorramp.color_ramp.elements[1].position = 0.80

            if not carpaint_layerweight:
                carpaint_layerweight = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeLayerWeight',
                    x = carpaint_colorramp.location.x-275,
                    y = carpaint_colorramp.location.y,
                )
                carpaint_layerweight.name = 'carpaint_layerweight'
                carpaint_layerweight.label = 'carpaint_layerweight'
            self.socket_connect(tree, carpaint_layerweight, carpaint_colorramp, 1, 0, socket_type='VALUE')

            if not carpaint_roughness_rgb_to_bw:
                carpaint_roughness_rgb_to_bw = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeRGBToBW',
                    x = principled_carpaint.location.x-275,
                    y = principled_carpaint.location.y-600,
                )
                carpaint_roughness_rgb_to_bw.name = 'carpaint_roughness_rgb_to_bw'
                carpaint_roughness_rgb_to_bw.label = 'carpaint_roughness_rgb_to_bw'
            self.socket_connect(tree, carpaint_roughness_rgb_to_bw, principled_carpaint, 0, 4, socket_type='VALUE')

            if not carpaint_roughness_ramp:
                carpaint_roughness_ramp = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeValToRGB',
                    x = carpaint_roughness_rgb_to_bw.location.x-300,
                    y = carpaint_roughness_rgb_to_bw.location.y,
                )
                carpaint_roughness_ramp.name = 'carpaint_roughness_ramp'
                carpaint_roughness_ramp.label = 'carpaint_roughness_ramp'
            self.socket_connect(tree, carpaint_roughness_ramp, carpaint_roughness_rgb_to_bw, 0, 0, socket_type='RGBA')
            carpaint_roughness_ramp.color_ramp.elements[0].color = self.carpaint_roughness_ramp_start
            carpaint_roughness_ramp.color_ramp.elements[1].color = self.carpaint_roughness_ramp_end

            if not carpaint_roughness_voronoi:
                carpaint_roughness_voronoi = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeTexVoronoi',
                    x = carpaint_roughness_ramp.location.x-300,
                    y = carpaint_roughness_ramp.location.y,
                )
                carpaint_roughness_voronoi.name = 'carpaint_roughness_voronoi'
                carpaint_roughness_voronoi.label = 'carpaint_roughness_voronoi'
            self.socket_connect(
                tree,
                carpaint_roughness_voronoi,
                carpaint_roughness_ramp,
                0,
                0,
                socket_type='RGBA',
                socket_to_type='VALUE'
            )
            carpaint_roughness_voronoi.voronoi_dimensions = '4D'
            carpaint_roughness_voronoi.feature = 'F1'
            carpaint_roughness_voronoi.distance = 'EUCLIDEAN'
            carpaint_roughness_voronoi.inputs['Scale'].default_value = self.carpaint_roughness_scale

            if not tex_coord:
                tex_coord = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeTexCoord',
                    x = carpaint_roughness_voronoi.location.x-300,
                    y = carpaint_roughness_voronoi.location.y,
                )
                tex_coord.name = 'tex_coord'
                tex_coord.label = 'tex_coord'
            self.socket_connect(tree, tex_coord, carpaint_roughness_voronoi, 3, 0, socket_type='VECTOR')
            # CARPAINT END
            return

        if principled_carpaint:
            tree.nodes.remove(principled_carpaint)


    def general(self, tree, clear=True):
        output = self.node(tree)
        final_mix_shader = self.node(tree, bl_idname='ShaderNodeMixShader', name='final_mix_shader')
        principled = self.node(tree, bl_idname='ShaderNodeBsdfPrincipled')
        principled_carpaint = self.node(tree, bl_idname='ShaderNodeBsdfPrincipled')
        basecolor_ramp = self.node(tree, bl_idname='ShaderNodeValToRGB', name='basecolor_ramp')
        roughness_ramp = self.node(tree, bl_idname='ShaderNodeValToRGB', name='roughness_ramp')
        roughness_rgb_to_bw = self.node(tree, bl_idname='ShaderNodeRGBToBW', name='roughness_rgb_to_bw')
        carpaint_ramp = self.node(tree, bl_idname='ShaderNodeValToRGB', name='carpaint_ramp')
        carpaint_rgb_to_bw = self.node(tree, bl_idname='ShaderNodeRGBToBW', name='carpaint_rgb_to_bw')
        carpaint_round = self.node(tree, bl_idname='ShaderNodeMath', name='carpaint_round')
        carpaint_hsv = self.node(tree, bl_idname='ShaderNodeHueSaturation', name='carpaint_hsv')
        carpaint_shift_mix = self.node(tree, bl_idname='ShaderNodeMixRGB', name='carpaint_shift_mix')
        carpaint_shift_value = self.node(tree, bl_idname='ShaderNodeValue', name='carpaint_shift_value')
        carpaint_shift_ramp = self.node(tree, bl_idname='ShaderNodeValToRGB', name='carpaint_shift_ramp')
        carpaint_colorramp = self.node(tree, bl_idname='ShaderNodeValToRGB', name='carpaint_colorramp')
        carpaint_layerweight = self.node(tree, bl_idname='ShaderNodeLayerWeight', name='carpaint_layerweight')
        carpaint_roughness_rgb_to_bw = self.node(tree, bl_idname='ShaderNodeRGBToBW', name='carpaint_roughness_rgb_to_bw')
        carpaint_roughness_ramp = self.node(tree, bl_idname='ShaderNodeValToRGB', name='carpaint_roughness_ramp')
        carpaint_roughness_voronoi = self.node(tree, bl_idname='ShaderNodeTexVoronoi', name='carpaint_roughness_voronoi')
        tex_coord = self.node(tree, bl_idname='ShaderNodeTexCoord', name='tex_coord')
        carpaint_metallic_value = self.node(tree, bl_idname='ShaderNodeValue', name='carpaint_metallic_value')
        metal_ramp = self.node(tree, bl_idname='ShaderNodeValToRGB', name='metal_ramp')
        metal_rgb_to_bw = self.node(tree, bl_idname='ShaderNodeRGBToBW', name='metal_rgb_to_bw')
        metal_round = self.node(tree, bl_idname='ShaderNodeMath', name='metal_round')
        clearcoat_ramp = self.node(tree, bl_idname='ShaderNodeValToRGB', name='metal_ramp')
        clearcoat_rgb_to_bw = self.node(tree, bl_idname='ShaderNodeRGBToBW', name='metal_rgb_to_bw')
        clearcoat_round = self.node(tree, bl_idname='ShaderNodeMath', name='metal_round')
        colorize_rgb_picker = self.node(tree, bl_idname='ShaderNodeRGB', name='colorize_rgb_picker')
        colorize_rgb_mix_node = self.node(tree, bl_idname='ShaderNodeMixRGB', name='colorize_rgb_mix_node')
        object_info = self.node(tree, bl_idname='ShaderNodeObjectInfo', name='object_info')

        if not clear:
            # Mix Shader
            if not final_mix_shader:
                final_mix_shader = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeMixShader',
                    x = output.location.x-250,
                    y = output.location.y,
                )
                final_mix_shader.name = 'final_mix_shader'
                final_mix_shader.label = 'final_mix_shader'
            self.socket_connect(tree, final_mix_shader, output)

            # Primary Hard Surface Shader
            if not principled:
                principled = self.new_node(tree,
                    bl_idname = 'ShaderNodeBsdfPrincipled',
                    x = output.location.x-1400,
                    y = output.location.y,
                )
                principled.name = 'principled'
                principled.label = 'principled'
            principled.location.x = output.location.x-1400
            principled.location.y = output.location.y
            self.socket_connect(tree, principled, final_mix_shader, 0, 0, socket_type='SHADER')

            # CARPAINT BEGIN
            if not principled_carpaint:
                principled_carpaint = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeBsdfPrincipled',
                    x = principled.location.x,
                    y = principled.location.y-1400,
                )
                principled_carpaint.name = 'principled_carpaint'
                principled_carpaint.label = 'principled_carpaint'
            self.socket_connect(tree, principled_carpaint, final_mix_shader, 0, 1, socket_type='SHADER')
            principled_carpaint.inputs[12].default_value = 1.0 # set clearcoat
            principled_carpaint.inputs[12].default_value = 0.05 # set clearcoat roughness

            if not carpaint_metallic_value:
                carpaint_metallic_value = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeValue',
                    x = principled_carpaint.location.x-275,
                    y = principled_carpaint.location.y-300,
                )
                carpaint_metallic_value.name = 'carpaint_metallic_value'
                carpaint_metallic_value.label = 'carpaint_metallic_value'
            self.socket_connect(tree, carpaint_metallic_value, principled_carpaint, 0, 1, socket_type='VALUE')
            if self.rampbased_carpaint_metallic:
                carpaint_metallic_value.outputs[0].default_value = 1.0
            else:
                carpaint_metallic_value.outputs[0].default_value = 0.0

            if not carpaint_hsv:
                carpaint_hsv = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeHueSaturation',
                    x = principled_carpaint.location.x-275,
                    y = principled_carpaint.location.y,
                )
                carpaint_hsv.name = 'carpaint_hsv'
                carpaint_hsv.label = 'carpaint_hsv'
            self.socket_connect(tree, carpaint_hsv, principled_carpaint, 0, 0, socket_type='RGBA')
            carpaint_hsv.inputs['Hue'].default_value = self.carpaint_hue_shift
            carpaint_hsv.inputs['Saturation'].default_value = self.carpaint_saturation
            carpaint_hsv.inputs['Value'].default_value = self.carpaint_value_brightness

            if not carpaint_shift_mix:
                carpaint_shift_mix = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeMixRGB',
                    x = carpaint_hsv.location.x-275,
                    y = carpaint_hsv.location.y-300,
                )
                carpaint_shift_mix.name = 'carpaint_shift_mix'
                carpaint_shift_mix.label = 'carpaint_shift_mix'
            self.socket_connect(tree, carpaint_shift_mix, carpaint_hsv, 0, 0, socket_type='RGBA', socket_to_type='VALUE')
            carpaint_shift_mix.inputs['Fac'].default_value = self.carpaint_hue_variation / 100.0

            if not carpaint_shift_value:
                carpaint_shift_value = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeValue',
                    x = carpaint_shift_mix.location.x-275,
                    y = carpaint_shift_mix.location.y+100,
                )
                carpaint_shift_value.name = 'carpaint_shift_value'
                carpaint_shift_value.label = 'carpaint_shift_value'
            self.socket_connect(tree, carpaint_shift_value, carpaint_shift_mix, 0, 0, socket_type='VALUE', socket_to_type='RGBA')
            carpaint_shift_value.outputs[0].default_value = self.carpaint_hue_shift

            if not carpaint_shift_ramp:
                carpaint_shift_ramp = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeValToRGB',
                    x = carpaint_shift_value.location.x-275,
                    y = carpaint_shift_value.location.y-100,
                )
                carpaint_shift_ramp.name = 'carpaint_shift_ramp'
                carpaint_shift_ramp.label = 'carpaint_shift_ramp'
            self.socket_connect(tree, carpaint_shift_ramp, carpaint_shift_mix, 0, 1, socket_type='RGBA')

            if not carpaint_colorramp:
                carpaint_colorramp = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeValToRGB',
                    x = carpaint_hsv.location.x-275,
                    y = carpaint_hsv.location.y,
                )
                carpaint_colorramp.name = 'carpaint_colorramp'
                carpaint_colorramp.label = 'carpaint_colorramp'
            self.socket_connect(tree, carpaint_colorramp, carpaint_hsv, 0, 0, socket_type='RGBA')
            carpaint_colorramp.color_ramp.elements[0].color = self.carpaint_colorramp_start_color
            carpaint_colorramp.color_ramp.elements[1].color = self.carpaint_colorramp_end_color
            carpaint_colorramp.color_ramp.elements[1].position = 0.80

            if not carpaint_layerweight:
                carpaint_layerweight = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeLayerWeight',
                    x = carpaint_colorramp.location.x-275,
                    y = carpaint_colorramp.location.y,
                )
                carpaint_layerweight.name = 'carpaint_layerweight'
                carpaint_layerweight.label = 'carpaint_layerweight'
            self.socket_connect(tree, carpaint_layerweight, carpaint_colorramp, 1, 0, socket_type='VALUE')

            if not carpaint_roughness_rgb_to_bw:
                carpaint_roughness_rgb_to_bw = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeRGBToBW',
                    x = principled_carpaint.location.x-275,
                    y = principled_carpaint.location.y-600,
                )
                carpaint_roughness_rgb_to_bw.name = 'carpaint_roughness_rgb_to_bw'
                carpaint_roughness_rgb_to_bw.label = 'carpaint_roughness_rgb_to_bw'
            self.socket_connect(tree, carpaint_roughness_rgb_to_bw, principled_carpaint, 0, 4, socket_type='VALUE')

            if not carpaint_roughness_ramp:
                carpaint_roughness_ramp = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeValToRGB',
                    x = carpaint_roughness_rgb_to_bw.location.x-300,
                    y = carpaint_roughness_rgb_to_bw.location.y,
                )
                carpaint_roughness_ramp.name = 'carpaint_roughness_ramp'
                carpaint_roughness_ramp.label = 'carpaint_roughness_ramp'
            self.socket_connect(tree, carpaint_roughness_ramp, carpaint_roughness_rgb_to_bw, 0, 0, socket_type='RGBA')
            carpaint_roughness_ramp.color_ramp.elements[0].color = self.carpaint_roughness_ramp_start
            carpaint_roughness_ramp.color_ramp.elements[1].color = self.carpaint_roughness_ramp_end

            if not carpaint_roughness_voronoi:
                carpaint_roughness_voronoi = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeTexVoronoi',
                    x = carpaint_roughness_ramp.location.x-300,
                    y = carpaint_roughness_ramp.location.y,
                )
                carpaint_roughness_voronoi.name = 'carpaint_roughness_voronoi'
                carpaint_roughness_voronoi.label = 'carpaint_roughness_voronoi'
            self.socket_connect(
                tree,
                carpaint_roughness_voronoi,
                carpaint_roughness_ramp,
                0,
                0,
                socket_type='RGBA',
                socket_to_type='VALUE'
            )
            carpaint_roughness_voronoi.voronoi_dimensions = '4D'
            carpaint_roughness_voronoi.feature = 'F1'
            carpaint_roughness_voronoi.distance = 'EUCLIDEAN'
            carpaint_roughness_voronoi.inputs['Scale'].default_value = self.carpaint_roughness_scale

            if not tex_coord:
                tex_coord = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeTexCoord',
                    x = carpaint_roughness_voronoi.location.x-300,
                    y = carpaint_roughness_voronoi.location.y,
                )
                tex_coord.name = 'tex_coord'
                tex_coord.label = 'tex_coord'
            self.socket_connect(tree, tex_coord, carpaint_roughness_voronoi, 3, 0, socket_type='VECTOR')
            # CARPAINT END

            # COLORIZATION START
            if not colorize_rgb_mix_node:
                colorize_rgb_mix_node = self.new_node(tree,
                    bl_idname = 'ShaderNodeMixRGB',
                    x = principled.location.x-200,
                    y = principled.location.y,
                )
                colorize_rgb_mix_node.name = 'colorize_rgb_mix_node'
                colorize_rgb_mix_node.label = 'colorize_rgb_mix_node'
            colorize_rgb_mix_node.location.x = principled.location.x-200
            colorize_rgb_mix_node.location.y = principled.location.y+400
            self.socket_connect(tree, colorize_rgb_mix_node, principled, socket_type='RGBA')

            if not colorize_rgb_picker:
                colorize_rgb_picker = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeRGB',
                    x = colorize_rgb_mix_node.location.x-275,
                    y = colorize_rgb_mix_node.location.y-125,
                )
                colorize_rgb_picker.outputs[0].default_value = self.colorize_rgb
                colorize_rgb_picker.name = 'colorize_rgb_picker'
                colorize_rgb_picker.label = 'colorize_rgb_picker'
            colorize_rgb_picker.location.x = colorize_rgb_mix_node.location.x-275
            colorize_rgb_picker.location.y = colorize_rgb_mix_node.location.y-125
            self.socket_connect(tree, colorize_rgb_picker, colorize_rgb_mix_node, 0, 1, socket_type='RGBA')

            if not basecolor_ramp:
                basecolor_ramp = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeValToRGB',
                    x = colorize_rgb_mix_node.location.x-275,
                    y = colorize_rgb_mix_node.location.y+125,
                )
                basecolor_ramp.name = 'basecolor_ramp'
                basecolor_ramp.label = 'basecolor_ramp'
            basecolor_ramp.color_ramp.elements[0].color = self.rampbased_ramp_start
            basecolor_ramp.color_ramp.elements[1].color = self.rampbased_ramp_end
            basecolor_ramp.color_ramp.elements[1].position = self.rampbased_ramp_spread
            self.socket_connect(tree, basecolor_ramp, colorize_rgb_mix_node, socket_type='RGBA')

            if not object_info:
                object_info = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeObjectInfo',
                    x = basecolor_ramp.location.x-250,
                    y = basecolor_ramp.location.y,
                )
                object_info.name = 'object_info'
                object_info.label = 'object_info'
            self.socket_connect(tree, object_info, basecolor_ramp, 2, 0, socket_type='VALUE') # from 'Random' to 'Fac'
            self.socket_connect(tree, object_info, carpaint_shift_ramp, 2, 0, socket_type='VALUE')
            # COLORIZATION END

            # ROUGHNESS START
            if not roughness_rgb_to_bw:
                roughness_rgb_to_bw = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeRGBToBW',
                    x = principled.location.x-200,
                    y = principled.location.y,
                )
                roughness_rgb_to_bw.name = 'roughness_rgb_to_bw'
                roughness_rgb_to_bw.label = 'roughness_rgb_to_bw'
            self.socket_connect(tree, roughness_rgb_to_bw, principled, 0, 4, socket_type='VALUE')

            if not roughness_ramp:
                roughness_ramp = self.new_node(
                    tree,
                    bl_idname='ShaderNodeValToRGB',
                    x = roughness_rgb_to_bw.location.x-275,
                    y = roughness_rgb_to_bw.location.y,
                )
                roughness_ramp.name = 'roughness_ramp'
                roughness_ramp.label = 'roughness_ramp'

            self.socket_connect(tree, roughness_ramp, roughness_rgb_to_bw, 0, 0, socket_type='RGBA')
            self.socket_connect(tree, object_info, roughness_ramp, 2, 0, socket_type='VALUE')

            roughness_ramp_start = [0.0, 0.0, 0.0, 1.0]
            roughness_ramp_end = [0.0, 0.0, 0.0, 1.0]
            for index, value in enumerate(roughness_ramp_start[:3]):
                roughness_ramp_start[index] = self.rampbased_roughness_min

            for index, value in enumerate(roughness_ramp_end[:3]):
                roughness_ramp_end[index] = self.rampbased_roughness_max

            roughness_ramp.color_ramp.elements[0].color = roughness_ramp_start
            roughness_ramp.color_ramp.elements[1].color = roughness_ramp_end
            # ROUGHNESS END

            # CARPAINT PROBABILITY START
            if not carpaint_round:
                carpaint_round = self.new_node(
                    tree,
                    bl_idname='ShaderNodeMath',
                    x = final_mix_shader.location.x-200,
                    y = final_mix_shader.location.y+500,
                )
                carpaint_round.name = 'carpaint_round'
                carpaint_round.label = 'carpaint_round'
            carpaint_round.operation = 'ROUND'
            carpaint_round.use_clamp = True
            self.socket_connect(tree, carpaint_round, final_mix_shader, 0, 0, socket_type='VALUE')

            if not carpaint_rgb_to_bw:
                carpaint_rgb_to_bw = self.new_node(
                    tree,
                    bl_idname='ShaderNodeRGBToBW',
                    x = carpaint_round.location.x-200,
                    y = carpaint_round.location.y,
                )
                carpaint_rgb_to_bw.name = 'carpaint_rgb_to_bw'
                carpaint_rgb_to_bw.label = 'carpaint_rgb_to_bw'
            self.socket_connect(tree, carpaint_rgb_to_bw, carpaint_round, 0, 0, socket_type='VALUE')

            if not carpaint_ramp:
                carpaint_ramp = self.new_node(
                    tree,
                    bl_idname = 'ShaderNodeValToRGB',
                    x = carpaint_rgb_to_bw.location.x-275,
                    y = carpaint_rgb_to_bw.location.y,
                )
                carpaint_ramp.name = 'carpaint_ramp'
                carpaint_ramp.label = 'carpaint_ramp'

            self.socket_connect(tree, carpaint_ramp, carpaint_rgb_to_bw, 0, 0, socket_type='RGBA')
            self.socket_connect(tree, object_info, carpaint_ramp, 2, 0, socket_type='VALUE')

            carpaint_ramp.color_ramp.interpolation = 'CONSTANT'
            if self.rampbased_carpaint_probability == 100.0 or self.rampbased_carpaint_probability == 0.0:
                if len(carpaint_ramp.color_ramp.elements.values()) > 1:
                    for element in carpaint_ramp.color_ramp.elements.values()[1:]:
                        carpaint_ramp.color_ramp.elements.remove(element)
                tmp_v = self.rampbased_carpaint_probability / 100.0
                carpaint_ramp.color_ramp.elements[0].color = [tmp_v, tmp_v, tmp_v, 1.0]
                carpaint_ramp.color_ramp.elements[0].position = 0.0
            else:
                if len(carpaint_ramp.color_ramp.elements.values()) != 2:
                    for element in carpaint_ramp.color_ramp.elements.values()[1:]:
                        carpaint_ramp.color_ramp.elements.remove(element)
                    carpaint_ramp.color_ramp.elements.new(1.0)
                carpaint_ramp.color_ramp.elements[0].position = 0.0
                carpaint_ramp.color_ramp.elements[0].color = [0.0, 0.0, 0.0, 1.0]
                carpaint_ramp.color_ramp.elements[1].position = 1.0 - (self.rampbased_carpaint_probability / 100.0)
                carpaint_ramp.color_ramp.elements[1].color = [1.0, 1.0, 1.0, 1.0]
            # CARPAINT PROBABILITY END

            # METAL START
            if not metal_round:
                metal_round = self.new_node(
                    tree,
                    bl_idname='ShaderNodeMath',
                    x = principled.location.x-200,
                    y = principled.location.y-300,
                )
                metal_round.name = 'metal_round'
                metal_round.label = 'metal_round'
            metal_round.operation = 'ROUND'
            metal_round.use_clamp = True
            self.socket_connect(tree, metal_round, principled, 0, 1, socket_type='VALUE')

            if not metal_rgb_to_bw:
                metal_rgb_to_bw = self.new_node(
                    tree,
                    bl_idname='ShaderNodeRGBToBW',
                    x = metal_round.location.x-200,
                    y = metal_round.location.y,
                )
                metal_rgb_to_bw.name = 'metal_rgb_to_bw'
                metal_rgb_to_bw.label = 'metal_rgb_to_bw'
            self.socket_connect(tree, metal_rgb_to_bw, metal_round, 0, 0, socket_type='VALUE')

            if not metal_ramp:
                metal_ramp = self.new_node(
                    tree,
                    bl_idname='ShaderNodeValToRGB',
                    x = metal_rgb_to_bw.location.x-275,
                    y = metal_rgb_to_bw.location.y,
                )
                metal_ramp.name = 'metal_ramp'
                metal_ramp.label = 'metal_ramp'

            self.socket_connect(tree, metal_ramp, metal_rgb_to_bw, 0, 0, socket_type='RGBA')
            self.socket_connect(tree, object_info, metal_ramp, 2, 0, socket_type='VALUE')
            metal_ramp.color_ramp.interpolation = 'CONSTANT'
            if self.rampbased_metal_probability == 100.0 or self.rampbased_metal_probability == 0.0:
                if len(metal_ramp.color_ramp.elements.values()) > 1:
                    for element in metal_ramp.color_ramp.elements.values()[1:]:
                        metal_ramp.color_ramp.elements.remove(element)
                tmp_v = self.rampbased_metal_probability / 100.0
                metal_ramp.color_ramp.elements[0].color = [tmp_v, tmp_v, tmp_v, 1.0]
                metal_ramp.color_ramp.elements[0].position = 0.0
            else:
                if len(metal_ramp.color_ramp.elements.values()) != 2:
                    for element in metal_ramp.color_ramp.elements.values()[1:]:
                        metal_ramp.color_ramp.elements.remove(element)
                    metal_ramp.color_ramp.elements.new(1.0)
                metal_ramp.color_ramp.elements[0].position = 0.0
                metal_ramp.color_ramp.elements[0].color = [0.0, 0.0, 0.0, 1.0]
                metal_ramp.color_ramp.elements[1].position = 1.0 - (self.rampbased_metal_probability / 100.0)
                metal_ramp.color_ramp.elements[1].color = [1.0, 1.0, 1.0, 1.0]
            # METAL END

            # CLEARCOAT START
            if not clearcoat_round:
                clearcoat_round = self.new_node(
                    tree,
                    bl_idname='ShaderNodeMath',
                    x = principled.location.x-200,
                    y = principled.location.y-600,
                )
                clearcoat_round.name = 'clearcoat_round'
                clearcoat_round.label = 'clearcoat_round'
            clearcoat_round.operation = 'ROUND'
            clearcoat_round.use_clamp = True
            self.socket_connect(tree, clearcoat_round, principled, 0, 9, socket_type='VALUE')

            if not clearcoat_rgb_to_bw:
                clearcoat_rgb_to_bw = self.new_node(
                    tree,
                    bl_idname='ShaderNodeRGBToBW',
                    x = clearcoat_round.location.x-200,
                    y = clearcoat_round.location.y,
                )
                clearcoat_rgb_to_bw.name = 'clearcoat_rgb_to_bw'
                clearcoat_rgb_to_bw.label = 'clearcoat_rgb_to_bw'
            self.socket_connect(tree, clearcoat_rgb_to_bw, clearcoat_round, 0, 0, socket_type='VALUE')

            if not clearcoat_ramp:
                clearcoat_ramp = self.new_node(
                    tree,
                    bl_idname='ShaderNodeValToRGB',
                    x = clearcoat_rgb_to_bw.location.x-275,
                    y = clearcoat_rgb_to_bw.location.y,
                )
                clearcoat_ramp.name = 'clearcoat_ramp'
                clearcoat_ramp.label = 'clearcoat_ramp'

            self.socket_connect(tree, clearcoat_ramp, clearcoat_rgb_to_bw, 0, 0, socket_type='RGBA')
            self.socket_connect(tree, object_info, clearcoat_ramp, 2, 0, socket_type='VALUE')
            clearcoat_ramp.color_ramp.interpolation = 'CONSTANT'
            if self.rampbased_clearcoat_probability == 100.0 or self.rampbased_clearcoat_probability == 0.0:
                if len(clearcoat_ramp.color_ramp.elements.values()) > 1:
                    for element in clearcoat_ramp.color_ramp.elements.values()[1:]:
                        clearcoat_ramp.color_ramp.elements.remove(element)
                tmp_v = self.rampbased_clearcoat_probability / 100.0
                clearcoat_ramp.color_ramp.elements[0].color = [tmp_v, tmp_v, tmp_v, 1.0]
                clearcoat_ramp.color_ramp.elements[0].position = 0.0
            else:
                if len(clearcoat_ramp.color_ramp.elements.values()) != 2:
                    for element in clearcoat_ramp.color_ramp.elements.values()[1:]:
                        clearcoat_ramp.color_ramp.elements.remove(element)
                    clearcoat_ramp.color_ramp.elements.new(1.0)
                clearcoat_ramp.color_ramp.elements[0].position = 0.0
                clearcoat_ramp.color_ramp.elements[0].color = [0.0, 0.0, 0.0, 1.0]
                clearcoat_ramp.color_ramp.elements[1].position = 1.0 - (self.rampbased_clearcoat_probability / 100.0)
                clearcoat_ramp.color_ramp.elements[1].color = [1.0, 1.0, 1.0, 1.0]
            # CLEARCOAT END

            colorize_rgb_mix_node.mute = not self.colorize
            return

        if principled:
            tree.nodes.remove(principled)

        if principled_carpaint:
            tree.nodes.remove(principled_carpaint)


    def emission(self, tree, clear=True):
        output = self.node(tree, bl_idname='ShaderNodeOutputMaterial')
        emission = self.node(tree, bl_idname='ShaderNodeEmission')

        if not clear:
            if not emission:
                emission = self.new_node(tree,
                    bl_idname = 'ShaderNodeEmission',
                    x = output.location.x-180,
                    y = output.location.y)

                self.socket(emission, type='inputs', socket_type='RGBA').default_value = self.random

                self.socket_connect(tree, emission, output)

            multiply = self.new_node(tree,
                bl_idname = 'ShaderNodeMath',
                x = emission.location.x-180,
                y = emission.location.y)

            self.socket(multiply, type='inputs', socket_type='VALUE', index=1).default_value = 8
            multiply.operation = 'MULTIPLY'

            self.socket_connect(tree, multiply, emission, socket_type='VALUE')

            floor = self.new_node(tree,
                bl_idname = 'ShaderNodeMath',
                x = multiply.location.x-180,
                y = multiply.location.y)

            floor.use_clamp = True
            floor.operation = 'FLOOR'

            self.socket_connect(tree, floor, multiply, socket_type='VALUE')

            arctan2 = self.new_node(tree,
                bl_idname = 'ShaderNodeMath',
                x = floor.location.x-180,
                y = floor.location.y)

            arctan2.operation = 'ARCTAN2'

            if self.pulse:
                driven_path = self.socket(
                    arctan2,
                    type = 'inputs',
                    socket_type = 'VALUE',
                    path_id = 'default_value')
                new = tree.driver_add(driven_path)
                new.driver.type = 'SCRIPTED'
                new.driver.expression = f'cos(frame*pi/{30/self.frequency})'

            self.socket_connect(tree, arctan2, floor, socket_type='VALUE')

            self.socket(arctan2, type='inputs', socket_type='VALUE', index=1).default_value = 0.2

            return

        connected = self.connected_nodes(emission, [])

        for node in connected:
            tree.nodes.remove(node)

        # tree.nodes.remove(emission)


    # 50% alpha in workbench view
    def glass(self, tree, clear=True):
        output = self.node(tree, bl_idname='ShaderNodeOutputMaterial')
        mix = self.node(tree, bl_idname='ShaderNodeMixShader')

        if not clear:
            if not mix:
                mix = self.new_node(tree,
                    bl_idname = 'ShaderNodeMixShader',
                    x = output.location.x-180,
                    y = output.location.y)

                self.socket_connect(tree, mix, output)

            color_ramp = self.new_node(tree,
                bl_idname = 'ShaderNodeValToRGB',
                x = mix.location.x-280,
                y = mix.location.y+150)

            color_ramp.color_ramp.elements[1].position = 0.3
            color_ramp.color_ramp.elements[1].color = (0.6, 0.6, 0.6, 1.0)

            self.socket_connect(tree, color_ramp, mix, socket_type='RGBA', socket_to_type='VALUE')

            fresnel = self.new_node(tree,
                bl_idname = 'ShaderNodeFresnel',
                x = color_ramp.location.x-180,
                y = color_ramp.location.y-100)

            self.socket_connect(tree, fresnel, color_ramp, socket_type='VALUE')

            glass = self.new_node(tree,
                bl_idname = 'ShaderNodeBsdfGlass',
                x = fresnel.location.x,
                y = fresnel.location.y-220)

            self.socket(glass, type='inputs', socket_type='VALUE').default_value = 0.1
            self.socket_connect(tree, glass, mix, index_to=1)

            transparent = self.new_node(tree,
                bl_idname = 'ShaderNodeBsdfTransparent',
                x = fresnel.location.x,
                y = fresnel.location.y-120)

            self.socket(transparent, type='inputs', socket_type='RGBA').default_value = (0.6, 0.6, 0.6, 1.0)
            self.socket_connect(tree, transparent, mix)

            value = self.new_node(tree,
                bl_idname = 'ShaderNodeValue',
                x = transparent.location.x-180,
                y = transparent.location.y)

            self.socket(value, socket_type='VALUE').default_value = 1.45

            self.socket_connect(tree, value, fresnel, socket_type='VALUE')
            self.socket_connect(tree, value, glass, socket_type='VALUE', index_to=1)

            return

        connected = self.connected_nodes(mix, [])

        for node in connected:
            tree.nodes.remove(node)

        # tree.nodes.remove(mix)


    def invoke(self, context, event):
        if event.ctrl and not event.shift:
            self.unique = True
            self.type = 'PRINCIPLED'
            if get_preferences().ui.Hops_extra_info:
                bpy.ops.hops.display_notification(info=F'Blank Material - Principle (unique)', name="")

        elif event.shift and not event.ctrl:
            self.type = 'GLASS'
            if get_preferences().ui.Hops_extra_info:
                bpy.ops.hops.display_notification(info=F'Blank Material - Glass', name="")

        elif event.alt and not event.shift and not event.ctrl:
            self.type = 'EMISSION'
            if get_preferences().ui.Hops_extra_info:
                bpy.ops.hops.display_notification(info=F'Blank Material - Emission', name="")

        elif self.helper_call:
            self.type = 'PRINCIPLED'
            # if get_preferences().ui.Hops_extra_info:
            #     bpy.ops.hops.display_notification(info=F'Blank Material - Principle', name="")

        else:
            self.type = 'PRINCIPLED'
            if get_preferences().ui.Hops_extra_info:
                bpy.ops.hops.display_notification(info=F'Blank Material - Principle ', name="")

        return self.execute(context)

    def execute(self, context):
        blend_method = 'OPAQUE' if self.type != 'GLASS' else 'BLEND'

        name = self.type.title() if self.type != 'PRINCIPLED' else 'Material'
        mat = self.new(name=name, blend_method=blend_method)

        if self.type == 'GLASS':
            mat.diffuse_color = (0.5, 0.5, 0.5, 0.5)
            mat.metallic = 1
            mat.roughness = 0

        if self.type != 'PRINCIPLED':
            self.principled(mat.node_tree)

        self.random = random_color()
        getattr(self, self.type.lower())(mat.node_tree, clear=False)

        if self.type == 'EMISSION':
            mat.diffuse_color = self.random
            mat.roughness = 0

        if self.helper_call:
            self.helper_call = False
            context.active_object.active_material = mat
            if self.type == 'PRINCIPLED':
                mat.diffuse_color = self.random
            return {'FINISHED'}

        for obj in context.selected_objects:
            if obj.type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT'}:

                if self.unique and self.type != 'GLASS' and self.type != 'RAMPBASED' and self.type != 'CARPAINT':
                    mat = self.new(blend_method=blend_method)

                    if self.type != 'PRINCIPLED':
                        self.principled(mat.node_tree)

                    self.random = random_color()
                    getattr(self, self.type.lower())(mat.node_tree, clear=False)

                    if self.type == 'EMISSION':
                        mat.diffuse_color = self.random
                        mat.roughness = 0

                #add(context, obj, mat=mat, append=False, viewport=self.type == 'PRINCIPLED')
                add(context, obj, mat=mat, append=False, viewport=True)

                #Add is undoing glass atm (will need fixing)
                if self.type == 'GLASS':
                    mat.diffuse_color[3] = 0.5

        if self.cleanup:
            for mat in bpy.data.materials[:]:
                if not mat.users:
                    bpy.data.materials.remove(mat)

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        row = column.row()
        row.prop(self, 'type', expand=True)

        if self.type == 'PRINCIPLED':
            self.label_row(column.row(), 'Unique Material', 'unique')
            self.label_row(column.row(), 'Colorize', 'colorize')
            self.label_row(column.row(), 'Colorize RGB', 'colorize_rgb')
            self.label_row(column.row(), 'Clearcoat', 'clearcoat')
            if not self.colorize:
                column.separator()
                self.label_row(column.row(), 'Grayscale', 'grayscale')
            column.separator()
            self.label_row(column.row(), 'Clamp', 'clamp')
            self.label_row(column.row(), 'Advanced Clamp Options', 'clamp_expand')
            if self.clamp_expand:
                self.label_row(column.row(), 'Clamp Min', 'clamp_min_nonmetals')
                self.label_row(column.row(), 'Clamp Max', 'clamp_max_nonmetals')
                self.label_row(column.row(), 'Clamp Min', 'clamp_min_metals')
                self.label_row(column.row(), 'Clamp Max', 'clamp_max_metals')
            
            self.label_row(column.row(), 'Bevel Shader','bevel_shader')
            if self.bevel_shader:
                self.label_row(column.row(), 'Samples','bevel_shader_samples')
                self.label_row(column.row(), 'Radius','bevel_shader_radius')

        if self.type == 'GLASS':
            pass # currently no extra options needed, placeholder

        if self.type == 'EMISSION':
            self.label_row(column.row(), 'Unique Material', 'unique')
            self.label_row(column.row(), 'Pulse', 'pulse')
            self.label_row(column.row(), 'Frequency', 'frequency')

        if self.type == 'CARPAINT':
            self.label_row(column.row(), 'Carpaint Metallic', 'rampbased_carpaint_metallic')
            self.label_row(column.row(), 'Carpaint Hue Shift', 'carpaint_hue_shift')
            self.label_row(column.row(), 'Carpaint Hue Variation', 'carpaint_hue_variation')
            self.label_row(column.row(), 'Carpaint Saturation', 'carpaint_saturation')
            self.label_row(column.row(), 'Carpaint Brightness', 'carpaint_value_brightness')
            self.label_row(column.row(), 'Advanced Carpaint Options', 'carpaint_expand_advanced')
            if self.carpaint_expand_advanced:
                self.label_row(column.row(), 'Carpaint Roughness Ramp Start', 'carpaint_roughness_ramp_start')
                self.label_row(column.row(), 'Carpaint Roughness Ramp End', 'carpaint_roughness_ramp_end')
                self.label_row(column.row(), 'Carpaint Roughness Scale', 'carpaint_roughness_scale')
                self.label_row(column.row(), 'Carpaint Color Start', 'carpaint_colorramp_start_color')
                self.label_row(column.row(), 'Carpaint Color End', 'carpaint_colorramp_end_color')

        if self.type == 'GENERAL':
            self.label_row(column.row(), 'Colorize', 'colorize')
            self.label_row(column.row(), 'Colorize RGB', 'colorize_rgb')
            column.separator()
            self.label_row(column.row(), 'Advanced Carpaint Options', 'carpaint_expand_advanced')
            if self.carpaint_expand_advanced:
                self.label_row(column.row(), 'Carpaint Metallic', 'rampbased_carpaint_metallic')
                self.label_row(column.row(), 'Carpaint Probability', 'rampbased_carpaint_probability')
                self.label_row(column.row(), 'Carpaint Hue Shift', 'carpaint_hue_shift')
                self.label_row(column.row(), 'Carpaint Hue Variation', 'carpaint_hue_variation')
                self.label_row(column.row(), 'Carpaint Saturation', 'carpaint_saturation')
                self.label_row(column.row(), 'Carpaint Brightness', 'carpaint_value_brightness')
                self.label_row(column.row(), 'Carpaint Roughness Ramp Start', 'carpaint_roughness_ramp_start')
                self.label_row(column.row(), 'Carpaint Roughness Ramp End', 'carpaint_roughness_ramp_end')
                self.label_row(column.row(), 'Carpaint Roughness Scale', 'carpaint_roughness_scale')
                self.label_row(column.row(), 'Carpaint Color Start', 'carpaint_colorramp_start_color')
                self.label_row(column.row(), 'Carpaint Color End', 'carpaint_colorramp_end_color')
            column.separator()
            self.label_row(column.row(), 'Metal Probability', 'rampbased_metal_probability')
            self.label_row(column.row(), 'Clearcoat Probability', 'rampbased_clearcoat_probability')
            column.separator()
            self.label_row(column.row(), 'Roughness Min', 'rampbased_roughness_min')
            self.label_row(column.row(), 'Roughness Max', 'rampbased_roughness_max')
            column.separator()
            self.label_row(column.row(), 'Ramp Start', 'rampbased_ramp_start')
            self.label_row(column.row(), 'Ramp End', 'rampbased_ramp_end')
            self.label_row(column.row(), 'Ramp Spread', 'rampbased_ramp_spread')
        column.separator()
        self.label_row(column.row(), 'Remove Zero User Materials', 'cleanup')


    def label_row(self, row, label, prop):
        row.label(text=label)
        row.prop(self, prop, text='')
