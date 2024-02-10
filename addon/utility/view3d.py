import bpy
import math
import bl_ui

from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d, location_3d_to_region_2d, region_2d_to_location_3d
from mathutils.geometry import intersect_line_plane

from . import addon, active_tool
from .. panel import statusicon


def location2d_to_origin3d(x, y):
    return region_2d_to_origin_3d(bpy.context.region, bpy.context.region_data, (x, y))


def location2d_to_vector3d(x, y):
    return region_2d_to_vector_3d(bpy.context.region, bpy.context.region_data, (x, y))


def location2d_intersect3d(x, y, location, normal):
    origin = location2d_to_origin3d(x, y)
    return intersect_line_plane(origin, origin + location2d_to_vector3d(x, y), location, normal)


def location3d_to_location2d(location):
    return location_3d_to_region_2d(bpy.context.region, bpy.context.region_data, location)


def location2d_to_location3d(x, y, location):
    return region_2d_to_location_3d(bpy.context.region, bpy.context.region_data, (x, y), location)


def view_orientation():
    # self.region_3d.view_rotation
    r = lambda x: round(x, 3)
    view_rot = bpy.context.region_data.view_rotation.to_euler()

    orientation_dict = {(0.0, 0.0, 0.0): 'TOP',
                        (r(math.pi), 0.0, 0.0): 'BOTTOM',
                        (r(math.pi/2), 0.0, 0.0): 'FRONT',
                        (r(math.pi/2), 0.0, r(math.pi)): 'BACK',
                        (r(math.pi/2), 0.0, r(-math.pi/2)): 'LEFT',
                        (r(math.pi/2), 0.0, r(math.pi/2)): 'RIGHT'}

    return orientation_dict.get(tuple(map(r, view_rot)), 'UNDEFINED')


def tool_header_original(ht, context): pass


def tool_header(ht, context):
    if active_tool().idname in {'Hops', 'Hardflow'}:
        layout = ht.layout

        layout.row(align=True).template_header()

        ht.draw_tool_settings(context)

        layout.separator_spacer()

        ht.draw_mode_settings(context)
    else:
        tool_header_original(ht, context)


def header_original(ht, context): pass


def header(ht, context):
    if active_tool().idname in {'Hops', 'Hardflow'}:
        layout = ht.layout

        tool_settings = context.tool_settings
        view = context.space_data
        shading = view.shading
        # mode_string = context.mode
        obj = context.active_object
        show_region_tool_header = view.show_region_tool_header

        if not show_region_tool_header:
            layout.row(align=True).template_header()

        row = layout.row(align=True)
        object_mode = 'OBJECT' if obj is None else obj.mode

        # Note: This is actually deadly in case enum_items have to be dynamically generated
        #       (because internal RNA array iterator will free everything immediately...).
        # XXX This is an RNA internal issue, not sure how to fix it.
        # Note: Tried to add an accessor to get translated UI strings instead of manual call
        #       to pgettext_iface below, but this fails because translated enumitems
        #       are always dynamically allocated.
        act_mode_item = bpy.types.Object.bl_rna.properties["mode"].enum_items[object_mode]
        act_mode_i18n_context = bpy.types.Object.bl_rna.properties["mode"].translation_context

        sub = row.row(align=True)
        sub.ui_units_x = 5.5
        sub.operator_menu_enum(
            "object.mode_set", "mode",
            text=bpy.app.translations.pgettext_iface(act_mode_item.name, act_mode_i18n_context),
            icon=act_mode_item.icon,
        )
        del act_mode_item

        layout.template_header_3D_mode()

        # Contains buttons like Mode, Pivot, Layer, Mesh Select Mode...
        if obj:
            # Particle edit
            if object_mode == 'PARTICLE_EDIT':
                row = layout.row()
                row.prop(tool_settings.particle_edit, "select_mode", text="", expand=True)

        # Grease Pencil
        if obj and obj.type == 'GPENCIL' and context.gpencil_data:
            gpd = context.gpencil_data

            if gpd.is_stroke_paint_mode:
                row = layout.row()
                sub = row.row(align=True)
                sub.prop(tool_settings, "use_gpencil_draw_onback", text="", icon='MOD_OPACITY')
                sub.separator(factor=0.4)
                sub.prop(tool_settings, "use_gpencil_weight_data_add", text="", icon='WPAINT_HLT')
                sub.separator(factor=0.4)
                sub.prop(tool_settings, "use_gpencil_draw_additive", text="", icon='FREEZE')

            if gpd.use_stroke_edit_mode:
                row = layout.row(align=True)
                row.prop(tool_settings, "gpencil_selectmode", text="", expand=True)

            if gpd.use_stroke_edit_mode or gpd.is_stroke_sculpt_mode or gpd.is_stroke_weight_mode:
                row = layout.row(align=True)

                if gpd.is_stroke_sculpt_mode:
                    row.prop(tool_settings.gpencil_sculpt, "use_select_mask", text="")
                    row.separator()

                row.prop(gpd, "use_multiedit", text="", icon='GP_MULTIFRAME_EDITING')

                sub = row.row(align=True)
                sub.active = gpd.use_multiedit
                sub.popover(
                    panel="VIEW3D_PT_gpencil_multi_frame",
                    text="Multiframe",
                )

            if gpd.use_stroke_edit_mode:
                row = layout.row(align=True)
                row.prop(tool_settings.gpencil_sculpt, "use_select_mask", text="")

                row.popover(
                    panel="VIEW3D_PT_tools_grease_pencil_interpolate",
                    text="Interpolate",
                )

        overlay = view.overlay

        bl_ui.space_view3d.VIEW3D_MT_editor_menus.draw_collapsible(context, layout)

        layout.separator_spacer()

        bl_ui.space_view3d.VIEW3D_HT_header.draw_xform_template(layout, context)

        layout.separator_spacer()

        if object_mode in {'PAINT_GPENCIL', 'SCULPT_GPENCIL'}:
            # Grease pencil
            if object_mode == 'PAINT_GPENCIL':
                layout.prop_with_popover(
                    tool_settings,
                    "gpencil_stroke_placement_view3d",
                    text="",
                    panel="VIEW3D_PT_gpencil_origin",
                )

            if object_mode in {'PAINT_GPENCIL', 'SCULPT_GPENCIL'}:
                layout.prop_with_popover(
                    tool_settings.gpencil_sculpt,
                    "lock_axis",
                    text="",
                    panel="VIEW3D_PT_gpencil_lock",
                )

            if object_mode == 'PAINT_GPENCIL':
                # FIXME: this is bad practice!
                # Tool options are to be displayed in the topbar.
                if context.workspace.tools.from_space_view3d_mode(object_mode).idname == "builtin_brush.Draw":
                    settings = tool_settings.gpencil_sculpt.guide
                    row = layout.row(align=True)
                    row.prop(settings, "use_guide", text="", icon='GRID')
                    sub = row.row(align=True)
                    sub.active = settings.use_guide
                    sub.popover(
                        panel="VIEW3D_PT_gpencil_guide",
                        text="Guides",
                    )

            layout.separator_spacer()
        elif not show_region_tool_header:
            # Transform settings depending on tool header visibility
            bl_ui.space_view3d.VIEW3D_HT_header.draw_xform_template(layout, context)

            layout.separator_spacer()

        # Viewport Settings
        layout.popover(
            panel="VIEW3D_PT_object_type_visibility",
            icon_value=view.icon_from_show_object_viewport,
            text="",
        )

        # Gizmo toggle & popover.
        row = layout.row(align=True)
        # FIXME: place-holder icon.
        row.prop(view, "show_gizmo", text="", toggle=True, icon='GIZMO')
        sub = row.row(align=True)
        sub.active = view.show_gizmo
        sub.popover(
            panel="VIEW3D_PT_gizmo_display",
            text="",
        )

        # Overlay toggle & popover.
        row = layout.row(align=True)
        row.prop(overlay, "show_overlays", icon='OVERLAY', text="")
        sub = row.row(align=True)
        sub.active = overlay.show_overlays
        sub.popover(panel="VIEW3D_PT_overlay", text="")

        row = layout.row()
        row.active = (object_mode == 'EDIT') or (shading.type in {'WIREFRAME', 'SOLID'})

        if shading.type == 'WIREFRAME':
            row.prop(shading, "show_xray_wireframe", text="", icon='XRAY')
        else:
            row.prop(shading, "show_xray", text="", icon='XRAY')

        row = layout.row(align=True)
        row.prop(shading, "type", text="", expand=True)
        sub = row.row(align=True)
        # TODO, currently render shading type ignores mesh two-side, until it's supported
        # show the shading popover which shows double-sided option.

        # sub.enabled = shading.type != 'RENDERED'
        sub.popover(panel="VIEW3D_PT_shading", text="")

        # row = layout.row()
        # row.popover('HOPS_PT_Button', text='', icon_value=statusicon(ht, context))

    else:
        header_original(ht, context)


def add_hops_headers():
    return

    global header_original
    global tool_header_original

    header_original = bl_ui.space_view3d.VIEW3D_HT_header.draw
    tool_header_original = bl_ui.space_view3d.VIEW3D_HT_tool_header.draw

    bl_ui.space_view3d.VIEW3D_HT_header.draw = header
    bl_ui.space_view3d.VIEW3D_HT_tool_header.draw = tool_header


def remove_hops_headers():
    return

    bl_ui.space_view3d.VIEW3D_HT_header.draw = header_original
    bl_ui.space_view3d.VIEW3D_HT_tool_header.draw = tool_header_original
