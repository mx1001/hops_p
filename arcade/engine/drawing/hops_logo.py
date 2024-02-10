import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from bgl import *
from mathutils import Vector
from .... utils.blender_ui import get_dpi_factor
from .... preferences import get_preferences


def draw_arcade_hops_logo(color=(0,0,0,.5), size=100, x=100, y=100):
    '''Draw the hops logo.\n
    Notes: Max Width = 10px, Max Height = 10px'''

    factor = get_dpi_factor()
    d = size * factor

    vertices = (
        (0*d + x, 0*d + y),
        (4*d + x, 0*d + y),
        (4*d + x, 1*d + y),
        (1*d + x, 1*d + y),
        (1*d + x, 4*d + y),
        (0*d + x, 4*d + y),

        (10*d + x, 0*d + y),
        (10*d + x, 4*d + y),
        (9*d + x,  4*d + y),
        (9*d + x,  1*d + y),
        (6*d + x,  1*d + y),
        (6*d + x,  0*d + y),

        (0*d + x, 10*d + y),
        (0*d + x, 6*d + y),
        (1*d + x, 6*d + y),
        (1*d + x, 9*d + y),
        (4*d + x, 9*d + y),
        (4*d + x, 10*d + y),

        (9*d + x,  9*d + y),
        (9*d + x,  6*d + y),
        (10*d + x, 6*d + y),
        (10*d + x, 10*d + y),
        (6*d + x,  10*d + y),
        (6*d + x,  9*d + y),

        (2.5*d + x, 2*d + y),
        (2.5*d + x, 4*d + y),
        (4*d + x,   3.5*d + y),
        (4*d + x,   2*d + y),

        (2.5*d + x, 4*d + y),
        (6*d + x,   7.5*d + y),
        (6.5*d + x, 6*d + y),
        (4*d + x,   3.5*d + y),

        (6*d + x,   7.5*d + y),
        (8*d + x,   7.5*d + y),
        (8*d + x,   6*d + y),
        (6.5*d + x, 6*d + y))

    indices = (
        (0, 1, 2), (2, 3, 0), (0, 4, 3), (0, 5, 4),
        (6, 7, 8), (8, 9, 6), (6, 10, 9), (6, 11, 10),
        (12, 13, 14), (14, 15, 12), (12, 16, 15), (12, 17, 16),
        (18, 19, 20), (20, 21, 18), (18, 22, 21), (18, 23, 22),
        (24, 25, 26), (26, 27, 24),
        (28, 29, 30), (30, 31, 28),
        (32, 33, 34), (34, 35, 32))

    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'TRIS', {"pos" : vertices}, indices=indices)
    shader.bind()
    shader.uniform_float("color", color)
    glEnable(GL_BLEND)
    batch.draw(shader)
    glDisable(GL_BLEND)
