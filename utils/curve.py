import bpy
import math
import bmesh


def add_curve_to_scene(context, location=(0,0,0), name="curve", select=True):
    '''Create a new curve and add it to the viewlayer.'''

    active_obj = context.active_object

    view_layer = context.view_layer
    curve_data_block = bpy.data.curves.new(name=name, type='CURVE')
    curve = bpy.data.objects.new(name=name + "_curve", object_data=curve_data_block)
    view_layer.active_layer_collection.collection.objects.link(curve)
    curve.location = location
    view_layer.objects.active = curve

    if select:
        curve.select_set(True)
    else:
        active_obj.select_set(True)
        view_layer.objects.active = active_obj

    add_bezier_spline(curve=curve)
    return curve


def add_bezier_spline(curve, location=(0,0,0)):
    '''Adds a bezier spline to the curve.'''

    curve.data.splines.new('BEZIER')
    curve.data.dimensions = '3D'
    curve.data.splines[0].bezier_points[0].co = location
    curve.data.splines[0].bezier_points[0].handle_right_type = 'VECTOR'
    curve.data.splines[0].bezier_points[0].handle_left_type = 'VECTOR'


def add_bezier_point(curve, location=(0,0,0)):
    '''Add a point to the bezier path.'''
    
    curve.data.splines.active.bezier_points.add(count=1)
    curve.data.splines[0].bezier_points[-1].co = location
    curve.data.splines[0].bezier_points[-1].handle_right_type = 'AUTO'
    curve.data.splines[0].bezier_points[-1].handle_left_type = 'AUTO'

    last_loc = curve.data.splines[0].bezier_points[-1].co
    curve.data.splines[0].bezier_points[0].handle_left = last_loc
    curve.data.splines[0].bezier_points[0].handle_right = last_loc


def copy_curve(context, curve):
    '''Copy the curve object.'''

    # Clone and append the curve
    new_obj = curve.copy()
    new_obj.data = curve.data.copy()
    new_obj.animation_data_clear()
    bpy.context.collection.objects.link(new_obj)

    return new_obj


def convert_curve_to_mesh(context, curve, smooth_repeat, smoothing_factor):
    '''Convert the curve into a mesh object.'''

    # Come out of edit mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Get current active object
    active_object = context.active_object

    # Deselect all objects
    for obj in context.view_layer.objects:
        if obj.name != curve.name:
            obj.select_set(False)
        
    # Make the curve the selected object
    override = context.copy()
    override['active_object'] = curve

    # Convert curve
    bpy.ops.object.convert(override, target='MESH',  keep_original=False)

    # Go back to edit mode
    bpy.ops.object.mode_set(mode='EDIT')

    # Smooth the curve
    mesh = curve.data
    if len(mesh.vertices) > 3:
        bm = bmesh.from_edit_mesh(mesh)
        verts = [v for v in bm.verts]
        verts.pop(0)
        verts.pop(-1)

        for i in range(smooth_repeat):
            bmesh.ops.smooth_vert(bm, verts=verts, factor=smoothing_factor, use_axis_x=True, use_axis_y=True, use_axis_z=True)

        bmesh.update_edit_mesh(mesh)
        bm.free()
        bpy.context.view_layer.update()

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')

    return curve