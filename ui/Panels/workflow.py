import bpy
from bpy.types import Panel

from ... preferences import get_preferences
from ... utility import modifier

class HOPS_PT_workflow(Panel):
    bl_label = 'Workflow'
    bl_space_type = 'VIEW_3D'
    bl_category = 'HardOps'
    bl_region_type = 'UI'


    def draw(self, context):
        layout = self.layout
        preference = get_preferences().property

        column = layout.column(align=True)

        row = column.row(align=True)
        row.prop(preference, 'workflow', expand=True)

        row = column.row(align=True).split(factor=0.1, align=True)
        row.prop(preference, 'add_weighten_normals_mod', toggle=True)

        row2 = row.row(align=True).split(factor=0.1, align=True)
        row2.prop(preference, 'use_harden_normals', toggle=True)

        sub = row2.row(align=True)
        sub.prop(preference, 'workflow_mode', expand=True)

        column.separator()

        row = column.row(align=True)
        row.prop(preference, 'sort_modifiers', text='sort modifiers', expand=True)

        if preference.sort_modifiers:
            row = row.row(align=True)
            row.scale_x = 1.5
            row.alignment = 'RIGHT'
            split = row.split(align=True, factor=0.85)

            row = split.row(align=True)
            for type in modifier.sort_types:
                icon = F'MOD_{type}'
                if icon == 'MOD_WEIGHTED_NORMAL':
                    icon = 'MOD_NORMALEDIT'
                elif icon == 'MOD_SIMPLE_DEFORM':
                    icon = 'MOD_SIMPLEDEFORM'
                elif icon == 'MOD_DECIMATE':
                    icon = 'MOD_DECIM'
                elif icon == 'MOD_WELD':
                    icon = 'AUTOMERGE_OFF'
                elif icon == 'MOD_UV_PROJECT':
                    icon = 'MOD_UVPROJECT'
                row.prop(preference, F'sort_{type.lower()}', text='', icon=icon)

            row = split.row(align=True)
            row.scale_x = 1.5
            row.popover('HOPS_PT_sort_last', text='', icon='SORT_ASC')

        # sub = row.row(align=True)
        # sub.alignment = 'RIGHT'

        # if get_preferences().property.sort_bevel:
        #     sub.prop(get_preferences().property, 'sort_bevel_last', text='', icon='SORT_ASC')
        #     sub.separator()
        # sub.prop(preference, 'sort_bevel', text='', icon='MOD_BEVEL')
        # sub.prop(preference, 'sort_array', text='', icon='MOD_ARRAY')
        # sub.prop(preference, 'sort_mirror', text='', icon='MOD_MIRROR')
        # sub.prop(preference, 'sort_solidify', text='', icon='MOD_SOLIDIFY')
        # sub.prop(preference, 'sort_weighted_normal', text='', icon='MOD_NORMALEDIT')
        # sub.prop(preference, 'sort_simple_deform', text='', icon='MOD_SIMPLEDEFORM')
        # sub.prop(preference, 'sort_triangulate', text='', icon='MOD_TRIANGULATE')
        # sub.prop(preference, 'sort_decimate', text='', icon='MOD_DECIM')

        column.separator()
