import bpy
from bpy.props import *
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )
import os
from ... icons import get_icon_id
from ... preferences import  pro_mode_enabled
from ... utils.objects import get_inactive_selected_objects

class HopsDynamicToolsPanel(bpy.types.Panel):
    bl_label = "Dynamic tools"
    bl_category = "HardOps"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout
        active_object = context.active_object

        if active_object is None:
            layout.label("Select object first")
        elif active_object.mode == "OBJECT":
            if active_object.type == "LATTICE":
                self.draw_lattice_menu(layout)
            elif active_object.type == "CURVE":
                self.draw_curve_menu(layout)
            elif active_object.type == "LAMP":
                self.draw_lamp_menu(layout)
            elif active_object.type == "CAMERA":
                self.draw_camera_menu(layout)
            elif active_object.hops.status == "BOOLSHAPE":
                self.draw_boolshape_menu(layout)
            elif active_object.type == "MESH":
                self.draw_object_mode_menu(layout)
            else:
                pass
        elif active_object.mode == "EDIT":
            if active_object.type == "MESH":
                self.draw_edit_mode_menu(layout, active_object)
            else:
                pass
        elif active_object.mode == "POSE":
            self.draw_rigging_menu(layout)
        elif active_object.mode == "SCULPT":
            self.draw_sculpt_menu(layout)
            


    # Object Mode
    ############################################################################

    def draw_object_mode_menu(self, layout):
        active_object, other_objects, other_object = get_current_selected_status()
        only_meshes_selected = all(object.type == "MESH" for object in bpy.context.selected_objects)

        object = bpy.context.active_object

        if len(bpy.context.selected_objects) == 1:  
            if object.hops.status in ("CSHARP", "SUBSHARP"):
                if active_object is not None and other_object is None and only_meshes_selected:
                        self.draw_only_with_active_object_is_csharpen(layout, active_object)

            if object.hops.status == "CSTEP":
                if active_object is not None and other_object is None and only_meshes_selected:
                    self.draw_only_with_active_object_is_cstep(layout, active_object)

            if object.hops.status == "UNDEFINED":
                if active_object is not None and other_object is None and only_meshes_selected:
                    if active_object.name.startswith("AP_"):
                        self.draw_only_with_AP_as_active_object(layout, active_object)
                    else:
                        self.draw_only_with_active_object(layout, active_object)         


        elif len(bpy.context.selected_objects) == 2:  
            
            selected = bpy.context.selected_objects
            active = bpy.context.active_object
            selected.remove(active)
            object = selected[0]

            if object.hops.is_for_merge:
                if active_object is not None and other_object is not None and only_meshes_selected:
                    self.draw_with_active_object_and_other_mesh_for_merge(layout, active_object, other_object)

            elif object.hops.is_for_softmerge:
                if active_object is not None and other_object is not None and only_meshes_selected:
                    self.draw_with_active_object_and_other_mesh_for_softmerge(layout, active_object, other_object)

            else:
                if active_object is not None and other_object is not None and only_meshes_selected:
                    self.draw_with_active_object_and_other_mesh(layout, active_object, other_object)


        elif len(bpy.context.selected_objects) > 2:

            self.draw_with_active_object_and_other_mesh(layout, active_object, other_object)

        else:
            self.draw_without_active_object(layout)
            layout.separator()
            layout.menu("settings.submenu", text="Settings", icon_value=get_icon_id("Gui"))

    def draw_without_active_object(self, layout):
        layout.label("Select object first")

    def draw_only_with_AP_as_active_object(self, layout, object):
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator("hops.copy_merge", text = "Copy Merge", icon_value=get_icon_id("Merge"))
        layout.operator("hops.remove_merge", text = "coming soon", icon_value=get_icon_id("Merge"))
        layout.operator("hops.remove_merge", text = "Remove Merge", icon_value=get_icon_id("Merge"))

    def draw_only_with_active_object(self, layout, object):
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator("hops.soft_sharpen", text = "(S) Sharpen", icon_value=get_icon_id("Ssharpen"))
        layout.operator("hops.complex_sharpen", text = "(C) Sharpen", icon_value=get_icon_id("CSharpen"))
        object = bpy.context.active_object
        if object.hops.is_pending_boolean:
            layout.operator("reverse.boolean", text = "(Re)Bool", icon_value=get_icon_id("ReBool"))
        else:
            layout.operator("hops.adjust_tthick", text = "(T)Thick", icon_value=get_icon_id("Tthick"))

    def draw_only_with_active_object_is_csharpen(self, layout, object):
        object = bpy.context.active_object
        layout.operator_context = "INVOKE_DEFAULT"
        if object.hops.is_pending_boolean:
            layout.operator("hops.complex_sharpen", text = "(C) Sharpen", icon_value=get_icon_id("CSharpen"))
            layout.operator("hops.adjust_bevel", text = "(B)Width", icon_value=get_icon_id("AdjustBevel"))
            layout.operator("reverse.boolean", text = "(Re)Bool", icon_value=get_icon_id("ReBool"))
        else:
            layout.operator("hops.soft_sharpen", text = "(S) Sharpen", icon_value=get_icon_id("Ssharpen"))
            layout.operator("hops.adjust_bevel", text = "(B)Width", icon_value=get_icon_id("AdjustBevel"))
            layout.operator("step.cstep", text = "(C) Step", icon_value=get_icon_id("Cstep"))

        
    def draw_only_with_active_object_is_cstep(self, layout, object):
        object = bpy.context.active_object
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator("step.sstep", text = "(S) Step", icon_value=get_icon_id("Sstep"))
        if object.hops.is_pending_boolean:
            layout.operator("reverse.bools", text = "(Re)Bool-Sstep", icon_value=get_icon_id("ReBool"))
        else:
            layout.operator("hops.adjust_bevel", text = "(B)Width", icon_value=get_icon_id("AdjustBevel"))
        layout.operator("step.cstep", text = "(C) Step", icon_value=get_icon_id("Cstep"))

    def draw_with_active_object_and_other_mesh(self, layout, active_object, other_object):
        object = bpy.context.active_object
        layout.operator_context = "INVOKE_DEFAULT" 
        if object.hops.status == "CSTEP":
            layout.operator("step.sstep", text = "(S) Step", icon_value=get_icon_id("Sstep"))
        else:
            layout.operator("hops.complex_sharpen", text = "(C) Sharpen", icon_value=get_icon_id("CSharpen"))
        layout.operator("hops.complex_split_boolean", text = "(C)Slice", icon_value=get_icon_id("Csplit"))
        layout.operator("step.cstep", text = "(C) Step", icon_value=get_icon_id("Cstep"))

    def draw_with_active_object_and_other_mesh_for_merge(self, layout, active_object, other_object):
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator("hops.parent_merge", text = "(C) merge", icon_value = get_icon_id("Merge"))
        layout.operator("hops.simple_parent_merge", text = "(S) merge", icon_value=get_icon_id("Merge"))
        layout.operator("hops.remove_merge", text = "Remove Merge", icon_value=get_icon_id("Merge"))

    def draw_with_active_object_and_other_mesh_for_softmerge(self, layout, active_object, other_object):
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator("hops.parent_merge_soft", text = "(C) merge(soft)", icon_value = get_icon_id("CSharpen"))
        layout.operator("hops.complex_split_boolean", text = "(C)Slice", icon_value=get_icon_id("Csplit"))
        layout.operator("hops.remove_merge", text = "Remove Merge", icon_value=get_icon_id("CSharpen"))

    def draw_options(self, layout):
        layout.separator()
        layout.menu("protomenu.submenu", text = "Operations", icon_value=get_icon_id("Noicon"))
        layout.separator()
        layout.menu("view3d.mstool_submenu", text = "MeshTools", icon_value=get_icon_id("Noicon"))
        layout.menu("inserts.objects", text="Insert", icon_value=get_icon_id("Noicon"))
        layout.menu("settings.submenu", text="Settings", icon_value=get_icon_id("Noicon"))



    # Edit Mode
    ############################################################################

    def draw_edit_mode_menu(self, layout, object):
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("bevelandsharp1.objects", text = "Make SSharp", icon_value = get_icon_id("MakeSharpE"))
        if pro_mode_enabled():
            layout.operator("transform.edge_bevelweight", text = "Bweight", icon_value = get_icon_id("AdjustBevel"))
        layout.operator("clean1.objects", text = "Clean SSharps", icon_value = get_icon_id("CleansharpsE")).clearsharps = True

    # Sculpt Menu
    ############################################################################
    def draw_sculpt_menu(self, layout):
        layout.menu("hops_sculpt.submenu", text = "Sculpt")

    # Lamp Menu
    ############################################################################

    def draw_lamp_menu(self, layout):
        #bpy.ops.wm.context_modal_mouse(data_path_iter="selected_editable_objects", data_path_item="data.node_tree.nodes[\"Emission\"].inputs[\"Strength\"].default_value", header_text="Lamp Strength: %.3f", input_scale=0.1)
        #bpy.ops.wm.context_modal_mouse(data_path_iter="selected_editable_objects", data_path_item="data.shadow_soft_size", header_text="Lamp Size: %.3f")
        layout.label("No Lamp Options Yet")
        
    # Camera Menu
    ############################################################################

    def draw_camera_menu(self, layout):
        #cam = bpy.context.space_data
        obj = bpy.context.object
        
        row = layout.row(align=False)
        col = row.column(align=True)

        obj = bpy.context.object.data
        col.prop(obj, "lens", text = "Lens")
        col.prop(obj, "passepartout_alpha", text = "PP")
        col.prop(obj, "dof_object", text = "")
        
        obj = bpy.context.object.data.cycles
        col.prop(obj, "aperture_size", text = "DOF Size")
        
        layout.separator()
        
        #col.label("Color Options")
        #obj = bpy.data.scenes["Scene"].view_settings
        #col.prop(obj, "view_transform", text = "")
        #col.prop(obj, "look", text = "")
        layout.operator("hops.set_camera", text = "Set Active Cam") 
                
        layout.separator()
        layout.menu("settings.submenu", text="Settings", icon_value=get_icon_id("Noicon"))

        
    # Lattice Mode
    ############################################################################

    def draw_lattice_menu(self, layout):
        layout.prop(bpy.context.object.data, "points_u", text="X")
        layout.prop(bpy.context.object.data, "points_v", text="Y")
        layout.prop(bpy.context.object.data, "points_w", text="Z")
        layout.prop(bpy.context.object.data, "use_outside")
        layout.operator("hops.simplify_lattice", text = "Simplify")
        #self.draw_options(layout)
        layout.separator()
        layout.menu("settings.submenu", text="Settings", icon_value=get_icon_id("Noicon"))

     # BoolShape Menu
    ############################################################################

    def draw_boolshape_menu(self, layout):
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator("hops.adjust_bevel", text = "(B)Width", icon_value=get_icon_id("AdjustBevel"))
        layout.operator("hops.adjust_tthick", text = "(T)Thick", icon_value=get_icon_id("Tthick"))
        layout.operator("nw.a_rray", text = "(Q)Array", icon_value=get_icon_id("Qarray"))
        layout.separator()
        #layout.menu("protomenu.submenu", text = "Operations", icon_value=get_icon_id("Noicon"))
        #layout.separator()
        layout.menu("view3d.mstool_submenu", text = "MeshTools", icon_value=get_icon_id("Noicon"))
        layout.menu("settings.submenu", text="Settings", icon_value=get_icon_id("Noicon"))
        

    def draw_curve_menu(self, layout):
        layout.operator("hops.curve_bevel", text = "Curve bevel")
        
    def draw_rigging_menu(self, layout):
        layout.operator("object.create_driver_constraint", text = "Driver Constraint")

def get_current_selected_status():
    active_object = bpy.context.active_object
    other_objects = get_inactive_selected_objects()
    other_object = None
    if len(other_objects) == 1:
            other_object = other_objects[0]

    return active_object, other_objects, other_object
