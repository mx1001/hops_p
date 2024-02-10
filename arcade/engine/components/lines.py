import bpy, math
from .... addon.utility.screen import dpi_factor
from ..drawing.gl_funcs import draw_2D_lines, draw_2D_geo


class Lines_Comp:

    def __init__(self):

        self.scale_factor = dpi_factor()
        if bpy.context.preferences.system.pixel_size == 2:
            self.scale_factor *= .75

        # Component Props
        self.line_width = 2
        self.line_color = (1,1,1,1)
        self.vertices = []


    def draw(self, context):

        draw_2D_lines(self.vertices, width=self.line_width, color=self.line_color)