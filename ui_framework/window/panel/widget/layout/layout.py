

class Layout():

    def __init__(self, db):

        self.rows = []
        self.db = db
        self.max_cell_height = 0


    def setup(self, bottom_left=(0,0), bottom_right=(0,0), top_left=(0,0), top_right=(0,0)):
        '''Setup all the cells.'''

        layout_height = top_right[1] - bottom_right[1]
        layout_width = bottom_right[0] - bottom_left[0]

        row_offset = 0
        col_offset = 0

        for row in self.rows:
            row_height = (layout_height * row.height_percent) * .01
            col_offset = 0

            for column in row.columns:
                column_width = (layout_width * column.width_percent) * .01

                cell_index = 0

                for cell in column.cells:
                    
                    # More than one cell in the column
                    split = len(column.cells)
                    if split > 1:

                        height_offset = (row_height / split) * cell_index
                        cell_height = row_height / split

                        # Cell Dims
                        cell.top_left    = (bottom_left[0] + col_offset, bottom_left[1] + height_offset + row_offset + cell_height)
                        cell.bottom_left = (bottom_left[0] + col_offset, bottom_left[1] + height_offset + row_offset)

                        cell.top_right    = (bottom_left[0] + col_offset + column_width, bottom_left[1] + height_offset + row_offset + cell_height)
                        cell.bottom_right = (bottom_left[0] + col_offset + column_width, bottom_right[1] + height_offset + row_offset)

                    else:

                        # Cell Dims
                        cell.top_left    = (bottom_left[0] + col_offset, bottom_left[1] + row_height + row_offset)
                        cell.bottom_left = (bottom_left[0] + col_offset, bottom_left[1] + row_offset)

                        cell.top_right    = (bottom_left[0] + col_offset + column_width, bottom_left[1] + row_height + row_offset)
                        cell.bottom_right = (bottom_left[0] + col_offset + column_width, bottom_right[1] + row_offset)

                    cell_index += 1
                    
                # X Offset
                col_offset += column_width

            # Y Offset
            row_offset += row_height


    def event(self):

        for row in self.rows:
            for column in row.columns:
                for cell in column.cells:
                    cell.event()


    def draw(self):

        for row in self.rows:
            for column in row.columns:
                for cell in column.cells:
                    cell.draw()