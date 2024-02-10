import bpy
import bmesh
from math import degrees
import bpy.utils.previews
from ... preferences import get_preferences
from ...ui_framework.operator_ui import Master


class HOPS_OT_CleanMeshOperator(bpy.types.Operator):
    bl_idname      = "view3d.clean_mesh"
    bl_label       = "Limited Dissolve"
    bl_options     = {'REGISTER', 'UNDO'}
    bl_description = """Clean Mesh
    
Cleans mesh of Coplanar / Colinear / Degenerate / Duplicate FACES, EDGES and VERTS
Advanced selection options in F6"""

    text      = "Limited Dissolve Removed"
    op_tag    = "Limited Dissolve / Remove Doubles"
    op_detail = "Angled Doubles Dissolved"

    called_ui = False

    def __init__(self):

        HOPS_OT_CleanMeshOperator.called_ui = False


    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.mode in {'OBJECT', 'EDIT'}


    def draw(self, context):

        layout = self.layout
        box = layout.box()
        row = box.row()

        row.prop(get_preferences().property, 'meshclean_mode', expand=True)
        box.prop(get_preferences().property, 'meshclean_dissolve_angle', text="Limited Dissolve Angle")
        box.prop(get_preferences().property, 'meshclean_remove_threshold', text="Remove Threshold")
        box.prop(get_preferences().property, 'meshclean_unhide_behavior', text="Unhide Mesh")
        box.prop(get_preferences().property, 'meshclean_delete_interior', text="Delete Interior Faces")


    def execute(self, context):

        self.object_mode = context.active_object.mode

        if get_preferences().property.meshclean_mode == 'SELECTED':
            if self.object_mode == 'OBJECT':
                original_active_object = context.view_layer.objects.active

                for object in context.selected_objects:
                    if object.type == 'MESH':
                        self.clean_mesh(context, object)

                context.view_layer.objects.active = original_active_object

            else:
                if context.active_object.type == 'MESH':
                    self.clean_mesh(context, context.active_object)

        elif get_preferences().property.meshclean_mode == 'VISIBLE':
            if self.object_mode == 'OBJECT':
                original_active_object = context.view_layer.objects.active

                for object in context.visible_objects:
                    if object.type == 'MESH':
                        self.clean_mesh(context, object)

                context.view_layer.objects.active = original_active_object

            else:
                if context.active_object.type == 'MESH':
                    mesh = bmesh.from_edit_mesh(context.active_object.data)

                    original_selected_geometry = {'verts': [vert for vert in mesh.verts if vert.select],
                                                  'edges': [edge for edge in mesh.edges if edge.select],
                                                  'faces': [face for face in mesh.faces if face.select]}

                    visible_geometry = {'verts': [vert for vert in mesh.verts if not vert.hide],
                                        'edges': [edge for edge in mesh.edges if not edge.hide],
                                        'faces': [face for face in mesh.faces if not face.hide]}

                    # unselect geometry
                    for type in original_selected_geometry:
                        for geo in original_selected_geometry[type]:
                            geo.select_set(False)

                    # select visible
                    for type in visible_geometry:
                        for geo in visible_geometry[type]:
                            geo.select_set(True)

                    self.clean_mesh(context, context.active_object)

        else:
            if context.active_object.type == 'MESH':
                self.clean_mesh(context, context.active_object)

        bpy.ops.object.mode_set(mode=self.object_mode)

        # Operator UI
        if not HOPS_OT_CleanMeshOperator.called_ui:
            HOPS_OT_CleanMeshOperator.called_ui = True

            ui = Master()

            draw_data = [
                ["Clean Mesh"],
                ["Remove Threshold", "%.1f" % get_preferences().property.meshclean_remove_threshold],
                ["Dissovle Angle", "%.1f" % degrees(get_preferences().property.meshclean_dissolve_angle)+ "°"],
                [f"Modifiers Applied / Remain", f"{0} / {len(context.active_object.modifiers[:])}"],
                ["MeshClean Mode ", get_preferences().property.meshclean_mode]
            ]

            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return {'FINISHED'}


    def clean_mesh(self, context, object):

        context.view_layer.objects.active = object

        bpy.ops.object.mode_set(mode='EDIT')

        if get_preferences().property.meshclean_unhide_behavior:
            bpy.ops.mesh.reveal()

        context.tool_settings.mesh_select_mode = (False, True, False)

        if get_preferences().property.meshclean_mode == 'ACTIVE' or self.object_mode == 'OBJECT':
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_all(action='TOGGLE')

        bpy.ops.mesh.remove_doubles(threshold=get_preferences().property.meshclean_remove_threshold)

        bpy.ops.mesh.dissolve_limited(angle_limit=get_preferences().property.meshclean_dissolve_angle)

        if get_preferences().property.meshclean_delete_interior:
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_interior_faces()
            bpy.ops.mesh.delete(type='FACE')

        bpy.ops.object.mode_set(mode='OBJECT')
