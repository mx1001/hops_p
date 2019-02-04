import bpy
from bpy.props import *

from ... utils.objects import set_active, get_current_selected_status, mesh_of_activeobj_select
from ... utils.modifiers import apply_modifiers
from ... material import assign_material


def use_bmesh_boolean(context, boolean_method = 'DIFFERENCE'):
    active_object, other_objects, other_object = get_current_selected_status()
    mesh_of_activeobj_select('DESELECT')
    if not other_objects:
        assign_material(context, other_object)
    for obj in other_objects:
        assign_material(context, obj)
        set_active(obj, select = False, only_select = False)
        mesh_of_activeobj_select('SELECT')

    set_active(active_object, select = False, only_select = False)
    bpy.ops.object.join()
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_mode(type="VERT")
    if  boolean_method == 'DIFFERENCE':
        bpy.ops.mesh.intersect_boolean(operation='DIFFERENCE')
    elif boolean_method == 'UNION':
        bpy.ops.mesh.intersect_boolean(operation='UNION')
    elif boolean_method == 'INTERSECT':
        bpy.ops.mesh.intersect_boolean(operation='INTERSECT')
    bpy.ops.object.mode_set(mode = 'OBJECT')


def use_carve_boolean(context, boolean_method = 'DIFFERENCE'):
    active_object, other_objects, other_object = get_current_selected_status()
    if not other_objects:
        assign_material(context, other_object)
    for obj in other_objects:
        assign_material(context, obj)
        obj.draw_type = 'WIRE'
        obj.hops.status = "BOOLSHAPE"

        boolean = active_object.modifiers.new("Boolean", "BOOLEAN")
        if  boolean_method == 'DIFFERENCE':
            boolean.operation = 'DIFFERENCE'
        elif boolean_method == 'UNION':
            boolean.operation = 'UNION'
        elif boolean_method == 'INTERSECT':
           boolean.operation = 'INTERSECT'
        boolean.object = obj
    apply_list = [active_object]
    apply_modifiers(active_object, 'BOOLEAN')
    bpy.ops.object.select_all(action='DESELECT')
    for obj in other_objects:
        obj.select = True
        bpy.ops.object.delete(use_global=False)


def use_carve_mod_boolean(context, boolean_method = 'DIFFERENCE'):
    active_object, other_objects, other_object = get_current_selected_status()
    if not other_objects:
        assign_material(context, other_object)
    for obj in other_objects:
        assign_material(context, obj)
        obj.draw_type = 'WIRE'
        obj.hops.status = "BOOLSHAPE"

        boolean = active_object.modifiers.new("Boolean", "BOOLEAN")
        if  boolean_method == 'DIFFERENCE':
            boolean.operation = 'DIFFERENCE'
            boolean.solver = 'CARVE'
        elif boolean_method == 'UNION':
            boolean.operation = 'UNION'
            boolean.solver = 'CARVE'
        elif boolean_method == 'INTERSECT':
           boolean.operation = 'INTERSECT'
           boolean.solver = 'CARVE'
        boolean.object = obj
    set_active(active_object, select = True, only_select = True)


def use_bmesh_mod_boolean(context, boolean_method = 'DIFFERENCE'):
    active_object, other_objects, other_object = get_current_selected_status()
    if not other_objects:
        assign_material(context, other_object)
    for obj in other_objects:
        assign_material(context, obj)
        obj.draw_type = 'WIRE'
        obj.hops.status = "BOOLSHAPE"

        boolean = active_object.modifiers.new("Boolean", "BOOLEAN")
        if  boolean_method == 'DIFFERENCE':
            boolean.operation = 'DIFFERENCE'
            boolean.solver = 'BMESH'
        elif boolean_method == 'UNION':
            boolean.operation = 'UNION'
            boolean.solver = 'BMESH'
        elif boolean_method == 'INTERSECT':
           boolean.operation = 'INTERSECT'
           boolean.solver = 'BMESH'
        boolean.object = obj
    set_active(active_object, select = True, only_select = True)
