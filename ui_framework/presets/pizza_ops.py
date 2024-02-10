import bpy, webbrowser
from mathutils import Vector
from . utils import add_list_items, toggle_help, toggle_mods
from .. graphics.load import load_image_file
from ... preferences import get_preferences

class Preset_Pizza_Ops():

    def __init__(self, create):

        self.create = create
        self.db = self.create.db
        self.images = []
        self.main_window = None
        self.widget = None
        self.widget_layout = None

        self.setup()


    def setup(self):

        # Create windows
        self.main_window = self.create.window(window_key="Pizza_Ops")
        self.main_window_layout()

        # Override colors
        prefs = get_preferences()

        # Original
        self.prefs_colors = []
        self.prefs_colors.append(prefs.color.Hops_UI_background_color)
        self.prefs_colors.append(prefs.color.Hops_UI_cell_background_color)
        self.prefs_colors.append(prefs.color.Hops_UI_border_color)
        self.prefs_colors.append(prefs.color.Hops_UI_mods_highlight_color)

        # Cloned
        self.Hops_UI_background_color      = Vector((self.prefs_colors[0][0], self.prefs_colors[0][1], self.prefs_colors[0][2], self.prefs_colors[0][3]))
        self.Hops_UI_cell_background_color = Vector((self.prefs_colors[1][0], self.prefs_colors[1][1], self.prefs_colors[1][2], self.prefs_colors[1][3]))
        self.Hops_UI_border_color          = Vector((self.prefs_colors[2][0], self.prefs_colors[2][1], self.prefs_colors[2][2], self.prefs_colors[2][3]))
        self.Hops_UI_mods_highlight_color  = Vector((self.prefs_colors[3][0], self.prefs_colors[3][1], self.prefs_colors[3][2], self.prefs_colors[3][3]))

        # Set overrides
        prefs.color.Hops_UI_background_color      = (.375,.375,1,.5)
        prefs.color.Hops_UI_cell_background_color = (0,1,0,.5)
        prefs.color.Hops_UI_border_color          = (1,0,1,.75)
        prefs.color.Hops_UI_mods_highlight_color  = (1,0,1,1)


    ########################
    #   Create Skeletons
    ########################


    def main_window_layout(self):
        '''Create the main window skeleton.'''

        # Panel 1
        self.create.panel(window=self.main_window, x_split_percent=100, y_split_percent=100)

        # Header
        self.create.window_header_layout(window=self.main_window, header_height_percent=20, min_max_height=(20, 30))

        header_layout = self.main_window.header_layout
        self.create.row(layout=header_layout, height_percent=100)

        self.create.column(layout=header_layout, width_percent=100)
        self.create.cell(layout=header_layout, hover_highlight=True)
        self.create.element_text(layout=header_layout, text="Pizza Ops", target_size=12)
        self.create.element_border(layout=header_layout, line_width=1)

        # Widget
        split_count = get_preferences().ui.Hops_modal_pizza_ops_display_count
        self.create.widget_scroll(panel=self.main_window.panels[-1], win_key="Pizza_Ops", collapsable=False, split_count_override=True, split_count=split_count)
        self.widget = self.main_window.panels[-1].widget
        self.widget.split_count = split_count

        self.create.widget_body_layout(widget=self.widget)
        self.widget_layout = self.widget.layout

    ########################
    #   Populate Skeletons
    ########################

    def build_main(self, win_dict, window_name, win_form=None):

        split_count = get_preferences().ui.Hops_modal_pizza_ops_display_count
        self.widget.split_count = split_count
        row_percent = 100 / len(win_dict) if len(win_dict) > 0 else 100

        for key, val in win_dict.items():

            image = val["icon"]
            link = val["link"]
            desc = val["description"]

            self.create.row(layout=self.widget_layout, height_percent=row_percent)
            self.create.column(layout=self.widget_layout, width_percent=100)
            self.create.cell(layout=self.widget_layout, hover_highlight=True)
            self.create.element_background(layout=self.widget_layout, primary=False, bevel=True)
            self.create.element_border(layout=self.widget_layout, line_width=1)
            self.create.element_image(layout=self.widget_layout, image=image, scale=1, force_fit=False, padding=6, maximize=True)
            #self.create.element_background(layout=self.widget_layout, primary=True, bevel=False, dims_override=(0, 0, -.3125, .375))
            self.create.element_text(layout=self.widget_layout, target_size=16, text=desc, color_select=2, bottom_align=True, y_offset=-.125)
            self.create.event_call_back(layout=self.widget_layout, func=self.web_link_callback, positive_args=(link, ))
    

    def web_link_callback(self, link=""):
        '''Function to create the web link call back.'''

        webbrowser.open(link)


    def destroy(self):

        # Unload images
        if self.images != []:
            for image in self.images:
                if image != None:
                    try:
                        bpy.data.images.remove(image)
                    except:
                        pass

        # Set color overrides back to original
        prefs = get_preferences()
        prefs.color.Hops_UI_background_color      = self.Hops_UI_background_color
        prefs.color.Hops_UI_cell_background_color = self.Hops_UI_cell_background_color
        prefs.color.Hops_UI_border_color          = self.Hops_UI_border_color
        prefs.color.Hops_UI_mods_highlight_color  = self.Hops_UI_mods_highlight_color