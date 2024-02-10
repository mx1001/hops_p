import bpy
from mathutils import Vector, Matrix

from . import addon, math


def duplicate(obj, name='', link=False):
    duplicate = obj.copy()
    duplicate.data = obj.data.copy()

    if name:
        duplicate.name = name
        duplicate.data.name = name

    addon.log(value=F'Duplicated {obj.name} as: {duplicate.name}', indent=2)

    if link:
        bpy.context.scene.collection.objects.link(duplicate)
        addon.log(value=F'Linked {duplicate.name} to the scene', indent=2)

    return duplicate

def center(obj, matrix=Matrix()):
    return 0.125 * math.vector_sum(bound_coordinates(obj, matrix=matrix))


def bound_coordinates(obj, matrix=Matrix()):
    return [matrix @ Vector(coord) for coord in obj.bound_box]


def mesh_duplicate(obj, depsgraph, apply_modifiers=True):
    mesh = obj.to_mesh()

    if apply_modifiers:
        obj = obj.evaluated_get(depsgraph)
        mesh = obj.to_mesh()

    return mesh


def apply_scale (obj):
    
    obj.data.transform(math.get_sca_matrix(obj.scale))
    obj.scale = Vector((1,1,1))

def apply_location (obj):
    
    obj.data.transform(math.get_loc_matrix(obj.location))
    obj.location = Vector((0,0,0))

def apply_rotation (obj):

    obj.data.transform(math.get_rot_matrix(obj.rotation_quaternion))
    obj.scale = Vector((0,0,0))


def apply_transforms(obj):
    obj.data.transform(obj.matrix_world)
    clear_transforms(obj)


def clear_transforms(obj):
    obj.matrix_world = Matrix()


def apply_transform_bpy_version():
    '''Apply the transform on the active object.'''

    # TODO: Make a low level version of this.

    if bpy.context.active_object.mode == "EDIT":
        bpy.ops.object.mode_set(mode='OBJECT')
        
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    if bpy.context.active_object.mode == "OBJECT":
        bpy.ops.object.mode_set(mode='EDIT')