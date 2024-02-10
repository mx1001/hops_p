'''
Copyright (C) 2015 masterxeon1001
masterxeon1001@gmail.com

Created by masterxeon1001 and team

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


bl_info = {
    "name": "Hard Ops 9",
    "description": "Hard Ops 9 - MercuryX",
    "author": "AR / MX, proxe, bonjorno7, Neerhom / c0, ST3, General Ginsu, MACHIN3, Jacques Lucke, Ivan Santic, Robert Fornoff, Johnathan Mueller, Batfinger, SE, PL, MKB, CGStrive, PG, AX, Adam K, WZ, PW, and you",
    "version": (0, 9, 86, 15),
    "blender": (2, 83, 0),
    "location": "View3D",
    # "warning": "Hard Ops - The Global Bevelling Offensive V 007x",
    "wiki_url": "https://masterxeon1001.com/2020/06/12/hard-ops-986-mercury-release/",
    "category": "3D View"}


if 'bpy' in locals():
    print('HOPS Reloading')
    from importlib import reload
    import sys
    for k, v in list(sys.modules.items()):
        if k.startswith('HOps.'):
            reload(v)

# from . import developer_utils

import bpy,bgl,blf
from bpy.utils import register_class, unregister_class
from .registration import register_all, unregister_all
from .extend_bpy_types import *
# from .preferences import *
from .material import *
from .mesh_check import *
from .ui_popup import *

from .graphics.rectangle import *

from .icons.__init__ import *

from .legacy.ops_meshtools import *
from .legacy.ops_misc import *
from .legacy.ops_sets import *
from .legacy.ops_sharpeners import *

from .operators.modifiers import simple_deform, triangulate, uv_project, weighted_normal, wireframe, displace, subsurf, screw, weld, lattice, decimate, Apply_modfiers, shrinkwrap, skin, cast, mask, hook, smooth, l_smooth

from .operators.booleans.bool_modal import *
from .operators.booleans.bool_shift import *
from .operators.booleans.utility import *
# from .operators.booleans.bool_intersect import *
# from .operators.booleans.bool_union import *
# from .operators.booleans.bool_knife import *
# from .operators.booleans.bool_inset import *
from .operators.booleans.bool_dice import *
from .operators.booleans.editmode_difference import *
from .operators.booleans.editmode_union import *
from .operators.booleans.editmode_intersect import *
from .operators.booleans.editmode_knife import *
from .operators.booleans.editmode_slash import *
from .operators.booleans.editmode_inset import *

from .operators.cutters.complex_split_boolean import *
from .operators.cutters.cutin import *
# from .operators.cutters.slash import *

from .operators.editmode.analysis import *
from .operators.editmode.bevel_weight import *
from .operators.editmode.circle import *
from .operators.editmode.set_bevel_weight import *
from .operators.editmode.star_connect import *
from .operators.editmode.to_curve import *
from .operators.editmode.to_rope import *

from .operators.Gizmos.mirror import *
from .operators.Gizmos.main import *
from .operators.Gizmos.array import *

#GP Addition
from.operators.grease.gp_copymove import *
from.operators.grease.gp_surfaceoffset import *

from .operators.meshtools.mesh_clean import *
from .operators.meshtools.meshtools import *
from .operators.meshtools.sclean_rc import *
from .operators.meshtools.applymod import *
from .operators.meshtools.voxelizer import *
from .operators.meshtools.curve_extrude import *
from .operators.meshtools.curve_draw import *
from .operators.meshtools.flatten_to_face import *
from .operators.meshtools.mesh_align import *
from .operators.meshtools.selection_to_boolean import *
from .operators.meshtools.selection_to_boolean_v2 import *
from .operators.meshtools.vertext_align import HOPS_OT_VertextAlign
from .operators.meshtools.selection_tool import HOPS_OT_FastMeshEditor
from .operators.meshtools.add_object_to_selection import HOPS_OT_SelectedToSelection

from .operators.misc.logo_transform import *
from .operators.misc.about import *
from .operators.misc.bevel_multiplier import *
from .operators.misc.boolshape_status_swap import *
from .operators.misc.curve_toolsV1 import *
from .operators.misc.decalmachinefix import *
from .operators.misc.empty_image_tools import *
from .operators.misc.evict import *
from .operators.misc.pizza_ops import HOPS_OT_Pizza_Ops_Window
from .operators.misc.late_parent import *
from .operators.misc.mesh_reset import *
from .operators.misc.mirror_array import *
from .operators.misc.mesh_toolsV2 import HOPS_OT_SimplifyLattice, HOPS_OT_SetAsAam, HOPS_OT_meshdispOperator
from .operators.meshtools.twist360 import *
from .operators.misc.meshtool_uni import *
from .operators.misc.mirrormirror import *
from .operators.misc.misc import *
from .operators.misc.notif_display import *
from .operators.misc.open_keymap_for_editing import *
from .operators.misc.reset_axis import *
from .operators.misc.scroll_multi import *
from .operators.misc.shrinkwrap import *
from .operators.misc.shrinkwrap2 import *
from .operators.misc.sphere_cast import *
from .operators.misc.to_shape import *
from .operators.misc.to_plane import *
from .operators.misc.toggle_bools import *
from .operators.misc.triangulate_ngons import *

from .operators.modals.adjust_array import *
from .operators.modals.radial_array import *
from .operators.modals.adjust_bevel import *
from .operators.modals.adjust_bevel2d import *
from .operators.modals.adjust_curve import *
from .operators.modals.adjust_auto_smooth import *
from .operators.modals.adjust_viewport import *
from .operators.modals.adjust_tthick import *
from .operators.modals.bool_object_scroll import *
from .operators.modals.modifier_scroll import *
from .operators.modals.curve_guide_setup import *
from .operators.modals.curve_guide_setup import *
from .operators.modals.curve_stretch_setup import *
from .operators.modals.mirror import *
from .operators.modals.reset_axis import *
from .operators.modals.super_array import *
from .operators.modals.st3_array import *
from .operators.modals.material_scroll import *
from .operators.modals.blank_light import *
from .operators.modals.view_align import *

from .operators.preferences.modifiers import *
from .operators.preferences.set_sharpness import *
from .operators.preferences.sharp_manager import *

from .operators.sculpt.brush_toggle import *
from .operators.sculpt.sculpt_tools import *
from .operators.sculpt.sculpt_window import *

from .operators.sharpeners.clear_ssharps import *
from .operators.sharpeners.complex_sharpen import *
from .operators.sharpeners.octane_meshsetup import *
from .operators.sharpeners.sharpen import *
from .operators.sharpeners.soft_sharpen import *
from .operators.sharpeners.step import *

from .operators.UV_tools.uv_draw import *
from .operators.UV_tools.x_unwrap import *

from .operators.third_party.power_save import HOPS_OT_TP_PowerSaveInt
from .operators.third_party.power_link import HOPS_OT_TP_PowerLinkInt
from .operators.third_party.kit_ops import HOPS_OT_Kit_Ops_Window
from .operators.third_party.power_save_dialog import HOPS_OT_PowerSave_Dialog

from .ui.Panels.a0_help import *
from .ui.Panels.a1_sharpening import *
from .ui.Panels.a2_inserts import *
from .ui.Panels.a3_dynamic_tools import *
from .ui.Panels.a4_operations import *
from .ui.Panels.a5_Booleans import *
from .ui.Panels.a6_meshtools import *
from .ui.Panels.a7_options import *
from .ui.Panels.cutting_material import *
from .ui.Panels.opt_ins import *
from .ui.Submenus.inserts import *
from .ui.Submenus.operators import *
from .ui.Submenus.settings import *
from .ui.Submenus.sub_menus import *
from .ui.Submenus.tools import *
from .ui.hops_helper import *
from .ui.hops_helper.utility import *
from .ui.hops_helper import property as HopsHelper
from .ui.bevel_helper import *
from .ui.hopstool_helper import *
from .ui.uv_drawer import*
from .ui.main_menu import *
from .ui.main_pie import *
from .ui.status_helper import *
from .ui.select_menu import *

from .utility import check_for_update

from .utils.context import *
from .utils.blender_ui import *

from .ui_framework.operator_ui import HOPS_OT_UI_Draw
from .ui_framework.master import HOPS_MODAL_UI_Draw

from .arcade.games.pong.pong_modal import HOPS_OT_Arcade_Pong

classes = (
    HOPS_MT_RenderSetSubmenuLQ,
    HOPS_MT_RenderSetSubmenuHQ,
    HOPS_OT_SelectedToSelection,
    HOpsObjectProperties,
    HopsMaterialOptions,
    MATERIAL_OT_hops_new,
    HOPS_OT_AddMaterials,
    HOPS_OT_RemoveMaterials,
    HOPS_OT_MaterialScroll,
    HopsMeshCheckCollectionGroup,
    HOPS_OT_DataOpFaceTypeSelect,
    # HardOpsPreferences,
    HOPS_OT_LearningPopup,
    HOPS_OT_InsertsPopupPreview,
    HOPS_OT_AddonPopupPreview,
    HOPS_OT_PizzaPopupPreview,
    HOPS_OT_FacegrateOperator,
    HOPS_OT_FaceknurlOperator,
    HOPS_OT_EntrenchOperatorA,
    HOPS_OT_PanelOperatorA,
    HOPS_OT_StompObjectnoloc,
    HOPS_OT_MakeLink,
    HOPS_OT_SolidAll,
    HOPS_OT_ReactivateWire,
    HOPS_OT_ShowOverlays,
    HOPS_OT_HideOverlays,
    HOPS_OT_UnLinkObjects,
    HOPS_OT_ApplyMaterial,
    HOPS_OT_DeleteModifiers,
    HOPS_OT_BevelWeighSwap,
    HOPS_OT_MaterialOtSimplifyNames,
    HOPS_OT_renset1Operator,
    HOPS_OT_renset2Operator,
    HOPS_OT_renset3Operator,
    HOPS_OT_ReguiOperator,
    HOPS_OT_CleanuiOperator,
    HOPS_OT_EndframeOperator,
    HOPS_OT_MeshdispOperator,
    HOPS_OT_ClearClean,
    HOPS_OT_TwistApply,
    HOPS_OT_EditMultiTool,
    HOPS_OT_Bevel_Half_Add,
    HOPS_OT_UnsharpOperatorE,
    HOPS_OT_ClearCustomData,
    HOPS_OT_SharpandbevelOperatorE,
    HOPS_OT_BoolModal,
    HOPS_OT_BoolShift,
    HOPS_OT_BoolDifference,
    HOPS_OT_BoolDifference_hotkey,
    HOPS_OT_BoolIntersect,
    HOPS_OT_BoolIntersect_hotkey,
    HOPS_OT_BoolUnion,
    HOPS_OT_BoolUnion_hotkey,
    HOPS_OT_BoolKnife,
    HOPS_OT_BoolInset,
    HOPS_OT_BoolDice,
    HOPS_OT_EditBoolDifference,
    HOPS_OT_EditBoolUnion,
    HOPS_OT_EditBoolIntersect,
    HOPS_OT_EditBoolKnife,
    HOPS_OT_EditBoolSlash,
    HOPS_OT_EditBoolInset,
    HOPS_OT_ComplexSplitBooleanOperator,
    HOPS_OT_CutIn,
    HOPS_OT_Slash,
    HOPS_OT_Slash_hotkey,
    HOPS_OT_Analysis,
    HOPS_OT_AdjustBevelWeightOperator,
    HOPS_OT_ModalCircle,
    HOPS_OT_SetEditSharpen,
    HOPS_OT_StarConnect,
    HOPS_OT_Edge2Curve,
    HOPS_OT_ToRope,
    HOPS_OT_CleanMeshOperator,
    HOPS_OT_VertcircleOperator,
    HOPS_OT_VertextAlign,
    HOPS_OT_CleanReOrigin,
    HOPS_OT_About,
    HOPS_OT_BevelMultiplier,
    HOPS_OT_BoolshapeStatusSwap,
    HOPS_OT_CurveBevelOperator,
    HOPS_OT_DecalMachineFix,
    HOPS_OT_EmptyToImageOperator,
    HOPS_OT_EVICT,
    HOPS_OT_COLLECT,
    HOPS_OT_LateParent,
    HOPS_OT_LateParen_t,
    HOPS_OT_CenterEmptyOperator,
    HOPS_OT_EmptyTransparencyModal,
    HOPS_OT_EmptyOffsetModal,
    HOPS_OT_DisplayNotification,
    HOPS_OT_ResetStatus,
    HOPS_OT_SimplifyLattice,
    HOPS_OT_MOD_Twist360,
    HOPS_OT_SetAsAam,
    HOPS_OT_Pizza_Ops_Window,
    HOPS_OT_MirrorX,
    HOPS_OT_MirrorY,
    HOPS_OT_MirrorZ,
    HOPS_OT_EnableTopbar,
    HOPS_OT_OpenKeymapForEditing,
    HOPS_OT_ResetAxis,
    HOPS_OT_ScrollMulti,
    HOPS_OT_BevBoolMulti,
    HOPS_OT_EditMeshMacro,
    HOPS_OT_FlattenAlign,
    HOPS_OT_Conv_To_Shape,
    HOPS_OT_Conv_To_Plane,
    HOPS_OT_BVL_MULTI,
    HOPS_OT_Mirror_Array,
    HOPS_OT_ResetAxisModal,
    HOPS_OT_Shrinkwrap,
    HOPS_OT_ShrinkwrapRefresh,
    HOPS_OT_SphereCast,
    HOPS_OT_BoolToggle,
    HOPS_OT_TriangulateNgons,
    HOPS_OT_TriangulateModifier,
    HOPS_OT_AdjustArrayOperator,
    HOPS_OT_RadialArray,
    HOPS_OT_AdjustBevelOperator,
    HOPS_OT_SuperArray,
    HOPS_OT_ST3_Array,
    HOPS_OT_FastMeshEditor,
    HOPS_OT_Blank_Light,
    HOPS_OT_ViewAlign,
    HOPS_OT_TwoDBevelOperator,
    HOPS_OT_AdjustCurveOperator,
    HOPS_OT_AdjustAutoSmooth,
    HOPS_OT_AdjustViewport,
    HOPS_OT_AdjustTthickOperator,
    HOPS_OT_BoolObjectScroll,
    HOPS_OT_ModifierScroll,
    HOPS_OT_CurveGuide,
    HOPS_OT_CurveStretch,
    HOPS_OT_ApplyModifiers,
    HOPS_OT_ModalMirror,
    HOPS_OT_CollapseModifiers,
    HOPS_OT_OpenModifiers,
    HOPS_OT_SetSharpness30,
    HOPS_OT_SetSharpness45,
    HOPS_OT_SetSharpness60,
    HOPS_OT_SetAutoSmooth,
    HOPS_OT_SharpManager,
    HOPS_OT_BrushToggle,
    HOPS_OT_SculptDecimate,
    HOPS_OT_Sculpt_Ops_Window,
    HOPS_OT_UnSharpOperator,
    HOPS_OT_ComplexSharpenOperator,
    HOPS_OT_Sharpen,
    HOPS_OT_AddEdgeSplit,
    HOPS_OT_SoftSharpenOperator,
    HOPS_OT_StepOperator,
    HOPS_OT_DrawUV,
    HOPS_OT_XUnwrapF,
    HOPS_OT_GPCopyMove,
    HOPS_OT_GPCSurfaceOffset,
    HOPS_OT_VoxelizerOperator,
    HOPS_OT_AdjustLogo,
    HopsHelper.Tool,
    HopsHelper.Object,
    HopsHelper.Constraint,
    HopsHelper.Modifier,
    HopsHelper.Mesh,
    HopsHelper.Curve,
    HopsHelper.Surface,
    HopsHelper.Meta,
    HopsHelper.Font,
    HopsHelper.GPencil,
    HopsHelper.Armature,
    HopsHelper.Lattice,
    HopsHelper.Empty,
    HopsHelper.Speaker,
    HopsHelper.Camera,
    HopsHelper.Light,
    HopsHelper.Light_Probe,
    HopsHelper.Data,
    HopsHelper.ShaderFX,
    HopsHelper.Bone,
    HopsHelper.BoneConstraint,
    HopsHelper.Material,
    HopsHelper.Panels,
    HopsHelper.Operators,
    HopsHelper.Buttons,
    HopsHelper.HopsHelperOptions,
    HopsHelper.HopsButtonOptions,
    HOPS_MT_SelectGrouped,
    HOPS_OT_helper,
    HOPS_OT_helper_add_mat,
    HOPS_PT_material_hops,
    HOPS_OT_hopstool_helper,
    HOPS_OT_bevel_helper,
    HOPS_OT_DrawObjectUVs,
    HOPS_MT_MainMenu,
    HOPS_MT_ModSubmenu,
    HOPS_MT_MainPie,
    HOPS_OT_StatusHelperPopup,
    HOPS_MT_InsertsObjectsSubmenu,
    HOPS_MT_MeshOperatorsSubmenu,
    HOPS_MT_ObjectsOperatorsSubmenu,
    HOPS_MT_MergeOperatorsSubmenu,
    HOPS_MT_EditClassicsSubmenu,
    HOPS_MT_BoolScrollOperatorsSubmenu,
    HOPS_MT_SettingsSubmenu,
    HOPS_MT_Export,
    HOPS_MT_MaterialListMenu,
    HOPS_MT_SculptSubmenu,
    HOPS_MT_MiraSubmenu,
    HOPS_MT_BasicObjectOptionsSubmenu,
    HOPS_MT_FrameRangeSubmenu,
    HOPS_MT_SelectViewSubmenu,
    HOPS_MT_ViewportSubmenu,
    HOPS_MT_RenderSetSubmenu,
    HOPS_MT_ResetAxiSubmenu,
    HOPS_MT_MiscSubmenu,
    HOPS_MT_SymmetrySubmenu,
    HOPS_MT_PluginSubmenu,
    HOPS_MT_BoolSumbenu,
    HOPS_MT_ObjectToolsSubmenu,
    HOPS_MT_ST3MeshToolsSubmenu,

    HOPS_OT_Curve_Extrude,
    HOPS_OT_Mesh_Align,
    HOPS_OT_Flatten_To_Face,
    HOPS_OT_Curve_Draw,
    HOPS_OT_Selection_To_Boolean,
    HOPS_OT_Sel_To_Bool_V2,

    HOPS_OT_StoreMousePosition,
    HOPS_OT_HopsArrayGizmoGroup,
    HOPS_OT_ArrayGizmo,
    HopsArrayExecuteXmGizmo,
    HOPS_PT_mirror_transform_orientations,
    HOPS_PT_mirror_mode,
    HOPS_PT_mirror_pivot,
    HOPS_OT_MirrorGizmoGroup,
    HOPS_OT_MirrorGizmo,
    HOPS_MT_MirrorMenu,
    HOPS_OT_MirrorRemoveGizmo,
    HOPS_OT_MirrorExecuteFinal,
    HOPS_OT_MirrorExecuteXGizmo,
    HOPS_OT_MirrorExecuteXmGizmo,
    HOPS_OT_MirrorExecuteYGizmo,
    HOPS_OT_MirrorExecuteYmGizmo,
    HOPS_OT_MirrorExecuteZGizmo,
    HOPS_OT_MirrorExecuteZmGizmo,
    HOPS_PT_MirrorOptions,
    HOPS_GT_ArrayPlusShapeGizmo,
    HOPS_GT_ArrayMinusShapeGizmo,
    HOPS_OT_ArrayMinus,
    HOPS_OT_ArrayPlus,
    HOPS_OT_TP_PowerSaveInt,
    HOPS_OT_TP_PowerLinkInt,
    HOPS_OT_PowerSave_Dialog,
    simple_deform.HOPS_OT_MOD_Simple_deform,
    triangulate.HOPS_OT_MOD_Triangulate,
    uv_project.HOPS_OT_MOD_UV_Project,
    weighted_normal.HOPS_OT_MOD_Weighted_Normal,
    wireframe.HOPS_OT_MOD_Wireframe,
    displace.HOPS_OT_MOD_Displace,
    subsurf.HOPS_OT_MOD_Subdivision,
    screw.HOPS_OT_MOD_Screw,
    weld.HOPS_OT_MOD_Weld,
    lattice.HOPS_OT_MOD_Lattice,
    decimate.HOPS_OT_MOD_Decimate,
    Apply_modfiers.HOPS_OT_MOD_Apply,
    shrinkwrap.HOPS_OT_MOD_Shrinkwrap,
    smooth.HOPS_OT_MOD_Smooth,
    l_smooth.HOPS_OT_MOD_LSmooth,
    skin.HOPS_OT_MOD_Skin,
    cast.HOPS_OT_MOD_Cast,
    hook.HOPS_OT_MOD_Hook,
    mask.HOPS_OT_MOD_Mask,
    HOPS_OT_UI_Draw,
    HOPS_MODAL_UI_Draw,
    HOPS_OT_Kit_Ops_Window,
    HOPS_OT_Arcade_Pong
)

from . import addon
# from . addon import operator, panel, ui, keymap, pie, preference, property, topbar, tool


def register():
    for cls in classes:
        register_class(cls)

    register_all()
    addon.register()

    check_for_update(bl_info['version'])


def unregister():
    addon.unregister()
    unregister_all()

    for cls in reversed(classes):
        unregister_class(cls)
