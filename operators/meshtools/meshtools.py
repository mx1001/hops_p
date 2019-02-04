import bpy
from bgl import *
from bpy.props import *
from math import radians, degrees
from ... overlay_drawer import show_text_overlay
from ... utils.addons import addon_exists
from ... utils.context import ExecutionContext
from ... preferences import tool_overlays_enabled, Hops_display_time, Hops_fadeout_time
from ... utils.operations import invoke_individual_resizing
from ... overlay_drawer import show_custom_overlay, disable_active_overlays

class vertcircleOperator(bpy.types.Operator):
    bl_idname = "view3d.vertcircle"
    bl_label = "Vert To Circle"
    bl_description = "Converts Vertices To Circle"
    bl_options = {"REGISTER","UNDO"}

    divisions = IntProperty(name="Division Count", description="Amount Of Vert divisions", default=5, min = 3, max = 10)

    message = "< Default >"

    nth_mode = BoolProperty(default = False)

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "divisions")

    def invoke(self, context, event):
        self.execute(context)

        if tool_overlays_enabled():
            disable_active_overlays()
            if addon_exists("mesh_looptools"):
                message = "< Adjust Scale >"
                show_text_overlay(text = message, font_size = 13, color = (1, 1, 1),
                    stay_time = Hops_display_time(), fadeout_time = Hops_fadeout_time())
            else:
                message = "< Install LoopTools >"
                show_text_overlay(text = message, font_size = 60, color = (1, 0, 0),
                    stay_time = Hops_display_time(), fadeout_time = Hops_fadeout_time())
        return {"FINISHED"}

    def execute(self, context):
        if addon_exists("mesh_looptools"):
            setup_verts(context.active_object, self.divisions, self.nth_mode)
            invoke_individual_resizing()

        return {"FINISHED"}

def setup_verts(object, divisions, nth_mode):
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
    if nth_mode:
        bpy.ops.mesh.select_nth()
    bpy.ops.mesh.bevel(offset=0.2, segments=divisions, vertex_only=True)
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
    bpy.ops.mesh.dissolve_mode()
    bpy.ops.mesh.looptools_circle()
