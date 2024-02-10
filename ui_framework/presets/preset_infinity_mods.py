import bpy
from ..graphics.load import load_image_file
from .utils import add_list_items, toggle_help, toggle_mods

class Preset_Infinity_Mods():

    def __init__(self, create):

        self.create = create
        self.db = self.create.db
        self.images = []

        # Main Window
        self.main_window = None
        self.main_window_text = None

        # Help Window
        self.help_window = None

        # Mods Window
        self.mod_window = None

        self.setup()


    def setup(self):

        # Load Images
        self.images.append(load_image_file(filename="logo_red"))

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
        self.create.window_header_layout(window=self.main_window, header_height_percent=20, min_max_height=(10, 40))

        header_layout = self.main_window.header_layout
        self.create.row(layout=header_layout, height_percent=100)

        self.create.column(layout=header_layout, width_percent=20)
        self.create.cell(layout=header_layout, hover_highlight=False)
        self.create.element_image(layout=header_layout, image=self.images[0], scale=.8, force_fit=False)
        self.create.element_border(layout=header_layout, line_width=1)

        self.create.column(layout=header_layout, width_percent=40)
        self.create.cell(layout=header_layout, hover_highlight=True)
        self.create.element_text(layout=header_layout, text="Help", target_size=12)
        self.create.element_border(layout=header_layout, line_width=1)
        self.create.event_call_back(layout=header_layout, func=toggle_help, positive_args=(self.db,))

        self.create.column(layout=header_layout, width_percent=40)
        self.create.cell(layout=header_layout, hover_highlight=True)
        self.create.element_text(layout=header_layout, text="Modifiers", target_size=12)
        self.create.element_border(layout=header_layout, line_width=1)
        self.create.event_call_back(layout=header_layout, func=toggle_mods, positive_args=(self.db,))

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

        # Body
        # Panel 1
        self.create.panel(window=self.help_window, x_split_percent=100, y_split_percent=100)

        # Widget
        self.create.widget_scroll(panel=self.help_window.panels[-1], win_key="Help")
        widget = self.help_window.panels[-1].widget

        # Widget Header
        self.create.widget_header_layout(widget=widget, header_height_percent=20)
        header_layout = widget.header_layout

        self.create.row(layout=header_layout, height_percent=100)
        self.create.column(layout=header_layout, width_percent=100)
        self.create.cell(layout=header_layout, hover_highlight=False)
        self.create.element_text(layout=header_layout, text="Help")
        self.create.element_border(layout=header_layout, line_width=2)

        self.create.widget_body_layout(widget=widget)
        body_layout = widget.layout


    def mod_window_layout(self):
        '''Create the mods window skeleton.'''

        # Body
        self.create.panel(window=self.mod_window, x_split_percent=100, y_split_percent=100)

        # Widget
        self.create.widget_scroll(panel=self.mod_window.panels[-1], win_key="Mods")
        widget = self.mod_window.panels[-1].widget

        # Widget Header
        self.create.widget_header_layout(widget=widget, header_height_percent=20)
        header_layout = widget.header_layout

        self.create.row(layout=header_layout, height_percent=100)
        self.create.column(layout=header_layout, width_percent=100)
        self.create.cell(layout=header_layout, hover_highlight=False)
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

        #self.main_window_text.text = window_name

        self.create.row(layout=layout, height_percent=100)

        self.create.column(layout=layout, width_percent=20)
        if win_dict["main_count"] != []:
            self.create.cell(layout=layout, hover_highlight=True, dims_override=(4,-4,-4,4))
            self.create.element_background(layout=layout, primary=False, bevel=True)
            add_list_items(create=self.create, layout=layout, dict_val=win_dict["main_count"], color_select=1, target_size=18)


        self.create.column(layout=layout, width_percent=40)

        if win_dict["last_col_cell_1"] != []:
            self.create.cell(layout=layout, hover_highlight=True, dims_override=(0,-4,0,4))
            self.create.element_background(layout=layout, primary=False, bevel=True)
            add_list_items(create=self.create, layout=layout, dict_val=win_dict["last_col_cell_1"], color_select=1)

        if win_dict["header_sub_text"] != []:
            self.create.cell(layout=layout, hover_highlight=True, dims_override=(0,-4,-4,0))
            self.create.element_background(layout=layout, primary=False, bevel=True)
            add_list_items(create=self.create, layout=layout, dict_val=win_dict["header_sub_text"], color_select=1)

        self.create.column(layout=layout, width_percent=40)

        padding = 0
        if win_dict["last_col_cell_3"] == []:
            padding = -4

        if win_dict["last_col_cell_2"] != []:
            self.create.cell(layout=layout, hover_highlight=True, dims_override=(0,-4,padding,4))
            self.create.element_background(layout=layout, primary=False, bevel=True)
            add_list_items(create=self.create, layout=layout, dict_val=win_dict["last_col_cell_2"], color_select=1)

        if win_dict["last_col_cell_3"] != []:
            self.create.cell(layout=layout, hover_highlight=True, dims_override=(0,-4,-4,0))
            self.create.element_background(layout=layout, primary=False, bevel=True)
            add_list_items(create=self.create, layout=layout, dict_val=win_dict["last_col_cell_3"], color_select=1)


    def build_help(self, hot_keys_dict, quick_ops_dict):


            widget = self.help_window.panels[0].widget
            layout = widget.layout
            rows = len(hot_keys_dict)
            row_percent = 100 / rows if rows > 0 else 100

            primary = True
            target_size = 12
            drag = False

            for key, val in hot_keys_dict.items():
                
                # Add key
                self.create.row(layout=layout, height_percent=row_percent)
                self.create.column(layout=layout, width_percent=30)
                self.create.cell(layout=layout, hover_highlight=True, dims_override=(0,-6,0,0))
                self.create.element_background(layout=layout, primary=False, bevel=True)
                self.create.element_border(layout=layout, line_width=1)
                self.create.element_text(layout=layout, text=key, color_select=1)

                if type(val) == str:

                    # Add description
                    self.create.column(layout=layout, width_percent=70)
                    self.create.cell(layout=layout, hover_highlight=False)
                    self.create.element_border(layout=layout, line_width=1)
                    self.create.element_text(layout=layout, text=val, color_select=0, target_size=target_size)

                if len(val) > 0:

                    if len(val) == 1:

                        # Add description
                        self.create.column(layout=layout, width_percent=70)
                        self.create.cell(layout=layout, hover_highlight=False)
                        self.create.element_text(layout=layout, text=val[0], color_select=0, target_size=target_size)

                    if len(val) == 2:
                        if drag:
                            self.create.event_call_drag(layout=layout, func=val[1])
                        else:
                            self.create.event_call_back(layout=layout, func=val[1])
                        
                        # Add description
                        self.create.column(layout=layout, width_percent=70)
                        self.create.cell(layout=layout, hover_highlight=False)
                        self.create.element_border(layout=layout, line_width=1)
                        self.create.element_text(layout=layout, text=val[0], color_select=0, target_size=target_size)

                    elif len(val) == 3:
                        if drag:
                            self.create.event_call_drag(layout=layout, func=val[1], positive_args=val[2])
                        
                        else:
                            self.create.event_call_back(layout=layout, func=val[1], positive_args=val[2])

                        # Add description
                        self.create.column(layout=layout, width_percent=70)
                        self.create.cell(layout=layout, hover_highlight=False)
                        self.create.element_border(layout=layout, line_width=1)
                        self.create.element_text(layout=layout, text=val[0], color_select=0, target_size=target_size)

                    elif len(val) == 4:
                        if drag:
                            self.create.event_call_drag(layout=layout, func=val[1], positive_args=val[2], negative_args=val[3])
                        
                        else:
                            self.create.event_call_back(layout=layout, func=val[1], positive_args=val[2], negative_args=val[3])

                        # Add description
                        self.create.column(layout=layout, width_percent=70)
                        self.create.cell(layout=layout, hover_highlight=False)
                        self.create.element_border(layout=layout, line_width=1)
                        self.create.element_text(layout=layout, text=val[0], color_select=0, target_size=target_size)


    def build_mods(self, win_dict, active_mod_name, body_scroll=True):

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
                self.create.cell(layout=layout, hover_highlight=False)
                self.create.element_border(layout=layout, line_width=1)
                self.create.element_text(layout=layout, text=str(count))
                # Col
                self.create.column(layout=layout, width_percent=65)
                self.create.cell(layout=layout, hover_highlight=False)
                self.create.element_background(layout=layout, primary=False, bevel=True)
                self.create.element_border(layout=layout, line_width=1)
                self.create.element_text(layout=layout, text=key, color_select=2)
                # Col
                self.create.column(layout=layout, width_percent=25)
                self.create.cell(layout=layout, hover_highlight=False)
                self.create.element_border(layout=layout, line_width=1)
                self.create.element_text(layout=layout, text=val)

            else:
                # Row
                self.create.row(layout=layout, height_percent=row_percent)
                # Col
                self.create.column(layout=layout, width_percent=10)
                self.create.cell(layout=layout, hover_highlight=False)
                self.create.element_border(layout=layout, line_width=1)
                self.create.element_text(layout=layout, text=str(count))
                # Col
                self.create.column(layout=layout, width_percent=65)
                self.create.cell(layout=layout, hover_highlight=False)
                self.create.element_border(layout=layout, line_width=1)
                self.create.element_text(layout=layout, text=key)
                # Col
                self.create.column(layout=layout, width_percent=25)
                self.create.cell(layout=layout, hover_highlight=False)
                self.create.element_border(layout=layout, line_width=1)
                self.create.element_text(layout=layout, text=val)

            count -= 1


    def destroy(self):

        # Unload images
        if self.images != []:
            for image in self.images:
                if image != None:
                    try:
                        bpy.data.images.remove(image)
                    except:
                        pass