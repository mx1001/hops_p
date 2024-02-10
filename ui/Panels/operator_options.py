import bpy
from bpy.types import Panel

from ... preferences import get_preferences


class HOPS_PT_operator_options(Panel):
    bl_label = 'Operator Options'
    bl_space_type = 'VIEW_3D'
    bl_category = 'HardOps'
    bl_region_type = 'UI'


    def draw(self, context):
        layout = self.layout
        preference = get_preferences().property
        color = get_preferences().color
        ui = get_preferences().ui

        column = layout.column(align=True)
        row = column.row(align=True)
        row.label(text='Bevel Profile:')
        row = column.row(align=True)
        row.prop(preference, 'bevel_profile', text='bevel profile')
        column.separator()
        # column.separator()
        # row = column.row(align=True)
        # row.prop(preference, 'Hops_twist_radial_sort', text='Radial / Twist (Render Toggle)')
        # row = column.row(align=True)
        # row.prop(preference, 'to_cam_jump', text='To_Cam Jump')
        # row.prop(preference, 'to_render_jump', text='Viewport+ Set Render')
        # if get_preferences().property.menu_array_type == 'ST3':
        #     row = column.row(align=True)
        #     row.prop(preference, 'array_type', text='ST3 Array Gizmo')
        column.separator()

        # row = column.row(align=True)
        # row.label(text='Circle:')
        # row = column.row(align=True)
        # row.prop(preference, 'circle_divisions', expand=True, text='Circle (E) Divisions')

        row = column.row(align=True)
        row.label(text='CSharpen:')
        row = column.row(align=True)

        column.separator()

        row = column.row(align=True)
        row.prop(preference, 'bevel_loop_slide', text='use Loop slide')
        row = column.row(align=True)
        row.prop(preference, 'auto_bweight', text='jump to (B)Width')

        row = column.row(align=True)
        row.prop(preference, 'Hops_sharp_remove_cutters', text='Remove Cutters')

        row = column.row(align=True)
        # row.label(text='Mirror:')

        # row = column.row(align=True)
        # row.prop(preference, 'Hops_mirror_modal_scale', text='Mirror Scale')
        # row.prop(preference, 'Hops_mirror_modal_sides_scale', text='Mirror Size')

        # row = column.row(align=True)
        # row.prop(preference, 'Hops_mirror_modal_Interface_scale', text='Mirror Interface Scale')
        # row.prop(preference, 'Hops_mirror_modal_revert', text='Revert')

        # row = column.row(align=True)
        # row.prop(preference, 'Hops_gizmo_mirror_u', text='mirror u')
        # row.prop(preference, 'Hops_gizmo_mirror_v', text='mirror v')

        column.separator()
        column.separator()

        row = column.row(align=True)
        row.label(text='Cut In:')
        row = column.row(align=True)
        row.prop(preference, 'keep_cutin_bevel', expand=True, text='Bool:CutIn - Keep Bevel')

        # column.separator()
        #
        # row = column.row(align=True)
        # row.label(text='Array:')
        # row = column.row(align=True)
        # row.prop(preference, 'force_array_reset_on_init', expand=True, text='Array Reset on Init')
        #
        # row = column.row(align=True)
        # row.prop(preference, 'force_array_apply_scale_on_init', expand=True, text='Array Scale Apply on Init')
        #
        # column.separator()
        # column.separator()
        #
        # row = column.row(align=True)
        # row.label(text='Thick:')
        # row = column.row(align=True)
        # row.prop(preference, 'force_thick_reset_solidify_init', expand=True, text='Solidify Reset on Init')
        #
        # column.separator()
        #
        # row = column.row(align=True)
        # row.label(text='Modals:')
        # row = column.row(align=True)
        #
        # column.separator()

        row = column.row(align=True)
        #row.prop(preference, 'Hops_modal_scale', text='Modal Scale')
        row.prop(preference, 'adaptivewidth', text='Adaptive')

        column.separator()
