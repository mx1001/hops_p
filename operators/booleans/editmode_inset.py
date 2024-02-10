import bpy
import bmesh
from ... preferences import get_preferences
from ...ui_framework.operator_ui import Master


def edit_bool_inset(context, keep_cutters, outset, thickness):
    def select( geom):
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

    target = [g for g in visible if not g.select]
    cutter = [g for g in visible if g.select]

    if keep_cutters:
        duplicate = bmesh.ops.duplicate(bm, geom=cutter)["geom"]
        hide(duplicate)

    inset = bmesh.ops.duplicate(bm, geom=target)["geom"]
    faces = [g for g in inset if type(g) == bmesh.types.BMFace]

    if outset:
        bmesh.ops.reverse_faces(bm, faces=faces)

    bmesh.ops.solidify(bm, geom=inset, thickness=float(thickness))
    bmesh.ops.inset_region(bm, faces=faces, thickness=0.00, depth=0.01, use_even_offset=True)

    hide(target)
    bmesh.update_edit_mesh(mesh)
    bpy.ops.mesh.intersect_boolean(operation='INTERSECT')

    geometry = bm.verts[:] + bm.edges[:] + bm.faces[:]
    result = [g for g in geometry if not g.hide]

    reveal(target)
    select(result)
    bpy.ops.mesh.intersect_boolean(operation='UNION' if outset else 'DIFFERENCE')

    if keep_cutters:
        geometry = bm.verts[:] + bm.edges[:] + bm.faces[:]
        deselect(geometry)
        reveal(duplicate)
        select(duplicate)

    bmesh.update_edit_mesh(mesh)
    return {'FINISHED'}


class HOPS_OT_EditBoolInset(bpy.types.Operator):
    bl_idname = "hops.edit_bool_inset"
    bl_label = "Hops Inset Boolean Edit Mode"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """Inset Boolean in Edit Mode
LMB - Inset and remove cutters after use (DEFAULT)
LMB + Ctrl - Keep cutters after use
LMB + Shift - Outset"""

    keep_cutters: bpy.props.BoolProperty(
        name="Keep Cutters",
        description="Keep cutters after use",
        default=False)

    outset: bpy.props.BoolProperty(
        name="Outset",
        description="Use union instead of difference",
        default=False)

    thickness: bpy.props.FloatProperty(
        name="Thickness",
        description="How deep the inset should cut",
        default=0.10,
        min=0.00,
        soft_max=10.0,
        step=1,
        precision=3,)

    called_ui = False

    def __init__(self):

        HOPS_OT_EditBoolInset.called_ui = False

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.mode == 'EDIT' and obj.type == 'MESH'

    def draw(self, context):
        row = self.layout.row()
        row.prop(self, "keep_cutters")
        row.prop(self, "outset")
        self.layout.prop(self, "thickness")

    def invoke(self, context, event):
        self.keep_cutters = event.ctrl
        self.outset = event.shift
        return self.execute(context)

    def execute(self, context):

        # Operator UI
        if not HOPS_OT_EditBoolInset.called_ui:
            HOPS_OT_EditBoolInset.called_ui = True

            ui = Master()

            draw_data = [
                ["Inset Boolean"]]

            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return edit_bool_inset(context, self.keep_cutters, self.outset, self.thickness)
