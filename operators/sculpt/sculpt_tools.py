import bpy

from bpy.props import FloatProperty


class HOPS_OT_SculptDecimate(bpy.types.Operator):
    bl_idname = "sculpt.decimate_mesh"
    bl_label = "Decimate Sculpt"
    bl_description = """Mesh Decimate
    
    Decimates mesh for continued sculpting
    Default (.25) Shift (.5) Ctrl (.75)
    Alt (.10)
    
    """
    bl_options = {"REGISTER", "UNDO"}

    ratio: FloatProperty(name="Ratio", description="Amount Of Decimation", default=0.25, min=0.01, max=1.0)

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    # def draw(self, context):
    #     layout = self.layout
    #     layout.prop(self, "ratio")

    def invoke(self, context, event):
        if event.shift:
            self.ratio = 0.50
            bpy.ops.hops.display_notification(info=F'Decimation Ratio : {self.ratio}', name="")
        elif event.ctrl:
            self.ratio = 0.75
            bpy.ops.hops.display_notification(info=F'Decimation Ratio : {self.ratio}', name="")
        elif event.alt:
            self.ratio = 0.10
            bpy.ops.hops.display_notification(info=F'Decimation Ratio : {self.ratio}', name="")
        else:
            self.ratio = 0.25
            bpy.ops.hops.display_notification(info=F'Decimation Ratio : {self.ratio}', name="")
        
        if bpy.context.active_object.mode == 'SCULPT':
            exit_sculpt()
        self.report({'INFO'}, F'Decimation Ratio : {self.ratio}')
        add_decimate(self.ratio)
        bpy.ops.object.mode_set(mode='SCULPT')
        return {"FINISHED"}


def exit_sculpt():
    bpy.ops.sculpt.sculptmode_toggle()


def add_decimate(ratio):
    bpy.ops.object.modifier_add(type='DECIMATE')
    bpy.context.object.modifiers["Decimate"].ratio = ratio
    bpy.context.object.modifiers["Decimate"].use_symmetry = True
    bpy.ops.object.modifier_apply(modifier="Decimate") # apply_as='DATA',
