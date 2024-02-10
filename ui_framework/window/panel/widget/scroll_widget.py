from .layout.grid.elements.background import Background_Element
from .layout.grid.elements.border import Border_Element
from ....utils.checks import is_mouse_in_quad

from ..widget.header_controller import Widget_Header_Controller

import copy
import time
import math

class Scroll_Widget():

    def __init__(self, db):

        # Data
        self.db = db
        self.win_key = ""

        # Containers
        self.layout = None
        self.layout_copy = None

        # Header
        self.collapsable = False
        self.header_layout = None
        self.header_controller = Widget_Header_Controller(db=self.db)
        self.header_height_percent = 0
        self.header_height = 0
        self.min_max_height = (0,0)

        # Layout Dims
        self.layout_width = 0
        self.bottom_left = (0, 0)
        self.bottom_right = (0, 0)
        self.top_left = (0, 0)
        self.top_right = (0, 0)

        # Layout Subdivide
        self.split_count_override = False
        self.split_count = 1
        self.start_slice = 0
        self.end_slice = 0

        # Scroll Bar
        self.scroll_bar = Scroll_Bar(db=self.db)
        self.bar_width = 0
        self.body_height = 0
        self.show_scroll_bar = True
        self.scroll_speed = 0

        # Scroll Bar Reset
        self.first_cycle = True
        self.last_row_count = 0

        # Scroll bar behaviors
        self.full_body_scroll_detection = True
        

    def setup(self, bottom_left=(0,0), bottom_right=(0,0), top_left=(0,0), top_right=(0,0)):
        '''The head function for the dimensions setup across the layouts.'''

        self.bottom_left = bottom_left
        self.bottom_right = bottom_right
        self.top_left = top_left
        self.top_right = top_right

        self.header_dims_setup()

        self.subdivide_body()

        # Body / Scroll Bar
        if self.layout != None:
            # Adjust the rendering layout
            self.layout_alter()
            self.body_setup()

            if self.show_scroll_bar:
                self.scroll_bar_setup()


    def header_dims_setup(self):
        
        self.header_height = (self.header_height_percent * (self.top_left[1] - self.bottom_left[1])) * .01

        if self.header_height > self.min_max_height[1]:
            self.header_height = self.min_max_height[1]

        elif self.header_height < self.min_max_height[0]:
            self.header_height = self.min_max_height[0]

        # Widget header controller adds the drop down toggle
        self.header_controller.header_layout = self.header_layout
        self.header_controller.collapsable = self.collapsable

        # Header
        if self.header_layout != None:
            self.header_setup()
        else:
            self.body_height = self.top_left[1] - self.bottom_left[1]


    def header_setup(self):
        '''Set the dimensions on the layout's header. '''

        self.body_height = (self.top_left[1] - self.bottom_left[1]) - self.header_height
        self.header_controller.body_height = self.body_height
        self.header_controller.bottom_left = self.bottom_left
        self.header_controller.bottom_right = self.bottom_right
        self.header_controller.top_left = self.top_left
        self.header_controller.top_right = self.top_right

        self.header_controller.setup()


    def subdivide_body(self):
        '''Set the split count for the body.'''

        # Subdivide the window
        height = self.top_left[1] - self.bottom_left[1]
        row_count = len(self.layout.rows)
        row_height = height / row_count if row_count > 0 else 1

        cell_height_split = self.db.ui_event.min_height * self.db.scale_factor

        if row_height > cell_height_split:
            if self.split_count_override == True:
                self.show_scroll_bar = True

            else:
                self.split_count = len(self.layout.rows)
                self.show_scroll_bar = False

        else:
            if self.split_count_override == False:
                self.split_count = int(height / cell_height_split)
            self.show_scroll_bar = True

        self.scroll_speed = row_height


    def layout_alter(self):
        '''Make a copy of the original layout. The copy will be drawn.'''

        self.layout_copy = copy.copy(self.layout)

        self.slice_rows()

        # Set row heights
        height_percent = 0
        if self.split_count < len(self.layout.rows):
            height_percent = 100 / self.split_count
        elif len(self.layout.rows) == 0:
            height_percent = 100
        else:
           height_percent = 100 / len(self.layout.rows)

        for row in self.layout_copy.rows:
            row.height_percent = height_percent


    def slice_rows(self):
        '''Slice the rows out of the original layout and insert them into the copy.'''

        self.reset_scroll_bar_on_change()

        row_height = self.body_height / len(self.layout.rows) if len(self.layout.rows) > 0 else self.body_height
        bottom_offset = self.scroll_bar.bottom_offset
        index = bottom_offset / row_height

        if index > int(index) + .5:
            index = math.ceil(index)
        else:
            index = int(index)

        # Prevent the scroll bar being at the top of the window slicing incorrectly when scaling window
        if self.split_count == len(self.layout.rows):
            index = 0

        self.start_slice = index
        self.end_slice = self.split_count + self.start_slice

        self.layout_copy.rows = self.layout_copy.rows[self.start_slice : self.end_slice]


    def reset_scroll_bar_on_change(self):
        '''Resets the scroll bar bottom offset if the list is rebuilt and the length is different.'''

        if self.first_cycle == False:
            if len(self.layout.rows) != self.last_row_count:
                self.last_row_count = len(self.layout.rows)
                self.scroll_bar.bottom_offset = 0

        if self.first_cycle == True:
            self.last_row_count = len(self.layout.rows)
            self.first_cycle = False


    def body_setup(self):
        '''Set the dimensions on the layouts body.'''

        self.layout_width = self.bottom_right[0] - self.bottom_left[0]

        if self.show_scroll_bar: 
            self.bar_width = (self.layout_width * self.scroll_bar.bar_width_percent) * .01

        else:
            self.bar_width = 0

        self.layout_copy.setup(bottom_left  =(self.bottom_left[0], self.bottom_left[1]), 
                               bottom_right =(self.bottom_right[0] - self.bar_width, self.bottom_right[1]),
                               top_left     =(self.top_left[0], self.top_left[1] - self.header_height),
                               top_right    =(self.top_right[0] - self.bar_width, self.top_right[1] - self.header_height))


    def scroll_bar_setup(self):
        '''Set the dimensions on the scroll bar.'''

        body_width = self.layout_width - self.bar_width

        row_height = self.body_height / len(self.layout.rows) if len(self.layout.rows) > 0 else self.body_height

        bar_height = row_height * self.split_count if len(self.layout.rows) > self.split_count else self.body_height

        self.scroll_bar.bar_height = bar_height
        self.scroll_bar.bottom_left = (self.bottom_left[0] + body_width, self.bottom_left[1])
        self.scroll_bar.bottom_right = (self.bottom_right[0], self.bottom_right[1])
        self.scroll_bar.top_left = (self.top_left[0] + body_width, self.top_left[1] - self.header_height)
        self.scroll_bar.top_right = (self.top_right[0], self.top_right[1] - self.header_height)

        self.scroll_bar.setup()


    def event(self):
        '''Run the event layer on the layouts and the scroll bar.'''
        
        # Header layout
        self.header_controller.event()

        # Body layout
        if not self.header_controller.collapsed:
            if self.layout != None:
                self.layout.event()

        # Scroll Bar
        if not self.header_controller.collapsed:
            self.scroll_bar.event()

        self.mouse_scrolling()


    def mouse_scrolling(self):

        mouse_over_scroll_box = False

        # Does the mouse scroll work on the entire window.
        if self.full_body_scroll_detection:
            mouse_over_scroll_box = is_mouse_in_quad(
                quad=(self.top_left, self.bottom_left, self.top_right, self.bottom_right), 
                mouse_pos=self.db.event.mouse_pos, 
                tolerance=0)
        # Only scrolls with mouse over scroll bar
        else:
            mouse_over_scroll_box = is_mouse_in_quad(
                quad=(self.scroll_bar.top_left, self.scroll_bar.bottom_left, self.scroll_bar.top_right, self.scroll_bar.bottom_right), 
                mouse_pos=self.db.event.mouse_pos, 
                tolerance=0)

        if mouse_over_scroll_box:
            if self.db.event.wheel_up:
                self.scroll_bar.bottom_offset += self.scroll_speed
                self.scroll_bar.clamp_offset()
            elif self.db.event.wheel_down:
                self.scroll_bar.bottom_offset -= self.scroll_speed
                self.scroll_bar.clamp_offset()


    def draw(self):
        '''Draw all the layouts.'''

        # Header layout
        self.header_controller.draw()

        if not self.header_controller.collapsed:

            # Body layout
            if self.layout_copy != None:
                self.layout_copy.draw()

            # Scroll Bar
            if self.show_scroll_bar:
                self.scroll_bar.draw()


class Scroll_Bar():

    def __init__(self, db):

        self.db = db

        # Dims
        self.bar_width_percent = 6
        self.bar_height = 0
        self.bottom_offset = 0

        self.bottom_left = (0, 0)
        self.bottom_right = (0, 0)
        self.top_left = (0, 0)
        self.top_right = (0, 0)

        # Event
        self.dragging = False

        # Elements
        self.elements()

    
    def elements(self):

        self.border = Border_Element()
        self.border.db = self.db

        self.bar = Background_Element()
        self.bar.db = self.db

        self.bar_border = Border_Element()
        self.bar_border.db = self.db


    def setup(self):
        '''Setup the dimensions for the drawable elements.'''

        self.setup_border()
        self.setup_bar()


    def setup_border(self):

        self.border.top_left = self.top_left
        self.border.top_right = self.top_right
        self.border.bottom_left = self.bottom_left
        self.border.bottom_right = self.bottom_right
        self.border.line_width = 2


    def setup_bar(self):

        self.bar.top_left = (self.bottom_left[0], self.bottom_left[1] + self.bar_height + self.bottom_offset)
        self.bar.top_right = (self.bottom_right[0], self.bottom_right[1] + self.bar_height + self.bottom_offset)
        self.bar.bottom_left = (self.bottom_left[0], self.bottom_left[1] + self.bottom_offset)
        self.bar.bottom_right = (self.bottom_right[0], self.bottom_right[1] + self.bottom_offset)
        self.bar.primary = False

        self.bar_border.top_left = (self.bottom_left[0], self.bottom_left[1] + self.bar_height + self.bottom_offset)
        self.bar_border.top_right = (self.bottom_right[0], self.bottom_right[1] + self.bar_height + self.bottom_offset)
        self.bar_border.bottom_left = (self.bottom_left[0], self.bottom_left[1] + self.bottom_offset)
        self.bar_border.bottom_right = (self.bottom_right[0], self.bottom_right[1] + self.bottom_offset)

        self.clamp_bar()


    def clamp_bar(self):

        if self.bar.top_left[1] > self.top_left[1]:

            self.bar.top_left = (self.bar.top_left[0], self.top_left[1])
            self.bar.top_right = (self.bar.top_right[0], self.top_right[1])
            self.bar.bottom_left = (self.bar.top_left[0], self.bar.top_left[1] - self.bar_height)
            self.bar.bottom_right = (self.bar.top_right[0], self.bar.top_right[1] - self.bar_height)

            self.bar_border.top_left = (self.bar.top_left[0], self.top_left[1])
            self.bar_border.top_right = (self.bar.top_right[0], self.top_right[1])
            self.bar_border.bottom_left = (self.bar.top_left[0], self.bar.top_left[1] - self.bar_height)
            self.bar_border.bottom_right = (self.bar.top_right[0], self.bar.top_right[1] - self.bar_height)

        elif self.bar.bottom_left[1] < self.bottom_left[1]:

            self.bar.top_left = (self.bottom_left[0], self.bottom_left[1] + self.bar_height)
            self.bar.top_right = (self.bottom_right[0], self.bottom_right[1] + self.bar_height)
            self.bar.bottom_left = self.bottom_left
            self.bar.bottom_right = self.bottom_right

            self.bar_border.top_left = (self.bottom_left[0], self.bottom_left[1] + self.bar_height)
            self.bar_border.top_right = (self.bottom_right[0], self.bottom_right[1] + self.bar_height)
            self.bar_border.bottom_left = self.bottom_left
            self.bar_border.bottom_right = self.bottom_right


    def event(self):

        if self.dragging:
            self.drag()

        else:

            mouse_over_scroll_box = False
            if not self.db.ui_event.window_transforming:
                mouse_over_scroll_box = is_mouse_in_quad(
                    quad=(self.top_left, self.bottom_left, self.top_right, self.bottom_right), 
                    mouse_pos=self.db.event.mouse_pos, 
                    tolerance=0)

            # Mouse is over the bar
            if mouse_over_scroll_box:
                if self.db.event.mouse_dragging:
                    self.db.ui_event.cell_blocking = True
                    self.bar.drag_highlight = True
                    self.bar.highlight = False
                    self.dragging = True

                else:
                    self.db.ui_event.cell_blocking = False
                    self.bar.drag_highlight = False
                    self.bar.highlight = True

            else:
                self.bar.highlight = False

        if self.db.event.left_click_released:
            self.db.ui_event.cell_blocking = False
            self.bar.drag_highlight = False
            self.dragging = False

        # Prevent bottom offset from staying at its value before scaling
        if self.db.ui_event.window_transforming:
            self.clamp_offset()


    def drag(self):

        self.bottom_offset += self.db.event.mouse_frame_diff[1]
        self.clamp_offset()


    def clamp_offset(self):

        if self.bottom_offset > self.top_left[1] - self.bottom_left[1] - self.bar_height:
            self.bottom_offset = self.top_left[1] - self.bottom_left[1] - self.bar_height

        elif self.bottom_offset < 0:
            self.bottom_offset = 0


    def draw(self):

        self.bar.draw()
        self.bar_border.draw()
        self.border.draw()
