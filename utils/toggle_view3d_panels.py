import bpy, time
from ..preferences import get_preferences


def collapse_3D_view_panels(tool_shelf=False, n_panel=False):
    '''Collapses N-Panel and Tool Panel\n
    Returns (original_tool_shelf, original_n_panel) '''
    
    original_tool_shelf = False
    original_n_panel = False

    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:

                    if hasattr(space, 'show_region_toolbar'):
                        if hasattr(space, 'show_region_ui'):
                            # Returns
                            original_tool_shelf = space.show_region_toolbar
                            original_n_panel = space.show_region_ui

                            # Sets
                            if get_preferences().ui.Hops_auto_hide_t_panel == True:
                                if tool_shelf != space.show_region_toolbar:
                                    space.show_region_toolbar = tool_shelf

                            if get_preferences().ui.Hops_auto_hide_n_panel == True:
                                if n_panel != space.show_region_ui:
                                    space.show_region_ui = n_panel
                        
    return (original_tool_shelf, original_n_panel)