import bpy
import gpu
import math
import bmesh
import mathutils
from bmesh.types import BMFace
from mathutils import Vector, Matrix
from bpy.props import IntProperty, FloatProperty, BoolProperty, EnumProperty
from ... preferences import get_preferences
from ...ui_framework.operator_ui import Master
from ...utils.bmesh import get_face_center_location


class HOPS_OT_Flatten_To_Face(bpy.types.Operator):
    bl_idname = "hops.flatten_to_face"
    bl_label = "Flatten to Face"
    bl_description = "Flatten all geo to active face"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}

    normals_method: EnumProperty(
        name="Alignment Method",
        description="Pick a normals alignment method for the projection",
        items=[ ('Active Face', "Active Face", ""),
                ('Individual Face', "Individual Face", ""),])

    called_ui = False

    def __init__(self):

        HOPS_OT_Flatten_To_Face.called_ui = False

    @classmethod
    def poll(cls, context):

        mesh = False
        for obj in context.selected_editable_objects:
            if obj.type == "MESH":
                mesh_obj = obj
                mesh = True
        if mesh:
            return True
        return False


    def execute(self, context):

        start_state = context.active_object.mode

        if start_state == 'OBJECT':
            bpy.ops.object.mode_set(mode='EDIT')

        if start_state == 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')


        exit_message = flatten_faces(context=context, method=self.normals_method)

        # Operator UI
        if not HOPS_OT_Flatten_To_Face.called_ui:

            HOPS_OT_Flatten_To_Face.called_ui = True

            ui = Master()
            draw_data = [
                ["Flatten Faces"],
                ["Normals Method", self.normals_method]]

            if exit_message != None:
                draw_data = [
                    ["Flatten Faces"],
                    [exit_message, "ERROR"]]



            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return {"FINISHED"}


def flatten_faces(context: bpy.context, method: bpy.props.EnumProperty):
    '''Flatten all geometry to the active face.'''

    obj = context.active_object
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)
    bm.normal_update()

    face_center_loc = get_face_center_location(bm, obj=obj)

    if face_center_loc == None:
        return "Select an active face."

    active_face = bm.faces.active
    active_face_normal = active_face.normal

    faces = [f for f in bm.faces if f.select]
    if active_face in faces:
        faces.remove(active_face)
        if len(faces) == 0:
            return "Select more faces."

    index = 0
    for face in faces:
        
        face_normal = Vector((0,0,0))

        if method == "Active Face":
            face_normal = active_face_normal

        elif method == "Individual Face":
            face_normal = face.normal

        for vert in face.verts:

            scale_factor = 100000
            scaler = Vector((face_normal[0] * scale_factor, face_normal[1] * scale_factor, face_normal[2] * scale_factor))

            point_a = vert.co
            point_b = point_a + scaler
            intersection = mathutils.geometry.intersect_line_plane(point_a, point_b, face_center_loc, active_face_normal)

            if intersection != None:
                vert.co = intersection

    bm.normal_update()
    bmesh.update_edit_mesh(mesh)

    return None