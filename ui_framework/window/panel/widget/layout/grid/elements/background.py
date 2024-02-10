from .......graphics.draw import render_quad

import gpu
import blf
import bgl
from bgl import *
from gpu_extras.batch import batch_for_shader
from .......utils.geo import bevel_verts


class Background_Element():

    def __init__(self):

        # Global
        self.db = None

        # Dims
        self.top_left = (0, 0)
        self.top_right = (0, 0)
        self.bottom_left = (0, 0)
        self.bottom_right = (0, 0)

        # Element Props
        self.primary = True
        self.bevel = True
        self.cell_bg = True
        self.dims_override = (0, 0, 0, 0)

        # Cell Event Props : Cells set this.
        self.highlight = False
        self.drag_highlight = False


    def draw(self):

        # Get the color
        if self.highlight:
            self.color = self.db.colors.Hops_UI_highlight_color
        
        elif self.drag_highlight:
            self.color = self.db.colors.Hops_UI_highlight_drag_color 

        elif self.primary:
            self.color = self.db.colors.Hops_UI_background_color
            
        else:
            self.color = self.db.colors.Hops_UI_cell_background_color

        # Render as a cell background
        if self.cell_bg:
            if self.db.prefs.ui.Hops_modal_cell_background:

                self.alter_dims()

                render_quad(quad=(
                    self.top_left, 
                    self.bottom_left, 
                    self.top_right, 
                    self.bottom_right), 
                    color=self.color, 
                    bevel_corners=True)

        # Render as a window background
        else:
            if self.db.prefs.ui.Hops_modal_background:
                render_quad(quad=(
                    self.top_left, 
                    self.bottom_left, 
                    self.top_right, 
                    self.bottom_right), 
                    color=self.color, 
                    bevel_corners=True)


    def alter_dims(self):
        
        if self.dims_override == (0, 0, 0, 0):
            return
        
        else:
            # dims_override = Left, Right, Top, Bottom


            width = self.bottom_right[0] - self.bottom_left[0]
            height = self.top_left[1] - self.bottom_left[1]
 
            left_offset = width * self.dims_override[0]
            right_offset = width * self.dims_override[1]
            top_offset = height * self.dims_override[2]
            bottom_offset = height * self.dims_override[3]

            self.bottom_left  = (self.bottom_left[0] + left_offset, self.bottom_left[1] + bottom_offset)
            self.bottom_right = (self.bottom_right[0] + right_offset, self.bottom_right[1] + bottom_offset)
            self.top_left     = (self.top_left[0] + left_offset, self.top_left[1] + top_offset)
            self.top_right    = (self.top_right[0] + right_offset, self.top_right[1] + top_offset)