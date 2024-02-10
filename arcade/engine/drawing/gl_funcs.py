import gpu
import blf
import bgl
from bgl import *
from gpu_extras.batch import batch_for_shader


###############################################################
#   2D Drawing
###############################################################


def draw_2D_geo(vertices, indices, color=(1,1,1,1)):
    '''Render geo to the screen.'''

    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)
    shader.bind()
    shader.uniform_float("color", color)
    glEnable(GL_BLEND)
    batch.draw(shader)
    glDisable(GL_BLEND)

    del shader
    del batch


def draw_2D_lines(vertices, width=1, color=(0,0,0,1)):
    '''Draw lines to the screen.'''

    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_BLEND)
    glLineWidth(width)
    batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": vertices})
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)
    glDisable(GL_BLEND)

    del shader
    del batch


def draw_2D_points(vertices, size=3, color=(0,0,0,1)):
    '''Draw lines to the screen.'''

    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    glPointSize(size)
    glEnable(GL_BLEND)
    batch = batch_for_shader(shader, 'POINTS', {"pos": vertices})
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)
    glDisable(GL_BLEND)

    del shader
    del batch


def draw_2D_text(text, x, y, size=12, color=(1,1,1,1), dpi=72):
    '''Draw text to the screen.'''

    font_id = 0
    blf.position(font_id, x, y, 0)
    blf.size(font_id, size, dpi)
    blf.color(font_id, *color)
    blf.draw(font_id, text)