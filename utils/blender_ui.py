import bpy
import textwrap
from mathutils import Vector


def get_dpi_factor(force=True):
    return get_dpi(force=force) / 72


def get_dpi(force=True):
    preference = bpy.context.preferences.addons[__name__.partition('.')[0]].preferences
    if preference.ui.use_dpi_factoring or force:
        systemPreferences = bpy.context.preferences.system
        retinaFactor = getattr(systemPreferences, "pixel_size", 1)
        return int(systemPreferences.dpi * retinaFactor)
    else:
        return 72


def open_error_message(message = "", title = "Error", icon = "ERROR"):
    def draw_error_message(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw_error_message, title = title, icon = icon)


def get_location_in_current_3d_view(horizontal = "CENTER", vertical = "CENTER", offset = (0, 0), adapt_offset_to_dpi = True):
    area = bpy.context.area
    if area.type == "VIEW_3D":
        for region in area.regions:
            if region.type == "WINDOW":
                return get_location_in_region(region, horizontal, vertical, offset, adapt_offset_to_dpi)
    return Vector((0, 0))


def get_location_in_region(region, horizontal = "CENTER", vertical = "CENTER", offset = (0, 0), adapt_offset_to_dpi = True):
    if horizontal == "LEFT": x = 0
    elif horizontal == "CENTER": x = region.width / 2
    elif horizontal == "RIGHT": x = region.width
    else: raise Exception("'{}' is not in ('LEFT', 'CENTER', 'RIGHT')".format(horizontal))

    if vertical == "TOP": y = region.height
    elif vertical == "CENTER": y = region.height / 2
    elif vertical == "BOTTOM": y = 0
    else: raise Exception("'{}' is not in ('TOP', 'CENTER', 'BOTTOM')".format(vertical))

    offset = Vector(offset)
    if adapt_offset_to_dpi: offset *= get_dpi_factor()
    return Vector((x, y)) + offset


def get_3d_view_tools_panel_overlay_width(area, placement):
    use_region_overlap = bpy.context.preferences.system.use_region_overlap

    n = 0
    t = 0

    if placement == "left":
        if use_region_overlap:
            for region in area.regions:
                if region.type == "UI":
                    if region.x < bpy.context.region.width/3:
                        n = region.width
                if region.type == "TOOLS":
                    if region.x < bpy.context.region.width/3:
                        t = region.width

    if placement == "right":
        if use_region_overlap:
            for region in area.regions:
                if region.type == "UI":
                    if region.x > bpy.context.region.width/3:
                        n = region.width
                if region.type == "TOOLS":
                    if region.x > bpy.context.region.width/3:
                        t = region.width

    return n + t


def write_text(layout, text, width = 30, icon = "NONE"):
    col = layout.column(align = True)
    col.scale_y = 0.85
    prefix = " "
    for paragraph in text.split("\n"):
        for line in textwrap.wrap(paragraph, width):
            col.label(text=prefix + line, icon = icon)
            if icon != "NONE": prefix = "     "
            icon = "NONE"

mouse_position = Vector((0, 0))


def get_mouse_position_in_current_region():
    bpy.ops.hops.store_mouse_position("INVOKE_DEFAULT")
    return mouse_position.copy()


class HOPS_OT_StoreMousePosition(bpy.types.Operator):
    bl_idname = "hops.store_mouse_position"
    bl_label = "Store Mouse Position"
    bl_options = {"REGISTER", "INTERNAL"}

    def invoke(self, context, event):
        mouse_position.x = event.mouse_region_x
        mouse_position.y = event.mouse_region_y
        return {"FINISHED"}
