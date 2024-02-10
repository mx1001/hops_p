from .......graphics.draw import render_image
from bpy.types import Image

class Image_Element():

    def __init__(self):

        # Global
        self.db = None

        # Dims
        self.top_left = (0, 0)
        self.top_right = (0, 0)
        self.bottom_left = (0, 0)
        self.bottom_right = (0, 0)

        # Element Props
        self.image = None
        self.scale = 1
        self.force_fit = False
        self.padding = 4
        self.maximize = False


    def draw(self):
        
        if self.db.ui_event.images_remove == True:
            self.image = None


        # Bottom Left, Bottom Right, Top Right, Top Left
        if self.image != None and type(self.image) == Image:
            try:
                verts = None

                # Image will be the size of the cell
                if self.force_fit:
                    verts = (
                        self.bottom_left,
                        self.bottom_right,
                        self.top_right,
                        self.top_left)

                else:

                    if self.maximize:
                        self.padding = 0

                    # Image dimensions
                    i_dims_x = self.image.size[0]
                    i_dims_y = self.image.size[1]

                    # Apply scale
                    i_dims_x *= self.scale
                    i_dims_y *= self.scale

                    # Cell width and height
                    width = self.bottom_right[0] - self.bottom_left[0]
                    height = self.top_left[1] - self.bottom_left[1]

                    # Clamp size of iamge to padding
                    if i_dims_x > width - self.padding:
                        i_dims_x = width - self.padding
                        i_dims_y = width - self.padding

                    if i_dims_y > height - self.padding:
                        i_dims_x = height - self.padding
                        i_dims_y = height - self.padding

                    # Center the image in the cell
                    x_pad = (width - i_dims_x) * .5
                    y_pad = (height - i_dims_y) * .5

                    # Bottom left of the image
                    bottom_left = (
                        x_pad + self.bottom_left[0], 
                        y_pad + self.bottom_left[1])

                    # Image verts
                    verts = (
                        bottom_left,
                        (bottom_left[0] + i_dims_x, bottom_left[1]),
                        (bottom_left[0] + i_dims_x, bottom_left[1] + i_dims_y),
                        (bottom_left[0], bottom_left[1] + i_dims_y))

                render_image(self.image, verts)

            except:
                pass