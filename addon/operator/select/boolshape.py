import bpy
from bpy.props import EnumProperty, StringProperty


class HOPS_OT_SELECT_boolshape(bpy.types.Operator):
    bl_idname = "hops.select_boolshape"
    bl_label = "select boolshape"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """Select boolshape"""

    obj_name: StringProperty(name="name", default='None')

    def execute(self, context):

        bpy.context.view_layer.layer_collection.children['Cutters'].hide_viewport = False

        active = context.active_object
        if active:
            active.select_set(False)

        ob = bpy.data.objects[self.obj_name]
        ob.hide_set(False)
        ob.select_set(True)

        return {"FINISHED"}
