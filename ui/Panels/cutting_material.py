import bpy
from bpy.types import Panel

from ... preferences import get_preferences
from ...material import blank_cutting_mat

class HOPS_PT_material_hops(Panel):
    bl_label = 'Cutting Material'
    bl_space_type = 'VIEW_3D'
    bl_category = 'HardOps'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}

    
    def draw(self, context):
        layout = self.layout
        option = context.window_manager.Hard_Ops_material_options

        row = layout.row(align=True)
        row.alignment = 'LEFT'

        column = layout.column(align=True)

        row = column.row(align=True)
        row.prop(option, 'material_mode', expand=True)

        row = column.row(align=True)

        if option.material_mode == 'ALL':
            row.prop_search(option, 'active_material', bpy.data, 'materials', text='')

        elif option.material_mode == 'OBJECT':
            row.prop_search(option, 'active_material', context.active_object, 'material_slots', text='')
        elif option.material_mode == 'BLANK':
            row.prop(option, 'color_prob')
        row.prop(option, 'force', text='', icon='FORCE_FORCE')
    #method for bridging with BC
    @staticmethod
    def blank_cut():
        
        blank_cutting_mat()
         