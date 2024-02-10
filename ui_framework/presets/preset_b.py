import bpy
from ..graphics.load import load_image_file


class Preset_B():

    def __init__(self, create):

        self.create = create
        self.db = self.create.db
        self.images = []

        # Main Window
        self.main_window = None

        # Help Window
        self.help_window = None

        # Mods Window
        self.mod_window = None

        self.setup()


    def setup(self):

        # Load Images
        self.images.append(load_image_file(filename="logo_red"))
        self.images.append(load_image_file(filename="logo_orange"))
        self.images.append(load_image_file(filename="logo_blue"))

        # Create windows
        self.main_window = self.create.window(window_key="Main")
        self.main_window_layout()

        self.help_window = self.create.window(window_key="Help")
        self.help_window_layout()

        self.mod_window = self.create.window(window_key="Mods")
        self.mod_window_layout()


    ########################
    #   Create Skeletons
    ########################


    def main_window_layout(self):
        '''Create the main window skeleton.'''

        # Header
        self.create.window_header_layout(window=self.main_window, header_height=60)
        header_layout = self.main_window.header_layout
        self.create.row(layout=header_layout, height_percent=40)
        self.create.column(layout=header_layout, width_percent=50)
        self.create.cell(layout=header_layout, hover_highlight=True)
        self.create.element_text(layout=header_layout, text="Help", target_size=12)
        self.create.element_border(layout=header_layout, line_width=1)
        self.create.event_call_back(layout=header_layout, func=self.toggle_help)

        self.create.column(layout=header_layout, width_percent=50)
        self.create.cell(layout=header_layout, hover_highlight=True)
        self.create.element_text(layout=header_layout, text="Modifiers", target_size=12)
        self.create.element_border(layout=header_layout, line_width=1)
        self.create.event_call_back(layout=header_layout, func=self.toggle_mods)

        self.create.row(layout=header_layout, height_percent=60)
        self.create.column(layout=header_layout, width_percent=20)
        self.create.cell(layout=header_layout, hover_highlight=True)
        self.create.element_image(layout=header_layout, image=self.images[0], scale=1, force_fit=False)
        self.create.element_border(layout=header_layout, line_width=3)
        self.create.column(layout=header_layout, width_percent=80)
        self.create.cell(layout=header_layout, hover_highlight=True)
        self.create.element_text(layout=header_layout, text="Main Window", target_size=24)
        self.create.element_border(layout=header_layout, line_width=3)

        # Body

        # Panel 1
        self.create.panel(window=self.main_window, x_split_percent=100, y_split_percent=100)

        # Widget
        self.create.widget_text(panel=self.main_window.panels[-1], win_key="Help")
        widget = self.main_window.panels[-1].widget

        self.create.widget_body_layout(widget=widget)
        body_layout = widget.layout


    def help_window_layout(self):
        '''Create the help window skeleton.'''

        # Header
        self.create.window_header_layout(window=self.help_window, header_height=40)
        header_layout = self.help_window.header_layout
        self.create.row(layout=header_layout, height_percent=100)
        self.create.column(layout=header_layout, width_percent=20)
        self.create.cell(layout=header_layout, hover_highlight=True)
        self.create.element_image(layout=header_layout, image=self.images[2], scale=1, force_fit=False)
        self.create.element_border(layout=header_layout, line_width=3)
        self.create.column(layout=header_layout, width_percent=80)
        self.create.cell(layout=header_layout, hover_highlight=True)
        self.create.element_text(layout=header_layout, text="Help Window", target_size=24)
        self.create.element_border(layout=header_layout, line_width=3)

        # Body

        # Panel 1
        self.create.panel(window=self.help_window, x_split_percent=100, y_split_percent=100)

        # Widget
        self.create.widget_scroll(panel=self.help_window.panels[-1], win_key="Help")
        widget = self.help_window.panels[-1].widget

        # Widget Header
        self.create.widget_header_layout(widget=widget, header_height=30)
        header_layout = widget.header_layout

        self.create.row(layout=header_layout, height_percent=100)
        self.create.column(layout=header_layout, width_percent=100)
        self.create.cell(layout=header_layout, hover_highlight=True)
        self.create.element_text(layout=header_layout, text="Help")
        self.create.element_border(layout=header_layout, line_width=2)

        self.create.widget_body_layout(widget=widget)
        body_layout = widget.layout


    def mod_window_layout(self):
        '''Create the mods window skeleton.'''

        # Header
        self.create.window_header_layout(window=self.mod_window, header_height=40)
        header_layout = self.mod_window.header_layout
        self.create.row(layout=header_layout, height_percent=100)
        self.create.column(layout=header_layout, width_percent=20)
        self.create.cell(layout=header_layout, hover_highlight=True)
        self.create.element_image(layout=header_layout, image=self.images[1], scale=1, force_fit=False)
        self.create.element_border(layout=header_layout, line_width=3)
        self.create.column(layout=header_layout, width_percent=80)
        self.create.cell(layout=header_layout, hover_highlight=True)
        self.create.element_text(layout=header_layout, text="Mod Window", target_size=24)
        self.create.element_border(layout=header_layout, line_width=3)

        # Body
        self.create.panel(window=self.mod_window, x_split_percent=100, y_split_percent=100)

        # Widget
        self.create.widget_scroll(panel=self.mod_window.panels[-1], win_key="Mods")
        widget = self.mod_window.panels[-1].widget

        # Widget Header
        self.create.widget_header_layout(widget=widget, header_height=30)
        header_layout = widget.header_layout

        self.create.row(layout=header_layout, height_percent=100)
        self.create.column(layout=header_layout, width_percent=100)
        self.create.cell(layout=header_layout, hover_highlight=True)
        self.create.element_text(layout=header_layout, text="Modifiers")
        self.create.element_border(layout=header_layout, line_width=2)

        self.create.widget_body_layout(widget=widget)
        body_layout = widget.layout


    ########################
    #   Populate Skeletons
    ########################


    def build_main(self, win_dict, window_name):

        widget = self.main_window.panels[0].widget
        layout = widget.layout

        self.create.row(layout=layout, height_percent=100)

        self.create.column(layout=layout, width_percent=20)
        if win_dict["main_count"] != []:
            self.create.cell(layout=layout, hover_highlight=True)
            self.create.element_background(layout=layout, primary=False, bevel=True)
            self.add_list_items(layout=layout, dict_val=win_dict["main_count"], primary=False, target_size=18, drag=True)


        self.create.column(layout=layout, width_percent=40)
        if win_dict["header_sub_text"] != []:
            self.create.cell(layout=layout, hover_highlight=True)
            self.create.element_background(layout=layout, primary=False, bevel=True)
            self.add_list_items(layout=layout, dict_val=win_dict["header_sub_text"], primary=False)

        self.create.column(layout=layout, width_percent=40)

        if win_dict["last_col_cell_1"] != []:
            self.create.cell(layout=layout, hover_highlight=True)
            self.create.element_background(layout=layout, primary=False, bevel=True)
            self.add_list_items(layout=layout, dict_val=win_dict["last_col_cell_1"], primary=False)


        if win_dict["last_col_cell_2"] != []:
            self.create.cell(layout=layout, hover_highlight=True)
            self.create.element_background(layout=layout, primary=False, bevel=True)
            self.add_list_items(layout=layout, dict_val=win_dict["last_col_cell_2"], primary=False)


        if win_dict["last_col_cell_3"] != []:
            self.create.cell(layout=layout, hover_highlight=True)
            self.create.element_background(layout=layout, primary=False, bevel=True)
            self.add_list_items(layout=layout, dict_val=win_dict["last_col_cell_3"], primary=False)


    def build_help(self, hot_keys_dict, quick_ops_dict):

        widget = self.help_window.panels[0].widget
        layout = widget.layout
        rows = len(hot_keys_dict)
        row_percent = 100 / rows if rows > 0 else 100

        for key, val in hot_keys_dict.items():

            self.create.row(layout=layout, height_percent=row_percent)
            self.create.column(layout=layout, width_percent=30)
            self.create.cell(layout=layout, hover_highlight=True)
            self.create.element_text(layout=layout, text=key)
            self.create.element_border(layout=layout, line_width=2)

            self.create.column(layout=layout, width_percent=70)
            self.create.cell(layout=layout, hover_highlight=True)

            self.add_list_items(layout=layout, dict_val=val)


    def build_mods(self, win_dict, active_mod_name):

        widget = self.mod_window.panels[0].widget
        layout = widget.layout
        rows = len(win_dict)
        row_percent = 100 / rows if rows > 0 else 100

        count = len(win_dict)
        for key, val in win_dict.items():

            if key == active_mod_name:
                # Row
                self.create.row(layout=layout, height_percent=row_percent)
                # Col
                self.create.column(layout=layout, width_percent=10)
                self.create.cell(layout=layout, hover_highlight=True)
                self.create.element_text(layout=layout, text=str(count))
                self.create.element_border(layout=layout, line_width=2)
                # Col
                self.create.column(layout=layout, width_percent=15)
                self.create.cell(layout=layout, hover_highlight=True)
                self.create.element_geo(layout=layout, shape="TRIANGLE_RIGHT", color="HIGHLIGHT", padding=6, border=True)
                self.create.element_border(layout=layout, line_width=2)
                # Col
                self.create.column(layout=layout, width_percent=50)
                self.create.cell(layout=layout, hover_highlight=True)
                self.create.element_text(layout=layout, text=key)
                self.create.element_border(layout=layout, line_width=2)
                # Col
                self.create.column(layout=layout, width_percent=25)
                self.create.cell(layout=layout, hover_highlight=True)
                self.create.element_text(layout=layout, text=val)
                self.create.element_border(layout=layout, line_width=1)

            else:
                # Row
                self.create.row(layout=layout, height_percent=row_percent)
                # Col
                self.create.column(layout=layout, width_percent=10)
                self.create.cell(layout=layout, hover_highlight=True)
                self.create.element_text(layout=layout, text=str(count))
                self.create.element_border(layout=layout, line_width=2)
                # Col
                self.create.column(layout=layout, width_percent=65)
                self.create.cell(layout=layout, hover_highlight=True)
                self.create.element_text(layout=layout, text=key)
                self.create.element_border(layout=layout, line_width=2)
                # Col
                self.create.column(layout=layout, width_percent=25)
                self.create.cell(layout=layout, hover_highlight=True)
                self.create.element_text(layout=layout, text=val)
                self.create.element_border(layout=layout, line_width=1)

            count -= 1


    def add_list_items(self, layout=None, dict_val=[], primary=True, target_size=12, drag=False):

        if type(dict_val) == str:
            self.create.element_border(layout=layout, line_width=1)
            self.create.element_text(layout=layout, text=dict_val, primary=primary, target_size=target_size)

        if len(dict_val) > 0:

            if len(dict_val) == 1:
                self.create.element_border(layout=layout, line_width=1)
                self.create.element_text(layout=layout, text=dict_val[0], primary=primary, target_size=target_size)

            if len(dict_val) == 2:
                if drag:
                    self.create.event_call_drag(layout=layout, func=dict_val[1])
                else:
                    self.create.event_call_back(layout=layout, func=dict_val[1])

                self.create.element_border(layout=layout, line_width=1)
                self.create.element_text(layout=layout, text=dict_val[0], primary=primary, target_size=target_size)

            elif len(dict_val) == 3:
                if drag:
                    self.create.event_call_drag(layout=layout, func=dict_val[1], positive_args=dict_val[2])
                
                else:
                    self.create.event_call_back(layout=layout, func=dict_val[1], positive_args=dict_val[2])
                self.create.element_border(layout=layout, line_width=1)
                self.create.element_text(layout=layout, text=dict_val[0], primary=primary, target_size=target_size)

            elif len(dict_val) == 4:
                if drag:
                    self.create.event_call_drag(layout=layout, func=dict_val[1], positive_args=dict_val[2], negative_args=dict_val[3])
                
                else:
                    self.create.event_call_back(layout=layout, func=dict_val[1], positive_args=dict_val[2], negative_args=dict_val[3])
                self.create.element_border(layout=layout, line_width=1)
                self.create.element_text(layout=layout, text=dict_val[0], primary=primary, target_size=target_size)


    def destroy(self):

        # Unload images
        if self.images != []:
            for image in self.images:
                bpy.data.images.remove(image)


    def toggle_help(self):
        '''Toggle the help window.'''

        self.db.prefs.ui.Hops_modal_help_visible = not self.db.prefs.ui.Hops_modal_help_visible


    def toggle_mods(self):
        '''Toggle the mods window.'''

        self.db.prefs.ui.Hops_modal_mods_visible = not self.db.prefs.ui.Hops_modal_mods_visible
