

def is_mouse_in_quad(quad=((0,1), (0,0), (1,1), (0,1)), mouse_pos=(0,0), tolerance=0):
    '''Top Left, Bottom Left, Top Right, Bottom Right'''

    if mouse_pos[0] >= quad[0][0] - tolerance and mouse_pos[0] <= quad[2][0] + tolerance:
        if mouse_pos[1] >= quad[1][1] - tolerance and mouse_pos[1] <= quad[2][1] + tolerance:
            return True

    return False

