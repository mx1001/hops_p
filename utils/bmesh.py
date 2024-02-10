import bpy
import bmesh
from mathutils import Vector, Matrix


def selectSmoothEdges(self, me):

    bm = bmesh.from_edit_mesh(me)
    for e in bm.edges:
        if not e.smooth:
            e.select_set(True)


def get_edges_center(bm):
    '''Get the average center for all the verts in selected edges.'''

    edges = [e for e in bm.edges if e.select]

    verts = []
    for edge in edges:
        for vert in edge.verts:
            verts.append(vert)

    vert_sum = Vector((0,0,0))

    for vert in verts:
        vert_sum += vert.co

    vert_avg = vert_sum / len(verts) if len(verts) > 0 else Vector((0,0,0))

    return vert_avg


def get_verts_center(verts: list):
    '''Return the center point of the verts.'''

    vert_sum = Vector((0,0,0))

    for vert in verts:
        vert_sum += vert.co

    vert_avg = vert_sum / len(verts) if len(verts) > 0 else Vector((0,0,0))

    return vert_avg


def is_an_edge_selected(context, obj):
    '''Check if to make sure an edge is selected.'''

    start_state = context.active_object.mode
    
    if start_state == 'OBJECT':
        return False
        
    obj = context.object
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)

    edge_count = len([e for e in bm.edges if e.select])

    if edge_count > 0:
        return True
    else:
        return False


def get_face_normal_from_vert(bm):
    '''Return the face normal from the active vert.'''

    bm.faces.ensure_lookup_table()

    if bm.faces.active != None:
        return bm.faces.active.normal

    else:
        return Vector((0,0,1))


def get_face_center_location(bm: bmesh, obj: bpy.types.Object):
    ''''Returns the active face normal location as a transform matrix, or none.'''

    active_face = bm.faces.active

    if active_face == None:
        return None

    center = active_face.calc_center_bounds()

    return center
    
