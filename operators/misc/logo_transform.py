import bpy, math
from enum import Enum
from ... preferences import get_preferences
from ... utility.base_modal_controls import Base_Modal_Controls
from ... ui_framework.master import Master
from ... utils.toggle_view3d_panels import collapse_3D_view_panels
from ... addon.utility import method_handler
from ... arcade.engine.drawing import draw_2D_geo, draw_2D_lines
from ... addon.utility.screen import dpi_factor


class Edit_Mode(Enum):

    Move = 1
    Scale = 2
    Color = 3
    Alpha = 4


class HOPS_OT_AdjustLogo(bpy.types.Operator):
    bl_idname = "hops.adjust_logo"
    bl_label = "Adjust Hardops Logo"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}
    bl_description = """Adjust Logo"""

    def invoke(self, context, event):

        # Setup
        get_preferences().color.Hops_display_logo = True
        self.edit_mode = Edit_Mode.Move
        self.screen_width = context.area.width
        self.screen_height = context.area.height
        self.alpha = get_preferences().color.Hops_logo_color[3]
        self.color_dot_radius = 20 * dpi_factor()

        # Base Systems
        self.master = Master(context=context)
        self.master.only_use_fast_ui = True
        self.base_controls = Base_Modal_Controls(context, event)
        self.original_tool_shelf, self.original_n_panel = collapse_3D_view_panels()
        self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.safe_draw_shader, (context,), 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):

        # Base Systems
        self.master.receive_event(event=event)
        self.base_controls.update(context, event)

        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        if self.base_controls.cancel:
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            return {'CANCELLED'}

        if self.base_controls.confirm:
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            return {'FINISHED'}

        elif event.type == 'G':
            self.edit_mode = Edit_Mode.Move

        elif event.type == 'S':
            self.edit_mode = Edit_Mode.Scale

        elif event.type == 'C':
            self.edit_mode = Edit_Mode.Color

        elif event.type == 'A':
            self.edit_mode = Edit_Mode.Alpha

        elif event.type == 'W':
            get_preferences().color.Hops_logo_color[0] = 1
            get_preferences().color.Hops_logo_color[1] = 1
            get_preferences().color.Hops_logo_color[2] = 1

        elif event.type == 'X' and event.value == "PRESS":
            get_preferences().color.Hops_display_logo = not get_preferences().color.Hops_display_logo
        
        elif event.type == 'MOUSEMOVE':
            if self.edit_mode == Edit_Mode.Move:
                get_preferences().color.Hops_logo_x_position = event.mouse_x - self.screen_width
                get_preferences().color.Hops_logo_y_position = event.mouse_y - self.screen_height

            elif self.edit_mode == Edit_Mode.Scale:
                get_preferences().color.Hops_logo_size += (event.mouse_x - event.mouse_prev_x) * .25
                if get_preferences().color.Hops_logo_size < 1:
                    get_preferences().color.Hops_logo_size = 1

            elif self.edit_mode == Edit_Mode.Color:
                '''
                Ranges
                    RED   : 0 = screen_height * .25   <-||->   1 = screen_height * .75
                    GREEN : 0 = screen_width  * .75   <-||->   1 = screen_width  * .25
                    BLUE  : 0 = screen_width  * .25   <-||->   1 = screen_width  * .75
                '''
                # Clamp -> max(min(my_value, max_value), min_value)

                red = max(min(event.mouse_y, self.screen_height * .75), self.screen_height * .25)
                red /= self.screen_height * .5
                red -= .5

                green = max(min(self.screen_width - event.mouse_x, self.screen_width * .75), self.screen_width * .25)
                green /= self.screen_width * .5
                green -= .5

                blue = max(min(event.mouse_x, self.screen_width * .75), self.screen_width * .25)
                blue /= self.screen_width * .5
                blue -= .5

                get_preferences().color.Hops_logo_color = (red, green, blue, self.alpha)
                self.check_mouse_over_dot(event)

            elif self.edit_mode == Edit_Mode.Alpha:
                self.alpha += (event.mouse_x - event.mouse_prev_x) * .015625
                self.alpha = max(min(self.alpha, 1), .0625)
                get_preferences().color.Hops_logo_color[3] = self.alpha

        elif event.type == 'WHEELDOWNMOUSE':
            get_preferences().color.Hops_logo_size -= 1

        elif event.type == 'WHEELUPMOUSE':
            get_preferences().color.Hops_logo_size += 1

        self.draw_master(context=context)
        context.area.tag_redraw()
        return {"RUNNING_MODAL"}


    def draw_master(self, context):

        # Start
        self.master.setup()
        if self.master.should_build_fast_ui():
            win_list = []
            help_list = []
            mods_list = []

            # Main
            win_list.append(self.edit_mode.name)
            if self.edit_mode == Edit_Mode.Move:
                win_list.append(f'X: {get_preferences().color.Hops_logo_x_position:.1f}')
                win_list.append(f'Y: {get_preferences().color.Hops_logo_y_position:.1f}')
            elif self.edit_mode == Edit_Mode.Scale:
                win_list.append(f'Scale: {get_preferences().color.Hops_logo_size:.1f}')
            elif self.edit_mode == Edit_Mode.Color:
                r = f'{get_preferences().color.Hops_logo_color[0]:.2f}'
                g = f'{get_preferences().color.Hops_logo_color[1]:.2f}'
                b = f'{get_preferences().color.Hops_logo_color[2]:.2f}'
                win_list.append(f'Color: {r}  {g}  {b}')
            elif self.edit_mode == Edit_Mode.Alpha:
                win_list.append(f'Alpha: {self.alpha:.3f}')

            # Help
            help_list.append(["G",      "Edit Location"])
            help_list.append(["S",      "Edit Scale"])
            help_list.append(["C",      "Edit Color"])
            help_list.append(["A",      "Edit Alpha"])
            help_list.append(["W",      "Set White"])
            help_list.append(["B",      "Set Black"])
            help_list.append(["X",      "Toggle On / Off"])
            help_list.append(["Scroll", "Adjust Scale"])

            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="logo_gray")
        self.master.finished()


    def check_mouse_over_dot(self, event):
        '''Assign a direct color to the logo if mouse over a dot.'''

        mouse_pos = (event.mouse_region_x, event.mouse_region_y)

        red_loc = (self.screen_width * .5, self.screen_height * .75)
        green_loc = (self.screen_width * .25, self.screen_height * .25)
        blue_loc = (self.screen_width * .75, self.screen_height * .25)

        # Check Red
        if mouse_pos[0] <= red_loc[0] + self.color_dot_radius:
            if mouse_pos[0] >= red_loc[0] - self.color_dot_radius:
                if mouse_pos[1] <= red_loc[1] + self.color_dot_radius:
                    if mouse_pos[1] >= red_loc[1] - self.color_dot_radius:
                        get_preferences().color.Hops_logo_color[0] = 1
                        get_preferences().color.Hops_logo_color[1] = 0
                        get_preferences().color.Hops_logo_color[2] = 0
                        return

        # Check Green
        if mouse_pos[0] <= green_loc[0] + self.color_dot_radius:
            if mouse_pos[0] >= green_loc[0] - self.color_dot_radius:
                if mouse_pos[1] <= green_loc[1]:
                    if mouse_pos[1] >= green_loc[1] - self.color_dot_radius * 2:
                        get_preferences().color.Hops_logo_color[0] = 0
                        get_preferences().color.Hops_logo_color[1] = 1
                        get_preferences().color.Hops_logo_color[2] = 0
                        return

        # Check Blue
        if mouse_pos[0] <= blue_loc[0] + self.color_dot_radius:
            if mouse_pos[0] >= blue_loc[0] - self.color_dot_radius:
                if mouse_pos[1] <= blue_loc[1]:
                    if mouse_pos[1] >= blue_loc[1] - self.color_dot_radius * 2:
                        get_preferences().color.Hops_logo_color[0] = 0
                        get_preferences().color.Hops_logo_color[1] = 0
                        get_preferences().color.Hops_logo_color[2] = 1
                        return
    ####################################################
    #   SHADERS
    ####################################################

    def safe_draw_shader(self, context):
        method_handler(self.draw_shader,
            arguments = (context,),
            identifier = 'Logo Adjust',
            exit_method = self.remove_shader)


    def remove_shader(self):
        '''Remove shader handle.'''

        if self.draw_handle:
            self.draw_handle = bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle, "WINDOW")


    def draw_shader(self, context):
        '''Draw shader handle.'''

        if self.edit_mode == Edit_Mode.Color:
            segments = 20
            self.draw_red_circle(segments, self.screen_width, self.screen_height)
            self.draw_green_circle(segments, self.screen_width, self.screen_height)
            self.draw_blue_circle(segments, self.screen_width, self.screen_height)


    def draw_red_circle(self, segments=3, screen_width=0, screen_height=0):
        '''Draw the red circle : Top'''

        vertices = []
        for i in range(segments):
            index = i + 1
            angle = i * 3.14159 * 2 / segments
            x = math.cos(angle) * self.color_dot_radius
            y = math.sin(angle) * self.color_dot_radius

            x += screen_width * .5
            y += screen_height * .75

            vertices.append((x, y))

        first_vert = vertices[0]
        vertices.append(first_vert)

        # Polygon
        indices = []
        for i in range(len(vertices)):
            if i == len(vertices) - 2:
                break
            indices.append((0, i, i+1))

        # Draw
        draw_2D_geo(vertices, indices, color=(1,0,0,.75))
        draw_2D_lines(vertices, width=3, color=(1,0,0,1))


    def draw_green_circle(self, segments=3, screen_width=0, screen_height=0):
        '''Draw the green circle : Left'''
        
        vertices = []
        for i in range(segments):
            index = i + 1
            angle = i * 3.14159 * 2 / segments
            x = math.cos(angle) * self.color_dot_radius
            y = math.sin(angle) * self.color_dot_radius

            x += screen_width * .25
            y += screen_height * .25
            y -= self.color_dot_radius

            vertices.append((x, y))

        first_vert = vertices[0]
        vertices.append(first_vert)

        # Polygon
        indices = []
        for i in range(len(vertices)):
            if i == len(vertices) - 2:
                break
            indices.append((0, i, i+1))

        # Draw
        draw_2D_geo(vertices, indices, color=(0,1,0,.75))
        draw_2D_lines(vertices, width=3, color=(0,1,0,1))


    def draw_blue_circle(self, segments=3, screen_width=0, screen_height=0):
        '''Draw the blue circle : Right'''
        
        vertices = []
        for i in range(segments):
            index = i + 1
            angle = i * 3.14159 * 2 / segments
            x = math.cos(angle) * self.color_dot_radius
            y = math.sin(angle) * self.color_dot_radius

            x += screen_width * .75
            y += screen_height * .25
            y -= self.color_dot_radius

            vertices.append((x, y))

        first_vert = vertices[0]
        vertices.append(first_vert)

        # Polygon
        indices = []
        for i in range(len(vertices)):
            if i == len(vertices) - 2:
                break
            indices.append((0, i, i+1))

        # Draw
        draw_2D_geo(vertices, indices, color=(0,0,1,.75))
        draw_2D_lines(vertices, width=3, color=(0,0,1,1))