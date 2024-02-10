import bpy
from .. graphics.drawing2d import set_drawing_dpi
from .. utils.blender_ui import get_dpi, get_dpi_factor
from .. graphics.logo import draw_logo_hops
from .. preferences import get_preferences


def draw_hud():
    set_drawing_dpi(get_dpi())
    dpi_factor = get_dpi_factor()

    if get_preferences().color.Hops_display_logo:
        draw_logo_hops()


# Register
################################################################################

draw_handler = None


def register():
    global draw_handler
    draw_handler = bpy.types.SpaceView3D.draw_handler_add(draw_hud, tuple(), "WINDOW", "POST_PIXEL")


def unregister():
    global draw_handler
    bpy.types.SpaceView3D.draw_handler_remove(draw_handler, "WINDOW")
    draw_handler = None
