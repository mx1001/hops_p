import os
import bpy,bgl,blf
from bpy.types import Menu
from .. icons import get_icon_id
from .. utils.addons import addon_exists
from .. utils.objects import get_inactive_selected_objects
from .. preferences import use_asset_manager, get_preferences, right_handed_enabled, pro_mode_enabled, Relink_options_enabled, BC_unlock_enabled, mira_handler_enabled



#Insert Object
class Inserts_Objects(bpy.types.Menu):
    bl_idname = "inserts.objects"
    bl_label = "Inserts Objects"

    def draw(self, context):
        layout = self.layout

        wm = context.window_manager
        user_preferences = bpy.context.user_preferences
        addon_pref = get_preferences()

        if addon_pref.Asset_Manager_Preview :
            if any("asset_management" in s for s in bpy.context.user_preferences.addons.keys()):
                AM = context.   window_manager.asset_m
                #layout.operator("view3d.asset_m_pop_up_preview", "(AM)")
                layout.prop(AM, "libraries", text="")
                layout.prop(AM, "categories", text="")
                layout.template_icon_view(wm, "AssetM_previews", show_labels=True)

        if pro_mode_enabled():
            layout.operator("view3d.asset_scroller_window", "(Asset Window)", icon_value=get_icon_id("HardOps"))
        
        layout.template_icon_view(wm, "Hard_Ops_previews")
        layout.template_icon_view(wm, "sup_preview")
        layout.separator()

        if len(context.selected_objects) > 1:
            layout.operator("object.to_selection", text="Obj to selection", icon="MOD_MULTIRES")
            layout.operator("make.link", text = "Link Objects", icon='CONSTRAINT' )
            layout.operator("unlink.objects", text = "Unlink Objects", icon='UNLINKED' )

#############################
#Insert Object Classic
#############################

#Insert Object
class Inserts_ObjectsC(bpy.types.Menu):
    bl_idname = "inserts.objectsc"
    bl_label = "Inserts Objects Classic"

    def draw(self, context):
        layout = self.layout

        wm = context.window_manager
        current_dir = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
        user_preferences = bpy.context.user_preferences
        addon_pref = user_preferences.addons[current_dir].preferences

        if any("asset_management" in s for s in bpy.context.user_preferences.addons.keys()):
            if addon_pref.Asset_Manager_Preview :
                AM = context.window_manager.asset_m
                #layout.operator("view3d.asset_m_pop_up_preview", "(AM)")

                layout.prop(AM, "libraries", text="")
                layout.prop(AM, "categories", text="")
                layout.template_icon_view(wm, "AssetM_previews", show_labels=True)

        layout.operator("view3d.asset_scroller_window", "(Asset Window)")
        layout.template_icon_view(wm, "Hard_Ops_previews")
        layout.template_icon_view(wm, "sup_preview")
        layout.separator()

        if len(context.selected_objects) > 1:
            layout.operator("object.to_selection", text="Obj to selection", icon="MOD_MULTIRES")
            layout.operator("make.link", text = "Link Objects", icon='CONSTRAINT' )
            layout.operator("unlink.objects", text = "Unlink Objects", icon='UNLINKED' )




# Material
class MaterialListMenu(bpy.types.Menu):
    bl_idname = "view3d.material_list_menu"
    bl_label = "Material list"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        if len(bpy.data.materials):
            for mat in bpy.data.materials:
                name = mat.name
                try:
                    icon_val = layout.icon(mat)
                except:
                    icon_val = 1
                    print ("WARNING [Mat Panel]: Could not get icon value for %s" % name)

                op = col.operator("object.apply_material", text=name, icon_value=icon_val)
                op.mat_to_assign = name
        else:
            layout.label("No data materials")

class Sculpt_Submenu(bpy.types.Menu):
    bl_label = 'Sculpt'
    bl_idname = 'hops_sculpt.submenu'
    
    def draw(self, context):
        layout = self.layout

        #sculpt = context.tool_settings.sculpt
        #settings = self.paint_settings(context)
        #brush = settings.brush

        
        if context.sculpt_object.use_dynamic_topology_sculpting:
            layout.operator("sculpt.dynamic_topology_toggle", icon='X', text="Disable Dyntopo")
        else:
            layout.operator("sculpt.dynamic_topology_toggle", icon='SCULPT_DYNTOPO', text="Enable Dyntopo")
        layout.separator()

        if (context.tool_settings.sculpt.detail_type_method == 'CONSTANT'):
            layout.prop(context.tool_settings.sculpt, "constant_detail")
            layout.operator("sculpt.sample_detail_size", text="", icon='EYEDROPPER')
        elif (context.tool_settings.sculpt.detail_type_method == 'BRUSH'):
            layout.prop(context.tool_settings.sculpt, "detail_percent")
        else:
            layout.prop(context.tool_settings.sculpt, "detail_size")
        layout.prop(context.tool_settings.sculpt, "detail_refine_method", text="")
        layout.prop(context.tool_settings.sculpt, "detail_type_method", text="")
        layout.separator()
        layout.prop(context.tool_settings.sculpt, "use_smooth_shading")
        layout.operator("sculpt.optimize")
        if (context.tool_settings.sculpt.detail_type_method == 'CONSTANT'):
            layout.operator("sculpt.detail_flood_fill")
        layout.separator()
        layout.prop(context.tool_settings.sculpt, "symmetrize_direction", text="")
        layout.operator("sculpt.symmetrize")
     
class Settings_Submenu(bpy.types.Menu):
    bl_label = 'Settings'
    bl_idname = 'settings.submenu'

    def draw(self, context):
        layout = self.layout

        obj = context.object
        
        if pro_mode_enabled() == False:
            #Learning Hard Ops Button
            layout.operator("hops.learning_popup", text = "Hard Ops Learning", icon_value=get_icon_id("Noicon"))
            layout.separator()
            
        if pro_mode_enabled():
            if context.active_object.type == 'CAMERA':
                cam = bpy.context.space_data
                row = layout.row(align=False)
                col = row.column(align=True)

                #col.label("Lock Camera To View")
                col.prop(cam, "lock_camera", text = "Lock To View")
                
#                obj = bpy.context.object.data
#                col.label("Passepartout")
#                col.prop(obj, "passepartout_alpha", text = "")
#                col.label("DOF")
#                col.prop(obj, "dof_object", text = "")
#                col.label("Aperture")
#                obj = bpy.context.object.data.cycles
#                col.prop(obj, "aperture_size", text = "")
                layout.separator()

        if context.active_object.type == 'MESH':
            #Wire/Solid Toggle
            if context.object.draw_type == 'WIRE':
                layout.operator("object.solid_all", text="Solid Mode", icon='MESH_CUBE')
            else :
                layout.operator("showwire.objects", text = "Wire Mode", icon='OUTLINER_OB_LATTICE')
                
            layout.operator_context = 'INVOKE_DEFAULT'
            layout.operator("hops.draw_uv", text = "UV Preview", icon_value=get_icon_id("CUnwrap"))
            
            if len(context.selected_objects) == 1:
                layout.menu("ObjectOptions.submenu", text = "Object Options")

        #Viewport Submenu
        layout = self.layout
        layout.separator()

        if bpy.context.object and bpy.context.object.type == 'MESH':
            layout.menu("view3d.material_list_menu", icon_value=get_icon_id("Noicon"))
            
        layout.menu("viewport.submenu", text="ViewPort", icon_value=get_icon_id("Noicon"))

        #Helper Submenu
        #layout = self.layout
        #layout.menu("helper.submenu", text = "Helper Submenu")

        #Order Pizza Button Haha
        layout.operator("view3d.pizzapopup", text = "Pizza Ops", icon_value=get_icon_id("Pizzaops"))
        layout.separator()

        #Render Sets
        layout = self.layout
        scene = context.scene.cycles

        row = layout.row(align=False)
        col = row.column(align=True)

        layout.menu("renderSet.submenu", text="RenderSetups", icon_value=get_icon_id("Noicon"))

        col.prop(scene, "preview_samples")

        layout.separator()

        #FrameRange Settings
        layout = self.layout
        scene = context.scene

        row = layout.row(align=False)
        col = row.column(align=True)
        
        if pro_mode_enabled():
            col.prop(scene, 'frame_end')
            
            layout.menu("FrameRange.submenu", text = "Frame Range Options")
            
        #layout.menu("AddonChecker.submenu", text = "AddonChecker")
        
        layout.menu("Selection.submenu", text = "Selection Options")

class MiraSubmenu(bpy.types.Menu):
    bl_label = 'Mira Panel'
    bl_idname = 'mira.submenu'

    def draw(self, context):
        layout = self.layout


        layout = self.layout.column_flow(2)

        if mira_handler_enabled():
            layout.operator("mesh.curve_stretch", text="CurveStretch", icon="RNA")
            layout.operator("mesh.curve_guide", text='CurveGuide', icon="RNA")
        
        else:    
            layout.operator("mira.curve_stretch", text="CurveStretch", icon="RNA")
            layout.operator("mira.curve_guide", text="CurveGuide", icon="RNA")
            layout.prop(context.scene.mi_cur_stretch_settings, "points_number", text='')
            layout.prop(context.scene.mi_curguide_settings, "points_number", text='')
        
class ObjectOptions_submenu(bpy.types.Menu):
    bl_label = 'ObjectOptions'
    bl_idname = 'ObjectOptions.submenu'
    
    def draw(self, context):
        layout = self.layout
        
        layout = self.layout.column_flow(1)
        row = layout.row()
        sub = row.row()
        sub.scale_y = 1.2
        
        obj = bpy.context.object

        layout.prop(obj, "name", text="")
        layout.separator()
        
        obj = bpy.context.object
        
        layout.prop(obj, "show_name", text = "Show object's name"),

class FrameRange_submenu(bpy.types.Menu):
    bl_label = 'FrameRange'
    bl_idname = 'FrameRange.submenu'
    
    def draw(self, context):
        layout = self.layout

        layout = self.layout
        scene = context.scene

        row = layout.row(align=False)
        col = row.column(align=True)

        layout.operator("setframe.end", text =  "Frame Range", icon_value=get_icon_id("SetFrame"))

        if pro_mode_enabled():
            col.prop(scene, 'frame_start')
            
            col.prop(scene, 'frame_end')

class SelectView_submenu(bpy.types.Menu):
    bl_label = 'Selection'
    bl_idname = 'Selection.submenu'
    
    def draw(self, context):
        layout = self.layout
        
        m_check = context.window_manager.m_check
        
        if bpy.context.object and bpy.context.object.type == 'MESH':
            if m_check.meshcheck_enabled:
                layout.operator("object.remove_materials", text="Hidde Ngons/Tris", icon_value=get_icon_id("ShowNgonsTris"))
            else:
                layout.operator("object.add_materials", text="Display Ngons/Tris", icon_value=get_icon_id("ShowNgonsTris"))

            layout.operator("data.facetype_select", text="Ngons Select", icon_value=get_icon_id("Ngons")).face_type = "5"
            layout.operator("data.facetype_select", text="Tris Select", icon_value=get_icon_id("Tris")).face_type = "3"

class AddonChecker_submenu(bpy.types.Menu):
    bl_label = 'AddonChecker'
    bl_idname = 'AddonChecker.submenu'
    
    def draw(self, context):
        layout = self.layout
        
        a = any("MirrorMirrorTool" in s for s in bpy.context.user_preferences.addons.keys())

        #b = any("iceTools" in s for s in bpy.context.user_preferences.addons.keys())

        c = any("mira_tools" in s for s in bpy.context.user_preferences.addons.keys())

        d = any("asset_management" in s for s in bpy.context.user_preferences.addons.keys())

        e = any("BoolTool" in s for s in bpy.context.user_preferences.addons.keys())

        f =  any("QuickLatticeCreate" in s for s in bpy.context.user_preferences.addons.keys())

        g = any("AutoMirror" in s for s in bpy.context.user_preferences.addons.keys())

        if a and c and d and e and f and g:
            layout.separator()
        else:
            layout.operator("view3d.addoncheckerpopup", text = "Add On Diagnostic", icon="SCRIPTPLUGINS")
            layout.separator()
        

#Viewport
class Viewport_Submenu(bpy.types.Menu):
    bl_label = 'Viewport'
    bl_idname = 'viewport.submenu'

    def draw(self, context):
        layout = self.layout

        layout.operator("ui.reg", text = "Normal", icon_value=get_icon_id("NGui"))

        layout.operator("ui.red", text = "Matcap", icon_value=get_icon_id("RGui"))
        
        #needs icon for silouette
        if addon_exists("silhouette"): 
            layout.operator("ui.sil", text = "Silhouette", icon_value=get_icon_id("SilGui"))

        layout.operator("ui.clean", text = "Minimal", icon_value=get_icon_id("QGui"))
        
        layout.operator("ui.nor", text = "Normal", icon_value=get_icon_id("NorGui"))        
        
        layout.separator()
        
        if bpy.context.space_data.use_matcap == True:
                view = context.space_data
                layout.template_icon_view(view, "matcap_icon")

class RenderSet_Submenu(bpy.types.Menu):
    bl_label = 'RenderSet_submenu'
    bl_idname = 'renderSet.submenu'

    def draw(self, context):
        layout = self.layout

        layout.operator("render.setup", text = "Render (1)", icon="RESTRICT_RENDER_OFF")

        layout.operator("renderb.setup", text = "Render (2)", icon="RESTRICT_RENDER_OFF")
        
        layout.separator()
        
        row = layout.row(align=False)
        col = row.column(align=True)
        
        view_settings = context.scene.view_settings
        col.prop(view_settings, "view_transform", text = "")
        col.prop(view_settings, "look", text = "")


class arSub(bpy.types.Menu):
    bl_label = 'AR Protomenu'
    bl_idname = 'protomenu.submenu'

    def draw(self, context):
        layout = self.layout


        obj = context.active_object

        scene = context.scene
        col = layout.column()
        row = layout.row(align=False)
        col = row.column(align=True)

        object = context.active_object
        ob = object.hops


        is_multiselected = False
        is_notselected = False
        multislist = bpy.context.selected_objects


        if len(multislist) > 1:
            is_multiselected = True
        if len(multislist) < 1:
            is_notselected = True

        if is_multiselected == False:
            layout.operator_context = 'INVOKE_DEFAULT'
            layout.operator("hops.draw_uv", text = "UV Preview", icon_value=get_icon_id("CUnwrap"))
            layout.separator()
            
            layout.operator_context = 'INVOKE_DEFAULT'
            layout.operator("hops.adjust_bevel", text = "(B)Width", icon_value=get_icon_id("AdjustBevel"))
            
            layout.operator_context = 'INVOKE_DEFAULT'
            layout.operator("hops.2d_bevel", text = "(2d)Bevel", icon_value=get_icon_id("AdjustBevel"))

            layout.operator_context = 'INVOKE_DEFAULT'
            layout.operator("nw.a_rray", text = "(Q)Array", icon_value=get_icon_id("Qarray"))

            layout.operator_context = 'INVOKE_DEFAULT'
            layout.operator("hops.adjust_tthick", text = "(T)Thick", icon_value=get_icon_id("Tthick"))

            layout.separator()
            
            layout.operator_context = 'INVOKE_DEFAULT'
            layout.operator("hops.soft_sharpen", text = "(S) Sharpen", icon_value=get_icon_id("Ssharpen"))

            layout.operator_context = 'INVOKE_DEFAULT'
            layout.operator("hops.soft_sharpen", text = "(C) Sharpen", icon_value=get_icon_id("CSharpen"))
            
            layout.separator()
            
        if pro_mode_enabled():
            if is_multiselected == False:
                layout.operator_context = 'INVOKE_DEFAULT'
                layout.operator("step.cstep", text = "(C) Bake", icon_value=get_icon_id("Cstep")).set_status=False
                
                layout.operator_context = 'INVOKE_DEFAULT'
                layout.operator("step.sstep", text = "(S) Step", icon_value=get_icon_id("Sstep"))

                layout.operator_context = 'INVOKE_DEFAULT'
                layout.operator("step.cstep", text = "(C) Step", icon_value=get_icon_id("Cstep"))

            layout.separator()

        #ClearSharps
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("clean.sharps", text = "Clear S/C/Sharps", icon_value=get_icon_id("CleansharpsE"))
        
        if pro_mode_enabled():
            layout.operator_context = 'INVOKE_DEFAULT'
            layout.operator("view3d.clean_mesh", text = "Clean Mesh (E)", icon_value=get_icon_id("CleansharpsE"))

        layout.separator()
        
        if pro_mode_enabled():
            #Bevel Segment Test
            if ob.is_bevel and len(context.selected_objects) <= 1:
                col.prop(obj.modifiers['Bevel'], "segments")
                col.separator()

            if len(context.selected_objects) > 1:
                layout.operator("material.simplify", text = "Material Link", icon_value=get_icon_id("Noicon"))
                layout.separator()

            #muti Sshapen / Csharpen Items / C/SStep Multi
            if len(context.selected_objects) > 1:
                layout.operator("multi.csharp", text = "(C)Multi", icon_value=get_icon_id("CSharpen"))
                layout.operator("multi.ssharp", text = "(S)Multi", icon_value=get_icon_id("Ssharpen"))
                layout.operator("multi.clear", text = "Multi Clear", icon_value=get_icon_id("ClearSharps"))
                #layout.operator("multi.sstep", text = "(S) Multi-Step", icon_value=get_icon_id("Sstep"))
                #layout.operator("multi.cstep", text = "(C) Multi-Step", icon_value=get_icon_id("Cstep"))

            #Nada
            else:
                layout.separator()


class Meshtools(bpy.types.Menu):
    bl_label = 'Mesh_Tools'
    bl_idname = 'view3d.mstool_submenu'

    def draw(self, context):
        layout = self.layout
        
        if addon_exists("BoxCutter"):
            layout.operator("boxcutter.draw_boolean_layout", text = "BoxCutter", icon_value=get_icon_id("BoxCutter"))
        else: 
            layout.operator("wm.url_open", text="Get BoxCutter!", icon_value=get_icon_id("BoxCutter")).url = "https://gum.co/BoxCutter/iamanoperative"
            
        if pro_mode_enabled():
            if addon_exists("relink"):
                if Relink_options_enabled():           
                    layout.menu("relink_menu", text = "ReLink")
        
            if context.active_object.type == 'MESH':
                layout = self.layout.column_flow(1)
                row = layout.row()
                sub = row.row()
                sub.scale_y = 2.5
                sub.scale_x = 0.5

                if len(context.selected_objects) == 1:
                    #layout.operator("view3d.status_helper_popup", text = "StatusOveride")
                    layout.operator("hops.reset_status", text = "StatusReset")
                layout.separator()
        
        layout = self.layout
        
        layout.operator("array.twist", text = "Twist 360", icon_value=get_icon_id("ATwist360"))
        layout.operator("nw.radial_array", text = "Radial 360", icon_value=get_icon_id("ATwist360"))

        layout.separator()
        layout.operator("view3d.hops_helper_popup", text = "Modifier Helper", icon="SCRIPTPLUGINS").tab = "MODIFIERS"

        layout.separator()
        if bpy.context.object and bpy.context.object.type == 'MESH':
            layout.menu("view3d.material_list_menu", icon_value=get_icon_id("Noicon"))
        
        layout.separator()    
        layout.menu("view3d.symmetry_submenu", text = "Symmetry Options", icon_value=get_icon_id("Xslap"))

        layout.separator()

        layout.operator("hops.xunwrap", text = "(X) Unwrap", icon_value=get_icon_id("CUnwrap"))
        #layout.operator("object.cunwrap", text = "(C) Unwrap", icon_value=get_icon_id("CUnwrap"))

        layout.separator()

        layout.operator("clean.reorigin", text = "(S) Clean Recenter", icon_value=get_icon_id("SCleanRecenter"))
        
        if pro_mode_enabled():
            layout.operator("stomp2.object", text = "ApplyAll (-L)", icon_value=get_icon_id("Applyall"))


class symmetry_submenu(bpy.types.Menu):
    bl_idname = "view3d.symmetry_submenu"
    bl_label = "Symmetry Submenu"

    def draw(self, context):
        layout = self.layout
        #box = layout.box()
        #row = box.row()
        
        if pro_mode_enabled():
            if any("AutoMirror" in s for s in bpy.context.user_preferences.addons.keys()):
                layout.menu("automirror.submenu", text = "Automirror", icon_value=get_icon_id("MHelper"))
                layout.separator()                

        layout = self.layout.column_flow(2)
        row = layout.row()
        sub = row.row()
        sub.scale_y = 1.0
        sub.scale_x = 0.05

        if right_handed_enabled():
            sub.operator("view3d.symmetrize", text = "(X)", icon_value=get_icon_id("Xslap")).symtype = "POSITIVE_X"
            sub.operator("view3d.symmetrize", text = "(Y)", icon_value=get_icon_id("Yslap")).symtype = "POSITIVE_Y"
        else:
            sub.operator("view3d.symmetrize", text = "(X)", icon_value=get_icon_id("Xslap")).symtype = "NEGATIVE_X"
            sub.operator("view3d.symmetrize", text = "(Y)", icon_value=get_icon_id("Yslap")).symtype = "NEGATIVE_Y"
        #layout.operator("view3d.symmetrize", text = "(Y)", icon_value=get_icon_id("Yslap")).symtype = "NEGATIVE_Y"
        sub.operator("view3d.symmetrize", text = "(Z)", icon_value=get_icon_id("Zslap")).symtype = "POSITIVE_Z"
                
class eMeshtools(bpy.types.Menu):
    bl_label = 'EMesh_Tools'
    bl_idname = 'view3d.emstool_submenu'

    def draw(self, context):
        layout = self.layout

        if pro_mode_enabled():    
            layout.menu("view3d.ewiz_submenu", text = "AUX", icon="PLUGIN")
            
        layout.separator()
        
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("hops.draw_uv", text = "UV Preview", icon_value=get_icon_id("CUnwrap"))   

        layout.operator("hops.circle", text = "Circle(E)", icon_value=get_icon_id("CircleSetup"))#.nth_mode = False

        layout.operator("view3d.vertcircle", text = "Circle (Nth)(E)", icon_value=get_icon_id("NthCircle")).nth_mode = True

        layout.separator()

        layout.operator("fgrate.op", text = "Grate (Face)", icon_value=get_icon_id("FaceGrate"))

        layout.operator("fknurl.op", text = "Knurl (Face)", icon_value=get_icon_id("FaceKnurl"))

        layout.separator()

        layout.operator("quick.panel", text = "Panel (Face)", icon_value=get_icon_id("EdgeRingPanel"))

        layout.operator("entrench.selection", text = "Panel (Edge)", icon_value=get_icon_id("FacePanel"))
        
        layout.operator("hops.star_connect", text = "Star Connect")

        if any("mira_tools" in s for s in bpy.context.user_preferences.addons.keys()):
            layout.separator()
            layout.menu("mira.submenu", text = "Mira (T)", icon="PLUGIN")
        else:
            layout.separator()


class edgeWizard(bpy.types.Menu):
    bl_label = 'EWizard_Tools'
    bl_idname = 'view3d.ewiz_submenu'

    def draw(self, context):
        layout = self.layout
        
        #layout.operator_context = 'INVOKE_DEFAULT'
        #layout.operator("transform.edge_bevelweight", text = "Bweight", icon_value = get_icon_id("AdjustBevel"))
        
        if any("kk_QuickLatticeCreate" in s for s in bpy.context.user_preferences.addons.keys()):
            layout.operator("object.easy_lattice", text = "Easy Lattice", icon_value=get_icon_id("Easylattice"))
    
        if any("mesh_snap" in s for s in bpy.context.user_preferences.addons.keys()):
            layout.operator("mesh.snap_utilities_line", text = "Snap Line")
            layout.operator("mesh.snap_push_pull", text = "Push Pull Faces")
                
        if any("mesh_edge_equalize" in s for s in bpy.context.user_preferences.addons.keys()):
            layout.operator("mo.edge_equalize_active", text = "Edge Equalize")
        

class SharpSub(bpy.types.Menu):
    bl_label = 'C/S/T Sharp'
    bl_idname = 'sharpmenu.submenu1'

    def draw(self, context):
        layout = self.layout

        layout.operator("ssharpen.objects", text = "(S) Sharpen", icon_value=get_icon_id("Ssharpen"))

        layout.operator("csharpen.objects", text = "(C) Sharpen", icon_value=get_icon_id("CSharpen"))

        layout.operator("cstep.objects", text = "(C) Step", icon_value=get_icon_id("Frame"))

        layout.operator("solidify.objects", text = "(T) Sharpen", icon_value=get_icon_id("Tsharpen"))

        layout.operator("clean.objects", text = "Clear S/C/Sharps", icon_value=get_icon_id("ClearSharps"))


class HelpSub(bpy.types.Menu):
    bl_label = 'Helper Submenu'
    bl_idname = 'helper.submenu'

    def draw(self, context):
        layout = self.layout


        layout.operator("view3d.generalhelper", text = "General", icon_value=get_icon_id("Frame"))

        layout.operator("view3d.orientationhelper", text = "MenuBar", icon_value=get_icon_id("Frame"))

        layout.operator("view3d.hops_helper_popup", text = "Modifiers", icon_value=get_icon_id("Frame"))

        layout.operator("view3d.conhelper", text = "Constraint", icon_value=get_icon_id("Frame"))

        layout.operator("view3d.openglhelper", text = "OpenGL", icon_value=get_icon_id("Frame"))

        layout.operator("view3d.mathelper", text = "Material", icon_value=get_icon_id("Frame"))

        layout.operator("view3d.displayhelper", text = "Display Options", icon_value=get_icon_id("Frame"))

        layout.operator("view3d.transformhelper", text = "Transformation", icon_value=get_icon_id("Frame"))
