import gpu
import blf
import bgl
from bgl import *
from gpu_extras.batch import batch_for_shader

from .. utils.geo import bevel_verts
from ... preferences import get_preferences
from ... utils.blender_ui import get_dpi, get_dpi_factor



def render_quad(quad=((0,1), (0,0), (1,1), (0,1)), color=(1,1,1,1), bevel_corners=True):
    '''Render quads passed in. \n
        Top Left, Bottom Left, Top Right, Bottom Right
    '''

    indices = [(0, 1, 2), (1, 2, 3)]
    vertices = [quad[0], quad[1], quad[2], quad[3]]

    if bevel_corners:
        vertices, indices = bevel_verts(quad)

    #Drawing quad
    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)
    shader.bind()
    shader.uniform_float("color", color)
    glEnable(GL_BLEND)
    batch.draw(shader)
    glDisable(GL_BLEND)

    del shader
    del batch


def render_geo(verts=[], indices=[], color=(1,1,1,1)):
    '''Render geo passed in.'''

    #Draw
    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'TRIS', {"pos": verts}, indices=indices)
    shader.bind()
    shader.uniform_float("color", color)
    glEnable(GL_BLEND)
    batch.draw(shader)
    glDisable(GL_BLEND)

    del shader
    del batch


def render_text(text="", position=(0, 0), size=12, color=(1,1,1,1)):
    draw_text(str(text), position[0], position[1], align="LEFT", size=size, color=color)


def draw_border_lines(vertices=[], width=1, color=(0,0,0,1), bevel_corners=True, format_lines=False):
    '''Render quads passed in. \n
        Top Left, Bottom Left, Top Right, Bottom Right
    '''

    if bevel_corners:
        vertices = [vertices[0], vertices[1], vertices[2], vertices[3]]
        vertices, _ = bevel_verts(vertices)
        vertices.append(vertices[0])

    elif format_lines == True:
        vertices = [vertices[0],vertices[1],vertices[3],vertices[2],vertices[0]]


    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_BLEND)
    glLineWidth(width)
    batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": vertices})
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)

    glLineWidth(width)
    glDisable(GL_BLEND)

    del shader
    del batch


def render_image(image, verts):
    '''bottom left, bottom right, top right, top left'''

    shader = gpu.shader.from_builtin('2D_IMAGE')
    text_coords = ((0, 0), (1, 0), (1, 1), (0, 1))

    batch = batch_for_shader(
        shader, 'TRI_FAN',
        {
            "pos": verts,
            "texCoord": text_coords,
        },
    )

    if image.gl_load():
        raise Exception()


    bgl.glActiveTexture(bgl.GL_TEXTURE0)
    bgl.glBindTexture(bgl.GL_TEXTURE_2D, image.bindcode)
    glEnable(GL_BLEND)

    shader.bind()
    shader.uniform_int("image", 0)
    batch.draw(shader)

    image.gl_free()
    glDisable(GL_BLEND)

    del shader
    del batch


def draw_text(text, x, y, align="LEFT", size=12, color=(1, 1, 1, 1), dpi=None):

    #Prefs
    prefs = get_preferences()
    prefs_ui_scale = prefs.ui.Hops_modal_size

    if dpi == None:
        dpi = int(get_dpi() * prefs_ui_scale)

    font = 0
    blf.size(font, size, int(dpi))
    blf.color(font, *color)

    if align == "LEFT":
        blf.position(font, x, y, 0)
    else:
        width, height = blf.dimensions(font, text)
        if align == "RIGHT":
            blf.position(font, x - width, y, 0)

    blf.draw(font, text)    


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