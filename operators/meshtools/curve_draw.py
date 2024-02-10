import bpy
import gpu
import math
import bmesh
import mathutils
from bgl import *
from mathutils import Vector
from math import cos, sin, pi, radians, degrees
from gpu_extras.batch import batch_for_shader
from bpy.props import IntProperty, FloatProperty, BoolProperty, StringProperty
from mathutils import Matrix, Vector, geometry, Quaternion
from ... graphics.drawing2d import draw_text
from ... addon.utility import method_handler
from ... preferences import get_preferences
from ... ui_framework.master import Master
from ... utils.space_3d import get_3D_point_from_mouse, get_3D_raycast_from_mouse
from ... utils.bmesh import get_edges_center, is_an_edge_selected, get_face_normal_from_vert
from ... utils.curve import copy_curve, convert_curve_to_mesh, add_curve_to_scene, add_bezier_point


class HOPS_OT_Curve_Draw(bpy.types.Operator):

    """Curve Draw - ST3"""
    bl_idname = "hops.curve_draw"
    bl_label = "Draw a curve"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = """Draw a curve."""

    adaptive_segments: IntProperty(name="Adaptive Segments", default=15, min=2, max=100)
    stop_location: IntProperty(name="Stop Location", default=100, min=0, max=100)
    smooth_repeat: IntProperty(name="Smooth Repeat", default=0, min=0, max=50)
    smoothing_factor: FloatProperty(name="Smooth Factor", default=.5, min=0, max=1)


    # @classmethod
    # def poll(cls, context):
    #     mesh, junk_obj = False, False
    #     mesh_obj = None
    #     for obj in context.selected_editable_objects:
    #         if obj.type == "MESH":
    #             mesh_obj = obj
    #             mesh = True
    #         else:
    #             junk_obj = True
    #     if mesh and not junk_obj:
    #         return True
    #     return False


    def invoke(self, context, event):

        start_state = context.active_object.mode
        if start_state == 'OBJECT':
            bpy.ops.object.mode_set(mode='EDIT')

        # cancel_due_to_bad_selection = False
        # if is_an_edge_selected(context, context.active_object) == False:
        #     cancel_due_to_bad_selection = True

        # if cancel_due_to_bad_selection:
        #     if start_state == 'OBJECT':
        #         bpy.ops.object.mode_set(mode='OBJECT')
        #     return {'CANCELLED'}

        # Props
        self.obj = context.active_object
        self.intersection = Vector((0,0,0))
        self.point = Vector((0,0,0))
        self.normal = Vector((0,0,0))

        mesh = self.obj.data
        bm = bmesh.from_edit_mesh(mesh)
        loc = get_face_normal_from_vert(bm=bm)

        self.curve = add_curve_to_scene(context, location=loc, select=False)

        self.master = Master(context=context, show_fast_ui=False)
        self.intersection_draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_intersection, (context,), 'WINDOW', 'POST_VIEW')
        self.curve_draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_curve, (context,), 'WINDOW', 'POST_VIEW')
        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    def execute(self, context):

        print("TOP")
        print(context.selected_editable_objects)

        start_state = context.active_object.mode
        if start_state == 'OBJECT':
            bpy.ops.object.mode_set(mode='EDIT')

        cancel_due_to_bad_selection = False
        if is_an_edge_selected(context, context.active_object) == False:
            cancel_due_to_bad_selection = True

        if start_state == 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        if cancel_due_to_bad_selection:
            return {'CANCELLED'}

        # Get Mesh and Curve
        self.mesh, self.curve = None, None
        for obj in context.selected_editable_objects:
            if obj.type == "MESH":
                if context.active_object.name == obj.name:
                    self.mesh = obj
            if obj.type == "CURVE":
                self.curve = obj
        if self.mesh == None or self.curve == None:
            return {'CANCELLED'}

        #self.extrude_along_curve(context=context)

        bpy.ops.object.mode_set(mode='OBJECT')

        print("BOTTOM")

        return {"FINISHED"}


    def modal(self, context, event):

        # Fade effect
        self.master.receive_event(event=event)

        #Navigation
        if (event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} and event.ctrl != True):

            if not self.master.is_mouse_over_ui():
                return {'PASS_THROUGH'}

        #Confirm
        elif (event.type in {'SPACE', 'NUMPAD_ENTER', 'RET'}):

            if not self.master.is_mouse_over_ui():
                self.remove_intersection()
                self.remove_curve()
                self.master.run_fade()

                self.curve.select_set(True)
                self.obj.select_set(True)
                #bpy.ops.hops.curve_extrude('EXEC_DEFAULT')
                self.execute(context)
                return {'FINISHED'}

        #Cancel
        elif (event.type in {'RIGHTMOUSE', 'ESC'}):

            if not self.master.is_mouse_over_ui():
                self.remove_intersection()
                self.remove_curve()

                try:
                    self.cancel(context)
                except:
                    print("Error: Could not revert.")

                self.master.run_fade()
                return {'CANCELLED'}

        # Raycasting
        #elif event.type == 'MOUSEMOVE':
        if not self.master.is_mouse_over_ui():

            # Mouse Pos
            mouse_x = event.mouse_region_x
            mouse_y = event.mouse_region_y
            mouse_pos = (mouse_x, mouse_y)

            # Plane Point
            self.obj = context.object
            mesh = self.obj.data
            bm = bmesh.from_edit_mesh(mesh)
            self.point = get_edges_center(bm)
            self.point = self.point @ self.obj.matrix_world

            quat_mat = Quaternion((0, 1, 0), math.radians(90.0)).to_matrix()
            self.normal = get_face_normal_from_vert(bm=bm)
            self.normal = self.normal @ quat_mat

            self.intersection = get_3D_point_from_mouse(
                mouse_pos=mouse_pos, 
                context=context, 
                point=self.point,
                normal=self.normal)

            if event.type == 'LEFTMOUSE' and event.value == "PRESS":
                add_bezier_point(curve=self.curve, location=self.intersection)

        self.draw_ui(context=context)

        context.area.tag_redraw()

        return {'RUNNING_MODAL'}


    def cancel(self, context):

        pass


    def draw_ui(self, context):

        # Start
        self.master.setup()


        ########################
        #   Fast UI
        ########################


        if not self.master.should_build_fast_ui():

            ########################
            #   Main
            ########################

            main_window = {
                "main_count" : [],
                "header_sub_text" : [],
                "last_col_cell_1" : [],
                "last_col_cell_2" : [],
                "last_col_cell_3" : []
            }

            window_name = ""

            main_window["main_count"]      = ["TEST"]
            main_window["header_sub_text"] = ["TEST"]
            main_window["last_col_cell_1"] = ["TEST"]
            main_window["last_col_cell_2"] = ["TEST"]
            main_window["last_col_cell_3"] = ["TEST"]

            self.master.receive_main(win_dict=main_window, window_name=window_name)


            ########################
            #   Help
            ########################


            hot_keys_dict = {}
            quick_ops_dict = {}

            hot_keys_dict["V, B, N"] = "Change the mode."

            self.master.receive_help(hot_keys_dict=hot_keys_dict, quick_ops_dict={})


            ########################
            #   Mods
            ########################


            win_dict = {}

            for mod in reversed(context.active_object.modifiers):
                win_dict[mod.name] = str(mod.type)

            self.master.receive_mod(win_dict=win_dict, active_mod_name="")

        # Finished
        self.master.finished()


    def draw_intersection(self, context):
        method_handler(self._draw_intersection,
            arguments = (context, ),
            identifier = 'Curve Draw Intersection Shader',
            exit_method = self.remove_intersection)


    def remove_intersection(self):
        if self.intersection_draw_handle:
            self.intersection_draw_handle = bpy.types.SpaceView3D.draw_handler_remove(self.intersection_draw_handle, "WINDOW")


    def draw_curve(self, context):
        method_handler(self._draw_curve,
            arguments = (context, ),
            identifier = 'Curve Draw Shader',
            exit_method = self.remove_curve)


    def remove_curve(self):
        if self.curve_draw_handle:
            self.curve_draw_handle = bpy.types.SpaceView3D.draw_handler_remove(self.curve_draw_handle, "WINDOW")


    def _draw_curve(self, context):

        pass



    def _draw_intersection(self, context):

        radius = .25
        vertices = []
        indices = []
        segments = 32
        width = 2
        color = (0,0,0,1)

        #Build ring
        for i in range(segments):
            index = i + 1
            angle = i * 3.14159 * 2 / segments

            x = cos(angle) * radius
            y = sin(angle) * radius
            z = 0
            vert = Vector((x, y, z))

            rot_mat = self.normal.rotation_difference(Vector((0,0,1))).to_matrix()

            vert = vert @ rot_mat

            vert[0] = vert[0] + self.intersection[0]
            vert[1] = vert[1] + self.intersection[1]
            vert[2] = vert[2] + self.intersection[2]

            vertices.append(vert)

            if(index == segments):
                indices.append((i, 0))
            else:
                indices.append((i, i + 1))

        # Build Grid
        grid_segments = 3
        for i in range(grid_segments):
            index = i + 1
            angle = i * 3.14159 * 2 / grid_segments

            x = cos(angle) * 5
            y = sin(angle) * 5
            z = 0
            vert = Vector((x, y, z))

            rot_mat = self.normal.rotation_difference(Vector((0,0,1))).to_matrix()
            vert = vert @ rot_mat

            vert[0] = vert[0] + self.point[0]
            vert[1] = vert[1] + self.point[1]
            vert[2] = vert[2] + self.point[2]

            vertices.append(vert)

            if(index == grid_segments):
                indices.append((i + segments, segments))
            else:
                indices.append((i + segments, i + segments + 1))


        color = (1,0,1,1)

        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'LINES', {'pos': vertices}, indices=indices)
        shader.bind()

        shader.uniform_float('color', color)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)
        glLineWidth(width)
        batch.draw(shader)

        del shader
        del batch









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

        self.curve.select_set(True)
        self.obj.select_set(True)


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

