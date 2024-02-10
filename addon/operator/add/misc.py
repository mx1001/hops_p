import bpy
import math
import bmesh
from .... preferences import get_preferences
from ... property.preference import property


class HOPS_OT_ADD_vertex(bpy.types.Operator):
    bl_idname = "hops.add_vertex"
    bl_label = "Add smart vertex"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """Create vertex"""

    def execute(self, context):
        verts = [(0, 0, 0)]
        obj = bpy.data.objects.new("Cube", bpy.data.meshes.new("Cube"))

        bpy.ops.object.select_all(action='DESELECT')
        context.collection.objects.link(obj)
        context.view_layer.objects.active = obj
        obj.select_set(True)

        bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)

        if get_preferences().behavior.cursor_boolshapes:
            obj.rotation_euler = bpy.context.scene.cursor.rotation_euler

        bm = bmesh.new()
        for v in verts:
            bm.verts.new(v)
        bm.to_mesh(context.object.data)
        bm.free()

        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = math.radians(60)

        return {"FINISHED"}
