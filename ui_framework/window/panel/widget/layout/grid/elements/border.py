from .......graphics.draw import draw_border_lines


class Border_Element():

    def __init__(self):

        # Global
        self.db = None

        # Dims
        self.top_left = (0, 0)
        self.top_right = (0, 0)
        self.bottom_left = (0, 0)
        self.bottom_right = (0, 0)

        # Element Props
        self.line_width = 3


    def draw(self):
        
        if self.db.prefs.ui.Hops_modal_cell_border:

            vertices =[self.top_left, self.bottom_left, self.top_right, self.bottom_right]
            color = self.db.colors.Hops_UI_border_color

            draw_border_lines(vertices=vertices, width=self.line_width, color=color, bevel_corners=True)