import bpy
from . utils.addons import addon_exists
from . preferences import use_asset_manager, get_preferences, right_handed_enabled, pro_mode_enabled, Relink_options_enabled, BC_unlock_enabled


addon_keymaps = []

def register_keymap():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name = "3D View", space_type = "VIEW_3D")

    kmi = km.keymap_items.new("wm.call_menu_pie", "Q", "PRESS", shift = True)
    kmi.properties.name = "hops_main_pie"

    kmi = km.keymap_items.new("wm.call_menu", "Q", "PRESS")
    kmi.properties.name = "hops_main_menu"

    kmi = km.keymap_items.new("view3d.hops_helper_popup", "ACCENT_GRAVE", "PRESS", ctrl = True)
    kmi.properties.tab = "MODIFIERS"
    
    kmi = km.keymap_items.new("wm.call_menu", "M", "PRESS", alt = True)
    kmi.properties.name = "view3d.material_list_menu"
    
    kmi = km.keymap_items.new("wm.call_menu", "V", "PRESS", alt = True)
    kmi.properties.name = "viewport.submenu"
    
    #only add if Mirror Mirror Is Not Enabled
    if addon_exists("MirrorMirrorTool") == False:
        wm = bpy.context.window_manager
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new("hops.mirror_mirror_x", 'X', 'PRESS', alt=True, shift = True)

        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new("hops.mirror_mirror_y", 'Y', 'PRESS', alt=True, shift = True)

        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new("hops.mirror_mirror_z", 'Z', 'PRESS', alt=True, shift = True)
    
    if addon_exists("Booltool") == False:
        # handle the keymap
        wm = bpy.context.window_manager
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        
        # HOPS Boolean Hotkeys
        kmi = km.keymap_items.new("hops.bool_union", 'NUMPAD_PLUS', 'PRESS', ctrl=True, shift=False)
        kmi = km.keymap_items.new("hops.bool_difference", 'NUMPAD_MINUS', 'PRESS', ctrl=True, shift=False)
        kmi = km.keymap_items.new("hops.complex_split_boolean", 'NUMPAD_ASTERIX', 'PRESS', ctrl=True, shift=False)
        
    addon_keymaps.append(km)

def unregister_keymap():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()


# reregister keymap when this file is executed on its own
if __name__ == "__main__":
    unregister_keymap()
    register_keymap()
