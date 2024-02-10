import bpy
from .. icons import get_icon_id, icons
from .. utils.addons import addon_exists
from .. preferences import get_preferences
from .. utils.objects import get_current_selected_status
from .. import bl_info


class HOPS_MT_MainPie(bpy.types.Menu):
    bl_idname = "HOPS_MT_MainPie"
    bl_label = f"HOps: {bl_info['version'][0]}.{bl_info['version'][1]}.{bl_info['version'][2]}.{bl_info['version'][3]}"

    def draw(self, context):
        layout = self.layout
        active_object = context.active_object

        if active_object is None:
            self.draw_without_active_object_pie(layout)
        elif active_object.mode == "OBJECT":
            if active_object.type == "LATTICE":
                self.draw_lattice_menu(layout)
            elif active_object.type == "CURVE":
                self.draw_curve_menu(layout)
            elif active_object.type == "LIGHT":
                self.draw_lamp_menu(layout)
            elif active_object.type == "CAMERA":
                self.draw_camera_menu(layout, context)
            elif active_object.type == "EMPTY":
                self.draw_empty_menu(layout, context)
            else:
                self.draw_object_mode_pie(layout)
        elif active_object.mode == "EDIT":
            self.draw_edit_mode_pie(layout, active_object)
        elif active_object.mode == 'POSE':
            self.draw_rigging_menu(layout)
        elif active_object.mode == "SCULPT":
            self.draw_sculpt_menu(layout, context)
        elif active_object.mode == "PAINT_GPENCIL":
            self.draw_pencil_menu(layout, context)
        else:
            self.draw_others(layout, context)

    # Without Selection
    ############################################################################

    def draw_without_active_object_pie(self, layout):
        wm = bpy.context.window_manager
        pie = self.layout.menu_pie()
        pie.column().label()

        # top
        pie.column().label()
        pie.column().label()

        box = pie.box()
        col = box.column()
        col.menu("HOPS_MT_RenderSetSubmenu", text="RenderSets")  # , icon_value=get_icon_id("Gui"))
        col.menu("HOPS_MT_ViewportSubmenu", text="ViewPort")  # , icon_value=get_icon_id("Viewport"))
        # col.menu("HOPS_MT_SettingsSubmenu", text="Settings")  # , icon_value=get_icon_id("Gui"))

        pie.column().label()
        pie.column().label()

    # Always
    ############################################################################

    # Object Mode
    ############################################################################

    def drawpie_options_all(self, layout):
        pie = self.layout.menu_pie()
        split = pie.box().split(align=True)
        col = split.column(align=True)
        col.scale_x = 1.3
        col.scale_y = 1.3
        row = col.row(align=True)
        row.menu("SCREEN_MT_user_menu", text="", icon="WINDOW")

    def draw_others(self, layout, object):
        pie = self.layout.menu_pie()
        pie.column().label()
        pie.column().label()
        pie.column().label()
        self.drawpie_options_all(layout)
        pie.column().label()
        pie.column().label()
        pie.column().label()
        pie.column().label()

    def draw_object_mode_pie(self, layout):
        active_object, other_objects, other_object = get_current_selected_status()
        only_meshes_selected = all(object.type == "MESH" for object in bpy.context.selected_objects)
        object = bpy.context.active_object

        if len(bpy.context.selected_objects) == 1:

            # if object.hops.status == "UNDEFINED":
            if active_object is not None and other_object is None and only_meshes_selected:
                self.drawpie_only_with_active_object(layout, active_object)

        elif len(bpy.context.selected_objects) >= 2:
            self.drawpie_with_active_object_and_other_mesh(layout, active_object)

        else:
            self.draw_without_active_object_pie(layout)

    def drawpie_only_with_AP_as_active_object(self, layout, object):
        pie = self.layout.menu_pie()
        pie.operator("hops.remove_merge", text="Remove Merge")  # , icon_value=get_icon_id("Merge"))
        self.mod_options(layout)
        pie.operator("hops.copy_merge", text="Copy Merge")  # , icon_value=get_icon_id("Merge"))
        self.drawpie_options(layout)
        pie.column().label()
        pie.column().label()
        pie.operator("hops.remove_merge", text="coming soon", icon_value=get_icon_id("Merge"))
        pie.operator("hops.mirror_gizmo", text="", icon="MOD_MIRROR")

    def drawpie_only_with_active_object(self, layout, object):
        pie = self.layout.menu_pie()
        object = bpy.context.active_object

        pie.operator("hops.adjust_tthick", text="Solidify", icon_value=get_icon_id("Tthick"))
        self.mod_options(layout)
        pie.operator("hops.sharpen", text="Sharpen", icon_value=get_icon_id("Ssharpen"))
        self.drawpie_options(layout)
        pie.column().label()
        pie.column().label()
        pie.operator("hops.adjust_bevel", text="Bevel", icon_value=get_icon_id("AdjustBevel"))
        pie.operator("hops.mirror_gizmo", text="", icon="MOD_MIRROR")

    def draw_boolshape_menu(self, layout):
        pie = self.layout.menu_pie()

        pie.operator("hops.adjust_tthick", text="Solidify", icon_value=get_icon_id("ReBool"))
        self.mod_options(layout)
        if get_preferences().property.menu_array_type == 'ST3':
            pie.operator("hops.super_array", text="Array (ST3)", icon_value=get_icon_id("Display_operators"))
        elif get_preferences().property.menu_array_type == 'ST3_V2':
            pie.operator("hops.st3_array", text="Array V2(ST3)", icon_value=get_icon_id("GreyArrayX"))
        else:
            pie.operator("hops.adjust_array", text="Array", icon="MOD_ARRAY")
        self.drawpie_options(layout)
        pie.column().label()
        pie.column().label()
        pie.operator("hops.adjust_bevel", text="(B) Width", icon_value=get_icon_id("AdjustBevel"))
        col = pie.column(align=True)
        colrow = col.row(align=True)
        colrow.operator("hops.boolshape_status_swap", text="Boolshape")
        colrow.operator("clean.sharps", text="Clean")

    def drawpie_with_active_object_and_other_mesh(self, layout, active_object):
        pie = self.layout.menu_pie()

        pie.operator("hops.adjust_tthick", text="Solidify", icon_value=get_icon_id("Tthick"))
        self.mod_options(layout)
        pie.operator("hops.sharpen", text="Sharpen", icon_value=get_icon_id("SSharpen"))
        self.drawpie_options(layout)
        pie.column().label()
        pie.column().label()

        pie.operator("hops.adjust_bevel", text="(B) Width", icon_value=get_icon_id("AdjustBevel"))
        pie.operator("hops.mirror_gizmo", text="", icon="MOD_MIRROR")

    def mod_edit_options(self, layout):
        pie = self.layout.menu_pie()
        maincol = pie.column()
        split = maincol.box().row(align=True)
        row = split.row(align=True)
        col = row.column(align=True)
        col.scale_x = 1.3
        col.scale_y = 1.3

        if get_preferences().property.pie_mod_expand:

            col.operator("hops.adjust_bevel", text="", icon="MOD_BEVEL")
            col.operator("hops.mod_lattice", text="", icon="MOD_LATTICE")
            col.operator("hops.mod_hook", text="", icon="HOOK")
            col.operator("hops.mod_mask", text="", icon="MOD_MASK")
            row = split.row(align=True)
            col = row.column(align=True)
            col.scale_x = 1.3
            col.scale_y = 1.3

            col.operator("hops.mod_weld", text="", icon="AUTOMERGE_OFF")

            split.separator()
            row = split.row(align=True)
            col = row.column(align=True)
            col.scale_x = 1.3
            col.scale_y = 1.3

        col.operator("hops.edit_bool_difference", text="", icon_value=get_icon_id("red"))
        col.operator("hops.edit_bool_union", text="", icon_value=get_icon_id("green"))
        col.operator("hops.edit_bool_intersect", text="", icon_value=get_icon_id("orange"))

        row = split.row(align=True)
        col = row.column(align=True)
        col.scale_x = 1.3
        col.scale_y = 1.3

        col.operator("hops.edit_bool_inset", text="", icon_value=get_icon_id("purple"))
        col.operator("hops.edit_bool_knife", text="", icon_value=get_icon_id("blue"))
        col.operator("hops.edit_bool_slash", text="", icon_value=get_icon_id("yellow"))
        if get_preferences().property.pie_mod_expand:
            col.prop(get_preferences().property, "pie_mod_expand", text="", icon="TRIA_LEFT")
        else:
            col.prop(get_preferences().property, "pie_mod_expand", text="", icon="TRIA_RIGHT")

        maincol.label()
        maincol.label()

    def mod_options(self, layout):
        pie = self.layout.menu_pie()
        maincol = pie.column()
        split = maincol.box().row(align=True)
        row = split.row(align=True)
        col = row.column(align=True)
        col.scale_x = 1.3
        col.scale_y = 1.3

        if get_preferences().property.pie_mod_expand:

            col.operator("hops.adjust_tthick", text="", icon="MOD_SOLIDIFY")
            col.operator("hops.mod_screw", text="", icon="MOD_SCREW")
            col.operator("hops.mod_simple_deform", text="", icon="MOD_SIMPLEDEFORM")
            col.operator("hops.mod_shrinkwrap", text="", icon="MOD_SHRINKWRAP")
            row = split.row(align=True)
            col = row.column(align=True)
            col.scale_x = 1.3
            col.scale_y = 1.3

            if get_preferences().property.menu_array_type == 'ST3':
                col.operator("hops.super_array", text="", icon_value=get_icon_id("Display_operators"))
            elif get_preferences().property.menu_array_type == 'ST3_V2':
                col.operator("hops.st3_array", text="", icon_value=get_icon_id("GreyArrayX"))
            else:
                col.operator("hops.array_gizmo", text="", icon="MOD_ARRAY")
            col.operator("hops.mod_triangulate", text="", icon="MOD_TRIANGULATE")
            col.operator("hops.mod_wireframe", text="", icon="MOD_WIREFRAME")
            col.operator("hops.mod_cast", text="", icon="MOD_CAST")
            row = split.row(align=True)
            col = row.column(align=True)
            col.scale_x = 1.3
            col.scale_y = 1.3

            col.operator("hops.mod_lattice", text="", icon="MOD_LATTICE")
            col.operator("hops.mod_weighted_normal", text="", icon="MOD_NORMALEDIT")
            col.operator("hops.mod_displace", text="", icon="MOD_DISPLACE")
            col.operator("hops.mod_decimate", text="", icon="MOD_DECIM")
            row = split.row(align=True)
            col = row.column(align=True)
            col.scale_x = 1.3
            col.scale_y = 1.3

            col.operator("hops.adjust_bevel", text="", icon="MOD_BEVEL")
            col.operator("hops.mod_subdivision", text="", icon="MOD_SUBSURF")
            # col.operator("hops.mod_displace", text="", icon="MOD_DISPLACE")
            col.operator("hops.mod_skin", text="", icon="MOD_SKIN")
            col.operator("hops.mod_weld", text="", icon="AUTOMERGE_OFF")

            row = split.row(align=True)
            col = row.column(align=True)
            col.scale_x = 1.3
            col.scale_y = 1.3

            col.operator("hops.mod_smooth", text="", icon="MOD_SMOOTH")
            col.operator("hops.mod_uv_project", text="", icon="MOD_UVPROJECT")
            col.operator("hops.mod_apply", text="", icon="REC")
            # col.operator("hops.mod_displace", text="", icon="MOD_DISPLACE")

            split.separator()

            row = split.row(align=True)
            col = row.column(align=True)
            col.scale_x = 1.3
            col.scale_y = 1.3


        col.operator("hops.bool_difference", text="", icon_value=get_icon_id("red"))
        col.operator("hops.bool_union", text="", icon_value=get_icon_id("green"))
        col.operator("hops.bool_intersect", text="", icon_value=get_icon_id("orange"))

        row = split.row(align=True)
        col = row.column(align=True)
        col.scale_x = 1.3
        col.scale_y = 1.3

        col.operator("hops.bool_inset", text="", icon_value=get_icon_id("purple"))
        col.operator("hops.bool_knife", text="", icon_value=get_icon_id("blue"))
        col.operator("hops.slash", text="", icon_value=get_icon_id("yellow"))

        if get_preferences().property.pie_mod_expand:
            col.prop(get_preferences().property, "pie_mod_expand", text="", icon="TRIA_LEFT")
        else:
            col.prop(get_preferences().property, "pie_mod_expand", text="", icon="TRIA_RIGHT")

        maincol.label()
        maincol.label()

    def drawpie_options(self, layout):
        pie = self.layout.menu_pie()
        split = pie.box().split(align=True)
        col = split.column(align=True)
        col.scale_x = 1.3
        col.scale_y = 1.3
        row = col.row(align=True)

        # col.popover(panel='HOPS_MT_ObjectsOperatorsSubmenu', text='', icon="MOD_MIRROR")
        # col.popover(panel='HOPS_MT_ObjectToolsSubmenu', text='', icon="MOD_MIRROR")
        # col.popover(panel='HOPS_MT_SettingsSubmenu', text='', icon="MOD_MIRROR")
        # col.popover(panel='SCREEN_MT_user_menu', text='', icon="MOD_MIRROR")

        if addon_exists("kitops"):
            if hasattr(bpy.context.window_manager, 'kitops'):
                row.operator('view3d.insertpopup', text = '', icon_value=get_icon_id("Insert"))
                row.separator()
        row.menu("HOPS_MT_ObjectsOperatorsSubmenu", text="", icon="SNAP_FACE")
        row.separator()
        row.menu("HOPS_MT_ObjectToolsSubmenu", text="", icon="OBJECT_DATAMODE")
        row.separator()
        row.menu("HOPS_MT_SettingsSubmenu", text="", icon="PREFERENCES")
        row.separator()
        row.menu("SCREEN_MT_user_menu", text="", icon="WINDOW")

    def draw_lattice_menu(self, layout):
        pie = self.layout.menu_pie()

        pie.row().prop(bpy.context.object.data, "points_u", text="X")
        pie.operator("hops.simplify_lattice", text="Simplify")
        pie.row().prop(bpy.context.object.data, "points_v", text="Y")
        pie.column().label()
        pie.column().label()
        pie.prop(bpy.context.object.data, "use_outside")
        pie.row().prop(bpy.context.object.data, "points_w", text="Z")
        pie.column().label()

    def draw_curve_menu(self, layout):
        pie = self.layout.menu_pie()
        pie.operator("hops.curve_bevel", text="Curve bevel")
        pie.column().label()
        pie.column().label()
        pie.column().label()
        pie.column().label()
        self.drawpie_options(layout)
        pie.operator("hops.adjust_curve", text="Adjust Curve")
        pie.column().label()

    def draw_rigging_menu(self, layout):
        pie = self.layout.menu_pie()
        pie.column().label()
        pie.column().label()
        pie.column().label()
        pie.column().label()
        pie.column().label()
        self.drawpie_options(layout)
        pie.operator("object.create_driver_constraint", text="Driver Constraint")
        pie.column().label()

    def draw_lamp_menu(self, layout):
        pie = self.layout.menu_pie()
        pie.column().label()
        c = bpy.context.scene
        if c.render.engine == 'BLENDER_EEVEE':
            pie.prop(bpy.context.object.data, "energy", text="Energy")
            pie.prop(bpy.context.object.data, "use_contact_shadow", text="Contact Shadow")
            if bpy.context.object.data.type == 'AREA':
                pie.prop(bpy.context.object.data, "shape", text = '')
            pie.separator()
            pie.prop(bpy.context.scene.eevee,"use_soft_shadows", text = "SCN_Soft Shadows")
            pie.prop(bpy.context.scene.eevee, "use_gtao", text = "SCN_Global AO")
        else:
            pie.label(text="No Lamp Options Yet")
        pie.column().label()

    def draw_camera_menu(self, layout, context):
        # cam = context.camera

        pie = self.layout.menu_pie()
        pie.column().label()
        split = pie.box().split(align=True)
        col = split.column()
        col.prop(context.object.data, "sensor_fit", text="sensor fit")
        if context.object.data.sensor_fit == 'AUTO':
            col.prop(context.object.data, "sensor_width", text="Width")
        else:
            col.prop(context.object.data, "sensor_width", text="Width")
            col.prop(context.object.data, "sensor_height", text="Height")

        pie.column().label()

        split = pie.box().split(align=True)
        col = split.column()
        col.prop(context.object.data, "lens", text="Lens")
        col.prop(context.object.data, "passepartout_alpha", text="PP")
        col.prop(context.object.data, "dof_object", text="")
        col.prop(context.object.data.cycles, "aperture_size", text="DOF Size")

        pie.column().label()
        pie.column().label()
        pie.operator("hops.set_camera", text="Set Active Cam")
        pie.column().label()

    def draw_empty_menu(self, layout, context):
        pie = self.layout.menu_pie()

        pie.column().label()
        pie.operator("hops.set_empty_image", text="Set Image")
        pie.column().label()
        pie.column().label()
        pie.column().label()
        self.drawpie_options(layout)
        pie.column().label()
        pie.operator("hops.mirror_gizmo", text="", icon_value=get_icon_id("AdjustBevel"))

    def draw_sculpt_menu(self, layout, context):
        pie = self.layout.menu_pie()
        pie.prop(context.tool_settings.sculpt, "use_smooth_shading")

        if context.sculpt_object.use_dynamic_topology_sculpting:
            pie.operator("sculpt.dynamic_topology_toggle", text="Disable Dyntopo")
        else:
            pie.operator("sculpt.dynamic_topology_toggle", text="Enable Dyntopo")

        pie.operator("sculpt.symmetrize")

        split = pie.box().split(align=True)
        col = split.column()
        col.prop(context.tool_settings.sculpt, "detail_refine_method", text="")
        col.prop(context.tool_settings.sculpt, "detail_type_method", text="")
        col.prop(context.tool_settings.sculpt, "symmetrize_direction", text="")
        if (context.tool_settings.sculpt.detail_type_method == 'CONSTANT'):
            col.prop(context.tool_settings.sculpt, "constant_detail")
            col.operator("sculpt.sample_detail_size", text="", icon='EYEDROPPER')
        elif (context.tool_settings.sculpt.detail_type_method == 'BRUSH'):
            col.prop(context.tool_settings.sculpt, "detail_percent")
        else:
            col.prop(context.tool_settings.sculpt, "detail_size")

        if (context.tool_settings.sculpt.detail_type_method == 'CONSTANT'):
            pie.operator("sculpt.detail_flood_fill")
        else:
            pie.column().label()

        pie.operator("hops.shrinkwrap_refresh", text="Shrinkwrap Refresh").sculpt = True
        pie.operator("sculpt.optimize")
        pie.column().label()

    def draw_pencil_menu(self, layout, context):
        pie = self.layout.menu_pie()

        pie.operator("hops.surfaceoffset", text="Surface OffSet", icon_value=get_icon_id("dots"))
        pie.column().label()
        pie.operator("hops.copy_move", text="Copy / Move", icon_value=get_icon_id("dots"))
        self.drawpie_options(layout)
        pie.column().label()
        pie.column().label()
        pie.operator("hops.surfaceoffset", text="Surface OffSet", icon_value=get_icon_id("dots"))
        pie.operator("hops.mirror_gizmo", text="", icon="MOD_MIRROR")

    # Edit Mode
    ############################################################################

    def draw_edit_mode_pie(self, layout, object):
        pie = self.layout.menu_pie()
        # left
        pie.operator("hops.star_connect", text="Star Connect")
        # right
        self.mod_edit_options(layout)
        # bot
        pie.operator("hops.set_edit_sharpen", text="Set Sharp")
        # top

        pie = self.layout.menu_pie()
        split = pie.box().split(align=True)
        col = split.column(align=True)
        col.scale_x = 1.3
        col.scale_y = 1.3
        row = col.row(align=True)

        row.menu("HOPS_MT_MeshOperatorsSubmenu", text="", icon="SNAP_FACE")
        row.separator()
        row.operator("hops.reset_axis_modal", text="", icon_value=get_icon_id("Xslap"))
        if bpy.context.object and bpy.context.object.type == 'MESH':
            row.separator()
            row.menu("HOPS_MT_MaterialListMenu", text="", icon_value=get_icon_id("StatusOveride"))
        row.separator()
        row.menu("SCREEN_MT_user_menu", text="", icon="WINDOW")

        # top L
        pie.column().label()
        # top R
        pie.column().label()
        # pie.operator("hops.analysis", text="Analysis")
        # bot L
        pie.operator("hops.bevel_weight", text="(B)Weight", icon_value=get_icon_id("AdjustBevel"))
        # bot R
        pie.operator("hops.mirror_gizmo", text="", icon="MOD_MIRROR")
