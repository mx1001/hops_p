from bpy_extras.image_utils import load_image

from ... icons import get_icon_id, icons, icons_directory


def load_image_file(filename=""):
    '''Return the loaded image.'''

    return load_image(filename + ".png", dirname=icons_directory)