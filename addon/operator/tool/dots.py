import bpy
from mathutils import Matrix, Vector

from ... utility import addon, view3d, screen


def update(ot, context, dots, mouse):
    obj = context.active_object

    ot.highlight_type = "none"
    ot.highlight = False
    ot.highlight_indices = []

    for index, point in enumerate(dots.points):
        location = view3d.location3d_to_location2d(point.location3d)
        point.location2d = location if location else (0, 0)
        point.highlight = False

        highlight = test_select(ot, point.location2d, mouse)

        if highlight:
            ot.highlight = True
            ot.highlight_indices.append(index)
            ot.highlight_location = obj.matrix_world.inverted() @ Vector((point.location3d[0], point.location3d[1], point.location3d[2]))

        if point.type == 'boolshape':
            location = view3d.location2d_intersect3d(ot.mouse.x, ot.mouse.y, point.location3d, Vector((0, 0, -1)))
            point_loc = Vector(point.location3d[:])
            if isinstance(location, Vector):
                distance = (location - point_loc).length
            else:
                distance = (Vector((0, 0, 0)) - point_loc).length
            fade_distance = addon.preference().display.dot_boolshape_fade_distance
            inverse = distance / fade_distance

            if inverse > 1:
                inverse = 1.0

            point.alpha = 1.0 - inverse
            point.display = inverse < 1.0

    if ot.highlight:
        closest = min([
            (mouse - Vector(dots.points[point].location2d[:]), point)
            for point in ot.highlight_indices])

        ot.active_point = dots.points[closest[1]]
        point = ot.active_point
        point.highlight = True
        dots.hit = True
        dots.location = point.location3d
        ot.highlight_type = point.type
        ot.highlight_modname = point.name

        del point
        del closest

    else:
        dots.hit = False
        dots.location = (0.0, 0.0, 0.0)
        dots.normal = Vector()


def test_select(ot, location, mouse):
    size = addon.preference().display.dot_size * screen.dpi_factor() * addon.preference().display.dot_detect
    location = Vector(location[:])
    within_x = mouse.x > location[0] - size and mouse.x < location[0] + size
    within_y = mouse.y > location[1] - size and mouse.y < location[1] + size

    return within_x and within_y
