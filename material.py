import bpy

from bpy.types import PropertyGroup, Operator
from bpy.props import EnumProperty, StringProperty, BoolProperty

#############################
#Material Option Props
#############################

class material_options(PropertyGroup):

    material_mode = EnumProperty(name = "Mode",
                                 description = "",
                                 items = [("ALL", "All", "Look for all materials."),
                                          ("OBJECT", "Object", "Look for materials on the active object.")],
                                 default = "ALL")

    active_material = StringProperty(name = "Select Material",
                                     description = "Assign the secondary material for bool operations.",
                                     default = "")

    force = BoolProperty(name = "Force",
                         description = "Force this active material as the material for non-active objects in a bool operation.",
                         default = True)

#############################
#Assign Material
#############################

def assign_material(context, object, replace=False, csplit=False, active=None):
    option = context.window_manager.Hard_Ops_material_options
    if option.active_material:
        if object:
            if replace:
                old_active = bpy.data.objects[context.active_object.name] if not active else active
                context.scene.objects.active = object
                while object.material_slots:
                    bpy.ops.object.material_slot_remove()
                bpy.ops.object.material_slot_add()
                object.material_slots[0].material = bpy.data.materials[option.active_material]
                context.scene.objects.active = old_active
            else:
                prepare(context, option, object, active)
                if not csplit:
                    add_material(context, option, context.active_object, active)

def prepare(context, option, object, active):
    old_active = bpy.data.objects[context.active_object.name] if not active else active
    context.scene.objects.active = object
    if option.force:
        while object.material_slots:
            bpy.ops.object.material_slot_remove()
        bpy.ops.object.material_slot_add()
        object.material_slots[0].material = bpy.data.materials[option.active_material]
    else:
        bpy.ops.object.material_slot_add()
        object.material_slots[-1].material = bpy.data.materials[option.active_material]
    bpy.ops.showwire.objects(noexist=True)
    context.scene.objects.active = old_active

def add_material(context, option, object, active):
    old_active = context.scene.objects.active if not active else active
    context.scene.objects.active = object
    if len(object.material_slots) > 1:
        if object.material_slots[-1].material != bpy.data.materials[option.active_material]:
            bpy.ops.object.material_slot_add()
            object.material_slots[-1].material = bpy.data.materials[option.active_material]
    else:
        bpy.ops.object.material_slot_add()
        object.material_slots[-1].material = bpy.data.materials[option.active_material]
    context.scene.objects.active = old_active

#############################
#HOps New Material
#############################

class new_material(Operator):
    bl_idname = "material.hops_new"
    bl_label = "New"
    bl_description = "Add a new material"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        object = context.active_object
        slots = object.material_slots
        index = object.active_material_index
        if not slots or slots[index].material != None:
            bpy.ops.object.material_slot_add()
            bpy.ops.material.new()
            slots[object.active_material_index].material = bpy.data.materials[-1]
        else:
            bpy.ops.material.new()
            slots[object.active_material_index].material = bpy.data.materials[-1]
        return {'FINISHED'}
