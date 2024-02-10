import bpy
import math
import bmesh
import mathutils
from math import radians
from bmesh.types import BMFace
from mathutils import Vector, Matrix, Euler
from bpy.props import IntProperty, FloatProperty, BoolProperty
from ... preferences import get_preferences
from ... ui_framework.operator_ui import Master
from ... utils.bmesh import get_verts_center
from ...utility.object import apply_transforms


class HOPS_OT_Selection_To_Boolean(bpy.types.Operator):
    bl_idname = "hops.selection_to_boolean"
    bl_label = "Selection To Boolean"
    bl_description = "Take a selection and convert it to boolean."
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}
    extrude_depth: FloatProperty(name="Extrude Depth", default=.1)
    face_offset: FloatProperty(name="Face Offset", default=-.01)
    inset_depth: FloatProperty(name="Inset Depth", default=.02)
    called_ui = False

    def __init__(self):

        HOPS_OT_Selection_To_Boolean.called_ui = False

    @classmethod
    def poll(cls, context):

        if context.active_object.type == "MESH":
            if context.active_object.mode == 'EDIT':
                return True
        
        return False


    def execute(self, context):

        exit_code = self.create_boolean_from_selection(context)

        # Operator UI
        if not HOPS_OT_Selection_To_Boolean.called_ui:
            HOPS_OT_Selection_To_Boolean.called_ui = True
            ui = Master()

            draw_data = []

            if exit_code == None:
                draw_data = [
                    ["Selection to Boolean"],
                    ["Extrude Depth", self.extrude_depth],
                    ["Face Offset", self.face_offset],
                    ["Inset Depth", self.inset_depth]]

            if exit_code != None:
                draw_data = [
                    ["Selection to Boolean"],
                    [exit_code, "ERROR"]]

            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return {"FINISHED"}


    def create_boolean_from_selection(self, context: bpy.context):
        '''Create a boolean from selection set.'''

        obj = context.active_object
        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)

        # Extrude faces
        faces = [f for f in bm.faces if f.select]
        if len(faces) != 0:
            get_extruded_faces(context, mesh, bm, faces, self.extrude_depth, self.face_offset, self.inset_depth)
            return None

        # Create a new face
        else:
            return "Select Face(s)"

            # proceed = setup_face_from_verts(bm)
            # if proceed != None:
            #     pass
            #     #get_extruded_faces(context, mesh, bm, faces)
        


def get_extruded_faces(context: bpy.context, mesh: bpy.types.Mesh, bm: bmesh, faces: list, extrude_depth, face_offset, inset_depth):
    '''Extrude the faces or single face.'''

    original_obj = context.active_object

    # Deselect all the verts
    for face in bm.faces:
        face.select = False

    # Extrude the faces
    if len(faces) != 0:

        ret_geo = bmesh.ops.duplicate(bm, geom=faces)
        dup_faces = [f for f in ret_geo["geom"] if isinstance(f, bmesh.types.BMFace)]

        for face in dup_faces:
            face.select = True
        bpy.ops.transform.shrink_fatten(value=face_offset, use_even_offset=True)

        solidify_geo = bmesh.ops.solidify(bm, geom=dup_faces, thickness=extrude_depth)
        solidify_faces = [f for f in solidify_geo["geom"] if isinstance(f, bmesh.types.BMFace)]

        # # Select duplicate geo
        # for face in dup_faces:
        #     face.select = True

        # # Select solidify geo
        # for face in solidify_faces:
        #     face.select = True

        # Select extruded ring
        for face in dup_faces:
            face.select = True
            for edge in face.edges:
                linked = edge.link_faces
                for face in linked:
                    face.select = True

        selected_faces = [f for f in bm.faces if f.select]
        for face in selected_faces:
            if face in solidify_faces:
                face.select = False
            if face in dup_faces:
                face.select = False

        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bpy.ops.transform.shrink_fatten(value=inset_depth, use_even_offset=True)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

        # Select duplicate geo
        for face in dup_faces:
            face.select = True

        # Select solidify geo
        for face in solidify_faces:
            face.select = True

        # Select extruded ring
        for face in dup_faces:
            face.select = True
            for edge in face.edges:
                linked = edge.link_faces
                for face in linked:
                    face.select = True


        # Create a new object from the extruded geo
        new_obj = create_new_obj(context, bm.copy())

        # remove_faces = [f for f in bm.faces if f.select]
        # for face in remove_faces:
        #     bm.faces.remove(face)

        # remove_edges = [e for e in bm.edges if e.select]
        # for edge in remove_edges:
        #     bm.edges.remove(edge)

        remove_verts = [v for v in bm.verts if v.select]
        for vert in remove_verts:
            bm.verts.remove(vert)

        bmesh.update_edit_mesh(mesh)
        bm.free()

        # Assign boolean mod to original object
        mod = original_obj.modifiers.new("HOPS Boolean", 'BOOLEAN')
        mod.object = new_obj
        mod.show_render = False

        # Go into edit mode on the new object
        new_obj.select_set(True)
        new_obj.parent = original_obj
        new_obj.matrix_world = original_obj.matrix_world
        new_obj.display_type = 'WIRE'
        context.view_layer.objects.active = new_obj


        # Update data to prevent crash
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')


def setup_face_from_verts(bm: bmesh, verts: list):
    '''Create a new face in bmesh and select it.'''

    verts = [v for v in bm.verts if v.select]

    if len(verts) < 3:
        return None


def create_new_obj(context: bpy.context, bm: bmesh):
    '''Create the new mesh.'''

    mesh = bpy.data.meshes.new("HOPS_Boolean")
    obj = bpy.data.objects.new(mesh.name, mesh)
    obj.hops.status = "BOOLSHAPE"

    col = None
    if "Cutters" in bpy.data.collections:
        col = bpy.data.collections.get("Cutters")

    else:
        col = bpy.data.collections.new("Cutters")
        context.scene.collection.children.link(col)

    col.objects.link(obj)
    bpy.context.view_layer.objects.active = obj

    # remove_faces = [f for f in bm.faces if not f.select]
    # for face in remove_faces:
    #     bm.faces.remove(face)

    # remove_edges = [e for e in bm.edges if not e.select]
    # for edge in remove_edges:
        # bm.edges.remove(edge)

    remove_verts = [v for v in bm.verts if not v.select]
    for vert in remove_verts:
        bm.verts.remove(vert)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    bm.to_mesh(mesh)
    bm.free()

    return obj


# def get_linked_faces(f):
    
#     if f.tag:
#         # If the face is already tagged, return empty list
#         return []
    
#     # Add the face to list that will be returned
#     f_linked = [f]
#     f.tag = True
    
#     # Select edges that link two faces
#     edges = [e for e in f.edges if len(e.link_faces) == 2]
#     for e in edges:
#         # Select all firs-degree linked faces, that are not yet tagged
#         faces = [elem for elem in e.link_faces if not elem.tag]
        
#         # Recursively call this function on all connected faces
#         if not len(faces) == 0:
#             for elem in faces:
#                 # Extend the list with second-degree connected faces
#                 f_linked.extend(get_linked_faces(elem))

#     return f_linked