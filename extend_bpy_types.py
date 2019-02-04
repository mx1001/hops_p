import bpy
from bpy.props import *
from . utils.objects import get_modifier_with_type

def register():
    bpy.types.Object.hops = PointerProperty(name = "HardOps Properties", type = HOpsObjectProperties)

def unregister():
    del bpy.types.Object.hops

status_items = [
    ("UNDEFINED", "Undefined", "", "NONE", 0),
    ("CSHARP", "CSharp", "", "NONE", 1),
    ("CSTEP", "CStep", "", "NONE", 2), 
    #("SUBSHARP", "SubSharp", "", "NONE", 3),
    #("SUBSTEP", "SubStep", "", "NONE", 4),
    ("BOOLSHAPE", "BoolShape", "", "NONE", 3)]

    #obj.hops.status = "BOOLSHAPE"

class HOpsObjectProperties(bpy.types.PropertyGroup):

    status = EnumProperty(name = "Status", default = "UNDEFINED", items = status_items)


    def get_is_bevel(self):
        return get_modifier_with_type(self.id_data, "BEVEL") is not None
    
    def get_is_subsharp(self):
        return get_modifier_with_type(self.id_data, "SUBSURF") is not None
        
    def get_is_solidify(self):
        return get_modifier_with_type(self.id_data, "SOLIDIFY") is not None

    def get_is_for_softmerge(self):
        return self.id_data.name.startswith("BB")

    def get_is_for_merge(self):
        return self.id_data.name.startswith("AP")

    def get_is_pending_boolean(self):
        return get_modifier_with_type(self.id_data, "BOOLEAN") is not None

    is_bevel = BoolProperty(name = "Is Bevel", get = get_is_bevel)
    is_solidify = BoolProperty(name = "Is Solidify", get = get_is_solidify)
    is_for_merge = BoolProperty(name = "Is For Merge", get = get_is_for_merge)
    is_for_softmerge = BoolProperty(name = "Is For Soft Merge", get = get_is_for_softmerge)
    is_pending_boolean = BoolProperty(name = "Is Pending Boolean", get = get_is_pending_boolean)
