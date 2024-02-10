import bpy

from bpy.types import PropertyGroup
from bpy.props import BoolProperty, IntProperty, FloatProperty

from ... utility import names


class hardflow(PropertyGroup):

    dot_size: IntProperty(
        name = 'Dot Size',
        description = 'Dot size',
        soft_min = 3,
        soft_max = 40,
        default = 5)

    dot_detect: IntProperty(
        name = 'Dot Detection',
        description = 'Dot detection size',
        soft_min = 1,
        soft_max = 30,
        default = 14)

    dot_side_offset: FloatProperty(
        name = 'Dot offset',
        description = 'Dot side offset',
        soft_min = 0.5,
        soft_max = 5.0,
        default = 1.9)

    dot_corner_offset: FloatProperty(
        name = 'Dot Corner offset',
        description = 'Dot corner offset',
        soft_min = 0.5,
        soft_max = 5.0,
        default = 1.5)

    display_corner: IntProperty(
        name = 'Dot Display Corner',
        description = 'Dot display corner',
        soft_min = 0,
        soft_max = 7,
        default = 2)

    dot_boolshape_fade_distance: FloatProperty(
        name = 'Boolshape Fade distance',
        description = 'Fade distance for boolshape dots',
        default = 2.5)

    display_smartshape: BoolProperty(
        name = 'Display Smartshape Row',
        description = 'Display Smartshape Row',
        default = True)

    display_modifiers: BoolProperty(
        name = 'Display Modifiers Row',
        description = 'Display Modifiers Row',
        default = True)

    display_misc: BoolProperty(
        name = 'Display Misc Row',
        description = 'Display Misc Row',
        default = True)

    display_text: BoolProperty(
        name = 'Display OnScreen Text',
        description = 'Display OnScreen Text',
        default = True)

    bc_notifications: BoolProperty(
        name = 'BC Notifications',
        description = """Boxcutter Assistive Notifications
        
        Display OnScreen Text for BoxCutter
        Intended to assist with notification display 
        
        """,
        default = False)

    display_text_size: IntProperty(
        name = 'Text size',
        description = 'Text size',
        soft_min = 1,
        soft_max = 40,
        default = 12)

    display_text_size_for_dots: IntProperty(
        name = 'Text size',
        description = 'Text size',
        soft_min = 1,
        soft_max = 40,
        default = 12)

    use_label_factor: BoolProperty(
        name = 'Use Label Factor',
        description = 'Use label scale factor for blender version 2.82 and greater.\n'
                      'Fixes issues with label size in the topbar for most screens.\n'
                      'Disable if the labels in the topbar are displaying incorrectly',
        default = True)

def label_row(path, prop, row, label=''):
    row.label(text=label if label else names[prop])
    row.prop(path, prop, text='')


def draw(preference, context, layout):

    label_row(preference.display, 'dot_size', layout.row(), 'Dot Size')
    label_row(preference.display, 'dot_detect', layout.row(), 'Dot Detection')
    label_row(preference.display, 'dot_side_offset', layout.row(), 'Dot side OffSet')
    label_row(preference.display, 'dot_corner_offset', layout.row(), 'Dot corner OffSet')
    label_row(preference.display, 'display_corner', layout.row(), 'Dot Display Corner')
    label_row(preference.display, 'display_smartshape', layout.row(), 'Display Smartshape Row')
    label_row(preference.display, 'display_modifiers', layout.row(), 'Display Modifiers Row')
    label_row(preference.display, 'display_misc', layout.row(), 'Display Misc Row')
    label_row(preference.display, 'display_text', layout.row(), 'Display Text in 3d')
    label_row(preference.display, 'display_text_size', layout.row(), 'Display Text Size')
    label_row(preference.display, 'display_text_size_for_dots', layout.row(), 'Display Dot Text Size')
    label_row(preference.display, 'use_label_factor', layout.row(), 'Fix Label Size')
