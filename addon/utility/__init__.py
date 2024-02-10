__all__ = ('addon', 'data', 'lattice', 'math', 'mesh', 'modal', 'modifier', 'object', 'ray', 'screen', 'view3d')

import traceback

import bpy

from bl_ui.space_toolsystem_common import activate_by_id as activate_tool
from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active as view3d_tools


name = __name__.partition('.')[0]

# TODO: create collections for these in preferences
vertice_presets = [3, 6, 8, 32, 64]
array_presets = [2, 4, 6, 8, 10]
width_presets = [0.02, 0.05, 0.1]
segment_presets = [1, 2, 3, 4, 6]
angle_presets = [5, 15, 30, 45, 90]

names = {
    'cut': 'Cut',
    'slice': 'Slice',
    'inset': 'Inset',
    'join': 'Join',
    'make': 'Make',
    'knife': 'Knife',
    'snap': 'Snap',
    'negative': 'Negative',
    'bbox': 'Bbox',
    'dot': 'Dot',
    'dot_highlight': 'Highlight',
    'wire': 'Wire',
    'show_shape_wire': 'Show Shape Wire',
    'wire_width': 'Wire Width',
    'bounds': 'Show Bounds',
    'allow_selection': 'Allow Selection',
    'sort_modifiers': 'Sort Modifiers',
    'keep_modifiers': 'Keep Modifiers',
    'ngon_snap_angle': 'Ngon Snap Angle',
    'auto_smooth': 'Auto Smooth',
    'join_flip_z': 'Join Flip Z',
    'use_multi_edit': 'Use Mult-Edit',
    'make_active': 'Shift to Active',
    'show_shape': 'Show Shape',
    'parent_shape': 'Parent Shape',
    'apply_slices': 'Apply Slices',
    'make_align_z': 'Make on Z',
    'offset': 'Offset',
    'destructive_menu': 'Destructive Menu',
    'mode_label': 'Mode Label',
    'shape_label': 'Shape Label',
    'operation_label': 'Operation Label',
    'surface_label': 'Surface Label',
    'wire_only': 'Wires Only',
    'thick_wire': 'Thick Wire',
    'circle_vertices': 'Circle Vertices',
    'bevel_width': 'Bevel Width',
    'bevel_segments': 'Bevel Segments',
    'quad_bevel': 'Quad Bevel',
    'straight_edges': 'Straight Corner Flow',
    'inset_thickness': 'Inset Thickness',
    'solidify_thickness': 'Solidify Thickness',
    'array_count': 'Array Count',
    'lazorcut_limit': 'Lazorcut Limit',
    'quick_execute': 'Quick Execute',
    'simple_trace': 'Simple Trace',
    'edit_disable_modifiers': 'Disable Ctrl & Shift LMB (Edit Mode)',
    'enable_surface_toggle': 'Enable Surface Toggle',
    'cursor': 'Cursor',
    'transform_gizmo': 'Transform Gizmo',
    'reduce_opacity_editmode': 'Reduce Opacity in Edit',
    'scroll_adjust_circle': 'Scroll Adjust Circle',
    'cursor_axis': 'Cursor Axis'}


def active_tool():
    return view3d_tools.tool_active_from_context(bpy.context)


def activate_by_name(name):
    activate_tool(bpy.context, 'VIEW_3D', name)


def method_handler(method,
    arguments = tuple(),
    identifier = str(),
    exit_method = None,
    exit_arguments= tuple(),
    return_result = False,
    return_value = {'CANCELLED'}):
    '''
    method: method to call
    arguments: method arguments
    identifier: optional identifer for printout
    exit_method: optional exit method to call on exception
    exit_arguments: exit method arguments
    return_result: allows return of the method and values
    return_value: return value on exception
    '''
    identifier = identifier + ' ' if identifier else ''
    try:
        if return_result:
            return method(*arguments)
        else:
            method(*arguments)
    except Exception:
        print(F'\n{name} {identifier}Method Failed:\n')
        traceback.print_exc()

        if exit_method:
            try:
                if return_result:
                    return exit_method(*exit_arguments)
                else:
                    exit_method(*exit_arguments)
            except Exception:
                print(F'\n{name} {identifier}Exit Method Failed:\n')
                traceback.print_exc()

        if return_result:
            try: return return_value
            except Exception:
                print(F'\n{name} {identifier}Exit Return Value Failed:\n')
                traceback.print_exc()
