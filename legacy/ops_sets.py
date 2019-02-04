import os
import bpy
import bmesh
from bpy.props import *
from math import pi, radians
import bpy.utils.previews
from random import choice
from .. utils.addons import addon_exists

#############################
#RenderSet1
#############################    
    
#Sets Up The Render / As Always
class renset1Operator(bpy.types.Operator):
    "Typical Starter Render Settings"
    bl_idname = "render.setup"
    bl_label = "RenderSetup"
    bl_options = {'REGISTER', 'UNDO'}
    
    colmgm = BoolProperty(default = False)
    
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.prop( self, 'colmgm', text = "Optura 981113")
        
    def execute(self, context):
        bpy.context.scene.cycles.progressive = 'PATH'
        bpy.context.scene.cycles.sample_clamp_indirect = 2
        bpy.context.scene.cycles.sample_clamp_direct = 2
        bpy.context.scene.cycles.use_square_samples = True
        bpy.context.scene.cycles.preview_samples = 30
        bpy.context.scene.cycles.samples = 15
        bpy.context.scene.cycles.min_bounces = 5
        bpy.context.scene.cycles.glossy_bounces = 16
        bpy.context.scene.cycles.diffuse_bounces = 16
        bpy.context.scene.cycles.blur_glossy = 0.8
        bpy.context.scene.world.cycles.sample_as_light = True
        bpy.context.scene.world.cycles.sample_map_resolution = 512
        #Added A Look Option Too.
        if self.colmgm:  
            bpy.context.scene.view_settings.look = 'Canon Optura 981113'
            bpy.context.scene.view_settings.gamma = 1.04115
            bpy.context.scene.view_settings.exposure = 0
        else:
            bpy.context.scene.view_settings.exposure = 0
        return {'FINISHED'}

#############################
#RenderSet2
#############################

#Sets Up The Render / As Always
class rensetBOperator(bpy.types.Operator):
    "Branched Render Settings"
    bl_idname = "renderb.setup"
    bl_label = "RenderSetupb"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.context.scene.cycles.progressive = 'BRANCHED_PATH'
        bpy.context.scene.cycles.sample_clamp_direct = 2
        bpy.context.scene.cycles.sample_clamp_indirect = 0.2
        bpy.context.scene.cycles.aa_samples = 5
        bpy.context.scene.cycles.preview_aa_samples = 5
        bpy.context.scene.cycles.glossy_samples = 1
        bpy.context.scene.cycles.transmission_samples = 1
        bpy.context.scene.cycles.ao_samples = 1
        bpy.context.scene.cycles.mesh_light_samples = 1
        bpy.context.scene.cycles.subsurface_samples = 1
        bpy.context.scene.cycles.volume_samples = 1
        bpy.context.scene.cycles.diffuse_samples = 1
        bpy.context.scene.cycles.sample_all_lights_direct = True
        bpy.context.scene.cycles.sample_all_lights_indirect = True
        bpy.context.scene.world.cycles.sample_as_light = False
        return {'FINISHED'}

#############################
#Set UI Ops Start Here
#############################

#Return The UI Back To Normal
class reguiOperator(bpy.types.Operator):
    "Turns On Stuff I'd Turn Off"
    bl_idname = "ui.reg"
    bl_label = "regViewport"   
    
    def execute(self, context):
        bpy.context.space_data.show_floor = True
        bpy.context.space_data.show_relationship_lines = True
        bpy.context.space_data.show_only_render = False
        bpy.context.space_data.use_matcap = False
        if addon_exists("silhouette"):
            if bpy.context.scene.silhouette.show_silhouette:
                bpy.context.scene.silhouette.show_silhouette = False
        return {'FINISHED'}

#Attempting To Clean Up UI For A Clean Workspace
class cleanuiOperator(bpy.types.Operator):
    "Turns Off Stuff I'd Turn Off"
    bl_idname = "ui.clean"
    bl_label = "cleanViewport"   
    
    def execute(self, context):
        bpy.context.space_data.show_floor = False
        bpy.context.space_data.show_relationship_lines = False
        bpy.context.space_data.show_only_render = True
        bpy.context.space_data.use_matcap = False
        if addon_exists("silhouette"):
            if bpy.context.scene.silhouette.show_silhouette:
                bpy.context.scene.silhouette.show_silhouette = False
        return {'FINISHED'}
    
#ClassicBigRedMode
class redmodeOperator(bpy.types.Operator):
    "Cleans UI / Preps You With Red"
    bl_idname = "ui.red"
    bl_label = "redViewport"   
    
    def execute(self, context):
        bpy.context.space_data.show_floor = False
        bpy.context.space_data.show_relationship_lines = False
        bpy.context.space_data.show_only_render = True
        bpy.context.space_data.use_matcap = True
        bpy.context.space_data.matcap_icon = '17'
        if addon_exists("silhouette"):
            if bpy.context.scene.silhouette.show_silhouette:
                bpy.context.scene.silhouette.show_silhouette = False
        return {'FINISHED'}


#NormalMatcapMode
class normodeOperator(bpy.types.Operator):
    "Cleans UI / Preps You With Normal View"
    bl_idname = "ui.nor"
    bl_label = "norViewport"   
    
    def execute(self, context):
        bpy.context.space_data.show_floor = False
        bpy.context.space_data.show_relationship_lines = False
        bpy.context.space_data.show_only_render = True
        bpy.context.space_data.use_matcap = True
        bpy.context.space_data.matcap_icon = '23'
        if addon_exists("silhouette"):
            if bpy.context.scene.silhouette.show_silhouette:
                bpy.context.scene.silhouette.show_silhouette = False
        return {'FINISHED'}
    
#SilhouetteMode
class silhouettemodeOperator(bpy.types.Operator):
    "Cleans UI / Preps You With Silhouette View"
    bl_idname = "ui.sil"
    bl_label = "silViewport"   
    
    def execute(self, context):
        #bpy.context.space_data.show_floor = False
        #bpy.context.space_data.show_relationship_lines = False
        #bpy.context.space_data.show_only_render = True
        #bpy.context.space_data.use_matcap = True
        #bpy.context.space_data.matcap_icon = '23'
        if addon_exists("silhouette"):
            bpy.context.scene.silhouette.show_silhouette = True
        return {'FINISHED'}

#Sets the final frame. Experimental
class endframeOperator(bpy.types.Operator):
    "Sets EndTime On Timeline Maybe start too someday"
    bl_idname = "setframe.end"
    bl_label = "Frame Range"
    bl_options = {'REGISTER', 'UNDO'}
    
    #this should be a property next to the option
       
    firstframe = IntProperty(name="StartFrame", description="SetStartFrame.", default=1, min = 1, max = 20000)
    lastframe = IntProperty(name="EndFrame", description="SetStartFrame.", default=100, min = 1, max = 20000)
    
    
    def execute(self, context):
        lastframe=self.lastframe #needed to get var involved
        firstframe=self.firstframe
        bpy.context.scene.frame_start = firstframe
        bpy.context.scene.frame_end = lastframe
        return {'FINISHED'}


