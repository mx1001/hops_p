import bpy
from bgl import *
from bpy.props import *
from math import radians, degrees
from ... preferences import tool_overlays_enabled
from ... utils.context import ExecutionContext
from ... overlay_drawer import show_custom_overlay, disable_active_overlays
from ... utils.blender_ui import get_location_in_current_3d_view
from ... overlay_drawer import show_custom_overlay, disable_active_overlays
from ... graphics.drawing2d import set_drawing_dpi, draw_horizontal_line, draw_boolean, draw_text
from ... utils.objects import get_objects_in_same_group, set_active, remove_object_from_scene, only_select

from ... preferences import tool_overlays_enabled, get_hops_preferences_colors_with_transparency, Hops_display_time, Hops_fadeout_time
from ... graphics.drawing2d import set_drawing_dpi, draw_horizontal_line, draw_boolean, draw_text, draw_box, draw_logo_csharp


class ParentMergeOperator(bpy.types.Operator):
    bl_idname = "hops.parent_merge"
    bl_label = "Parent Merge"
    bl_options = {'REGISTER', 'UNDO'} 
    
    text = "Objects Joined via merge - AP and BB removed"
    op_tag = "Merge"
    op_detail = "Objects have been merged"
    
    sharpen_mesh = BoolProperty(default = True)
    
    @classmethod
    def poll(self, context):
        return getattr(context.active_object, "type", "") == "MESH"
        return getattr(context.selected_objects, "AP") is not None

    def invoke(self, context, event):
        self.execute(context)

        if tool_overlays_enabled():
            disable_active_overlays()
            self.wake_up_overlay = show_custom_overlay(draw,
                parameter_getter = self.parameter_getter,
                location = get_location_in_current_3d_view("CENTER", "BOTTOM", offset = (0, 130)),
                location_type = "CUSTOM",
                stay_time = Hops_display_time(),
                fadeout_time = Hops_fadeout_time())

        return {"FINISHED"}

    def parameter_getter(self):
        return self.op_detail, self.op_tag, self.text, self.sharpen_mesh
    
    def execute(self, context):
        hide_child_objects(False)
        target_object = context.active_object
        
        plane_object = get_prefixed_object(context.selected_objects, "AP")

        set_active(plane_object)
        bpy.ops.object.select_grouped(type = "CHILDREN_RECURSIVE")
        bpy.ops.object.parent_clear(type = "CLEAR_KEEP_TRANSFORM")

        childrens = context.selected_objects
        bounding_box_object = get_prefixed_object(childrens, "BB")
        
        boolean_diff_objects(target_object, bounding_box_object)

        if check_status(target_object):
            cstep_reset(target_object)
            bpy.ops.step.sstep()
            op_detail = "Objects have been merged - Via SStep"
        else:
            #bpy.ops.csharpen.objects()
            bpy.ops.hops.complex_sharpen
            op_detail = "Objects have been merged - Via CSharp"

        remove_object_from_scene(plane_object)
        remove_object_from_scene(bounding_box_object)

        
        try: self.wake_up_overlay()
        except: pass

        return {"FINISHED"}

class ParentMergeSOperator(bpy.types.Operator):
    bl_idname = "hops.parent_merge_soft"
    bl_label = "Parent Merge Soft"
    bl_options = {'REGISTER', 'UNDO'} 
    
    text = "Objects Joined Soft Merge - No meshes removed"
    op_tag = "Merge Soft"
    op_detail = "Objects have been merged without sharpening"
    
    sharpen_mesh = BoolProperty(default = False)
    
    @classmethod
    def poll(self, context):
        return getattr(context.active_object, "type", "") == "MESH"
        return getattr(context.selected_objects, "AP") is not None

    def invoke(self, context, event):
        self.execute(context)

        if tool_overlays_enabled():
            disable_active_overlays()
            self.wake_up_overlay = show_custom_overlay(draw,
                parameter_getter = self.parameter_getter,
                location = get_location_in_current_3d_view("CENTER", "BOTTOM", offset = (0, 130)),
                location_type = "CUSTOM",
                stay_time = Hops_display_time(),
                fadeout_time = Hops_fadeout_time())

        return {"FINISHED"}

    def parameter_getter(self):
        return self.op_detail, self.op_tag, self.text, self.sharpen_mesh
    
    def execute(self, context):
        target_object = context.active_object

        childrens = context.selected_objects
        bounding_box_object = get_prefixed_object(childrens, "BB")

        boolean_diff_objects(target_object, bounding_box_object)
        
        try: self.wake_up_overlay()
        except: pass

        return {"FINISHED"}

class SelectionMergeSOperator(bpy.types.Operator):
    bl_idname = "hops.select_merge"
    bl_label = "select_merge"
    bl_options = {'REGISTER', 'UNDO'} 
    
    def execute(self, context):
        hide_child_objects(False)
            
        return {"FINISHED"}

def hide_child_objects(hide):
    scene = bpy.context.scene

    if hide :
        for ob in scene.objects:
            if ob.type == 'MESH' and ob.name.startswith("OB_"):
                ob.hide_select = True
            if ob.type == 'MESH' and ob.name.startswith("BB_"):
                ob.hide_select = True
    else:
        for ob in scene.objects:
            if ob.type == 'MESH' and ob.name.startswith("OB_"):
                ob.hide_select = False
            if ob.type == 'MESH' and ob.name.startswith("BB_"):
                ob.hide_select = False
     
def get_prefixed_object(objects, prefix):
    for object in objects:
        if object.name.startswith(prefix): return object

def check_status(object):
    object = bpy.context.active_object    
    if object.hops.status == "CSTEP": return True
    return False

def cstep_reset(target_object):
    object = bpy.context.active_object
    bpy.ops.object.editmode_toggle()    
    if object.hops.status == "CSTEP":
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_all(action='TOGGLE')
        bpy.ops.mesh.hide()
    bpy.ops.object.editmode_toggle()

def boolean_diff_objects(target_object, brush_object):
    only_select([target_object, brush_object])
    set_active(target_object)
    bpy.ops.hops.bool_difference(boolean_method='CARVEMOD')

def draw(display, parameter_getter):
    op_detail, op_tag, text, sharpen_mesh = parameter_getter()    
        
    scale_factor = 0.9

    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)

    set_drawing_dpi(display.get_dpi() * scale_factor)
    dpi_factor = display.get_dpi_factor() * scale_factor
    line_height = 18 * dpi_factor

    transparency = display.transparency

    color_text1, color_text2, color_border, color_border2 = get_hops_preferences_colors_with_transparency(transparency)
    region_width = bpy.context.region.width

    # Box
    ########################################################

    location = display.location
    x, y = location.x - 60* dpi_factor, location.y - 118* dpi_factor

    draw_box(0, 43 *dpi_factor, region_width, -4 * dpi_factor, color = color_border2)
    draw_box(0, 0, region_width, -82 * dpi_factor, color = color_border)

    draw_logo_csharp(color_border2) #Logo so illa. I love this bitch.

     # Name
    ########################################################
    draw_text("MERGE", x - 380 *dpi_factor , y -12*dpi_factor,
              align = "LEFT", size = 20 , color = color_text2)
              
     # First Coloumn
    ########################################################
    x = x - 160 * dpi_factor
    r = 34 * dpi_factor

    draw_text(text, x , y,
              align = "LEFT",size = 11, color = color_text2)

    draw_text(op_detail, x, y - line_height,
              align = "LEFT", color = color_text2)
    
    glDisable(GL_BLEND)
    glDisable(GL_LINE_SMOOTH)