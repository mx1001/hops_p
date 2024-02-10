import bpy
from ... preferences import get_preferences


class HOPS_PT_bool_options(bpy.types.Panel):
    bl_label = "Bool Options"
    bl_category = "HardOps"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        preference = get_preferences().property
        self.layout.prop(preference, 'bool_bstep', text='Bool: Bevel Step')
        self.layout.prop(preference, 'parent_boolshapes', text='Bool / Sharpen: Parent Boolshapes')
        self.layout.label(text = "Remove Cutters")
        self.layout.prop(preference, 'Hops_sharp_remove_cutters', text='Csharp')
        self.layout.prop(preference, 'Hops_smartapply_remove_cutters', text='Smart Apply')
        #label_row(preference.property, 'Hops_sharp_remove_cutters', layout.row(), label='Hops_sharp_remove_cutters')
