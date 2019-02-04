import bpy
from bpy.props import *
from . bool_utils import use_bmesh_boolean, use_carve_boolean, use_carve_mod_boolean, use_bmesh_mod_boolean

#per drawing
from bgl import *
from ... preferences import tool_overlays_enabled, get_hops_preferences_colors_with_transparency, Hops_display_time, Hops_fadeout_time
from ... utils.blender_ui import get_location_in_current_3d_view
from ... overlay_drawer import show_custom_overlay, disable_active_overlays
from ... graphics.drawing2d import set_drawing_dpi, draw_text, draw_box, draw_logo_csharp

class HopsBoolUnion(bpy.types.Operator):
    """Boolean one shape to another """
    bl_idname = "hops.bool_union"
    bl_label = "Hops Union Boolean"
    bl_options = {'REGISTER', 'UNDO'}

    bool_items = [
    ("BMESH", "Bmesh", ""),
    ("CARVE", "Carve", ""),
    ("CARVEMOD", "Carve-mod", ""),
    ("BMESHMOD", "Bmesh-mod", "") ]

    boolean_method = EnumProperty(name = "", default = "CARVEMOD", options = {"SKIP_SAVE"}, items = bool_items)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "boolean_method")

    def invoke(self, context, event):
        self.execute(context)

        object = bpy.context.active_object
        if tool_overlays_enabled():
            disable_active_overlays()
            self.wake_up_overlay = show_custom_overlay(draw,
                parameter_getter = self.parameter_getter,
                location = get_location_in_current_3d_view("CENTER", "BOTTOM", offset = (0, 130)),
                location_type = "CUSTOM",
                stay_time = Hops_display_time(),
                fadeout_time = Hops_fadeout_time())

        return {"FINISHED"}

    def parameter_getter(self):
        return self.boolean_method

    def execute(self, context):
        if self.boolean_method == 'BMESH':
            use_bmesh_boolean(context, 'UNION')
        elif self.boolean_method == 'CARVE':
            use_carve_boolean(context, 'UNION')
        elif self.boolean_method == 'CARVEMOD':
            use_carve_mod_boolean(context, 'UNION')
        elif self.boolean_method == 'BMESHMOD':
            use_bmesh_mod_boolean(context, 'UNION')

        try: self.wake_up_overlay()
        except: pass
        return {'FINISHED'}

# Overlay
###################################################################

def draw(display, parameter_getter):
    boolean_method = parameter_getter()
    scale_factor = 0.9

    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)

    set_drawing_dpi(display.get_dpi() * scale_factor)
    dpi_factor = display.get_dpi_factor() * scale_factor
    line_height = 18 * dpi_factor

    transparency = display.transparency

    color_text1, color_text2, color_border, color_border2 = get_hops_preferences_colors_with_transparency(transparency)
    region_width = bpy.context.region.width


    # Box
    ########################################################

    location = display.location
    x, y = location.x - 60* dpi_factor, location.y - 118* dpi_factor

    draw_box(0, 43 *dpi_factor, region_width, -4 * dpi_factor, color = color_border2)
    draw_box(0, 0, region_width, -82 * dpi_factor, color = color_border)

    draw_logo_csharp(color_border2) #Logo so illa. I love this bitch.


    # Name
    ########################################################
    draw_text("UNION", x - 380 *dpi_factor , y -12*dpi_factor,
              align = "LEFT", size = 20 , color = color_text2)


    # First Coloumn
    ########################################################
    x = x - 160 * dpi_factor
    r = 34 * dpi_factor

    draw_text("TYPE:", x , y,
              align = "LEFT",size = 11, color = color_text2)

    draw_text(boolean_method, x + r, y,
              align = "LEFT",size = 11, color = color_text2)

    glDisable(GL_BLEND)
    glDisable(GL_LINE_SMOOTH)
