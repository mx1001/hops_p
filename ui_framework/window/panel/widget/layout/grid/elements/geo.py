from .......graphics.draw import render_geo
from .......graphics.draw import draw_border_lines


class Geo_Element():

    def __init__(self):

        # Global
        self.db = None

        # Dims
        self.top_left = (0, 0)
        self.top_right = (0, 0)
        self.bottom_left = (0, 0)
        self.bottom_right = (0, 0)

        # Element Props
        self.selected_shape = ""
        self.selected_color = ""
        self.padding = 0
        self.border = False


    def draw(self):
        
        color = (0,0,0,0)
        verts = []
        indices = []
        
        # Fitted square
        sq_bottom_left = ()
        sq_width = 0
        sq_height = 0

        # How far over the fitted square is inside the cell
        x_offset = 0
        y_offset = 0

        cell_width = self.bottom_right[0] - self.bottom_left[0]
        cell_height = self.top_left[1] - self.bottom_left[1]

        # Cell is wider than it is tall
        if cell_width >= cell_height:

            x_offset = (cell_width - cell_height) * .5
            sq_bottom_left = (self.bottom_left[0] + x_offset, self.bottom_left[1])
            sq_width = cell_height
            sq_height = cell_height

        # Cell is taller than it is wide
        elif cell_width <= cell_height:

            y_offset = (cell_height - cell_width) * .5
            sq_bottom_left = (self.bottom_left[0], self.bottom_left[1] + y_offset)
            sq_width = cell_width
            sq_height = cell_width


        # Color
        if self.selected_color == "PRIMARY":
            color = self.db.colors.Hops_UI_background_color
        
        elif self.selected_color == "SECONDARY":
            color = self.db.colors.Hops_UI_highlight_color

        elif self.selected_color == "HIGHLIGHT":
            color = self.db.colors.Hops_UI_highlight_drag_color 


        # Shapes

        # Triangle
        # Bottom Left, Top Right, Center

        if self.selected_shape == "TRIANGLE_RIGHT":

            verts = [
                (sq_bottom_left[0] + self.padding,            sq_bottom_left[1] + self.padding),
                (sq_bottom_left[0] + self.padding,            sq_bottom_left[1] - self.padding + sq_height),
                (sq_bottom_left[0] - self.padding + sq_width, sq_bottom_left[1] + (sq_height * .5))]

            indices = [(0, 1, 2)]

        elif self.selected_shape == "TRIANGLE_DOWN":

            verts = [
                (sq_bottom_left[0] + (sq_width * .5),         sq_bottom_left[1] + self.padding),
                (sq_bottom_left[0] + self.padding,            sq_bottom_left[1] + sq_height - self.padding),
                (sq_bottom_left[0] - self.padding + sq_width, sq_bottom_left[1] + sq_height - self.padding)]

            indices = [(0, 1, 2)]

        
        # Border lines
        if self.border:
            border_color = self.db.colors.Hops_UI_border_color
            border_verts = verts[:]
            border_verts.append(border_verts[0])
            draw_border_lines(vertices=border_verts, width=1, color=border_color, bevel_corners=False)

        # Draw geo
        render_geo(verts=verts, indices=indices, color=color)