from .elements.background import Background_Element
from .elements.drag import Drag_Event
from ......utils.checks import is_mouse_in_quad

class Cell():

    def __init__(self):

        # Data
        self.db = None
        self.window_key = ""
        self.cell_index = None
        
        # Dims
        self.top_left = (0, 0)
        self.top_right = (0, 0)
        self.bottom_left = (0, 0)
        self.bottom_right = (0, 0)

        self.dims_override = (0, 0, 0, 0)

        # Drawing
        self.elements = []
        self.hover_highlight = True
        self.temp_elements = []

        # Events
        self.click_events = []
        self.drag_events = []


    def event(self):

        # Drag cell is being fired off
        if self.cell_index != None:
            if self.cell_index == self.db.ui_event.cell_index:
                for click_event in self.click_events:
                    if type(click_event) == Drag_Event:
                        click_event.cell_center_x = self.bottom_right[0] - (self.bottom_right[0] - self.bottom_left[0]) * .5
                        click_event.event()
                    else:
                        click_event.event()

        self.temp_elements = []

        # Mouse over highlight
        mouse_over = is_mouse_in_quad(
            quad=(self.top_left, self.bottom_left, self.top_right, self.bottom_right),
            mouse_pos=self.db.event.mouse_pos)

        if mouse_over:
            if not self.db.ui_event.cell_blocking:
                if not self.db.ui_event.window_transforming:
                    if self.hover_highlight:
                        self.add_highlight(dragging=False)

                    # Lock cell while mouse is dragging
                    if self.db.event.mouse_dragging:
                        self.db.ui_event.cell_blocking = True

                    # Call cell events
                    if self.db.event.left_clicked:
                        for click_event in self.click_events:
                            if type(click_event) == Drag_Event:
                                click_event.cell_center_x = self.bottom_right[0] - (self.bottom_right[0] - self.bottom_left[0]) * .5
                                click_event.set_hook()
                            else:
                                click_event.event()

                    # Scroll on drag cell
                    if self.db.event.wheel_up:
                        for click_event in self.click_events:
                            click_event.external_cell_event_call(positive=True)
                    if self.db.event.wheel_down:
                        for click_event in self.click_events:
                            click_event.external_cell_event_call(positive=False)


        elif self.cell_index != None:
            if self.cell_index == self.db.ui_event.cell_index:
                if not self.db.ui_event.window_transforming:
                    self.add_highlight(dragging=False)


    def add_highlight(self, dragging=False):

        highlight = Background_Element()
        highlight.db = self.db
        highlight.bevel = True

        if dragging:
            highlight.highlight = False
            highlight.drag_highlight = True

        else:
            highlight.highlight = True
            highlight.drag_highlight = False

        self.temp_elements.append(highlight)


    def draw(self):

        for element in self.elements:
            element.top_left =     (self.top_left[0]     + self.dims_override[0], self.top_left[1]     + self.dims_override[2])
            element.top_right =    (self.top_right[0]    + self.dims_override[1], self.top_right[1]    + self.dims_override[2])
            element.bottom_left =  (self.bottom_left[0]  + self.dims_override[0], self.bottom_left[1]  + self.dims_override[3])
            element.bottom_right = (self.bottom_right[0] + self.dims_override[1], self.bottom_right[1] + self.dims_override[3])
            element.draw()

        for element in self.temp_elements:
            element.top_left =     (self.top_left[0]     + self.dims_override[0], self.top_left[1]     + self.dims_override[2])
            element.top_right =    (self.top_right[0]    + self.dims_override[1], self.top_right[1]    + self.dims_override[2])
            element.bottom_left =  (self.bottom_left[0]  + self.dims_override[0], self.bottom_left[1]  + self.dims_override[3])
            element.bottom_right = (self.bottom_right[0] + self.dims_override[1], self.bottom_right[1] + self.dims_override[3])
            element.draw()