import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from bgl import *
from mathutils import Vector
from .. utils.blender_ui import get_dpi_factor
from .. preferences import get_preferences
from .. utility import active_tool
from .. addon.utility import addon


def draw_logo_hops():
    object = bpy.context.active_object
    if addon.bc():
        tracked_states = bc_tracked_states()

    if object is not None:
        if object.hops.status == "BOOLSHAPE":
            color = get_preferences().color.Hops_logo_color_boolshape[:]
        else:
            color = get_preferences().color.Hops_logo_color[:]

    if addon.bc() and bpy.context.scene.bc.running:
        color = Vector(getattr(addon.bc().color, tracked_states.mode.lower()))
    # else:
    #     color = Vector(addon.bc().color.negative)
    else:
        color = get_preferences().color.Hops_logo_color[:]

    factor = get_dpi_factor()

    rw = rw = bpy.context.region.width#  - get_3d_view_tools_panel_overlay_width(bpy.context.area, "right")
    rh = bpy.context.region.height - 50 * factor
    d = get_preferences().color.Hops_logo_size * factor
    # x = get_preferences().color.Hops_logo_x_position * factor
    x = get_preferences().color.Hops_logo_x_position
    # y = get_preferences().color.Hops_logo_y_position * factor
    y = get_preferences().color.Hops_logo_y_position

    vertices = (
        (rw + 0*d + x, rh + (0*d + y)),
        (rw + 4*d + x, rh + (0*d + y)),
        (rw + 4*d + x, rh + (1*d + y)),
        (rw + 1*d + x, rh + (1*d + y)),
        (rw + 1*d + x, rh + (4*d + y)),
        (rw + 0*d + x, rh + (4*d + y)),

        (rw + 10*d + x, rh + (0*d + y)),
        (rw + 10*d + x, rh + (4*d + y)),
        (rw + 9*d + x, rh + (4*d + y)),
        (rw + 9*d + x, rh + (1*d + y)),
        (rw + 6*d + x, rh + (1*d + y)),
        (rw + 6*d + x, rh + (0*d + y)),

        (rw + 0*d + x, rh + (10*d + y)),
        (rw + 0*d + x, rh + (6*d + y)),
        (rw + 1*d + x, rh + (6*d + y)),
        (rw + 1*d + x, rh + (9*d + y)),
        (rw + 4*d + x, rh + (9*d + y)),
        (rw + 4*d + x, rh + (10*d + y)),

        (rw + 9*d + x, rh + (9*d + y)),
        (rw + 9*d + x, rh + (6*d + y)),
        (rw + 10*d + x, rh + (6*d + y)),
        (rw + 10*d + x, rh + (10*d + y)),
        (rw + 6*d + x, rh + (10*d + y)),
        (rw + 6*d + x, rh + (9*d + y)),

        (rw + 2.5*d + x, rh + (2*d + y)),
        (rw + 2.5*d + x, rh + (4*d + y)),
        (rw + 4*d + x, rh + (3.5*d + y)),
        (rw + 4*d + x, rh + (2*d + y)),

        (rw + 2.5*d + x, rh + (4*d + y)),
        (rw + 6*d + x, rh + (7.5*d + y)),
        (rw + 6.5*d + x, rh + (6*d + y)),
        (rw + 4*d + x, rh + (3.5*d + y)),

        (rw + 6*d + x, rh + (7.5*d + y)),
        (rw + 8*d + x, rh + (7.5*d + y)),
        (rw + 8*d + x, rh + (6*d + y)),
        (rw + 6.5*d + x, rh + (6*d + y))

        )

    indices = (
        (0, 1, 2), (2, 3, 0), (0, 4, 3), (0, 5, 4),
        (6, 7, 8), (8, 9, 6), (6, 10, 9), (6, 11, 10),
        (12, 13, 14), (14, 15, 12), (12, 16, 15), (12, 17, 16),
        (18, 19, 20), (20, 21, 18), (18, 22, 21), (18, 23, 22),
        (24, 25, 26), (26, 27, 24),
        (28, 29, 30), (30, 31, 28),
        (32, 33, 34), (34, 35, 32))

    vertices2 = (
        (rw + 0*d + x, rh + (0*d + y)),
        (rw + 4*d + x, rh + (0*d + y)),
        (rw + 4*d + x, rh + (1*d + y)),
        (rw + 1*d + x, rh + (1*d + y)),
        (rw + 1*d + x, rh + (4*d + y)),
        (rw + 0*d + x, rh + (4*d + y)),

        (rw + 10*d + x, rh + (0*d + y)),
        (rw + 10*d + x, rh + (4*d + y)),
        (rw + 9*d + x, rh + (4*d + y)),
        (rw + 9*d + x, rh + (1*d + y)),
        (rw + 6*d + x, rh + (1*d + y)),
        (rw + 6*d + x, rh + (0*d + y)),

        (rw + 0*d + x, rh + (10*d + y)),
        (rw + 0*d + x, rh + (6*d + y)),
        (rw + 1*d + x, rh + (6*d + y)),
        (rw + 1*d + x, rh + (9*d + y)),
        (rw + 4*d + x, rh + (9*d + y)),
        (rw + 4*d + x, rh + (10*d + y)),

        (rw + 9*d + x, rh + (9*d + y)),
        (rw + 9*d + x, rh + (6*d + y)),
        (rw + 10*d + x, rh + (6*d + y)),
        (rw + 10*d + x, rh + (10*d + y)),
        (rw + 6*d + x, rh + (10*d + y)),
        (rw + 6*d + x, rh + (9*d + y)),

        (rw + 8*d + x, rh + (2*d + y)),
        (rw + 2*d + x, rh + (2*d + y)),
        (rw + 2*d + x, rh + (8*d + y)),

        (rw + 6*d + x, rh + (4*d + y)),
        (rw + 7*d + x, rh + (3*d + y)),
        (rw + 7*d + x, rh + (7*d + y)),
        (rw + 6*d + x, rh + (6*d + y)),

        (rw + 3*d + x, rh + (7*d + y)),
        (rw + 7*d + x, rh + (7*d + y)),
        (rw + 6*d + x, rh + (6*d + y)),
        (rw + 4*d + x, rh + (6*d + y))

        )

    indices2 = (
        (0, 1, 2), (2, 3, 0), (0, 4, 3), (0, 5, 4),
        (6, 7, 8), (8, 9, 6), (6, 10, 9), (6, 11, 10),
        (12, 13, 14), (14, 15, 12), (12, 16, 15), (12, 17, 16),
        (18, 19, 20), (20, 21, 18), (18, 22, 21), (18, 23, 22),
        (24, 25, 26),
        (27, 28, 29),(29, 30, 27),
        (31, 32, 33),(33, 34, 31)
        )

    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')

    #if active_tool().idname == 'Boxcutter':
    if addon.bc() and bpy.context.scene.bc.running:
        batch = batch_for_shader(shader, 'TRIS', {"pos" : vertices2}, indices=indices2)
    else:
        batch = batch_for_shader(shader, 'TRIS', {"pos" : vertices}, indices=indices)

    shader.bind()
    shader.uniform_float("color", color)
    glEnable(GL_BLEND)
    batch.draw(shader)
    glDisable(GL_BLEND)

def bc_tracked_states():
    if addon.bc():
        import importlib
        BC = importlib.import_module(bpy.context.window_manager.bc.addon)
        return BC.addon.operator.shape.utility.tracked_states
    return None
