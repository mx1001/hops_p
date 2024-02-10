import bpy
from bpy.types import Panel

from math import radians
from ... preferences import get_preferences


class HOPS_PT_sharp_options(Panel):
    bl_label = 'Sharp Options'
    bl_space_type = 'VIEW_3D'
    bl_category = 'HardOps'
    bl_region_type = 'UI'


    def draw(self, context):
        layout = self.layout
        preference = get_preferences().property
        obj = bpy.context.object
        column = layout.column(align=True)

        row = column.row(align=True)
        row.prop(preference, 'sharp_use_crease', text='Apply crease')
        row.prop(preference, 'sharp_use_bweight', text='Apply bweight')

        row = column.row(align=True)
        row.prop(preference, 'sharp_use_seam', text='Apply seam')
        row.prop(preference, 'sharp_use_sharp', text='Apply sharp')

        column.separator()

        row = column.row(align=True)
        # XXX: set sharpness ot should be fed a param rather then being 3 ot's
        row.operator('hops.set_sharpness_30', text='30')
        row.operator('hops.set_sharpness_45', text='45')
        row.operator('hops.set_sharpness_60', text='60')

        column.prop(preference, 'sharpness', text='Sharpness')

        column.separator()
        if obj:
            if obj.type == 'MESH':
                asmooth = bpy.context.object.data
                row = column.row(align=True)
                row.prop(obj.hops, "is_global", text="Global", toggle=True)
                row.prop(asmooth, "use_auto_smooth", text="Auto Smooth", toggle=True)
                row.prop(asmooth, "auto_smooth_angle", text="Auto Smooth Angle")

                row = column.row(align=True)
                row.operator('hops.set_autosmoouth', text='5').angle = radians(5)
                row.operator('hops.set_autosmoouth', text='10').angle = radians(10)
                row.operator('hops.set_autosmoouth', text='15').angle = radians(15)
                row.operator('hops.set_autosmoouth', text='30').angle = radians(30)
                row.operator('hops.set_autosmoouth', text='45').angle = radians(45)
                row.operator('hops.set_autosmoouth', text='60').angle = radians(60)
                row.operator('hops.set_autosmoouth', text='90').angle = radians(90)