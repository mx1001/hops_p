import os
import bpy
import bmesh
from bpy.props import *
from math import pi, radians
import bpy.utils.previews
from random import choice

#############################
#FaceOps Start Here
#############################

#Sets Up Faces For Grating
class facegrateOperator(bpy.types.Operator):
    "Face Grate Setup"
    bl_idname = "fgrate.op"
    bl_label = "FaceGrate" 
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.context.space_data.pivot_point = 'INDIVIDUAL_ORIGINS'
        bpy.ops.mesh.poke()
        
        #Threshold is a tricky devil
        bpy.ops.mesh.tris_convert_to_quads(face_threshold=0.698132, shape_threshold=1.39626)        
        bpy.ops.mesh.inset(thickness=0.004, use_individual=True)   
        return {'FINISHED'}
    
#Sets Up Faces For Knurling
class faceknurlOperator(bpy.types.Operator):
    "Face Knurl Setup"
    bl_idname = "fknurl.op"
    bl_label = "FaceKnurl" 
    bl_options = {'REGISTER', 'UNDO'}
    """
    knurlSubd = IntProperty(name="KnurlSubdivisions", description="Amount Of Divisions", default=0, min = 0, max = 5)"""
    
    def execute(self, context):
        #allows the knurl to be subdivided
        #knurlSubd = self.knurlSubd
        #bpy.ops.mesh.subdivide(0)                
        bpy.ops.mesh.inset(thickness=0.024, use_individual=True)
        bpy.ops.mesh.poke()
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
        bpy.ops.mesh.select_less()
        #bpy.ops.transform.shrink_fatten(value=0.2, use_even_offset=True, mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        return {'FINISHED'}


###########################
#Circle Stuff Starts Here
###########################

#Creates a Circle With No Extrudes / Allows For Setup
class circleSetupOperator(bpy.types.Operator):
    "Creates a Clean Circle At The Vert"
    bl_idname = "circle.setup"
    bl_label = "SetCircle"
    bl_options = {'REGISTER', 'UNDO'} 
    
    circleSubdivs = IntProperty(name="Circle", description="Amount Of Divisions Per Circle", default=5, min = 2, max = 8)
    
    
    def execute(self, context):     
        #Now Has A Custom Count
        circleSubdivs=self.circleSubdivs #sets the subdivs on the circle.
           
        bpy.ops.mesh.bevel(offset=0.1, segments=circleSubdivs, vertex_only=True)
        bpy.ops.mesh.looptools_circle(custom_radius=False, fit='best', flatten=True, influence=100, lock_x=False, lock_y=False, lock_z=False, radius=1, regular=True)
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
        
        
        bpy.ops.mesh.dissolve_mode()
        #sets Individual Scaling Of Newly Created Points.
        bpy.context.space_data.pivot_point = 'INDIVIDUAL_ORIGINS'
        return {'FINISHED'}


#Make A Circle At Each Vert - No Mercy
class circleOperator(bpy.types.Operator):
    '''Creates A Circle At Vert'''
    bl_idname = "area.circle"
    bl_label = "Encircle"
    bl_options = {'REGISTER', 'UNDO'} 
    
    def execute(self, context):
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
        bpy.ops.mesh.bevel(offset=0.1, segments=4, vertex_only=True)
        bpy.ops.mesh.looptools_circle(custom_radius=False, fit='best', flatten=True, influence=100, lock_x=False, lock_y=False, lock_z=False, radius=1, regular=True)
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
        bpy.ops.mesh.inset(thickness=0.0109504)
        bpy.ops.mesh.inset(thickness=0.0150383)
        bpy.ops.transform.shrink_fatten(value=0.0977827, use_even_offset=False, mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        bpy.ops.mesh.inset(thickness=0.0125973)
        bpy.ops.mesh.dissolve_mode()
        bpy.ops.mesh.dissolve_faces()
        return {'FINISHED'}

#Nth Circle Rings
class cicleRinger(bpy.types.Operator):
    '''Turns Every Nth Selection Into a Circle'''
    bl_idname = "nth.circle"
    bl_label = "Nthcircle"
    bl_options = {'REGISTER', 'UNDO'} 
    
    def execute(self, context):
        #massive hole punching
        #bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
        #bpy.ops.mesh.inset(thickness=0.05)
        bpy.context.space_data.pivot_point = 'INDIVIDUAL_ORIGINS'    
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
        bpy.ops.mesh.select_nth()
        bpy.ops.mesh.bevel(offset=0.03, segments=4, vertex_only=True)
        bpy.ops.mesh.looptools_circle(custom_radius=False, fit='best', flatten=True, influence=100, lock_x=False, lock_y=False, lock_z=False, radius=1, regular=True)
        #bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
        #bpy.ops.mesh.inset(thickness=0.0109504)
        #bpy.ops.mesh.inset(thickness=0.0150383)
        #bpy.ops.transform.shrink_fatten(value=0.0977827, use_even_offset=False, mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        #bpy.ops.mesh.inset(thickness=0.0125973)
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
        bpy.ops.mesh.dissolve_mode()
        return {'FINISHED'}

#Individual Circle Rings AKA Circle Selection
class cicleRings(bpy.types.Operator):
    '''Turns Every Vert Into a Circle'''
    bl_idname = "select.circle"
    bl_label = "Selectioncircle"
    bl_options = {'REGISTER', 'UNDO'} 
    
    def execute(self, context):
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
        #these 2 lines might be a bad idea
        bpy.ops.mesh.inset(thickness=0.0705154)
        #bpy.ops.mesh.bevel(offset=0.065, segments=2, vertex_only=False) #the segments should offset because of the segments lower down
        #bpy.ops.mesh.select_less()
        #but lets find out!
        bpy.ops.mesh.bevel(offset=0.04, segments=4, vertex_only=True) #segments should be adjustable in an ideal world
        bpy.ops.mesh.looptools_circle(custom_radius=False, fit='best', flatten=True, influence=100, lock_x=False, lock_y=False, lock_z=False, radius=1, regular=True)
        bpy.context.space_data.pivot_point = 'INDIVIDUAL_ORIGINS'
        bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
        bpy.ops.transform.resize(value=(0.730115, 0.730115, 0.730115), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        bpy.ops.transform.shrink_fatten(value=0.0841381, use_even_offset=False, mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, -0.0705891), "constraint_axis":(False, False, True), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
        bpy.ops.mesh.select_more()
        bpy.ops.mesh.dissolve_faces()
        #ew N-gon I need a way to make this individally solve for the grid fill operation while also keeping them going the same directions and not be rampart
        return {'FINISHED'}

#Single Circle Rings AKA Circle Ring
class cicleRing(bpy.types.Operator):
    '''Turns Every Vert Into a Circle'''
    bl_idname = "circle.ring"
    bl_label = "CircleRing"
    bl_options = {'REGISTER', 'UNDO'} 
    
    def execute(self, context):
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
        bpy.ops.mesh.bevel(offset=0.1, segments=4, vertex_only=True)
        bpy.ops.mesh.looptools_circle(custom_radius=False, fit='best', flatten=True, influence=100, lock_x=False, lock_y=False, lock_z=False, radius=1, regular=True)
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
        bpy.ops.mesh.inset(thickness=0.0109504)
        bpy.ops.mesh.inset(thickness=0.0150383)
        bpy.ops.transform.shrink_fatten(value=0.0977827, use_even_offset=False, mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        bpy.ops.mesh.inset(thickness=0.0125973)
        bpy.ops.mesh.dissolve_mode()
        #ew N-gon I need a way to make this individally solve for the grid fill operation while also keeping them going the same directions and not be rampart
        return {'FINISHED'}

#############################
#Panelling Operators Start Here
#############################

#Panel From An Edge Ring Selection
#Scale Dependant for now.
class entrenchOperatorA(bpy.types.Operator):
    '''Entrench Those Edges!'''
    bl_idname = "entrench.selection"
    bl_label = "Entrench"
    bl_options = {'REGISTER', 'UNDO'} 
    
    def execute(self, context):
        bpy.context.space_data.pivot_point = 'MEDIAN_POINT'
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
        bpy.ops.mesh.bevel(offset=0.0128461, vertex_only=False)
        bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
        bpy.ops.transform.shrink_fatten(value=0.04, use_even_offset=True, mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        bpy.ops.mesh.region_to_loop()
        bpy.ops.mesh.bevel(offset=0.00885385, vertex_only=False)
        bpy.ops.mesh.select_more()
        bpy.ops.mesh.region_to_loop()
        bpy.ops.transform.edge_bevelweight(value=1)
        bpy.ops.mesh.mark_sharp()
        bpy.ops.object.editmode_toggle()
        #its important to specify that its edge mode youre working from. Vert mode is a different game altogether for it. 
        return {'FINISHED'}

#Make A Panel Loop From Face Selection
#Scale Dependant for now.
class panelOperatorA(bpy.types.Operator):
    '''Create A Panel From A Face Selection'''
    bl_idname = "quick.panel"
    bl_label = "Sharpen"
    bl_options = {'REGISTER', 'UNDO'} 
    
    def execute(self, context):
        bpy.context.space_data.pivot_point = 'MEDIAN_POINT'
        bpy.ops.mesh.region_to_loop()
        bpy.ops.mesh.bevel(offset=0.00841237, segments=2, vertex_only=False)
        bpy.ops.mesh.select_less()
        bpy.ops.transform.shrink_fatten(value=0.0211908, use_even_offset=False, mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        bpy.ops.mesh.bevel(offset=0.00683826, vertex_only=False)
        return {'FINISHED'}
    
#############################
#OrginAndApply Operators Start Here
#############################

class cleanRecenter(bpy.types.Operator):
    "RemovesDoubles/RecenterOrgin/ResetGeometry"
    bl_idname = "clean.recenter"
    bl_label = "CleanRecenter"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        #maybe convert to mesh then recenter
        bpy.ops.object.modifier_remove(modifier="Bevel")
        #bpy.ops.object.modifier_remove(modifier="Solidify")
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_all(action='TOGGLE')
        bpy.ops.mesh.remove_doubles()
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        bpy.ops.object.location_clear()
        return {'FINISHED'}

#apply all 2 except Loc at once and be done    
class stompObjectnoloc(bpy.types.Operator):
    "RemovesDoubles/ResetGeometry/NotLoc"
    bl_idname = "stomp2.object"
    bl_label = "stompObjectnoLoc"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        #bpy.ops.object.location_clear()
        return {'FINISHED'}

#apply all 3 at once and be done
class stompObject(bpy.types.Operator):
    "Applies LocRotScale Finally"
    bl_idname = "stomp.object"
    bl_label = "stompObject"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.object.location_clear()
        return {'FINISHED'}
    


# #############################
# #Skin Hose Experimental
# #############################

# #creates a skin mod hose / needs a vert count limit so it doesnt cause crashes
# class skinhoseOperator(bpy.types.Operator):
#     "Sets EndTime On Timeline Maybe start too someday"
#     bl_idname = "skinhose.add"
#     bl_label = "VertToSkinHose"
    
#     def execute(self, context):
#         bpy.ops.object.modifier_add(type='SUBSURF')
#         bpy.ops.object.modifier_add(type='SKIN')
#         bpy.ops.object.modifier_add(type='SUBSURF')
#         bpy.context.object.modifiers["Subsurf"].show_expanded = False
#         #bpy.context.object.modifiers["Skin"].show_expanded = False
#         bpy.context.object.modifiers["Subsurf.001"].show_expanded = False
#         bpy.context.object.modifiers["Subsurf"].show_in_editmode = False
#         #bpy.context.object.modifiers["Skin"].show_in_editmode = False
#         bpy.context.object.modifiers["Subsurf.001"].show_in_editmode = False
#         #I need to add a query here but I'm tired right now. 
#         return {'FINISHED'}
