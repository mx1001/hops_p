import bpy, math
from .... addon.utility.screen import dpi_factor
from ..drawing.gl_funcs import draw_2D_lines, draw_2D_geo


class Rectangle_Comp:

    def __init__(self, use_scale_factor=True):

        self.use_scale_factor = use_scale_factor
        self.scale_factor = dpi_factor(min=.25)
        if bpy.context.preferences.system.pixel_size == 2:
            self.scale_factor *= .75

        # Component Props
        self.__height = 10
        self.__width = 10
        self.location = (0,0)
        self.line_color = (1,1,1,1)
        self.poly_color = (.75,.75,1,1)

    @property
    def height(self):
        return self.__height

    @height.setter
    def height(self, val):
        if self.use_scale_factor:
            self.__height = val * self.scale_factor
        else:
            self.__height = val

    @property
    def width(self):
        return self.__width

    @width.setter
    def width(self, val):
        if self.use_scale_factor:
            self.__width = val * self.scale_factor
        else:
            self.__width = val


    def adjust_width_height(self, add_width=0, add_height=0):
        '''Add width and height, use this to bypass the scale factor.'''

        self.__height += add_height
        self.__width += add_width


    def draw(self, context):

        vertices = [
            (self.location[0] - self.__width * .5, self.location[1] - self.__height * .5),
            (self.location[0] - self.__width * .5, self.location[1] + self.__height * .5),
            (self.location[0] + self.__width * .5, self.location[1] + self.__height * .5),
            (self.location[0] + self.__width * .5, self.location[1] - self.__height * .5),
            (self.location[0] - self.__width * .5, self.location[1] - self.__height * .5)]

        # Polygon
        indices = [
            (0, 1, 2),
            (0, 2, 3)]
    
        # Draw
        draw_2D_geo(vertices, indices, color=self.poly_color)
        draw_2D_lines(vertices, width=2, color=self.line_color)