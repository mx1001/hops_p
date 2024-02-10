import bpy

def carpaint_material(material = None, name= 'Carpaint'):
    if not material:
        material = bpy.data.materials.new (name)
    material.use_nodes = True
    material_nodes = material.node_tree.nodes
    material_nodes.clear()
    output = material_nodes.new(type="ShaderNodeOutputMaterial")
    
    paint = material_nodes.new('ShaderNodeGroup')
    paint.node_tree = carpaint_node_group()
    material.node_tree.links.new(paint.outputs[0], output.inputs[0]) 
    paint.location = [-300, output.location[1]]
    return (material, paint)

def carpaint_node_group():
    group_name = 'HOPS.carpaint_shader'
    carpaint_shader = None
    try:
        carpaint_shader = bpy.data.node_groups[group_name]
        return carpaint_shader
    except:
        pass

    carpaint_shader = bpy.data.node_groups.new(group_name,'ShaderNodeTree')


    principled_carpaint = carpaint_shader.nodes.new("ShaderNodeBsdfPrincipled")
    principled_carpaint.location = [789, 105]
    principled_carpaint.name = "principled_carpaint"
    principled_carpaint.label = "principled_carpaint"
    #Node properties
    #unliked node I/O
    principled_carpaint.inputs["Subsurface"].default_value = 0.0
    principled_carpaint.inputs["Subsurface Radius"].default_value = [1.0, 0.20000000298023224, 0.10000000149011612]
    principled_carpaint.inputs["Subsurface Color"].default_value = [0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0]
    principled_carpaint.inputs["Specular"].default_value = 0.5
    principled_carpaint.inputs["Specular Tint"].default_value = 0.0
    principled_carpaint.inputs["Anisotropic"].default_value = 0.0
    principled_carpaint.inputs["Anisotropic Rotation"].default_value = 0.0
    principled_carpaint.inputs["Sheen"].default_value = 0.0
    principled_carpaint.inputs["Sheen Tint"].default_value = 0.5
    principled_carpaint.inputs["IOR"].default_value = 1.4500000476837158
    principled_carpaint.inputs["Transmission"].default_value = 0.0
    principled_carpaint.inputs["Transmission Roughness"].default_value = 0.0
    principled_carpaint.inputs["Emission"].default_value = [0.0, 0.0, 0.0, 1.0]
    principled_carpaint.inputs["Alpha"].default_value = 1.0
    principled_carpaint.inputs["Normal"].default_value = [0.0, 0.0, 0.0]
    principled_carpaint.inputs["Clearcoat Normal"].default_value = [0.0, 0.0, 0.0]
    principled_carpaint.inputs["Tangent"].default_value = [0.0, 0.0, 0.0]

    carpaint_roughness_voronoi = carpaint_shader.nodes.new("ShaderNodeTexVoronoi")
    carpaint_roughness_voronoi.location = [-287, -494]
    carpaint_roughness_voronoi.name = "carpaint_roughness_voronoi"
    carpaint_roughness_voronoi.label = "carpaint_roughness_voronoi"
    #Node properties
    carpaint_roughness_voronoi.voronoi_dimensions = "4D"
    carpaint_roughness_voronoi.feature = "F1"
    carpaint_roughness_voronoi.distance = "EUCLIDEAN"
    #unliked node I/O
    carpaint_roughness_voronoi.inputs["W"].default_value = 0.0
    carpaint_roughness_voronoi.inputs["Smoothness"].default_value = 1.0
    carpaint_roughness_voronoi.inputs["Exponent"].default_value = 0.5
    carpaint_roughness_voronoi.inputs["Randomness"].default_value = 1.0

    carpaint_colorramp = carpaint_shader.nodes.new("ShaderNodeValToRGB")
    carpaint_colorramp.location = [-65, -106]
    carpaint_colorramp.name = "carpaint_colorramp"
    carpaint_colorramp.label = "carpaint_colorramp"
    #Node properties
    carpaint_colorramp.color_ramp.color_mode = "RGB"
    carpaint_colorramp.color_ramp.interpolation = "LINEAR"
    carpaint_colorramp.color_ramp.elements[0].position = 0.0
    carpaint_colorramp.color_ramp.elements[0].color = [0.5534290075302124, 0.1514420062303543, 0.0514569990336895, 1.0]
    carpaint_colorramp.color_ramp.elements[1].position = 0.800000011920929
    carpaint_colorramp.color_ramp.elements[1].color = [1.0, 0.023302000015974045, 0.014751999638974667, 1.0]
    #unliked node I/O

    carpaint_hsv = carpaint_shader.nodes.new("ShaderNodeHueSaturation")
    carpaint_hsv.location = [540, 453]
    carpaint_hsv.name = "carpaint_hsv"
    carpaint_hsv.label = "carpaint_hsv"
    #Node properties
    #unliked node I/O
    carpaint_hsv.inputs["Fac"].default_value = 1.0

    Map_Range = carpaint_shader.nodes.new("ShaderNodeMapRange")
    Map_Range.location = [107, -490]
    Map_Range.name = "Map_Range"
    #Node properties
    #unliked node I/O
    Map_Range.inputs["From Min"].default_value = 0.0
    Map_Range.inputs["From Max"].default_value = 1.0
    Map_Range.inputs["Steps"].default_value = 4.0

    carpaint_layerweight = carpaint_shader.nodes.new("ShaderNodeLayerWeight")
    carpaint_layerweight.location = [-237, -108]
    carpaint_layerweight.name = "carpaint_layerweight"
    carpaint_layerweight.label = "carpaint_layerweight"
    #Node properties
    #unliked node I/O
    carpaint_layerweight.inputs["Blend"].default_value = 0.5
    carpaint_layerweight.inputs["Normal"].default_value = [0.0, 0.0, 0.0]

    tex_coord = carpaint_shader.nodes.new("ShaderNodeTexCoord")
    tex_coord.location = [-638, -548]
    tex_coord.name = "tex_coord"
    tex_coord.label = "tex_coord"
    #Node properties
    #unliked node I/O

    Group_Output = carpaint_shader.nodes.new("NodeGroupOutput")
    Group_Output.location = [1139, 100]
    Group_Output.name = "Group_Output"
    #Node properties

    Gorup_in = carpaint_shader.nodes.new("NodeGroupInput")
    Gorup_in.location = [-815, 467]
    Gorup_in.name = "Gorup_in"
    Gorup_in.label = "Gorup_in"
    #Node properties

    Object_Info = carpaint_shader.nodes.new("ShaderNodeObjectInfo")
    Object_Info.location = [-816, 657]
    Object_Info.name = "Object_Info"
    #Node properties
    #unliked node I/O

    carpaint_shift_mix_002 = carpaint_shader.nodes.new("ShaderNodeMixRGB")
    carpaint_shift_mix_002.location = [210, 391]
    carpaint_shift_mix_002.name = "carpaint_shift_mix_002"
    carpaint_shift_mix_002.label = "carpaint_shift_mix"
    #Node properties
    carpaint_shift_mix_002.blend_type = "MIX"
    carpaint_shift_mix_002.use_clamp = True
    #unliked node I/O

    Map_Range_002 = carpaint_shader.nodes.new("ShaderNodeMapRange")
    Map_Range_002.location = [106, 746]
    Map_Range_002.name = "Map_Range_002"
    #Node properties
    #unliked node I/O
    Map_Range_002.inputs["From Min"].default_value = 0.0
    Map_Range_002.inputs["From Max"].default_value = 1.0
    Map_Range_002.inputs["To Min"].default_value = 0.0
    Map_Range_002.inputs["To Max"].default_value = 1.0
    Map_Range_002.inputs["Steps"].default_value = 4.0

    Map_Range_003 = carpaint_shader.nodes.new("ShaderNodeMapRange")
    Map_Range_003.location = [-28, 502]
    Map_Range_003.name = "Map_Range_003"
    #Node properties
    #unliked node I/O
    Map_Range_003.inputs["From Min"].default_value = 0.0
    Map_Range_003.inputs["From Max"].default_value = 1.0
    Map_Range_003.inputs["To Min"].default_value = 0.0
    Map_Range_003.inputs["To Max"].default_value = 1.0
    Map_Range_003.inputs["Steps"].default_value = 4.0

    carpaint_shift_mix = carpaint_shader.nodes.new("ShaderNodeMixRGB")
    carpaint_shift_mix.location = [109, 1145]
    carpaint_shift_mix.name = "carpaint_shift_mix"
    carpaint_shift_mix.label = "carpaint_shift_mix"
    #Node properties
    carpaint_shift_mix.blend_type = "MIX"
    carpaint_shift_mix.use_clamp = True
    #unliked node I/O

    carpaint_shift_mix_001 = carpaint_shader.nodes.new("ShaderNodeMixRGB")
    carpaint_shift_mix_001.location = [273, 611]
    carpaint_shift_mix_001.name = "carpaint_shift_mix_001"
    carpaint_shift_mix_001.label = "carpaint_shift_mix"
    #Node properties
    carpaint_shift_mix_001.blend_type = "MIX"
    carpaint_shift_mix_001.use_clamp = True
    #unliked node I/O

    Math = carpaint_shader.nodes.new("ShaderNodeMath")
    Math.location = [-400, 638]
    Math.name = "Math"
    #Node properties
    Math.operation = "MULTIPLY"
    Math.use_clamp = False
    #unliked node I/O
    Math.inputs[2].default_value = 0.0

    Math_001 = carpaint_shader.nodes.new("ShaderNodeMath")
    Math_001.location = [-193, 1113]
    Math_001.name = "Math_001"
    #Node properties
    Math_001.operation = "ADD"
    Math_001.use_clamp = False
    #unliked node I/O
    Math_001.inputs[1].default_value = 0.0
    Math_001.inputs[2].default_value = 0.0

    Math_003 = carpaint_shader.nodes.new("ShaderNodeMath")
    Math_003.location = [-166, 265]
    Math_003.name = "Math_003"
    #Node properties
    Math_003.operation = "ADD"
    Math_003.use_clamp = False
    #unliked node I/O
    Math_003.inputs[1].default_value = 0.0
    Math_003.inputs[2].default_value = 0.0

    Map_Range_001 = carpaint_shader.nodes.new("ShaderNodeMapRange")
    Map_Range_001.location = [-91, 893]
    Map_Range_001.name = "Map_Range_001"
    #Node properties
    #unliked node I/O
    Map_Range_001.inputs["From Min"].default_value = 0.0
    Map_Range_001.inputs["From Max"].default_value = 1.0
    Map_Range_001.inputs["To Min"].default_value = 0.0
    Map_Range_001.inputs["To Max"].default_value = 1.0
    Map_Range_001.inputs["Steps"].default_value = 4.0

    Math_002 = carpaint_shader.nodes.new("ShaderNodeMath")
    Math_002.location = [-205, 394]
    Math_002.name = "Math_002"
    #Node properties
    Math_002.operation = "ADD"
    Math_002.use_clamp = False
    #unliked node I/O
    Math_002.inputs[1].default_value = 0.0
    Math_002.inputs[2].default_value = 0.0
    #group llinks
    carpaint_shader.links.new(carpaint_hsv.outputs["Color"], principled_carpaint.inputs["Base Color"])
    carpaint_shader.links.new(carpaint_colorramp.outputs["Color"], carpaint_hsv.inputs["Color"])
    carpaint_shader.links.new(carpaint_layerweight.outputs["Facing"], carpaint_colorramp.inputs["Fac"])
    carpaint_shader.links.new(tex_coord.outputs["Object"], carpaint_roughness_voronoi.inputs["Vector"])
    carpaint_shader.links.new(Map_Range.outputs["Result"], principled_carpaint.inputs["Roughness"])
    carpaint_shader.links.new(carpaint_roughness_voronoi.outputs["Color"], Map_Range.inputs["Value"])
    carpaint_shader.links.new(Object_Info.outputs["Random"], Math.inputs[0])
    carpaint_shader.links.new(Map_Range_001.outputs["Result"], carpaint_shift_mix.inputs["Color2"])
    carpaint_shader.links.new(carpaint_shift_mix.outputs["Color"], carpaint_hsv.inputs["Hue"])
    carpaint_shader.links.new(Math.outputs["Value"], Map_Range_001.inputs[0])
    carpaint_shader.links.new(Math_001.outputs["Value"], carpaint_shift_mix.inputs["Color1"])
    carpaint_shader.links.new(Map_Range_002.outputs["Result"], carpaint_shift_mix_001.inputs["Color2"])
    carpaint_shader.links.new(Math.outputs["Value"], Map_Range_002.inputs[0])
    carpaint_shader.links.new(Math_002.outputs["Value"], carpaint_shift_mix_001.inputs["Color1"])
    carpaint_shader.links.new(Map_Range_003.outputs["Result"], carpaint_shift_mix_002.inputs["Color2"])
    carpaint_shader.links.new(carpaint_shift_mix_001.outputs["Color"], carpaint_hsv.inputs["Saturation"])
    carpaint_shader.links.new(carpaint_shift_mix_002.outputs["Color"], carpaint_hsv.inputs["Value"])
    carpaint_shader.links.new(Math_003.outputs["Value"], carpaint_shift_mix_002.inputs["Color1"])
    carpaint_shader.links.new(Math.outputs["Value"], Map_Range_003.inputs[0])
    carpaint_shader.links.new(Gorup_in.outputs[0], carpaint_shift_mix.inputs["Fac"])
    carpaint_shader.links.new(Gorup_in.outputs[1], Math_001.inputs[0])
    carpaint_shader.links.new(Gorup_in.outputs[2], carpaint_shift_mix_001.inputs["Fac"])
    carpaint_shader.links.new(Gorup_in.outputs[3], Math_002.inputs[0])
    carpaint_shader.links.new(Gorup_in.outputs[4], carpaint_shift_mix_002.inputs["Fac"])
    carpaint_shader.links.new(Gorup_in.outputs[5], Math_003.inputs[0])
    carpaint_shader.links.new(Gorup_in.outputs[6], principled_carpaint.inputs["Metallic"])
    carpaint_shader.links.new(Gorup_in.outputs[7], Map_Range.inputs["To Min"])
    carpaint_shader.links.new(Gorup_in.outputs[8], Map_Range.inputs["To Max"])
    carpaint_shader.links.new(Gorup_in.outputs[9], carpaint_roughness_voronoi.inputs["Scale"])
    carpaint_shader.links.new(Gorup_in.outputs[10], principled_carpaint.inputs["Clearcoat"])
    carpaint_shader.links.new(Gorup_in.outputs[11], principled_carpaint.inputs["Clearcoat Roughness"])
    carpaint_shader.links.new(Gorup_in.outputs[12], Math.inputs[1])
    carpaint_shader.links.new(principled_carpaint.outputs["BSDF"], Group_Output.inputs[0])
    Gorup_in.outputs[0].name = "Hue Variation"
    carpaint_shader.inputs[0].name = "Hue Variation"
    Gorup_in.outputs[1].name = "Hue Shift Base Value"
    carpaint_shader.inputs[1].name = "Hue Shift Base Value"
    Gorup_in.outputs[2].name = "Saturation Variation"
    carpaint_shader.inputs[2].name = "Saturation Variation"
    Gorup_in.outputs[3].name = "Saturation Base Value"
    carpaint_shader.inputs[3].name = "Saturation Base Value"
    Gorup_in.outputs[4].name = "Brightness Variation"
    carpaint_shader.inputs[4].name = "Brightness Variation"
    Gorup_in.outputs[5].name = "Brightness Value"
    carpaint_shader.inputs[5].name = "Brightness Value"
    Gorup_in.outputs[6].name = "Metallic"
    carpaint_shader.inputs[6].name = "Metallic"
    Gorup_in.outputs[7].name = "Flake Roughness Minimum"
    carpaint_shader.inputs[7].name = "Flake Roughness Minimum"
    Gorup_in.outputs[8].name = "Flake Roughness Maximum"
    carpaint_shader.inputs[8].name = "Flake Roughness Maximum"
    Gorup_in.outputs[9].name = "Flake Scale"
    carpaint_shader.inputs[9].name = "Flake Scale"
    Gorup_in.outputs[10].name = "Clearcoat"
    carpaint_shader.inputs[10].name = "Clearcoat"
    Gorup_in.outputs[11].name = "Clearcoat Roughness"
    carpaint_shader.inputs[11].name = "Clearcoat Roughness"
    Gorup_in.outputs[12].name = "Randomness"
    carpaint_shader.inputs[12].name = "Randomness"
    Group_Output.inputs[0].name = "BSDF"
    carpaint_shader.outputs[0].name = "BSDF"
    carpaint_shader.inputs["Hue Variation"].min_value = 0.0
    carpaint_shader.inputs["Hue Variation"].max_value = 1.0
    carpaint_shader.inputs["Hue Shift Base Value"].min_value = 0.0
    carpaint_shader.inputs["Hue Shift Base Value"].max_value = 1.0
    carpaint_shader.inputs["Saturation Variation"].min_value = 0.0
    carpaint_shader.inputs["Saturation Variation"].max_value = 1.0
    carpaint_shader.inputs["Saturation Base Value"].min_value = 0.0
    carpaint_shader.inputs["Saturation Base Value"].max_value = 1.0
    carpaint_shader.inputs["Brightness Variation"].min_value = 0.0
    carpaint_shader.inputs["Brightness Variation"].max_value = 1.0
    carpaint_shader.inputs["Brightness Value"].min_value = -1.0
    carpaint_shader.inputs["Brightness Value"].max_value = 1.0
    carpaint_shader.inputs["Metallic"].min_value = 0.0
    carpaint_shader.inputs["Metallic"].max_value = 1.0
    carpaint_shader.inputs["Flake Roughness Minimum"].min_value = 0.0
    carpaint_shader.inputs["Flake Roughness Minimum"].max_value = 1.0
    carpaint_shader.inputs["Flake Roughness Maximum"].min_value = 0.0
    carpaint_shader.inputs["Flake Roughness Maximum"].max_value = 1.0
    carpaint_shader.inputs["Flake Scale"].min_value = 1.0
    carpaint_shader.inputs["Flake Scale"].max_value = 20000.0
    carpaint_shader.inputs["Clearcoat"].min_value = 0.0
    carpaint_shader.inputs["Clearcoat"].max_value = 1.0
    carpaint_shader.inputs["Clearcoat Roughness"].min_value = 0.0
    carpaint_shader.inputs["Clearcoat Roughness"].max_value = 1.0
    carpaint_shader.inputs["Randomness"].min_value = 0.0
    carpaint_shader.inputs["Randomness"].max_value = 1.0


    return carpaint_shader