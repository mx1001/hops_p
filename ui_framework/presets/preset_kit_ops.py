import bpy
from ..graphics.load import load_image_file
from .utils import add_list_items, toggle_help, toggle_mods
from ...preferences import get_preferences

class Preset_Kit_Ops():

    def __init__(self, create):

        self.create = create
        self.db = self.create.db
        self.images = []

        # Main Window
        self.main_window = None

        # Widgets
        self.thumbnails_widget = None
        self.folders_widget = None

        # Widget Layouts
        self.thumbnails_layout = None
        self.folders_layout = None

        # Special Overrides
        self.packs_text = None

        self.setup()


    def setup(self):

        # Create windows
        self.main_window = self.create.window(window_key="Kit_Ops")
        self.main_window_layout()


    ########################
    #   Create Skeletons
    ########################


    def main_window_layout(self):
        '''Create the main window skeleton.'''

        # Panel 1
        self.create.panel(window=self.main_window, x_split_percent=55, y_split_percent=70)

        # Header
        self.create.window_header_layout(window=self.main_window, header_height_percent=20, min_max_height=(10, 40))

        header_layout = self.main_window.header_layout
        self.create.row(layout=header_layout, height_percent=100)

        self.create.column(layout=header_layout, width_percent=100)
        self.create.cell(layout=header_layout, hover_highlight=True)
        self.window_text = self.create.element_text(layout=header_layout, text="Kitops", target_size=12)
        self.create.element_border(layout=header_layout, line_width=1)
        self.tab_event = self.create.event_call_back(layout=header_layout, func=None)

        # Widget
        split_count = get_preferences().ui.Hops_modal_kit_ops_display_count
        self.create.widget_scroll(panel=self.main_window.panels[-1], win_key="Kit_Ops", collapsable=False, split_count_override=True, split_count=split_count)
        self.thumbnails_widget = self.main_window.panels[-1].widget
        self.thumbnails_widget.split_count = split_count

        self.create.widget_body_layout(widget=self.thumbnails_widget)
        self.thumbnails_layout = self.thumbnails_widget.layout

        # Panel 2
        self.create.panel(window=self.main_window, x_split_percent=45, y_split_percent=30)

        # Widget
        self.create.widget_scroll(panel=self.main_window.panels[-1], win_key="Kit_Ops", collapsable=False)
        self.folders_widget = self.main_window.panels[-1].widget

        self.create.widget_header_layout(widget=self.folders_widget, header_height_percent=15, min_max_height=(15, 30))
        header_layout = self.folders_widget.header_layout
        self.create.row(layout=header_layout, height_percent=100)   
        self.create.column(layout=header_layout, width_percent=100)
        self.create.cell(layout=header_layout, hover_highlight=False)
        self.create.element_border(layout=header_layout, line_width=3)
        self.packs_text = self.create.element_text(layout=header_layout, text="Packs", color_select=0)

        self.create.widget_body_layout(widget=self.folders_widget)
        self.folders_layout = self.folders_widget.layout

    ########################
    #   Populate Skeletons
    ########################

    def build_main(self, win_dict, window_name, win_form=None):

        self.window_text.text = window_name
        self.tab_event.func = win_dict["function_call_back_for_tab"][0]
        self.tab_event.positive_args = win_dict["function_call_back_for_tab"][1]

        self.add_folders(items=win_dict["folders"])

        if 'powerlink' in win_dict:
            self.packs_text.text = 'Saves'
            self.add_powerlink_files(win_dict['powerlink'])
        else:
            self.packs_text.text = 'Packs'
            self.add_thumbnails(thumbs=win_dict["images"], files=win_dict["files"])


    def add_folders(self, items=[]):

        row_percent = 100 / len(items) if len(items) > 0 else 100
        for folder in items:
            folder_name = folder[0]
            if len(folder) == 1:
                self.create.row(layout=self.folders_layout, height_percent=row_percent)
                self.create.column(layout=self.folders_layout, width_percent=100)
                self.create.cell(layout=self.folders_layout, hover_highlight=True, dims_override=(0,0,0,0))
                self.create.element_background(layout=self.folders_layout, primary=False, bevel=True)
                self.create.element_border(layout=self.folders_layout, line_width=1)
                self.create.element_text(layout=self.folders_layout, text=folder_name, color_select=1)
                continue

            # Non Highlighted K-Packs
            if folder[3] == False:
                self.create.row(layout=self.folders_layout, height_percent=row_percent)
                self.create.column(layout=self.folders_layout, width_percent=100)
                self.create.cell(layout=self.folders_layout, hover_highlight=True, dims_override=(0,0,0,0))
                self.create.element_background(layout=self.folders_layout, primary=False, bevel=True)
                self.create.element_border(layout=self.folders_layout, line_width=1)
                self.create.element_text(layout=self.folders_layout, text=folder_name, color_select=1)
                self.create.event_call_back(layout=self.folders_layout, func=folder[1], positive_args=folder[2])

            # Highlight the active K-Pack
            else:
                self.create.row(layout=self.folders_layout, height_percent=row_percent)
                self.create.column(layout=self.folders_layout, width_percent=100)
                self.create.cell(layout=self.folders_layout, hover_highlight=True, dims_override=(0,0,0,0))
                self.create.element_background(layout=self.folders_layout, primary=False, bevel=True)
                self.create.element_border(layout=self.folders_layout, line_width=1)
                self.create.element_text(layout=self.folders_layout, text=folder_name, color_select=2)
                self.create.event_call_back(layout=self.folders_layout, func=folder[1], positive_args=folder[2])                


    def add_thumbnails(self, thumbs=[], files=[]):

        self.thumbnails_widget.split_count_override = True
        split_count = get_preferences().ui.Hops_modal_kit_ops_display_count
        self.thumbnails_widget.split_count = split_count

        row_percent = 100 / len(thumbs) if len(thumbs) > 0 else 100

        index = 0
        for thumb in thumbs:
            self.create.row(layout=self.thumbnails_layout, height_percent=row_percent)
            self.create.column(layout=self.thumbnails_layout, width_percent=100)
            self.create.cell(layout=self.thumbnails_layout, hover_highlight=True, dims_override=(0,0,0,0))
            self.create.element_background(layout=self.thumbnails_layout, primary=False, bevel=True)
            self.create.element_border(layout=self.thumbnails_layout, line_width=1)
            self.create.element_image(layout=self.thumbnails_layout, image=thumb[0], scale=1, force_fit=False, padding=6, maximize=True)
            #self.create.element_background(layout=self.thumbnails_layout, primary=False, bevel=True, dims_override=(0,0,-.75,0))

            if len(thumb) > 1:
                self.create.element_text(layout=self.thumbnails_layout, text=files[index][0], color_select=1, bottom_align=True, y_offset=-.9)
                self.create.event_call_back(layout=self.thumbnails_layout, func=thumb[1], positive_args=thumb[2])

            index += 1


    def add_powerlink_files(self, files=[]):

        row_percent = 100 / len(files) if len(files) > 0 else 100
        self.thumbnails_widget.split_count_override = False

        for item in files:
            self.create.row(layout=self.thumbnails_layout, height_percent=row_percent)
            self.create.column(layout=self.thumbnails_layout, width_percent=100)
            self.create.cell(layout=self.thumbnails_layout, hover_highlight=True, dims_override=(0,0,0,0))
            self.create.element_background(layout=self.thumbnails_layout, primary=False, bevel=True)
            self.create.element_border(layout=self.thumbnails_layout, line_width=1)

            self.create.element_text(layout=self.thumbnails_layout, text=item[0], color_select=1)
            self.create.event_call_back(layout=self.thumbnails_layout, func=item[1], positive_args=item[2])


    def destroy(self):

        # Unload images
        if self.images != []:
            for image in self.images:
                if image != None:
                    try:
                        bpy.data.images.remove(image)
                    except:
                        pass
