import bpy, math, time
from .... addon.utility.screen import dpi_factor
from .... ui_framework.utils.geo import get_blf_text_dims
from ..drawing.gl_funcs import draw_2D_text

class Marquee_Comp:

    def __init__(self, use_scale_factor=True):

        self.use_scale_factor = use_scale_factor

        self.scale_factor = dpi_factor()
        if bpy.context.preferences.system.pixel_size == 2:
            self.scale_factor *= .75

        # Component Props
        self.top_left = (0,0)
        self.marquee_text = {} # Key = Header Text, Val = List of strings
        self.hold_time = 1.0
        self.cycle_start_time = time.time()
        self.start_slice_index = 0
        self.body_display_count = 2
        self.start_key = ""
        self.__text_padding_y = 5 * self.scale_factor
        self.keys = []

        # Header
        self.header_dims = (0,0)
        self.__header_font_size = int(24 * self.scale_factor)
        self.header_font_color = (1,1,1,1)

        # Body
        self.body_dims = (0,0)
        self.__body_font_size = int(16 * self.scale_factor)
        self.body_font_color = (1,1,1,1)

    @ property
    def header_font_size(self):
        return self.__header_font_size

    @ header_font_size.setter
    def header_font_size(self, val):
        if self.use_scale_factor:
            self.__header_font_size = int(val * self.scale_factor)
        else:
            self.__header_font_size = int(val)

    @ property
    def body_font_size(self):
        return self.__body_font_size

    @ body_font_size.setter
    def body_font_size(self, val):
        if self.use_scale_factor:
            self.__body_font_size = int(val * self.scale_factor)
        else:
            self.__body_font_size = int(val)

    @ property
    def text_padding_y(self):
        return self.__text_padding_y

    @ text_padding_y.setter
    def text_padding_y(self, val):
        if self.use_scale_factor:
            self.__text_padding_y = int(val * self.scale_factor)
        else:
            self.__text_padding_y = int(val)


    def setup(self):
        '''Call this function inside of Invoke, make sure to set all variables first.'''

        self.start_key = ""
        self.keys = []

        # Setup all the text dims: assigns the longest on from each item
        for key, val in self.marquee_text.items():
            
            self.keys.append(key)

            # See if the start key needs to be set
            if self.start_key != "" or self.start_key not in self.marquee_text:
                self.start_key = key

            temp_header_dims = get_blf_text_dims(str(key), self.__header_font_size)

            if temp_header_dims[0] > self.header_dims[0]:
                self.header_dims = temp_header_dims

            for string in val:
                temp_body_dims = get_blf_text_dims(str(string), self.__body_font_size)

                if temp_body_dims[0] > self.body_dims[0]:
                    self.body_dims = temp_body_dims


    def draw(self, context):

        # Catch basic errors
        if self.start_key not in self.marquee_text:
            return


        #--- Draw header ---#
        header_loc = (self.top_left[0], self.top_left[1] - self.header_dims[1])
        draw_2D_text(self.start_key, header_loc[0], header_loc[1], size=self.__header_font_size, color=self.header_font_color, dpi=72)

        #--- Draw body ---#
        # Slice the items
        body_text = self.marquee_text[self.start_key][ self.start_slice_index : self.start_slice_index + self.body_display_count ]
        body_loc = (self.top_left[0], header_loc[1] - self.body_dims[1] - self.__text_padding_y)
        for text in body_text:
            draw_2D_text(text, body_loc[0], body_loc[1], size=self.__body_font_size, color=self.body_font_color, dpi=72)
            body_loc = (body_loc[0], body_loc[1] - self.body_dims[1] - self.__text_padding_y)

        # Cycle the text around
        # If the slice is at the end go to the next key
        if time.time() - self.cycle_start_time >= self.hold_time:
            self.cycle_start_time = time.time()
            if self.start_slice_index + self.body_display_count > len(self.marquee_text[self.start_key]):
                self.start_slice_index = 0

                # Go to the next key
                if len(self.keys) > 1:
                    index = self.keys.index(self.start_key)

                    # Determin if the cycle goes foward or starts over
                    if index + 1 > len(self.keys) - 1:
                        self.start_key = self.keys[0]

                    else:
                        self.start_key = self.keys[index + 1]

            self.start_slice_index += 1
