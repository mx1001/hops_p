import bpy
import math
from ... preferences import get_preferences


def get_mods_list(mods: bpy.types.Modifier):
    '''Returns back the modifier list for fast UI.'''

    mods_list = []

    for mod in reversed(mods):
        if mod.type == 'BOOLEAN':
            item = mod.operation
        elif mod.type == 'WELD':
            if mod.vertex_group:
                #item = f'VGROUP: {mod.vertex_group}'
                item = f'VGROUP: {mod.merge_threshold:.3f}'
            else:
                item = f'WELD: {mod.merge_threshold:.3f}'
        elif mod.type == 'SCREW':
            angle = int(math.degrees(mod.angle))
            if angle == 0:
                item = f'EXTRUDE: {mod.axis} {mod.screw_offset:.1f}'
            elif angle == 360:
                item = f'SCREW(360): {mod.axis}'
            else:
                item = f'SCREW: {mod.axis} {angle:.0f}'
        elif mod.type == 'BEVEL':
            if custom_profile(mod):
                item = f'CUSTOM PROFILE {mod.width:.3f}'
            else:
                item = f'{mod.limit_method} {mod.width:.3f}'
        elif mod.type == 'SUBSURF':
            if mod.subdivision_type == 'SIMPLE':
                sub_d_type = 'SIMPLE'
            else:
                sub_d_type = 'CATMULL'
            item = f' {mod.levels} {sub_d_type}'
        elif mod.type == 'ARRAY':
            if mod.use_relative_offset:
                item = f'{mod.count}:RELATIVE'
            elif mod.use_constant_offset:
                item = f'{mod.count}:CONSTANT'
            elif mod.use_object_offset:
                item = f'{mod.count}:OBJECT'
            else:
                item = f'{mod.count}:UNKNOWN'
        elif mod.type == 'DISPLACE':
            item = f'{mod.direction} {mod.strength:.2f}'
        elif mod.type == 'CAST':
            item = f'{mod.cast_type} {mod.factor}'
        elif mod.type == 'SOLIDIFY':
            if mod.use_rim_only:
                RIM = 'TRUE'
            else:
                RIM = 'FALSE'
            item = f'RIM:{RIM} {mod.thickness:.2f}'
        elif mod.type == 'MIRROR':
            if mod.mirror_object:
                item = "TO_MIRROR"
            else:
                item = "MIRROR (self)"
        elif mod.type == 'WEIGHTED_NORMAL':
            if mod.keep_sharp:
                WN = 'FALSE'
            else:
                WN = 'TRUE'
            item = f'SHARP :{WN}'
        #All else fail just put mod and fill it in.
        else:
            item = str(mod.type)
        mods_list.append([mod.name, item])


    return mods_list

def custom_profile(mod):
    custom_profile = False

    if bpy.app.version > (2, 90, 0):
        if mod.profile_type == 'CUSTOM':
            custom_profile = True
        else:
            custom_profile = False
    elif bpy.app.version < (2, 90, 0):
        if mod.use_custom_profile == True:
            custom_profile = True
        else:
            custom_profile = False    
    else:
        custom_profile = False

    return custom_profile
