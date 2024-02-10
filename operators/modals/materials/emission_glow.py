import bpy
from math import pi

def emission_glow_material(material = None, name= 'emission_glow'):
    if not material:
        material = bpy.data.materials.new (name)
    material.use_nodes = True
    material_nodes = material.node_tree.nodes
    material_nodes.clear()
    output = material_nodes.new(type="ShaderNodeOutputMaterial")

    emission_glow = material_nodes.new('ShaderNodeGroup')
    emission_glow.node_tree = emission_glow_node_group()
    material.node_tree.links.new(emission_glow.outputs[0], output.inputs[0]) 
    emission_glow.location = [-300, output.location[1]]
    return (material, emission_glow)

def emission_glow_node_group():
    group_name = 'HOPS.emission_glow'
    emission_glow = None
    try:
        emission_glow = bpy.data.node_groups[group_name]
        return emission_glow
    except:
        pass


    emission_glow = bpy.data.node_groups.new(group_name,"ShaderNodeTree")

    Reroute_005 = emission_glow.nodes.new("NodeReroute")
    Reroute_005.location = [-192, -449]
    Reroute_005.name = "Reroute_005"
    #Node properties

    Reroute_004 = emission_glow.nodes.new("NodeReroute")
    Reroute_004.location = [-597, -447]
    Reroute_004.name = "Reroute_004"
    #Node properties

    Node = emission_glow.nodes.new("ShaderNodeMath")
    Node.location = [155, 90]
    Node.name = "Node"
    #Node properties
    Node.operation = "COSINE"
    Node.use_clamp = False
    #node I/O
    Node.inputs[0].default_value = 3.1415927410125732
    Node.inputs[1].default_value = 0.5
    Node.inputs[2].default_value = 0.0

    Reroute_007 = emission_glow.nodes.new("NodeReroute")
    Reroute_007.location = [561, -626]
    Reroute_007.name = "Reroute_007"
    #Node properties

    Reroute_006 = emission_glow.nodes.new("NodeReroute")
    Reroute_006.location = [-864, -624]
    Reroute_006.name = "Reroute_006"
    #Node properties

    Reroute_009 = emission_glow.nodes.new("NodeReroute")
    Reroute_009.location = [-1066, -697]
    Reroute_009.name = "Reroute_009"
    #Node properties

    Func_Offset_deg = emission_glow.nodes.new("ShaderNodeMath")
    Func_Offset_deg.location = [-395, 224]
    Func_Offset_deg.name = "Func_Offset_(deg)"
    Func_Offset_deg.label = "Func Offset "
    #Node properties
    Func_Offset_deg.operation = "RADIANS"
    Func_Offset_deg.use_clamp = False
    #node I/O
    Func_Offset_deg.inputs[0].default_value = 0.0
    Func_Offset_deg.inputs[1].default_value = 0.0
    Func_Offset_deg.inputs[2].default_value = 0.0

    Math_007 = emission_glow.nodes.new("ShaderNodeMath")
    Math_007.location = [-72, 193]
    Math_007.name = "Math_007"
    #Node properties
    Math_007.operation = "ADD"
    Math_007.use_clamp = False
    #node I/O
    Math_007.inputs[0].default_value = 3.1415927410125732
    Math_007.inputs[1].default_value = 0.5
    Math_007.inputs[2].default_value = 0.0

    Math_002 = emission_glow.nodes.new("ShaderNodeMath")
    Math_002.location = [-324, -10]
    Math_002.name = "Math_002"
    #Node properties
    Math_002.operation = "MULTIPLY"
    Math_002.use_clamp = False
    #node I/O
    Math_002.inputs[0].default_value = 3.1415927410125732
    Math_002.inputs[1].default_value = 0.5
    Math_002.inputs[2].default_value = 0.0

    Emission = emission_glow.nodes.new("ShaderNodeEmission")
    Emission.location = [1561, 213]
    Emission.name = "Emission"
    #Node properties
    #node I/O
    Emission.inputs["Color"].default_value = [1.0, 1.0, 1.0, 1.0]
    Emission.inputs["Strength"].default_value = 1.0

    Math_005 = emission_glow.nodes.new("ShaderNodeMath")
    Math_005.location = [564, 314]
    Math_005.name = "Math_005"
    #Node properties
    Math_005.operation = "SIGN"
    Math_005.use_clamp = True
    #node I/O
    Math_005.inputs[0].default_value = 3.1415927410125732
    Math_005.inputs[1].default_value = 0.0
    Math_005.inputs[2].default_value = 0.0

    Reroute_008 = emission_glow.nodes.new("NodeReroute")
    Reroute_008.location = [677, -707]
    Reroute_008.name = "Reroute_008"
    #Node properties

    Reroute_011 = emission_glow.nodes.new("NodeReroute")
    Reroute_011.location = [-1065, -900]
    Reroute_011.name = "Reroute_011"
    #Node properties

    Math_001 = emission_glow.nodes.new("ShaderNodeMath")
    Math_001.location = [741, 236]
    Math_001.name = "Math_001"
    #Node properties
    Math_001.operation = "ADD"
    Math_001.use_clamp = True
    #node I/O
    Math_001.inputs[0].default_value = 0.5
    Math_001.inputs[1].default_value = 0.0
    Math_001.inputs[2].default_value = 0.0

    Group_Output = emission_glow.nodes.new("NodeGroupOutput")
    Group_Output.location = [2078, 143]
    Group_Output.name = "Group_Output"
    #Node properties

    driver = emission_glow.nodes.new("ShaderNodeValue")
    driver.location = [-693, -152]
    driver.name = "driver"
    driver.label = "driver"
    #Node properties
    #node I/O
    node_driver = driver.outputs["Value"].driver_add('default_value')
    if bpy.context.preferences.filepaths.use_scripts_auto_execute:
        node_driver.driver.expression = '(frame-bpy.context.scene.frame_start)/(bpy.context.scene.frame_end+1-bpy.context.scene.frame_start)'
    else:
        node_driver.driver.expression = '(frame-frame_start)/(frame_end+1-frame_start)'

        # create frame start variable
        frame_start = node_driver.driver.variables.new()
        frame_start.name = 'frame_start'
        frame_start.targets[0].id_type = 'SCENE'
        frame_start.targets[0].id = bpy.context.scene
        frame_start.targets[0].data_path = 'frame_start'

        # create frame end variable
        frame_end = node_driver.driver.variables.new()
        frame_end.name = 'frame_end'
        frame_end.targets[0].id_type = 'SCENE'
        frame_end.targets[0].id = bpy.context.scene
        frame_end.targets[0].data_path = 'frame_end'
    
    Math = emission_glow.nodes.new("ShaderNodeMath")
    Math.location = [-733, 68]
    Math.name = "Math"
    #Node properties
    Math.operation = "MULTIPLY"
    Math.use_clamp = False
    #node I/O
    Math.inputs[0].default_value = 0
    Math.inputs[1].default_value = pi*2
    Math.inputs[2].default_value = 0.0

    Math_003 = emission_glow.nodes.new("ShaderNodeMath")
    Math_003.location = [550, -109]
    Math_003.name = "Math_003"
    #Node properties
    Math_003.operation = "ABSOLUTE"
    Math_003.use_clamp = True

    Group_Input = emission_glow.nodes.new("NodeGroupInput")
    Group_Input.location = [-1751, -35]
    Group_Input.name = "Group_Input"
    #Node properties

    Mix = emission_glow.nodes.new("ShaderNodeMixRGB")
    Mix.location = [1065, 432]
    Mix.name = "Mix"
    #Node properties
    Mix.blend_type = "MIX"
    Mix.use_clamp = False
    #node I/O
    Mix.inputs["Fac"].default_value = 0.0
    Mix.inputs["Color1"].default_value = [0.5, 0.5, 0.5, 1.0]
    Mix.inputs["Color2"].default_value = [0.5, 0.5, 0.5, 1.0]

    Emission_Multi = emission_glow.nodes.new("ShaderNodeMath")
    Emission_Multi.location = [782, -113]
    Emission_Multi.name = "Emission_Multi"
    Emission_Multi.label = "Emission Multi"
    #Node properties
    Emission_Multi.operation = "MULTIPLY_ADD"
    Emission_Multi.use_clamp = False
    #node I/O
    Emission_Multi.inputs[0].default_value = 0.5
    Emission_Multi.inputs[1].default_value = 0.0
    Emission_Multi.inputs[2].default_value = 0.0

    Reroute_010 = emission_glow.nodes.new("NodeReroute")
    Reroute_010.location = [993, -874]
    Reroute_010.name = "Reroute_010"
    #Node properties

    Math_006 = emission_glow.nodes.new("ShaderNodeMath")
    Math_006.location = [345, 110]
    Math_006.name = "Math_006"
    Math_006.label = "Transition Sharp"
    #Node properties
    Math_006.operation = "MULTIPLY"
    Math_006.use_clamp = False
    #node I/O


    Color_MIx = emission_glow.nodes.new("ShaderNodeMixRGB")
    Color_MIx.location = [948, 1000]
    Color_MIx.name = "Color_MIx"
    Color_MIx.label = "Color MIx"
    #Node properties
    Color_MIx.blend_type = "MIX"
    Color_MIx.use_clamp = False
    #node I/O
    Color_MIx.inputs["Fac"].default_value = 0.5
    Color_MIx.inputs["Color1"].default_value = [1.0, 0.702504575252533, 0.6747211813926697, 1.0]
    Color_MIx.inputs["Color2"].default_value = [0.0, 0.0, 0.0, 1.0]

    Reroute_012 = emission_glow.nodes.new("NodeReroute")
    Reroute_012.location = [969, 152]
    Reroute_012.name = "Reroute_012"
    #Node properties

    Invert = emission_glow.nodes.new("ShaderNodeInvert")
    Invert.location = [916, 760]
    Invert.name = "Invert"
    #Node properties
    #node I/O
    Invert.inputs["Fac"].default_value = 1.0
    Invert.inputs["Color"].default_value = [0.0, 0.0, 0.0, 1.0]
    #group llinks
    emission_glow.links.new(Emission_Multi.outputs[0], Emission.inputs["Strength"])
    emission_glow.links.new(Color_MIx.outputs["Color"], Emission.inputs["Color"])
    emission_glow.links.new(Math_003.outputs[0], Emission_Multi.inputs[0])
    emission_glow.links.new(Math_006.outputs[0], Math_005.inputs[0])
    emission_glow.links.new(Node.outputs[0], Math_006.inputs[0])
    emission_glow.links.new(Math_006.outputs[0], Math_003.inputs[0])
    emission_glow.links.new(Reroute_005.outputs["Output"], Math_006.inputs[1])
    emission_glow.links.new(Reroute_004.outputs["Output"], Reroute_005.inputs["Input"])
    emission_glow.links.new(Invert.outputs["Color"], Color_MIx.inputs["Fac"])
    emission_glow.links.new(Math_002.outputs[0], Math_007.inputs[0])
    emission_glow.links.new(driver.outputs["Value"], Math_002.inputs[1])
    emission_glow.links.new(Math.outputs[0], Math_002.inputs[0])
    emission_glow.links.new(Math_007.outputs[0], Node.inputs[0])
    emission_glow.links.new(Func_Offset_deg.outputs[0], Math_007.inputs[1])
    emission_glow.links.new(Reroute_007.outputs["Output"], Emission_Multi.inputs[1])
    emission_glow.links.new(Reroute_006.outputs["Output"], Reroute_007.inputs["Input"])
    emission_glow.links.new(Reroute_008.outputs["Output"], Emission_Multi.inputs[2])
    emission_glow.links.new(Reroute_009.outputs["Output"], Reroute_008.inputs["Input"])
    emission_glow.links.new(Math_005.outputs[0], Mix.inputs["Color1"])
    emission_glow.links.new(Mix.outputs["Color"], Invert.inputs["Color"])
    emission_glow.links.new(Math_001.outputs[0], Mix.inputs["Color2"])
    emission_glow.links.new(Math_006.outputs[0], Math_001.inputs[0])
    emission_glow.links.new(Reroute_012.outputs["Output"], Mix.inputs["Fac"])
    emission_glow.links.new(Reroute_011.outputs["Output"], Reroute_010.inputs["Input"])
    emission_glow.links.new(Reroute_010.outputs["Output"], Reroute_012.inputs["Input"])
    emission_glow.links.new(Group_Input.outputs[0], Math.inputs[0])
    emission_glow.links.new(Group_Input.outputs[1], Reroute_004.inputs["Input"])
    emission_glow.links.new(Group_Input.outputs[2], Reroute_006.inputs["Input"])
    emission_glow.links.new(Group_Input.outputs[3], Color_MIx.inputs["Color1"])
    emission_glow.links.new(Group_Input.outputs[4], Color_MIx.inputs["Color2"])
    emission_glow.links.new(Group_Input.outputs[5], Func_Offset_deg.inputs["Value"])
    emission_glow.links.new(Group_Input.outputs[6], Reroute_009.inputs["Input"])
    emission_glow.links.new(Group_Input.outputs[7], Reroute_011.inputs["Input"])
    emission_glow.links.new(Emission.outputs["Emission"], Group_Output.inputs[0])
    emission_glow.links.new(Math_006.outputs["Value"], Group_Output.inputs[1])
    Group_Input.outputs[0].name = "Cycle Count"
    emission_glow.inputs[0].name = "Cycle Count"
    Group_Input.outputs[1].name = "Transition Sharp"
    emission_glow.inputs[1].name = "Transition Sharp"
    Group_Input.outputs[2].name = "Emit Multiplier"
    emission_glow.inputs[2].name = "Emit Multiplier"
    Group_Input.outputs[3].name = "Color1"
    emission_glow.inputs[3].name = "Color1"
    Group_Input.outputs[4].name = "Color2"
    emission_glow.inputs[4].name = "Color2"
    Group_Input.outputs[5].name = "Func Offset (deg)"
    emission_glow.inputs[5].name = "Func Offset (deg)"
    Group_Input.outputs[6].name = "Emit Offset"
    emission_glow.inputs[6].name = "Emit Offset"
    Group_Input.outputs[7].name = "Color Blend"
    emission_glow.inputs[7].name = "Color Blend"
    Group_Output.inputs[0].name = "Emission"
    emission_glow.outputs[0].name = "Emission"
    Group_Output.inputs[1].name = "Cosine"
    emission_glow.outputs[1].name = "Cosine"
    emission_glow.inputs["Cycle Count"].min_value = 0.0
    emission_glow.inputs["Cycle Count"].max_value = 10000.0
    emission_glow.inputs["Transition Sharp"].min_value = 0.0
    emission_glow.inputs["Transition Sharp"].max_value = 10000.0
    emission_glow.inputs["Emit Multiplier"].min_value = -10000.0
    emission_glow.inputs["Emit Multiplier"].max_value = 10000.0
    emission_glow.inputs["Func Offset (deg)"].min_value = -10000.0
    emission_glow.inputs["Func Offset (deg)"].max_value = 10000.0
    emission_glow.inputs["Emit Offset"].min_value = 0.0
    emission_glow.inputs["Emit Offset"].max_value = 3.4028234663852886e+38
    emission_glow.inputs["Color Blend"].min_value = 0.0
    emission_glow.inputs["Color Blend"].max_value = 1.0

    #group dumped


    return emission_glow
