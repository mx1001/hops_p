# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>
from bpy.types import Panel
from ... preferences import get_preferences


# Parent class for constraint panels, with templates and drawing methods
# shared between the bone and object constraint panels
class ConstraintButtonsPanel(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = ""
    bl_options = {'INSTANCED', 'HEADER_LAYOUT_EXPAND', 'DRAW_BOX'}

    @staticmethod
    def draw_influence(self, layout, con):
        layout.separator()
        if con.type in {'IK', 'SPLINE_IK'}:
            # constraint.disable_keep_transform doesn't work well
            # for these constraints.
            layout.prop(con, "influence")
        else:
            row = layout.row(align=True)
            row.prop(con, "influence")
            row.operator("constraint.disable_keep_transform", text="", icon='CANCEL')

    @staticmethod
    def space_template(self, layout, con, target=True, owner=True):
        if target or owner:
            layout.separator()
            if target:
                layout.prop(con, "target_space", text="Target")
            if owner:
                layout.prop(con, "owner_space", text="Owner")

    @staticmethod
    def target_template(self, layout, con, subtargets=True):
        col = layout.column()
        col.prop(con, "target")  # XXX limiting settings for only 'curves' or some type of object

        if con.target and subtargets:
            if con.target.type == 'ARMATURE':
                col.prop_search(con, "subtarget", con.target.data, "bones", text="Bone")

                if con.subtarget and hasattr(con, "head_tail"):
                    row = col.row(align=True)
                    row.use_property_decorate = False
                    sub = row.row(align=True)
                    sub.prop(con, "head_tail")
                    # XXX icon, and only when bone has segments?
                    sub.prop(con, "use_bbone_shape", text="", icon='IPO_BEZIER')
                    row.prop_decorator(con, "head_tail")
            elif con.target.type in {'MESH', 'LATTICE'}:
                col.prop_search(con, "subtarget", con.target, "vertex_groups", text="Vertex Group")

    def get_constraint(self, context, layout):
        con = None
        if context.pose_bone:
            con = context.pose_bone.constraints[self.list_panel_index]
        else:
            con = context.object.constraints[self.list_panel_index]
        self.layout.context_pointer_set("constraint", con)
        return con

    def draw_header(self, context, layout, con):


        layout.template_constraint_header(con)

    # Drawing methods for specific constraints. (Shared by object and bone constraint panels)

    def CHILD_OF(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        self.target_template(self, layout, con)

        row = layout.row(heading="Location")
        row.use_property_decorate = False
        row.prop(con, "use_location_x", text="X", toggle=True)
        row.prop(con, "use_location_y", text="Y", toggle=True)
        row.prop(con, "use_location_z", text="Z", toggle=True)
        row.label(icon='BLANK1')

        row = layout.row(heading="Rotation")
        row.use_property_decorate = False
        row.prop(con, "use_rotation_x", text="X", toggle=True)
        row.prop(con, "use_rotation_y", text="Y", toggle=True)
        row.prop(con, "use_rotation_z", text="Z", toggle=True)
        row.label(icon='BLANK1')

        row = layout.row(heading="Scale")
        row.use_property_decorate = False
        row.prop(con, "use_scale_x", text="X", toggle=True)
        row.prop(con, "use_scale_y", text="Y", toggle=True)
        row.prop(con, "use_scale_z", text="Z", toggle=True)
        row.label(icon='BLANK1')

        row = layout.row()
        row.operator("constraint.childof_set_inverse")
        row.operator("constraint.childof_clear_inverse")

        self.draw_influence(self, layout, con)

    def TRACK_TO(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        self.target_template(self, layout, con)

        layout.prop(con, "track_axis", expand=True)
        layout.prop(con, "up_axis", text="Up", expand=True)
        layout.prop(con, "use_target_z")

        self.space_template(self, layout, con)

        self.draw_influence(self, layout, con)

    def FOLLOW_PATH(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        self.target_template(self, layout, con)

        if con.use_fixed_location:
            layout.prop(con, "offset_factor", text="Offset Factor")
        else:
            layout.prop(con, "offset")

        layout.prop(con, "forward_axis", expand=True)
        layout.prop(con, "up_axis", expand=True)

        col = layout.column()
        col.prop(con, "use_fixed_location")
        col.prop(con, "use_curve_radius")
        col.prop(con, "use_curve_follow")

        layout.operator("constraint.followpath_path_animate", text="Animate Path", icon='ANIM_DATA')

        self.draw_influence(self, layout, con)

    def LIMIT_ROTATION(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        # Decorators and property split are really buggy with these properties
        row = layout.row(heading="Limit X", align=True)
        row.use_property_decorate = False
        row.prop(con, "use_limit_x", text="")
        sub = row.column(align=True)
        sub.active = con.use_limit_x
        sub.prop(con, "min_x", text="Min")
        sub.prop(con, "max_x", text="Max")
        row.label(icon="BLANK1")

        row = layout.row(heading="Y", align=True)
        row.use_property_decorate = False
        row.prop(con, "use_limit_y", text="")
        sub = row.column(align=True)
        sub.active = con.use_limit_y
        sub.prop(con, "min_y", text="Min")
        sub.prop(con, "max_y", text="Max")
        row.label(icon="BLANK1")

        row = layout.row(heading="Z", align=True)
        row.use_property_decorate = False
        row.prop(con, "use_limit_z", text="")
        sub = row.column(align=True)
        sub.active = con.use_limit_z
        sub.prop(con, "min_z", text="Min")
        sub.prop(con, "max_z", text="Max")
        row.label(icon="BLANK1")

        layout.prop(con, "use_transform_limit")
        layout.prop(con, "owner_space")

        self.draw_influence(self, layout, con)

    def LIMIT_LOCATION(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        col = layout.column()

        row = col.row(heading="Minimum X", align=True)
        row.use_property_decorate = False
        sub = row.row(align=True)
        sub.prop(con, "use_min_x", text="")
        subsub = sub.row(align=True)
        subsub.active = con.use_min_x
        subsub.prop(con, "min_x", text="")
        row.prop_decorator(con, "min_x")

        row = col.row(heading="Y", align=True)
        row.use_property_decorate = False
        sub = row.row(align=True)
        sub.prop(con, "use_min_y", text="")
        subsub = sub.row(align=True)
        subsub.active = con.use_min_y
        subsub.prop(con, "min_y", text="")
        row.prop_decorator(con, "min_y")

        row = col.row(heading="Z", align=True)
        row.use_property_decorate = False
        sub = row.row(align=True)
        sub.prop(con, "use_min_z", text="")
        subsub = sub.row(align=True)
        subsub.active = con.use_min_z
        subsub.prop(con, "min_z", text="")
        row.prop_decorator(con, "min_z")

        col.separator()

        row = col.row(heading="Maximum X", align=True)
        row.use_property_decorate = False
        sub = row.row(align=True)
        sub.prop(con, "use_max_x", text="")
        subsub = sub.row(align=True)
        subsub.active = con.use_max_x
        subsub.prop(con, "max_x", text="")
        row.prop_decorator(con, "max_x")

        row = col.row(heading="Y", align=True)
        row.use_property_decorate = False
        sub = row.row(align=True)
        sub.prop(con, "use_max_y", text="")
        subsub = sub.row(align=True)
        subsub.active = con.use_max_y
        subsub.prop(con, "max_y", text="")
        row.prop_decorator(con, "max_y")

        row = col.row(heading="Z", align=True)
        row.use_property_decorate = False
        sub = row.row(align=True)
        sub.prop(con, "use_max_z", text="")
        subsub = sub.row(align=True)
        subsub.active = con.use_max_z
        subsub.prop(con, "max_z", text="")
        row.prop_decorator(con, "max_z")

        layout.prop(con, "use_transform_limit")
        layout.prop(con, "owner_space")

        self.draw_influence(self, layout, con)

    def LIMIT_SCALE(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        col = layout.column()

        row = col.row(heading="Minimum X", align=True)
        row.use_property_decorate = False
        sub = row.row(align=True)
        sub.prop(con, "use_min_x", text="")
        subsub = sub.row(align=True)
        subsub.active = con.use_min_x
        subsub.prop(con, "min_x", text="")
        row.prop_decorator(con, "min_x")

        row = col.row(heading="Y", align=True)
        row.use_property_decorate = False
        sub = row.row(align=True)
        sub.prop(con, "use_min_y", text="")
        subsub = sub.row(align=True)
        subsub.active = con.use_min_y
        subsub.prop(con, "min_y", text="")
        row.prop_decorator(con, "min_y")

        row = col.row(heading="Z", align=True)
        row.use_property_decorate = False
        sub = row.row(align=True)
        sub.prop(con, "use_min_z", text="")
        subsub = sub.row(align=True)
        subsub.active = con.use_min_z
        subsub.prop(con, "min_z", text="")
        row.prop_decorator(con, "min_z")

        col.separator()

        row = col.row(heading="Maximum X", align=True)
        row.use_property_decorate = False
        sub = row.row(align=True)
        sub.prop(con, "use_max_x", text="")
        subsub = sub.row(align=True)
        subsub.active = con.use_max_x
        subsub.prop(con, "max_x", text="")
        row.prop_decorator(con, "max_x")

        row = col.row(heading="Y", align=True)
        row.use_property_decorate = False
        sub = row.row(align=True)
        sub.prop(con, "use_max_y", text="")
        subsub = sub.row(align=True)
        subsub.active = con.use_max_y
        subsub.prop(con, "max_y", text="")
        row.prop_decorator(con, "max_y")

        row = col.row(heading="Z", align=True)
        row.use_property_decorate = False
        sub = row.row(align=True)
        sub.prop(con, "use_max_z", text="")
        subsub = sub.row(align=True)
        subsub.active = con.use_max_z
        subsub.prop(con, "max_z", text="")
        row.prop_decorator(con, "max_z")


        layout.prop(con, "use_transform_limit")
        layout.prop(con, "owner_space")

        self.draw_influence(self, layout, con)

    def COPY_ROTATION(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        self.target_template(self, layout, con)

        layout.prop(con, "euler_order", text="Order")

        row = layout.row(heading="Axis", align=True)
        row.use_property_decorate = False
        sub = row.row(align=True)
        sub.prop(con, "use_x", text="X", toggle=True)
        sub.prop(con, "use_y", text="Y", toggle=True)
        sub.prop(con, "use_z", text="Z", toggle=True)
        row.label(icon='BLANK1')

        row = layout.row(heading="Invert", align=True)
        row.use_property_decorate = False
        sub = row.row(align=True)
        sub.prop(con, "invert_x", text="X", toggle=True)
        sub.prop(con, "invert_y", text="Y", toggle=True)
        sub.prop(con, "invert_z", text="Z", toggle=True)
        row.label(icon='BLANK1')

        layout.prop(con, "mix_mode", text="Mix")

        self.space_template(self, layout, con)

        self.draw_influence(self, layout, con)

    def COPY_LOCATION(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        self.target_template(self, layout, con)

        row = layout.row(heading="Axis", align=True)
        row.use_property_decorate = False
        sub = row.row(align=True)
        sub.prop(con, "use_x", text="X", toggle=True)
        sub.prop(con, "use_y", text="Y", toggle=True)
        sub.prop(con, "use_z", text="Z", toggle=True)
        row.label(icon='BLANK1')

        row = layout.row(heading="Invert", align=True)
        row.use_property_decorate = False
        sub = row.row(align=True)
        sub.prop(con, "invert_x", text="X", toggle=True)
        sub.prop(con, "invert_y", text="Y", toggle=True)
        sub.prop(con, "invert_z", text="Z", toggle=True)
        row.label(icon='BLANK1')

        layout.prop(con, "use_offset")

        self.space_template(self, layout, con)

        self.draw_influence(self, layout, con)

    def COPY_SCALE(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        self.target_template(self, layout, con)

        row = layout.row(heading="Axis", align=True)
        row.use_property_decorate = False
        sub = row.row(align=True)
        sub.prop(con, "use_x", text="X", toggle=True)
        sub.prop(con, "use_y", text="Y", toggle=True)
        sub.prop(con, "use_z", text="Z", toggle=True)
        row.label(icon='BLANK1')

        col = layout.column()
        col.prop(con, "power")
        col.prop(con, "use_make_uniform")

        col.prop(con, "use_offset")
        row = col.row()
        row.active = con.use_offset
        row.prop(con, "use_add")

        self.space_template(self, layout, con)

        self.draw_influence(self, layout, con)

    def MAINTAIN_VOLUME(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        layout.prop(con, "mode")

        row = layout.row(heading="Free Axis")
        row.prop(con, "free_axis", expand=True)

        layout.prop(con, "volume")

        layout.prop(con, "owner_space")

        self.draw_influence(self, layout, con)

    def COPY_TRANSFORMS(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        self.target_template(self, layout, con)

        layout.prop(con, "mix_mode", text="Mix")

        self.space_template(self, layout, con)
        self.draw_influence(self, layout, con)

    def ACTION(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        self.target_template(self, layout, con)

        layout.prop(con, "mix_mode", text="Mix")

        self.draw_influence(self, layout, con)

    def LOCKED_TRACK(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        self.target_template(self, layout, con)

        layout.prop(con, "track_axis", expand=True)
        layout.prop(con, "lock_axis", expand=True)

        self.draw_influence(self, layout, con)

    def LIMIT_DISTANCE(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        self.target_template(self, layout, con)

        row = layout.row()
        row.prop(con, "distance")
        row.operator("constraint.limitdistance_reset", text="", icon="X")

        layout.prop(con, "limit_mode", text="Clamp Region")

        layout.prop(con, "use_transform_limit")

        self.space_template(self, layout, con)

        self.draw_influence(self, layout, con)

    def STRETCH_TO(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        self.target_template(self, layout, con)

        row = layout.row()
        row.prop(con, "rest_length")
        row.operator("constraint.stretchto_reset", text="", icon="X")

        layout.separator()

        col = layout.column()
        col.prop(con, "bulge", text="Volume Variation")

        row = col.row(heading="Volume Min", align=True)
        row.use_property_decorate = False
        sub = row.row(align=True)
        sub.prop(con, "use_bulge_min", text="")
        subsub = sub.row(align=True)
        subsub.active = con.use_bulge_min
        subsub.prop(con, "bulge_min", text="")
        row.prop_decorator(con, "bulge_min")

        row = col.row(heading="Max", align=True)
        row.use_property_decorate = False
        sub = row.row(align=True)
        sub.prop(con, "use_bulge_max", text="")
        subsub = sub.row(align=True)
        subsub.active = con.use_bulge_max
        subsub.prop(con, "bulge_max", text="")
        row.prop_decorator(con, "bulge_max")

        row = col.row()
        row.active = con.use_bulge_min or con.use_bulge_max
        row.prop(con, "bulge_smooth", text="Smooth")

        layout.prop(con, "volume", expand=True)
        layout.prop(con, "keep_axis", text="Rotation", expand=True)

        self.draw_influence(self, layout, con)

    def MIN_MAX(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        self.target_template(self, layout, con)

        layout.prop(con, "offset")
        layout.prop(con, "floor_location", expand=True, text="Min/Max")
        layout.prop(con, "use_rotation")

        self.space_template(self, layout, con)

        self.draw_influence(self, layout, con)

    def CLAMP_TO(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        self.target_template(self, layout, con)

        row = layout.row(align=True)
        row.prop(con, "main_axis", expand=True)

        layout.prop(con, "use_cyclic")

        self.draw_influence(self, layout, con)

    def TRANSFORM(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        self.target_template(self, layout, con)

        layout.prop(con, "use_motion_extrapolate", text="Extrapolate")

        self.space_template(self, layout, con)

        self.draw_influence(self, layout, con)

        layout.use_property_split = False
        pref = get_preferences().modifier
        layout.prop(pref, "transformation_map", text="Map From")
        if get_preferences().modifier.transformation_map:
            layout.use_property_split = True

            layout.prop(con, "map_from", expand=True)

            layout.use_property_split = True
            layout.use_property_decorate = True

            from_axes = [con.map_to_x_from, con.map_to_y_from, con.map_to_z_from]

            if con.map_from == 'ROTATION':
                layout.prop(con, "from_rotation_mode", text="Mode")

            ext = "" if con.map_from == 'LOCATION' else "_rot" if con.map_from == 'ROTATION' else "_scale"

            col = layout.column(align=True)
            col.active = "X" in from_axes
            col.prop(con, "from_min_x" + ext, text="X Min")
            col.prop(con, "from_max_x" + ext, text="Max")

            col = layout.column(align=True)
            col.active = "Y" in from_axes
            col.prop(con, "from_min_y" + ext, text="Y Min")
            col.prop(con, "from_max_y" + ext, text="Max")

            col = layout.column(align=True)
            col.active = "Z" in from_axes
            col.prop(con, "from_min_z" + ext, text="Z Min")
            col.prop(con, "from_max_z" + ext, text="Max")

        layout.use_property_split = False
        pref = get_preferences().modifier
        layout.prop(pref, "transformation_to", text="Map TO")
        if get_preferences().modifier.transformation_to:
            layout.use_property_split = True

            layout.prop(con, "map_to", expand=True)

            layout.use_property_split = True
            layout.use_property_decorate = True

            if con.map_to == 'ROTATION':
                layout.prop(con, "to_euler_order", text="Order")

            ext = "" if con.map_to == 'LOCATION' else "_rot" if con.map_to == 'ROTATION' else "_scale"

            col = layout.column(align=True)
            col.prop(con, "map_to_x_from", expand=False, text="X Source Axis")
            col.prop(con, "to_min_x" + ext, text="Min")
            col.prop(con, "to_max_x" + ext, text="Max")

            col = layout.column(align=True)
            col.prop(con, "map_to_y_from", expand=False, text="Y Source Axis")
            col.prop(con, "to_min_y" + ext, text="Min")
            col.prop(con, "to_max_y" + ext, text="Max")

            col = layout.column(align=True)
            col.prop(con, "map_to_z_from", expand=False, text="Z Source Axis")
            col.prop(con, "to_min_z" + ext, text="Min")
            col.prop(con, "to_max_z" + ext, text="Max")

            layout.prop(con, "mix_mode" + ext, text="Mix")

    def SHRINKWRAP(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        self.target_template(layout, con, False)

        layout.prop(con, "distance")
        layout.prop(con, "shrinkwrap_type", text="Mode")

        layout.separator()

        if con.shrinkwrap_type == 'PROJECT':
            layout.prop(con, "project_axis", expand=True, text="Project Axis")
            layout.prop(con, "project_axis_space", text="Space")
            layout.prop(con, "project_limit", text="Distance")
            layout.prop(con, "use_project_opposite")

            layout.separator()

            col = layout.column()
            row = col.row()
            row.prop(con, "cull_face", expand=True)
            row = col.row()
            row.active = con.use_project_opposite and con.cull_face != 'OFF'
            row.prop(con, "use_invert_cull")

            layout.separator()

        if con.shrinkwrap_type in {'PROJECT', 'NEAREST_SURFACE', 'TARGET_PROJECT'}:
            layout.prop(con, "wrap_mode", text="Snap Mode")
            row = layout.row(heading="Align to Normal", align=True)
            row.use_property_decorate = False
            sub = row.row(align=True)
            sub.prop(con, "use_track_normal", text="")
            subsub = sub.row(align=True)
            subsub.active = con.use_track_normal
            subsub.prop(con, "track_axis", text="")
            row.prop_decorator(con, "track_axis")

        self.draw_influence(self, layout, con)

    def DAMPED_TRACK(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        self.target_template(self, layout, con)

        layout.prop(con, "track_axis", expand=True)

        self.draw_influence(self, layout, con)

    def SPLINE_IK(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        self.target_template(self, layout, con)

        self.draw_influence(self, layout, con)

    def PIVOT(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        self.target_template(self, layout, con)

        if con.target:
            layout.prop(con, "offset", text="Pivot Offset")
        else:
            layout.prop(con, "use_relative_location")
            if con.use_relative_location:
                layout.prop(con, "offset", text="Pivot Point")
            else:
                layout.prop(con, "offset", text="Pivot Point")

        col = layout.column()
        col.prop(con, "rotation_range", text="Rotation Range")

        self.draw_influence(self, layout, con)

    def FOLLOW_TRACK(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        clip = None
        if con.use_active_clip:
            clip = context.scene.active_clip
        else:
            clip = con.clip

        layout.prop(con, "use_active_clip")
        layout.prop(con, "use_3d_position")

        row = layout.row()
        row.active = not con.use_3d_position
        row.prop(con, "use_undistorted_position")


        if not con.use_active_clip:
            layout.prop(con, "clip")

        layout.prop(con, "frame_method")

        if clip:
            tracking = clip.tracking

            layout.prop_search(con, "object", tracking, "objects", icon='OBJECT_DATA')

            tracking_object = tracking.objects.get(con.object, tracking.objects[0])

            layout.prop_search(con, "track", tracking_object, "tracks", icon='ANIM_DATA')

        layout.prop(con, "camera")

        row = layout.row()
        row.active = not con.use_3d_position
        row.prop(con, "depth_object")

        layout.operator("clip.constraint_to_fcurve")

        self.draw_influence(self, layout, con)

    def CAMERA_SOLVER(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        layout.prop(con, "use_active_clip")

        if not con.use_active_clip:
            layout.prop(con, "clip")

        layout.operator("clip.constraint_to_fcurve")

        self.draw_influence(self, layout, con)

    def OBJECT_SOLVER(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        clip = None
        if con.use_active_clip:
            clip = context.scene.active_clip
        else:
            clip = con.clip

        layout.prop(con, "use_active_clip")

        if not con.use_active_clip:
            layout.prop(con, "clip")

        if clip:
            layout.prop_search(con, "object", clip.tracking, "objects", icon='OBJECT_DATA')

        layout.prop(con, "camera")

        row = layout.row()
        row.operator("constraint.objectsolver_set_inverse")
        row.operator("constraint.objectsolver_clear_inverse")

        layout.operator("clip.constraint_to_fcurve")

        self.draw_influence(self, layout, con)

    def TRANSFORM_CACHE(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        layout.template_cache_file(con, "cache_file")

        cache_file = con.cache_file

        if cache_file is not None:
            layout.prop_search(con, "object_path", cache_file, "object_paths")

        self.draw_influence(self, layout, con)

    def PYTHON_CONSTRAINT(self, context, layout, con):

        layout.label(text="Blender 2.6 doesn't support python constraints yet")

    def ARMATURE(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        col = layout.column()
        col.prop(con, "use_deform_preserve_volume")
        col.prop(con, "use_bone_envelopes")

        if context.pose_bone:
            col.prop(con, "use_current_location")

        layout.operator("constraint.add_target", text="Add Target Bone")

        layout.operator("constraint.normalize_target_weights")

        self.draw_influence(self, layout, con)

        if not con.targets:
            layout.label(text="No target bones added", icon='ERROR')

    def KINEMATIC(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        self.target_template(self, layout, con)

        if context.object.pose.ik_solver == 'ITASC':
            layout.prop(con, "ik_type")

            # This button gives itself too much padding, so put it in a column with the subtarget
            col = layout.column()
            col.prop(con, "pole_target")

            if con.pole_target and con.pole_target.type == 'ARMATURE':
                col.prop_search(con, "pole_subtarget", con.pole_target.data, "bones", text="Bone")

            col = layout.column()
            if con.pole_target:
                col.prop(con, "pole_angle")
            col.prop(con, "use_tail")
            col.prop(con, "use_stretch")
            col.prop(con, "chain_count")

            if con.ik_type == 'COPY_POSE':
                layout.prop(con, "reference_axis", expand=True)

                # Use separate rows and columns here to avoid an alignment issue with the lock buttons
                loc_col = layout.column()
                loc_col.prop(con, "use_location")

                row = loc_col.row()
                row.active = con.use_location
                row.prop(con, "weight", text="Weight", slider=True)

                row = loc_col.row(heading="Lock", align=True)
                row.use_property_decorate = False
                row.active = con.use_location
                sub = row.row(align=True)
                sub.prop(con, "lock_location_x", text="X", toggle=True)
                sub.prop(con, "lock_location_y", text="Y", toggle=True)
                sub.prop(con, "lock_location_z", text="Z", toggle=True)
                row.label(icon='BLANK1')

                rot_col = layout.column()
                rot_col.prop(con, "use_rotation")

                row = rot_col.row()
                row.active = con.use_rotation
                row.prop(con, "orient_weight", text="Weight", slider=True)

                row = rot_col.row(heading="Lock", align=True)
                row.use_property_decorate = False
                row.active = con.use_rotation
                sub = row.row(align=True)
                sub.prop(con, "lock_rotation_x", text="X", toggle=True)
                sub.prop(con, "lock_rotation_y", text="Y", toggle=True)
                sub.prop(con, "lock_rotation_z", text="Z", toggle=True)
                row.label(icon='BLANK1')

            elif con.ik_type == 'DISTANCE':
                layout.prop(con, "limit_mode")

                col = layout.column()
                col.prop(con, "weight", text="Weight", slider=True)
                col.prop(con, "distance", text="Distance", slider=True)
        else:
            # Standard IK constraint
            col = layout.column()
            col.prop(con, "pole_target")

            if con.pole_target and con.pole_target.type == 'ARMATURE':
                col.prop_search(con, "pole_subtarget", con.pole_target.data, "bones", text="Bone")

            col = layout.column()
            if con.pole_target:
                col.prop(con, "pole_angle")
            col.prop(con, "iterations")
            col.prop(con, "chain_count")
            col.prop(con, "use_tail")
            col.prop(con, "use_stretch")

            col = layout.column()
            row = col.row(align=True, heading="Weight Position")
            row.prop(con, "use_location", text="")
            sub = row.row(align=True)
            sub.active = con.use_location
            sub.prop(con, "weight", text="", slider=True)

            row = col.row(align=True, heading="Rotation")
            row.prop(con, "use_rotation", text="")
            sub = row.row(align=True)
            sub.active = con.use_rotation
            sub.prop(con, "orient_weight", text="", slider=True)

        self.draw_influence(self, layout, con)


# Parent class for constraint subpanels
class ConstraintButtonsSubPanel(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = ""
    bl_options = {'DRAW_BOX'}

    def get_constraint(self, context, layout, con):
        self.layout.context_pointer_set("constraint", con)
        return con

    def draw_transform_from(self, context, layout, con):


        layout.prop(con, "map_from", expand=True)

        layout.use_property_split = True
        layout.use_property_decorate = True

        from_axes = [con.map_to_x_from, con.map_to_y_from, con.map_to_z_from]

        if con.map_from == 'ROTATION':
            layout.prop(con, "from_rotation_mode", text="Mode")

        ext = "" if con.map_from == 'LOCATION' else "_rot" if con.map_from == 'ROTATION' else "_scale"

        col = layout.column(align=True)
        col.active = "X" in from_axes
        col.prop(con, "from_min_x" + ext, text="X Min")
        col.prop(con, "from_max_x" + ext, text="Max")

        col = layout.column(align=True)
        col.active = "Y" in from_axes
        col.prop(con, "from_min_y" + ext, text="Y Min")
        col.prop(con, "from_max_y" + ext, text="Max")

        col = layout.column(align=True)
        col.active = "Z" in from_axes
        col.prop(con, "from_min_z" + ext, text="Z Min")
        col.prop(con, "from_max_z" + ext, text="Max")

    def draw_transform_to(self, context, layout, con):


        layout.prop(con, "map_to", expand=True)

        layout.use_property_split = True
        layout.use_property_decorate = True

        if con.map_to == 'ROTATION':
            layout.prop(con, "to_euler_order", text="Order")

        ext = "" if con.map_to == 'LOCATION' else "_rot" if con.map_to == 'ROTATION' else "_scale"

        col = layout.column(align=True)
        col.prop(con, "map_to_x_from", expand=False, text="X Source Axis")
        col.prop(con, "to_min_x" + ext, text="Min")
        col.prop(con, "to_max_x" + ext, text="Max")

        col = layout.column(align=True)
        col.prop(con, "map_to_y_from", expand=False, text="Y Source Axis")
        col.prop(con, "to_min_y" + ext, text="Min")
        col.prop(con, "to_max_y" + ext, text="Max")

        col = layout.column(align=True)
        col.prop(con, "map_to_z_from", expand=False, text="Z Source Axis")
        col.prop(con, "to_min_z" + ext, text="Min")
        col.prop(con, "to_max_z" + ext, text="Max")      

        layout.prop(con, "mix_mode" + ext, text="Mix")

    def draw_armature_bones(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        for i, tgt in enumerate(con.targets):
            has_target = tgt.target is not None

            box = layout.box()
            header = box.row()
            header.use_property_split = False

            split = header.split(factor=0.45, align=True)
            split.prop(tgt, "target", text="")

            row = split.row(align=True)
            row.active = has_target
            if has_target:
                row.prop_search(tgt, "subtarget", tgt.target.data, "bones", text="")
            else:
                row.prop(tgt, "subtarget", text="", icon='BONE_DATA')

            header.operator("constraint.remove_target", text="", icon='X').index = i

            row = box.row()
            row.active = has_target and tgt.subtarget != ""
            row.prop(tgt, "weight", slider=True, text="Weight")

    def draw_spline_ik_fitting(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        col = layout.column()
        col.prop(con, "chain_count")
        col.prop(con, "use_even_divisions")
        col.prop(con, "use_chain_offset")

    def draw_spline_ik_chain_scaling(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        layout.prop(con, "use_curve_radius")

        layout.prop(con, "y_scale_mode")
        layout.prop(con, "xz_scale_mode")

        if con.xz_scale_mode in {'INVERSE_PRESERVE', 'VOLUME_PRESERVE'}:
            layout.prop(con, "use_original_scale")

        if con.xz_scale_mode == 'VOLUME_PRESERVE':
            col = layout.column()
            col.prop(con, "bulge", text="Volume Variation")

            row = col.row(heading="Volume Min")
            row.prop(con, "use_bulge_min", text="")
            sub = row.row()
            sub.active = con.use_bulge_min
            sub.prop(con, "bulge_min", text="")

            row = col.row(heading="Max")
            row.prop(con, "use_bulge_max", text="")
            sub = row.row()
            sub.active = con.use_bulge_max
            sub.prop(con, "bulge_max", text="")

            row = layout.row()
            row.active = con.use_bulge_min or con.use_bulge_max
            row.prop(con, "bulge_smooth", text="Smooth")

    def draw_action_target(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        layout.prop(con, "transform_channel", text="Channel")
        layout.prop(con, "target_space")

        col = layout.column(align=True)
        col.prop(con, "min", text="Range Min")
        col.prop(con, "max", text="Max")


    def draw_action_action(self, context, layout, con):

        layout.use_property_split = True
        layout.use_property_decorate = True

        layout.prop(con, "action")
        layout.prop(con, "use_bone_object_action")

        col = layout.column(align=True)
        col.prop(con, "frame_start", text="Frame Start")
        col.prop(con, "frame_end", text="End")


