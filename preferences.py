import os
import bpy


def get_preferences():
    name = get_addon_name()
    return bpy.context.preferences.addons[name].preferences


def get_addon_name():
    return os.path.basename(os.path.dirname(os.path.realpath(__file__)))
