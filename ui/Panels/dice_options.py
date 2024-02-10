import bpy
from ... preferences import get_preferences


class HOPS_PT_dice_options(bpy.types.Panel):
    bl_label = "Dice Options"
    bl_category = "HardOps"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        preference = get_preferences().property
        self.layout.prop(preference, 'dice_method', text='Method')
        self.layout.prop(preference, 'dice_adjust', text='Adjust')
        self.layout.prop(preference, 'smart_apply_dice', text='Pre-Apply')
