import bpy
import os

from pathlib import Path
from math import radians
from mathutils import Vector

from bpy.types import PropertyGroup
from bpy.props import BoolProperty, FloatVectorProperty, FloatProperty, StringProperty, EnumProperty, IntProperty

from .... preferences import get_preferences, get_addon_name

from ... utility import addon, names, modifier

def update_HardOps_Panel_Tools(self, context):
    panel = getattr(bpy.types, "hops_main_panel", None)
    if panel is not None:
        bpy.utils.unregister_class(panel)
        panel.bl_category = get_preferences().toolbar_category_name
        bpy.utils.register_class(panel)


def category_name_changed(self, context):
    category = get_preferences().toolbar_category_name
    change_hard_ops_category(category)

# edit mode properties


Eevee_presets = [
    ("64", "64", "64"),
    ("128", "128", "128"),
    ("256", "256", "256"),
    ("512", "512", "512"),
    ("1024", "1024", "1024"),
    ("2048", "2048", "2048"),
    ("4096", "4096", "4096")]


booleans_modes = [
    ("BMESH", "Bmesh", ""),
    ("CARVE", "Carve", "")]

settings_tabs_items = [
    ("UI", "UI", ""),
    ("DRAWING", "Drawing", ""),
    ("INFO", "Info", ""),
    ("KEYMAP", "Keymap", ""),
    ("LINKS", "Links / Help", ""),
    ("ADDONS", "Addons", "")]

mirror_modes = [
    ("MODIFIER", "Mod", ""),
    ("BISECT", "Bisect", ""),
    ("SYMMETRY", "Symmetry", "")]

mirror_modes_multi = [
    ("VIA_ACTIVE", "Mod", ""),
    ("MULTI_SYMMETRY", "Symmetry", "")]

mirror_direction = [
    ("-", "-", ""),
    ("+", "+", "")]

ko_popup_type = [
    ("DEFAULT", "Default", ""),
    ("ST3", "St3", "")]

# menu_array_type = [
#     ("DEFAULT", "Default", ""),
#     ("ST3", "St3 V1", ""),
#     ("ST3_V2", "St3 V2", "")]

array_type = [
    ("CIRCLE", "Circle", ""),
    ("DOT", "Dot", "")]

symmetrize_type = [
    ("DEFAULT", "Default", ""),
    ("Machin3", "Machin3", "")]

sort_options = (
    'sort_modifiers',
    'sort_bevel',
    'sort_array',
    'sort_mirror',
    'sort_solidify',
    'sort_weighted_normal',
    'sort_simple_deform',
    'sort_triangulate',
    'sort_decimate',
    'sort_remesh',
    'sort_subsurf',
    'sort_bevel_last',
    'sort_array_last',
    'sort_mirror_last',
    'sort_solidify_last',
    'sort_weighted_normal_last',
    'sort_simple_deform_last',
    'sort_triangulate_last',
    'sort_decimate_last',
    'sort_remesh_last',
    'sort_subsurf_last')


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


def sync_sort(prop, context):
    for option in sort_options:

        if bc() and hasattr(bc().behavior, option):
            bc().behavior[option] = getattr(prop, option)

        else:
            print(F'Unable to sync sorting options with Box Cutter; Hard Ops {option}\nUpdate Box Cutter!')

        if kitops() and hasattr(kitops(), option):
            kitops()[option] = getattr(prop, option)

        else:
            print(F'Unable to sync sorting options with KIT OPS; Hard Ops {option}\nUpdate KIT OPS!')


class hops(PropertyGroup):

    bl_idname = get_addon_name()

    debug: BoolProperty(name="debug", default=False)

    # not shown in pref
    show_presets: BoolProperty(
        name = "Show Presets",
        description = "Show presets in helper",
        default = True)

    decalmachine_fix: BoolProperty(name="Use Setup For DECALmachine", default=False)

    adaptivemode: BoolProperty("Adaptive Segments", default=False)
    adaptiveoffset: FloatProperty("Adaptive Offset", default=10, min=0)
    adaptivewidth: BoolProperty("Adaptive Segments", default=False)

    auto_bweight: BoolProperty("auto bweight", default=False)
    bevel_profile: FloatProperty("default bevel profile", default=0.70, min=0, max=1, description="Default bevel profile for modals")
    profile_folder: StringProperty("Profile Folder", default=str(Path(__file__).parents[5].joinpath('presets', 'profiles')), subtype='FILE_PATH')

    lights_folder: StringProperty("Lights Folder", default=str(Path(__file__).parents[5].joinpath('presets', 'lights')), subtype='FILE_PATH')

    keep_cutin_bevel: BoolProperty(name="Keep Cut In Bevel", default=True)
    force_array_reset_on_init: BoolProperty(name="Force Array Reset", default=False)
    force_array_apply_scale_on_init: BoolProperty(name="Force Array Apply Scale", default=False)
    force_thick_reset_solidify_init: BoolProperty(name="Force Reset Solidify", default=False)

    ko_popup_type: EnumProperty(name="KitOps Popup Type",
                                 description="""Asset Loader Toggle

                                 Kitops popup toggle for expansive or classic
                                 Default - classic kitops popup
                                 Expansive - digital loader for both kitops and decalmachine

                                 """,
                                 items=[("DEFAULT", "Default", ""),
                                 ("ST3", "Expansive", "")],
                                 default='ST3')

    menu_array_type: EnumProperty(name="Array Q Menu Option Type",
                                  description="""Array Selection Switch

                                  HOPS array style for Q menus
                                  Classic - initial array of hops
                                  V1 - prototype multi array
                                  V2 - classic / 3d array

                                  """,
                                  items=[("DEFAULT", "Classic", ""),
                                  ("ST3", "Array V1", ""),
                                  ("ST3_V2", "Array V2", "")],
                                  default='ST3_V2')

    array_type: EnumProperty(name="Array V1 Gizmo Type",
                                description="Array V1 Circle / DOT",
                                items=[
                                    ("CIRCLE", "Circle", ""),
                                    ("DOT", "Dot", "")],
                                default='CIRCLE')

    st3_meshtools: BoolProperty(name="Enable ST3 Meshtools", default=False, description="Enable experimental ST3 Meshtools in edit")

    meshclean_mode: EnumProperty(name="Mode",
                                 description="",
                                 items=[('ACTIVE', "Active", "Effect all the active object geometry"),
                                        ('SELECTED', "Selected", "Effect only selected geometry or selected objects geometry"),
                                        ('VISIBLE', "Visible", "Effect only visible geometry")],
                                 default='ACTIVE')

    meshclean_dissolve_angle: FloatProperty(name="Limited Dissolve Angle",
                                            default=radians(0.5),
                                            min=radians(0),
                                            max=radians(30),
                                            subtype="ANGLE")
    meshclean_remove_threshold: FloatProperty(name="Remove Threshold Amount",
                                              description="Remove Double Amount",
                                              default=0.001,
                                              min=0.0001,
                                              max=1.00)
    meshclean_unhide_behavior: BoolProperty(default=True)
    meshclean_delete_interior: BoolProperty(default=False)
    #to_cam_jump: BoolProperty(default=True, description="To_Camera activate new camera as active")
    to_cam: EnumProperty(name="To_Cam Behavior",
                                description="""To_Cam Behavior

                                Frontal - places camera in front of central model
                                View - Aligns camera to view which can be preferred

                                """,
                                items=[
                                    ("DEFAULT", "Frontal", ""),
                                    ("VIEW", "View", "")],
                                default='VIEW')

    to_render_jump: BoolProperty(default=False, description="Lookdev settings to render settings on confirm of viewport+")
    to_light_constraint: BoolProperty(default=False, description="Blank / Add light utilizes track to")

    bool_scroll: EnumProperty(
        name="Default Boolscroll Method",
        description="What technique to use to boolscroll",
        items=[
            ('CLASSIC', "Classic", "Isolate cutters then begin showing cutters via scroll"),
            ('ADDITIVE', "Additive", "Do not hide previous cutters when beginning scroll")],
        default='CLASSIC')

    dice_method: EnumProperty(
        name="Default Dice Method",
        description="What technique to use to cut the object",
        items=[
            ('KNIFE_PROJECT', "Knife Project", "Use knife project to cut the object"),
            ('MESH_INTERSECT', "Mesh Intersect", "Use mesh intersect to cut the object")],
        default='KNIFE_PROJECT')

    dice_adjust: EnumProperty(
        name="Default Dice Adjust",
        description="What variable to start out adjusting with the mouse",
        items=[
            ('AXIS', "Axis", "Use the mouse to adjust the dicing axis"),
            ('SEGMENTS', "Segments", "Use the mouse to adjust the amount of cuts"),
            ('NONE', "None", "Don't use the mouse to adjust anything")],
        default='AXIS')

    smart_apply_dice: EnumProperty(
        name="Default Dice Adjust",
        description="What variable to start out adjusting with the mouse",
        items=[
            ('SMART_APPLY', "Smart Apply", "Smart apply prior to dice"),
            ('APPLY', "Apply", "Convert to mesh prior to dice."),
            ('NONE', "None", "Do not apply. Just Dice.")],
        default='NONE')

    bool_bstep: BoolProperty(
        name="Bool Bevel Step",
        description="Add new bevel during sort bypass on Ctrl + click boolean operations",
        default=True)


    sharp_use_crease: BoolProperty(name="Allow Sharpening To Use Crease", default=False, description="Sharpen / Mark to mark using crease 1.0")
    sharp_use_bweight: BoolProperty(name="Allow Sharpening To Use Bevel Weight", default=True, description="Sharpen / Mark to mark using bevel weight 1.0")
    sharp_use_seam: BoolProperty(name="Allow Sharpening To Use Seams", default=False, description="Sharpen / Mark to mark using seams. Assists with face selection")
    sharp_use_sharp: BoolProperty(name="Allow Sharpening To Use Sharp Edges", default=True, description="Sharpen / Mark to mark using sharp marking. Assists autosmoothing")


    sort_modifiers: BoolProperty(name="Sort Modifiers", update=sync_sort, default=True)
    # sort_bevel_last: BoolProperty(name="Sort Bevel Last", update=sync_sort, default=False)
    # sort_bevel: BoolProperty(name="Sort Bevel", update=sync_sort, default=True)
    # sort_solidify: BoolProperty(name='Sort Solidify', update=sync_sort, default=False)
    # sort_array: BoolProperty(name="Sort Array", update=sync_sort, default=True)
    # sort_mirror: BoolProperty(name="Sort Mirror", update=sync_sort, default=True)
    # sort_weighted_normal: BoolProperty(name="Sort Weighted Normal", update=sync_sort, default=True)
    # sort_simple_deform: BoolProperty(name="Sort Simple Deform", update=sync_sort, default=True)
    # sort_triangulate: BoolProperty(name="Sort Triangulate", update=sync_sort, default=True)
    # sort_decimate: BoolProperty(name="Sort Decimate", update=sync_sort, default=False)


    sort_bevel: BoolProperty(
        name = 'Sort Bevel',
        description = '\n Ensure bevel modifiers are placed after any boolean modifiers created',
        update = sync_sort,
        default = True)

    sort_weighted_normal: BoolProperty(
        name = 'Sort Weighted Normal',
        description = '\n Ensure weighted normal modifiers are placed after any boolean modifiers created',
        update = sync_sort,
        default = True)

    sort_array: BoolProperty(
        name = 'Sort Array',
        description = '\n Ensure array modifiers are placed after any boolean modifiers created',
        update = sync_sort,
        default = True)

    sort_mirror: BoolProperty(
        name = 'Sort Mirror',
        description = '\n Ensure mirror modifiers are placed after any boolean modifiers created',
        update = sync_sort,
        default = True)

    sort_solidify: BoolProperty(
        name = 'Sort Soldify',
        description = '\n Ensure solidify modifiers are placed after any boolean modifiers created',
        update = sync_sort,
        default = False)

    sort_triangulate: BoolProperty(
        name = 'Sort Triangulate',
        description = '\n Ensure triangulate modifiers are placed after any boolean modifiers created',
        update = sync_sort,
        default = True)

    sort_simple_deform: BoolProperty(
        name = 'Sort Simple Deform',
        description = '\n Ensure simple deform modifiers are placed after any boolean modifiers created',
        update = sync_sort,
        default = True)

    sort_decimate: BoolProperty(
        name = 'Sort Decimate',
        description = '\n Ensure decimate modifiers are placed after any boolean modifiers created',
        update = sync_sort,
        default = False)

    sort_remesh: BoolProperty(
        name = 'Sort Remesh',
        description = '\n Ensure remesh modifiers are placed after any boolean modifiers created',
        update = sync_sort,
        default = True)

    sort_subsurf: BoolProperty(
        name = 'Sort Subsurf',
        description = '\n Ensure subsurf modifiers are placed after any boolean modifiers created',
        update = sync_sort,
        default = False)

    sort_weld: BoolProperty(
        name = 'Sort Weld',
        description = '\n Ensure weld modifiers are placed after any boolean modifiers created',
        update = sync_sort,
        default = False)

    sort_uv_project: BoolProperty(
        name = 'Sort UV Project',
        description = '\n Ensure uv project modifiers are placed after any boolean modifiers created',
        update = sync_sort,
        default = True)

    sort_bevel_last: BoolProperty(
        name = 'Sort Bevel',
        description = '\n Only effect the most recent bevel modifier when sorting',
        update = sync_sort,
        default = True)

    sort_weighted_normal_last: BoolProperty(
        name = 'Sort Weighted Normal Last',
        description = '\n Only effect the most recent weighted normal modifier when sorting',
        update = sync_sort,
        default = True)

    sort_array_last: BoolProperty(
        name = 'Sort Array Last',
        description = '\n Only effect the most recent array modifier when sorting',
        update = sync_sort,
        default = True)

    sort_mirror_last: BoolProperty(
        name = 'Sort Mirror Last',
        description = '\n Only effect the most recent mirror modifier when sorting',
        update = sync_sort,
        default = True)

    sort_solidify_last: BoolProperty(
        name = 'Sort Soldify Last',
        description = '\n Only effect the most recent solidify modifier when sorting',
        update = sync_sort,
        default = False)

    sort_triangulate_last: BoolProperty(
        name = 'Sort Triangulate Last',
        description = '\n Only effect the most recent triangulate modifier when sorting',
        update = sync_sort,
        default = True)

    sort_simple_deform_last: BoolProperty(
        name = 'Sort Simple Deform Last',
        description = '\n Only effect the most recent simple deform modifier when sorting',
        update = sync_sort,
        default = True)


    sort_decimate_last: BoolProperty(
        name = 'Sort Decimate Last',
        description = '\n Only effect the most recent decimate modifier when sorting',
        update = sync_sort,
        default = False)

    sort_remesh_last: BoolProperty(
        name = 'Sort Remesh Last',
        description = '\n Only effect the most recent remesh modifier when sorting',
        update = sync_sort,
        default = True)

    sort_subsurf_last: BoolProperty(
        name = 'Sort Subsurf Last',
        description = '\n Only effect the most recent subsurface modifier when sorting',
        update = sync_sort,
        default = False)

    sort_weld_last: BoolProperty(
        name = 'Sort Weld Last',
        description = '\n Only effect the most recent weld modifier when sorting',
        update = sync_sort,
        default = True)

    sort_uv_project_last: BoolProperty(
        name = 'Sort UV Project Last',
        description = '\n Only effect the most recent uv project modifier when sorting',
        update = sync_sort,
        default = True)

    sort_bevel_ignore_vgroup: BoolProperty(
        name = 'Ignore VGroup Bevels',
        description = '\n Ignore bevel modifiers that are using the vertex group limit method while sorting',
        update = sync_sort,
        default = True)

    sort_bevel_ignore_only_verts: BoolProperty(
        name = 'Ignore Only Vert Bevels',
        description = '\n Ignore bevel modifiers that are using the only vertices option while sorting',
        update = sync_sort,
        default = True)

    workflow: EnumProperty(name="Mode",
                           description="",
                           items=[('DESTRUCTIVE', "Destructive", ""),
                                  ('NONDESTRUCTIVE', "NonDestructive", "")],
                           default='NONDESTRUCTIVE')

    workflow_mode: EnumProperty(name="Mode",
                                description="",
                                items=[('ANGLE', "Angle", ""),
                                       ('WEIGHT', "Weight", "")],
                                default='ANGLE')

    add_weighten_normals_mod: BoolProperty(name="WN", default=False)
    use_harden_normals: BoolProperty(name="HN", default=False)

    helper_tab: StringProperty(name="Helper Set Category", default="MODIFIERS")

    Eevee_preset_HQ: EnumProperty(items=Eevee_presets, default="2048")
    Eevee_preset_LQ: EnumProperty(items=Eevee_presets, default="64")

    tab: EnumProperty(name="Tab", items=settings_tabs_items)

    toolbar_category_name: StringProperty(
        name="Toolbar Category",
        default="HardOps",
        description="Name of the tab in the toolshelf in the 3d view",
        update=category_name_changed)

    bevel_loop_slide: BoolProperty(
        name="Bweight loop slide",
        default=True,
        description="loop slide")

    pie_mod_expand: BoolProperty(
        name="Pie Mod Expand",
        default=False,
        description="Expand Pie")

    right_handed: BoolProperty(
        name="Right Handed",
        default=True,
        description="Reverse The X Mirror For Right Handed People")

    BC_unlock: BoolProperty(
        name="BC",
        default=False,
        description="BC Support")

    hops_modal_help: BoolProperty(
        name="Modal Help",
        default=False,
        description="Enables help for modal operators")

    Hops_sharp_remove_cutters: BoolProperty(name="Remove Cutters",
                                            description="Remove Cutters on Csharp apply",
                                            default=False)

    Hops_smartapply_remove_cutters: BoolProperty(name="Smart Apply Remove Cutters",
                                            description="""Smart Apply Remove Cutters

                                            Experimental:
                                            Can have issues with multi mesh smart apply or shared cutters.
                                            Work in progress.
                                            """,
                                            default=False)

    sharpness: FloatProperty(name="angle edge marks are applied to", default=radians(30), min=radians(1), max=radians(180), precision=3, unit='ROTATION')
    auto_smooth_angle: FloatProperty(name="angle edge marks are applied to", default=radians(60), min=radians(1), max=radians(180), precision=3, unit='ROTATION')


    # operators
    Hops_mirror_modes: EnumProperty(name="Mirror Modes", items=mirror_modes, default='MODIFIER')
    Hops_mirror_modes_multi: EnumProperty(name="Mirror Modes Multi", items=mirror_modes_multi, default='VIA_ACTIVE')
    Hops_mirror_direction: EnumProperty(name="Mirror Direction", items=mirror_direction, default='+')

    Hops_gizmo_mirror_block_x: BoolProperty(name="Mirror X Gizmo Block", default=False)
    Hops_gizmo_mirror_block_y: BoolProperty(name="Mirror Y Gizmo Block", default=False)
    Hops_gizmo_mirror_block_z: BoolProperty(name="Mirror Z Gizmo Block", default=False)

    Hops_gizmo_mirror_u: BoolProperty(name="Mirror UV", default=False)
    Hops_gizmo_mirror_v: BoolProperty(name="Mirror UV", default=False)

    Hops_mirror_modal_mod_on_bisect: BoolProperty(
        name="Modal Mirror Bisect Modifier",
        default=True,
        description="use modifier for modal mirror bisect")

    Hops_mirror_modal_use_cursor: BoolProperty(
        name="Modal Mirror Uess Cursor",
        default=False,
        description="uses cursor for modal mirror")

    Hops_mirror_modal_revert: BoolProperty(
        name="Modal Mirror Revert",
        default=True,
        description="reverts modal mirror")

    Hops_mirror_modal_Interface_scale: FloatProperty(
        name="Modal Mirror Interface Scale",
        description="Modal Mirror Interface Scale",
        default=0.7, min=0.1, max=50)

    Hops_gizmo_array: FloatProperty(
        name="Array gizmo",
        description="Array gizmo",
        default=0
        )

    Hops_modal_percent_scale: FloatProperty(
        name="Modal Operators Scale",
        description="Modal Operators Scale",
        default=1, min=0.001, max=100)

    Hops_twist_radial_sort: BoolProperty(
        name="Twist / Radial Bypass",
        default=False,
        description="""Determines render visibility for twist360/radial

        Bypasses sort bypass / edit display on twist / radial 360
        *bypassing sort can be useful for cutting radial shapes as a whole*

        """)

    # edit mode properties

    adjustbevel_use_1_segment: BoolProperty(name="use 1 segment", default=True)

    Hops_circle_size: FloatProperty(
        name="Bevel offset step",
        description="Bevel offset step",
        default=0.0001, min=0.0001)

    Hops_gizmo: BoolProperty(name="Display Mirror Gizmo", default=True)
    Hops_gizmo_fail: BoolProperty(name="gizmo failed", default=False)
    Hops_gizmo_mirror: BoolProperty(name="Display Mirror Gizmo", default=False)
    Hops_gizmo_qarray: BoolProperty(name="Display Array Gizmo", default=False)

    circle_divisions: IntProperty(name="Division Count", description="Amount Of Vert divisions for circle", default=5, min=1, max=12)

    dots_snap: EnumProperty(name="Mode",
                            description="",
                            items=[('ORIGIN', "Origin", ""),
                                   ('FIXED', "Fixed", ""),
                                   ('CURSOR', "Cursor", "")],
                            default='CURSOR')

    modal_handedness: EnumProperty(name="Handedness",
                            description="""Orientation Style for modal operation
                            protip: Use left.

                            """,
                            items=[('LEFT', "Left", ""),
                                   ('RIGHT', "Right", "")],
                            default='LEFT')

    dots_x_cursor: FloatProperty("dots x", default=100)
    dots_y_cursor: FloatProperty("dots y", default=0)

    dots_x: FloatProperty("dots x", default=100)
    dots_y: FloatProperty("dots y", default=100)

    parent_boolshapes: BoolProperty(name="Parent Boolshapes", default=False, description="Parents cutter to the target allowing for transformation")

def label_row(path, prop, row, label=''):
    row.label(text=label if label else names[prop])
    row.prop(path, prop, text='')


def draw(preference, context, layout):
    layout.label(text='Hardops Properties:')
    layout.separator()
    label_row(preference.property, 'modal_handedness', layout.row(), label='Modal Handedness')
    layout.separator()
    label_row(preference.property, 'ko_popup_type', layout.row(), label='KitOps Popup Type')
    label_row(preference.property, 'menu_array_type', layout.row(), label='Array Q Menu Option')
    label_row(preference.property, 'array_type', layout.row(), label='ST3 Array Gizmo')
    layout.separator()
    #label_row(preference.property, 'advanced_stats', layout.row(), label='Advanced Stats')
    label_row(preference.property, 'meshclean_mode', layout.row(), label='MeshClean Mode')
    label_row(preference.property, 'bevel_profile', layout.row(), label='Bevel Profile')
    label_row(preference.property, 'bool_scroll', layout.row(), label='Bool Scroll System')
    label_row(preference.property, 'profile_folder', layout.row(), label='Profile Folder')
    label_row(preference.property, 'lights_folder', layout.row(), label='Lights Folder')
    #label_row(preference.property, 'circle_divisions', layout.row(), label='Circle(E) Divisions')
    #label_row(preference.property, 'st3_meshtools', layout.row(),label='ST3 Meshtools Unlock')
    label_row(preference.behavior, 'mat_viewport', layout.row(), label='Blank Mat Scroll to Viewport Mat')
    label_row(preference.property, 'Hops_twist_radial_sort', layout.row(), label='Radial / Twist (Render Toggle)')
    label_row(preference.property, 'to_cam', layout.row(), label='To_Cam Behavior')
    label_row(preference.property, 'to_render_jump', layout.row(), label='Viewport+ Set Render')
    label_row(preference.property, 'to_light_constraint', layout.row(), label='Blank Light Constraint')
    layout.label(text='Sharpen Options:')
    label_row(preference.property, 'sharpness', layout.row(), label='Sharpness Angle')
    layout.label(text='Sharp : Mark:')
    label_row(preference.property, 'sharp_use_crease', layout.row(), label='Crease')
    label_row(preference.property, 'sharp_use_bweight', layout.row(), label='Bevel Weight')
    label_row(preference.property, 'sharp_use_seam', layout.row(), label='Seam')
    label_row(preference.property, 'sharp_use_sharp', layout.row(), label='Sharp')
    layout.label(text='Remove Cutters:')
    label_row(preference.property, 'Hops_sharp_remove_cutters', layout.row(), label='Sharpen ')
    label_row(preference.property, 'Hops_smartapply_remove_cutters', layout.row(), label='Smart Apply ')
    layout.separator()
    label_row(preference.property, 'debug', layout.row(), label='Debug Options')
    layout.separator()
    if get_preferences().property.debug:

        #label_row(preference.property, 'st3_meshtools', layout.row(), label='St3 Meshtools')
        label_row(preference.property, 'decalmachine_fix', layout.row(), label='Use Decalmachine Fix')
        label_row(preference.property, 'show_presets', layout.row(), label='show_presets')
        label_row(preference.property, 'adaptivemode', layout.row(), label='Use Adaptive Mode')
        label_row(preference.property, 'adaptiveoffset', layout.row(), label='Use Adaptive Offset')
        label_row(preference.property, 'adaptivewidth', layout.row(), label='Use Adaptive Width')
        label_row(preference.property, 'auto_bweight', layout.row(), label='Use Auto Bweight')
        label_row(preference.property, 'keep_cutin_bevel', layout.row(), label='keep_cutin_bevel')
        label_row(preference.property, 'force_array_reset_on_init', layout.row(), label='force_array_reset_on_init')
        label_row(preference.property, 'force_array_apply_scale_on_init', layout.row(), label='force_array_apply_scale_on_init')
        label_row(preference.property, 'force_thick_reset_solidify_init', layout.row(), label='force_thick_reset_solidify_init')
        label_row(preference.property, 'meshclean_dissolve_angle', layout.row(), label='meshclean_dissolve_angle')
        label_row(preference.property, 'meshclean_remove_threshold', layout.row(), label='meshclean_remove_threshold')
        label_row(preference.property, 'meshclean_unhide_behavior', layout.row(), label='meshclean_unhide_behavior')
        label_row(preference.property, 'meshclean_delete_interior', layout.row(), label='meshclean_delete_interior')
        label_row(preference.property, 'Hops_gizmo_mirror_u', layout.row(), label='mirror U')
        label_row(preference.property, 'Hops_gizmo_mirror_v', layout.row(), label='mirror V')
        #label_row(preference.property, 'hops_modal_help', layout.row(), label='Show Help For modal Operators')
        # label_row(preference.property, 'sort_bevel', layout.row(), label='sort_bevel')
        # label_row(preference.property, 'sort_solidify', layout.row(), label='sort_solidify')
        # label_row(preference.property, 'sort_array', layout.row(), label='sort_array')
        # label_row(preference.property, 'sort_mirror', layout.row(), label='sort_mirror')
        # label_row(preference.property, 'sort_weighted_normal', layout.row(), label='sort_weighted_normal')
        # label_row(preference.property, 'sort_simple_deform', layout.row(), label='sort_simple_deform')
        # label_row(preference.property, 'sort_triangulate', layout.row(), label='sort_triangulate')
        # label_row(preference.property, 'sort_decimate', layout.row(), label='sort_decimate')


        if preference.property.sort_modifiers:
            row = layout.row(align=True)
            row.alignment = 'RIGHT'
            split = row.split(align=True, factor=0.85)

            row = split.row(align=True)
            for type in modifier.sort_types:
                icon = F'MOD_{type}'
                if icon == 'MOD_WEIGHTED_NORMAL':
                    icon = 'MOD_NORMALEDIT'
                elif icon == 'MOD_SIMPLE_DEFORM':
                    icon = 'MOD_SIMPLEDEFORM'
                elif icon == 'MOD_DECIMATE':
                    icon = 'MOD_DECIM'
                elif icon == 'MOD_WELD':
                    icon = 'AUTOMERGE_OFF'
                row.prop(preference.property, F'sort_{type.lower()}', text='', icon=icon)

            row = split.row(align=True)
            row.scale_x = 1.5
            row.popover('HOPS_PT_sort_last', text='', icon='SORT_ASC')

        label_row(preference.property, 'workflow', layout.row(), label='workflow')
        label_row(preference.property, 'workflow_mode', layout.row(), label='workflow_mode')
        label_row(preference.property, 'add_weighten_normals_mod', layout.row(), label='add_weighten_normals_mod')
        label_row(preference.property, 'use_harden_normals', layout.row(), label='use_harden_normals')
        label_row(preference.property, 'helper_tab', layout.row(), label='helper_tab')
        label_row(preference.property, 'tab', layout.row(), label='tab')
        label_row(preference.property, 'toolbar_category_name', layout.row(), label='toolbar_category_name')
        label_row(preference.property, 'bevel_loop_slide', layout.row(), label='bevel_loop_slide')
        label_row(preference.property, 'pie_mod_expand', layout.row(), label='pie_mod_expand')
        label_row(preference.property, 'right_handed', layout.row(), label='right_handed')
        label_row(preference.property, 'BC_unlock', layout.row(), label='BC_unlock')
        label_row(preference.property, 'auto_smooth_angle', layout.row(), label='auto_smooth_angle')
        label_row(preference.property, 'Hops_mirror_modes', layout.row(), label='Hops_mirror_modes')
        label_row(preference.property, 'Hops_mirror_modes_multi', layout.row(), label='Hops_mirror_modes_multi')
        label_row(preference.property, 'Hops_mirror_direction', layout.row(), label='Hops_mirror_direction')
        label_row(preference.property, 'Hops_mirror_modal_use_cursor', layout.row(), label='Hops_mirror_modal_use_cursor')
        label_row(preference.property, 'Hops_mirror_modal_revert', layout.row(), label='Hops_mirror_modal_revert')
        label_row(preference.property, 'Hops_mirror_modal_Interface_scale', layout.row(), label='Hops_mirror_modal_Interface_scale')
        label_row(preference.property, 'Hops_gizmo_array', layout.row(), label='Hops_gizmo_array')
        label_row(preference.property, 'Hops_modal_percent_scale', layout.row(), label='Hops_modal_percent_scale')
        label_row(preference.property, 'adjustbevel_use_1_segment', layout.row(), label='adjustbevel_use_1_segment')
        label_row(preference.property, 'Hops_circle_size', layout.row(), label='Hops_circle_size')
        label_row(preference.property, 'Hops_gizmo', layout.row(), label='Hops_gizmo')
        label_row(preference.property, 'Hops_gizmo_fail', layout.row(), label='Hops_gizmo_fail')
        label_row(preference.property, 'Hops_gizmo_mirror', layout.row(), label='Hops_gizmo_mirror')
        label_row(preference.property, 'Hops_gizmo_qarray', layout.row(), label='Hops_gizmo_qarray')
        label_row(preference.property, 'parent_boolshapes', layout.row(), label='Parent Boolshapes')
