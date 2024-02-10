import bpy
import math
import bmesh
import mathutils
from math import radians
from bmesh.types import BMFace
from mathutils import Vector, Matrix, Euler
from bpy.props import IntProperty, FloatProperty, BoolProperty
from ... ui_framework.operator_ui import Master
from ... preferences import get_preferences
from ... utils.bmesh import get_verts_center
from ...utility.object import apply_transforms


class HOPS_OT_Mesh_Align(bpy.types.Operator):
    bl_idname = "hops.mesh_align"
    bl_label = "Align Mesh"
    bl_description = "Align a mesh to an active face"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}
    
    obj_normal_offset: FloatProperty(name="Active normal offset", default=0, min=-20, max=20)
    target_normal_offset: FloatProperty(name="Target normal offset", default=0, min=-20, max=20)
    flip_edge_one: BoolProperty(name="Flip edge one", default=False)
    flip_edge_two: BoolProperty(name="Flip edge two", default=False)
    first_edge_solver: IntProperty(name="First Edge Solver", description="End user additional rotation solver", default=0, min=0, max=360)
    second_edge_solver: IntProperty(name="Second Edge Solver", description="End user additional rotation solver", default=0, min=0, max=360)
    apply_active_transform: BoolProperty(name="Apply Active Obj Transform", default=False)
    apply_target_transform: BoolProperty(name="Apply Target Obj Transform", default=False)
    place_cursor_at_pivot: BoolProperty(name="Place cursor at pivot", default=False)

    called_ui = False

    def __init__(self):

        HOPS_OT_Mesh_Align.called_ui = False

    @classmethod
    def poll(cls, context):

        selected_mesh_count = 0
        for obj in context.selected_editable_objects:
            if obj.type == 'MESH':
                selected_mesh_count += 1
        if selected_mesh_count > 1:
            return True
        return False


    def execute(self, context):

        if context.active_object.mode == 'OBJECT':
            bpy.ops.object.mode_set(mode='EDIT')

        # Get the two mesh objects
        active_object = context.active_object
        target_obj = None

        for obj in context.selected_editable_objects:
            if obj.type == 'MESH':
                if obj.name != active_object.name:
                    target_obj = obj
                    break
        
        if target_obj == None:
            return {"FINISHED"}

        if active_object and target_obj:
            fin = align(
                active_obj=active_object,
                target_obj=target_obj,
                obj_normal_offset=self.obj_normal_offset,
                target_normal_offset=self.target_normal_offset,
                first_edge_solver=self.first_edge_solver,
                second_edge_solver=self.second_edge_solver,
                flip_edge_one=self.flip_edge_one,
                flip_edge_two=self.flip_edge_two,
                apply_active_transform=self.apply_active_transform,
                apply_target_transform=self.apply_target_transform,
                place_cursor_at_pivot=self.place_cursor_at_pivot)

        # Operator UI
        if not HOPS_OT_Mesh_Align.called_ui:
            HOPS_OT_Mesh_Align.called_ui = True
            ui = Master()

            draw_data = [
                ["Mesh Align"],
                ["Active N Offset", self.obj_normal_offset],
                ["Target N Offset", self.target_normal_offset],
                ["Flip edge one", self.flip_edge_one],
                ["Flip edge two", self.flip_edge_two],
                ["First Edge Solver", self.first_edge_solver],
                ["Second Edge Solver", self.second_edge_solver]]

            if fin != None:
                draw_data = [
                    ["Mesh Align"],
                    [fin, "ERROR"]]

            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return {"FINISHED"}


def align(
    active_obj: bpy.types.Object, 
    target_obj: bpy.types.Object, 
    obj_normal_offset, 
    target_normal_offset, 
    first_edge_solver, 
    second_edge_solver, 
    flip_edge_one, 
    flip_edge_two,
    apply_active_transform,
    apply_target_transform,
    place_cursor_at_pivot):

    '''Align the active object using 3 verts to the target object using 3 verts.'''

    if apply_active_transform:
        apply_transforms(active_obj)

    if apply_target_transform:
        apply_transforms(target_obj)

    # Active Object
    a_mesh = active_obj.data
    active_bm = bmesh.from_edit_mesh(a_mesh)
    active_bm.normal_update()

    # Target Object
    t_mesh = target_obj.data
    target_bm = bmesh.from_edit_mesh(t_mesh)
    target_bm.normal_update()

    # Active object first 3 verts
    active_verts = [v for v in active_bm.select_history if isinstance(v, bmesh.types.BMVert)]
    if len(active_verts) < 3:
        return "Select 3 VERTS"
    elif len(active_verts) > 3:
        active_verts = active_verts[ 0:3 ]

    # Target object first 3 verts
    target_verts = [v for v in target_bm.select_history if isinstance(v, bmesh.types.BMVert)]
    if len(target_verts) < 3:
        return "Select 3 VERTS"
    elif len(target_verts) > 3:
        target_verts = target_verts[ 0:3 ]

    verts = [v for v in active_bm.verts]

    #-- Rotate first edge --#
    active_edge = active_verts[1].co - active_verts[0].co
    active_edge.normalize()
    target_edge = target_verts[1].co - target_verts[0].co
    target_edge.normalize()

    angle = target_edge.angle(active_edge)

    if flip_edge_one:
        angle -= math.pi / 2

    angle += math.radians(first_edge_solver)

    axis = active_edge.cross(target_edge)
    rot_mat = Matrix.Rotation(angle, 3, axis)

    bmesh.ops.rotate(
        active_bm,
        cent=target_verts[0].co,
        matrix=rot_mat,
        verts=verts,
        space=active_obj.matrix_world)

    #-- Rotate second edge --#
    a_edge_1 = (active_obj.matrix_world @ active_verts[1].co) - (active_obj.matrix_world @ active_verts[0].co)
    a_edge_2 = (active_obj.matrix_world @ active_verts[2].co) - (active_obj.matrix_world @ active_verts[0].co)
    a_normal = a_edge_1.cross(a_edge_2)
    a_normal.normalize()

    t_edge_1 = (target_obj.matrix_world @ target_verts[1].co) - (target_obj.matrix_world @ target_verts[0].co)
    t_edge_2 = (target_obj.matrix_world @ target_verts[2].co) - (target_obj.matrix_world @ target_verts[0].co)
    t_normal = t_edge_1.cross(t_edge_2)
    t_normal.normalize()

    normal_diff_quat = a_normal.rotation_difference(t_normal)
    angle = t_normal.angle(a_normal)

    if flip_edge_two:
        angle -= math.pi / 2    

    angle += math.radians(second_edge_solver)

    axis = target_verts[1].co - target_verts[0].co
    rot_mat = Matrix.Rotation(angle, 3, axis)

    bmesh.ops.rotate(
        active_bm,
        cent=target_verts[1].co - target_verts[0].co,
        matrix=rot_mat,
        verts=verts,
        space=active_obj.matrix_world)

    #-- Move --#
    active_point_1 = active_obj.matrix_world @ active_verts[0].co
    target_point_1 = target_obj.matrix_world @ target_verts[0].co
    obj_offset_vec = target_point_1 - active_point_1

    for vert in verts:
        vert.co += obj_offset_vec

    #-- Additional Offset Redo Panel --#
    a_edge_1 = (active_obj.matrix_world @ active_verts[1].co) - (active_obj.matrix_world @ active_verts[0].co)
    a_edge_2 = (active_obj.matrix_world @ active_verts[2].co) - (active_obj.matrix_world @ active_verts[0].co)
    a_normal = a_edge_1.cross(a_edge_2)
    a_normal.normalize()
    offset = a_normal * obj_normal_offset
    for vert in verts:
        vert.co += offset

    t_edge_1 = (target_obj.matrix_world @ target_verts[1].co) - (target_obj.matrix_world @ target_verts[0].co)
    t_edge_2 = (target_obj.matrix_world @ target_verts[2].co) - (target_obj.matrix_world @ target_verts[0].co)
    t_normal = t_edge_1.cross(t_edge_2)
    t_normal.normalize()
    offset = t_normal * target_normal_offset
    for vert in verts:
        vert.co += offset

    if place_cursor_at_pivot:
        bpy.context.scene.cursor.location = active_point_1 + obj_offset_vec
        up = Vector((0,0,1))
        angle = up.rotation_difference(t_normal).to_euler()
        bpy.context.scene.cursor.rotation_euler = angle

    # Update
    bmesh.update_edit_mesh(a_mesh)

    return None


def set_rotation_on_object(obj: bpy.types.Object):

    euler = Euler(map(radians, (0, 0, 0)), 'XYZ')
    loc, rot, scale = obj.matrix_world.decompose()
    smat = Matrix()

    for i in range(3):
        smat[i][i] = scale[i]

    mat = Matrix.Translation(loc) @ euler.to_matrix().to_4x4() @ smat
    obj.matrix_world = mat
