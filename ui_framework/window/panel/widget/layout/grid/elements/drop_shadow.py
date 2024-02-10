from .......graphics.draw import render_quad


class Drop_Shadow_Element():

    def __init__(self):

        # Global
        self.db = None

        # Dims
        self.top_left = (0, 0)
        self.top_right = (0, 0)
        self.bottom_left = (0, 0)
        self.bottom_right = (0, 0)

        # Element Props
        self.bevel = True


    def draw(self):
        
        if self.db.prefs.ui.Hops_modal_drop_shadow:

            # Prefs data
            color = self.db.colors.Hops_UI_dropshadow_color
            offset = self.db.prefs.ui.Hops_modal_drop_shadow_offset

            render_quad(quad=(
                (self.top_left[0]     + offset[0], self.top_left[1]     + offset[1]), 
                (self.bottom_left[0]  + offset[0], self.bottom_left[1]  + offset[1]), 
                (self.top_right[0]    + offset[0], self.top_right[1]    + offset[1]), 
                (self.bottom_right[0] + offset[0], self.bottom_right[1] + offset[1])), 
                color=color, 
                bevel_corners=True)