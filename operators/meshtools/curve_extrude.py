import bpy
import gpu
import math
import bmesh
from math import radians
from bmesh.types import BMFace
from mathutils import Vector, Matrix, Euler
from bpy.props import IntProperty, FloatProperty, BoolProperty
from ... preferences import get_preferences
from ...ui_framework.operator_ui import Master
from ...utils.bmesh import get_edges_center, is_an_edge_selected
from ...utils.curve import copy_curve, convert_curve_to_mesh
from ...utility.object import apply_transform_bpy_version

class HOPS_OT_Curve_Extrude(bpy.types.Operator):
    bl_idname = "hops.curve_extrude"
    bl_label = "Curve Extrude"
    bl_description = "Extrude face along a curve"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}

    adaptive_segments: IntProperty(name="Adaptive Segments", default=15, min=2, max=100)
    stop_location: IntProperty(name="Stop Location", default=100, min=0, max=100)
    smooth_repeat: IntProperty(name="Smooth Repeat", default=0, min=0, max=50)
    smoothing_factor: FloatProperty(name="Smooth Factor", default=.5, min=0, max=1)
    apply_object_transform: BoolProperty(name="Apply Object Transform", default=False)

    called_ui = False

    def __init__(self):

        HOPS_OT_Curve_Extrude.called_ui = False

    @classmethod
    def poll(cls, context):

        mesh, curve, junk_obj = False, False, False
        mesh_obj = None
        for obj in context.selected_editable_objects:
            if obj.type == "MESH":
                mesh_obj = obj
                mesh = True
            elif obj.type == "CURVE":
                curve = True
            else:
                junk_obj = True
        if mesh and curve and not junk_obj:
            return True
        return False


    def execute(self, context):

        start_state = context.active_object.mode
        if start_state == 'OBJECT':
            bpy.ops.object.mode_set(mode='EDIT')

        cancel_due_to_bad_selection = False
        if is_an_edge_selected(context, context.active_object) == False:
            cancel_due_to_bad_selection = True

        if start_state == 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Operator UI
        if not HOPS_OT_Curve_Extrude.called_ui:
            
            HOPS_OT_Curve_Extrude.called_ui = True

            ui = Master()
            draw_data= []
            if not cancel_due_to_bad_selection:
                draw_data = [
                    ["Curve Extrude"],
                    ["Smooth Factor", self.smoothing_factor],
                    ["Smooth Repeat", self.smooth_repeat],
                    ["Stop Location", self.stop_location],
                    ["Adaptive Segments", self.adaptive_segments]]
            else:
                draw_data = [
                    ["Curve Extrude"],
                    ["Select a Face(s) or Edge(s)", "ERROR"]]

            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        if cancel_due_to_bad_selection:
            return {'CANCELLED'}

        # Get Mesh and Curve
        self.mesh, self.curve = None, None
        self.mesh_obj = None
        for obj in context.editable_objects:
            if obj.type == "MESH":
                if context.active_object.name == obj.name:
                    self.mesh = obj
                    self.mesh_obj = obj
            if obj.type == "CURVE":
                self.curve = obj
        if self.mesh == None or self.curve == None:
            return {'CANCELLED'}

        if self.apply_object_transform:
            apply_transform_bpy_version()

        self.extrude_along_curve(context=context)

        # Set the mesh and curve selection back
        self.curve.select_set(True)
        self.mesh.select_set(True)

        return {"FINISHED"}


    def extrude_along_curve(self, context):

        # Copy original curve
        original_segments = self.curve.data.resolution_u
        mesh_curve = copy_curve(context, self.curve)

        # Set curve segs
        mesh_curve.data.resolution_u = self.adaptive_segments

        # Convert curve to mesh
        m_curve = convert_curve_to_mesh(context, mesh_curve, self.smooth_repeat, self.smoothing_factor)
        self.curve.data.resolution_u = original_segments

        # Get the points along the mesh curve
        points = get_points_from_mesh_curve(context, self.curve, m_curve, context.object)
        
        # Extrude
        extrude(context, points, self.stop_location, self.adaptive_segments)

        # Remove the mesh curve
        bpy.data.objects.remove(mesh_curve, do_unlink=True)


def extrude(context, points, stop_location, adaptive_segments):

    obj = context.object
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)
    stop_location = int(len(points) * (stop_location * .01))
    index = 0

    for point in points:
        if stop_location == index:
            break

        # Extrude edges
        if bm.faces.active == None:
            edge_extrude(bm, point, points, obj, index)

        # Extrude faces
        else:
            face_extrude(bm, point, points, obj, index)
            
        index += 1

    bmesh.update_edit_mesh(mesh)


def face_extrude(bm, point, points, obj, index):

    bm.normal_update()
    active_face = bm.faces.active
    face_normal = active_face.normal
    face_normal = obj.matrix_world @ face_normal

    face_center_loc = get_edges_center(bm)
    face_center_loc = obj.matrix_world @ face_center_loc

    face_to_point_vec = point - face_center_loc

    if index == 0:
        if int(face_to_point_vec.magnitude) ==  0:
            return
        if face_center_loc == point:
            return

    # Extrude faces
    faces = [f for f in bm.faces if f.select]
    ret_geom = bmesh.ops.extrude_face_region(bm, geom=faces)

    for face in faces:
        face.select = False

    for face in ret_geom["geom"]:
        if isinstance(face, bmesh.types.BMFace):
            face.select = True
    
    # Flip extruded geo
    bmesh.ops.reverse_faces(bm, faces=faces)

    # Offset vector
    offset_vec = point - face_to_point_vec

    # Translate
    verts = [v for v in ret_geom["geom"] if isinstance(v, bmesh.types.BMVert)]
    ret_geom = bmesh.ops.translate(bm, vec=face_to_point_vec, space=obj.matrix_world, verts=verts)

    # Rotate
    if index + 1 < len(points):
        rot = face_normal.rotation_difference(points[index + 1] - point).to_matrix()
        bmesh.ops.rotate(bm, cent=point, matrix=rot, verts=verts, space=obj.matrix_world)

    # Delete
    bmesh.ops.delete(bm, geom=faces, context='FACES_KEEP_BOUNDARY')


def edge_extrude(bm, point, points, obj, index):

    edge_center_loc = get_edges_center(bm)
    edge_center_loc = obj.matrix_world @ edge_center_loc

    bm.normal_update()
    edge_center_to_point = point - edge_center_loc

    if index == 0:
        if int(edge_center_to_point.magnitude) == 0:
            return
        if edge_center_loc == point:
            return

    # Extrude edges
    edges = [e for e in bm.edges if e.select]
    ret_geom = bmesh.ops.extrude_edge_only(bm, edges=edges, use_normal_flip=True)

    # Recalc the extruded normals
    faces = []
    for face in ret_geom["geom"]:
        if isinstance(face, bmesh.types.BMFace):
            faces.append(face)

    bmesh.ops.recalc_face_normals(bm, faces=faces)

    for edge in edges:
        edge.select = False

    for edge in ret_geom["geom"]:
        if isinstance(edge, bmesh.types.BMEdge):
            edge.select = True
    
    # Offset vector
    offset_vec = point - edge_center_to_point

    # Translate
    verts = [v for v in ret_geom["geom"] if isinstance(v, bmesh.types.BMVert)]
    ret_geom = bmesh.ops.translate(bm, vec=edge_center_to_point, space=obj.matrix_world, verts=verts)

    # Rotate
    if index + 1 < len(points):
        rot = edge_center_to_point.rotation_difference(points[index + 1] - point).to_matrix()
        bmesh.ops.rotate(bm, cent=point, matrix=rot, verts=verts, space=obj.matrix_world)


def get_points_from_mesh_curve(context, original_curve, mesh_curve, obj):
    '''Get the points from the curve mesh, this also makes sure to send back the correct order.'''

    # Get the face center location
    bm = bmesh.from_edit_mesh(obj.data)
    face = bm.faces.active

    face_center_loc = Vector((0,0,0))

    # If there is no active face
    if face == None:
        face_center_loc = get_edges_center(bm)
        face_center_loc = obj.matrix_world @ face_center_loc
    
    else:
        face_center_loc = face.calc_center_median()
        face_center_loc = obj.matrix_world @ face_center_loc
    
    points = []
    verts = mesh_curve.data.vertices

    # Generate the points with the tail end closer to the face center
    first_coord = original_curve.matrix_world @ verts[0].co
    last_coord = original_curve.matrix_world @ verts[-1].co
    reverse = False if (first_coord - face_center_loc).magnitude < (last_coord - face_center_loc).magnitude else True

    if reverse:
        for vert in reversed(verts):
            points.append(original_curve.matrix_world @ vert.co)
    else:
        for vert in verts:
            points.append(original_curve.matrix_world @ vert.co)

    return points

