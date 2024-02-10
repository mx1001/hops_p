import bpy, math
from .... addon.utility.screen import dpi_factor
from .. drawing.gl_funcs import draw_2D_lines


class Trail_Render_Comp:

    def __init__(self):

        self.scale_factor = dpi_factor()
        if bpy.context.preferences.system.pixel_size == 2:
            self.scale_factor *= .75

        # Component Props
        self.vert_limits = 25
        self.line_width = 2
        self.line_color = (1,1,1,.125)
        self.vertices = []


    def remove_trail(self):
        '''Remove the trail.'''

        self.vertices = []


    def update(self, new_point=(0,0)):
        '''Update the trail render.'''

        self.vertices.append(new_point)
        self.vertices = self.vertices[-self.vert_limits:]


    def draw(self, context):

        draw_2D_lines(self.vertices, width=self.line_width, color=self.line_color)