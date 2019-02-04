import os
import bpy
import rna_keymap_ui
from mathutils import Vector
from bpy.props import *
from . utils.addons import addon_exists
from . ui.addon_checker import draw_addon_diagnostics
from . utils.blender_ui import write_text, get_dpi_factor

def get_preferences():
    name = get_addon_name()
    return bpy.context.user_preferences.addons[name].preferences

def get_addon_name():
    return os.path.basename(os.path.dirname(os.path.realpath(__file__)))


# Specific preference settings

def tool_overlays_enabled():
    return get_preferences().enable_tool_overlays

def pie_placeholder_1_enabled():
    return get_preferences().pie_placeholder_1

def pie_F6_enabled():
    return get_preferences().pie_F6

def pie_bool_options_enabled():
    return get_preferences().pie_bool_options

def use_asset_manager():
    return get_preferences().Asset_Manager_Preview and addon_exists("asset_management")

def right_handed_enabled():
    return get_preferences().right_handed

def pro_mode_enabled():
    return get_preferences().pro_mode

def extra_options_enabled():
    return get_preferences().extra_options

def Relink_options_enabled():
    return get_preferences().Relink_options

def BC_unlock_enabled():
    return get_preferences().BC_unlock

def mira_handler_enabled():
    return get_preferences().mira_handler_enabled

#colors

def get_hops_preferences_colors_with_transparency(transparency):
    color_text1 = [Hops_text_color()[0], Hops_text_color()[1], Hops_text_color()[2], Hops_text_color()[3] * transparency]
    color_text2 = [Hops_text2_color()[0], Hops_text2_color()[1], Hops_text2_color()[2], Hops_text2_color()[3] * transparency]
    color_border = [Hops_border_color()[0], Hops_border_color()[1], Hops_border_color()[2], Hops_border_color()[3] * transparency]
    color_border2 = [Hops_border2_color()[0], Hops_border2_color()[1], Hops_border2_color()[2], Hops_border2_color()[3] * transparency]
    return color_text1, color_text2, color_border, color_border2

def Hops_text_color():
    return get_preferences().Hops_text_color

def Hops_text2_color():
    return get_preferences().Hops_text2_color
def Hops_border_color():
    return get_preferences().Hops_border_color

def Hops_border2_color():
    return get_preferences().Hops_border2_color

#Display Parameter Time
def Hops_display_time():
    return get_preferences().display_time

def Hops_fadeout_time():
    return get_preferences().fadeout_time

def get_color_for_drawing():

    bg2R = 0.692
    bg2G = 0.298
    bg2B = 0.137
    bg2A = 0.718

    bgR = 0.235
    bgG = 0.235
    bgB = 0.235
    bgA = 0.8

    txR = 0.6
    txG = 0.6
    txB = 0.6
    txA = 0.9

    return bg2R, bg2G, bg2B, bg2A, bgR, bgG, bgB, bgA, txR, txG, txB, txA 

#Tool Panel for update category and hide panel
def update_HardOps_Panel_Tools(self, context):
    panel = getattr(bpy.types, "hops_main_panel", None)
    if panel is not None:
        bpy.utils.unregister_class(panel)
        panel.bl_category = get_preferences().toolbar_category_name
        bpy.utils.register_class(panel)

def category_name_changed(self, context):
    category = get_preferences().toolbar_category_name
    change_hard_ops_category(category)

#edit mode properties
def Hops_circle_size():
    return get_preferences().Hops_circle_size


settings_tabs_items = [
    ("UI", "UI", ""),
    ("DRAWING", "Drawing", ""),
    ("INFO", "Info", ""),
    ("KEYMAP", "Keymap", ""),
    ("LINKS", "Links / Help", ""),
    ("ADDONS", "Addons", "") ]

class HardOpsPreferences(bpy.types.AddonPreferences):
    bl_idname = get_addon_name()

    helper_tab =  StringProperty(name = "Helper Set Category", default = "MODIFIERS")

    tab = EnumProperty(name = "Tab", items = settings_tabs_items)

    toolbar_category_name = StringProperty(name = "Toolbar Category", default = "HardOps",
            description = "Name of the tab in the toolshelf in the 3d view",
            update = category_name_changed)

    enable_tool_overlays = BoolProperty(name = "Enable Tool Overlays", default=True)
    
    mira_handler_enabled = BoolProperty(name = "Hard Ops Mira Handler", default=False)

    Asset_Manager_Preview = BoolProperty(name = "Asset Manager Preview", default=False)
    
    Diagnostics_Mode = BoolProperty(name = "Debug Mode", default=False)
    
    Relink_options = BoolProperty(name = "Re-Link Options", default=False)

    pie_placeholder_1 = bpy.props.BoolProperty(name="Pie Placeholder 1", default=False,
            description="add placehoder button to pie menu")

    pie_F6 = bpy.props.BoolProperty(name="Pie F6", default=True,
            description="add F6 button to pie menu")

    pie_bool_options = bpy.props.BoolProperty(name="Pie Bool Options", default=True,
            description="add bool button to pie menu")
    
    right_handed = bpy.props.BoolProperty(name="Right Handed", default=True,
            description="Reverse The X Mirror For Right Handed People")
    
    pro_mode = bpy.props.BoolProperty(name="Pro Mode", default=False,
            description="Enables Pro Level Hard Ops Options")
    
    extra_options = bpy.props.BoolProperty(name="Extra Options", default=False,
            description="Enables Extra Options Hidden")
            
    BC_unlock = bpy.props.BoolProperty(name="BC", default=False,
            description="BC Support")

    #Display Parameter Time
    display_time = FloatProperty(name = "Display Time", default = 1, min = 1, max = 5)
    fadeout_time = FloatProperty(name = "Fadeout Time", default = 0.8, min = 0, max = 5)
    
    #getimg theme colors
    bg2R, bg2G, bg2B, bg2A, bgR, bgG, bgB, bgA, txR, txG, txB, txA = get_color_for_drawing()

    Hops_text_color = FloatVectorProperty(
            name="", 
            default= Vector((txR, txG, txB, txA)),
            size = 4, 
            min=0, max=1,
            subtype='COLOR'
            )

    Hops_text2_color = FloatVectorProperty(
            name="", 
            default=Vector((txR, txG, txB, txA)),
            size = 4, 
            min=0, max=1,
            subtype='COLOR'
            )

    Hops_border_color = FloatVectorProperty(
            name="", 
            default=Vector((bgR, bgG, bgB, bgA)),
            size = 4, 
            min=0, max=1,
            subtype='COLOR'
            )

    Hops_border2_color = FloatVectorProperty(
            name="", 
            default=Vector((bg2R, bg2G, bg2B, bg2A)),
            size = 4, 
            min=0, max=1,
            subtype='COLOR'
            )

    #edit mode properties

    Hops_circle_size = FloatProperty(
        name="Bevel offset step",
        description = "Bevel offset step",
        default = 0.0001, min =  0.0001)

    #menu
    def draw(self, context):
        layout = self.layout

        col = layout.column(align = True)
        row = col.row()
        row.prop(self, "tab", expand = True)

        box = col.box()

        if self.tab == "UI":
            self.draw_ui_tab(box)
        elif self.tab == "ADDONS":
            self.draw_addons_tab(box)
        elif self.tab == "DRAWING":
            self.draw_drawing_tab(box)
        elif self.tab == "INFO":
            self.draw_info_tab(box)
        elif self.tab == "LINKS":
            self.draw_links_tab(box)
        elif self.tab == "KEYMAP":
            self.draw_keymap_tab(box)

    def draw_drawing_tab(self, layout):
        box = layout.box()

        row = box.row(align=True)
        row.prop(self, "enable_tool_overlays")

        box = layout.box()
        row = box.row(align=True)
        row.operator("hops.color_to_default", text = 'Hard Ops')
        row.operator("hops.color_to_theme", text = 'AR')
        row.operator("hops.color_to_theme2", text = 'ThemeGrabber')

        box = layout.box()
        row = box.row(align=True)
        row.prop(self, "Hops_text_color", text = "Main Text Color ")

        row = box.row(align=True)
        row.prop(self, "Hops_text2_color", text = "Secoundary Text Color ")

        row = box.row(align=True)
        row.prop(self, "Hops_border_color", text = "Border Color")

        row = box.row(align=True)
        row.prop(self, "Hops_border2_color", text = "Secondary Border Color")
        
        box = layout.box()
        row = box.row(align=True)
        row.prop(self, "display_time", text = "HUD Display Time (seconds)")

        row = box.row(align=True)
        row.prop(self, "fadeout_time", text = "HUD Fadeout Time (seconds)")


    def draw_ui_tab(self, layout):
        #layout.prop(self, "toolbar_category_name")
        row = layout.row()
        row.prop(self, "pro_mode")
        
        row = layout.row()
        row.prop(self, "extra_options")

        row = layout.row()
        row.prop(self, "right_handed", text = "Right Handed")
        
        if self.extra_options == True:
            row = layout.row()
            row.prop(self, "pie_F6", text = "Pie: F6 Option At Top")
            
            if addon_exists("relink"):
                row.prop(self, "pie_placeholder_1", text = "Pie: Enable Long button")
            
            row = layout.row()
            row.prop(self, "pie_bool_options", text = "Pie: Add Boolean Options")

            row = layout.row()
            if addon_exists("relink"):
                row = layout.row()
                row.label("Re-Link Found!")
                row.prop(self, "Relink_options", text = "Re-Link: Options")
                
                row = layout.row()
                row.label("Dev Options")
                row.prop(self, "Diagnostics_Mode", text = "Diagnostics: Show Info")    
        
        if addon_exists("asset_management"):
            row = layout.row()
            row.label("Asset Manager Expansion:")
            row.prop(self, "Asset_Manager_Preview", text = "Asset Manager: Add To HOps")
        
        if addon_exists("mira_tools"):
            row = layout.row()
            row.label("Mira Tools Expansion:")
            row.prop(self, "mira_handler_enabled", text = "Mira Tools: Enable Hops Handler")

    def draw_info_tab(self, layout):
        write_text(layout, info_text, width = bpy.context.region.width / get_dpi_factor() / 8)

    def draw_keymap_tab(self, layout):
        layout.label("By default (Q) is menu and (Shift+Q) is pie")
        layout.label("There is also a button to edit the script below. Not recommended")
        layout.operator("hops.open_keymap_for_editing")

    def draw_links_tab(self, layout):
        col = layout.column()
        for name, url in weblinks:
            col.operator("wm.url_open", text = name).url = url

    def draw_addons_tab(self, layout):
        draw_addon_diagnostics(layout, columns = 4)


info_text = """HardOps is a toolset to maximize hard surface efficiency. I personally wanted
this to be a toolkit for workflows of my style. But as this add-on has developed
so has my style. The support of the Hard Ops team has made this into a masterpiece.
Tools are built to be used for concept mesh creation. The goal is speed but also
fine surfaces. With bevels. Leave your topology at the door. Just have fun! There is
documentation on my blog if you have issues using it not to mention to many demos of it! Feel
free to write about improvements or getting involved! Thank you for your support.


License Code: 29468741xxxx4x5  haha just kidding! This.... is... Blender!
""".replace("\n", " ")

weblinks = [
    ("Youtube",                 "https://www.youtube.com/user/masterxeon1001/"),
    ("Gumroad",                 "https://gumroad.com/l/hardops/"),
    ("Intro Guide",             "https://masterxeon1001.wordpress.com/2016/02/23/hard-ops-007-intro-guide/"),
    ("Basic Usage",             "https://masterxeon1001.wordpress.com/hard-ops-007-basic-usage/"),
    ("Hard Ops Videos",         "https://www.youtube.com/playlist?list=PL0RqAjByAphGEVeGn9QdPdjk3BLJXu0ho"),
    ("Version 8 Notes",         "https://masterxeon1001.com/2016/05/28/hard-ops-8-release-notes/"),
]
