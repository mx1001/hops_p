import bpy

from bpy.types import PropertyGroup
from bpy.props import BoolProperty, IntProperty, FloatProperty

from ... utility import names


class hardflow(PropertyGroup):

    quick_execute: BoolProperty(
        name = names['quick_execute'],
        description = 'Quickly execute cuts on release',
        default = False)

    use_dpi_factor: BoolProperty(
        name = 'Use DPI Factor',
        description = ('Use DPI factoring when drawing and choosing dimensions.\n'
                       'Note: Having this enabled can cause behavior issues on some machines'),
        default = True)

    display_gizmo: BoolProperty(
        name ='Display Gizmo',
        description = 'Hide gizmo on Ctrl',
        default = True)

    display_dots: BoolProperty(
        name ='Display Dots',
        description = 'Display dots on Ctrl',
        default = True)

    display_operators: BoolProperty(
        name ='Display Operators',
        description = 'Display Operators on Ctrl',
        default = True)

    display_boolshapes: BoolProperty(
        name ='Display Boolshapes',
        description = 'Display boolshapes on Ctrl',
        default = True)

    display_boolshapes_for_all: BoolProperty(
        name ='Display All Boolshapes Dots',
        description = 'Display boolshapes on Ctrl',
        default = False)

    add_mirror_to_boolshapes: BoolProperty(
        name ='Add Mirror to Boolshapes',
        description = 'Add Mirror to Boolshapes',
        default = True)

    add_WN_to_boolshapes: BoolProperty(
        name ='Add WN to Boolshapes',
        description = 'Add WN to Boolshapes',
        default = True)

    cursor_boolshapes: BoolProperty(
        name ='Orient Boolshapes to Cursor',
        description = 'Orient Boolshapes to Cursor',
        default = False)
    
    mat_viewport: BoolProperty(
        name ='Blank Mat use same viewport mat',
        description = """Vieport Mat to blank mat
        
        **Material Scroll only**

        """,
        default = False)

def label_row(path, prop, row, label=''):
    row.label(text=label if label else names[prop])
    row.prop(path, prop, text='')


def draw(preference, context, layout):
    label_row(preference.behavior, 'quick_execute', layout.row())
    label_row(preference.behavior, 'display_gizmo', layout.row())
    label_row(preference.behavior, 'display_dots', layout.row())
    label_row(preference.behavior, 'display_operators', layout.row())
    label_row(preference.behavior, 'display_boolshapes', layout.row())
    label_row(preference.behavior, 'display_boolshapes_for_all', layout.row())
    label_row(preference.behavior, 'add_mirror_to_boolshapes', layout.row())
    label_row(preference.behavior, 'add_WN_to_boolshapes', layout.row())
    label_row(preference.behavior, 'cursor_boolshapes', layout.row())
