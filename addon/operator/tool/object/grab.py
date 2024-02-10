import bpy
import gpu
from bgl import *
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from math import cos, sin, pi

from .. shader import grab
from .. dots import update
from .... utility import addon, view3d, screen
from ..... utils.blender_ui import get_dpi_factor


class HOPS_OT_dots_grab(bpy.types.Operator):
    bl_idname = "hops.dots_grab"
    bl_label = "Adjust Hopstool Dots"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR"}
    bl_description = """Adjust Hopstool Dots"""

    def invoke(self, context, event):
        self.mouse = event.mouse_region_x, event.mouse_region_y
        grab.handler = bpy.types.SpaceView3D.draw_handler_add(grab, (self, context), "WINDOW", "POST_PIXEL")

        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):

        self.mouse = addon.preference().property.dots_x, addon.preference().property.dots_y = event.mouse_region_x, event.mouse_region_y

        context.area.header_text_set("Dots Grab")

        if event.type == 'LEFTMOUSE':
            if event.value == 'RELEASE':
                context.area.header_text_set(text=None)
                grab.remove(self)
                return {'FINISHED'}

        if event.type in ("ESC", "RIGHTMOUSE"):
            context.area.header_text_set(text=None)
            grab.remove(self)
            return {'CANCELLED'}

        context.area.tag_redraw()
        return {'RUNNING_MODAL'}
