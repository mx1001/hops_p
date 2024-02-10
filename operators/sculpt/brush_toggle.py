import bpy
from bpy.props import FloatProperty


class HOPS_OT_BrushToggle(bpy.types.Operator):
    bl_idname = "sculpt.toggle_brush"
    bl_label = "Sculpt Toggle_Brush"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = """Relative / Brush Toggle
    
    Toggles Brush between relative and brush along with sizes used often
    Relative uses a brush and scene scale
    Brush uses the brush scale for detail scale. *useful for detailing*
    
    """

    amountpercent: FloatProperty(name="Detail Percent", description="Detail Brush", default=25.0, min=0.01, max=100.0)

    amountsize: FloatProperty(name="Detail Size", description="Detail Relative", default=8.0, min=0.50, max=40.0)

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def draw(self, context):
        layout = self.layout
        sculpt_brush_mode = bpy.context.scene.tool_settings.sculpt.detail_type_method
        if sculpt_brush_mode == 'BRUSH':
            layout.prop(self, "amountpercent")
        if sculpt_brush_mode == 'RELATIVE':
            layout.prop(self, "amountsize")
        # else:
        #    layout.text("NO")

    def invoke(self, context, event):
        self.execute(context)
        return {"FINISHED"}

    def execute(self, context):
        sculpt_brush_mode = bpy.context.scene.tool_settings.sculpt.detail_type_method
        if bpy.context.active_object.mode == 'SCULPT':
            type = bpy.context.scene.tool_settings.sculpt.detail_type_method
            toggle_brush(type, self.amountpercent, self.amountsize)
        if sculpt_brush_mode == 'BRUSH':
            #context.area.header_text_set(text='Brush Mode')
            self.report({'INFO'}, F'Brush Mode : {self.amountpercent}')
            bpy.ops.hops.display_notification(info=F'Brush Mode : {self.amountpercent}', name="")
        if sculpt_brush_mode == 'RELATIVE':
            #context.area.header_text_set(text='Relative Mode')
            self.report({'INFO'}, F'Relative Mode : {self.amountsize}')
            bpy.ops.hops.display_notification(info=F'Relative Mode : {self.amountsize}', name="")
        return {"FINISHED"}


def toggle_brush(type, amountpercent, amountsize):
    if type == 'BRUSH':
        bpy.context.scene.tool_settings.sculpt.detail_refine_method = 'SUBDIVIDE'
        bpy.context.scene.tool_settings.sculpt.detail_type_method = 'RELATIVE'
        bpy.context.scene.tool_settings.sculpt.detail_size = amountsize
    if type == 'RELATIVE':
        bpy.context.scene.tool_settings.sculpt.detail_refine_method = 'SUBDIVIDE'
        bpy.context.scene.tool_settings.sculpt.detail_type_method = 'BRUSH'
        bpy.context.scene.tool_settings.sculpt.detail_percent = amountpercent
