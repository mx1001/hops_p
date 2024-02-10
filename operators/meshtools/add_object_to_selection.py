import bpy
import bmesh
from mathutils import Vector, Matrix


class HOPS_OT_SelectedToSelection(bpy.types.Operator):
    bl_idname = "object.to_selection"
    bl_label = "To selection"

    def execute(self, context):

        obj_list = []
        bpy.ops.object.mode_set(mode='OBJECT')
        ref_obj = bpy.context.active_object

        obj1, obj2 = context.selected_objects
        second_obj = obj1 if obj2 == ref_obj else obj2

        obj_list.append(second_obj.name)
        bpy.data.objects[second_obj.name].select_set(False)
        bpy.ops.object.duplicate_move()
        bpy.context.active_object.name = "Dummy"
        obj = context.active_object
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        bm = bmesh.new()
        bm.from_mesh(obj.data)

        selected_faces = [f for f in bm.faces if f.select]

        for face in selected_faces:

            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = bpy.data.objects[second_obj.name]
            bpy.data.objects[second_obj.name].select_set(True)
            bpy.ops.object.duplicate()

            # Rotate
            normal = face.normal
            quat = normal.rotation_difference(Vector((0,0,1)))
            quat.invert()
            context.object.rotation_euler = quat.to_euler()

            # Move
            context.object.location = face.calc_center_median()
            
            obj_list.append(context.object.name)

        bm.to_mesh(obj.data)
        bm.free()

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = bpy.data.objects["Dummy"]
        bpy.data.objects["Dummy"].select_set(True)
        bpy.ops.object.delete(use_global=False)

        bpy.context.view_layer.objects.active = bpy.data.objects[obj_list[0]]

        # custom link called from operators module
        for obj in obj_list:
            bpy.data.objects[obj].select_set(True)
            bpy.ops.make.link() 

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = bpy.data.objects[ref_obj.name]
        bpy.data.objects[second_obj.name].select_set(True)
        bpy.data.objects[ref_obj.name].select_set(True)

        bpy.ops.object.mode_set(mode='EDIT')
        del(obj_list[:])

        return {'FINISHED'}