import bpy
import blf
import bgl
import time
from bpy.props import *
from mathutils import Vector
from collections import defaultdict
from bpy.app.handlers import persistent
from . utils.blender_ui import get_dpi, get_dpi_factor, get_mouse_position_in_current_region

'''
Only these functions should be called from the outside:

    show_custom_overlay: Here you can give a specialised draw function as
        parameter to draw very specific overlays.

    show_text_overlay: This is a special form of the show_custom_overlay function
        that allows you to quickly draw simple texts without having to write a
        draw function yourself.

    disable_active_overlays: Removes all overlays so that they don't overlap.
'''

draw_handler_by_space = {}
overlay_draw_handlers = {}

def disable_active_overlays():
    overlay_draw_handlers.clear()

def show_text_overlay(text, stay_time = 2, fadeout_time = 1,
                      location_type = "MOUSE", location = (0, 0),
                      font_size = 12, color = (1, 1, 1)):
    return show_custom_overlay(draw_text_message,
                stay_time, fadeout_time, location_type, location, text = text,
                font_size = font_size, color = color)

def show_custom_overlay(function, stay_time = 2, fadeout_time = 1,
                        location_type = "MOUSE", location = (0, 0),
                        *args, **kwargs):
    if location_type == "MOUSE":
        location = get_mouse_position_in_current_region()

    area = bpy.context.area
    display = OverlayDisplayData(stay_time = stay_time, fadeout_time = fadeout_time,
                location = location, area = area, area_type = area.type)

    current_draw_function = assign_arguments(function, *args, **kwargs)
    overlay_draw_handlers[display] = current_draw_function

    return display.wake_up

def assign_arguments(function, *args, **kwargs):
    def wrapper(display):
        try:
            return function(display, *args, **kwargs)
        except ReferenceError as e:
            display.tag_close()
            print(e)
    return wrapper


class OverlayDisplayData:
    def __init__(self, stay_time, fadeout_time, location, area, area_type):
        self.wake_up()
        self.stay_time = stay_time
        self.location = location
        self.fadeout_time = max(fadeout_time, 0.001) # avoid division by zero
        self.sleep_time = 30 # time until the message is removed
        self.area = area
        self.area_type = area_type
        self.transparency = 0.0

    def wake_up(self):
        self.start_time = time.clock()

    def tag_close(self):
        self.start_time = -1000 # some large negative number

    @property
    def disabled(self):
        return time.clock() > sum((self.start_time, self.stay_time, self.fadeout_time, self.sleep_time))

    @property
    def invisible(self):
        return self.transparency <= 0

    def update_transparency(self):
        old = self.transparency
        self.transparency = max(0, 1 - max(0, (time.clock() - self.start_time - self.stay_time) / self.fadeout_time)) ** 1.5
        return self.transparency - old

    def get_dpi_factor(self):
        return get_dpi_factor()

    def get_dpi(self):
        return get_dpi()


def draw_text_message(display, text, font_size, color):
    font = 0
    location = display.location

    blf.size(font, font_size, display.get_dpi())

    finalColor = list(color) + [display.transparency]
    bgl.glColor4f(*finalColor)

    line_height = font_size * 1.3 * display.get_dpi_factor()
    for i, line in enumerate(text.split("\n")):
        y = display.location.y - i * line_height
        blf.position(font, location.x, y, 0)
        blf.draw(font, line)


@persistent
def update_drawing(scene):
    old_overlays = []
    for display in overlay_draw_handlers.keys():
        change = display.update_transparency()
        if display.disabled:
            old_overlays.append(display)
        elif abs(change) > 0:
            display.area.tag_redraw()

    for display in old_overlays:
        del overlay_draw_handlers[display]


def draw_overlay():
    # Draw all overlays in current area
    area = bpy.context.area
    for display, drawer in overlay_draw_handlers.items():
        if area == display.area and area.type == display.area.type:
            drawer(display)


def register_callbacks():
    space_type_names = [
        "ClipEditor", "Console", "DopeSheetEditor", "FileBrowser", "GraphEditor",
        "ImageEditor", "Info", "LogicEditor", "NLA", "NodeEditor", "Outliner",
        "Properties", "SequenceEditor", "TextEditor", "Timeline", "UserPreferences", "View3D"]

    space_types = [getattr(bpy.types, "Space" + name) for name in space_type_names]

    for space in space_types:
        draw_handler = space.draw_handler_add(draw_overlay, tuple(), "WINDOW", "POST_PIXEL")
        draw_handler_by_space[space] = draw_handler
    bpy.app.handlers.scene_update_post.append(update_drawing)

def unregister_callbacks():
    for space, draw_handler in draw_handler_by_space.items():
        space.draw_handler_remove(draw_handler, "WINDOW")
    bpy.app.handlers.scene_update_post.remove(update_drawing)
