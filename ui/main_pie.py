import bpy
import os
from .. icons import get_icon_id, icons
from .. utils.addons import addon_exists
from .. preferences import use_asset_manager, get_preferences, pie_placeholder_1_enabled, pie_F6_enabled, pie_bool_options_enabled
from .. utils.objects import get_inactive_selected_objects

class HOpsMainPie(bpy.types.Menu):
    bl_idname = "hops_main_pie"
    bl_label = "Hard Ops 0087"

    def draw(self, context):
        layout = self.layout
        active_object = context.active_object

        if active_object is None:
            self.draw_without_active_object_pie(layout)
        elif active_object.mode == "OBJECT":
            if active_object.hops.status == "BOOLSHAPE":
                self.draw_boolshape_menu(layout)
            else:
                if active_object.type == "LATTICE":
                    self.draw_lattice_menu(layout)
                elif active_object.type == "CURVE":
                    self.draw_curve_menu(layout)
                else:
                    self.draw_object_mode_pie(layout)
        elif active_object.mode == "EDIT":
            self.draw_edit_mode_pie(layout, active_object)
        elif active_object.mode == 'POSE':
            self.draw_rigging_menu(layout)

    # Without Selection
    ############################################################################

    def draw_without_active_object_pie(self, layout):
        wm = bpy.context.window_manager
        pie = self.layout.menu_pie()
        group = pie.column()
        box = group.box()
        row = box.row()
        row.operator("view3d.asset_scroller_window", "(HOps)")
        row = box.row()
        row.template_icon_view(wm, "Hard_Ops_previews")
        row.template_icon_view(wm, "sup_preview")

        pie.separator()
        if addon_exists("asset_management"):
            box = pie.box()
            col = box.column()
            asset_manager = wm.asset_m
            col.prop(asset_manager, "libraries", text = "")
            col.prop(asset_manager, "categories", text = "")
            col.template_icon_view(wm, "AssetM_previews", show_labels = True)
        #ol.separator()
        else:
            pie.separator()

        #top
        pie.separator()
        pie.separator()

        box = pie.box()
        col = box.column()
        col.menu("renderSet.submenu", text="RenderSets")#, icon_value=get_icon_id("Gui"))
        col.menu("viewport.submenu", text="ViewPort")#, icon_value=get_icon_id("Viewport"))
        #col.menu("settings.submenu", text="Settings")#, icon_value=get_icon_id("Gui"))

        pie.separator()
        pie.separator()




    # Always
    ############################################################################





    # Object Mode
    ############################################################################

    def draw_object_mode_pie(self, layout):
        active_object, other_objects, other_object = get_current_selected_status()
        only_meshes_selected = all(object.type == "MESH" for object in bpy.context.selected_objects)

        object = bpy.context.active_object
        pie = self.layout.menu_pie()

        if len(bpy.context.selected_objects) == 1:  

            if object.hops.status in ("CSHARP", "SUBSHARP"):
                if active_object is not None and other_object is None and only_meshes_selected:
                        self.drawpie_only_with_active_object_is_csharpen(layout, active_object)

            if object.hops.status == "CSTEP":
                if active_object is not None and other_object is None and only_meshes_selected:
                    self.drawpie_only_with_active_object_is_cstep(layout, active_object)

            if object.hops.status == "UNDEFINED":
                if active_object is not None and other_object is None and only_meshes_selected:
                    if active_object.name.startswith("AP_") :
                        self.drawpie_only_with_AP_as_active_object(layout, active_object)
                    else:
                        self.drawpie_only_with_active_object(layout, active_object)


        elif len(bpy.context.selected_objects) == 2:  
            
            selected = bpy.context.selected_objects
            active = bpy.context.active_object
            selected.remove(active)
            object = selected[0]

            if object.hops.is_for_merge:
                if active_object is not None and other_object is not None and only_meshes_selected:
                    self.drawpie_with_active_object_and_other_mesh_for_merge(layout, active_object, other_object)

            elif object.hops.is_for_softmerge:
                if active_object is not None and other_object is not None and only_meshes_selected:
                    self.drawpie_with_active_object_and_other_mesh_for_softmerge(layout, active_object, other_object)

            else:
                if active_object is not None and other_object is not None and only_meshes_selected:
                    self.drawpie_with_active_object_and_other_mesh(layout, active_object, other_object)

        elif len(bpy.context.selected_objects) > 2:

            self.drawpie_with_active_object_and_other_mesh(layout, active_object, other_object)


        else:
            self.draw_without_active_object_pie(layout)

    def drawpie_only_with_AP_as_active_object(self, layout, object):
        pie = self.layout.menu_pie()
        pie.operator("hops.remove_merge", text = "Remove Merge")#, icon_value=get_icon_id("Merge"))
        pie.separator()
        pie.operator("hops.copy_merge", text = "Copy Merge")#, icon_value=get_icon_id("Merge"))
        self.draw_f6_option(layout)
        pie.separator()
        self.drawpie_options(layout)
        pie.operator("hops.remove_merge", text = "coming soon")#, icon_value=get_icon_id("Merge"))
        pie.separator()


    def drawpie_only_with_active_object(self, layout, object):
        pie = self.layout.menu_pie()
        object = bpy.context.active_object
        if object.hops.is_pending_boolean:
            pie.operator("reverse.boolean", text = "(Re)Bool")#, icon_value=get_icon_id("ReBool"))
        else:
            pie.operator("hops.adjust_tthick", text = "(T)Thick")#, icon_value=get_icon_id("Tthick"))
        pie.separator()
        pie.operator("hops.soft_sharpen", text = "(S) Sharpen")#, icon_value=get_icon_id("Ssharpen"))
        self.draw_f6_option(layout)
        pie.separator()
        self.drawpie_options(layout)
        pie.operator("hops.complex_sharpen", text = "(C) Sharpen")#, icon_value=get_icon_id("CSharpen"))
        pie.separator()


    def draw_boolshape_menu(self, layout):
        pie = self.layout.menu_pie()

        pie.operator("hops.adjust_tthick", text = "(T)Thick")#, icon_value=get_icon_id("ReBool"))
        pie.separator()
        pie.operator("nw.a_rray", text = "(Q)Array")#, icon_value=get_icon_id("CSharpen"))
        self.draw_f6_option(layout)
        pie.separator()
        self.drawpie_options(layout)
        pie.operator("hops.adjust_bevel", text = "(B)Width")#, icon_value=get_icon_id("AdjustBevel"))
        pie.separator()

    def drawpie_only_with_active_object_is_csharpen(self, layout, object):
        pie = self.layout.menu_pie()
        object = bpy.context.active_object
        if object.hops.is_pending_boolean:

            pie.operator("reverse.boolean", text = "(Re)Bool")#, icon_value=get_icon_id("ReBool"))
            pie.separator()
            pie.operator("hops.complex_sharpen", text = "(C) Sharpen")#, icon_value=get_icon_id("CSharpen"))
            self.draw_f6_option(layout)
            pie.separator()
            self.drawpie_options(layout)
            pie.operator("hops.adjust_bevel", text = "(B)Width")#, icon_value=get_icon_id("AdjustBevel"))
            pie.separator()
        else:
            pie.operator("step.cstep", text = "(C) Step")#, icon_value=get_icon_id("Cstep"))
            pie.separator()
            pie.operator("hops.soft_sharpen", text = "(S) Sharpen")#, icon_value=get_icon_id("Ssharpen"))
            self.draw_f6_option(layout)
            pie.separator()
            self.drawpie_options(layout)
            pie.operator("hops.adjust_bevel", text = "(B)Width")#, icon_value=get_icon_id("AdjustBevel"))
            pie.separator()


    def drawpie_only_with_active_object_is_cstep(self, layout, object):
        pie = self.layout.menu_pie()
        object = bpy.context.active_object

        pie.operator("step.cstep", text = "(C) Step")#, icon_value=get_icon_id("Cstep"))
        pie.separator()
        pie.operator("step.sstep", text = "(S) Step")#, icon_value=get_icon_id("Sstep"))
        self.draw_f6_option(layout)
        pie.separator()
        self.drawpie_options(layout)
        if object.hops.is_pending_boolean:
            pie.operator("reverse.bools", text = "(Re)Bool-Sstep")#, icon_value=get_icon_id("ReBool"))
        else:
            pie.operator("hops.adjust_bevel", text = "(B)Width")#, icon_value=get_icon_id("AdjustBevel"))
        pie.separator()

    def drawpie_with_active_object_and_other_mesh(self, layout, active_object, other_object):
        pie = self.layout.menu_pie()
        object = bpy.context.active_object

        pie.operator("step.cstep", text = "(C) Step")#, icon_value=get_icon_id("Cstep"))
        pie.separator()
        if object.hops.status == "CSTEP":
            pie.operator("step.sstep", text = "(S) Step")#, icon_value=get_icon_id("Sstep"))
        else:
            pie.operator("hops.complex_sharpen", text = "(C) Sharpen")#, icon_value=get_icon_id("CSharpen"))
        self.draw_f6_option(layout)
        self.drawpie_bool_options(layout)
        self.drawpie_options(layout)
        pie.operator("hops.complex_split_boolean", text = "(C)Split")#, icon_value=get_icon_id("Csplit"))
        pie.separator()


    def drawpie_with_active_object_and_other_mesh_for_merge(self, layout, active_object, other_object):
        pie = self.layout.menu_pie()

        pie.operator("hops.remove_merge", text = "Remove Merge")#, icon_value=get_icon_id("Merge"))
        pie.separator()
        pie.operator("hops.parent_merge", text = "(C) merge")#, icon_value = get_icon_id("Merge"))
        self.draw_f6_option(layout)
        pie.separator()
        self.drawpie_options(layout)
        pie.operator("hops.simple_parent_merge", text = "(S) merge")#, icon_value=get_icon_id("Merge"))
        pie.separator()




    def drawpie_with_active_object_and_other_mesh_for_softmerge(self, layout, active_object, other_object):
        pie = self.layout.menu_pie()

        pie.operator("hops.remove_merge", text = "Remove Merge")#, icon_value=get_icon_id("CSharpen"))
        pie.separator()
        pie.operator("hops.parent_merge_soft", text = "Merge(soft)")#, icon_value = get_icon_id("CSharpen"))
        self.draw_f6_option(layout)
        pie.separator()
        self.drawpie_options(layout)
        pie.operator("hops.complex_split_boolean", text = "(C)Split")#, icon_value=get_icon_id("Csplit"))
        pie.separator()

    def drawpie_options(self, layout): 
        pie = self.layout.menu_pie() 
        split = pie.box().split(align=True) 
        col = split.column(align=True)  
        col.menu("protomenu.submenu", text = "Operations")
        col.menu("view3d.mstool_submenu", text = "MeshTools")
        col.menu("inserts.objects", text="Insert")
        col.menu("settings.submenu", text="Settings")

    def drawpie_bool_options(self, layout): 
        pie = self.layout.menu_pie()     
        if pie_bool_options_enabled():
            row = pie.row() 
            row.operator("hops.bool_intersect", text="Intersection")
            row.operator("hops.bool_union", text="Union")
            row.operator("hops.bool_difference", text="Difference")
        else:
            pie.separator()

    def draw_f6_option(self, layout):
        pie = self.layout.menu_pie()
        if pie_F6_enabled():
            pie.operator("screen.redo_last", text="F6", icon='SCRIPTWIN')
        else:
            pie.separator()

    def draw_lattice_menu(self, layout):
        pie = self.layout.menu_pie()

        pie.row().prop(bpy.context.object.data, "points_u", text="X")
        pie.operator("hops.simplify_lattice", text = "Simplify")
        pie.row().prop(bpy.context.object.data, "points_v", text="Y")
        self.draw_f6_option(layout)
        pie.separator()
        pie.prop(bpy.context.object.data, "use_outside")
        pie.row().prop(bpy.context.object.data, "points_w", text="Z")
        pie.separator()

    def draw_curve_menu(self, layout):
        pie = self.layout.menu_pie()
        pie.operator("hops.adjust_curve", text = "Adjust Curve")
        pie.separator()
        pie.separator()
        pie.separator()
        pie.separator()
        self.drawpie_options(layout)
        pie.operator("hops.curve_bevel", text = "Curve bevel")
        pie.separator()

       
        
    def draw_rigging_menu(self, layout):
        pie = self.layout.menu_pie()
        pie.separator()
        pie.separator()
        pie.separator()
        pie.separator()
        pie.separator()
        self.drawpie_options(layout)
        pie.operator("object.create_driver_constraint", text = "Driver Constraint")
        pie.separator()


    # Edit Mode
    ############################################################################

    def draw_edit_mode_pie(self, layout, object):
        pie = self.layout.menu_pie()  
        #left
        pie.operator("hops.star_connect", text = "Star Connect")
        #right
        pie.separator()
        #bot
        pie.operator("hops.set_edit_sharpen", text = "Set Sharp")
        #top
        pie.separator()
        #top L
        pie.separator()
        #top R
        split = pie.box().split(align=True) 
        col = split.column()   
        col.menu("view3d.emstool_submenu", text = "MeshTools")
        if addon_exists("mira_tools"):
            col.menu("mira.submenu", text = "Mira (T)")
        #col.operator("ehalfslap.object", text = "xSymmetrize")#, icon_value = get_icon_id("Xslap"))
        col.menu("view3d.symmetry_submenu", text = "Symmetrize") 
        if object.data.show_edge_crease == False:
            col.operator("object.showoverlays", text = "Show Overlays", icon = "RESTRICT_VIEW_ON")
        else :
            col.operator("object.hide_overlays", text = "Hide Overlays", icon = "RESTRICT_VIEW_OFF")
        col.menu("inserts.objects", text = "Insert")
        #bot L
        pie.operator("hops.bevel_weight", text = "(B)Weight")
        #bot R 
        pie.operator("hops.circle", text = "Circle")

def get_current_selected_status():
    active_object = bpy.context.active_object
    other_objects = get_inactive_selected_objects()
    other_object = None
    if len(other_objects) == 1:
            other_object = other_objects[0]

    return active_object, other_objects, other_object