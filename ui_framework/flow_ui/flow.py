import bpy
from ..utils.geo import get_blf_text_dims
from ..utils.checks import is_mouse_in_quad
from ..graphics.draw import render_quad, render_text, draw_border_lines, draw_2D_lines, render_image
from ..graphics.load import load_image_file
from ...addon.utility.screen import dpi_factor
from ...preferences import get_preferences


####################################################
#   FLOW SYSTEM
####################################################

class Flow_Menu:
    '''Flow menu system.'''

    def __init__(self):
        # Event
        self.is_open = False
        self.exit_padding = 18 * dpi_factor(min=.25)

        # Data
        self.elements = []
        self.bounds = Bounds()

        # Draw Settings
        self.Hops_UI_cell_background_color = get_preferences().color.Hops_UI_cell_background_color
        self.Hops_UI_border_color = get_preferences().color.Hops_UI_border_color
        
        # Draw Data
        self.icon = load_image_file('logo_red')
        self.icon_size = 24 * dpi_factor(min=.25)

    # Setup flow
    def setup_flow_data(self, flow_data):
        '''Create all the elements.'''

        # Clear
        self.elements = []
        DATA.active_ref_key = None

        flow_data.reverse()

        # Create elements
        for index, item in enumerate(flow_data):
            element = Element(item)
            element.ref_key = index
            element.flow_form = item
            self.elements.append(element)

    # Modal func
    def run_updates(self, context, event):
        '''Modal func to handle window.'''

        if self.check_for_open(event):
            if self.is_open == False:
                self.open_menu(context, event)

        if self.is_open:
            self.update(context, event)

    # Check if should open window
    def check_for_open(self, event):
        '''Check if the window should open.'''

        # Check for shift click
        if event.type == 'SPACE' and event.value == 'PRESS':
            if event.shift == True:
                return True
            if event.alt == True:
                return True

        # if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
        #     if event.alt == True:
        #         if event.shift == False:
        #             if event.ctrl == False:
        #                 return True
        return False

    # Open window
    def open_menu(self, context, event):
        '''Update the window system.'''

        self.is_open = True
        DATA.active_ref_key = None
        mouse_pos = (event.mouse_region_x, event.mouse_region_y)

        # Setup window bounds
        # Get all the dims off each element
        all_dims = []
        for element in self.elements:
            dims = element.get_max_dims()
            all_dims.append(dims)

        # Get max dims
        max_width = 0
        max_height = 0
        for dims in all_dims:
            if dims[0] > max_width:
                max_width = dims[0]
            max_height += dims[1]

        # Assign flow window bounds
        self.bounds.bot_left  = (mouse_pos[0]            , mouse_pos[1] - max_height)
        self.bounds.bot_right = (mouse_pos[0] + max_width, mouse_pos[1] - max_height)
        self.bounds.top_left  = (mouse_pos[0]            , mouse_pos[1])
        self.bounds.top_right = (mouse_pos[0] + max_width, mouse_pos[1])

        # Setup element bounds
        y_offset = 0
        for element in self.elements:
            element.bounds.bot_left  = (self.bounds.bot_left[0] , self.bounds.bot_left[1] + y_offset)
            element.bounds.bot_right = (self.bounds.bot_right[0], self.bounds.bot_left[1] + y_offset)
            element.bounds.top_left  = (self.bounds.bot_left[0] , self.bounds.bot_left[1] + y_offset + element.max_dims[1])
            element.bounds.top_right = (self.bounds.bot_right[0], self.bounds.bot_left[1] + y_offset + element.max_dims[1])
            y_offset += element.max_dims[1]

        self.update(context, event)

    # Update flow while open
    def update(self, context, event):
        '''Update the flow system.'''

        mouse_pos = (event.mouse_region_x, event.mouse_region_y)
        clicked = True if event.type == 'LEFTMOUSE' and event.value == 'PRESS' else False

        # Setup
        for element in self.elements:
            element.update()

        # Event
        for element in self.elements:
            element.event(event)

        # Mouse left the window : Close
        quad = (
            self.bounds.top_left,
            self.bounds.bot_left,
            self.bounds.top_right,
            self.bounds.bot_right)

        if is_mouse_in_quad(quad=quad, mouse_pos=mouse_pos, tolerance=self.exit_padding) == False:
            self.is_open = False
            DATA.active_ref_key = None

    # Remove old data
    def shut_down(self):
        '''Remove images and clean up.'''

        if self.icon != None:
            try:
                bpy.data.images.remove(self.icon)
            except:
                pass

    # Draw flow while open
    def draw_2D(self):
        '''Draw all the elements.'''

        if self.is_open == False:
            return

        # Draw background
        render_quad(
            quad=(
                self.bounds.top_left,
                self.bounds.bot_left,
                self.bounds.top_right,
                self.bounds.bot_right),
            color=self.Hops_UI_cell_background_color,
            bevel_corners=True)

        draw_border_lines(
            vertices=[
                self.bounds.top_left,
                self.bounds.bot_left,
                self.bounds.top_right,
                self.bounds.bot_right],
            width=1,
            color=self.Hops_UI_border_color,
            bevel_corners=True,
            format_lines=False)

        # Draw elements
        for element in self.elements:
            element.draw()

        # Draw the icon
        if self.icon != None:
            verts = [
                (self.bounds.top_left[0] - self.icon_size, self.bounds.top_left[1] - self.icon_size),
                (self.bounds.top_left[0]                 , self.bounds.top_left[1] - self.icon_size),
                (self.bounds.top_left[0]                 , self.bounds.top_left[1]),
                (self.bounds.top_left[0] - self.icon_size, self.bounds.top_left[1])]
            render_image(self.icon, verts)

####################################################
#   DATA OBJECTS
####################################################

class DATA:
    active_ref_key = None


class Bounds:
    '''Generic dimension bounds.'''

    def __init__(self):
        self.bot_left  = (0,0)
        self.bot_right = (0,0)
        self.top_left  = (0,0)
        self.top_right = (0,0)


class Flow_Form:
    '''Controls flow menu elements.'''

    def __init__(self, text="", font_size=16, func=None, pos_args=None, neg_args=None, tip_box=""):
        self.text = text
        self.font_size = font_size
        self.func = func
        self.pos_args = pos_args
        self.neg_args = neg_args
        self.tip_box = tip_box

####################################################
#   ELEMENTS
####################################################

class Element:
    '''Text box element.'''

    def __init__(self, flow_form):
        self.flow_form = flow_form
        self.ref_key = 0
        self.font_pos = (0,0)
        self.font_color = get_preferences().color.Hops_UI_secondary_text_color
        self.font_padding = 12 * dpi_factor(min=.25)
        self.bounds = Bounds()
        self.max_dims = (0,0)
        # BG
        self.show_bg = False
        self.Hops_UI_mouse_over_color = get_preferences().color.Hops_UI_mouse_over_color
        self.Hops_UI_border_color = get_preferences().color.Hops_UI_border_color
        # Event
        self.mouse_pos = (0,0)
        # Tip Box
        self.tip_font_size = 12
        self.show_tip = False
        self.tip_bounds = Bounds()
        self.tip_list = []


    def get_max_dims(self):
        '''Get a tuple of the elements dims.'''

        text_dims = get_blf_text_dims(self.flow_form.text, self.flow_form.font_size)
        self.max_dims = (
            text_dims[0] + self.font_padding * 2,
            text_dims[1] + self.font_padding * 2)
        return self.max_dims


    def update(self):
        '''Update the elements dims.'''

        center_x = self.bounds.bot_right[0] - self.bounds.bot_left[0]
        center_x = (center_x * .5) + self.bounds.bot_left[0]

        center_y = (self.bounds.top_right[1] - self.bounds.bot_right[1])
        center_y = (center_y * .5) + self.bounds.bot_right[1]

        text_dims = get_blf_text_dims(self.flow_form.text, self.flow_form.font_size)

        self.font_pos = (
            center_x - (text_dims[0] * .5),
            center_y - (text_dims[1] * .5)) 


    def event(self, event):
        '''Run the event update on this element.'''

        # There is no call back
        if self.flow_form.func == None:
            if self.flow_form.tip_box == "":
                return

        # Mouse is over cell
        self.mouse_pos = (event.mouse_region_x, event.mouse_region_y)
        quad = (
            self.bounds.top_left,
            self.bounds.bot_left,
            self.bounds.top_right,
            self.bounds.bot_right)

        mouse_is_inside = False
        if is_mouse_in_quad(quad=quad, mouse_pos=self.mouse_pos):
            mouse_is_inside = True

            # Decide what to draw
            if self.flow_form.func != None:
                self.show_bg = True
            if self.flow_form.tip_box != "":
                self.show_tip = True
                self.calculate_tip_box()
        else:
            self.show_bg = False
            self.show_tip = False

        # Call backs
        if self.flow_form.func != None:
            if mouse_is_inside:

                # Click event
                if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                    if self.flow_form.pos_args != None:
                        self.flow_form.func(*self.flow_form.pos_args)
                    else:
                        self.flow_form.func()

    # Called from inside event on this element
    def calculate_tip_box(self):
        '''Setup tip box for rendering.'''

        self.tip_list = self.flow_form.tip_box.split(';')

        height = 0
        width = 0

        for tip in self.tip_list:
            text_dims = get_blf_text_dims(tip, self.tip_font_size)
            height += text_dims[1] + self.font_padding
            if text_dims[0] > width:
                width = text_dims[0]
        height += self.font_padding
        width += self.font_padding * 2

        # This box is to the right of the active box + font padding : the top is flush with the active box
        self.tip_bounds.top_left =  (self.font_padding + self.bounds.top_right[0]        , self.bounds.top_right[1])
        self.tip_bounds.top_right = (self.font_padding + self.bounds.top_right[0] + width, self.bounds.top_right[1])
        self.tip_bounds.bot_left =  (self.font_padding + self.bounds.top_right[0]        , self.bounds.top_right[1] - height)
        self.tip_bounds.bot_right = (self.font_padding + self.bounds.top_right[0] + width, self.bounds.top_right[1] - height)


    def draw(self):
        '''Draw the element.'''

        if self.show_bg == True:
            self.draw_bg()

        if self.show_tip == True:
            self.draw_tip_box()

        # Draw label
        render_text(self.flow_form.text, self.font_pos, self.flow_form.font_size, self.font_color)


    def draw_bg(self):
        '''If show bg is true draw highlight.'''

        # Draw background
        render_quad(
            quad=(
                self.bounds.top_left,
                self.bounds.bot_left,
                self.bounds.top_right,
                self.bounds.bot_right),
            color=self.Hops_UI_mouse_over_color,
            bevel_corners=True)

        draw_border_lines(
            vertices=[
                self.bounds.top_left,
                self.bounds.bot_left,
                self.bounds.top_right,
                self.bounds.bot_right],
            width=1,
            color=self.Hops_UI_border_color,
            bevel_corners=True,
            format_lines=False)


    def draw_tip_box(self):
        '''If flow form has hover box text.'''

        render_quad(
            quad=(
                self.tip_bounds.top_left,
                self.tip_bounds.bot_left,
                self.tip_bounds.top_right,
                self.tip_bounds.bot_right),
            color=self.Hops_UI_mouse_over_color,
            bevel_corners=True)

        draw_border_lines(
            vertices=[
                self.tip_bounds.top_left,
                self.tip_bounds.bot_left,
                self.tip_bounds.top_right,
                self.tip_bounds.bot_right],
            width=1,
            color=self.Hops_UI_border_color,
            bevel_corners=True,
            format_lines=False)

        # Draw all the text
        pos_x = self.tip_bounds.bot_left[0] + self.font_padding
        pos_y = self.tip_bounds.bot_left[1] + self.font_padding
        for tip in reversed(self.tip_list):
            render_text(tip, (pos_x, pos_y), self.tip_font_size, self.font_color)
            pos_y += get_blf_text_dims(tip, self.tip_font_size)[1] + self.font_padding