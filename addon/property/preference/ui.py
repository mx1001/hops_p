import bpy
from mathutils import Vector
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, FloatVectorProperty, FloatProperty, EnumProperty, IntProperty, StringProperty

from ... utility import names, addon
from ... panel import button
from .... ui.Panels import cutting_material
from .... preferences import get_preferences


def update_hops_panels(props, context):
    panels = (button.HOPS_PT_Button, cutting_material.HOPS_PT_material_hops)
    category = get_preferences().ui.Hops_panel_location
    region = 'UI' if category else 'HEADER'

    for panel in panels:
        panel.bl_category = category
        panel.bl_region_type = region
        bpy.utils.unregister_class(panel)
        bpy.utils.register_class(panel)


class hops(PropertyGroup):

    use_dpi_factoring: BoolProperty(
        name = 'Popup Dpi Factoring',
        description = 'Automatically determine UI scale for popups',
        default = True)

    Hops_modal_scale: FloatProperty(
        name="Modal Operators Scale",
        description="Modal Operators Scale",
        default=1, min=0.001, max=100)

    expanded_menu: BoolProperty(
        name="Show Q Menus Expanded",
        default=True,
        description="""Q Menu Delivery Format
        
        Show as a list or stacked.
        List - items stacked vertically
        Stacked - items stack horizontally (new)
        
        """)

    use_helper_popup: BoolProperty(
        name="Use Helper as Pop-up",
        default=False,
        description="Use helper pop-up instead of OK dialogue")

    Hops_helper_width: IntProperty(
        name="Helper width",
        default=350,
        min=100,
        description="Helper width")

    use_bevel_helper_popup: BoolProperty(
        name="Use Bevel Helper as Pop-up",
        default=True,
        description="Use bevel helper pop-up instead of OK dialogue")

    use_kitops_popup: BoolProperty(
        name="Use KITOPS as Pop-up",
        default=True,
        description="Use KITOPS pop-up instead of OK dialogue")

    #################
    # UI Framework
    #################

    Hops_auto_hide_n_panel: BoolProperty(
        name="Auto Hide N-Panel",
        default=True,
        description="Auto Hide N-Panel during Fast UI")

    Hops_auto_hide_t_panel: BoolProperty(
        name="Auto Hide T-Panel",
        default=False,
        description="Auto Hide T-Panel during Fast UI")

    Hops_warp_on: BoolProperty(
        name="Activates warp on or off",
        default=True,
        description="Utilizes custom warp for Fast UI")

    Hops_warp_mode: BoolProperty(
        name="Custom Warp",
        default=False,
        description="Activates custom warp")

    Hops_warp_border_display_style: EnumProperty(
        name="Display Style",
        default='CORNERS',
        items=[("BORDER", "Border", ""),
               ("CORNERS", "Corners", "")])

    Hops_warp_line_length: IntProperty(
        name="Display line length",
        default=64,
        min=1,
        max=125,
        description="Display line length")

    Hops_warp_line_width: IntProperty(
        name="Display line width",
        default=1,
        min=1,
        max=20,
        description="Display line width")

    Hops_warp_border_display: BoolProperty(
        name="Cursor warp border",
        default=True,
        description="Display custom padded line for Fast UI")

    Hops_warp_mode_padding: IntProperty(
        name="Cursor warp padding for modals",
        default=75,
        min=0,
        max=125,
        description="Window Padding for 3d view")

    Hops_modal_size: FloatProperty(
        name="Modal Operators UI size",
        description="Modal Operators UI size",
        default=1, min=0.25, max=2)

    presets = [
        ("preset_A", "Preset A", ""),
        ("preset_B", "Preset B", "")]

    Hops_modal_presets: EnumProperty(
        name="Presets",
        default='preset_A',
        items=presets)

    Hops_modal_background: BoolProperty(
        name="Display background",
        default=True,
        description="Does the modal UI display a background")

    Hops_modal_drop_shadow: BoolProperty(
        name="Display drop shadow",
        default=True,
        description="Does the modal UI display a drop shadow")

    Hops_modal_drop_shadow_offset: FloatVectorProperty(
        name="Drop shadow offset",
        description="Offset the drop shadow",
        size=2,
        default=(5,-5),
        min=-20,
        max=20)

    Hops_modal_cell_background: BoolProperty(
        name="Display cell background",
        default=True,
        description="Does the modal UI display backgrounds in cell")

    Hops_modal_cell_border: BoolProperty(
        name="Display cell border",
        default=True,
        description="Does the modal UI display borders around the cell")

    # Main Window Props
    Hops_modal_main_window_bottom_left: FloatVectorProperty(
        name="Main Window Bottom Left",
        description="Sets the bottom left corner of the main window",
        size=2,
        default=(60,30),
        min=0)

    Hops_modal_main_window_scale: FloatVectorProperty(
        name="Main Window Scale",
        description="Sets the scale of the main window",
        size=2,
        default=(250,100),
        min=100)

    # Mods Window Props
    Hops_modal_mods_window_bottom_left: FloatVectorProperty(
        name="Modifiers Window Bottom Left",
        description="Sets the bottom left corner of the modifiers window",
        size=2,
        default=(300,30),
        min=0)

    Hops_modal_mods_window_scale: FloatVectorProperty(
        name="Mods Window Scale",
        description="Sets the scale of the mods window",
        size=2,
        default=(250,100),
        min=50)

    # Help Window Props
    Hops_modal_help_window_bottom_left: FloatVectorProperty(
        name="Help Window Bottom Left",
        description="Sets the bottom left corner of the help window",
        size=2,
        default=(20,30),
        min=0)

    Hops_modal_help_window_scale: FloatVectorProperty(
        name="Help Window Scale",
        description="Sets the scale of the help window",
        size=2,
        default=(250,100),
        min=100)

    # Kit Ops Window Props
    Hops_modal_kit_ops_window_bottom_left: FloatVectorProperty(
        name="Kit Ops Window Bottom Left",
        description="Sets the bottom left corner of the kit ops window",
        size=2,
        default=(20,30),
        min=0)

    Hops_modal_kit_ops_window_scale: FloatVectorProperty(
        name="Kit Ops Window Scale",
        description="Sets the scale of the kit ops window",
        size=2,
        default=(375,350),
        min=100)

    Hops_modal_kit_ops_display_count: IntProperty(
        name="Kit Ops Display Count",
        default=2,
        min=1,
        max=5,
        description="Sets the display count for kit ops window")


    asset_loader_opts = [
        ("KO", "Kit Ops", ""),
        ("DM", "Decal Machine", ""),
        ("PL", "Power Link", "")]

    Hops_asset_loader_window: EnumProperty(
        name="LoaderOpts",
        default='KO',
        items=asset_loader_opts)

    # Pizza Ops Window Props
    Hops_modal_pizza_ops_window_bottom_left: FloatVectorProperty(
        name="Pizza Ops Window Bottom Left",
        description="Sets the bottom left corner of the pizza ops window",
        size=2,
        default=(20,30),
        min=0)

    Hops_modal_pizza_ops_window_scale: FloatVectorProperty(
        name="Pizza Ops Window Scale",
        description="Sets the scale of the pizza ops window",
        size=2,
        default=(275,350),
        min=100)

    Hops_modal_pizza_ops_display_count: IntProperty(
        name="Pizza Ops Display Count",
        default=2,
        min=1,
        max=5,
        description="Sets the display count for pizza ops window")

    # Sclupt Window Props
    Hops_modal_sculpt_ops_window_bottom_left: FloatVectorProperty(
        name="Sculpt Ops Window Bottom Left",
        description="Sets the bottom left corner of the sculpt ops window",
        size=2,
        default=(20,30),
        min=0)

    Hops_modal_sculpt_ops_window_scale: FloatVectorProperty(
        name="Sculpt Ops Window Scale",
        description="Sets the scale of the sculpt ops window",
        size=2,
        default=(275,350),
        min=100)

    # Fast UI
    Hops_modal_auto_show_mods: BoolProperty(
        name="Show Mods when modal starts",
        default=True,
        description="Show Mods when modal starts")

    Hops_modal_auto_show_help: BoolProperty(
        name="Show Help when modal starts",
        default=False,
        description="Show Help when modal starts")

    Hops_modal_mods_left_open: BoolProperty(
        name="Show Mods if it was left open",
        default=False,
        description="Show Mods if it was left open")

    Hops_modal_help_left_open: BoolProperty(
        name="Show Help if it was left open",
        default=False,
        description="Show Help if it was left open")

    Hops_modal_mods_show_label: BoolProperty(
        name="Show Mods label in fast UI",
        default=False,
        description="Show Mods label in fast UI")

    Hops_modal_help_show_label: BoolProperty(
        name="Show Help label in fast UI",
        default=True,
        description="Show Help label in fast UI")

    Hops_modal_mods_visible: BoolProperty(
        name="Mods show window",
        default=False,
        description="Dispaly the window")

    Hops_modal_help_visible: BoolProperty(
        name="Help show window",
        default=False,
        description="Dispaly the window")

    Hops_modal_fast_ui_loc_options: IntProperty(
        name="Main banner location options.\n \
             1 - bottom of the screen.\n \
             2 - follow mouse.\n \
             3 - stick on mouse initial position.",
        default=1,
        min=1,
        max=3,
        description="Main banner location options.")

    Hops_material_count: IntProperty(
        name="Material List Count",
        default=20,
        min=5,
        max=100,
        description="Material list count per section")

    Hops_modal_mod_count_fast_ui: IntProperty(
        name="Mod count to show for fast UI",
        default=30,
        min=1,
        max=60,
        description="How many mods to show in mods list for fast ui.")

    Hops_modal_fast_ui_padding: IntProperty(
        name="Panel offset from viewport sides.",
        default=30,
        min=0,
        max=60,
        description="Panel offset from viewport sides.")

    Hops_modal_fast_ui_mods_offset: FloatVectorProperty(
        name="Fast UI Mods Offset",
        description="Fast UI Mods Offset",
        size=2,
        default=(0,0))

    Hops_modal_fast_ui_mods_size: FloatProperty(
        name="Fast UI Mods Size",
        description="Fast UI Mods Size",
        default=1, min=0.25, max=1)

    Hops_modal_fast_ui_help_offset: FloatVectorProperty(
        name="Fast UI Help Offset",
        description="Fast UI Help Offset",
        size=2,
        default=(0,0))

    Hops_modal_fast_ui_help_size: FloatProperty(
        name="Fast UI Help Size",
        description="Fast UI Help Size",
        default=1, min=0.25, max=1)

    Hops_modal_fast_ui_main_y_offset: FloatProperty(
        name="Fast UI Main Y Offset",
        description="Fast UI Main Y Offset",
        default=0, min=0, max=250)

    # Fades
    Hops_modal_fade: FloatProperty(
        name="Modal Fade Time",
        description="Modal Fade Time",
        default=.01, min=0.001, max=3)

    Hops_modal_fade_in: FloatProperty(
        name="Modal Fade In Time",
        description="Modal Fade In Time",
        default=.001, min=0.001, max=1)

    Hops_operator_fade: FloatProperty(
        name="Operator Fade Time",
        description="Operator Fade Time",
        default=0.5, min=0, max=6)

    # Operator UI
    Hops_operator_ui_offset: FloatVectorProperty(
        name="Hops operator UI offset",
        description="Hops operator UI offset",
        size=2,
        default=(0,60))

    Hops_operator_display_time: FloatProperty(
        name="Operator Display Time",
        description="Operator Display Time",
        default=3, min=0.25, max=16)

    Hops_operator_display: BoolProperty(
        name="Operator Display",
        default=True,
        description="Display text stats for operators")

    Hops_extra_info: BoolProperty(
        name="Extra Info Display",
        default=True,
        description="Display Extra info intended for guidance")

    Hops_operator_draw_bg: BoolProperty(
        name="Operator BG Draw",
        description="Operator BG Draw",
        default=True)

    Hops_operator_draw_border: BoolProperty(
        name="Operator BG Draw",
        description="Operator BG Draw",
        default=True)

    Hops_operator_border_size: FloatProperty(
        name="Operator Border Size",
        description="Operator Border Size",
        default=0.5, min=0.001, max=10)

    # N panel
    Hops_panel_location: StringProperty(
        name="HardOps panel category",
        description="HardOps panel category",
        default="HardOps",
        update = update_hops_panels)

    Hops_FastUI_expand: BoolProperty(name="expand Fast UI options", default=False)
    Hops_OperatorUI_expand: BoolProperty(name="expand Operator UI options", default=False)
    Hops_hopsUI_expand: BoolProperty(name="expand Fast UI options", default=False)
    Hops_Display_expand: BoolProperty(name="expand Operator UI options", default=False)
    Hops_Fade_expand: BoolProperty(name="expand Fast UI options", default=False)


def label_row(path, prop, row, label=''):
    row.label(text=label if label else names[prop])
    row.prop(path, prop, text='')


def header_row(row, prop, label='', emboss=False):
    preference = addon.preference()
    icon = 'DISCLOSURE_TRI_RIGHT' if not getattr(preference.ui, prop) else 'DISCLOSURE_TRI_DOWN'
    row.alignment = 'LEFT'
    row.prop(preference.ui, prop, text='', emboss=emboss)

    sub = row.row(align=True)
    sub.scale_x = 0.25
    sub.prop(preference.ui, prop, text='', icon=icon, emboss=emboss)
    row.prop(preference.ui, prop, text=F'{label}', emboss=emboss)

    sub = row.row(align=True)
    sub.scale_x = 0.75
    sub.prop(preference.ui, prop, text=' ', icon='BLANK1', emboss=emboss)


def draw(preference, context, layout):

    wm = bpy.context.window_manager
    # N panel
    layout.separator()
    label_row(preference.ui, 'Hops_panel_location', layout.row(), label='HardOps panel category')

    box = layout.box()
    header_row(box.row(align=True), 'Hops_hopsUI_expand', label='Hardops UI')
    box.separator()
    if preference.ui.Hops_hopsUI_expand:
        label_row(preference.ui, 'Hops_modal_scale', box.row(), label='Modal Scale')
        #UI Framework : Expnaded UI
        label_row(preference.ui, 'Hops_modal_size',               box.row(), label='Modal UI Size')
        label_row(preference.ui, 'Hops_modal_fast_ui_loc_options',box.row(), label='Modal UI Display Method')


    box = layout.box()
    header_row(box.row(align=True), 'Hops_Display_expand', label='Display options')
    box.separator()
    if preference.ui.Hops_Display_expand:
        #label_row(preference.ui, 'Hops_modal_presets',              layout.row(), label='Modal Presets')
        label_row(preference.ui, 'Hops_modal_background',            box.row(), label='Modal Background')
        label_row(preference.ui, 'Hops_modal_drop_shadow',           box.row(), label='Modal Drop Shadow')
        label_row(preference.ui, 'Hops_modal_cell_border',           box.row(), label='Modal Cell Border')
        label_row(preference.ui, 'Hops_modal_drop_shadow_offset',    box.row(), label='Modal Drop Shadow Offset')
        label_row(preference.ui, 'Hops_modal_cell_background',       box.row(), label='Modal Cell Background')
        label_row(preference.ui, 'Hops_modal_kit_ops_display_count', box.row(), label='Kit Ops Display Count')

    box = layout.box()
    header_row(box.row(align=True), 'Hops_Fade_expand', label='Fade options')
    box.separator()
    if preference.ui.Hops_Fade_expand:
        label_row(preference.ui, 'Hops_modal_fade_in', box.row(), label='Modal fade in time')
        label_row(preference.ui, 'Hops_modal_fade',    box.row(), label='Modal fade out time')


    box = layout.box()
    header_row(box.row(align=True), 'Hops_FastUI_expand', label='Fast UI options')
    box.separator()
    if preference.ui.Hops_FastUI_expand:
        #UI Framework : Fast UI
        label_row(preference.ui, 'Hops_modal_fast_ui_padding',       box.row(), label='Fast UI panel offset')
        label_row(preference.ui, 'Hops_modal_mod_count_fast_ui',     box.row(), label='Fast UI Mod count')
        label_row(preference.ui, 'Hops_modal_auto_show_help',        box.row(), label='Fast UI auto show Help')
        label_row(preference.ui, 'Hops_modal_auto_show_mods',        box.row(), label='Fast UI auto show Mods')
        label_row(preference.ui, 'Hops_modal_help_show_label',       box.row(), label='Fast UI show Help label in fast UI')
        label_row(preference.ui, 'Hops_modal_mods_show_label',       box.row(), label='Fast UI show Mods label')

        label_row(preference.ui, 'Hops_modal_fast_ui_mods_offset',   box.row(), label='Fast UI Mods Offset')
        label_row(preference.ui, 'Hops_modal_fast_ui_mods_size',     box.row(), label='Fast UI Mods Size')
        label_row(preference.ui, 'Hops_modal_fast_ui_help_offset',   box.row(), label='Fast UI Help Offset')
        label_row(preference.ui, 'Hops_modal_fast_ui_help_size',     box.row(), label='Fast UI Help Size')
        label_row(preference.ui, 'Hops_modal_fast_ui_main_y_offset', box.row(), label='Fast UI Main Y Offset')
        label_row(preference.ui, 'Hops_warp_on',                     box.row(), label='Turn Cursor Warp on or off')
        label_row(preference.ui, 'Hops_warp_mode_padding',           box.row(), label='Cursor Warp Padding')
        label_row(preference.ui, 'Hops_warp_border_display',         box.row(), label='Display Warp Border')
        label_row(preference.ui, 'Hops_warp_border_display_style',         box.row(), label='Display Style')
        label_row(preference.ui, 'Hops_warp_line_length',         box.row(), label='Display lenght')
        label_row(preference.ui, 'Hops_warp_line_width',         box.row(), label='Display width')
        label_row(preference.ui, 'Hops_auto_hide_n_panel',           box.row(), label='Auto Hide N-Panel')
        label_row(preference.ui, 'Hops_auto_hide_t_panel',           box.row(), label='Auto Hide T-Panel')

    box = layout.box()
    header_row(box.row(align=True), 'Hops_OperatorUI_expand', label='Operator UI options')
    box.separator()
    if preference.ui.Hops_OperatorUI_expand:
        #UI Framework : Operator UI
        label_row(preference.ui, 'Hops_operator_ui_offset',    box.row(), label='Operator UI offset')
        label_row(preference.ui, 'Hops_operator_display_time', box.row(), label='Operator Display Time')
        label_row(preference.ui, 'Hops_operator_fade',         box.row(), label='Operator Fade Time')
        label_row(preference.ui, 'Hops_operator_display',      box.row(), label='Operator Display')
        if preference.ui.Hops_operator_display:
            label_row(preference.ui, 'Hops_extra_info',        box.row(), label='Extra Info Display')
        if preference.ui.Hops_operator_display and hasattr(wm, 'bc'):
            label_row(preference.display, 'bc_notifications',       box.row(), label='Boxcutter Notification')
        label_row(preference.ui, 'Hops_operator_draw_bg',      box.row(), label='Operator Background')
        label_row(preference.ui, 'Hops_operator_draw_border',  box.row(), label='Operator Border')
        label_row(preference.ui, 'Hops_operator_border_size',  box.row(), label='Operator Border Size')

    box = layout.box()
    box.separator()
    label_row(preference.ui, 'Hops_material_count',    box.row(), label='Material List Count')
    label_row(preference.ui, 'expanded_menu',          box.row(), label='Sequential Q Menus')
    label_row(preference.ui, 'use_dpi_factoring',      box.row(), label='Popup Dpi Factoring')
    label_row(preference.ui, 'use_helper_popup',       box.row(), label='Helper popup')
    label_row(preference.ui, 'Hops_helper_width',       box.row(), label='Helper Width')
    label_row(preference.ui, 'use_bevel_helper_popup', box.row(), label='Bevel Helper popup')
    label_row(preference.ui, 'use_kitops_popup',       box.row(), label='Use KITOPS popup')
    #label_row(preference.display, 'bc_notifications', box.row(), label='BC Notifications')
