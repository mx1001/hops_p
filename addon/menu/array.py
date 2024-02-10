import bpy
from ... icons import get_icon_id

#Insert Object
class HOPS_MT_Tool_array(bpy.types.Menu):
    bl_idname = "HOPS_MT_Tool_array"
    bl_label = "Array Axis"

    def draw(self, context):
        layout = self.layout

        layout.operator_context = "INVOKE_DEFAULT"
        array1 = layout.operator("hops.add_mod_circle_array", text="Circular Array    Move: X     Face: Z", icon_value=get_icon_id('ArrayCircle'))
        array1.axis = 'X'
        array1.swap = True
        array2 = layout.operator("hops.add_mod_circle_array", text="Circular Array    Move: X     Face: Y", icon_value=get_icon_id('ArrayCircle'))
        array2.axis = 'X'
        array2.swap = False
        array3 = layout.operator("hops.add_mod_circle_array", text="Circular Array    Move: Y     Face: Z", icon_value=get_icon_id('ArrayCircle'))
        array3.axis = 'Y'
        array3.swap = True
        array4 = layout.operator("hops.add_mod_circle_array", text="Circular Array    Move: Y     Face: X", icon_value=get_icon_id('ArrayCircle'))
        array4.axis = 'Y'
        array4.swap = False
        array5 = layout.operator("hops.add_mod_circle_array", text="Circular Array    Move: Z     Face: X", icon_value=get_icon_id('ArrayCircle'))
        array5.axis = 'Z'
        array5.swap = True
        array6 = layout.operator("hops.add_mod_circle_array", text="Circular Array    Move: Z     Face: Y", icon_value=get_icon_id('ArrayCircle'))
        array6.axis = 'Z'
        array6.swap = False

