import bpy
from math import radians
from bpy.props import FloatProperty
from ... preferences import get_preferences


class HOPS_OT_SetSharpness30(bpy.types.Operator):
    bl_idname = "hops.set_sharpness_30"
    bl_label = "Set Hops Global Sharpness Angle 30"
    bl_options = {"REGISTER", "INTERNAL"}
    bl_description = "Sets hops global sharpness angle"

    sharpness: FloatProperty(name="angle edge marks are applied to", default=radians(30), min=radians(1), max=radians(180), subtype="ANGLE")

    def execute(self, context):

        get_preferences().property.sharpness = self.sharpness

        return {"FINISHED"}


class HOPS_OT_SetSharpness45(bpy.types.Operator):
    bl_idname = "hops.set_sharpness_45"
    bl_label = "Set Hops Global Sharpness Angle 45"
    bl_options = {"REGISTER", "INTERNAL"}
    bl_description = "Sets hops global sharpness angle"

    sharpness: FloatProperty(name="angle edge marks are applied to", default=radians(45), min=radians(1), max=radians(180), subtype="ANGLE")

    def execute(self, context):

        get_preferences().property.sharpness = self.sharpness

        return {"FINISHED"}


class HOPS_OT_SetSharpness60(bpy.types.Operator):
    bl_idname = "hops.set_sharpness_60"
    bl_label = "Set Hops Global Sharpness Angle 60"
    bl_options = {"REGISTER", "INTERNAL"}
    bl_description = "Sets hops global sharpness angle"

    sharpness: FloatProperty(name="angle edge marks are applied to", default=radians(60), min=radians(1), max=radians(180), subtype="ANGLE")

    def execute(self, context):

        get_preferences().property.sharpness = self.sharpness

        return {"FINISHED"}


class HOPS_OT_SetAutoSmooth(bpy.types.Operator):
    bl_idname = "hops.set_autosmoouth"
    bl_label = "Set Autosmooth Angle"
    bl_options = {"REGISTER", "INTERNAL"}
    bl_description = "Sets hops global sharpness angle"

    angle: FloatProperty(name="Angle", default=radians(45), min=radians(1), max=radians(180), subtype="ANGLE")

    @classmethod
    def poll(cls, context):
        object = context.active_object
        if object.mode == "OBJECT":
            return True

    def execute(self, context):

        context.object.data.use_auto_smooth = True
        bpy.ops.object.shade_smooth()
        context.object.data.auto_smooth_angle = self.angle

        return {"FINISHED"}
