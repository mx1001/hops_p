import bpy

from mathutils import Vector

from bpy.types import PropertyGroup
from bpy.props import BoolProperty, FloatVectorProperty, FloatProperty

from ... utility import names, addon

class hops(PropertyGroup):

    wire: FloatVectorProperty(
        name = names['wire'],
        description = 'Color of the shape\'s wire',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.0, 0.0, 0.0, 0.33))

    show_shape_wire: FloatVectorProperty(
        name = names['show_shape_wire'],
        description = 'Color of the shape\'s wire when the object is to be shown',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.23, 0.7, 0.15, 0.33))

    dot2: FloatVectorProperty(
        name = 'Dot 2',
        description = 'Color of Dot 2',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.35, 1, 0.29, 0.9))

    dot3: FloatVectorProperty(
        name = 'Dot 3',
        description = 'Color of Dot 3',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (1, 0.133, 0.133, 0.9))

    dot4: FloatVectorProperty(
        name = 'Dot 4',
        description = 'Color of Dot 4',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (1, 0.9, 0.03, 0.9))

    dot5: FloatVectorProperty(
        name = 'Dot 5',
        description = 'Color of Dot 5',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.32, 0.67, 1, 0.9))

    dot6: FloatVectorProperty(
        name = 'Dot 5',
        description = 'Color of Dot 6',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.88, 0.19, 1, 0.9))

    dot7: FloatVectorProperty(
        name = 'Dot 5',
        description = 'Color of Dot 7',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (1, 0.57, 0.176, 0.9))

    displace_x: FloatVectorProperty(
        name = 'displace_x',
        description = 'Color of displace_x',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (1, 0.2, 0.322, 0.9))

    displace_y: FloatVectorProperty(
        name = 'displace_y',
        description = 'Color of displace_y',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.54, 0.83, 0, 0.9))

    displace_z: FloatVectorProperty(
        name = 'displace_z',
        description = 'Color of displace_z',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.157, 0.565, 1, 0.9))

    screw_x: FloatVectorProperty(
        name = 'screw_x',
        description = 'Color of screw_x',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.4, 1, 0.9, 0.9))

    screw_y: FloatVectorProperty(
        name = 'screw_y',
        description = 'Color of screw_y',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.4, 1, 0.9, 0.9))

    screw_z: FloatVectorProperty(
        name = 'screw_z',
        description = 'Color of screw_z',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.4, 1, 0.9, 0.9))

    solidify_x: FloatVectorProperty(
        name = 'solidify_x',
        description = 'Color of solidify_x',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.4, 1, 0.9, 0.9))

    solidify_y: FloatVectorProperty(
        name = 'solidify_y',
        description = 'Color of solidify_y',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.4, 1, 0.9, 0.9))

    solidify_z: FloatVectorProperty(
        name = 'solidify_z',
        description = 'Color of solidify_z',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.4, 1, 0.9, 0.9))

    solidify_c: FloatVectorProperty(
        name = 'solidify_c',
        description = 'Color of solidify_c',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.157, 0.565, 1, 0.9))

    array_x: FloatVectorProperty(
        name = 'array_x',
        description = 'Color of array_x',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.875, 0.832, 0, 0.9))

    array_y: FloatVectorProperty(
        name = 'array_y',
        description = 'Color of array_y',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.875, 0.832, 0, 0.9))

    array_z: FloatVectorProperty(
        name = 'array_z',
        description = 'Color of array_z',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.875, 0.832, 0, 0.9))

    simple_deform_x: FloatVectorProperty(
        name = 'simple_deform_x',
        description = 'Color of simple_deform_x',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.939, 0.236, 1, 0.9))

    simple_deform_y: FloatVectorProperty(
        name = 'simple_deform_y',
        description = 'Color of simple_deform_y',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.939, 0.236, 1, 0.9))

    simple_deform_z: FloatVectorProperty(
        name = 'simple_deform_z',
        description = 'Color of simple_deform_z',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.939, 0.236, 1, 0.9))

    wireframe_c: FloatVectorProperty(
        name = 'wireframe_c',
        description = 'Color of wireframe_c',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.939, 0.236, 1, 0.9))

    bevel_c: FloatVectorProperty(
        name = 'bevel_c',
        description = 'Color of bevel_c',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.4, 1, 0.9, 0.9))

    dot: FloatVectorProperty(
        name = names['dot'],
        description = 'Color of snapping points',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.4, 1, 0.9, 0.9))

    dot_highlight: FloatVectorProperty(
        name = names['dot_highlight'],
        description = 'Color of snapping points highlighted',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (1, 0.597, 0.133, 0.9))

    enable_tool_overlays: BoolProperty(
        name='Enable tool overlays',
        description='Enable tool overlays',
        default=True)

    Hops_text_color: FloatVectorProperty(
        name="",
        default=Vector((0.6, 0.6, 0.6, 0.9)),
        size=4,
        min=0, max=1,
        subtype='COLOR')

    Hops_text2_color: FloatVectorProperty(
        name="",
        default=Vector((0.6, 0.6, 0.6, 0.9)),
        size=4,
        min=0, max=1,
        subtype='COLOR')

    Hops_border_color: FloatVectorProperty(
        name="",
        default=Vector((0.235, 0.235, 0.235, 0.8)),
        size=4,
        min=0, max=1,
        subtype='COLOR'
        )

    Hops_border2_color: FloatVectorProperty(
        name="",
        default=Vector((0.692, 0.298, 0.137, 0.718)),
        size=4,
        min=0, max=1,
        subtype='COLOR'
        )

    Hops_logo_color: FloatVectorProperty(
        name="",
        default=(0.448, 0.448, 0.448, 0.1),
        size=4,
        min=0, max=1,
        subtype='COLOR'
        )

    Hops_logo_color_csharp: FloatVectorProperty(
        name="",
        default=(1, 0.597, 0.133, 0.9),
        size=4,
        min=0, max=1,
        subtype='COLOR'
        )

    Hops_logo_color_cstep: FloatVectorProperty(
        name="",
        default=(0.29, 0.52, 1.0, 0.9),
        size=4,
        min=0, max=1,
        subtype='COLOR'
        )

    Hops_logo_color_boolshape2: FloatVectorProperty(
        name="",
        default=(1, 0.133, 0.133, 0.53),
        size=4,
        min=0, max=1,
        subtype='COLOR'
        )

    Hops_logo_color_boolshape: FloatVectorProperty(
        name="",
        default=(0.35, 1, 0.29, 0.53),
        size=4,
        min=0, max=1,
        subtype='COLOR'
        )

    Hops_hud_color: FloatVectorProperty(
        name="",
        default=(0.17, 0.17, 0.17, 1),
        size=4,
        min=0, max=1,
        subtype='COLOR'
        )

    Hops_hud_text_color: FloatVectorProperty(
        name="",
        default=(0.831, 0.831, 0.831, 1),
        size=4,
        min=0, max=1,
        subtype='COLOR'
        )

    Hops_hud_help_color: FloatVectorProperty(
        name="",
        default=(0.250, 0.750, 1, 0.7),
        size=4,
        min=0, max=1,
        subtype='COLOR'
        )

    Hops_display_logo: BoolProperty(name="Display Logo", default=False)

    Bool_Dots_Text: BoolProperty(name="Display Dots Text", default=True)

    Hops_logo_size: FloatProperty(
        name="HardOps Indicator Size",
        description="BoxCutter indicator size",
        default=2, min=0, max=100)

    Hops_logo_x_position: FloatProperty(
        name="HardOps Indicator X Position",
        description="BoxCutter Indicator X Position",
        default=-203)

    Hops_logo_y_position: FloatProperty(
        name="HardOps Indicator Y Position",
        description="BoxCutter Indicator Y Position",
        default=19)

    Hops_mirror_modal_scale: FloatProperty(
        name="Modal Mirror Operators Scale",
        description="Modal Mirror Operators Scale",
        default=5, min=0.1, max=100
        )

    Hops_mirror_modal_sides_scale: FloatProperty(
        name="Modal Mirror Operators Sides Scale",
        description="Modal Mirror Operators Sides Scale",
        default=0.20, min=0.01, max=0.99)

    expand: BoolProperty(name="expand color options", default=False)

    #UI SYSTEM
    Hops_UI_text_color: FloatVectorProperty(
        name="",
        default=(1, 1, 1, 1),
        size=4,
        min=0, max=1,
        subtype='COLOR'
        )

    Hops_UI_secondary_text_color: FloatVectorProperty(
        name="",
        default=(1, 1, 1, 1),
        size=4,
        min=0, max=1,
        subtype='COLOR'
        )

    Hops_UI_mods_highlight_color: FloatVectorProperty(
        name="",
        default=(1, 1, 0, 1),
        size=4,
        min=0, max=1,
        subtype='COLOR'
        )

    Hops_UI_highlight_color: FloatVectorProperty(
        name="",
        default=(0, 0, 1, .25),
        size=4,
        min=0, max=1,
        subtype='COLOR'
        )

    Hops_UI_highlight_drag_color: FloatVectorProperty(
        name="",
        default=(1, 0, 0, .25),
        size=4,
        min=0, max=1,
        subtype='COLOR'
        )

    Hops_UI_background_color: FloatVectorProperty(
        name="",
        default=(.75, .75, .75, 0),
        size=4,
        min=0, max=1,
        subtype='COLOR'
        )

    Hops_UI_cell_background_color: FloatVectorProperty(
        name="",
        default=(.901, .314, .302, .2),
        size=4,
        min=0, max=1,
        subtype='COLOR',
        description = "Background color for modals"
        )

    Hops_UI_dropshadow_color: FloatVectorProperty(
        name="",
        default=(0, 0, 0, .15),
        size=4,
        min=0, max=1,
        subtype='COLOR'
        )

    Hops_UI_border_color: FloatVectorProperty(
        name="",
        default=(0.2, 0.2, 0.2, .7),
        size=4,
        min=0, max=1,
        subtype='COLOR'
        )

    Hops_UI_mouse_over_color: FloatVectorProperty(
        name="",
        default=(0, 0, .25, .5),
        size=4,
        min=0, max=1,
        subtype='COLOR'
        )

    Hops_UI_text_highlight_color: FloatVectorProperty(
        name="",
        default=(1, 1, 0, 1),
        size=4,
        min=0, max=1,
        subtype='COLOR'
        )


def header_row(row, prop, label='', emboss=False):
    preference = addon.preference()
    icon = 'DISCLOSURE_TRI_RIGHT' if not getattr(preference.color, prop) else 'DISCLOSURE_TRI_DOWN'
    row.alignment = 'LEFT'
    row.prop(preference.color, prop, text='', emboss=emboss)

    sub = row.row(align=True)
    sub.scale_x = 0.25
    sub.prop(preference.color, prop, text='', icon=icon, emboss=emboss)
    row.prop(preference.color, prop, text=F'{label}', emboss=emboss)

    sub = row.row(align=True)
    sub.scale_x = 0.75
    sub.prop(preference.color, prop, text=' ', icon='BLANK1', emboss=emboss)


def label_row(path, prop, row, label=''):
    row.label(text=label if label else names[prop])
    row.prop(path, prop, text='')


def draw(preference, context, layout):
    layout.label(text='Hardops Drawing:')

    label_row(preference.color, 'enable_tool_overlays', layout.row(), label='Enable Overlays')
    layout.separator()
    layout.separator()
    layout.label(text='UI System:')

    #Modal framework related
    # Text
    label_row(preference.color, 'Hops_UI_cell_background_color', layout.row(), label='Cell Background Color')
    label_row(preference.color, 'Hops_UI_text_color', layout.row(), label='Main Text Color')
    label_row(preference.color, 'Hops_UI_secondary_text_color', layout.row(), label='Secoundary Text Color')
    label_row(preference.color, 'Hops_UI_mods_highlight_color', layout.row(), label='Text Highlight')
    #label_row(preference.color, 'Hops_UI_text_highlight_color', layout.row(), label='Text Highlight')
    # Backgrounds
    label_row(preference.color, 'Hops_UI_background_color', layout.row(), label='Background Color')
    #label_row(preference.color, 'Hops_UI_cell_background_color', layout.row(), label='Cell Background Color')
    label_row(preference.color, 'Hops_UI_highlight_color', layout.row(), label='Highlight Color')
    label_row(preference.color, 'Hops_UI_dropshadow_color', layout.row(), label='Drop Shadow Color')
    # Misc
    label_row(preference.color, 'Hops_UI_border_color', layout.row(), label='Border Color')
    label_row(preference.color, 'Hops_UI_mouse_over_color', layout.row(), label='Hover Color')
    label_row(preference.color, 'Hops_UI_highlight_drag_color', layout.row(), label='Drag Color')

    #layout.label(text='Modal:')
    #label_row(preference.color, 'Hops_text_color', layout.row(), label='Main Text Color')
    #label_row(preference.color, 'Hops_text2_color', layout.row(), label='Secoundary Text Color')
    #label_row(preference.color, 'Hops_border_color', layout.row(), label='Border Color')
    #label_row(preference.color, 'Hops_border2_color', layout.row(), label='Secondary Border Color')
    #layout.separator()
    layout.separator()
    layout.label(text='Logo:')
    label_row(preference.color, 'Hops_display_logo', layout.row(), label='Display Logo')
    label_row(preference.color, 'Hops_logo_color', layout.row(), label='Logo Color')
    #label_row(preference.color, 'Hops_logo_color_csharp', layout.row(), label='Csharp Color')
    #label_row(preference.color, 'Hops_logo_color_cstep', layout.row(), label='Cstep Color')
    label_row(preference.color, 'Hops_logo_color_boolshape', layout.row(), label='Boolshape Color')
    #label_row(preference.color, 'Hops_logo_color_boolshape2', layout.row(), label='Boolshape2 Color')
    label_row(preference.color, 'Hops_logo_size', layout.row(), label='Logo Size')
    label_row(preference.color, 'Hops_logo_x_position', layout.row(), label='Logo X Position')
    label_row(preference.color, 'Hops_logo_y_position', layout.row(), label='Logo Y Position')
    layout.separator()
    layout.separator()
    layout.label(text='Hud:')
    #label_row(preference.color, 'Hops_hud_color', layout.row(), label='Hud Color')
    #label_row(preference.color, 'Hops_hud_text_color', layout.row(), label='Hud Text Color')
    #label_row(preference.color, 'Hops_hud_help_color', layout.row(), label='Hud Help Color')
    layout.separator()
    layout.separator()
    layout.label(text='Gizmo')
    label_row(preference.color, 'Hops_mirror_modal_scale', layout.row(), label='modal mirror scale')
    label_row(preference.color, 'Hops_mirror_modal_sides_scale', layout.row(), label='modal mirror sides scale')

    layout.separator()
    layout.separator()
    layout.label(text='Active tool:')
    label_row(preference.color, 'wire', layout.row())
    label_row(preference.color, 'show_shape_wire', layout.row())

    layout.separator()
    header_row(layout.row(align=True), 'expand', label='Dots colors')
    if preference.color.expand:
        layout.separator()
        label_row(preference.color, 'Bool_Dots_Text', layout.row(), label='Display Dots Text')
        layout.separator()
        layout.label(text='     Basic Dots')
        label_row(preference.color, 'dot', layout.row())
        label_row(preference.color, 'dot_highlight', layout.row())
        layout.label(text='     Displace')
        label_row(preference.color, 'displace_x', layout.row(), label='Displace X')
        label_row(preference.color, 'displace_y', layout.row(), label='Displace Y')
        label_row(preference.color, 'displace_z', layout.row(), label='Displace Z')
        layout.label(text='     Screw')
        label_row(preference.color, 'screw_x', layout.row(), label='Screw X')
        label_row(preference.color, 'screw_y', layout.row(), label='Screw Y')
        label_row(preference.color, 'screw_z', layout.row(), label='Screw Z')
        layout.label(text='     Solidify')
        label_row(preference.color, 'solidify_x', layout.row(), label='Solidify X')
        label_row(preference.color, 'solidify_y', layout.row(), label='Solidify Y')
        label_row(preference.color, 'solidify_z', layout.row(), label='Solidify Z')
        label_row(preference.color, 'solidify_c', layout.row(), label='Solidify C')
        layout.label(text='     Array')
        label_row(preference.color, 'array_x', layout.row(), label='Array X')
        label_row(preference.color, 'array_y', layout.row(), label='Array Y')
        label_row(preference.color, 'array_z', layout.row(), label='Array Z')
        layout.label(text='     Simple Deform')
        label_row(preference.color, 'simple_deform_x', layout.row(), label='Deform X')
        label_row(preference.color, 'simple_deform_y', layout.row(), label='Deform Y')
        label_row(preference.color, 'simple_deform_z', layout.row(), label='Deform Z')
        layout.label(text='     Wireframe')
        label_row(preference.color, 'wireframe_c', layout.row(), label='Wireframe')
        layout.label(text='     Bevel')
        label_row(preference.color, 'bevel_c', layout.row(), label='Bevel')
        layout.label(text='     Booleandots')
        label_row(preference.color, 'dot2', layout.row(), label='Union')
        label_row(preference.color, 'dot3', layout.row(), label='Difference')
        label_row(preference.color, 'dot4', layout.row(), label='Slash')
        label_row(preference.color, 'dot5', layout.row(), label='Knife')
        label_row(preference.color, 'dot6', layout.row(), label='Inset')
        label_row(preference.color, 'dot7', layout.row(), label='Intersect')
