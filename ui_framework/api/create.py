# Tree
from ..window.window import Window
from ..window.panel.panel import  Panel
from ..window.panel.widget.layout.layout import Layout
from ..window.panel.widget.layout.grid.row import Row
from ..window.panel.widget.layout.grid.column import Column
from ..window.panel.widget.layout.grid.cell import Cell

# Widgets
from ..window.panel.widget.text_widget import Text_Widget
from ..window.panel.widget.scroll_widget import Scroll_Widget

# Elements
from ..window.panel.widget.layout.grid.elements.text import Text_Element
from ..window.panel.widget.layout.grid.elements.border import Border_Element
from ..window.panel.widget.layout.grid.elements.background import Background_Element
from ..window.panel.widget.layout.grid.elements.image import Image_Element
from ..window.panel.widget.layout.grid.elements.drop_shadow import Drop_Shadow_Element
from ..window.panel.widget.layout.grid.elements.geo import Geo_Element

# Event
from ..window.panel.widget.layout.grid.elements.call_back import Call_Back_Event
from ..window.panel.widget.layout.grid.elements.drag import Drag_Event


class Create():

    def __init__(self, db):

        # Database
        self.db = db

        self.cell_index = 0


    ########################
    #   Window
    ########################


    def window(self, window_key="", background=True, border=True, primary=True, bevel=True, line_width=3, drop_shadow=True):
        '''Create and return a window.'''

        window = Window(db=self.db, window_key=window_key)

        if drop_shadow:
            element = Drop_Shadow_Element()
            element.db = self.db
            element.bevel = bevel
            window.elements.append(element)

        if background:
            element = Background_Element()
            element.db = self.db
            element.cell_bg = False
            element.primary = primary
            element.bevel = bevel
            window.elements.append(element)

        if border:
            element = Border_Element()
            element.db = self.db
            element.line_width = line_width
            window.elements.append(element)

        self.db.windows[window_key] = window

        return window


    def window_header_layout(self, window=None, header_height_percent=0, min_max_height=(15, 40)):
        '''Insert the layout into the window and set header height on window'''

        min_max_height = (min_max_height[0] * self.db.scale_factor, min_max_height[1] * self.db.scale_factor)

        window.header_height_percent = header_height_percent
        window.min_max_height = min_max_height
        window.header_layout = Layout(db=self.db)


    ########################
    #   Spacers
    ########################


    def panel(self, window=None, x_split_percent=100, y_split_percent=100):
        '''Create a panel for the lastly created window.'''

        panel = Panel()
        panel.window = window
        panel.x_split_percent = x_split_percent
        panel.y_split_percent = y_split_percent

        window.panels.append(panel)


    def row(self, layout=None, height_percent=100):
        '''Insert a row into the target layout.'''

        row = Row()
        row.height_percent = height_percent

        layout.rows.append(row)


    def column(self, layout=None, width_percent=100):
        '''Insert a column into the target layout.'''

        column = Column()
        column.width_percent = width_percent

        layout.rows[-1].columns.append(column)


    def cell(self, layout=None, hover_highlight=True, dims_override=(0,0,0,0)):
        '''Create a panel for the lastly created window.\n
        dims_override = Left, Right, Top, Bottom (PIXELS)'''

        self.cell_index += 1

        if dims_override != (0,0,0,0):
            dims_override = (
                dims_override[0] * self.db.scale_factor,
                dims_override[1] * self.db.scale_factor,
                dims_override[2] * self.db.scale_factor,
                dims_override[3] * self.db.scale_factor)

        cell = Cell()
        cell.db = self.db
        cell.hover_highlight = hover_highlight
        cell.dims_override = dims_override

        layout.rows[-1].columns[-1].cells.append(cell)


    ########################
    #   Widgets
    ########################


    def widget_text(self, panel=None, win_key=""):
        '''Insert a text widget into the panel.'''

        widget = Text_Widget()
        widget.panel = panel
        widget.win_key = win_key

        panel.widget = widget


    def widget_scroll(self, panel=None, win_key="", collapsable=False, split_count_override=False, split_count=1):
        '''Insert a scroll widget into the panel.'''

        widget = Scroll_Widget(db=self.db)
        widget.win_key = win_key
        widget.collapsable = collapsable

        if split_count_override:
            widget.split_count_override = True
            widget.split_count = split_count

        panel.widget = widget


    def widget_body_layout(self, widget=None):
        '''Create a body layout for the widget.'''

        if widget != None:
            layout = Layout(db=self.db)

            widget.layout = layout


    def widget_header_layout(self, widget=None, header_height_percent=0, min_max_height=(15, 30)):
        '''Create a header layout for the widget.'''

        min_max_height = (min_max_height[0] * self.db.scale_factor, min_max_height[1] * self.db.scale_factor)

        if widget != None:
            layout = Layout(db=self.db)

            widget.header_height_percent = header_height_percent
            widget.min_max_height = min_max_height
            widget.header_layout = layout


    ########################
    #   Elements
    ########################


    def element_text(self, layout=None, text="", centered=True, color_select=0, target_size=12, force_fit_text=True, bottom_align=False, y_offset=0):
        '''Add the element to the lastly created cell on the layout\n
        Colors: 0 = Primary, 1 = Secondary, 2 = Mod Highlight'''

        element = Text_Element()
        element.db = self.db
        element.text = text
        element.centered = centered
        element.target_size = target_size
        element.color_select = color_select
        element.force_fit_text = force_fit_text
        element.bottom_align = bottom_align
        element.y_offset = y_offset

        layout.rows[-1].columns[-1].cells[-1].elements.append(element)

        return element


    def element_background(self, layout=None, primary=True, bevel=True, dims_override=(0,0,0,0)):
        '''Add the element to the lastly created cell on the layout\n
        dims_override = Left, Right, Top, Bottom : Examples -> 1 = same size, 2 = double, .5 = half'''

        element = Background_Element()
        element.db = self.db
        element.primary = primary
        element.bevel = bevel
        element.dims_override = dims_override

        layout.rows[-1].columns[-1].cells[-1].elements.append(element)


    def element_border(self, layout=None, line_width=3):
        '''Add the element to the lastly created cell on the layout'''

        element = Border_Element()
        element.db = self.db
        element.line_width = line_width

        layout.rows[-1].columns[-1].cells[-1].elements.append(element)


    def element_image(self, layout=None, image=None, scale=1, force_fit=False, padding=6, maximize=False):
        '''Add the element to the lastly created cell on the layout'''

        element = Image_Element()
        element.db = self.db
        element.image = image
        element.scale = scale
        element.force_fit = force_fit
        element.padding = padding
        element.maximize = maximize

        layout.rows[-1].columns[-1].cells[-1].elements.append(element)


    def element_geo(self, layout=None, shape="", color="", padding=0, border=False):
        '''Add the element to the lastly created cell on the layout\n
        shape options: ('TRIANGLE_RIGHT', TRIANGLE_DOWN )\n
        color options: ('PRIMARY', 'SECONDARY', 'HIGHLIGHT')'''

        element = Geo_Element()
        element.db = self.db
        element.selected_shape = shape
        element.selected_color = color
        element.border = border
        element.padding = padding

        layout.rows[-1].columns[-1].cells[-1].elements.append(element)


    ########################
    #   Event Elements
    ########################


    def event_call_back(self, layout=None, func=None, positive_args=None, negative_args=None, scrollable=False):
        '''Add the event to the lastly created cell on the layout.\n
        Func          : The function to call when the cell is clicked.\n
        Positive Args : When the cell is left clicked.\n
        Negative Args : When the cell is Alt Clicked.'''

        event = Call_Back_Event()
        event.db = self.db

        event.func = func
        event.positive_args = positive_args
        event.negative_args = negative_args
        event.scrollable = scrollable

        layout.rows[-1].columns[-1].cells[-1].click_events.append(event)

        return event


    def event_call_drag(self, layout=None, func=None, positive_args=None, negative_args=None):
        '''Add the event to the lastly created cell on the layout.\n
        Func          : The function to call when the cell is clicked.\n
        Positive Args : When the cell is left clicked.\n
        Negative Args : When the cell is Alt Clicked.'''

        event = Drag_Event()
        event.db = self.db

        event.func = func
        event.positive_args = positive_args
        event.negative_args = negative_args

        event.cell_index = self.cell_index

        layout.rows[-1].columns[-1].cells[-1].click_events.append(event)

        layout.rows[-1].columns[-1].cells[-1].cell_index = self.cell_index
