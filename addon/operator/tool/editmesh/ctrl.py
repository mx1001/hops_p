import platform

import bpy
import bmesh

from math import radians, sqrt
from statistics import median

from mathutils import Matrix, Vector
from itertools import combinations

from bpy.types import Operator

from .. shader import dots
from .. dots import update


class HARDFLOW_OT_display(Operator):
    bl_idname = 'hardflow.display'
    bl_label = 'ctrl'
    bl_description = 'Display Hardflow Dots'
    bl_options = {'REGISTER', 'UNDO'}


    def invoke(self, context, event):
        hardflow = bpy.context.window_manager.hardflow
        self.bm = bmesh.from_edit_mesh(context.active_object.data)
        # preference = addon.preference()
        self.original_region = bpy.context.region
        self.mouse = Vector((event.mouse_region_x, event.mouse_region_y))

        context.window_manager.modal_handler_add(self)

        hardflow.dots.points.clear()
        self.collect_cross_vert(context, self.bm, self.mouse)
        update(self, context, hardflow.dots, self.mouse)
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(dots, (self, context), 'WINDOW', 'POST_PIXEL')

        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        # preference = addon.preference()
        hardflow = bpy.context.window_manager.hardflow
        #preference = addon.preference()
        # hardflow = context.window_manager.hardflow

        # held = event.ctrl or (event.oskey and self.system == 'MAC')
        # update = bool(hardflow.obj) or bool(hardflow.dots.mesh)
        # hardflow_reset = update and (hardflow.running and not self.hardflow_start)

        # print(hardflow.dots.points)
        if event.type == 'MOUSEMOVE':
            # self.collect(context)
            self.mouse = Vector((event.mouse_region_x, event.mouse_region_y))
            update(self, context, hardflow.dots, self.mouse)
        context.area.tag_redraw()


        if self.highlight is True:

            if event.type == 'LEFT_CTRL':
                if event.value == 'RELEASE':
                    vert_new = self.bm.verts.new(self.highlight_location)
                    if self.highlight_type == "cross":
                        verts = [self.v2, self.vs, self.v1, vert_new]
                    elif self.highlight_type == "cross1":
                        verts = [self.v3, self.vs, self.v1, vert_new]
                    elif self.highlight_type == "cross2":
                        verts = [self.v3, self.vs, self.v2, vert_new]

                    self.bm.faces.new(verts)
                    bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces)
                    bmesh.update_edit_mesh(context.active_object.data)
                    bpy.ops.ed.undo_push()

                    hardflow.dots.points.clear()
                    self.collect_cross_vert(context, self.bm, self.mouse)
                    update(self, context, hardflow.dots, self.mouse)

                    # print(self.highlight_location)
                    # vert_new = bm.verts.new(new_pos)
                    # self.highlight_indices
                # return {'PASS_THROUGH'}
            return {'RUNNING_MODAL'}


        if not event.ctrl:
            self.exit(context)
            hardflow.dots.points.clear()
            # update(self, context, hardflow.dots, self.mouse)
            # context.area.tag_redraw()
            return {'CANCELLED'}


        return {'PASS_THROUGH'}


    def active_vert(self, bm):
        for elem in reversed(bm.select_history):
            if isinstance(elem, bmesh.types.BMVert):
                return elem
        else:
            return None

    def collect_cross_vert(self, context, bm, mouse):
        hardflow = context.window_manager.hardflow
        vert = self.active_vert(bm)
        if vert:

            edges = [edge for edge in vert.link_edges if len(edge.link_faces) == 1]
            if len(edges) < 2:
                return

            linked_verts = []
            for e1, e2 in combinations(edges, 2):
                other_verts = [v for edge in [e1, e2] for v in edge.verts]
                other_verts.remove(vert)
                other_verts.remove(vert)
                for v in other_verts:
                    if v not in linked_verts:
                        linked_verts.append(v)

            self.vs = vert
            self.v1 = linked_verts[-1]
            self.v2 = linked_verts[-2]

            simple_edge = [edge for edge in vert.link_edges if len(edge.link_faces) == 0]

            if simple_edge:
                if len(simple_edge) < 1:
                    return

                else:
                    other_verts = [v for edge in simple_edge for v in edge.verts]
                    other_verts.remove(vert)
                    for v in other_verts:
                        self.v3 = v

                    cross_v = (self.v1.co.copy() + self.v3.co.copy()) / 2
                    new_pos = 2 * (cross_v - vert.co.copy()) + vert.co.copy()
                    new_pos = context.active_object.matrix_world @ new_pos
                    new = hardflow.dots.points.add()
                    new.location3d = new_pos
                    new.type = "cross1"

                    cross_v = (self.v2.co.copy() + self.v3.co.copy()) / 2
                    new_pos = 2 * (cross_v - vert.co.copy()) + vert.co.copy()
                    new_pos = context.active_object.matrix_world @ new_pos
                    new = hardflow.dots.points.add()
                    new.location3d = new_pos
                    new.type = "cross2"

            else:

                cross_v = (linked_verts[-1].co.copy() + linked_verts[-2].co.copy()) / 2
                new_pos = 2 * (cross_v - vert.co.copy()) + vert.co.copy()
                new_pos = context.active_object.matrix_world @ new_pos
                new = hardflow.dots.points.add()
                new.location3d = new_pos
                new.type = "cross"

    def collect_selected_verts(self, context):
        bm = bmesh.from_edit_mesh(context.active_object.data)
        # preference = addon.preference()
        hardflow = context.window_manager.hardflow
        # dots.index = ot.index

        # hardflow.dots.points.clear()

        sel = [v for v in bm.verts if v.select]

        for vert in sel:
            new = hardflow.dots.points.add()
            new.location3d = vert.co

    def exit(self, context):
        hardflow = context.window_manager.hardflow
        hardflow.dots.display = False

        self.active_point = None

        hardflow.dots.hit = False
        hardflow.dots.location = (0.0, 0.0, 0.0)
        hardflow.dots.normal = Vector()
        hardflow.dots.object = None

        # if hardflow.dots.mesh:
        #     bpy.data.meshes.remove(hardflow.dots.mesh)

        hardflow.dots.mesh = None
        hardflow.dots.index = int()
        hardflow.dots.points.clear()

        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, 'WINDOW')

        del self.draw_handler
        del self.original_region
