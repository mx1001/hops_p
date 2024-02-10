import bpy
from ..addon.utility.screen import dpi_factor
from ..preferences import get_preferences


def get_screen_warp_padding():
    '''The padding around the modal frame.'''

    tolerance = get_preferences().ui.Hops_warp_mode_padding
    return int(tolerance * dpi_factor())


def mouse_warp(context: bpy.context, event: bpy.types.Event):
    '''Warp the mouse in the screen region.'''

    if get_preferences().ui.Hops_warp_on == False:
        return

    mouse_warped = False

    mouse_pos = (event.mouse_region_x, event.mouse_region_y)
    x_pos = mouse_pos[0]
    y_pos = mouse_pos[1]
    tolerance = get_screen_warp_padding()

    # X Warp
    if mouse_pos[0] + tolerance > context.area.width:
        x_pos = tolerance + 5
    elif mouse_pos[0] - tolerance < 0:
        x_pos = context.area.width - (tolerance + 5)

    # Y Warp
    if mouse_pos[1] + tolerance > context.area.height:
        y_pos = tolerance + 5
    elif mouse_pos[1] - tolerance < 0:
        y_pos = context.area.height - (tolerance + 5)

    if x_pos != mouse_pos[0] or y_pos != mouse_pos[1]:
        x_pos += context.area.x
        y_pos += context.area.y
        context.window.cursor_warp(x_pos, y_pos)
        mouse_warped = True
        
    return mouse_warped