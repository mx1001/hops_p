import bpy
from mathutils import Vector


def apply_modifiers(object, modtype):
    for obj in object:
        if obj.type == "MESH":
            for mod in obj.modifiers:
                if mod.type in modtype:
                    bpy.ops.object.modifier_apply(modifier=mod.name) # apply_as='DATA',


def remove_modifiers(object, modtype):
    # objects = bpy.data.objects
    for obj in object:
        if obj.type == "MESH":
            modifiers = obj.modifiers
            for mod in modifiers:
                if mod.type == modtype:
                    obj.modifiers.remove(mod)


def get_mod_copy(mod):
    '''Copy a modifier into a class object and return the copy.'''
    
    atts = [a for a in dir(mod) if "__" not in a]

    dict = {}
    for att in atts:

        # Convert bpy prop types to simple data types for copy
        if att == 'relative_offset_displace':
            vec = getattr(mod, att)
            dict[att] = [vec[0], vec[1], vec[2]]

        elif att == 'constant_offset_displace':
            vec = getattr(mod, att)
            dict[att] = [vec[0], vec[1], vec[2]]

        else:
            dict[att] = getattr(mod, att)

    cls = type(mod.name, (), dict)

    return cls


def transfer_mod_data(active_mod, copied_mod):
    '''Takes the active mod and sets its values to the copied mod.'''
    
    copied_atts = { a : getattr(copied_mod, a) for a in dir(copied_mod) if "__" not in a} 
    types = [type(True), type(1), type(1.0), type("Str"), Vector, list]
    
    for key, val in copied_atts.items():
        if type(val) in types:
            try:
                setattr(active_mod, key, val)
            except:
                pass