import os

from math import pi, radians
from random import choice

import bpy
import bmesh
import bpy.utils.previews

from bpy.props import *

from .. material import assign_material

#############################
#Reverse Boolean
#############################

class RevBool(bpy.types.Operator):
    """Gives A Reverse Boolean Of Selection"""
    bl_idname = "reverse.boolean"
    bl_label = "ReverseBoolean"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        scene = context.scene
        material_option = context.window_manager.Hard_Ops_material_options

        old_active = context.active_object
        obj = context.object.copy()

        bool_mods = [m for m in obj.modifiers if m.type == 'BOOLEAN']

        if bool_mods:
            mod = bool_mods[-1]
            if mod.operation == 'DIFFERENCE':
                mod.operation = 'INTERSECT'

            elif mod.operation == 'INTERSECT':
                mod.operation = 'DIFFERENCE'

        scene.objects.link(obj)
        bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, texture=False, animation=False)
        bpy.ops.multi.csharp()
        if material_option.active_material:
            if old_active.material_slots:
                if old_active.material_slots[-1].material == bpy.data.materials[material_option.active_material]:
                    bpy.ops.object.material_slot_remove()
            assign_material(context, obj, replace=True)
        return {'FINISHED'}

#############################
#Reverse Boolean Cstep
#############################

class ReBool(bpy.types.Operator):
    """Gives A Reverse Boolean Of Selection For Sstep"""
    bl_idname = "reverse.bools"
    bl_label = "ReBool-S"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        scene = context.scene

        obj = context.object.copy()

        bool_mods = [m for m in obj.modifiers if m.type == 'BOOLEAN']

        if len(bool_mods):
            mod = bool_mods[-1]
            if mod.operation == 'DIFFERENCE':
                mod.operation = 'INTERSECT'

            elif mod.operation == 'INTERSECT':
                mod.operation = 'DIFFERENCE'

        scene.objects.link(obj)
        bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, texture=False, animation=False)
        bpy.ops.multi.sstep()
        return {'FINISHED'}

#############################
#Multi-SStep
#############################

class multisstepOperator(bpy.types.Operator):
    """Multi SStep"""
    bl_idname = "multi.sstep"
    bl_label = "Multi Object Sstep"

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
                bpy.ops.step.sstep()

        return {'FINISHED'}

#############################
#Multi-CStep
#############################

class multicstepOperator(bpy.types.Operator):
    """Multi CStep"""
    bl_idname = "multi.cstep"
    bl_label = "Multi Object Cstep"

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
                bpy.ops.step.cstep()

        return {'FINISHED'}
