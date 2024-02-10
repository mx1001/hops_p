import bpy
import pathlib
from ... addon.utility.screen import dpi_factor
from ... ui_framework.graphics.draw import render_quad, render_geo, render_text, draw_border_lines
from ... ui_framework.operator_ui import Master
from ... ui_framework.utils.geo import get_blf_text_dims
from ... utils.toggle_view3d_panels import collapse_3D_view_panels
from ... utils.addons import addon_exists
from ... addon.utility import method_handler
from ... utility import addon
from ... preferences import get_preferences

# Save system
invalid = {'\\', '/', ':', '*', '?', '"', '<', '>', '|', '.'}
completed = {'LEFTMOUSE', 'RET', 'NUMPAD_ENTER'}
cancel = {'RIGHTMOUSE', 'ESC'}


class HOPS_OT_PowerSave_Dialog(bpy.types.Operator):

    """Open a dialog that lets you choose a file name to save as"""
    bl_idname = "hops.power_save_dialog"
    bl_label = "PowerSave Dialog"
    bl_options = {"REGISTER", "UNDO"}


    def invoke(self, context, event):

        # Editor Props
        self.file_name = None
        self.input_complete = False
        self.cancelled = False

        # Shader Props
        self.shader_file_name = ""
        self.shader_help_text = "PowerSave: Type file name or hit return for auto naming."
        self.screen_width = context.area.width
        self.screen_height = context.area.height

        self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.safe_draw_file_name, (context,), 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


    def modal(self, context, event):

        self.save_system(context, event)

        if self.cancelled == True:
            self.cancled_ui()
            self.remove_file_name_shader()
            context.area.tag_redraw()
            return {'FINISHED'}

        if self.input_complete:

            # PowerSave
            if addon_exists("PowerSave"):
                # Refresh first
                from PowerSave.addon.utils import common
                common.update_powersave_name()
                # Call operator
                from PowerSave.addon.utils.common import prefs
                prefs = prefs()
                if self.file_name == None:
                    self.file_name = ""
                prefs.powersave_name = self.file_name
                bpy.ops.powersave.powersave('INVOKE_DEFAULT')
                self.launch_power_save_ui()

            self.remove_file_name_shader()
            context.area.tag_redraw()
            return {'FINISHED'}

        context.area.tag_redraw()
        return {'RUNNING_MODAL'}


    def save_system(self, context, event):
        '''Freeze the modal and take input.'''

        # Canceled
        if event.type in cancel and event.value == 'PRESS':
            self.cancelled = True
            return

        # Finished
        if event.type in completed and event.value == 'PRESS':
            self.input_complete = True

        # Append
        elif event.ascii not in invalid and event.value == 'PRESS':
            if self.file_name == None:
                self.file_name = ""
            self.file_name += event.ascii

        # Backspace
        if event.type == 'BACK_SPACE' and event.value == 'PRESS':
            if self.file_name != "" or self.file_name != None:
                self.file_name = self.file_name[:len(self.file_name)-1]
            elif self.file_name == None:
                self.file_name = ""
                self.shader_file_name = ""

        # Set text to draw
        if self.file_name == None:
            self.shader_file_name = "Auto"
        else:
           self.shader_file_name = self.file_name


    def safe_draw_file_name(self, context):
        method_handler(self.draw_file_name_shader,
            arguments = (context,),
            identifier = 'UI Framework',
            exit_method = self.remove_file_name_shader)


    def remove_file_name_shader(self):
        '''Remove shader handle.'''

        if self.draw_handle:
            self.draw_handle = bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle, "WINDOW")
            self.draw_handle = None


    def draw_file_name_shader(self, context):
        '''Draw shader handle.'''

        factor = dpi_factor()

        help_text_size = 18
        file_text_size = 24

        sample_y = get_blf_text_dims("XyZ`Qq", file_text_size)[1]
        help_text_dims = get_blf_text_dims(self.shader_help_text, help_text_size)
        file_text_dims = get_blf_text_dims(self.shader_file_name, file_text_size)

        center_x = self.screen_width * .5
        center_y = self.screen_height * .5

        text_padding_y = 30 * factor
        text_padding_x = 20 * factor

        total_height = text_padding_y * 3 + sample_y + sample_y
        widest_text = help_text_dims[0] if help_text_dims[0] > file_text_dims[0] else file_text_dims[0]
        total_width = text_padding_x * 2 + widest_text

        # TL, BL, TR, BR
        verts = [
            (center_x - total_width * .5, center_y + total_height * .5),
            (center_x - total_width * .5, center_y - total_height * .5),
            (center_x + total_width * .5, center_y + total_height * .5),
            (center_x + total_width * .5, center_y - total_height * .5)]

        render_quad(
            quad=verts,
            color=(0,0,0,.5))

        draw_border_lines(
            vertices=verts,
            width=2,
            color=(0,0,0,.75))

        x_loc = center_x - help_text_dims[0] * .5
        y_loc = center_y - help_text_dims[1] * .5 + file_text_size * factor
        render_text(
            text=self.shader_help_text, 
            position=(x_loc, y_loc), 
            size=help_text_size, 
            color=(1,1,1,1))

        x_loc = center_x - file_text_dims[0] * .5
        y_loc = center_y - file_text_dims[1] * .5 - file_text_size * factor
        render_text(
            text=self.shader_file_name, 
            position=(x_loc, y_loc), 
            size=file_text_size, 
            color=(1,1,1,1))


    def launch_power_save_ui(self):
        '''Launch the PowerSave UI dialog.'''

        path = pathlib.Path(bpy.data.filepath).resolve()
        folder, name = str(path.parent), path.stem

        ui = Master()
        draw_data = [
            ["PowerSave"],
            [folder, " "],
            [name, " "],
            ["Now saving ... ", " "]
        ]
        ui.receive_draw_data(draw_data=draw_data)
        ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)


    def cancled_ui(self):
        '''Launch the PowerSave UI dialog.'''

        ui = Master()
        draw_data = [["Cancelled Operation"]]
        ui.receive_draw_data(draw_data=draw_data)
        ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)
