import os
import bpy
from bpy.types import Menu
from ... icons import get_icon_id
from ... utils.addons import addon_exists
from ... preferences import get_preferences


class HOPS_MT_SettingsSubmenu(bpy.types.Menu):
    bl_label = 'Settings Submenu'
    bl_idname = 'HOPS_MT_SettingsSubmenu'

    def draw(self, context):
        layout = self.layout

        obj = context.object

        wm = bpy.context.window_manager
        view = context.space_data
        scene = context.scene

        row = layout.column().row()

        if get_preferences().ui.expanded_menu:
            column = row.column()
        else:
            column =self.layout

        if hasattr(wm, 'powersave'):
            column.operator("hops.powersave", text = "PowerSave",  icon_value=get_icon_id("powersave"))

        if bpy.context.space_data.show_region_tool_header == False:
            column.operator("hops.show_topbar", text = "Show Toolbar")

        #column.menu("HOPS_MT_MeshToolsSubmenu", text="Helper / Assistant",  icon_value=get_icon_id("SetFrame"))

        column.operator("hops.learning_popup", text="Hard Ops Learning", icon='HELP')

        column.separator()

        if context.active_object != None:
            if context.active_object.type == 'CAMERA':
                cam = bpy.context.space_data

                #col.label(text="Lock Camera To View")
                column.prop(cam, "lock_camera", text="Lock To View")

                column.separator()

        if context.active_object and context.active_object.type == 'MESH':
            #Wire/Solid Toggle
            if context.object.display_type == 'WIRE':
                column.operator("object.solid_all", text="Shade Solid", icon='MESH_CUBE')
            else :
                column.operator("showwire.objects", text="Shade Wire", icon='OUTLINER_OB_LATTICE')

#            column.operator_context = 'INVOKE_DEFAULT'
#            column.operator("hops.draw_uv", text="UV Preview", icon_value=get_icon_id("CUnwrap"))

#            if pro_mode_enabled():
#                column.operator("hops.viewport_buttons", text="Dots", icon_value=get_icon_id("dots"))

#            if len(context.selected_objects) == 1:
#                column.menu("HOPS_MT_BasicObjectOptionsSubmenu", text="Object Options")

        column.prop(view.overlay, 'show_wireframes')

        column.separator()

        column.operator("hops.evict", text="Manage", icon_value=get_icon_id("GreyDisplay_dots"))

        column.separator()

        column.operator_context = 'INVOKE_DEFAULT'
        column.operator("hops.adjust_viewport", text="LookDev+", icon_value=get_icon_id("RGui"))

        column.menu("HOPS_MT_ViewportSubmenu", text="ViewPort", icon_value=get_icon_id("WireMode"))

        if get_preferences().ui.expanded_menu:
            column = row.column()
        else:
            column.separator()
        #column.separator()

        #Voxelization Addition 2.81
        if context.active_object and context.active_object.type == 'MESH':

            column.prop(context.active_object.data, 'remesh_voxel_size', text='Voxel Size')

            column.operator("view3d.voxelizer", text=F"Voxelize Object", icon_value=get_icon_id("Voxelize"))

        #col.prop(scene, 'frame_end')

        column.separator()

        column.menu("HOPS_MT_FrameRangeSubmenu", text="Frame Range Options",  icon_value=get_icon_id("SetFrame"))

        column.menu("HOPS_MT_Export", text = 'Export', icon_value=get_icon_id("Tris"))

        column.separator()

        #Order Pizza Button Haha
        #column.operator("view3d.pizzapopup", text="Pizza Ops", icon_value=get_icon_id("Pizzaops"))
        column.operator("hops.pizza_ops_window", text="Pizza Ops", icon_value=get_icon_id("Pizzaops"))
        
        column.separator()

        column.operator("hops.pref_helper", text = "Keymap / Prefs",  icon='EVENT_Q')

        if get_preferences().needs_update:
            column.operator("hops.about", text = "About",  icon_value=get_icon_id("logo_red"))
        else:
            column.operator("hops.about", text = "About",  icon_value=get_icon_id("sm_logo_white"))

        # ot = column.operator("hops.display_notification", text="Notification")
        # ot.info = "Test Is working"
