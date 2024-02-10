import bpy
from math import radians, degrees
from .. preferences import get_preferences
from .. utils.blender_ui import get_dpi_factor
from .. icons import get_icon_id


class HOPS_OT_hopstool_helper(bpy.types.Operator):
    bl_idname = 'hops.hopstool_helper'
    bl_description = 'Display HOpstool Helper'
    bl_label = 'HOps Bevel Helper'


    def invoke(self, context, event):

        return context.window_manager.invoke_popup(self)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):

        topcol = self.layout.column()
        split = topcol.split(factor=0.8, align=True)
        split.label(text='HopsTool Menu')

        row = split.row(align=True)
        row.scale_x = 0.9
        row.scale_y = 0.9

        row.prop(get_preferences().behavior, "add_mirror_to_boolshapes", text="")#  icon="MOD_MIRROR")
        row.prop(get_preferences().behavior, "add_WN_to_boolshapes", text="")# , icon="MOD_NORMALEDIT")
        row.prop(get_preferences().behavior, "cursor_boolshapes", text="")# , icon="CURSOR")

        self.layout.separator()

        maincol = self.layout.column()
        split = maincol.row(align=True)

        row = split.row(align=True)
        col = row.column(align=True)
        col.scale_x = 1.3
        col.scale_y = 1.3
        col.operator('hops.add_plane', text='', icon='MESH_PLANE')
        col.operator('hops.add_box', text='', icon='MESH_CUBE')
        col.operator('hops.add_bbox', text='', icon='META_CUBE')
        col.operator('hops.add_circle', text='', icon='MESH_CIRCLE')
        col.operator('hops.add_cylinder', text='', icon='MESH_CYLINDER')
        col.operator('hops.add_vertex', text='', icon='DOT')

        row = split.row(align=True)
        col = row.column(align=True)
        col.scale_x = 1.3
        col.scale_y = 1.3
        col.operator('hops.add_cone', text='', icon='MESH_CONE')
        col.operator('hops.add_ring', text='', icon='MESH_TORUS')
        col.operator('hops.add_screw', text='', icon='MOD_SCREW')
        col.operator('hops.add_sphere', text='', icon='MESH_UVSPHERE')
        col.menu('HOPS_MT_Tool_grid', text='', icon='MESH_GRID')

        row.separator(factor=3)

        row = split.row(align=True)
        col = row.column(align=True)
        col.scale_x = 1.3
        col.scale_y = 1.3

        selected = context.selected_objects
        col.enabled = getattr(context.active_object, "type", "") == "MESH" and context.active_object in selected
        grey = 'Grey' if not col.enabled else ''

        col.operator(
            'hops.add_mod_displace',
            text = '',
            icon_value=get_icon_id(F"{grey}MoveX")).axis = 'X'

        col.operator(
            'hops.add_mod_displace',
            text = '',
            icon_value = get_icon_id(F"{grey}MoveY")).axis = 'Y'

        col.operator(
            'hops.add_mod_displace',
            text = '',
            icon_value = get_icon_id(F"{grey}MoveZ")).axis = 'Z'

        col.operator(
            'hops.add_mod_extrude',
            text = '',
            icon_value = get_icon_id(F"{grey}ExtrudeX")).axis = 'X'

        col.operator(
            'hops.add_mod_extrude',
            text = '',
            icon_value = get_icon_id(F"{grey}ExtrudeY")).axis = 'Y'

        col.operator(
            'hops.add_mod_extrude',
            text = '',
            icon_value = get_icon_id(F"{grey}ExtrudeZ")).axis = 'Z'


        row = split.row(align=True)
        col = row.column(align=True)
        col.scale_x = 1.3
        col.scale_y = 1.3

        selected = context.selected_objects
        col.enabled = getattr(context.active_object, "type", "") == "MESH" and context.active_object in selected
        grey = 'Grey' if not col.enabled else ''

        col.operator(
            'hops.add_mod_screw',
            text = '',
            icon = 'MOD_SCREW').axis = 'X'

        col.operator(
            'hops.add_mod_solidify',
            text = '',
            icon = 'FACESEL').axis = 'Z'

        col.operator(
            'hops.add_mod_solidify',
            text = '',
            icon = 'MOD_SOLIDIFY').axis = 'C'

        col.operator(
            'hops.add_mod_decimate',
            text = '',
            icon = 'MOD_DECIM')

        col.operator(
            'hops.add_mod_weld',
            text = '',
            icon = 'AUTOMERGE_OFF')

        col.operator(
            'hops.add_mod_split',
            text = '',
            icon = 'MOD_EDGESPLIT')

        row = split.row(align=True)
        col = row.column(align=True)
        col.scale_x = 1.3
        col.scale_y = 1.3

        selected = context.selected_objects
        col.enabled = getattr(context.active_object, "type", "") == "MESH" and context.active_object in selected
        grey = 'Grey' if not col.enabled else ''

        col.operator(
            'hops.add_mod_bevel_corners',
            text = '',
            icon_value = get_icon_id(F"{grey}BevelCorners"))

        col.operator(
            'hops.add_mod_bevel_chamfer',
            text = '',
            icon_value = get_icon_id(F"{grey}BevelChamfer"))

        col.operator(
            'hops.add_mod_bevel',
            text = '',
            icon_value = get_icon_id(F"{grey}BevelAll"))

        col.operator(
            'hops.add_mod_triangulate',
            text = '',
            icon = 'MOD_TRIANGULATE')

        col.operator(
            'hops.add_mod_wireframe',
            text = '',
            icon = 'MOD_WIREFRAME')

        col.operator(
            'hops.add_mod_lattice',
            text = '',
            icon = 'MOD_LATTICE')

        row = split.row(align=True)
        col = row.column(align=True)
        col.scale_x = 1.3
        col.scale_y = 1.3

        selected = context.selected_objects
        col.enabled = getattr(context.active_object, "type", "") == "MESH" and context.active_object in selected
        grey = 'Grey' if not col.enabled else ''

        col.operator(
            'hops.add_mod_subsurf',
            text = '',
            icon = 'MOD_SUBSURF')

        twist = col.operator(
            'hops.add_mod_deform',
            text = '',
            icon_value = get_icon_id(F"{grey}Twist"))
        twist.axis = 'Z'
        twist.mode = 'TWIST'
        twist.name = 'HOPS_twist_z'

        bend = col.operator(
            'hops.add_mod_deform',
            text = '',
            icon_value = get_icon_id(F"{grey}Bend"))
        bend.axis = 'Z'
        bend.mode = 'BEND'
        bend.name = 'HOPS_bend_z'

        taper = col.operator(
            'hops.add_mod_deform',
            text = '',
            icon_value = get_icon_id(F"{grey}Taper"))
        taper.axis = 'Z'
        taper.mode = 'TAPER'
        taper.name = 'HOPS_taper_z'

        strech = col.operator(
            'hops.add_mod_deform',
            text = '',
            icon_value = get_icon_id(F"{grey}Stretch"))
        strech.axis = 'Z'
        strech.mode = 'STRETCH'
        strech.name = 'HOPS_strech_z'

        col.operator(
            'hops.add_mod_curve',
            text = '',
            icon = 'MOD_CURVE')

        row = split.row(align=True)
        col = row.column(align=True)
        col.scale_x = 1.3
        col.scale_y = 1.3

        selected = context.selected_objects
        col.enabled = getattr(context.active_object, "type", "") == "MESH" and context.active_object in selected
        grey = 'Grey' if not col.enabled else ''

        col.operator(
            'hops.add_mod_array',
            text = '',
            icon_value = get_icon_id(F"{grey}ArrayX")).axis = 'X'

        col.operator(
            'hops.add_mod_array',
            text = '',
            icon_value = get_icon_id(F"{grey}ArrayY")).axis = 'Y'

        col.operator(
            'hops.add_mod_array',
            text = '',
            icon_value = get_icon_id(F"{grey}ArrayZ")).axis = 'Z'

        col.operator(
            'hops.add_mod_circle_array',
            text = '',
            icon_value = get_icon_id(F"{grey}ArrayCircle")).axis = 'X'

        row.separator(factor=3)

        row = split.row(align=True)
        col = row.column(align=True)
        col.scale_x = 1.3
        col.scale_y = 1.3

        col.operator("hops.mirror_gizmo", text="", icon="MOD_MIRROR")

