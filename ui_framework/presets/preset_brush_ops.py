import bpy, webbrowser
from mathutils import Vector
from . utils import add_list_items, toggle_help, toggle_mods
from .. graphics.load import load_image_file
from ... preferences import get_preferences

class Preset_Brush_Ops():

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
        self.main_window = self.create.window(window_key="Brush_Ops")
        self.main_window_layout()

        # Override colors
        prefs = get_preferences()

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
        self.create.element_text(layout=header_layout, text="Brush List", target_size=12)
        self.create.element_border(layout=header_layout, line_width=1)

        # Widget
        self.create.widget_scroll(panel=self.main_window.panels[-1], win_key="Brush_Ops", collapsable=False, split_count_override=False)
        self.widget = self.main_window.panels[-1].widget
        # self.widget.split_count = split_count

        self.create.widget_body_layout(widget=self.widget)
        self.widget_layout = self.widget.layout

    ########################
    #   Populate Skeletons
    ########################

    def build_main(self, win_dict, window_name, win_form=None):

        row_percent = 100 / len(win_dict) if len(win_dict) > 0 else 100

        for brush_form in reversed(win_dict):
            self.create.row(layout=self.widget_layout, height_percent=row_percent)
            self.create.column(layout=self.widget_layout, width_percent=75)
            self.create.cell(layout=self.widget_layout, hover_highlight=True)
            #self.create.element_background(layout=self.widget_layout, primary=False, bevel=True)
            #self.create.element_border(layout=self.widget_layout, line_width=1)
            self.create.element_text(layout=self.widget_layout, target_size=16, text=brush_form.name)
            self.create.event_call_back(layout=self.widget_layout, func=brush_form.call_back, positive_args=brush_form.call_args)

            self.create.column(layout=self.widget_layout, width_percent=25)
            self.create.cell(layout=self.widget_layout, hover_highlight=True)
            self.create.element_background(layout=self.widget_layout, primary=False, bevel=True)
            self.create.element_border(layout=self.widget_layout, line_width=1)
            self.create.element_text(layout=self.widget_layout, target_size=16, text=brush_form.hot_key_display)
            self.create.event_call_back(layout=self.widget_layout, func=brush_form.call_back, positive_args=brush_form.call_args)

    
    def destroy(self):

        # Unload images
        if self.images != []:
            for image in self.images:
                if image != None:
                    try:
                        bpy.data.images.remove(image)
                    except:
                        pass
