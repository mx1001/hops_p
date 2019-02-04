import bpy
from bpy.props import *
from bpy.types import Menu
from . icons import get_icon_id, icons
from . ui.addon_checker import draw_addon_diagnostics
import os
from bpy.types import (
        Panel,
        Menu,
        Operator,
        UIList,
        )


class LearningPopup(bpy.types.Operator):
    bl_idname = "hops.learning_popup"
    bl_label = "Learning Popup Helper"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.user_preferences.system.dpi

        return context.window_manager.invoke_props_dialog(self, width=dpi_value*3, height=200)

    def draw(self, context):
        layout = self.layout

        col = layout.column(align = True)
        row = col.row()
        box = col.box()

        for name, url in weblinks:
            col.operator("wm.url_open", text = name).url = url

weblinks = [
    ("Intro Guide",             "https://masterxeon1001.wordpress.com/2016/02/23/hard-ops-007-intro-guide/"),
    ("Hard Ops 8 P4 Notes",        "https://masterxeon1001.com/2016/09/13/hard-ops-8-p4-update/"),
    ("Hard Ops 8 P3 Notes",        "https://masterxeon1001.com/2016/05/28/hard-ops-8-release-notes/"),
    ("Hard Ops Manual",         "http://hardops-manual.readthedocs.io/en/latest/"),
    ("Hard Ops Video Playlist", "https://www.youtube.com/playlist?list=PL0RqAjByAphGEVeGn9QdPdjk3BLJXu0ho"),
    ("Hard Ops User Gallery",   "https://www.pinterest.com/masterxeon1001/hard-ops-users/"),
    ("Challenge Board",         "https://www.pinterest.com/masterxeon1001/-np/"),
    ("Hard Ops Facebook Group", "https://www.facebook.com/groups/HardOps/"),
    ("Box Cutter Latest Guide", "https://masterxeon1001.com/2016/05/28/box-cutter-4-update-notes/")
]

class InsertsPopupPreview(bpy.types.Operator):
    bl_idname = "view3d.insertpopup"
    bl_label = "Asset Popup"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.user_preferences.system.dpi

        return context.window_manager.invoke_props_dialog(self, width=dpi_value*2, height=200)

    def draw(self, context):
        layout = self.layout
        #AM = context.window_manager.asset_m
        wm = context.window_manager


        layout = self.layout.column_flow(1)
        row = layout.row()
        sub = row.row()
        sub.scale_y = 1.2

        layout.label("Classic Inserts")
        layout.template_icon_view(wm, "Hard_Ops_previews")

        layout.separator()

        layout.label("Red Series")
        layout.template_icon_view(wm, "sup_preview")

        if context.object is not None and context.selected_objects:

            layout.separator()
            if len(context.selected_objects) >1 and context.object.mode == 'EDIT':
                row = layout.row()
                row.operator("object.to_selection", text="Obj to selection", icon="MOD_MULTIRES")

            #Link Objects
            if len(context.selected_objects) > 1 and context.object.mode == 'OBJECT':
                row = layout.split(align=True)
                row.operator("make.link", text = "Link Objects", icon='CONSTRAINT' )

            #Unlink Objects
            if context.object.mode == 'OBJECT':
                row = layout.split(align=True)
                row.operator("unlink.objects", text = "Unlink Objects", icon='UNLINKED' )
    def check(self, context):
        return True

class MatcapPopupPreview(bpy.types.Operator):
    bl_idname = "view3d.matcappopup"
    bl_label = "Matcap Popup"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.user_preferences.system.dpi

        return context.window_manager.invoke_props_dialog(self, width=dpi_value*3, height=200)

    def draw(self, context):
        layout = self.layout

        view = context.space_data
        layout.template_icon_view(view, "matcap_icon")

    def check(self, context):
        return True

class BrushPopupPreview(bpy.types.Operator):
    bl_idname = "view3d.brushpopup"
    bl_label = "Brush Popup"

    @classmethod
    def poll(cls, context):
        return cls.paint_settings(context)

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.user_preferences.system.dpi

        return context.window_manager.invoke_props_dialog(self, width=dpi_value*3, height=200)

    def draw(self, context):
        layout = self.layout

        toolsettings = context.tool_settings
        settings = self.paint_settings(context)
        brush = settings.brush

        col = layout.split().column()
        layout.template_ID_preview(settings, "brush")
        #, new="brush.add", rows=3, cols=8)

    def check(self, context):
        return True

class AddonPopupPreview(bpy.types.Operator):
    bl_idname = "view3d.addoncheckerpopup"
    bl_label = "Addon Popup"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.user_preferences.system.dpi

        return context.window_manager.invoke_props_dialog(self, width=dpi_value*3, height=200)

    def draw(self, context):
        draw_addon_diagnostics(self.layout, columns = 2)

    def check(self, context):
        return True


class PizzaPopupPreview(bpy.types.Operator):
    bl_idname = "view3d.pizzapopup"
    bl_label = "Pizza Popup"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.user_preferences.system.dpi

        return context.window_manager.invoke_props_dialog(self, width=dpi_value*2, height=200)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        layout.label(text="Pizza Ops")
        layout.label(text="")
        layout.label(text="")

        row = layout.row()

        layout.label(text="Dominos Pizza")
        layout.operator("wm.url_open", text="Order Dominoes").url = "https://order.dominos.com/"
        layout.label(text="")
        layout.separator()

        layout.label(text="Pizza Hut Pizza")
        layout.operator("wm.url_open", text="Order Pizza Hut").url = "http://www.pizzahut.com/"
        layout.label(text="")
        layout.separator()

        layout.label(text="Papa John's Pizza")
        layout.operator("wm.url_open", text="Order Papa John's").url = "https://www.papajohns.com/order/menu"
        layout.label(text="")
        layout.separator()


class HelperMenu(bpy.types.Menu):
    bl_label = 'Xtras Setup'
    bl_idname = 'helper.submenu'

    def draw(self, context):
        layout = self.layout


        layout = self.layout.column(1)

        box = layout.box().column(1)

        row = box.row(1)
        row.alignment = 'CENTER'

        Diagonal = icons.get("Diagonal")
        row.label('Xtras', icon_value=Diagonal.icon_id)

        box.separator()

        row = box.row(1)
        row.operator("view3d.addoncheckerpopup", text = "Diagnostic", icon='SCRIPT' )
        row.operator("view3d.pizzapopup", text = "Pizza Ops", icon='PREVIEW_RANGE')

        box.separator()

        row = box.row(1)

        if any("AutoMirror" in s for s in bpy.context.user_preferences.addons.keys()):
            Xslap = icons.get("Xslap")
            row.operator("view3d.mirrorhelper", text = "Mirror Helper", icon_value=Xslap.icon_id)

        if any("Lattice" in s for s in bpy.context.user_preferences.addons.keys()):
            Frame = icons.get("Frame")
            row.operator("object.easy_lattice", text = "Easy Lattice")

        if any("relink" in s for s in bpy.context.user_preferences.addons.keys()):
            layout.menu("relink_menu", text = "ReLink")

        row = box.row(1)

        if any("mira_tools" in s for s in bpy.context.user_preferences.addons.keys()):
            Frame = icons.get("Frame")
            row.menu("mira.submenu", text = "Mira (T)")
            row.operator("tp_batch.mira", text = "Mira (C)")

        box.separator()

        row = box.row(1)

        Frame = icons.get("Frame")
        row.operator("view3d.generalhelper", text = "(H) Gen", icon_value=Frame.icon_id)

        Frame = icons.get("Frame")
        row.operator("view3d.orientationhelper", text = "(H) Ort", icon_value=Frame.icon_id)

        row = box.row(1)

        Frame = icons.get("Frame")
        row.operator("view3d.verthelper", text = "(H) Vert", icon_value=Frame.icon_id)

        Frame = icons.get("Frame")
        row.operator("view3d.mathelper", text = "(H) Mat", icon_value=Frame.icon_id)

        row = box.row(1)

        Frame = icons.get("Frame")
        row.operator("view3d.hops_helper_popup", text = "(H) Mod", icon_value=Frame.icon_id)

        Frame = icons.get("Frame")
        row.operator("view3d.conhelper", text = "(H) Con", icon_value=Frame.icon_id)

        row = box.row(1)

        Frame = icons.get("Frame")
        row.operator("view3d.openglhelper", text = "(H) OpGL", icon_value=Frame.icon_id)

        Frame = icons.get("Frame")
        row.operator("view3d.mathelper", text = "(H) Mat", icon_value=Frame.icon_id)

        row = box.row(1)

        Frame = icons.get("Frame")
        row.operator("view3d.displayhelper", text = "(H) Dpy", icon_value=Frame.icon_id)

        Frame = icons.get("Frame")
        row.operator("view3d.transformhelper", text = "(H) GRS", icon_value=Frame.icon_id)

        box.separator()




class Orientation(bpy.types.Operator):
    bl_label = 'Orientation Helper'
    bl_idname = 'view3d.orientationhelper'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.user_preferences.system.dpi

        return context.window_manager.invoke_props_dialog(self, width=dpi_value*2, height=300)

    def draw(self, context):
        layout = self.layout.column(1)

        box = layout.box().column(1)

        row = box.row(1)
        row.alignment = 'CENTER'
        row.scale_x = 1
        row.prop(context.space_data, "transform_manipulators", text="")
        row.prop(context.space_data, "show_manipulator", text="")

        box.separator()

        row = box.row(1)
        row.prop(context.space_data, "transform_orientation", text="")

        box.separator()

        box = layout.box().column(1)

        row = box.row(1)
        row.prop(context.space_data, "use_pivot_point_align", text="")
        row.prop(context.space_data, "pivot_point", text="", icon_only=True)
        #row.operator("wm.context_toggle", text="", icon='ALIGN').data_path = "space_data.use_pivot_point_align"

        box.separator()

        box = layout.box().column(1)

        row = box.row(1)
        row.alignment = 'CENTER'
        row.scale_x = 1
        row.prop(context.tool_settings, "use_snap", text="")
        row.prop(context.tool_settings, "use_snap_grid_absolute", text="")
        row.prop(context.tool_settings, "use_snap_align_rotation", text="")
        row.prop(context.tool_settings, "use_snap_peel_object", text="")
        row.prop(context.tool_settings, "use_snap_project", text="")

        if context.mode == 'EDIT_MESH':
            row.prop(context.tool_settings, "use_snap_self", text="")

        box.separator()

        row = box.column(1)
        row.prop(context.tool_settings, "snap_element", text="", icon_only=True)
        row.prop(context.tool_settings, "snap_target", text="")

        box.separator()

        if context.mode == 'EDIT_MESH':
            box = layout.box().column(1)

            row = box.column(1)
            row.prop(context.tool_settings, "use_mesh_automerge", text="AutoMerge", icon='AUTOMERGE_ON')
            row.prop(context.space_data, "use_occlude_geometry", text="Limit 2 Visible", icon='ORTHO')

            box.separator()

        box = layout.box().column(1)

        row = box.row(1)
        row.prop(context.tool_settings , "use_proportional_edit_objects","", icon_only=True)
        row.prop(context.tool_settings , "proportional_edit_falloff", icon_only=True)

        box.separator()

        if context.mode == 'OBJECT':
            box = layout.box().column(1)

            row = box.column(1)
            row.prop(context.object, "layers")
            row.prop(context.space_data, "layers")

            box.separator()

        # Pose
        if context.mode == 'POSE':

            row = box.row(1)
            row.operator("pose.copy", text="", icon='COPYDOWN')
            row.operator("pose.paste", text="", icon='PASTEDOWN').flipped = False
            row.operator("pose.paste", text="", icon='PASTEFLIPDOWN').flipped = True

            box.separator()




class TransformHelper(bpy.types.Operator):
    bl_label = 'Transform Helper'
    bl_idname = 'view3d.transformhelper'

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.user_preferences.system.dpi

        return context.window_manager.invoke_props_dialog(self, width=dpi_value*3, height=300)

    def draw(self, context):
        layout = self.layout.column(1)

        box = layout.box().column(1)

        row = box.row(1)
        row.menu("translate.normal_menu", text="N-Move")
        row.menu("rotate.normal_menu", text="N-Rotate")
        row.menu("resize.normal_menu", text="N-Scale")

        box.separator()

        box = layout.box().column(1)

        row = box.row(1)
        row.label(text="", icon="MAN_TRANS")
        row.prop(context.object, 'location', text="")

        row = box.row(1)
        row.label(text="", icon="MAN_ROT")
        row.prop(context.object, 'rotation_euler', text="")

        row = box.row(1)
        row.label(text="", icon="MAN_SCALE")
        row.prop(context.object, 'scale', text="")

        row = box.row(1)
        row.label(text="", icon="MOD_MESHDEFORM")
        row.prop(context.object, 'dimensions', text="")

        box.separator()

        if context.mode == 'OBJECT':
            box = layout.box().column(1)

            row = box.row(1)
            split = box.split(percentage=0.1)

            col = split.column(1)
            col.label(text="")
            col.label(text="X:")
            col.label(text="Y:")
            col.label(text="Z:")

            split.column().prop(context.object, "lock_location", text="Location")
            split.column().prop(context.object, "lock_rotation", text="Rotation")
            split.column().prop(context.object, "lock_scale", text="Scale")

            if context.object.rotation_mode in {'QUATERNION', 'AXIS_ANGLE'}:
                row = box.row()
                row.prop(context.object, "lock_rotations_4d", text="Lock Rotation")

                sub = row.row()
                sub.active = context.object.lock_rotations_4d
                sub.prop(ocontext.object, "lock_rotation_w", text="W")

            box.separator()



class DisplayHelper(bpy.types.Operator):
    bl_label = 'Display Helper'
    bl_idname = 'view3d.displayhelper'

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.user_preferences.system.dpi

        return context.window_manager.invoke_props_dialog(self, width=dpi_value*3, height=300)

    def draw(self, context):
        layout = self.layout.column(1)

        box = layout.box().column(1)

        row = box.row(1)

        obj_type = context.object.type

        is_geometry = (obj_type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT'})
        is_wire = (obj_type in {'CAMERA', 'EMPTY'})
        is_empty_image = (obj_type == 'EMPTY' and context.object.empty_draw_type == 'IMAGE')
        is_dupli = (context.object.dupli_type != 'NONE')

        split = box.split()

        col = split.column()
        col.prop(context.object, "show_name", text="Name")
        col.prop(context.object, "show_axis", text="Axis")

        if is_geometry or is_dupli:
            col.prop(context.object, "show_wire", text="Wire")

        if obj_type == 'MESH' or is_dupli:
            col.prop(context.object, "show_all_edges", text="All Edges")

        col = split.column()
        row = col.row()
        row.prop(context.object, "show_bounds", text="Bounds")

        sub = row.row()
        sub.active = context.object.show_bounds
        sub.prop(context.object, "draw_bounds_type", text="")

        if is_geometry:
            col.prop(context.object, "show_texture_space", text="Texture Space")
        col.prop(context.object, "show_x_ray", text="X-Ray")
        if obj_type == 'MESH' or is_empty_image:
            col.prop(context.object, "show_transparent", text="Transparency")

        split = box.split()

        col = split.column()
        if is_wire:

            col.active = is_dupli
            col.label(text="Maximum Dupli Draw Type:")
        else:
            col.label(text="Maximum Draw Type:")
        col.prop(context.object, "draw_type", text="")

        col = split.column()
        if is_geometry or is_empty_image:

            col.label(text="Object Color:")
            col.prop(context.object, "color", text="")

        box.separator()

        if context.mode == 'EDIT_MESH':

            box = layout.box().column(1)

            row = box.row(1)
            row.prop(context.active_object.data, "show_faces", text="Faces")
            row.prop(context.active_object.data, "show_edge_sharp", text="Sharp")

            row = box.row(1)
            row.prop(context.active_object.data, "show_edges", text="Edges")
            row.prop(context.active_object.data, "show_edge_bevel_weight", text="Bevel")

            row = box.row(1)
            row.prop(context.active_object.data, "show_edge_crease", text="Creases")
            row.prop(context.active_object.data, "show_freestyle_edge_marks", text="Edge Marks")

            row = box.row(1)
            row.prop(context.active_object.data, "show_edge_seams", text="Seams")
            row.prop(context.active_object.data, "show_freestyle_face_marks", text="Face Marks")

            row = box.row(1)
            row.prop(context.active_object.data, "show_weight", text="Weight")


            box.separator()



class GeneralHelper(bpy.types.Operator):
    bl_label = 'General Helper'
    bl_idname = 'view3d.generalhelper'

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.user_preferences.system.dpi

        return context.window_manager.invoke_props_dialog(self, width=dpi_value*3, height=300)

    def draw(self, context):
        layout = self.layout.column(1)


        if context.mode == 'OBJECT':

            obj = context.object
            if obj:

                obj_type = obj.type

                if obj_type in {'MESH', 'CURVE', 'SURFACE', 'ARMATURE', 'FONT', 'LATTICE'}:


                    box = layout.box().column(1)

                    row = box.row(1)
                    row.alignment = 'CENTER'
                    row.label("____MULTI____")

                    box.separator()

                    row = box.column(1)
                    row.operator_menu_enum("object.origin_set", "type", text="Set Origin")

                    box.separator()

                    row = box.column(1)
                    row.operator("object.parent_set", text="Set Parent")
                    row.operator("object.parent_clear", text="Clear Parent")
                    row.operator('object.parent_to_empty')

                    box.separator()

                    """
                    row = box.column(1)
                    row.operator_menu_enum("object.make_links_data", "type"," Make Link Data")
                    row.operator_menu_enum("object.make_single_user", "type"," Make Single User")

                    box.separator()

                    row = box.column(1)
                    row.operator("object.make_local","Make Local")
                    row.operator("object.proxy_make","Make Proxy")

                    box.separator()
                    """

                if obj_type in {'CURVE', 'SURFACE', 'META', 'FONT'}:

                    row = box.row(1)
                    row.operator("object.convert",text="Convert > Mesh ", icon = "OUTLINER_DATA_MESH").target="MESH"

                    box.separator()


                if obj_type in {'MESH'}:

                    row = box.row(1)
                    row.operator("curve.convert_bezier",text="Convert > Curve", icon="CURVE_DATA")

                    box.separator()


                if obj_type in {'MESH'}:

                    box = layout.box().column(1)

                    row = box.row(1)
                    row.alignment = 'CENTER'
                    row.label("____MESH____")

                    box.separator()

                    row = box.column(1)
                    row.operator("object.data_transfer", text="Data Transfer")
                    row.operator("object.datalayout_transfer", text="Data Layout Transfer")

                    box.separator()


                if obj_type in {'LAMP'}:

                    box = layout.box().column(1)

                    row = box.row(1)
                    row.alignment = 'CENTER'
                    row.label("____LIGHTS____")

                    box.separator()

                    if context.object.data.type in {'POINT', 'SUN', 'SPOT', 'HEMI', 'AREA'}:

                        row = box.row(1)
                        row.prop(context.object.data, "type", expand=True)

                        row = box.row(1)
                        row.prop(context.object.data, "color", text="")
                        row.prop(context.object.data, "energy")

                        if lamp.type in {'POINT', 'SPOT'}:

                            row = box.row(1)
                            row.prop(context.object.data, "falloff_type", text="")
                            row.prop(context.object.data, "distance")

                            if lamp.falloff_type == 'LINEAR_QUADRATIC_WEIGHTED':
                                row = box.row(1)
                                row.prop(context.object.data, "linear_attenuation", slider=True, text="Linear")
                                row.prop(context.object.data, "quadratic_attenuation", slider=True, text="Quadratic")

                            row = box.row(1)
                            row.prop(context.object.data, "use_sphere")

                        if lamp.type == 'AREA':
                            row = box.row(1)
                            row.prop(context.object.data, "distance")
                            row.prop(context.object.data, "gamma")

                box.separator()




        if context.mode == 'EDIT_MESH':

            box = layout.box().column(1)

            row = box.row(1)
            row.alignment = 'CENTER'
            row.label("____MESH____")

            box.separator()

            row = box.row(1)
            row.prop(context.active_object.data , "show_extra_edge_length", text="Edge-Length")
            row.prop(context.active_object.data , "show_extra_face_area", text="Face-Area")

            row = box.row(align=True)

            row.prop(context.active_object.data , "show_extra_edge_angle", text="Edge-Angle")
            row.prop(context.active_object.data , "show_extra_face_angle", text="Face-Angle")

            box = layout.box().column(1)

            row = box.row(1)
            row.prop(context.active_object.data, "show_normal_vertex", text="", icon='VERTEXSEL')
            row.prop(context.active_object.data, "show_normal_loop", text="", icon='LOOPSEL')
            row.prop(context.active_object.data, "show_normal_face", text="", icon='FACESEL')

            row.active = context.active_object.data.show_normal_vertex or context.active_object.data.show_normal_face
            row.prop(context.scene.tool_settings, "normal_size", text="Size")

            box.separator()


        if context.mode == 'OBJECT' or context.mode == 'EDIT_LATTICE':

            obj = context.object
            if obj:

                obj_type = obj.type

                if obj_type in {'LATTICE'}:

                    box = layout.box().column(1)

                    row = box.row(1)
                    row.alignment = 'CENTER'
                    row.label("____LATTICE____")

                    box.separator()

                    row = box.row(1)
                    row.prop(context.object.data, "use_outside")
                    row.prop_search(context.object.data, "vertex_group", context.object, "vertex_groups", text="")

                    box.separator()

                    row = box.row(1)
                    row.prop(context.object.data, "points_u", text="X")
                    row.prop(context.object.data, "points_v", text="Y")
                    row.prop(context.object.data, "points_w", text="Z")

                    row = box.row(1)
                    row.prop(context.object.data, "interpolation_type_u", text="")
                    row.prop(context.object.data, "interpolation_type_v", text="")
                    row.prop(context.object.data, "interpolation_type_w", text="")

                    box.separator()

                    row = box.row(1)
                    row.operator("lattice.make_regular", "Make Regular", icon ="LATTICE_DATA")

                    box.separator()


        if context.mode == 'OBJECT' or context.mode == 'EDIT_CURVE':

            obj = context.object
            if obj:

                obj_type = obj.type

                if obj_type in {'CURVE'}:

                    box = layout.box().column(1)

                    row = box.row(1)
                    row.alignment = 'CENTER'
                    row.label("____CURVE____")

                    box.separator()

                    row = box.row(1)
                    sub = row.row(1)
                    sub.scale_x = 0.25
                    sub.prop(context.object.data, "dimensions", expand=True)

                    row = box.row(1)
                    row.prop(context.object.data, "fill_mode", text="")
                    row.prop(context.object.data, "bevel_depth", text="Bevel")

                    row = box.row(1)
                    row.prop(context.object.data, "resolution_u", text="Ring")
                    row.prop(context.object.data, "bevel_resolution", text="Loop")

                    row = box.row(1)
                    row.prop(context.object.data, "offset", "Offset")
                    row.prop(context.object.data, "extrude","Height")

                    box.separator()

                    row = box.row(1)
                    row.prop(context.object.data, "bevel_factor_start", text="Start")
                    row.prop(context.object.data, "bevel_factor_end", text="End")

                    row = box.row(1)
                    row.prop(context.object.data, "bevel_factor_mapping_start", text="")
                    row.prop(context.object.data, "bevel_factor_mapping_end", text="")

                    box.separator()

                    row = box.row(1)
                    row.prop(context.object, "show_wire", text="Wire")
                    row.prop(context.object, "show_x_ray", text="X-Ray")

                    box.separator()




class OpenGLHelper(bpy.types.Operator):
    bl_label = 'OpenGL Helper'
    bl_idname = 'view3d.openglhelper'

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.user_preferences.system.dpi

        return context.window_manager.invoke_props_dialog(self, width=dpi_value*3, height=300)

    def draw(self, context):
        layout = self.layout.column(1)

        box = layout.box().column(1)

        row = box.row(1)

        row.prop(context.space_data, "show_textured_solid","Enable Textured Solid")

        row = box.row(1)
        row.menu("VIEW3D_MT_opengl_lights_presets", text=bpy.types.VIEW3D_MT_opengl_lights_presets.bl_label, icon = "COLLAPSEMENU")
        row.operator("scene.opengl_lights_preset_add", text="", icon='ZOOMIN')
        row.operator("scene.opengl_lights_preset_add", text="", icon='ZOOMOUT').remove_active = True

        box.separator()

        system = bpy.context.user_preferences.system

        def opengl_lamp_buttons(column, lamp):

            split = column.split(percentage=0.1)
            split.prop(lamp, "use", text="", icon='OUTLINER_OB_LAMP' if lamp.use else 'LAMP_DATA')

            col = split.column()
            col.active = lamp.use

            row = col.row()
            row.label(text="Diffuse:")
            row.prop(lamp, "diffuse_color", text="")

            row = col.row()
            row.label(text="Specular:")
            row.prop(lamp, "specular_color", text="")

            col = split.column()
            col.active = lamp.use
            col.prop(lamp, "direction", text="")

        row = box.row(1)

        box.separator()

        box = layout.box().column(1)

        column = box.column()

        split = column.split(percentage=0.1)
        split.label()
        split.label(text="Colors:")
        split.label(text="Direction:")

        lamp = system.solid_lights[0]
        opengl_lamp_buttons(column, lamp)

        lamp = system.solid_lights[1]
        opengl_lamp_buttons(column, lamp)

        lamp = system.solid_lights[2]
        opengl_lamp_buttons(column, lamp)

        box.separator()



class VertexHelper(bpy.types.Operator):
    bl_label = 'Vertex Helper'
    bl_idname = 'view3d.verthelper'

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.user_preferences.system.dpi

        return context.window_manager.invoke_props_dialog(self, width=dpi_value*3, height=300)

    def draw(self, context):
        layout = self.layout.column(1)

        box = layout.box().column(1)

        row = box.row(1)
        row.alignment = 'CENTER'
        row.label("VERTEX#", icon='STICKY_UVS_LOC')

        box.separator()

        row = box.row()
        row.template_list("MESH_UL_vgroups", "", context.object, "vertex_groups", context.object.vertex_groups, "active_index", rows=4)

        col = row.column()
        sub = col.column(1)
        sub.operator("object.vertex_group_add", icon='ZOOMIN', text="")
        sub.operator("object.vertex_group_remove", icon='ZOOMOUT', text="").all = False
        sub.menu("MESH_MT_vertex_group_specials", icon='DOWNARROW_HLT', text="")
        sub.operator("object.vertex_group_move", icon='TRIA_UP', text="").direction = 'UP'
        sub.operator("object.vertex_group_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

        box.separator()

        row = box.row(1)
        row.operator("object.vertex_group_assign", text="Assign")
        row.operator("object.vertex_group_remove_from", text="Remove")

        row = box.row(1)
        row.operator("object.vertex_group_select", text="Select")
        row.operator("object.vertex_group_deselect", text="Deselect")

        row = box.row(1)
        row.prop(context.tool_settings, "vertex_group_weight", text="Weight")

        box.separator()


class MaterialHelper(bpy.types.Operator):
    bl_label = 'Material Helper'
    bl_idname = 'view3d.mathelper'

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.user_preferences.system.dpi

        return context.window_manager.invoke_props_dialog(self, width=dpi_value*3, height=300)

    def draw(self, context):
        layout = self.layout.column(1)

        box = layout.box().column(1)

        row = box.row(1)
        row.operator("object.material_color", text="", icon='ZOOMIN')
        row.menu("object.material_list", text="Apply...", icon="NLA_PUSHDOWN")
        row.operator("material.remove_all", text="", icon="ZOOMOUT")
        row.menu("MATERIAL_MT_specials", icon='DOWNARROW_HLT', text="")

        box.separator()

        row = box.row()
        row.template_list("MATERIAL_UL_matslots", "", context.object, "material_slots", context.object, "active_material_index", rows=3)

        split = row.split(1)
        row = split.column(1)
        row.operator("object.material_slot_move", icon='TRIA_UP', text="").direction = 'UP'
        row.operator("object.material_slot_move", icon='TRIA_DOWN', text="").direction = 'DOWN'
        row.operator("purge.unused_material_data", text="", icon="PANEL_CLOSE")

        if context.object.mode == 'EDIT':
            row.separator()

            row = box.row(1)
            row.operator("object.material_slot_assign", text="Assign")
            row.operator("object.material_slot_select", text="Select")
            row.operator("object.material_slot_deselect", text="Deselect")

        box.separator()

        if len(context.object.material_slots) > 0:
            box = layout.box().column(1)

            row = box.row(1)
            row.alignment = 'CENTER'
            row.label("Mat-Properties", icon='NODETREE')

            box.separator()

            row = box.row(1)
            row.prop(context.object.data, "diffuse_color", text="")

            if context.object.active_material:
                row = box.row(1)
                if context.object.active_material.use_object_color == True:
                    row.prop(context.object.active_material, "use_object_color","Obj-Color", icon="FILE_REFRESH")
                    row.prop(context.object, "color", text="")
                else:
                    row.prop(context.object.active_material, "use_object_color","Material Color", icon="FILE_REFRESH")

                if not context.object.active_material.use_object_color:

                    box.separator()

                    row = box.row(1)
                    row.prop(context.object.active_material, "type", expand=True)

                    row = box.row(1)
                    row.prop(context.object.active_material, "diffuse_intensity", text="DI")
                    row.prop(context.object.active_material, "diffuse_color", text="")

                    box.separator()

                    row = box.row(1)
                    row.prop(context.object.active_material, "specular_intensity", text="S-I")
                    row.prop(context.object.active_material, "specular_color", text="")

                    row = box.row(1)
                    row.prop(context.object.active_material, "specular_hardness", text="S-H")

                    box.separator()

                    row = box.row(1)
                    row.prop(context.object.active_material, "use_shadeless","Shadeless", icon="SNAP_FACE")
                    row.prop(context.object.active_material, "emit", "E")

                    row = box.row(1)
                    row.prop(context.object.active_material, "translucency", "T")
                    row.prop(context.object.active_material, "ambient", "A")

                    box.separator()

                    row = box.row(1)
                    row.operator("material.add_wire","2-Mat-Wire", icon="MESH_GRID")
                    sub = row.row(1)
                    sub.scale_x = 0.5
                    sub.prop(context.window_manager, 'col_material_wire')
                    sub.prop(context.window_manager, 'col_material_surface')

                    box.separator()

    def check(self, context):
        return True

class MirrorTest(bpy.types.Menu):
    bl_label = 'Automirror Panel'
    bl_idname = 'automirror.submenu'

    def draw(self, context):
        layout = self.layout
        if bpy.context.object and bpy.context.object.type == 'MESH':

            row = layout.row(align=True)
            row.operator("object.automirror")

            layout = self.layout.column_flow(2)

            layout.prop(context.scene, "AutoMirror_axis", text="Mirror Axis", expand=True)

            layout.prop(context.scene, "AutoMirror_orientation", text="")
            layout.prop(context.scene, "AutoMirror_toggle_edit", text="Toggle Edit")

            if bpy.context.scene.AutoMirror_cut:
                row = layout.row(align=True)
                col = row.column(align=True)
                col.prop(context.scene, "AutoMirror_use_clip", text="Use Clip")
                col.prop(context.scene, "AutoMirror_show_on_cage", text="Editable")
                layout.prop(context.scene, "AutoMirror_apply_mirror", text="Apply Mirror")

        else:
            layout.label(icon="ERROR", text="No mesh selected")


    def check(self, context):
        return True

class MirrorPopup(bpy.types.Operator):
    bl_idname = "view3d.mirrorhelper"
    bl_label = "(H) Mir"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.user_preferences.system.dpi
        return context.window_manager.invoke_props_dialog(self, width=dpi_value*3, height=300)

    def draw(self, context):
        layout = self.layout


        box = layout.box().column(1)

        row = box.row(1)
        row.operator("object.automirror", text = "Execute Auto Mirror" , icon = "MOD_WIREFRAME")

        row = box.row(1)
        row.prop(context.scene, "AutoMirror_axis", text="")
        row.prop(context.scene, "AutoMirror_orientation", text="")
        row.prop(context.scene, "AutoMirror_threshold", text="")

        box.separator()

        row = box.row(1)
        row.prop(context.scene, "AutoMirror_toggle_edit", text="Toggle Edit")
        row.prop(context.scene, "AutoMirror_cut", text="Cut+Mirror")

        if bpy.context.scene.AutoMirror_cut:

            row = box.row(1)
            row.prop(context.scene, "AutoMirror_use_clip", text="Use Clip")
            row.prop(context.scene, "AutoMirror_show_on_cage", text="Editable")

            row = box.row(1)
            row.prop(context.scene, "AutoMirror_apply_mirror", text="Apply Mirror")

        box.separator()

        box = layout.box().column(1)

        Xslap = icons.get("Xslap")
        row.operator("halfslap.object", text = "(X) - Symmetrize", icon_value=Xslap.icon_id)

        Yslap = icons.get("Yslap")
        row.operator("yhalfslap.object", text = "(Y) - Symmetrize", icon_value=Yslap.icon_id)

        Zslap = icons.get("Zslap")
        row.operator("zhalfslap.object", text = "(Z) - Symmetrize", icon_value=Zslap.icon_id)

        box.separator()

    def check(self, context):
        return True

class ConPopup(bpy.types.Operator):
    bl_idname = "view3d.conhelper"
    bl_label = "Constraint Helper"
    #bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.user_preferences.system.dpi

        return context.window_manager.invoke_props_dialog(self, width=dpi_value*4, height=300)

    def draw(self, context):
        mp = DATA_PT_constraints(context)
        ob = context.object

        layout = self.layout
        row = layout.row()

        if context.active_object is None:
            row.alignment = 'CENTER'
            row.label("No Object!", icon = 'INFO')
            return

        row.operator_menu_enum("object.constraint_add", "type")
        row.operator("object.make_links_data", text="Copy Constraints From").type="CONSTRAINTS"
        for md in ob.constraints:
            box = layout.template_constraint(md)
            if box:
                getattr(mp, md.type)(box, ob, md)

    def check(self, context):
        return True
