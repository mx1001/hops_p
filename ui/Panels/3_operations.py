import bpy
from bpy.props import *
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )
import os
from ... icons import get_icon_id
from ... utils.addons import addon_exists
from ... preferences import pro_mode_enabled

class HopsOperationsPanel(bpy.types.Panel):
    bl_label = "Operations"
    bl_category = "HardOps"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        active_object = context.active_object

        if active_object is None:
            layout.label("Select object first")
        elif active_object.mode == "OBJECT":

            layout = self.layout.column(1)           
            row = layout.row(1)
            row.operator_context = 'INVOKE_DEFAULT'
            row.operator("step.sstep", text = "(S) Step", icon_value=get_icon_id("Sstep"))
            row.operator("step.cstep", text = "(C) Step", icon_value=get_icon_id("Cstep"))

            row = layout.row(1)
            row.operator("hops.adjust_bevel", text = "(B)Width", icon_value=get_icon_id("AdjustBevel"))

            layout.separator()
            row = layout.row(1)
            row.operator("nw.a_rray", text = "(Q)Array", icon_value=get_icon_id("Qarray"))
            row.operator("hops.adjust_tthick", text = "(T)Thick", icon_value=get_icon_id("Tthick"))

            layout.separator()
            row = layout.row(1)
            row.operator("hops.draw_uv", text = "UV Preview", icon_value=get_icon_id("CUnwrap"))   
              
            row = layout.row(1)
            row.operator("hops.soft_sharpen", text = "(S) Sharpen", icon_value=get_icon_id("Ssharpen"))

            row.operator("hops.soft_sharpen", text = "(C) Sharpen", icon_value=get_icon_id("CSharpen"))
            row = layout.row(1)
            row.operator("clean.sharps", text = "Clear S/C/Sharps", icon_value=get_icon_id("CleansharpsE"))

            layout.separator()
            row.operator("view3d.clean_mesh", text = "Clean Mesh (E)", icon_value=get_icon_id("CleansharpsE"))
            row = layout.row(1)
            row.operator("hops.2d_bevel", text = "(2d)Bevel", icon_value=get_icon_id("AdjustBevel"))


        elif active_object.mode == "EDIT":
            layout.menu("view3d.symmetry_submenu", text = "Symmetrize", icon_value = get_icon_id("Xslap"))

   