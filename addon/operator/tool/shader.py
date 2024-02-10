import bpy
import bmesh
import gpu

from math import cos, sin, pi
from statistics import median

from bgl import *
from gpu_extras.batch import batch_for_shader

from mathutils import Vector

from ... utility import addon, screen, view3d, method_handler
from .... graphics.drawing2d import draw_text
from .... utils.blender_ui import get_dpi_factor


class dots:
    handler: None

    def __init__(self, ot, context):
        method_handler(self.points,
            arguments = (ot, context),
            identifier = 'Dot Shader',
            exit_method = self.remove)


    def remove(self):
        if self.handler:
            self.handler = bpy.types.SpaceView3D.draw_handler_remove(self.handler, 'WINDOW')


    def points(self, ot, context):
        hardflow = context.window_manager.hardflow

        for point in hardflow.dots.points:
            self.point(ot, point)

    def point(self, ot, point):
        preference = addon.preference()
        size = addon.preference().display.dot_size * 0.5 * screen.dpi_factor()

        if point.highlight:
            col = Vector(preference.color.dot_highlight[:])
            if addon.preference().color.Bool_Dots_Text:
                if ot.highlight_type in {"Cut", "Union", "Slash", "Inset", "Intersect", "Knife"}:
                    selected = bpy.context.selected_objects
                    factor = get_dpi_factor()
                    origins = [obj.location for obj in selected]
                    if addon.preference().property.dots_snap == 'FIXED':
                        mid = Vector((addon.preference().property.dots_x, addon.preference().property.dots_y))
                    elif addon.preference().property.dots_snap == 'CURSOR':
                        mid = Vector((addon.preference().property.dots_x_cursor + ot.start_mouse[0], addon.preference().property.dots_y_cursor + ot.start_mouse[1]))
                    elif addon.preference().property.dots_snap == 'ORIGIN':
                        mid = view3d.location3d_to_location2d(median(origins))
                    draw_text("{}".format(ot.highlight_type), (mid.x - 12 * factor), (mid.y - 46 * factor), size=addon.preference().display.display_text_size_for_dots, color=addon.preference().color.Hops_hud_text_color)

                else:
                    factor = get_dpi_factor()
                    mid = Vector((ot.mouse[0] + 30, ot.mouse[1] + 40))
                    draw_text("{}".format(ot.highlight_modname), (mid.x - 12 * factor), (mid.y - 46 * factor), size=addon.preference().display.display_text_size_for_dots, color=addon.preference().color.Hops_hud_text_color)


        else:
            if point.color == 'red':
                col = Vector(preference.color.dot3[:])
            elif point.color == 'yellow':
                col = Vector(preference.color.dot4[:])
            elif point.color == 'green':
                col = Vector(preference.color.dot2[:])
            elif point.color == 'blue':
                col = Vector(preference.color.dot5[:])
            elif point.color == 'purple':
                col = Vector(preference.color.dot6[:])
            elif point.color == 'orange':
                col = Vector(preference.color.dot7[:])
            elif point.color == 'black':
                col = Vector((1, 1, 1, 0))

            elif point.color == 'displace_x':
                col = Vector(preference.color.displace_x[:])
            elif point.color == 'displace_y':
                col = Vector(preference.color.displace_y[:])
            elif point.color == 'displace_z':
                col = Vector(preference.color.displace_z[:])
            elif point.color == 'screw_x':
                col = Vector(preference.color.screw_x[:])
            elif point.color == 'screw_y':
                col = Vector(preference.color.screw_y[:])
            elif point.color == 'screw_z':
                col = Vector(preference.color.screw_z[:])
            elif point.color == 'solidify_x':
                col = Vector(preference.color.solidify_x[:])
            elif point.color == 'solidify_y':
                col = Vector(preference.color.solidify_y[:])
            elif point.color == 'solidify_z':
                col = Vector(preference.color.solidify_z[:])
            elif point.color == 'solidify_c':
                col = Vector(preference.color.solidify_c[:])
            elif point.color == 'array_x':
                col = Vector(preference.color.array_x[:])
            elif point.color == 'array_y':
                col = Vector(preference.color.array_y[:])
            elif point.color == 'array_z':
                col = Vector(preference.color.array_z[:])
            elif point.color == 'simple_deform_x':
                col = Vector(preference.color.simple_deform_x[:])
            elif point.color == 'simple_deform_y':
                col = Vector(preference.color.simple_deform_y[:])
            elif point.color == 'simple_deform_z':
                col = Vector(preference.color.simple_deform_z[:])
            elif point.color == 'wireframe_c':
                col = Vector(preference.color.wireframe_c[:])
            elif point.color == 'bevel_c':
                col = Vector(preference.color.bevel_c[:])

            else:
                col = Vector(preference.color.dot[:])

        square_dots = {'boolshape'}

        if point.type in square_dots:
            size *= 0.75
            vertices = (
                (point.location2d[0] - size, point.location2d[1] - size),
                (point.location2d[0] + size, point.location2d[1] - size),
                (point.location2d[0] - size, point.location2d[1] + size),
                (point.location2d[0] + size, point.location2d[1] + size))

            indices = ((0, 1, 2), (2, 1, 3))
        else:
            vertices = [(point.location2d[0], point.location2d[1])]

            for i in range(32):
                index = i + 1
                vertices.append((point.location2d[0] + cos(index * pi * 2 * 0.03125) * size, point.location2d[1] + sin(index * pi * 2 * 0.03125) * size))

            indices = [(0, i + 1, i + 2 if i + 2 < 32 else 1) for i in range(32)]

        if point.type not in square_dots:
            vert_edges = vertices[1:]
            vert_edges.append(vert_edges[6])

            indice_edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 10), (10, 11), (11, 12), (12, 13), (13, 14), (14, 15), (15, 16), (16, 17), (17, 18), (18, 19), (19, 20), (20, 21), (21, 22), (22, 23), (23, 24), (24, 25), (25, 26), (26, 27), (27, 28), (28, 29), (29, 30), (30, 31), (31, 32), (0, 32)]

            shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'LINES', {'pos': vert_edges}, indices=indice_edges)

            shader.bind()
            shader.uniform_float('color', col)

            width = 1

            glEnable(GL_LINE_SMOOTH)
            glEnable(GL_BLEND)
            # glEnable(GL_ALWAYS)
            glLineWidth(width)
            batch.draw(shader)
            glDisable(GL_LINE_SMOOTH)
            glDisable(GL_BLEND)

            del shader
            del batch

        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRIS', {'pos': vertices}, indices=indices)

        shader.bind()

        if point.type == 'boolshape':
            col[3] = col[3] * point.alpha

        shader.uniform_float('color', col)

        glEnable(GL_BLEND)
        batch.draw(shader)
        glDisable(GL_BLEND)

        del shader
        del batch


class grab:
    handler: None


    def __init__(self, ot, context):
        method_handler(self.draw_ui,
            arguments = (ot, context),
            identifier = 'UI Shader',
            exit_method = self.remove)


    def remove(self):
        if self.handler:
            self.handler = bpy.types.SpaceView3D.draw_handler_remove(self.handler, 'WINDOW')


    def draw_ui(self, ot, context):
        vertices = []
        size = 30

        for i in range(33):
            index = i + 1
            vertices.append((ot.mouse[0] + cos(index * pi * 2 * 0.03125) * size, ot.mouse[1] + sin(index * pi * 2 * 0.03125) * size))

        indice_edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 10), (10, 11), (11, 12), (12, 13), (13, 14), (14, 15), (15, 16), (16, 17), (17, 18), (18, 19), (19, 20), (20, 21), (21, 22), (22, 23), (23, 24), (24, 25), (25, 26), (26, 27), (27, 28), (28, 29), (29, 30), (30, 31), (31, 32), (32, 0)]

        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'LINES', {'pos': vertices}, indices=indice_edges)

        shader.bind()
        shader.uniform_float('color', (0.87, 0.87, 0.87, 0.3))

        width = 2

        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)
        glLineWidth(width)
        batch.draw(shader)
        glDisable(GL_LINE_SMOOTH)
        glDisable(GL_BLEND)

        del shader
        del batch
