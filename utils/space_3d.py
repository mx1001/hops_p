import bpy
import math
import mathutils
from mathutils import Vector
from bpy_extras import view3d_utils


def centroid(points):
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    z = [p[2] for p in points]
    centroid = (sum(x) / len(points), sum(y) / len(points), sum(z) / len(points))

    return centroid


def scale(origin, point, value):
        ox, oy, oz = origin
        px, py, pz = point

        px = (px-ox)*value+ox
        py = (py-oy)*value+oy
        pz = (pz-oz)*value+oz

        return px, py, pz


def transform3D(point, location1, location2):
        px, py, pz = point
        x = [0, 0, 0]

        x[0] = location1[0] - px
        x[1] = location1[1] - py
        x[2] = location1[2] - pz
        px = location2[0] - x[0]
        py = location2[1] - x[1]
        pz = location2[2] - x[2]

        return px, py, pz


def rotate_z(origin, point, angle):
    ox, oy, oz = origin
    px, py, pz = point

    # Z rotation
    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    qz = pz

    return qx, qy, qz


def rotate_x(origin, point, angle):
    ox, oy, oz = origin
    px, py, pz = point

    # X rotation
    qx = px
    qz = oz + math.sin(angle) * (pz - oz) - math.cos(angle) * (py - oy)
    qy = oy + math.cos(angle) * (pz - oz) + math.sin(angle) * (py - oy)

    return qx, qy, qz


def rotate_y(origin, point, angle):
    ox, oy, oz = origin
    px, py, pz = point

    # Y rotation
    qy = py
    qx = ox + math.sin(angle) * (px - ox) - math.cos(angle) * (pz - oz)
    qz = oz + math.cos(angle) * (px - ox) + math.sin(angle) * (pz - oz)

    return qx, qy, qz


def get_3D_point_from_mouse(mouse_pos: Vector, context: bpy.context, point: Vector, normal: Vector):
        '''Point = The planes origin\n
           Normal = The direction the plane is facing'''

        # get the context arguments
        region = context.region
        rv3d = context.region_data

        intersection = Vector((0,0,0))
        try:
            #Camera Origin
            origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, mouse_pos)

            #Mouse origin
            mouse = view3d_utils.region_2d_to_vector_3d(region, rv3d, mouse_pos)

            #Camera Origin + Mouse
            ray_origin = origin + mouse

            #From the mouse to the viewport
            loc = view3d_utils.region_2d_to_location_3d(region, rv3d, mouse_pos, ray_origin - origin)

            #Ray to plane
            intersection = mathutils.geometry.intersect_line_plane(ray_origin, loc, point, normal)

        except:
            intersection = Vector((0,0,0))

        if(intersection == None):
            intersection = Vector((0,0,0))

        return intersection


def get_3D_raycast_from_mouse(event: bpy.types.Event, context: bpy.context):
    '''Cast a ray from the mouse into the scene returning the ray hit data.'''

    # get the context arguments
    region = context.region
    rv3d = context.region_data
    coord = event.mouse_region_x, event.mouse_region_y
    view_layer = context.view_layer

    #Camera Origin
    origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
    
    #Mouse origin
    mouse = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)

    #Mouse + Camera Origin
    ray_origin = origin + mouse

    # #Cast ray into scene
    result, location, normal, index, object, matrix = context.scene.ray_cast(view_layer, ray_origin, ray_origin - origin)

    return result, location, normal, index, object, matrix


def scene_ray_cast(context, event):
    '''Raycast from mouse into scene.'''

    mouse_pos = (event.mouse_region_x, event.mouse_region_y)

    origin = view3d_utils.region_2d_to_origin_3d(bpy.context.region, bpy.context.region_data, mouse_pos)
    direction = view3d_utils.region_2d_to_vector_3d(bpy.context.region, bpy.context.region_data, mouse_pos)

    hit, location, normal, index, object, matrix = context.scene.ray_cast(context.view_layer, origin, direction)
    return hit, location, normal, index, object, matrix