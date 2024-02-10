

class Panel():

    def __init__(self):

        self.window = None
        self.widget = None
        self.x_split_percent = 100
        self.y_split_percent = 100
        self.panel_width = 0
        self.panel_height = 0


    def setup(self, panel_index=0):
        '''Setup the dims for the widget.'''

        if self.widget != None:

            x_offset = 0
            y_offset = 0

            # Panels stacking side by side
            if self.window.stack_vertical == False:
                for i in range(panel_index):
                    x_offset += self.window.panels[i].panel_width


                self.panel_width = (self.window.body_width * self.x_split_percent) * .01
                self.panel_height = (self.window.body_height * self.y_split_percent) * .01

                bottom_left  = (self.window.bottom_left[0] + x_offset, self.window.bottom_left[1] + y_offset)
                top_left     = (self.window.top_left[0] + x_offset,    self.window.top_left[1] - self.window.header_height + y_offset)

                bottom_right = (self.window.bottom_left[0] + self.panel_width + x_offset, self.window.bottom_right[1] + y_offset)
                top_right    = (self.window.bottom_left[0] + self.panel_width + x_offset, self.window.top_right[1] - self.window.header_height + y_offset)

            # Panels stacking ontop of each other
            else:
                for i in range(panel_index):
                    y_offset += self.window.panels[i].panel_height

                self.panel_width = self.window.body_width
                self.panel_height = (self.window.body_height * self.y_split_percent) * .01

                bottom_left  = (self.window.bottom_left[0], self.window.bottom_left[1] + y_offset)
                top_left     = (self.window.top_left[0],    self.window.bottom_left[1] + self.panel_height + y_offset)

                bottom_right = (self.window.bottom_left[0] + self.panel_width, self.window.bottom_left[1] + y_offset)
                top_right    = (self.window.bottom_left[0] + self.panel_width, self.window.bottom_left[1] + self.panel_height + y_offset)

            self.widget.setup(bottom_left=bottom_left, 
                              bottom_right=bottom_right, 
                              top_left=top_left, 
                              top_right=top_right)


    def event(self):

        self.widget.event()


    def draw(self):

        if self.widget != None:
            self.widget.draw()