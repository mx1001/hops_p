import bpy, math, time
from .... addon.utility.screen import dpi_factor
from .... ui_framework.utils.geo import get_blf_text_dims
from .. drawing.gl_funcs import draw_2D_points, draw_2D_text


class Combo_Counter_Comp:
    '''Simple particle emitter.'''

    def __init__(self, use_scale_factor=True):

        self.use_scale_factor = use_scale_factor

        self.scale_factor = dpi_factor()
        if bpy.context.preferences.system.pixel_size == 2:
            self.scale_factor *= .75

        # Component Props
        self.delta_time = time.time()
        self.last_frame_end_time = time.time()
        self.transition_time = .75
        self.start_time = 0.0

        self.started = False

        # Global Controls
        self.location = (0,0)
        self.__text_gap = 30 * self.scale_factor

        # Combo Text
        self.current_text = ""
        self.new_text = ""
        self.font_color = (1,1,1,.5)
        self.text_dims = (0,0)
        self.__font_size = 64
        self.__scale_text_to = self.__font_size * 1.125

        # Lead Text
        self.lead_text = ""
        self.lead_font_color = (1,1,1,1)
        self.lead_text_dims = (0,0)
        self.__lead_font_size = 32

        # Particles
        self.particle_color = (1,1,1,.5)

    @ property
    def font_size(self):
        return self.__font_size

    @ font_size.setter
    def font_size(self, val):
        if self.use_scale_factor:
            self.__font_size = int(val * self.scale_factor)
            self.__scale_text_to = self.__font_size * 1.125
        else:
            self.__font_size = int(val)
            self.__scale_text_to = self.__font_size * 1.125

    @ property
    def lead_font_size(self):
        return self.__lead_font_size

    @ lead_font_size.setter
    def lead_font_size(self, val):
        if self.use_scale_factor:
            self.__lead_font_size = int(val * self.scale_factor)
        else:
            self.__lead_font_size = int(val)

    @ property
    def text_gap(self):
        return self.__text_gap

    @ text_gap.setter
    def text_gap(self, val):
        if self.use_scale_factor:
            self.__text_gap = int(val * self.scale_factor)
        else:
            self.__text_gap = int(val)


    def update_combo(self, location=(0,0), new_text="", lead_text=""):
        '''Call this function to explode particles.\n
        Params: 
            location -> center of combo text\n
            new_text -> what the combo text will update to\n
            lead_text -> the string in fron of the combo text'''
        
        if self.started == True:
            self.current_text = new_text

        self.started = True
        self.start_time = time.time()

        self.location = location
        self.new_text = new_text

        self.lead_text = lead_text

        self.text_dims = get_blf_text_dims(new_text, self.__font_size)
        self.lead_text_dims = get_blf_text_dims(lead_text, self.__lead_font_size)


    def draw(self, context):
        '''Draw any particles.'''

        # FPS
        self.delta_time = time.time() - self.last_frame_end_time

        #--- Initialize drawing ---#
        if self.lead_text != "":
            if self.lead_text_dims[0] <= 0:
                self.lead_text_dims = get_blf_text_dims(self.lead_text, self.__lead_font_size)
        if self.current_text != "":
            if self.text_dims[0] <= 0:
                self.text_dims = get_blf_text_dims(self.current_text, self.__font_size)

        # Draw lead text
        self.draw_lead_text()

        # Draw Action
        if self.started == True:
            time_from_start = time.time() - self.start_time

            if time_from_start <= self.transition_time:
                self.draw_combo_particles(time_from_start, self.delta_time)
                self.draw_combo_action(time_from_start)

            else:
                # Action is over set values
                self.started = False
                self.current_text = self.new_text


        # Draw Stationary
        else:
            self.draw_combo_stationary()

        self.last_frame_end_time = time.time()


    def draw_lead_text(self):
        '''Draw the text in front of the combo text.'''

        if self.lead_text != "":

            x_start_point = self.lead_text_dims[0] + self.__text_gap

            draw_2D_text(
                self.lead_text,
                self.location[0] - x_start_point,
                self.location[1],
                size=self.__lead_font_size,
                color=self.lead_font_color,
                dpi=72)


    def draw_combo_action(self, time_from_start=0):
        '''Draw the combo systems effects.'''
        
        temp_font_size = self.__font_size
        temp_text = ""
        temp_color = self.font_color

        # Old text
        if time_from_start < self.transition_time * .375:
            temp_text = self.current_text

            # Scale
            if time_from_start < self.transition_time * .125:
                lerp_factor = time_from_start / (self.transition_time * .125)
                temp_font_size += self.__scale_text_to * lerp_factor
                temp_font_size = int(temp_font_size)
            
            # Shrink
            else:
                temp_font_size += self.__scale_text_to
                start_time = self.transition_time * .125
                end_time = self.transition_time * .375
                lerp_factor = (time_from_start - start_time) / (end_time - start_time)
                temp_font_size *= 1 - lerp_factor
                temp_font_size = int(temp_font_size)

        # New text
        else:
            temp_text = self.new_text

            # Scale
            if time_from_start < self.transition_time * .5:
                start_time = self.transition_time * .25
                end_time = self.transition_time * .5
                lerp_factor = (time_from_start - start_time) / (end_time - start_time)
                temp_font_size += self.__scale_text_to * lerp_factor
                temp_font_size = int(temp_font_size)
            
            # Shrink
            else:
                temp_font_size += self.__scale_text_to
                start_time = self.transition_time * .5
                lerp_factor = (time_from_start - start_time) / (self.transition_time - start_time)
                
                scale_diff = temp_font_size - self.__font_size
                temp_font_size -= scale_diff * lerp_factor
                temp_font_size = int(temp_font_size)

                temp_color = (temp_color[0], temp_color[1], temp_color[2], 1 - lerp_factor)
                

        draw_2D_text(temp_text, self.location[0] - temp_font_size * .375, self.location[1], size=temp_font_size, color=temp_color, dpi=72)


    def draw_combo_particles(self, time_from_start, delta_time):
        '''Draw the particles for the combo system.'''

        lerp_factor = time_from_start / self.transition_time

        particle_size = 18 - (18 * lerp_factor)
        temp_color = (self.particle_color[0], self.particle_color[1], self.particle_color[2], 1 - lerp_factor)

        x_offset = 0

        if lerp_factor < .5:
            x_offset = lerp_factor * 75
        else:
            x_offset = lerp_factor * 20

        L1 = (self.location[0] - x_offset - 7 * self.scale_factor, self.location[1] + x_offset * .5 + self.text_dims[1] * .5)
        L2 = (self.location[0] - x_offset - 10 * self.scale_factor, self.location[1] + x_offset + self.text_dims[1] * .5)
        L3 = (self.location[0] - x_offset - 12 * self.scale_factor, self.location[1] + self.text_dims[1] * .5)
        L4 = (self.location[0] - x_offset - 3 * self.scale_factor, self.location[1] - x_offset * .5 + self.text_dims[1] * .5)
        L5 = (self.location[0] - x_offset - 15 * self.scale_factor, self.location[1] - x_offset + self.text_dims[1] * .5)

        text_offset = self.text_dims[0] if len(self.current_text) > 1 else 0
        R1 = (self.location[0] + x_offset + text_offset + 7 * self.scale_factor, self.location[1] + x_offset * .5 + self.text_dims[1] * .5)
        R2 = (self.location[0] + x_offset + text_offset + 10 * self.scale_factor, self.location[1] + x_offset + self.text_dims[1] * .5)
        R3 = (self.location[0] + x_offset + text_offset + 12 * self.scale_factor, self.location[1] + self.text_dims[1] * .5)
        R4 = (self.location[0] + x_offset + text_offset + 3 * self.scale_factor, self.location[1] - x_offset * .5 + self.text_dims[1] * .5)
        R5 = (self.location[0] + x_offset + text_offset + 15 * self.scale_factor, self.location[1] - x_offset + self.text_dims[1] * .5)

        points = [L1, L2, L3, L4, L5, R1, R2, R3, R4, R5]

        draw_2D_points(points, size=particle_size, color=temp_color)


    def draw_combo_stationary(self):
        '''Draw plain text.'''

        draw_2D_text(self.current_text, self.location[0] - self.__font_size * .375, self.location[1], size=self.__font_size, color=self.font_color, dpi=72)