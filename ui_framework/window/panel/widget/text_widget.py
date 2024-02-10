

class Text_Widget():

    def __init__(self):

        self.panel = None
        self.layout = None
        self.win_key = ""

        # Header
        self.header_layout = None
        self.header_height_percent = 0
        self.header_height = 0
        self.min_max_height = (0,0)


    def setup(self, bottom_left=(0,0), bottom_right=(0,0), top_left=(0,0), top_right=(0,0)):

        self.header_height = (self.header_height_percent * (top_left[1] - bottom_left[1])) * .01

        if self.header_height > self.min_max_height[1]:
            self.header_height = self.min_max_height[1]

        elif self.header_height < self.min_max_height[0]:
            self.header_height = self.min_max_height[0]

        # Header
        if self.header_layout != None:

            body_height = (top_left[1] - bottom_left[1]) - self.header_height

            self.header_layout.setup(bottom_left  =(bottom_left[0],  bottom_left[1] + body_height), 
                                     bottom_right =(bottom_right[0], bottom_right[1] + body_height),
                                     top_left     =(top_left[0],     top_left[1]),
                                     top_right    =(top_right[0],    top_right[1]))

        # Body
        if self.layout != None:

            self.layout.setup(bottom_left  =(bottom_left[0],  bottom_left[1]), 
                              bottom_right =(bottom_right[0], bottom_right[1]),
                              top_left     =(top_left[0],     top_left[1] - self.header_height),
                              top_right    =(top_right[0],    top_right[1] - self.header_height))


    def event(self):

        # Header layout
        if self.header_layout != None:
            self.header_layout.event()

        # Body layout
        if self.layout != None:
            self.layout.event()


    def draw(self):

        if self.header_layout != None:
            self.header_layout.draw()

        if self.layout != None:
            self.layout.draw()