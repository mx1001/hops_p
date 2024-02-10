import bpy
import time
from mathutils import Vector
from .fast_ui.main_banner import Fast_UI
from ..addon.utility.screen import dpi_factor
from ..preferences import get_preferences
from ..utility.base_modal_controls import tilde

#from .. utils.blender_ui import get_dpi_factor, get_dpi


'''
Main DB structure for the instance of Master.
'''


class DB():
    '''Database Head'''

    def __init__(self):

        # Window System
        self.windows = {}

        # Prefs
        self.prefs = get_preferences()
        self.scale_factor = dpi_factor(min=.25) * self.prefs.ui.Hops_modal_size
        if bpy.context.preferences.system.pixel_size == 2:
            self.scale_factor *= .75

        # Input Events
        self.event = Input_Event()

        # UI Events
        self.ui_event = UI_Event()

        # Colors
        self.colors = Colors(db=self)

        # Fast UI
        self.fast_ui = Fast_UI(db=self)


    def clear_db(self):
        '''Reset the the DB'''

        self.scale_factor = dpi_factor() * self.prefs.ui.Hops_modal_size

        for key, val in self.windows.items():
            val.clear_layouts()

        self.ui_event.maxed = {}

        self.fast_ui.clear()

        self.drawing_sync = 0


class Input_Event():
    '''Event data nested in Database Head'''

    def __init__(self):

        # Screen
        self.screen_width = 0
        self.screen_height = 0

        # Mouse
        self.mouse_pos = (0, 0)
        self.mouse_frame_diff = (0, 0)
        self.left_clicked = False
        self.right_clicked = False
        self.alt_left_clicked = False
        self.left_click_released = True
        self.mouse_dragging = False
        self.wheel_up = False
        self.wheel_down = False

        # Keys
        self.tab_pressed = False
        self.h_key_pressed = False
        self.m_key_pressed = False
        self.shift_pressed = False
        self.accent_grave_pressed = False 


    def update_events(self, event, context):

        # Screen
        self.screen_width = context.area.width
        self.screen_height = context.area.height

        # Mouse Left Click
        self.left_clicked = True if event.type == 'LEFTMOUSE' and event.value == "PRESS" else False
        self.right_clicked = True if event.type == 'RIGHTMOUSE' and event.value == "PRESS" else False
        self.alt_left_clicked = True if event.type == 'LEFTMOUSE' and event.value == "PRESS" and event.alt == True else False

        # Mouse location Difference
        self.mouse_frame_diff = (event.mouse_region_x - self.mouse_pos[0], event.mouse_region_y - self.mouse_pos[1])

        # Mouse Location
        self.mouse_pos = (event.mouse_region_x, event.mouse_region_y)

        # Mouse Dragging
        if event.type == 'LEFTMOUSE':
            self.left_click_released = True if event.value == "RELEASE" else False
        elif event.type == 'MOUSEMOVE':
            self.mouse_dragging = True if self.left_click_released == False else False

        # Wheel Up
        if event.type == 'WHEELUPMOUSE':
            self.wheel_up = True
        else:
            self.wheel_up = False

        # Wheel Down
        if event.type == 'WHEELDOWNMOUSE':
            self.wheel_down = True
        else:
            self.wheel_down = False

        # Keys
        self.tab_pressed = True if event.type == 'TAB' and event.value == "PRESS" else False
        self.h_key_pressed = True if event.type == 'H' and event.value == "PRESS" else False
        self.m_key_pressed = True if event.type == 'M' and event.value == "PRESS" else False
        self.shift_pressed = True if event.shift == True else False
      #  self.accent_grave_pressed = True if event.type == 'ACCENT_GRAVE' and event.value == "PRESS" else False
        self.accent_grave_pressed = tilde(context, event)


class UI_Event():
    '''Event data for the windows.'''

    def __init__(self):

        # The window the mouse is over
        self.active_window_key = ""

        # The window is being transformed
        self.window_transforming = False

        # The windows are locked by a cell
        self.cell_blocking = False

        # Cell drag event
        self.cell_index = None

        # Fading : The images need to stop trying to render
        self.images_remove = False

        # Min / Max cell heights
        self.min_height = 20
        self.max_height = 30


class Colors():

    def __init__(self, db):

        self.db = db
        self.prefs = self.db.prefs
        self.start_time = 0
        self.fade_out_duration = self.db.prefs.ui.Hops_modal_fade
        self.fade_in_duration = self.db.prefs.ui.Hops_modal_fade_in
        self.fade_in_time_start = time.time()
        self.current_diff = 0

        # States
        self.capture_start_time = True
        # Fading : This is for modal exit
        self.fade_completed = False
        

        self.get_colors()

    # - Setup -
    def get_colors(self):

        # Original
        self.prefs_colors = []
        self.prefs_colors.append(self.prefs.color.Hops_UI_text_color)
        self.prefs_colors.append(self.prefs.color.Hops_UI_secondary_text_color)
        self.prefs_colors.append(self.prefs.color.Hops_UI_highlight_color)
        self.prefs_colors.append(self.prefs.color.Hops_UI_highlight_drag_color)
        self.prefs_colors.append(self.prefs.color.Hops_UI_background_color)
        self.prefs_colors.append(self.prefs.color.Hops_UI_cell_background_color)
        self.prefs_colors.append(self.prefs.color.Hops_UI_dropshadow_color)
        self.prefs_colors.append(self.prefs.color.Hops_UI_border_color)
        self.prefs_colors.append(self.prefs.color.Hops_UI_mouse_over_color)
        self.prefs_colors.append(self.prefs.color.Hops_UI_text_highlight_color)
        self.prefs_colors.append(self.prefs.color.Hops_UI_mods_highlight_color)

        # Cloned
        self.Hops_UI_text_color            = Vector((self.prefs_colors[0][0], self.prefs_colors[0][1], self.prefs_colors[0][2], self.prefs_colors[0][3]))
        self.Hops_UI_secondary_text_color  = Vector((self.prefs_colors[1][0], self.prefs_colors[1][1], self.prefs_colors[1][2], self.prefs_colors[1][3]))
        self.Hops_UI_highlight_color       = Vector((self.prefs_colors[2][0], self.prefs_colors[2][1], self.prefs_colors[2][2], self.prefs_colors[2][3]))
        self.Hops_UI_highlight_drag_color  = Vector((self.prefs_colors[3][0], self.prefs_colors[3][1], self.prefs_colors[3][2], self.prefs_colors[3][3]))
        self.Hops_UI_background_color      = Vector((self.prefs_colors[4][0], self.prefs_colors[4][1], self.prefs_colors[4][2], self.prefs_colors[4][3]))
        self.Hops_UI_cell_background_color = Vector((self.prefs_colors[5][0], self.prefs_colors[5][1], self.prefs_colors[5][2], self.prefs_colors[5][3]))
        self.Hops_UI_dropshadow_color      = Vector((self.prefs_colors[6][0], self.prefs_colors[6][1], self.prefs_colors[6][2], self.prefs_colors[6][3]))
        self.Hops_UI_border_color          = Vector((self.prefs_colors[7][0], self.prefs_colors[7][1], self.prefs_colors[7][2], self.prefs_colors[7][3]))
        self.Hops_UI_mouse_over_color      = Vector((self.prefs_colors[8][0], self.prefs_colors[8][1], self.prefs_colors[8][2], self.prefs_colors[8][3]))
        self.Hops_UI_text_highlight_color  = Vector((self.prefs_colors[9][0], self.prefs_colors[9][1], self.prefs_colors[9][2], self.prefs_colors[9][3]))
        self.Hops_UI_mods_highlight_color  = Vector((self.prefs_colors[10][0], self.prefs_colors[10][1], self.prefs_colors[10][2], self.prefs_colors[10][3]))

    # - Fade out colors -
    def fade_out_colors(self):

        # Capture the start time
        if self.capture_start_time:
            self.capture_start_time = False
            self.start_time = time.time()

        time_diff = (time.time() - self.start_time) *.01
        self.current_diff += time_diff

        if time_diff < self.fade_out_duration:
            self.sub_from_colors(time_diff)

        if self.current_diff >= self.fade_out_duration:
            self.fade_completed = True


    def sub_from_colors(self, time_diff):

        for i in range(len(self.prefs_colors)):
            
            original_alpha = self.prefs_colors[i][3]
            
            if original_alpha <= 0:
                continue

            if i == 0:
                alpha = self.Hops_UI_text_color[3] - ((original_alpha / self.fade_out_duration) * time_diff)
                self.Hops_UI_text_color[3] = alpha
            
            elif i == 1:
                alpha = self.Hops_UI_secondary_text_color[3] - ((original_alpha / self.fade_out_duration) * time_diff)
                self.Hops_UI_secondary_text_color[3] = alpha

            elif i == 2:
                alpha = self.Hops_UI_highlight_color[3] - ((original_alpha / self.fade_out_duration) * time_diff)
                self.Hops_UI_highlight_color[3] = alpha

            elif i == 3:
                alpha = self.Hops_UI_highlight_drag_color[3] - ((original_alpha / self.fade_out_duration) * time_diff)
                self.Hops_UI_highlight_drag_color[3] = alpha

            elif i == 4:
                alpha = self.Hops_UI_background_color[3] - ((original_alpha / self.fade_out_duration) * time_diff)
                self.Hops_UI_background_color[3] = alpha

            elif i == 5:
                alpha = self.Hops_UI_cell_background_color[3] - ((original_alpha / self.fade_out_duration) * time_diff)
                self.Hops_UI_cell_background_color[3] = alpha

            elif i == 6:
                alpha = self.Hops_UI_dropshadow_color[3] - ((original_alpha / self.fade_out_duration) * time_diff)
                self.Hops_UI_dropshadow_color[3] = alpha

            elif i == 7:
                alpha = self.Hops_UI_border_color[3] - ((original_alpha / self.fade_out_duration) * time_diff)
                self.Hops_UI_border_color[3] = alpha

            elif i == 8:
                alpha = self.Hops_UI_mouse_over_color[3] - ((original_alpha / self.fade_out_duration) * time_diff)
                self.Hops_UI_mouse_over_color[3] = alpha

            elif i == 9:
                alpha = self.Hops_UI_text_highlight_color[3] - ((original_alpha / self.fade_out_duration) * time_diff)
                self.Hops_UI_text_highlight_color[3] = alpha

            elif i == 10:
                alpha = self.Hops_UI_mods_highlight_color[3] - ((original_alpha / self.fade_out_duration) * time_diff)
                self.Hops_UI_mods_highlight_color[3] = alpha

    # - Fade in colors -
    def fade_in_colors(self):

        # Capture the start time
        if self.capture_start_time:
            self.set_colors_alpha_to_zero()
            self.capture_start_time = False
            self.start_time = time.time()

        time_diff = ((time.time() - self.start_time) *.01 / self.fade_in_duration)

        return self.add_alpha_to_colors(time_diff)


    def set_colors_alpha_to_zero(self):

        self.Hops_UI_text_color[3] = 0
        self.Hops_UI_secondary_text_color[3] = 0
        self.Hops_UI_highlight_color[3] = 0
        self.Hops_UI_highlight_drag_color[3] = 0
        self.Hops_UI_background_color[3] = 0
        self.Hops_UI_cell_background_color[3] = 0
        self.Hops_UI_dropshadow_color[3] = 0
        self.Hops_UI_border_color[3] = 0
        self.Hops_UI_mouse_over_color[3] = 0
        self.Hops_UI_text_highlight_color[3] = 0
        self.Hops_UI_mods_highlight_color[3] = 0


    def add_alpha_to_colors(self, time_diff):

        completed = True

        for i in range(len(self.prefs_colors)):

            if i == 0:
                if self.Hops_UI_text_color[3] + time_diff >= self.prefs_colors[i][3]:
                    self.Hops_UI_text_color[3] = self.prefs_colors[i][3]
                else:
                    self.Hops_UI_text_color[3] += time_diff
                    completed = False

            elif i == 1:
                if self.Hops_UI_secondary_text_color[3] + time_diff >= self.prefs_colors[i][3]:
                    self.Hops_UI_secondary_text_color[3] = self.prefs_colors[i][3]
                else:
                    self.Hops_UI_secondary_text_color[3] += time_diff
                    completed = False

            elif i == 2:
                if self.Hops_UI_highlight_color[3] + time_diff >= self.prefs_colors[i][3]:
                    self.Hops_UI_highlight_color[3] = self.prefs_colors[i][3]
                else:
                    self.Hops_UI_highlight_color[3] += time_diff
                    completed = False

            elif i == 3:
                if self.Hops_UI_highlight_drag_color[3] + time_diff >= self.prefs_colors[i][3]:
                    self.Hops_UI_highlight_drag_color[3] = self.prefs_colors[i][3]
                else:
                    self.Hops_UI_highlight_drag_color[3] += time_diff
                    completed = False

            elif i == 4:
                if self.Hops_UI_background_color[3] + time_diff >= self.prefs_colors[i][3]:
                    self.Hops_UI_background_color[3] = self.prefs_colors[i][3]
                else:
                    self.Hops_UI_background_color[3] += time_diff
                    completed = False

            elif i == 5:
                if self.Hops_UI_cell_background_color[3] + time_diff >= self.prefs_colors[i][3]:
                    self.Hops_UI_cell_background_color[3] = self.prefs_colors[i][3]
                else:
                    self.Hops_UI_cell_background_color[3] += time_diff
                    completed = False

            elif i == 6:
                if self.Hops_UI_dropshadow_color[3] + time_diff >= self.prefs_colors[i][3]:
                    self.Hops_UI_dropshadow_color[3] = self.prefs_colors[i][3]
                else:
                    self.Hops_UI_dropshadow_color[3] += time_diff
                    completed = False

            elif i == 7:
                if self.Hops_UI_border_color[3] + time_diff >= self.prefs_colors[i][3]:
                    self.Hops_UI_border_color[3] = self.prefs_colors[i][3]
                else:
                    self.Hops_UI_border_color[3] += time_diff
                    completed = False

            elif i == 8:
                if self.Hops_UI_mouse_over_color[3] + time_diff >= self.prefs_colors[i][3]:
                    self.Hops_UI_mouse_over_color[3] = self.prefs_colors[i][3]
                else:
                    self.Hops_UI_mouse_over_color[3] += time_diff
                    completed = False

            elif i == 9:
                if self.Hops_UI_text_highlight_color[3] + time_diff >= self.prefs_colors[i][3]:
                    self.Hops_UI_text_highlight_color[3] = self.prefs_colors[i][3]
                else:
                    self.Hops_UI_text_highlight_color[3] += time_diff
                    completed = False

            elif i == 10:
                if self.Hops_UI_mods_highlight_color[3] + time_diff >= self.prefs_colors[i][3]:
                    self.Hops_UI_mods_highlight_color[3] = self.prefs_colors[i][3]
                else:
                    self.Hops_UI_mods_highlight_color[3] += time_diff
                    completed = False

        return completed


    def check_color_changes(self):
        '''Check if the RBG values have changed while the modal was running.'''

        if self.prefs_colors != []:

            copy_colors = [
                self.Hops_UI_text_color,
                self.Hops_UI_secondary_text_color,
                self.Hops_UI_highlight_color,
                self.Hops_UI_highlight_drag_color,
                self.Hops_UI_background_color,
                self.Hops_UI_cell_background_color,
                self.Hops_UI_dropshadow_color,
                self.Hops_UI_border_color,
                self.Hops_UI_mouse_over_color,
                self.Hops_UI_text_highlight_color,
                self.Hops_UI_mods_highlight_color]

            zipped_colors = zip(self.prefs_colors, copy_colors)
            rgb_changed = False

            for color in zipped_colors:
                for i in range(4):

                    if color[0][i] != color[1][i]:
                        rgb_changed = True

            if rgb_changed:

                self.get_colors()
