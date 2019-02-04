import os
import bpy
import bmesh
from bpy.props import *
from math import pi, radians
import bpy.utils.previews
from random import choice

#Clean Off Bevel and Sharps In Edit Mode
class unsharpOperatorE(bpy.types.Operator):
    '''Clear Off Sharps And Bevels'''
    bl_idname = "clean1.objects"
    bl_label = "UnsharpBevelE"
    bl_options = {'REGISTER', 'UNDO'}

    clearsharps = BoolProperty(default = True)
    clearbevel = BoolProperty(default = True)
    clearcrease = BoolProperty(default = True)

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        # DRAW YOUR PROPERTIES IN A BOX
        box.prop( self, 'clearsharps', text = "Clear Sharps")
        box.prop( self, 'clearbevel', text = "Clear Bevels")
        box.prop( self, 'clearcrease', text = "Clear Crease")

    def execute(self, context):
        #clear stuff
        clearsharps = self.clearsharps
        clearbevel = self.clearbevel
        clearcrease = self.clearcrease
        #bpy.ops.object.mode_set(mode='EDIT')
        #bpy.ops.mesh.select_all(action='DESELECT')
        #bpy.ops.mesh.select_all(action='TOGGLE')
        if clearsharps == True:
            bpy.ops.mesh.mark_sharp(clear=True)
        if clearbevel == True:
            bpy.ops.transform.edge_bevelweight(value=-1)
        if clearcrease == True:
            bpy.ops.transform.edge_crease(value=-1)
        #bpy.ops.object.editmode_toggle()
        #bpy.ops.object.shade_flat()
        #bpy.ops.object.modifier_remove(modifier="Bevel")
        #bpy.ops.object.modifier_remove(modifier="Solidify")

        return {'FINISHED'}

#Bevel and Sharps In Edit Mode to Selection
class sharpandbevelOperatorE(bpy.types.Operator):
    '''Mark Sharps And Bevels In Edit Mode'''
    bl_idname = "bevelandsharp1.objects"
    bl_label = "SharpBevelE"
    bl_options = {'REGISTER', 'UNDO'}

    marksharps = BoolProperty(default = True)
    markbevel = BoolProperty(default = True)
    markcrease = BoolProperty(default = True)

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        # DRAW YOUR PROPERTIES IN A BOX
        box.prop( self, 'marksharps', text = "Mark Sharps")
        box.prop( self, 'markbevel', text = "Mark Bevels")
        box.prop( self, 'markcrease', text = "Mark Crease")

    def execute(self, context):
        marksharps = self.marksharps
        markbevel = self.markbevel
        markcrease = self.markcrease

        #(former)
        #bpy.ops.transform.edge_bevelweight(value=1)
        #bpy.ops.transform.edge_crease(value=1)
        #bpy.ops.mesh.mark_sharp()

        if marksharps == True:
            bpy.ops.mesh.mark_sharp()
        if markbevel == True:
            bpy.ops.transform.edge_bevelweight(value=1)
        if markcrease == True:
            bpy.ops.transform.edge_crease(value=1)

        return {'FINISHED'}

#############################
#Multi-CSharp
#############################

class multicsharpOperator(bpy.types.Operator):
    """Multi CSharp"""
    bl_idname = "multi.csharp"
    bl_label = "Multi Object Csharp"

    @classmethod
    def poll(cls, context):

        obj_type = context.object.type
        return(obj_type in {'MESH'})
        return context.active_object is not None

    def execute(self, context):


        sel = bpy.context.selected_objects
        active = bpy.context.scene.objects.active.name

        for ob in sel:
                ob = ob.name
                bpy.context.scene.objects.active = bpy.data.objects[ob]
                bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, texture=False, animation=False)
                bpy.ops.hops.complex_sharpen()
        return {'FINISHED'}

#############################
#Multi-SSharp
#############################

class multissharpOperator(bpy.types.Operator):
    """Multi SSharp"""
    bl_idname = "multi.ssharp"
    bl_label = "Multi Object Ssharp"

    @classmethod
    def poll(cls, context):

        obj_type = context.object.type
        return(obj_type in {'MESH'})
        return context.active_object is not None

    def execute(self, context):

        sel = bpy.context.selected_objects
        active = bpy.context.scene.objects.active.name

        for ob in sel:
                ob = ob.name
                bpy.context.scene.objects.active = bpy.data.objects[ob]
                #bpy.ops.ssharpen.objects(ssharpangle=30, alternatemode=False)
                bpy.ops.hops.soft_sharpen()
        return {'FINISHED'}

#############################
#Multi-Clear
#############################

class multiClearOperator(bpy.types.Operator):
    """Multi Clear"""
    bl_idname = "multi.clear"
    bl_label = "Multi Ssharp Clear"

    @classmethod
    def poll(cls, context):

        obj_type = context.object.type
        return(obj_type in {'MESH'})
        return context.active_object is not None

    def execute(self, context):


        sel = bpy.context.selected_objects
        active = bpy.context.scene.objects.active.name

        for ob in sel:
                ob = ob.name
                bpy.context.scene.objects.active = bpy.data.objects[ob]

                #bpy.ops.clean.objects() This doesnt exist anymore
                bpy.ops.clean.sharps()

        return {'FINISHED'}


"""
#############################
#Sharpen Operators Start Here
#############################

class csharpenOperator(bpy.types.Operator): #now Csharp 2.0
    '''Sharpen With Modifiers and Bevelling'''
    bl_description = "Sharpens The Mesh And Adds Bevelling On Sharps"
    bl_idname = "csharpen.objects"
    bl_label = "CSharpen"
    bl_options = {'REGISTER', 'UNDO'}

    items = [(x.identifier, x.name, x.description, x.icon)
             for x in bpy.types.Modifier.bl_rna.properties['type'].enum_items]

    modtypes = EnumProperty(name="Modifier Types",
                           items=[(id, name, desc, icon, 2**i) for i, (id, name, desc, icon) in enumerate(items)
                                   if id in ['BOOLEAN', 'MIRROR', 'BEVEL', 'SOLIDIFY', 'SUBSURF', 'ARRAY']],
                           description="Don't apply these",
                           default={'BEVEL', 'MIRROR', 'SUBSURF','ARRAY'},
                           options={'ENUM_FLAG'})

    angle = FloatProperty(name="AutoSmooth Angle",
                          description="Set AutoSmooth angle",
                          default= radians(60.0),
                          min = 0.0,
                          max = radians(180.0),
                          subtype='ANGLE')

    bevelwidth = FloatProperty(name="Bevel Width Amount",
                               description="Set Bevel Width",
                               default=0.0200,
                               min =
                               0.002,
                               max =0.25)

    ssharpangle = FloatProperty(name="SSharpening Angle", description="Set SSharp Angle", default = 30.0, min = 0.0, max = 180.0)

    segmentamount = IntProperty(name="Segments", description = "Segments For Bevel", default = 3, min = 1, max = 12)

    togglesharpening = BoolProperty(default = True)

    apply_all = BoolProperty(default = True)

    original_bevel = FloatProperty()

    subdoption = BoolProperty(default = False)

    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob is None:
            return False
        return (ob.type == 'MESH')

        #F6 MENU
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        # DRAW YOUR PROPERTIES IN A BOX
        #box.prop( self, 'ssharpangle', text = "SsharpAngle")
        col = box.column()
        col.prop(self, "modtypes", expand=True)
        box.prop( self, 'angle', text = "SmoothingAngle" )
        box.prop( self, 'ssharpangle', text = "SSharp Angle")
        box.prop( self, 'bevelwidth', text = "BevelWidth")
        box.prop( self, 'segmentamount', text = "BevelSegments")
        box.prop( self, 'apply_all', text = "ApplyAll")
        box.prop( self, 'togglesharpening', text = "ToggleSsharp")
        box.prop( self, 'subdoption', text = "Sub-D Sharpening")


    def execute(self, context):
        scene = context.scene
        ob = context.object  # soapbox call don't use bpy.context as context is passed
        obs = context.selected_objects
        angle = self.angle
        segmentamount = self.segmentamount
        original_bevel = self.original_bevel
        bevelwidth = self.bevelwidth
        ssharpangle = self.ssharpangle
        subdoption = self.subdoption
        ssharpangle = ssharpangle * (3.14159265359/180)
        #global cstepmode
        b = bpy.context.active_object

        #Sets Original Bevel To Initial Value
        #original_bevel = 0.2

        mod_dic = {}
        if self.apply_all:
            #remove modifiers no one would want applied in this instance

            #bpy.ops.object.modifier_remove(modifier="Bevel")
            #bpy.ops.object.modifier_remove(modifier="Solidify")

            # replace with
            mods = [m for m in ob.modifiers if m.type in self.modtypes]
            for mod in mods:

                mod_dic[mod.name] = {k:getattr(mod, k) for k in mod.bl_rna.properties.keys()
                                     if k not in ["rna_type"]}
                #print(mod_dic)
                ob.modifiers.remove(mod)

            #convert to mesh for sanity
            #bpy.ops.object.convert(target='MESH')
            #Object.to_mesh(scene, apply_modifiers, settings, calc_tessface=True, calc_undeformed=False)

            mesh_name = ob.data.name
            ob.data.name = 'XXXX'
            # remove the old mesh
            if not ob.data.users:
                bpy.data.meshes.remove(ob.data)
            mesh = ob.to_mesh(scene, True, 'PREVIEW') # or 'RENDER'
            ob.modifiers.clear()
            mesh.name = mesh_name
            ob.data = mesh

            for name, settings in mod_dic.items():
                m = ob.modifiers.new(name, settings["type"])
                for s, v in settings.items():
                    if s == "type":
                        continue
                    setattr(m, s, v)

            #Attempting to toggle Ssharpening on Csharp
            if self.togglesharpening:
                #Start In Edit Mode
                bpy.ops.object.mode_set(mode='EDIT')

                #Unhide all The Geo!
                bpy.ops.mesh.reveal()

                #then do the ssharp operator stuff.

                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
                bpy.ops.mesh.select_all(action='DESELECT')

                #Sharpening now using the ssharpangle parameter.
                bpy.ops.mesh.edges_select_sharp(sharpness=ssharpangle)

                if subdoption == True:        #sets up for subd- no sharp/crease/
                    bpy.ops.transform.edge_bevelweight(value=1)
                    bpy.ops.transform.edge_crease(value=-1)
                    bpy.ops.mesh.mark_sharp(clear=True)
                else:
                    bpy.ops.transform.edge_bevelweight(value=1)
                    bpy.ops.transform.edge_crease(value=1)
                    bpy.ops.mesh.mark_sharp()


                #bpy.ops.transform.edge_bevelweight(value=1)
                #bpy.ops.transform.edge_crease(value=1)
                #bpy.ops.mesh.mark_sharp()

                bpy.ops.object.editmode_toggle()

                bpy.context.object.data.auto_smooth_angle = angle

            else:
                bpy.context.object.data.auto_smooth_angle = angle

            try :
                context.object.modifiers["Bevel"]
            except:
                bpy.context.object.modifiers.new("Bevel", "BEVEL")
                #bpy.ops.object.modifier_add(type='BEVEL')
                bpy.context.object.modifiers["Bevel"].use_clamp_overlap = False
                bpy.context.object.modifiers["Bevel"].show_in_editmode = False
                bpy.context.object.modifiers["Bevel"].width = bevelwidth
                bpy.context.object.modifiers["Bevel"].segments = segmentamount
                bpy.context.object.modifiers["Bevel"].profile = 0.70
                bpy.context.object.modifiers["Bevel"].limit_method = 'WEIGHT'
                bpy.context.object.modifiers["Bevel"].show_in_editmode = True

                #print("Added bevel modifier")

            #bpy.context.object.modifiers["Bevel"].width = bevelwidth
            bpy.context.object.modifiers["Bevel"].segments = segmentamount

            if subdoption == True: #allows for sub-d to turn off autosmooth
                bpy.context.object.data.use_auto_smooth = False
                bpy.context.object.modifiers["Bevel"].segments = 2
                bpy.context.object.modifiers["Bevel"].profile = 1
            else:
                bpy.context.object.data.use_auto_smooth = True
                bpy.ops.object.shade_smooth()

            bpy.ops.object.select_all(action='DESELECT')

            b.select = True
            bpy.ops.object.shade_smooth()

            text = "(C)Sharpen - Mesh Sharpened w/Bevel"

        return {'FINISHED'}

#SharpenMesh But Don't Bevel Edges AKA SSharpen (Now SSharp2.0)
class softsharpenOperator(bpy.types.Operator):
    '''Sharpen Without Modifiers'''
    bl_description = "Sharpens The Mesh And Without Bevelling On Sharps"
    bl_idname = "ssharpen.objects"
    bl_label = "softSharpen"
    bl_options = {'REGISTER', 'UNDO'}

    angle = FloatProperty(name="AutoSmooth Angle",
                          description="Set AutoSmooth angle",
                          default= radians(60.0),
                          min = 0.0,
                          max = radians(180.0),
                          subtype='ANGLE')


    ssharpangle = FloatProperty(name="SSharpening Angle", description="Set SSharp Angle", default= 30.0, min = 0.0, max = 180.0)

    subdoption = BoolProperty(default = False)

    alternatemode = BoolProperty(default = True)

    cstepmode = BoolProperty(default = False)

    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob is None:
            return False
        return (ob.type == 'MESH')

    def draw(self, context):
        layout = self.layout
        box = layout.box()

        box.prop( self, 'ssharpangle', text = "SsharpAngle" )
        box.prop( self, 'angle', text = "SmoothingAngle" )
        box.prop( self, 'alternatemode', text = "Additive Mode")
        box.prop( self, 'subdoption', text = "Sub-D Sharpening")

       # AR = cant make it work for global variable
        box.prop( self,'cstepmode', text = "cStep fix")

    #If - Default Calculation / Else - Replacive Calculation
    def execute(self, context):

        scene = context.scene
        ob = context.object  # soapbox call don't use bpy.context as context is passed
        obs = context.selected_objects
        angle = self.angle
        subdoption = self.subdoption

        ssharpangle = self.ssharpangle
        ssharpangle = ssharpangle * (3.14159265359/180)

        if self.alternatemode:
            #Start In Edit Mode
            bpy.ops.object.mode_set(mode='EDIT')

            #Unhide all The Geo!
            bpy.ops.mesh.reveal()

            #Now Sharpen It
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
            bpy.ops.mesh.select_all(action='DESELECT')

            #Selects Sharps From A Nothing Selection
            bpy.ops.mesh.edges_select_sharp(sharpness=ssharpangle)

            #And Then Adds Weight / Crease / Sharp
            #Added Option To Toggle Not Doing That
            if subdoption == True:
                bpy.ops.transform.edge_bevelweight(value=1)
                bpy.ops.transform.edge_crease(value=-1)
                bpy.ops.mesh.mark_sharp(clear=True)
            else:
                bpy.ops.transform.edge_bevelweight(value=1)
                bpy.ops.transform.edge_crease(value=1)
                bpy.ops.mesh.mark_sharp()

            #Comes Out Of Edit Mode
            bpy.ops.object.editmode_toggle()
            bpy.context.object.data.auto_smooth_angle = angle

        else:
            #Start In Edit Mode
            bpy.ops.object.mode_set(mode='EDIT')

            #Unhide all The Geo!
            bpy.ops.mesh.reveal()

            #Clear SSharps Then Redo It
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_all(action='TOGGLE')

            #AR suggested using -1s instead of Zeroes
            bpy.ops.transform.edge_bevelweight(value=-1)
            bpy.ops.mesh.mark_sharp(clear=True)
            bpy.ops.transform.edge_crease(value=-1)

            #Now Sharpen It
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
            bpy.ops.mesh.select_all(action='DESELECT')

            #Selects Sharps From A Nothing Selection
            bpy.ops.mesh.edges_select_sharp(sharpness=ssharpangle)

            #And Then Adds Weight / Crease / Sharp or not.
            if subdoption == True:        #sets up for subd- no sharp/crease/
                bpy.ops.transform.edge_bevelweight(value=1)
                bpy.ops.transform.edge_crease(value=-1)
                bpy.ops.mesh.mark_sharp(clear=True)
            else:
                bpy.ops.transform.edge_bevelweight(value=1)
                bpy.ops.transform.edge_crease(value=1)
                bpy.ops.mesh.mark_sharp()

            #Comes Out Of Edit Mode
            bpy.ops.object.editmode_toggle()
            bpy.context.object.data.auto_smooth_angle = angle

        if subdoption == True: #allows for sub-d to turn off autosmooth
            bpy.context.object.data.use_auto_smooth = False
        else:
            bpy.context.object.data.use_auto_smooth = True

        bpy.ops.object.shade_smooth()

        text = "(S)Sharpen - Mesh Sharpened"


        return {'FINISHED'}

class xsharpenOperator(bpy.types.Operator):
    '''Sharpen Test'''
    bl_idname = "xsharpen.objects"
    bl_label = "XSharpen"
    bl_options = {'REGISTER', 'UNDO'}

    ssharpangle = FloatProperty(name="SSharpening Angle", description="Set SSharp Angle", default= 30.0, min = 0.0, max = 180.0)

    angle = FloatProperty(name="AutoSmooth Angle", description="Set AutoSmooth angle", default= 60.0, min = 0.0, max = 180.0)

    bevelwidth = FloatProperty(name="Bevel Width Amount", description="Set Bevel Width", default= 0.0071, min = 0.002, max = .25)

    def execute(self, context):

        #convert angle
        ob = bpy.context.selected_objects
        angle = self.angle
        ssharpangle = self.ssharpangle
        angle = angle * (3.14159265359/180)
        #ssharpangle = self.ssharpangle
        ssharpangle = ssharpangle * (3.14159265359/180)

        #angle = bpy.context.object.data.auto_smooth_angle
        bevelwidth = self.bevelwidth

        #Sets the Bevel Width To The Orig Bevel Width
        #bevelwidth = bpy.context.object.modifiers["Bevel"].width

        #apply the scale to keep me sane
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        #remove modifiers
        bpy.ops.object.modifier_remove(modifier="Bevel")
        bpy.ops.object.modifier_remove(modifier="Solidify")
        #so that the csharp doesnt mesh up the object

        #converts to mesh because it makes sense
        bpy.ops.object.convert(target='MESH')

        #Start In Edit Mode
        bpy.ops.object.mode_set(mode='EDIT')

        #Unhide all The Geo!
        bpy.ops.mesh.reveal()

        #Clear SSharps Then Redo It
        #bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
        #bpy.ops.mesh.select_all(action='DESELECT')
        #bpy.ops.mesh.select_all(action='TOGGLE')

        #AR suggested using -1s instead of Zeroes
        #bpy.ops.transform.edge_bevelweight(value=-1)
        #bpy.ops.mesh.mark_sharp(clear=True)
        #bpy.ops.transform.edge_crease(value=-1)

        #then do the csharp operator stuff.
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
        bpy.ops.mesh.select_all(action='DESELECT')

        #Sharpening now using the ssharpangle parameter.
        bpy.ops.mesh.edges_select_sharp(sharpness=ssharpangle)


        bpy.ops.transform.edge_bevelweight(value=1)
        bpy.ops.transform.edge_crease(value=1)
        bpy.ops.mesh.mark_sharp()
        bpy.ops.object.editmode_toggle()

        #keep the old here for now
        bpy.ops.object.modifier_add(type='BEVEL')
        context.object.modifiers["Bevel"].use_clamp_overlap = False
        context.object.modifiers["Bevel"].show_in_editmode = False
        context.object.modifiers["Bevel"].width = 0.0071
        #context.object.modifiers["Bevel"].segments = 3
        context.object.modifiers["Bevel"].profile = 0.70
        context.object.modifiers["Bevel"].limit_method = 'WEIGHT'
        context.object.modifiers["Bevel"].show_in_editmode = True


        #Sets Bevel To Bevel Width
        context.object.modifiers["Bevel"].width = bevelwidth

        context.object.data.use_auto_smooth = True

        #now sets angle to Var angle.
        context.object.data.auto_smooth_angle = angle


        bpy.ops.object.shade_smooth()
        return {'FINISHED'}

#Solidify and Bevel Edges
class solidOperator(bpy.types.Operator):
    '''Solidify Mod And Bevel The Edges'''
    bl_description = "Sharpens The Mesh And Adds Thickness"
    bl_idname = "solidify.objects"
    bl_label = "EdgeSolidify"
    bl_options = {'REGISTER', 'UNDO'}

    #Declare Some Variables Here
    tthick = FloatProperty(name="ThickeningAmount", description="Set Thickness Amount", default= .1, min = 0.001, max = 4.0)

    angle = FloatProperty(name="AutoSmooth Angle", description="Set AutoSmooth angle", default= 60.0, min = 0.0, max = 180.0)

    bevelwidth = FloatProperty(name="Bevel Width Amount", description="Set Bevel Width", default= 0.01, min = 0.002, max = .25)

    ssharpangle = FloatProperty(name="SSharpening Angle", description="Set SSharp Angle", default= 30.0, min = 0.0, max = 180.0)

    bevelmodiferon = BoolProperty(default = True)

    sharpenon = BoolProperty(default = True)

    def draw(self, context):
        layout = self.layout

        box = layout.box()

        box.prop( self, 'tthick', text = "Thickness" )
        box.prop( self, 'bevelwidth', text = "Bevel Width" )
        box.prop( self, 'bevelmodiferon', text = "Bevel ON/OFF")
        box.prop( self, 'ssharpangle', text = "(S)Sharpen Angle")
        box.prop( self, 'sharpenon', text = "(S)Sharpen ON/OFF")

    def execute(self, context):
        #convert angle
        bevelwidth = self.bevelwidth
        ssharpangle = self.ssharpangle
        tthick = self.tthick
        ob = bpy.context.selected_objects
        angle = self.angle
        sharpenon = self.sharpenon
        angle = angle * (3.14159265359/180)
        ssharpangle = ssharpangle * (3.14159265359/180)

        #start off removing solidify and bevel to avoid issues later.
        bpy.ops.object.modifier_remove(modifier="Bevel")
        bpy.ops.object.modifier_remove(modifier="Solidify")

        #go into edit mode and select nothing then select all
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_all(action='TOGGLE')

        #convert to Loop and Mark Sharp + Beveling
        bpy.ops.mesh.region_to_loop()
        bpy.ops.transform.edge_bevelweight(value=1)
        bpy.ops.mesh.mark_sharp()

        if self.sharpenon:
            #Unhide all The Geo!
            bpy.ops.mesh.reveal()

            #Clear SSharps Then Redo It
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
            bpy.ops.mesh.select_all(action='DESELECT')
            #bpy.ops.mesh.select_all(action='TOGGLE')

            bpy.ops.mesh.edges_select_sharp(sharpness=ssharpangle)

            #AR suggested using -1s instead of Zeroes
            bpy.ops.transform.edge_bevelweight(value=-1)
            bpy.ops.mesh.mark_sharp(clear=True)
            bpy.ops.transform.edge_crease(value=-1)

        bpy.ops.object.editmode_toggle()

        if self.bevelmodiferon:
            #add Bevel
            bpy.ops.object.modifier_add(type='BEVEL')
            bpy.context.object.modifiers["Bevel"].use_clamp_overlap = False
            bpy.context.object.modifiers["Bevel"].show_in_editmode = False
            bpy.context.object.modifiers["Bevel"].width = bevelwidth
            #bpy.context.object.modifiers["Bevel"].segments = 3
            bpy.context.object.modifiers["Bevel"].profile = 0.734346
            bpy.context.object.modifiers["Bevel"].limit_method = 'WEIGHT'
            #bpy.context.object.modifiers["Bevel"].angle_limit = angle
            bpy.context.object.modifiers["Bevel"].show_in_editmode = True



        #add Solidify
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        bpy.ops.object.modifier_move_up(modifier="Solidify")
        bpy.context.object.modifiers["Solidify"].thickness = tthick
        bpy.context.object.modifiers["Solidify"].offset = 0
        bpy.context.object.modifiers["Solidify"].use_even_offset = True
        bpy.context.object.modifiers["Solidify"].material_offset_rim = 1
        bpy.context.object.modifiers["Solidify"].material_offset = 2
        bpy.context.object.modifiers["Solidify"].show_in_editmode = False

        #set Smoothing
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = angle
        bpy.ops.object.shade_smooth()

        return {'FINISHED'}


#Clean Off Bevel and Sharps In Object Mode (now with options to remove modifiers)
class unsharpOperator(bpy.types.Operator):
    '''Clear Off Sharps And Bevels'''
    bl_idname = "clean.objects"
    bl_label = "UnsharpBevel"
    bl_options = {'REGISTER', 'UNDO'}

    removeMods = BoolProperty(default = True)

    clearsharps = BoolProperty(default = True)
    clearbevel = BoolProperty(default = True)
    clearcrease = BoolProperty(default = True)

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        # DRAW YOUR PROPERTIES IN A BOX
        box.prop( self, 'removeMods', text = "RemoveModifiers?")
        box.prop( self, 'clearsharps', text = "Clear Sharps")
        box.prop( self, 'clearbevel', text = "Clear Bevels")
        box.prop( self, 'clearcrease', text = "Clear Crease")

    def execute(self, context):
        clearsharps = self.clearsharps
        clearbevel = self.clearbevel
        clearcrease = self.clearcrease

        bpy.ops.object.mode_set(mode='EDIT')

        #Unhide all The Geo!
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
        #bpy.ops.mesh.select_all(action='DESELECT')
        #bpy.ops.mesh.select_all(action='TOGGLE')

        if clearsharps == True:
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_all(action='TOGGLE')

            bpy.ops.mesh.mark_sharp(clear=True)
        if clearbevel == True:
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_all(action='TOGGLE')

            bpy.ops.transform.edge_bevelweight(value=-1)
        if clearcrease == True:
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_all(action='TOGGLE')

            bpy.ops.transform.edge_crease(value=-1)

        #AR suggested using -1s instead of Zeroes
        bpy.ops.transform.edge_bevelweight(value=-1)
        bpy.ops.mesh.mark_sharp(clear=True)
        bpy.ops.transform.edge_crease(value=-1)

        #Now Get Rid of Modifiers/SetSmooth
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.shade_flat()

        if self.removeMods:
            bpy.ops.object.modifier_remove(modifier="Bevel")
            bpy.ops.object.modifier_remove(modifier="Solidify")

        else:
            bpy.context.object.modifiers["Bevel"].limit_method = 'ANGLE'
            bpy.context.object.modifiers["Bevel"].angle_limit = 0.785398
            #return {'FINISHED'}

        return {'FINISHED'}"""

