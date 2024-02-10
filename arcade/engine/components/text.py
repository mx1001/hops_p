import bpy, math
from .... addon.utility.screen import dpi_factor
from .... ui_framework.utils.geo import get_blf_text_dims
from ..drawing.gl_funcs import draw_2D_text

class Text_Comp:

    def __init__(self, use_scale_factor=True):

        self.use_scale_factor = use_scale_factor

        self.scale_factor = dpi_factor(min=.25)
        if bpy.context.preferences.system.pixel_size == 2:
            self.scale_factor *= .75

        # Component Props
        self.location = (0,0)
        self.center = False
        self.text = ""
        self.__font_size = 16
        self.font_color = (1,1,1,1)

    @property
    def font_size(self):
        return self.__font_size

    @font_size.setter
    def font_size(self, val):
        if self.use_scale_factor:
            self.__font_size = int(val * self.scale_factor)
        else:
            self.__font_size = int(val)


    def draw(self, context):

        dims = (0, 0)
        if self.center == True:
            dims = get_blf_text_dims(self.text, self.__font_size)

        draw_2D_text(self.text, self.location[0] - dims[0] * .5, self.location[1], size=self.__font_size, color=self.font_color, dpi=72)