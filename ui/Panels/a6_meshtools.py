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

class HOPS_PT_MeshToolsPanel(bpy.types.Panel):
    bl_label = "Meshtools"
    # bl_category = "HardOps"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        active_object = context.active_object

        if active_object is None:
            layout.label(text="Select object first")
        elif active_object.mode == "OBJECT":

            layout = self.layout.column(1)

            layout.operator("hops.reset_status", text="StatusReset")
            layout.operator("hops.helper", text="Modifier Helper", icon="SCRIPTPLUGINS")
            layout.separator()
            layout.operator("array.twist", text="Twist 360", icon_value=get_icon_id("ATwist360"))
            layout.operator("nw.radial_array", text="Radial 360", icon_value=get_icon_id("ATwist360"))
            layout.separator()
            if bpy.context.object and bpy.context.object.type == 'MESH':
                layout.menu("HOPS_MT_MaterialListMenu", icon_value=get_icon_id("Noicon"))
            layout.separator()
            layout.menu("HOPS_MT_ResetAxiSubmenu", text="Reset Axis", icon_value=get_icon_id("Xslap"))
            layout.separator()
            layout.menu("HOPS_MT_SymmetrySubmenu", text="Symmetry Options", icon_value=get_icon_id("Xslap"))
            layout.separator()
            layout.operator("hops.xunwrap", text="(X) Unwrap", icon_value=get_icon_id("CUnwrap"))
            layout.separator()
            layout.operator("clean.reorigin", text="(S) Clean Recenter", icon_value=get_icon_id("SCleanRecenter"))

            layout.operator("stomp2.object", text="ApplyAll (-L)", icon_value=get_icon_id("Applyall"))


        elif active_object.mode == "EDIT":
            layout = self.layout.column(1)

            layout.menu("HOPS_MT_edgeWizardSubmenu", text="(E)Wizard")

            layout.operator_context = 'INVOKE_DEFAULT'
            layout.operator("hops.draw_uv", text="UV Preview", icon_value=get_icon_id("CUnwrap"))

            layout.operator("view3d.vertcircle", text="Circle(E)", icon_value=get_icon_id("CircleSetup")).nth_mode = False

            layout.operator("view3d.vertcircle", text="Circle (Nth)(E)", icon_value=get_icon_id("NthCircle")).nth_mode = True

            layout.separator()

            layout.operator("fgrate.op", text="Grate (Face)", icon_value=get_icon_id("FaceGrate"))

            layout.operator("fknurl.op", text="Knurl (Face)", icon_value=get_icon_id("FaceKnurl"))

            layout.separator()

            layout.operator("quick.panel", text="Panel (Face)", icon_value=get_icon_id("EdgeRingPanel"))

            layout.operator("entrench.selection", text="Panel (Edge)", icon_value=get_icon_id("FacePanel"))

            if any("mira_tools" in s for s in bpy.context.preferences.addons.keys()):
                layout.separator()
                layout.menu("HOPS_MT_MiraSubmenu", text="Mira (T)", icon="PLUGIN")
            else:
                layout.separator()
