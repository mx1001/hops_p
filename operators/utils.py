import bpy
import bmesh
from .. utils.context import ExecutionContext
from .. utils.objects import get_modifier_with_type

def update_bevel_modifier_if_necessary(object, segment_amount, bevelwidth, profile_value):
    bevel = get_modifier_with_type(object, "BEVEL")
    if bevel is None:
        bevel = object.modifiers.new("Bevel", "BEVEL")
        bevel.use_clamp_overlap = False
        bevel.show_in_editmode = False
        bevel.width = bevelwidth
        bevel.profile = profile_value
        bevel.limit_method = 'WEIGHT'
        bevel.show_in_editmode = True
        bevel.segments = segment_amount

def clear_ssharps(object):
    with ExecutionContext(mode = "EDIT", active_object = object):
        bpy.ops.mesh.select_mode(type = "EDGE", action = "ENABLE")
        bpy.ops.mesh.select_all(action = "SELECT")
        bpy.ops.transform.edge_bevelweight(value = -1)
        bpy.ops.mesh.mark_sharp(clear = True)
        bpy.ops.transform.edge_crease(value = -1)

def convert_to_sharps(object):
    with ExecutionContext(mode = "EDIT", active_object = object):
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_mode(type = "EDGE", action = "ENABLE")
        bpy.ops.mesh.select_all(action = "SELECT")
        bpy.ops.transform.edge_bevelweight(value = -1)
        bpy.ops.transform.edge_crease(value = -1)
        bpy.ops.mesh.mark_sharp(clear = False)

def mark_ssharps(object, sharpness, sub_d_sharpening):
    with ExecutionContext(mode = "EDIT", active_object = object):
        bpy.context.scene.tool_settings.use_mesh_automerge = False
        only_select_sharp_edges(sharpness)

        obj = bpy.context.object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        cr = bm.edges.layers.bevel_weight.verify()

        for e in bm.edges:
            if (e[cr] > 0):
                e.select = False

        bmesh.update_edit_mesh(me, False, False)
        bpy.ops.transform.edge_bevelweight(value = 1)
        only_select_sharp_edges(sharpness)

        if sub_d_sharpening:
            bpy.ops.transform.edge_crease(value = -1)
            bpy.ops.mesh.mark_sharp(clear = True)

        else:
            bpy.ops.transform.edge_crease(value = 1)
            bpy.ops.mesh.mark_sharp(clear = False, use_verts=False)
            #bpy.ops.mesh.mark_sharp()


def set_smoothing(object, auto_smooth_angle, sub_d_sharpening):
    with ExecutionContext(mode = "OBJECT", active_object = object):
        object.data.use_auto_smooth = not sub_d_sharpening
        object.data.auto_smooth_angle = auto_smooth_angle
        bpy.ops.object.shade_smooth()


def only_select_sharp_edges(sharpness):
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.mesh.edges_select_sharp(sharpness = sharpness)

