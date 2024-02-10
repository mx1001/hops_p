import os

import bpy

name = __name__.partition('.')[0]

icons = {}


class path:


    def __new__(self):
        return os.path.abspath(os.path.join(__file__, '..', '..', '..'))


    def icons():
        return os.path.join(path(), 'icons')


def preference():
    preference = bpy.context.preferences.addons[name].preferences

    return preference


def bc():
    wm = bpy.context.window_manager

    if hasattr(wm, 'bc'):
        return bpy.context.preferences.addons[wm.bc.addon].preferences

    return False


def kitops():
    wm = bpy.context.window_manager

    if hasattr(wm, 'kitops'):
        return bpy.context.preferences.addons[wm.kitops.addon].preferences

    return False


def powersave():
    wm = bpy.context.window_manager

    if hasattr(wm, 'powersave'):
        return bpy.context.preferences.addons[wm.powersave.addon].preferences

    return False
