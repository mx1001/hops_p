import bpy
from ... icons import get_icon_id
from ... utils.addons import addon_exists
from ... preferences import get_preferences


class HOPS_MT_ObjectToolsSubmenu(bpy.types.Menu):
    bl_label = 'Objects Tools Submenu'
    bl_idname = 'HOPS_MT_ObjectToolsSubmenu'

    def draw(self, context):
        layout = self.layout

        row = layout.column().row()

        if get_preferences().ui.expanded_menu:
            column = row.column()
        else:
            column =self.layout

        column.operator("hops.flatten_align", text="Reset Axis/Align/Select", icon_value=get_icon_id("Xslap"))
        column.operator("hops.adjust_auto_smooth", text="AutoSmooth", icon_value=get_icon_id("Diagonal"))
        column.separator()

        column.operator("hops.bool_dice", text="Dice", icon_value=get_icon_id("Dice"))
        column.operator("array.twist", text="Twist 360", icon_value=get_icon_id("ATwist360"))
        column.operator("hops.radial_array", text="Radial Array", icon_value=get_icon_id("ArrayCircle"))
        column.separator()

        column.operator("hops.sphere_cast", text="SphereCast", icon_value=get_icon_id("SphereCast"))
        column.separator()

        column.operator("hops.edge2curve", text="Curve/Extract", icon_value=get_icon_id("Curve"))
        column.separator()
        
        if get_preferences().property.menu_array_type == 'ST3_V2':
            column.operator("hops.st3_array", text="Array V2", icon_value=get_icon_id("GreyArrayX"))
        else:
            column.operator("hops.super_array", text="Array V1", icon_value=get_icon_id("Display_operators"))
        column.separator()

        column.operator("hops.apply_modifiers", text="Smart Apply", icon_value=get_icon_id("Applyall")) #.modifier_types='BOOLEAN'

        if get_preferences().ui.expanded_menu:
            column = row.column()
        else:
            column.separator()
            
        if bpy.context.active_object and bpy.context.active_object.type == 'MESH':
            column.menu("HOPS_MT_MaterialListMenu", text = "Material List", icon="MATERIAL_DATA")
            if len(context.selected_objects) >= 2:
                column.operator("material.simplify", text="Material Link", icon_value=get_icon_id("Applyall"))
            #column.separator()

        column.operator_context = 'INVOKE_DEFAULT'
        column.operator("material.hops_new", text = 'Add Blank Material', icon="PLUS")

        column.separator()

        column.operator("hops.xunwrap", text="Auto Unwrap", icon_value=get_icon_id("CUnwrap"))
        #column.separator()

        if len(context.selected_objects) == 1:
            column.operator("hops.reset_status", text="HOPS Reset", icon_value=get_icon_id("StatusReset"))
            #column.separator()

        if context.active_object and context.active_object.type == 'MESH':
            column.menu("HOPS_MT_SelectViewSubmenu", text="Selection Options",  icon_value=get_icon_id("ShowNgonsTris"))
            #column.separator()

        column.separator()

        column.menu("HOPS_MT_BoolScrollOperatorsSubmenu", text="Mod Scroll/Toggle", icon_value=get_icon_id("Diagonal"))
        
        column.separator()

        column.menu("HOPS_MT_Export", text = 'Export', icon="EXPORT")
        column.separator()

        if addon_exists("MESHmachine"):
            column.separator()
            column.menu("MACHIN3_MT_mesh_machine", text="MESHmachine", icon_value=get_icon_id("Machine"))
        
        if addon_exists("MESHmachine"):
            column.menu("VIEW3D_MT_cablerator", text="Cable Ops", icon_value=get_icon_id("Cablerator"))

        if len(context.selected_objects) == 2:
            column.operator("hops.shrinkwrap2", text="ShrinkTo", icon_value=get_icon_id("ShrinkTo"))
            column.separator()

class HOPS_MT_MeshToolsSubmenu(bpy.types.Menu):
    bl_label = 'Mesh Tools Submenu'
    bl_idname = 'HOPS_MT_MeshToolsSubmenu'

    def draw(self, context):
        layout = self.layout
        is_boolean = len([mod for mod in bpy.context.active_object.modifiers if mod.type == 'BOOLEAN'])

        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("hops.helper", text="Modifier Helper", icon="SCRIPTPLUGINS")

        layout.separator()

        layout.operator("hops.bevel_assist", text="Bevel / Edge Manager", icon_value=get_icon_id("CSharpen"))

        layout.separator()

        layout.operator("hops.bevel_helper", text="Bevel Helper", icon_value=get_icon_id("ModifierHelper"))
        layout.operator("hops.sharp_manager", text="Edge Manager", icon_value=get_icon_id("Diagonal"))
        layout.operator("view3d.bevel_multiplier", text="Bevel Exponent", icon_value=get_icon_id("FaceGrate"))

        layout.separator()

        if is_boolean:
            layout.operator("hops.scroll_multi", text="Bool Multi Scroll ", icon_value=get_icon_id("Diagonal"))
            layout.operator("hops.bool_scroll_objects", text="Object Scroll", icon_value=get_icon_id("StatusReset"))
            layout.separator()

        layout.operator("hops.scroll_multi", text="Mod Scroll/Toggle", icon_value=get_icon_id("StatusReset"))

        op = layout.operator("hops.modifier_scroll", text="Modifier Scroll", icon_value=get_icon_id("Diagonal"))
        op.additive = True
        op.all = True

        layout.operator("hops.bool_toggle_viewport", text= "Toggle Modifiers", icon_value=get_icon_id("Ngons")).all_modifiers = False

        layout.separator()

        layout.menu("HOPS_MT_Export", text = 'Export', icon="EXPORT")
