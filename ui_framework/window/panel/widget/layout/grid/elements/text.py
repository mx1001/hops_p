from ....... graphics.draw import render_text
from ....... utils.geo import get_blf_text_dims

class Text_Element():

    def __init__(self):

        # Global
        self.db = None

        # Dims
        self.top_left = (0, 0)
        self.top_right = (0, 0)
        self.bottom_left = (0, 0)
        self.bottom_right = (0, 0)

        # Element Props
        self.text = ""
        self.centered = True
        self.target_size = 12
        self.color_select = 0
        self.force_fit_text = True
        self.padding = 6
        self.bottom_align = False
        self.y_offset = 0

        # Overrides
        self.set_y_external = False
        self.external_y = 0


    def draw(self):

        temp_txt_size = self.target_size
        txt_dims = get_blf_text_dims(self.text, temp_txt_size)


        cell_width = self.bottom_right[0] - self.bottom_left[0]
        cell_height = self.top_left[1] - self.bottom_left[1]

        if self.force_fit_text:

            # Prevent infinite loops : Make sure the cell isnt smaller than 10 px
            execute = True
            if cell_height <= 2 or cell_width <= 2:
                execute = False

            #If the text is to tall or to short
            if txt_dims[0] >= cell_width - self.padding or txt_dims[1] >= cell_height - self.padding:
                
                cycle_limit = 15
                cycle_count = 0

                while execute == True:

                    if cycle_count >= cycle_limit:
                        execute = False
                        break

                    temp_txt_size -= 1

                    if temp_txt_size <= 2:
                        execute = False
                        break    

                    txt_dims = get_blf_text_dims(self.text, temp_txt_size)

                    if txt_dims[0] >= cell_width - self.padding or txt_dims[1] >= cell_height - self.padding:
                        continue
                    else:
                        execute = False
                        break

                    cycle_count += 1

        position = (self.bottom_left[0] + self.padding, (self.bottom_left[1] + (cell_height * .5)) - txt_dims[1] * .5)

        if self.centered:

            position = (
                 round(self.bottom_left[0] + (cell_width * .5) - (txt_dims[0] * .5)),
                 round(self.bottom_left[1] + (cell_height * .5) - (txt_dims[1] * .5)))

        # Override
        if self.set_y_external:
            # Set from fast UI to make sure all the text is the same height
            position = (position[0], self.external_y)

        if self.bottom_align:
            position = (position[0], self.bottom_left[1])

        # Finish Position
        if self.y_offset != 0:
            height = self.top_left[1] - self.bottom_left[1]
            top_offset = height * self.y_offset
            position = (position[0], self.top_left[1] + top_offset)

        color = (0,0,0,0)

        if self.color_select == 0:
            color = self.db.colors.Hops_UI_text_color
        elif self.color_select == 1:
            color = self.db.colors.Hops_UI_secondary_text_color
        elif self.color_select == 2:
            color = self.db.colors.Hops_UI_mods_highlight_color
            
        render_text(text=self.text, position=position, size=temp_txt_size, color=color)