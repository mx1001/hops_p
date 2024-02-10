import bpy, math
from .... addon.utility.screen import dpi_factor
from ..drawing.gl_funcs import draw_2D_lines, draw_2D_geo


class Circle_Comp:

    def __init__(self):

        self.scale_factor = dpi_factor()
        if bpy.context.preferences.system.pixel_size == 2:
            self.scale_factor *= .75

        # Component Props
        self.__radius = 10
        self.location = (0,0)
        self.line_color = (1,1,1,1)
        self.poly_color = (.75,.75,1,1)

    @property
    def radius(self):
        return self.__radius

    @radius.setter
    def radius(self, val):
        self.__radius = val * self.scale_factor


    def draw(self, context):

        # Border
        segments = 20
        vertices = []

        for i in range(segments):
            index = i + 1
            angle = i * 3.14159 * 2 / segments
            x = math.cos(angle) * self.__radius
            y = math.sin(angle) * self.__radius

            x += self.location[0]
            y += self.location[1]

            vertices.append((x, y))

        first_vert = vertices[0]
        vertices.append(first_vert)

        # Polygon
        indices = []
        for i in range(len(vertices)):
            if i == len(vertices) - 2:
                break
            indices.append((0, i, i+1))
    

        # Draw
        draw_2D_geo(vertices, indices, color=self.poly_color)
        draw_2D_lines(vertices, width=1, color=self.line_color)