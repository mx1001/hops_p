import bpy
import bmesh
from ... preferences import get_preferences
from ...ui_framework.operator_ui import Master


def edit_bool_slash(context, keep_cutters):
    def duplicate(bm, geom):
        return bmesh.ops.duplicate(bm, geom=geom)["geom"]

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

    mesh = context.active_object.data
    bm = bmesh.from_edit_mesh(mesh)

    geometry = bm.verts[:] + bm.edges[:] + bm.faces[:]
    visible = [g for g in geometry if not g.hide]
    hidden = [g for g in geometry if g.hide]

    target_one = [g for g in visible if not g.select]
    cutter_one = [g for g in visible if g.select]

    target_two = bmesh.ops.duplicate(bm, geom=target_one)["geom"]
    cutter_two = bmesh.ops.duplicate(bm, geom=cutter_one)["geom"]

    if keep_cutters:
        duplicate = bmesh.ops.duplicate(bm, geom=cutter_one)["geom"]
        hide(duplicate)

    hide(target_two + cutter_two)
    bpy.ops.mesh.intersect_boolean(operation='DIFFERENCE')

    geometry = bm.verts[:] + bm.edges[:] + bm.faces[:]
    hide(geometry)

    reveal(target_two + cutter_two)
    select(cutter_two)
    bpy.ops.mesh.intersect_boolean(operation='INTERSECT')

    geometry = bm.verts[:] + bm.edges[:] + bm.faces[:]
    if keep_cutters:
        deselect(geometry)
        reveal(duplicate)
        select(duplicate)
    else:
        visible = [g for g in geometry if not g.hide]
        select(visible)

    reveal(geometry)
    hide(hidden)

    bmesh.update_edit_mesh(mesh)
    return {'FINISHED'}


class HOPS_OT_EditBoolSlash(bpy.types.Operator):
    bl_idname = "hops.edit_bool_slash"
    bl_label = "Hops Slash Boolean Edit Mode"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """Slash Boolean in Edit Mode
LMB - Remove cutters after use (DEFAULT)
LMB + Ctrl - Keep cutters after use"""

    keep_cutters: bpy.props.BoolProperty(
        name="Keep Cutters",
        description="Keep cutters after use",
        default=False)

    called_ui = False

    def __init__(self):

        HOPS_OT_EditBoolSlash.called_ui = False

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.mode == 'EDIT' and obj.type == 'MESH'

    def draw(self, context):
        self.layout.prop(self, "keep_cutters")

    def invoke(self, context, event):
        self.keep_cutters = event.ctrl
        return self.execute(context)

    def execute(self, context):

        # Operator UI
        if not HOPS_OT_EditBoolSlash.called_ui:
            HOPS_OT_EditBoolSlash.called_ui = True

            ui = Master()

            draw_data = [
                ["Slash Boolean"]]

            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return edit_bool_slash(context, self.keep_cutters)
