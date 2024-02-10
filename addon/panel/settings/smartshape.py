import bpy

from bpy.types import Panel

from ... utility import active_tool, addon, names


class HARDFLOW_PT_display_smartshapes(Panel):
    bl_label = 'Smartshape'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Hops'

    @classmethod
    def poll(cls, context):
        return active_tool().idname == 'Hops'

    def draw(self, context):
        layout = self.layout

        preference = addon.preference()

        layout.operator('hops.add_vertex', text='Vertex', icon='DOT')
        layout.operator('hops.add_plane', text='Plane', icon='MESH_PLANE')
        layout.operator('hops.add_box', text='Cube', icon='MESH_CUBE')
        layout.operator('hops.add_bbox', text='Box', icon='META_CUBE')
        layout.menu('HOPS_MT_Tool_grid', text='Grid', icon='MESH_GRID')
        layout.operator('hops.add_circle', text='Circle', icon='MESH_CIRCLE')
        layout.operator('hops.add_sphere', text='Sphere', icon='MESH_UVSPHERE')
        layout.operator('hops.add_cylinder', text='Cylinder', icon='MESH_CYLINDER')
        layout.operator('hops.add_cone', text='Cone', icon='MESH_CONE')
        layout.operator('hops.add_ring', text='Ring', icon='MESH_TORUS')
        layout.operator('hops.add_screw', text='Screw', icon='MOD_SCREW')

        # self.label_row(layout.row(), preference.display, 'display_corner', label='Dot Display Corner')

    def label_row(self, row, path, prop, label=''):
        row.label(text=label if label else names[prop])
        row.prop(path, prop, text='')
