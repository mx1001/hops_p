import bpy
from bgl import *
from bpy.props import *
from ... utils.objects import get_current_selected_status

class HopsCurveBevelOperator(bpy.types.Operator):
    bl_idname = "hops.curve_bevel"
    bl_label = "Sets 2nd Curve To Bevel"
    bl_description = "Sets the 2nd curve the the first curve taper object"
    bl_options = {"REGISTER", "UNDO"}
      
    def execute(self, context):
        active_object, other_objects, other_object = get_current_selected_status()
        bpy.context.object.data.bevel_object = other_object
        return {"FINISHED"}
