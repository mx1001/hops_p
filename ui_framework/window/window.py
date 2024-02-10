from ..graphics.draw import draw_border_lines, render_quad
from ..utils.checks import is_mouse_in_quad
from ...utils.cursor_warp import get_screen_warp_padding

class Window():

    def __init__(self, db=None, window_key=""):

        # Data
        self.db = db
        self.window_key = window_key
        self.visible = True 

        # Event
        self.active = False

        # Dims
        self.top_left = (0, 0)
        self.top_right = (0, 0)
        self.bottom_left = (0, 0)
        self.bottom_right = (0, 0)
        self.scale = (0, 0)
        self.body_width = 0
        self.body_height = 0

        # Tree
        self.panels = []
        self.stack_vertical = False

        # Drawing
        self.elements = []

        # Header
        self.header_layout = None
        self.header_height_percent = 0
        self.header_height = 0
        self.min_max_height = (0,0)

        # Gizmo
        self.win_gizmo = Window_Gizmo(window=self)


    def setup(self):

        # Saved Dims
        if self.window_key == "Main":
            self.bottom_left = self.db.prefs.ui.Hops_modal_main_window_bottom_left
            self.scale = self.db.prefs.ui.Hops_modal_main_window_scale
        
        elif self.window_key == "Help":
            self.bottom_left = self.db.prefs.ui.Hops_modal_help_window_bottom_left
            self.scale = self.db.prefs.ui.Hops_modal_help_window_scale

        elif self.window_key == "Mods":
            self.bottom_left = self.db.prefs.ui.Hops_modal_mods_window_bottom_left
            self.scale = self.db.prefs.ui.Hops_modal_mods_window_scale

        elif self.window_key == "Kit_Ops":
            self.bottom_left = self.db.prefs.ui.Hops_modal_kit_ops_window_bottom_left
            self.scale = self.db.prefs.ui.Hops_modal_kit_ops_window_scale

        elif self.window_key == "Pizza_Ops":
            self.bottom_left = self.db.prefs.ui.Hops_modal_pizza_ops_window_bottom_left
            self.scale = self.db.prefs.ui.Hops_modal_pizza_ops_window_scale

        elif self.window_key == "Brush_Ops":
            self.bottom_left = self.db.prefs.ui.Hops_modal_sculpt_ops_window_bottom_left
            self.scale = self.db.prefs.ui.Hops_modal_sculpt_ops_window_scale

        self.check_initial_window_placement()

        self.header_height = (self.header_height_percent * self.scale[1]) * .01

        if self.header_height > self.min_max_height[1]:
            self.header_height = self.min_max_height[1]

        elif self.header_height < self.min_max_height[0]:
            self.header_height = self.min_max_height[0]
            
        self.top_left = (self.bottom_left[0], self.bottom_left[1] + self.scale[1])

        self.top_right = (self.bottom_left[0] + self.scale[0], self.bottom_left[1] + self.scale[1])

        self.bottom_right = (self.bottom_left[0] + self.scale[0], self.bottom_left[1])

        self.body_width = self.bottom_right[0] - self.bottom_left[0]

        self.body_height = (self.top_left[1] - self.bottom_left[1]) - self.header_height

        self.stack_vertical = True if self.body_height > self.body_width else False

        # Setup the header layout
        if self.header_layout != None:
            self.header_layout.setup(bottom_left=(self.bottom_left[0], self.top_left[1] - self.header_height), 
                                     bottom_right=(self.bottom_right[0], self.top_right[1] - self.header_height),
                                     top_left=self.top_left, 
                                     top_right=self.top_right)

        # Setup all the panels
        count = 0
        for panel in self.panels:
            panel.setup(panel_index=count)
            count += 1

        # Setup move gizmo
        self.win_gizmo.setup()
  

    def check_initial_window_placement(self):
        '''Place the windows centered if they are loaded for the first time.'''

        if self.window_key == "Main":
            # The defualt factory load location
            if self.bottom_left[0] == 60 and self.bottom_left[1] == 30:
                win_width = self.scale[0]
                screen_width = self.db.event.screen_width
                self.bottom_left = (
                    (screen_width * .5) - (win_width * .5),
                    30 * self.db.scale_factor)
                self.db.prefs.ui.Hops_modal_main_window_bottom_left = self.bottom_left
                self.win_gizmo.bottom_left = self.bottom_left

        elif self.window_key == "Help":
            # The defualt factory load location
            if self.bottom_left[0] == 20 and self.bottom_left[1] == 30:
                win_width = self.scale[0]
                screen_width = self.db.event.screen_width
                self.bottom_left = (
                    screen_width - win_width - self.win_gizmo.width - self.win_gizmo.offset,
                    30 * self.db.scale_factor)
                self.db.prefs.ui.Hops_modal_help_window_bottom_left = self.bottom_left
                self.win_gizmo.bottom_left = self.bottom_left

        elif self.window_key == "Mods":
            # The defualt factory load location
            if self.bottom_left[0] == 300 and self.bottom_left[1] == 30:
                self.bottom_left = (
                    self.win_gizmo.width + self.win_gizmo.offset,
                    30 * self.db.scale_factor)
                self.db.prefs.ui.Hops_modal_mods_window_bottom_left = self.bottom_left
                self.win_gizmo.bottom_left = self.bottom_left

        elif self.window_key == "Pizza_Ops":
            # The defualt factory load location
            if self.bottom_left[0] == 20 and self.bottom_left[1] == 30:
                win_width = self.scale[0]
                screen_width = self.db.event.screen_width
                self.bottom_left = (
                    (screen_width * .5) - (win_width * .5),
                    30 * self.db.scale_factor)
                self.db.prefs.ui.Hops_modal_pizza_ops_window_bottom_left = self.bottom_left
                self.win_gizmo.bottom_left = self.bottom_left

        elif self.window_key == "Brush_Ops":
            # The defualt factory load location
            if self.bottom_left[0] == 20 and self.bottom_left[1] == 30:
                win_width = self.scale[0]
                screen_width = self.db.event.screen_width
                self.bottom_left = (
                    (screen_width * .5) - (win_width * .5),
                    30 * self.db.scale_factor)
                self.db.prefs.ui.Hops_modal_sculpt_ops_window_bottom_left = self.bottom_left
                self.win_gizmo.bottom_left = self.bottom_left


    def event_check(self):
        '''Test if the window has events happening on it.'''

        # Window
        mouse_over_window = is_mouse_in_quad(
            quad=(self.top_left, self.bottom_left, self.top_right, self.top_left),
            mouse_pos=self.db.event.mouse_pos,
            tolerance=0)

        # Gizmo
        self.win_gizmo.event_check()

        # Set the active window
        if mouse_over_window or self.win_gizmo.mouse_over_move or self.win_gizmo.mouse_over_scale:
            if self.db.ui_event.active_window_key == "":
                self.db.ui_event.active_window_key = self.window_key  
                self.active = True
        else:
            self.active = False


    def run_event(self):
        '''If the window has events happening on it run the event cycle on the window.'''

        self.win_gizmo.event()

        if not self.db.ui_event.window_transforming:
            if self.header_layout != None:
                self.header_layout.event()

        #TODO: Probably add something to see if the header is blocking the UI before moving one

        for panel in self.panels:
            panel.event()


    def header_event(self):
        '''Run the header event.'''

        self.header_layout.event()


    def panel_event(self):
        '''Events for the panels in the window.'''

        #if self.window_key == self.db.cell.active_target_win_key:
        for panel in self.panels:
            panel.event()


    def draw(self):

        # Draw the window elements
        if self.elements != []:
            for element in self.elements:
                element.top_left = self.top_left
                element.top_right = self.top_right
                element.bottom_left = self.bottom_left
                element.bottom_right = self.bottom_right
                element.draw()


        # Draw the header layout
        if self.header_layout != None:
            self.header_layout.draw()

        # Draw all the panels
        if self.panels != []:
            for panel in self.panels:
                panel.draw()

        # Window Gizmos
        self.win_gizmo.draw()


    def clear_layouts(self):

        for panel in self.panels:
            if panel.widget.layout != None:
                panel.widget.layout.rows = []


class Window_Gizmo():

    def __init__(self, window):

        # Window the widget is on
        self.window = window
        self.win_height = 0
        self.win_width = 0

        # Dims
        self.width = 5
        self.offset = 15

        self.bottom_left = None
        self.scale = None

        # Color
        self.color = (0,0,0,.5)

        # Left Side: Top
        self.left_side_top = []

        # Left Side: Bottom
        self.left_side_bottom = []

        # Right Side: Top
        self.right_side_top = []

        # Right Side: Bottom
        self.right_side_bottom = []
    
        # Event
        self.mouse_over_scale = False
        self.mouse_over_move = False

        # Warp bounds
        self.warp_bounds = get_screen_warp_padding() if self.window.db.prefs.ui.Hops_warp_mode else 0


    def setup(self):

        self.win_height = self.window.top_right[1] - self.window.bottom_left[1]
        self.win_width = self.window.bottom_right[0] - self.window.bottom_left[0]

        # Left Side: Top
        self.left_side_top = [
            (self.window.bottom_left[0] - self.offset - self.width, self.window.bottom_left[1] + self.win_height * .25),
            (self.window.bottom_left[0] - self.offset - self.width, self.window.bottom_left[1] - self.offset - self.width),
            (self.window.bottom_left[0] - self.offset,              self.window.bottom_left[1] + self.win_height * .25),
            (self.window.bottom_left[0] - self.offset,              self.window.bottom_left[1] - self.offset - self.width)
        ]

        # Left Side: Bottom
        self.left_side_bottom = [
            (self.window.bottom_left[0] - self.offset,     self.window.bottom_left[1] - self.offset),
            (self.window.bottom_left[0] - self.offset,     self.window.bottom_left[1] - self.offset - self.width),
            (self.window.bottom_left[0] + self.win_width * .25, self.window.bottom_left[1] - self.offset),
            (self.window.bottom_left[0] + self.win_width * .25, self.window.bottom_left[1] - self.offset - self.width)
        ]

        # Right Side: Top
        self.right_side_top = [
            (self.window.top_right[0] - self.win_width * .25, self.window.top_right[1] + self.offset + self.width),
            (self.window.top_right[0] - self.win_width * .25, self.window.top_right[1] + self.offset),
            (self.window.top_right[0] + self.offset,     self.window.top_right[1] + self.offset + self.width),
            (self.window.top_right[0] + self.offset,     self.window.top_right[1] + self.offset)
        ]

        # Right Side: Bottom
        self.right_side_bottom = [
            (self.window.top_right[0] + self.offset,              self.window.top_right[1] + self.offset + self.width),
            (self.window.top_right[0] + self.offset,              self.window.top_right[1] - self.win_height * .25),
            (self.window.top_right[0] + self.offset + self.width, self.window.top_right[1] + self.offset + self.width),
            (self.window.top_right[0] + self.offset + self.width, self.window.top_right[1] - self.win_height * .25)
        ]     

        # Get Window Prefs
        if self.window.window_key == "Main":
            self.bottom_left = self.window.db.prefs.ui.Hops_modal_main_window_bottom_left
            self.scale = self.window.db.prefs.ui.Hops_modal_main_window_scale

        elif self.window.window_key == "Help":
            self.bottom_left = self.window.db.prefs.ui.Hops_modal_help_window_bottom_left
            self.scale = self.window.db.prefs.ui.Hops_modal_help_window_scale

        elif self.window.window_key == "Mods":
            self.bottom_left = self.window.db.prefs.ui.Hops_modal_mods_window_bottom_left
            self.scale = self.window.db.prefs.ui.Hops_modal_mods_window_scale

        elif self.window.window_key == "Kit_Ops":
            self.bottom_left = self.window.db.prefs.ui.Hops_modal_kit_ops_window_bottom_left
            self.scale = self.window.db.prefs.ui.Hops_modal_kit_ops_window_scale
            
        elif self.window.window_key == "Pizza_Ops":
            self.bottom_left = self.window.db.prefs.ui.Hops_modal_pizza_ops_window_bottom_left
            self.scale = self.window.db.prefs.ui.Hops_modal_pizza_ops_window_scale

        elif self.window.window_key == "Brush_Ops":
            self.bottom_left = self.window.db.prefs.ui.Hops_modal_sculpt_ops_window_bottom_left
            self.scale = self.window.db.prefs.ui.Hops_modal_sculpt_ops_window_scale

        self.color = self.window.db.prefs.color.Hops_UI_border_color


    def event_check(self):

        if not self.window.db.ui_event.cell_blocking:
            self.mouse_over_setup()
        self.clamp_ui_location()


    def event(self):

        if self.mouse_over_move:
            self.window.db.ui_event.window_transforming = True
            self.move_win()

        elif self.mouse_over_scale:
            self.window.db.ui_event.window_transforming = True
            self.scale_win()

        if not self.window.db.event.mouse_dragging:
            self.window.db.ui_event.window_transforming = False


    def mouse_over_setup(self):

        # Check mouse over scale gizmo
        vert = is_mouse_in_quad(
            quad=self.right_side_top,
            mouse_pos=self.window.db.event.mouse_pos,
            tolerance=self.offset)

        horiz = is_mouse_in_quad(
            quad=self.right_side_bottom,
            mouse_pos=self.window.db.event.mouse_pos,
            tolerance=self.offset)

        if vert or horiz:
            self.mouse_over_scale = True
        elif not self.window.db.event.mouse_dragging:
            self.mouse_over_scale = False


        # Check mouse over move gizmo
        vert = is_mouse_in_quad(
            quad=self.left_side_top,
            mouse_pos=self.window.db.event.mouse_pos,
            tolerance=self.offset)

        horiz = is_mouse_in_quad(
            quad=self.left_side_bottom,
            mouse_pos=self.window.db.event.mouse_pos,
            tolerance=self.offset)

        if vert or horiz:
            self.mouse_over_move = True
        elif not self.window.db.event.mouse_dragging:
            self.mouse_over_move = False


    def move_win(self):
        '''Moves the window.'''

        if self.window.db.event.mouse_dragging:
            self.bottom_left[0] += self.window.db.event.mouse_frame_diff[0]
            self.bottom_left[1] += self.window.db.event.mouse_frame_diff[1]

            self.clamp_ui_location()
            self.window.setup()


    def scale_win(self):
        '''Scales the window.'''

        if self.window.db.event.mouse_dragging:

            max_size = (0,0)
            if self.window.window_key == "Main":
                max_size = (500 * self.window.db.scale_factor, 350 * self.window.db.scale_factor)

            elif self.window.window_key == "Help":
                max_size = (400 * self.window.db.scale_factor, 700 * self.window.db.scale_factor)

            elif self.window.window_key == "Mods":
                max_size = (400 * self.window.db.scale_factor, 600 * self.window.db.scale_factor)

            elif self.window.window_key == "Kit_Ops":
                max_size = (700 * self.window.db.scale_factor, 700 * self.window.db.scale_factor)

            elif self.window.window_key == "Pizza_Ops":
                max_size = (375 * self.window.db.scale_factor, 500 * self.window.db.scale_factor)

            elif self.window.window_key == "Brush_Ops":
                max_size = (375 * self.window.db.scale_factor, 500 * self.window.db.scale_factor)

            # Scale in X
            if self.scale[0] + self.window.db.event.mouse_frame_diff[0] < max_size[0]:
                self.scale[0] += self.window.db.event.mouse_frame_diff[0]
            
            # Scale in Y
            if self.scale[1] + self.window.db.event.mouse_frame_diff[1] < max_size[1]:
                self.scale[1] += self.window.db.event.mouse_frame_diff[1]

            self.clamp_ui_location()
            self.window.setup()


    def clamp_ui_location(self):

        # Check that the handles around the window dont go past the screen
        if self.scale != None:
            if self.scale[0] + (self.width + self.offset) * 2 > self.window.db.event.screen_width:
                self.scale[0] = self.window.db.event.screen_width - (self.width + self.offset) * 2

            if self.scale[1] + (self.width + self.offset) * 2 > self.window.db.event.screen_height:
                self.scale[1] = self.window.db.event.screen_height - (self.width + self.offset) * 2

        # Left
        if self.bottom_left[0] < self.width + self.offset + self.warp_bounds:
            self.bottom_left[0] = self.width + self.offset + self.warp_bounds

        # Right
        if self.bottom_left[0] + self.win_width + self.width + self.offset > self.window.db.event.screen_width - self.warp_bounds:
            self.bottom_left[0] = self.window.db.event.screen_width - self.win_width - (self.width + self.offset) - self.warp_bounds

        # Top
        if self.bottom_left[1] + self.win_height + self.width + self.offset > self.window.db.event.screen_height - self.warp_bounds:
            self.bottom_left[1] = self.window.db.event.screen_height - self.win_height - (self.width + self.offset) - self.warp_bounds

        # Bottom
        if self.bottom_left[1] - self.width - self.offset < 0 + self.warp_bounds:
            self.bottom_left[1] = self.width + self.offset + self.warp_bounds


    def draw(self):

        # Show Move
        if self.mouse_over_move and self.window.db.ui_event.active_window_key == self.window.window_key:

            # Left side: Top
            render_quad(quad=(self.left_side_top[0], self.left_side_top[1], self.left_side_top[2], self.left_side_top[3]), 
                color=self.color, 
                bevel_corners=False)

            # Left Side: Bottom
            render_quad(quad=(self.left_side_bottom[0], self.left_side_bottom[1], self.left_side_bottom[2], self.left_side_bottom[3]), 
                color=self.color, 
                bevel_corners=False)

        # Show Scale
        elif self.mouse_over_scale and self.window.db.ui_event.active_window_key == self.window.window_key:

            # Right Side: Top
            render_quad(quad=(self.right_side_top[0], self.right_side_top[1], self.right_side_top[2], self.right_side_top[3]), 
                color=self.color, 
                bevel_corners=False)

            # Right Side: Bottom
            render_quad(quad=(self.right_side_bottom[0], self.right_side_bottom[1], self.right_side_bottom[2], self.right_side_bottom[3]), 
                color=self.color, 
                bevel_corners=False)
