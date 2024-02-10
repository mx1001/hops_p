from ....utils.checks import is_mouse_in_quad
from .layout.grid.elements.geo import Geo_Element
from .layout.grid.elements.border import Border_Element

class Widget_Header_Controller():
    '''Adds collapse to the header.'''

    def __init__(self, db):

        self.db = db
        self.header_layout = None

        # Dims
        self.body_height = 0
        self.collapse_width_percent = 10
        self.collapse_width_pixel = 0

        self.bottom_left = (0, 0)
        self.bottom_right = (0, 0)
        self.top_left = (0, 0)
        self.top_right = (0, 0)

        # Event
        self.collapsed = False
        self.mouse_over = False

        # Elements
        self.triangle = Geo_Element()
        self.border = Border_Element()
        self.init_elements()

        # Switches
        self.collapsable = True


    def init_elements(self):

        # Geo Element
        self.triangle.db = self.db
        self.triangle.selected_shape = "TRIANGLE_DOWN"
        self.triangle.selected_color = "SECONDARY"
        self.triangle.border = True
        self.triangle.padding = 6

        # Border Elements
        self.border.db = self.db
        self.border.line_width = 1


    def setup(self):

        if self.header_layout != None:

            if self.collapsable:

                body_width = self.bottom_right[0] - self.bottom_left[0]
                self.collapse_width_pixel = (self.collapse_width_percent * body_width) * .01

                self.header_layout.setup(bottom_left =(self.bottom_left[0] + self.collapse_width_pixel, self.bottom_left[1] + self.body_height), 
                                        bottom_right =(self.bottom_right[0],                            self.bottom_right[1] + self.body_height),
                                        top_left     =(self.top_left[0] + self.collapse_width_pixel,    self.top_left[1]),
                                        top_right    =(self.top_right[0],                               self.top_right[1]))

                self.setup_triangle()
                self.setup_border()

            else:

                body_width = self.bottom_right[0] - self.bottom_left[0]

                self.header_layout.setup(bottom_left =(self.bottom_left[0], self.bottom_left[1] + self.body_height), 
                                        bottom_right =(self.bottom_right[0],self.bottom_right[1] + self.body_height),
                                        top_left     =(self.top_left[0],    self.top_left[1]),
                                        top_right    =(self.top_right[0],   self.top_right[1]))


    
    def setup_triangle(self):

        self.triangle.top_left = (self.top_left[0], self.top_left[1])
        self.triangle.bottom_left = (self.bottom_left[0], self.bottom_left[1] + self.body_height)
        self.triangle.top_right = (self.top_left[0] + self.collapse_width_pixel, self.top_left[1])
        self.triangle.bottom_right = (self.bottom_left[0] + self.collapse_width_pixel, self.bottom_left[1] + self.body_height)


    def setup_border(self):
        
        self.border.top_left = (self.top_left[0], self.top_left[1])
        self.border.bottom_left = (self.bottom_left[0], self.bottom_left[1] + self.body_height)
        self.border.top_right = (self.top_left[0] + self.collapse_width_pixel, self.top_left[1])
        self.border.bottom_right = (self.bottom_left[0] + self.collapse_width_pixel, self.bottom_left[1] + self.body_height)


    def event(self):

        if self.collapsable:

            self.mouse_over = is_mouse_in_quad(
                quad=(
                    (self.top_left[0],                                self.top_left[1]),
                    (self.bottom_left[0],                             self.bottom_left[1] + self.body_height),
                    (self.top_left[0] + self.collapse_width_pixel,    self.top_left[1]),
                    (self.bottom_left[0] + self.collapse_width_pixel, self.bottom_left[1] + self.body_height)),
                mouse_pos=self.db.event.mouse_pos,
                tolerance=0)

            if self.db.event.left_clicked and self.mouse_over:
                if not self.db.ui_event.window_transforming:
                    if not self.db.ui_event.cell_blocking:
                        self.collapsed = not self.collapsed 

        # Run the event on the header layout
        if self.header_layout != None:
            self.header_layout.event()

    
    def draw(self):

        if self.header_layout != None:
            self.header_layout.draw()

            if self.collapsable:

                if self.collapsed:
                    self.triangle.selected_color = "HIGHLIGHT"
                    self.triangle.selected_shape = "TRIANGLE_RIGHT"
                else:
                    self.triangle.selected_color = "SECONDARY"
                    self.triangle.selected_shape = "TRIANGLE_DOWN"

                self.border.draw()
                self.triangle.draw()