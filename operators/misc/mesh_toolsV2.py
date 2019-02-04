import os
import bpy
import bmesh
from bgl import *
from bpy.props import *
from math import radians, degrees
from .. utils import update_bevel_modifier_if_necessary
from ... utils.context import ExecutionContext
#from . soft_sharpen import soft_sharpen_object
from ... preferences import tool_overlays_enabled, Hops_display_time, Hops_fadeout_time
from ... utils.blender_ui import get_location_in_current_3d_view
from ... utils.objects import get_modifier_with_type, apply_modifiers
from ... overlay_drawer import show_custom_overlay, disable_active_overlays
from ... graphics.drawing2d import set_drawing_dpi, draw_horizontal_line, draw_boolean, draw_text
from ... overlay_drawer import show_text_overlay

class FlattenMeshOperator(bpy.types.Operator):
    bl_idname = "hops.flatten_mesh"
    bl_label = "MeshFlatten"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Apply All And Revert Mesh To Undefined"
    
    items = [(x.identifier, x.name, x.description, x.icon)
             for x in bpy.types.Modifier.bl_rna.properties['type'].enum_items]

    modifier_types = EnumProperty(name="Modifier Types",
                           items=[(id, name, desc, icon, 2**i) for i, (id, name, desc, icon) in enumerate(items)
                                   if id in ['BOOLEAN', 'MIRROR', 'BEVEL', 'SOLIDIFY', 'SUBSURF', 'ARRAY']],
                           description="Don't apply these",
                           #default={'BEVEL', 'MIRROR', 'SUBSURF','ARRAY'},
                           options={'ENUM_FLAG'})
   
    @classmethod
    def poll(cls, context):
        object = context.active_object
        if object is None: return False
        return object.type == "MESH" and object.mode == "OBJECT"
    
    def invoke(self, context, event):
        self.execute(context)
        object = bpy.context.active_object
#        if tool_overlays_enabled():
#                disable_active_overlays()
#                self.wake_up_overlay = show_custom_overlay(draw,
#                    parameter_getter = self.parameter_getter,
#                    location = get_location_in_current_3d_view("CENTER", "BOTTOM", offset = (0, 130)),
#                    location_type = "CUSTOM",
#                    stay_time = Hops_display_time(),
#                    fadeout_time = Hops_fadeout_time())
        
    def execute(self, context):
        active = bpy.context.active_object
        object = bpy.context.active_object
        flatten_mesh(context.active_object, self.modifier_types)

def flatten_mesh(object, modifier_types):
    with ExecutionContext(mode = "OBJECT", active_object = object):
        apply_modifiers(object, ignored_types = modifier_types)
        convert_to_sharps(object)
        object.hops.status = "UNDEFINED"

class simplify_lattice(bpy.types.Operator):
    bl_idname = "hops.simplify_lattice"
    bl_label = "Simplify Lattice"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        bpy.context.object.data.points_u = 2
        bpy.context.object.data.points_v = 2
        bpy.context.object.data.points_w = 2
        bpy.context.object.data.use_outside = True
        return {"FINISHED"}
        
#############################
#Array Operators Start Here
#############################

#Array Twist
class arrayOperator(bpy.types.Operator):
    '''Array And Twist 360 Degrees'''
    bl_idname = "array.twist" #must be lowercase always
    bl_label = "ArrayTwist"
    bl_options = {'REGISTER', 'UNDO'} 
    
    arrayCount = IntProperty(name="ArrayCount", description="Amount Of Clones", default=8, min = 1, max = 100)
    
    destructive = BoolProperty(default = False)
    
    #xy = BoolProperty(default = False)

        # ADD A DRAW FUNCTION TO DISPLAY PROPERTIES ON THE F6 MENU
    def draw(self, context):
        layout = self.layout

        box = layout.box()
        # DRAW YOUR PROPERTIES IN A BOX
        box.prop( self, 'arrayCount', text = "ArrayCount" )
        box.prop( self, 'destructive', text = "Destructive/Non")
        #box.prop( self, 'xy', text = "Toggle X/Y")
      
        
    def execute(self, context):
        #Now Has A Custom Count
        arrayCount=self.arrayCount #sets array count
                
        if self.destructive:
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
            bpy.ops.object.modifier_add(type='ARRAY')
            bpy.context.object.modifiers["Array"].count = arrayCount
            bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
            bpy.context.object.modifiers["SimpleDeform"].deform_method = 'BEND'
            bpy.context.object.modifiers["SimpleDeform"].angle = 6.28319
            bpy.ops.object.convert(target='MESH')
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_all(action='TOGGLE')
            bpy.ops.mesh.remove_doubles()
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
            bpy.ops.object.location_clear()

        else:
            #Now Has A Custom Count
            arrayCount=self.arrayCount #sets array count
            
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
            bpy.ops.object.modifier_add(type='ARRAY')
            bpy.context.object.modifiers["Array"].count = arrayCount
            bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
            bpy.context.object.modifiers["SimpleDeform"].deform_method = 'BEND'
            bpy.context.object.modifiers["SimpleDeform"].angle = 6.28319     
        return {'FINISHED'}

class set_as_cam(bpy.types.Operator):
    bl_idname = "hops.set_camera"
    bl_label = "Sets Camera"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        bpy.ops.view3d.object_as_camera()
        return {"FINISHED"}