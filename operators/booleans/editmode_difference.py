import bpy
import bmesh
from ... preferences import get_preferences
from ...ui_framework.operator_ui import Master


def edit_bool_difference(context, keep_cutters):
    def select(geom):
        for g in geom:
            g.select = True

    def deselect(geom):
        for g in geom:
            g.select = False

    def reveal(geom):
        for g in geom:
            g.hide = False

    def hide(geom):
        for g in geom:
            g.hide = True

    if keep_cutters:
        mesh = context.active_object.data
        bm = bmesh.from_edit_mesh(mesh)
        geometry = bm.verts[:] + bm.edges[:] + bm.faces[:]
        cutter = [g for g in geometry if g.select]
        duplicate = bmesh.ops.duplicate(bm, geom=cutter)["geom"]
        hide(duplicate)
        bmesh.update_edit_mesh(mesh)

    bpy.ops.mesh.intersect_boolean(operation='DIFFERENCE')

    if keep_cutters:
        geometry = bm.verts[:] + bm.edges[:] + bm.faces[:]
        deselect(geometry)
        reveal(duplicate)
        select(duplicate)
        bmesh.update_edit_mesh(mesh)

    return {'FINISHED'}


class HOPS_OT_EditBoolDifference(bpy.types.Operator):
    bl_idname = "hops.edit_bool_difference"
    bl_label = "Hops Difference Boolean Edit Mode"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """Difference Boolean in Edit Mode
LMB - Remove cutters after use (DEFAULT)
LMB + Ctrl - Keep cutters after use"""

    keep_cutters: bpy.props.BoolProperty(
        name="Keep Cutters",
        description="Keep cutters after use",
        default=False)


    called_ui = False

    def __init__(self):

        HOPS_OT_EditBoolDifference.called_ui = False


    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.mode == 'EDIT' and obj.type == 'MESH'

    def draw(self, context):
        self.layout.prop(self, "keep_cutters")

    def execute(self, context):

        # Operator UI
        if not HOPS_OT_EditBoolDifference.called_ui:
            HOPS_OT_EditBoolDifference.called_ui = True

            ui = Master()

            draw_data = [
                ["Difference Boolean"]]

            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return edit_bool_difference(context, self.keep_cutters)
