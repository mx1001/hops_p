import bpy
from bpy.types import Panel
from ... preferences import get_preferences

mods_dic = {
    'ARMATURE': 'MOD_ARMATURE',
    'ARRAY': 'MOD_ARRAY',
    'BEVEL': 'MOD_BEVEL',
    'BOOLEAN': 'MOD_BOOLEAN',
    'BUILD': 'MOD_BUILD',
    'MESH_CACHE': 'MOD_MESHDEFORM',
    'MESH_SEQUENCE_CACHE': 'MOD_MESHDEFORM',
    'CAST': 'MOD_CAST',
    'CLOTH': 'MOD_CLOTH',
    'COLLISION': 'MOD_PHYSICS',
    'CURVE': 'MOD_CURVE',
    'DECIMATE': 'MOD_DECIM',
    'DISPLACE': 'MOD_DISPLACE',
    'DYNAMIC_PAINT': 'MOD_DYNAMICPAINT',
    'EDGE_SPLIT': 'MOD_EDGESPLIT',
    'EXPLODE': 'MOD_EXPLODE',
    'FLUID_SIMULATION': 'MOD_FLUIDSIM',
    'HOOK': 'HOOK',
    'LAPLACIANDEFORM': 'MOD_MESHDEFORM',
    'LAPLACIANSMOOTH': 'MOD_SMOOTH',
    'LATTICE': 'MOD_LATTICE',
    'MASK': 'MOD_MASK',
    'MESH_DEFORM': 'MOD_MESHDEFORM',
    'MIRROR': 'MOD_MIRROR',
    'MULTIRES': 'MOD_MULTIRES',
    'OCEAN': 'MOD_OCEAN',
    'PARTICLE_INSTANCE': 'MOD_PARTICLE_INSTANCE',
    'PARTICLE_SYSTEM': 'PARTICLE_DATA',
    'SCREW': 'MOD_SCREW',
    'SHRINKWRAP': 'MOD_SHRINKWRAP',
    'SIMPLE_DEFORM': 'MOD_SIMPLEDEFORM',
    'FLUID': 'MOD_FLUID',
    'SMOOTH': 'MOD_SMOOTH',
    'SOFT_BODY': 'MOD_SOFT',
    'SOLIDIFY': 'MOD_SOLIDIFY',
    'SUBSURF': 'MOD_SUBSURF',
    'SURFACE': 'MOD_MESHDEFORM',
    'SURFACE_DEFORM': 'MOD_MESHDEFORM',
    'UV_PROJECT': 'MOD_UVPROJECT',
    'WARP': 'MOD_WARP',
    'WAVE': 'MOD_WAVE',
    'REMESH': 'MOD_REMESH',
    'VERTEX_WEIGHT_EDIT': 'MOD_VERTEX_WEIGHT',
    'VERTEX_WEIGHT_MIX': 'MOD_VERTEX_WEIGHT',
    'VERTEX_WEIGHT_PROXIMITY': 'MOD_VERTEX_WEIGHT',
    'SKIN': 'MOD_SKIN',
    'TRIANGULATE': 'MOD_TRIANGULATE',
    'UV_WARP': 'MOD_UVPROJECT',
    'WIREFRAME': 'MOD_WIREFRAME',
    'WELD': 'AUTOMERGE_OFF',
    'DATA_TRANSFER': 'MOD_DATA_TRANSFER',
    'NORMAL_EDIT': 'MOD_NORMALEDIT',
    'CORRECTIVE_SMOOTH': 'MOD_SMOOTH',
    'WEIGHTED_NORMAL': 'MOD_NORMALEDIT'
}


class ModifierButtonsPanel:
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "modifier"
    bl_options = {'HIDE_HEADER'}


class DATA_PT_modifiers(ModifierButtonsPanel, Panel):
    bl_label = "Modifiers"

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type != 'GPENCIL'

    def draw(self, context):
        layout = self.layout

        ob = context.object

        layout.operator_menu_enum("object.modifier_add", "type")

        for md in ob.modifiers:
            box = layout.template_modifiers()
            if box:
                # match enum type to our functions, avoids a lookup table.
                getattr(self, md.type)(box, ob, md)

    # the mt.type enum is (ab)used for a lookup on function names
    # ...to avoid lengthy if statements
    # so each type must have a function here.

    def ARMATURE(self, layout, ob, md):
        layout.use_property_split = True
        col = layout.column()
        col.separator()

        col.prop(md, "object")
        row = col.row()
        row.prop_search(md, "vertex_group", ob, "vertex_groups", text="Vertex Group")
        sub = row.row(align=True)
        sub.active = bool(md.vertex_group)
        sub.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')

        col.prop(md, "use_deform_preserve_volume")
        col.prop(md, "use_multi_modifier")

        row = col.row(heading='Bind to')
        row.prop(md, "use_vertex_groups", text="Vertex Groups")
        col.prop(md, "use_bone_envelopes", text="Bone Envelopes")

        layout.separator()

    def ARRAY(self, layout, _ob, md):
        layout.use_property_split = True

        col = layout.column()
        col.separator()

        col.prop(md, "fit_type")

        if md.fit_type == 'FIXED_COUNT':
            col.prop(md, "count")
        elif md.fit_type == 'FIT_LENGTH':
            col.prop(md, "fit_length")
        elif md.fit_type == 'FIT_CURVE':
            col.prop(md, "curve")

        col.separator()

        col.prop(md, "start_cap")
        col.prop(md, "end_cap")

        col.separator()

        col.use_property_split = False
        col.prop(md, "use_relative_offset", text="Relative")
        if md.use_relative_offset:
            col.use_property_split = True
            col.prop(md, "relative_offset_displace", text="Factor")

        col.use_property_split = False
        col.prop(md, "use_constant_offset", text="Constant")
        if md.use_constant_offset:
            col.use_property_split = True
            col.prop(md, "constant_offset_displace", text="Distance")

        col.use_property_split = False
        col.prop(md, "use_merge_vertices", text="Merge")
        if md.use_merge_vertices:
            col.use_property_split = True
            col.prop(md, "use_merge_vertices_cap", text="First Last")
            col.prop(md, "merge_threshold", text="Distance")

        col.use_property_split = False
        col.prop(md, "use_object_offset")
        if md.use_object_offset:
            col.use_property_split = True
            col.prop(md, "offset_object", text="Object")

        col.use_property_split = False
        pref = get_preferences().modifier
        col.prop(pref, "array1", text="UVs:")
        if get_preferences().modifier.array1:
            col.use_property_split = True
            col.prop(md, "offset_u")
            col.prop(md, "offset_v")
        col.separator()

    def BEVEL(self, layout, ob, md):
        offset_type = md.offset_type
        layout.use_property_split = True

        col = layout.column()
        col.separator()

        if offset_type == 'PERCENT':
            col.prop(md, "width_pct")
        else:
            offset_text = "Width"
            if offset_type == 'DEPTH':
                offset_text = "Depth"
            elif offset_type == 'OFFSET':
                offset_text = "Offset"
            col.prop(md, "width", text=offset_text)

        col.prop(md, "offset_type")
        col.prop(md, "segments")

        col.separator()

        if bpy.app.version < (2, 90, 0):
            col.row().prop(md, "use_only_vertices")
        else:
            col.row().prop(md, "affect", expand=True)

        col.separator()

        col.row().prop(md, "limit_method")
        if md.limit_method == 'ANGLE':
            col.prop(md, "angle_limit")
        elif md.limit_method == 'VGROUP':
            row = col.row()
            row.prop_search(md, "vertex_group", ob, "vertex_groups", text="Vertex Group")
            sub = row.row(align=True)
            sub.active = bool(md.vertex_group)
            sub.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')

        col.use_property_split = False
        pref = get_preferences().modifier
        col.prop(pref, "bevel1", text="Profile:")
        if get_preferences().modifier.bevel1:
            col.row().prop(md, "profile_type", expand = True)
            col.use_property_split = True

            if bpy.app.version < (2, 90, 0):
                col.row().prop(md, "use_custom_profile")
                row = col.row()
                row.enabled = md.use_custom_profile
                if md.use_custom_profile:
                    col.template_curveprofile(md, "custom_profile")
                    row2 = col.row(align=True)
                    op = row2.operator('hops.save_bevel_profile', text='Save Profile')
                    op.obj, op.mod = ob.name, md.name
                    op = row2.operator('hops.load_bevel_profile', text='Load Profile')
                    op.obj, op.mod = ob.name, md.name
            else:
                col.prop(md, "profile")
                if md.profile_type == 'CUSTOM':
                    col.template_curveprofile(md, "custom_profile")
                    row2 = col.row(align=True)
                    op = row2.operator('hops.save_bevel_profile', text='Save Profile')
                    op.obj, op.mod = ob.name, md.name
                    op = row2.operator('hops.load_bevel_profile', text='Load Profile')
                    op.obj, op.mod = ob.name, md.name

        col.use_property_split = False
        pref = get_preferences().modifier
        col.prop(pref, "bevel2", text="Geometry:")
        if get_preferences().modifier.bevel2:
            col.use_property_split = True
            col.row().prop(md, "miter_outer", text="Outer")
            col.row().prop(md, "miter_inner", text="Inner")
            if md.miter_inner in {'MITER_PATCH', 'MITER_ARC'}:
                col.row().prop(md, "spread")
            col.separator()

            col.row().prop(md, "vmesh_method")
            col.prop(md, "use_clamp_overlap")
            col.prop(md, "loop_slide")

        col.use_property_split = False
        pref = get_preferences().modifier
        col.prop(pref, "bevel3", text="Shading:")
        if get_preferences().modifier.bevel3:
            col.use_property_split = True
            col.prop(md, "harden_normals")
            col.separator()
            col.prop(md, "mark_seam")
            col.prop(md, "mark_sharp")
            col.prop(md, "material")
            col.prop(md, "face_strength_mode")
        col.separator()

    def BOOLEAN(self, layout, _ob, md):
        layout.use_property_split = True
        col = layout.column()
        col.separator()

        col.prop(md, "operation")
        col.prop(md, "object")
        col.prop(md, "double_threshold")

        if bpy.app.debug:
            layout.prop(md, "debug_options")

        col.separator()

    def BUILD(self, layout, _ob, md):
        layout.use_property_split = True
        col = layout.column()
        col.separator()

        col.prop(md, "frame_start")
        col.prop(md, "frame_duration")
        col.prop(md, "use_reverse")

        col.separator()

        col.prop(md, "use_random_order")
        row = col.row()
        row.active = md.use_random_order
        row.prop(md, "seed")

    def MESH_CACHE(self, layout, _ob, md):
        layout.prop(md, "cache_format")
        layout.prop(md, "filepath")

        if md.cache_format == 'ABC':
            layout.prop(md, "sub_object")

        layout.label(text="Evaluation:")
        layout.prop(md, "factor", slider=True)
        layout.prop(md, "deform_mode")
        layout.prop(md, "interpolation")

        layout.label(text="Time Mapping:")

        row = layout.row()
        row.prop(md, "time_mode", expand=True)
        row = layout.row()
        row.prop(md, "play_mode", expand=True)
        if md.play_mode == 'SCENE':
            layout.prop(md, "frame_start")
            layout.prop(md, "frame_scale")
        else:
            time_mode = md.time_mode
            if time_mode == 'FRAME':
                layout.prop(md, "eval_frame")
            elif time_mode == 'TIME':
                layout.prop(md, "eval_time")
            elif time_mode == 'FACTOR':
                layout.prop(md, "eval_factor")

        layout.label(text="Axis Mapping:")
        split = layout.split(factor=0.5, align=True)
        split.alert = (md.forward_axis[-1] == md.up_axis[-1])
        split.label(text="Forward/Up Axis:")
        split.prop(md, "forward_axis", text="")
        split.prop(md, "up_axis", text="")
        split = layout.split(factor=0.5)
        split.label(text="Flip Axis:")
        row = split.row()
        row.prop(md, "flip_axis")

    def MESH_SEQUENCE_CACHE(self, layout, ob, md):
        layout.label(text="Cache File Properties:")
        box = layout.box()
        box.template_cache_file(md, "cache_file")

        cache_file = md.cache_file

        layout.label(text="Modifier Properties:")
        box = layout.box()

        if cache_file is not None:
            box.prop_search(md, "object_path", cache_file, "object_paths")

        if ob.type == 'MESH':
            box.row().prop(md, "read_data")

    def CAST(self, layout, ob, md):
        layout.use_property_split = True
        col = layout.column()
        col.separator()

        col.prop(md, "cast_type")
        row = col.row(align=True, heading='Axis')
        row.prop(md, "use_x", toggle=True)
        row.prop(md, "use_y", toggle=True)
        row.prop(md, "use_z", toggle=True)

        col.prop(md, "factor")
        col.prop(md, "radius")
        col.prop(md, "size")
        col.prop(md, "use_radius_as_size")


        row = col.row()
        row.prop_search(md, "vertex_group", ob, "vertex_groups", text="Vertex Group")
        row.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')
        col.prop(md, "object", text="Object")
        if md.object:
            col.prop(md, "use_transform")

    def CLOTH(self, layout, _ob, _md):
        layout.label(text="Settings are inside the Physics tab")

    def COLLISION(self, layout, _ob, _md):
        layout.label(text="Settings are inside the Physics tab")

    def CURVE(self, layout, ob, md):
        layout.use_property_split = True
        col = layout.column()
        col.separator()

        col.prop(md, "object")
        col.row().prop(md, "deform_axis")
        row = col.row()
        row.prop_search(md, "vertex_group", ob, "vertex_groups", text="Vertex Group")
        row.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')

    def DECIMATE(self, layout, ob, md):
        decimate_type = md.decimate_type

        layout.use_property_split = True
        col = layout.column()
        col.separator()

        col.prop(md, "decimate_type")

        if decimate_type == 'COLLAPSE':
            col.prop(md, "ratio")

            row = col.row(heading='Symmetry')
            row.prop(md, "use_symmetry", text="")
            row.prop(md, "symmetry_axis", expand=True)

            col.prop(md, "use_collapse_triangulate")

            row = col.row()
            row.prop_search(md, "vertex_group", ob, "vertex_groups", text="Vertex Group")
            sub = row.row(align=True)
            sub.active = bool(md.vertex_group)
            sub.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')
            col.prop(md, "vertex_group_factor")

        elif decimate_type == 'UNSUBDIV':
            col.prop(md, "iterations")

        else:
            col.prop(md, "angle_limit")
            col.prop(md, "delimit", expand=True)
            col.prop(md, "use_dissolve_boundaries")

        col.separator()
        col.label(text=f'Face Count: {md.face_count}')

    def DISPLACE(self, layout, ob, md):
        has_texture = (md.texture is not None)

        layout.use_property_split = True
        col = layout.column()
        col.separator()

        col.template_ID(md, "texture", new="texture.new")
        row = col.row()
        row.active = has_texture
        row.prop(md, "texture_coords", text='Coordinates')
        if md.texture_coords == 'OBJECT':
            col.prop(md, "texture_coords_object")
            obj = md.texture_coords_object
            if obj and obj.type == 'ARMATURE':
                col.prop_search(md, "texture_coords_bone", obj.data, "bones", text="Bone")
        elif md.texture_coords == 'UV' and ob.type == 'MESH':
            col.prop_search(md, "uv_layer", ob.data, "uv_layers", text="UV map")

        col.separator()
        col.prop(md, "direction")
        if md.direction in {'X', 'Y', 'Z', 'RGB_TO_XYZ'}:
            col.prop(md, "space")
        col.separator()

        col.prop(md, "mid_level")
        col.prop(md, "strength")
        row = col.row()
        row.prop_search(md, "vertex_group", ob, "vertex_groups", text="Vertex Group")
        sub = row.row(align=True)
        sub.active = bool(md.vertex_group)
        sub.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')

    def DYNAMIC_PAINT(self, layout, _ob, _md):
        layout.label(text="Settings are inside the Physics tab")

    def EDGE_SPLIT(self, layout, _ob, md):
        layout.use_property_split = True
        col = layout.column()
        col.separator()

        row = col.row(align=True, heading='Edge Angle')
        row.prop(md, "use_edge_angle", text="")
        row.prop(md, "split_angle")
        col.prop(md, "use_edge_sharp", text="Sharp Edges")

    def EXPLODE(self, layout, ob, md):
        split = layout.split()

        col = split.column()
        col.label(text="Vertex Group:")
        row = col.row(align=True)
        row.prop_search(md, "vertex_group", ob, "vertex_groups", text="")
        row.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')
        sub = col.column()
        sub.active = bool(md.vertex_group)
        sub.prop(md, "protect")
        col.label(text="Particle UV")
        col.prop_search(md, "particle_uv", ob.data, "uv_layers", text="")

        col = split.column()
        col.prop(md, "use_edge_cut")
        col.prop(md, "show_unborn")
        col.prop(md, "show_alive")
        col.prop(md, "show_dead")
        col.prop(md, "use_size")

        layout.operator("object.explode_refresh", text="Refresh")

    def FLUID_SIMULATION(self, layout, _ob, _md):
        layout.label(text="Settings are inside the Physics tab")

    def HOOK(self, layout, ob, md):
        use_falloff = (md.falloff_type != 'NONE')

        layout.use_property_split = True
        col = layout.column()
        col.separator()

        col.prop(md, "object")
        if md.object and md.object.type == 'ARMATURE':
            col.prop_search(md, "subtarget", md.object.data, "bones", text="Bone")
        row = col.row()
        row.prop_search(md, "vertex_group", ob, "vertex_groups", text="Vertex Group")
        row.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')
        col.prop(md, "strength", slider=True)

        if ob.mode == 'EDIT':
            row = col.row(align=True)
            row.operator("object.hook_reset", text="Reset")
            row.operator("object.hook_recenter", text="Recenter")

            row = col.row(align=True)
            row.operator("object.hook_select", text="Select")
            row.operator("object.hook_assign", text="Assign")

        col.use_property_split = False
        pref = get_preferences().modifier
        col.prop(pref, "hook_falloff", text="Falloff")
        if pref.hook_falloff:
            col.use_property_split = True

            col.prop(md, "falloff_type")
            col.prop(md, "falloff_radius")

            if use_falloff:
                if md.falloff_type == 'CURVE':
                    col.template_curve_mapping(md, "falloff_curve")

            col.prop(md, "use_falloff_uniform")


    def LAPLACIANDEFORM(self, layout, ob, md):
        is_bind = md.is_bind

        layout.use_property_split = True
        col = layout.column()
        col.separator()

        col.prop(md, "iterations")

        row = col.row()
        row.enabled = not is_bind
        row.prop_search(md, "vertex_group", ob, "vertex_groups", text="Vertex Group")
        row.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')

        col.separator()

        row = col.row()
        row.enabled = bool(md.vertex_group)
        row.operator("object.laplaciandeform_bind", text="Unbind" if is_bind else "Bind").modifier = md.name

    def LAPLACIANSMOOTH(self, layout, ob, md):
        layout.use_property_split = True
        col = layout.column()
        col.separator()

        col.prop(md, "iterations")

        row = col.row(align=True, heading='Axis')
        row.prop(md, "use_x", toggle=True)
        row.prop(md, "use_y", toggle=True)
        row.prop(md, "use_z", toggle=True)

        col.prop(md, "lambda_factor")
        col.prop(md, "lambda_border")

        col.prop(md, "use_volume_preserve")
        col.prop(md, "use_normalized")

        row = col.row()
        row.prop_search(md, "vertex_group", ob, "vertex_groups", text="Vertex Group")
        row.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')

    def LATTICE(self, layout, ob, md):
        layout.use_property_split = True
        col = layout.column()
        col.separator()

        col.prop(md, "object")
        row = col.row()
        row.prop_search(md, "vertex_group", ob, "vertex_groups", text="Vertex Group")
        row.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')
        col.prop(md, "strength", slider=True)

    def MASK(self, layout, ob, md):
        layout.use_property_split = True
        col = layout.column()
        col.separator()

        row = col.row(align=True)
        row.prop(md, "mode", expand=True)

        if md.mode == 'ARMATURE':
            row = col.row()
            row.prop(md, "armature", text="Armature")
            sub = row.row(align=True)
            sub.active = bool(md.vertex_group)
            sub.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')
        elif md.mode == 'VERTEX_GROUP':
            row = col.row()
            row.prop_search(md, "vertex_group", ob, "vertex_groups", text="Vertex Group")
            sub = row.row(align=True)
            sub.active = bool(md.vertex_group)
            sub.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')

        col.use_property_split = True
        col.prop(md, "threshold")

    def MESH_DEFORM(self, layout, ob, md):
        is_bind = md.is_bound
        layout.use_property_split = True
        col = layout.column()
        col.separator()

        col.prop(md, "object")
        row = col.row()
        row.prop_search(md, "vertex_group", ob, "vertex_groups", text="Vertex Group")
        sub = row.row(align=True)
        sub.active = bool(md.vertex_group)
        sub.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')
        col.prop(md, "precision")
        col.prop(md, "use_dynamic_bind")

        layout.separator()
        layout.operator("object.meshdeform_bind", text="Unbind" if is_bind else "Bind").modifier = md.name


    def MIRROR(self, layout, _ob, md):
        axis_text = "XYZ"
        layout.use_property_split = True

        col = layout.column(align=True)
        col.separator()

        row = col.row(heading="Axis")
        for i, text in enumerate(axis_text):
            row.prop(md, "use_axis", text=text, index=i, toggle=True)

        row = col.row(heading="Bisect")
        for i, text in enumerate(axis_text):
            row.prop(md, "use_bisect_axis", text=text, index=i, toggle=True)

        row = col.row(heading="Flip")
        for i, text in enumerate(axis_text):
            row.prop(md, "use_bisect_flip_axis", text=text, index=i, toggle=True)

        layout.separator()

        col = layout.column()
        col.prop(md, "mirror_object", text="Mirror Object")
        col.prop(md, "use_clip", text="Clipping")
        row = col.row()

        row = col.row(heading="Merge")
        row.prop(md, "use_mirror_merge", text="")
        row.active = md.use_mirror_merge
        row.prop(md, "merge_threshold", text="")


        col.use_property_split = False
        pref = get_preferences().modifier
        col.prop(pref, "mirrordata", text="Data:")
        if get_preferences().modifier.mirrordata:
            col.use_property_split = True

            col.prop(md, "offset_u", text="Offset U")
            col.prop(md, "offset_v", text="V")

            row = col.row(align=True, heading="Mirror U")
            row.prop(md, "use_mirror_u", text="")
            row.active = md.use_mirror_u
            row.prop(md, "mirror_offset_u", text="")

            row = col.row(align=True, heading="V")
            row.prop(md, "use_mirror_v", text="")
            row.active = md.use_mirror_v
            row.prop(md, "mirror_offset_v", text="")

            col.prop(md, "use_mirror_vertex_groups", text="Vertex Groups")
            col.prop(md, "use_mirror_udim", text="Flip UDIM")

        col.separator()

    def MULTIRES(self, layout, ob, md):
        # Changing some of the properties can not be done once there is an
        # actual displacement stored for this multires modifier. This check
        # will disallow those properties from change.
        # This is a bit stupid check but should be sufficient for the usual
        # multires usage. It might become less strict and only disallow
        # modifications if there is CD_MDISPS layer, or if there is actual
        # non-zero displacement but such checks will be too slow to be done
        # on every redraw.

        layout.use_property_split = True
        col = layout.column(align=True)
        col.separator()

        col.prop(md, "subdivision_type", text='Subdivision Type')

        col.prop(md, "sculpt_levels", text="Levels Sculpt")
        col.prop(md, "levels", text="Viewport")
        col.prop(md, "render_levels", text="Render")
        col.prop(md, "show_only_control_edges", text="Optimal Display")

        col.separator()
        split = col.split()
        col2 = split.column()

        op1 = col2.operator("object.multires_unsubdivide", text="Unsubdivide")
        op1.modifier = md.name
        col2.label(text='')
        op2 = col2.operator("object.multires_reshape", text="Reshape")
        op2.modifier = md.name

        col2 = split.column()
        row2 = col2.row(align=True)

        op3 = row2.operator("object.multires_subdivide", text="Subdivide")
        op3.modifier = md.name
        op3.mode = 'CATMULL_CLARK'
        op4 = row2.operator("object.multires_subdivide", text="Simple")
        op4.modifier = md.name
        op4.mode = 'SIMPLE'
        op5 = row2.operator("object.multires_subdivide", text="Linear")
        op5.modifier = md.name
        op5.mode = 'LINEAR'

        op6 = col2.operator("object.multires_higher_levels_delete", text="Delete Higher")
        op6.modifier = md.name
        op7 = col2.operator("object.multires_base_apply", text="Apply Base")
        op7.modifier = md.name

        col.separator()

        # if md.total_levels == 0:
        #     col.operator("object.multires_rebuild_subdiv", text="Rebuild Subdivisions")
        #     col.separator()

        # if md.is_external:
        #     col.operator("object.multires_external_pack", text="Pack External")
        #     col.prop(md, "filepath", text="")
        # else:
        #     col.operator_context = "INVOKE_DEFAULT"
        #     col.operator("object.multires_external_save", text="Save External...")

        # col.separator()

        col.use_property_split = False
        pref = get_preferences().modifier
        col.prop(pref, "multires_advanced", text="Advenced:")
        if get_preferences().modifier.multires_advanced:
            col.use_property_split = True

            col.prop(md, "quality")
            col.prop(md, "uv_smooth", text="UV Smooth")
            col.prop(md, "use_creases")

    def OCEAN(self, layout, _ob, md):
        if not bpy.app.build_options.mod_oceansim:
            layout.label(text="Built without OceanSim modifier")
            return

        layout.prop(md, "geometry_mode")

        if md.geometry_mode == 'GENERATE':
            row = layout.row()
            row.prop(md, "repeat_x")
            row.prop(md, "repeat_y")

        layout.separator()

        split = layout.split()

        col = split.column()
        col.prop(md, "time")
        col.prop(md, "depth")
        col.prop(md, "random_seed")

        col = split.column()
        col.prop(md, "resolution")
        col.prop(md, "size")
        col.prop(md, "spatial_size")

        layout.separator()

        layout.prop(md, "spectrum")

        if md.spectrum in {'TEXEL_MARSEN_ARSLOE', 'JONSWAP'}:
            split = layout.split()

            col = split.column()
            col.prop(md, "sharpen_peak_jonswap")

            col = split.column()
            col.prop(md, "fetch_jonswap")

        layout.label(text="Waves:")

        split = layout.split()

        col = split.column()
        col.prop(md, "choppiness")
        col.prop(md, "wave_scale", text="Scale")
        col.prop(md, "wave_scale_min")
        col.prop(md, "wind_velocity")

        col = split.column()
        col.prop(md, "wave_alignment", text="Alignment")
        sub = col.column()
        sub.active = (md.wave_alignment > 0.0)
        sub.prop(md, "wave_direction", text="Direction")
        sub.prop(md, "damping")

        layout.separator()

        layout.prop(md, "use_normals")

        split = layout.split()

        col = split.column()
        col.prop(md, "use_foam")
        sub = col.row()
        sub.active = md.use_foam
        sub.prop(md, "foam_coverage", text="Coverage")

        col = split.column()
        col.active = md.use_foam
        col.label(text="Foam Data Layer Name:")
        col.prop(md, "foam_layer_name", text="")

        layout.separator()

        if md.is_cached:
            layout.operator("object.ocean_bake", text="Delete Bake").free = True
        else:
            layout.operator("object.ocean_bake").free = False

        split = layout.split()
        split.enabled = not md.is_cached

        col = split.column(align=True)
        col.prop(md, "frame_start", text="Start")
        col.prop(md, "frame_end", text="End")

        col = split.column(align=True)
        col.label(text="Cache path:")
        col.prop(md, "filepath", text="")

        split = layout.split()
        split.enabled = not md.is_cached

        col = split.column()
        col.active = md.use_foam
        col.prop(md, "bake_foam_fade")

        col = split.column()

    def PARTICLE_INSTANCE(self, layout, ob, md):
        layout.prop(md, "object")
        if md.object:
            layout.prop_search(md, "particle_system", md.object, "particle_systems", text="Particle System")
        else:
            layout.prop(md, "particle_system_index", text="Particle System")

        split = layout.split()
        col = split.column()
        col.label(text="Create From:")
        layout.prop(md, "space", text="")
        col.prop(md, "use_normal")
        col.prop(md, "use_children")
        col.prop(md, "use_size")

        col = split.column()
        col.label(text="Show Particles When:")
        col.prop(md, "show_alive")
        col.prop(md, "show_unborn")
        col.prop(md, "show_dead")

        row = layout.row(align=True)
        row.prop(md, "particle_amount", text="Amount")
        row.prop(md, "particle_offset", text="Offset")

        row = layout.row(align=True)
        row.prop(md, "axis", expand=True)

        layout.separator()

        layout.prop(md, "use_path", text="Create Along Paths")

        col = layout.column()
        col.active = md.use_path
        col.prop(md, "use_preserve_shape")

        row = col.row(align=True)
        row.prop(md, "position", slider=True)
        row.prop(md, "random_position", text="Random", slider=True)
        row = col.row(align=True)
        row.prop(md, "rotation", slider=True)
        row.prop(md, "random_rotation", text="Random", slider=True)

        layout.separator()

        col = layout.column()
        col.prop_search(md, "index_layer_name", ob.data, "vertex_colors", text="Index Layer")
        col.prop_search(md, "value_layer_name", ob.data, "vertex_colors", text="Value Layer")

    def PARTICLE_SYSTEM(self, layout, _ob, _md):
        layout.label(text="Settings can be found inside the Particle context")

    def SCREW(self, layout, _ob, md):
        layout.use_property_split = True
        col = layout.column()
        col.separator()

        col.prop(md, "angle", text='Angle')
        col.prop(md, "screw_offset")
        col.prop(md, "iterations")
        col.separator()

        row = col.row(align=True, heading='Axis')
        row.prop(md, "axis", expand=True)
        col.prop(md, "object", text="Axis Object")
        col.prop(md, "use_object_screw_offset", text="Object Screw")
        col.separator()

        col.prop(md, "steps", text="Steps Viewport")
        col.prop(md, "render_steps", text="Render")
        col.separator()

        row = col.row(align=True, heading='Merge')
        row.prop(md, "use_merge_vertices", text="")
        row2 = row.row()
        row2.active = md.use_merge_vertices
        row2.prop(md, "merge_threshold", text="")
        col.separator()

        row = col.row(align=True, heading='Stretch UVs')
        row.prop(md, "use_stretch_u", text="U", toggle=True)
        row.prop(md, "use_stretch_v", text="V", toggle=True)

        col.separator()
        col.use_property_split = False
        pref = get_preferences().modifier
        col.prop(pref, "screw_normals", text="Normals:")
        if get_preferences().modifier.screw_normals:
            col.use_property_split = True
            col.prop(md, "use_smooth_shade")
            col.prop(md, "use_normal_calculate")
            col.prop(md, "use_normal_flip")

    def SHRINKWRAP(self, layout, ob, md):
        layout.use_property_split = True
        col = layout.column()
        col.separator()

        col.prop(md, "wrap_method")
        if md.wrap_method in {'PROJECT', 'NEAREST_SURFACEPOINT', 'TARGET_PROJECT'}:
            col.prop(md, "wrap_mode")

        if md.wrap_method == 'PROJECT':

            col.prop(md, "project_limit")
            col.prop(md, "subsurf_levels")

            row = col.row(align=True, heading='Axis')
            row.prop(md, "use_project_x", toggle=True)
            row.prop(md, "use_project_y", toggle=True)
            row.prop(md, "use_project_z", toggle=True)

            col.prop(md, "use_negative_direction")
            col.prop(md, "use_positive_direction")

            row = col.row(align=True, heading='Axis')
            row.prop(md, "cull_face", expand=True)

            col.prop(md, "use_invert_cull")

        col.prop(md, "target")

        if md.wrap_method == 'PROJECT':
            col.prop(md, "auxiliary_target")

        col.prop(md, "offset")
        row = col.row()
        row.prop_search(md, "vertex_group", ob, "vertex_groups", text="Vertex Group")
        row.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')

    def SIMPLE_DEFORM(self, layout, ob, md):

        layout.row().prop(md, "deform_method", expand=True)
        layout.use_property_split = True
        col = layout.column()
        col.separator()

        if md.deform_method in {'TAPER', 'STRETCH'}:
            col.prop(md, "factor")
        else:
            col.prop(md, "angle")

        col.prop(md, "origin")
        row = col.row()
        row.prop(md, "deform_axis", expand=True)

        col.use_property_split = False
        pref = get_preferences().modifier
        col.prop(pref, "simpledeform_restrictions", text="Restrictions:")
        if pref.simpledeform_restrictions:
            col.use_property_split = True

            col.prop(md, "limits", slider=True)

            if md.deform_method in {'TAPER', 'STRETCH', 'TWIST'}:
                row = col.row(align=True, heading='Lock')
                deform_axis = md.deform_axis
                if deform_axis != 'X':
                    row.prop(md, "lock_x")
                if deform_axis != 'Y':
                    row.prop(md, "lock_y")
                if deform_axis != 'Z':
                    row.prop(md, "lock_z")

            row = col.row()
            row.prop_search(md, "vertex_group", ob, "vertex_groups", text="Vertex Group")
            row.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')

    def FLUID(self, layout, _ob, _md):
        layout.label(text="Settings are inside the Physics tab")

    def SMOOTH(self, layout, ob, md):
        layout.use_property_split = True
        col = layout.column()
        col.separator()

        row = col.row(align=True, heading='Axis')
        col.prop(md, "use_x", toggle=True)
        col.prop(md, "use_y", toggle=True)
        col.prop(md, "use_z", toggle=True)

        col.prop(md, "factor")
        col.prop(md, "iterations")
        col.label(text="Vertex Group:")
        row = col.row()
        row.prop_search(md, "vertex_group", ob, "vertex_groups", text="Vertex Group")
        row.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')

    def SOFT_BODY(self, layout, _ob, _md):
        layout.label(text="Settings are inside the Physics tab")

    def SOLIDIFY(self, layout, ob, md):
        layout.use_property_split = True
        col = layout.column()
        col.separator()

        col.prop(md, "solidify_mode", text='Mode')

        solidify_mode = md.solidify_mode

        if solidify_mode == 'NON_MANIFOLD':
            col.prop(md, "nonmanifold_thickness_mode")
            col.prop(md, "nonmanifold_boundary_mode")

        col.prop(md, "thickness")
        col.prop(md, "offset")
        if solidify_mode == 'NON_MANIFOLD':
            col.prop(md, "nonmanifold_merge_threshold")
        col.prop(md, "use_rim")
        col.prop(md, "use_rim_only")

        col.separator()

        # col.use_property_split = False
        row = col.row()
        row.prop_search(md, "vertex_group", ob, "vertex_groups", text="Vertex Groups")
        sub = row.row(align=True)
        sub.active = bool(md.vertex_group)
        sub.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')

        col.use_property_split = True
        col.prop(md, "thickness_vertex_group", text="Factor")
        if solidify_mode == 'NON_MANIFOLD':
            col.prop(md, "use_flat_faces")

        col.separator()

        col.use_property_split = False
        pref = get_preferences().modifier
        col.prop(pref, "solidify_normals", text='Normals')
        if pref.solidify_normals:
            col.use_property_split = True
            col.prop(md, "use_flip_normals")
            if solidify_mode == 'EXTRUDE':
                col.prop(md, "use_even_offset")
                col.prop(md, "use_quality_normals")

        col.use_property_split = False
        pref = get_preferences().modifier
        col.prop(pref, "solidify_materials", text='Materials')
        if pref.solidify_materials:
            col.use_property_split = True
            col.prop(md, "material_offset", text="Material Offset")
            col.prop(md, "material_offset_rim", text="Rim")

        col.use_property_split = False
        pref = get_preferences().modifier
        col.prop(pref, "solidify_edgedata", text='Edge Data')
        if pref.solidify_edgedata:
            col.use_property_split = True
            if solidify_mode == 'EXTRUDE':
                col.label(text="Crease:")
                col.prop(md, "edge_crease_inner", text="Inner")
                col.prop(md, "edge_crease_outer", text="Outer")
                col.prop(md, "edge_crease_rim", text="Rim")
            col.prop(md, "bevel_convex")

        col.use_property_split = False
        pref = get_preferences().modifier
        col.prop(pref, "solidify_thicknes", text='Thickness Clamp')
        if pref.solidify_thicknes:
            col.use_property_split = True
            col.prop(md, "thickness_clamp", text='Clamp')
            col.prop(md, "use_thickness_angle_clamp")

        col.use_property_split = False
        pref = get_preferences().modifier
        col.prop(pref, "solidify_output", text='Output Vertex Groups')
        if pref.solidify_output:
            col.use_property_split = True
            row = col.row()
            row.prop_search(md, "shell_vertex_group", ob, "vertex_groups", text="Shell")
            row = col.row()
            row.prop_search(md, "rim_vertex_group", ob, "vertex_groups", text="Rim")

    def SUBSURF(self, layout, ob, md):
        from bpy import context
        layout.use_property_split = True
        col = layout.column()
        col.separator()

        col.prop(md, "subdivision_type", text='Type')
        col.separator()

        scene = context.scene
        engine = context.engine
        show_adaptive_options = (
            engine == 'CYCLES' and md == ob.modifiers[-1] and
            scene.cycles.feature_set == 'EXPERIMENTAL'
        )

        if show_adaptive_options:
            col.prop(ob.cycles, "use_adaptive_subdivision", text="Adaptive Subdivision")

        if show_adaptive_options and ob.cycles.use_adaptive_subdivision:
            col.prop(ob.cycles, "dicing_rate")
            render = max(scene.cycles.dicing_rate * ob.cycles.dicing_rate, 0.1)
            preview = max(scene.cycles.preview_dicing_rate * ob.cycles.dicing_rate, 0.1)
            col.label(text=f"Final Dicing Rate: Render {render:.2f} px, Preview {preview:.2f} px")
            col.separator()

        col.prop(md, "levels", text="Levels Viewport")
        col.prop(md, "render_levels", text="Render")
        col.separator()
        col.prop(md, "show_only_control_edges")

        col.separator()

        col.use_property_split = False
        pref = get_preferences().modifier
        col.prop(pref, "subsurf_advanced", text="Advenced")
        if pref.subsurf_advanced:
            col.use_property_split = True

            col.prop(md, "quality")
            col.prop(md, "uv_smooth")
            col.prop(md, "use_creases")

    def SURFACE(self, layout, _ob, _md):
        layout.label(text="Settings are inside the Physics tab")

    def SURFACE_DEFORM(self, layout, _ob, md):
        layout.use_property_split = True
        col = layout.column()
        col.separator()

        col.prop(md, "target")

        col.prop(md, "falloff")
        col.prop(md, "strength")

        row = col.row()
        row.prop_search(md, "vertex_group", _ob, "vertex_groups", text="Vertex Group")
        row.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')

        row = col.row()
        row.operator("object.surfacedeform_bind", text="Unbind" if md.is_bound else "Bind").modifier = md.name

    def UV_PROJECT(self, layout, ob, md):
        layout.use_property_split = True
        col = layout.column()
        col.separator()

        col.prop_search(md, "uv_layer", ob.data, "uv_layers")
        col.separator()

        col.prop(md, "aspect_x", text="Aspect X")
        col.prop(md, "aspect_y", text="Y")
        col.separator()

        col.prop(md, "scale_x", text="Scale X")
        col.prop(md, "scale_y", text="Y")
        col.separator()

        col.prop(md, "projector_count", text="Projectors")
        for proj in md.projectors:
            col.prop(proj, "object")

    def WARP(self, layout, ob, md):
        use_falloff = (md.falloff_type != 'NONE')

        layout.use_property_split = True
        col = layout.column()
        col.separator()

        col.prop(md, "object_from")
        obj = md.object_from
        if obj and obj.type == 'ARMATURE':
            col.label(text="Bone:")
            col.prop_search(md, "bone_from", obj.data, "bones", text="Bone From")
        col.separator()

        col.prop(md, "object_to")
        if obj and obj.type == 'ARMATURE':
            col.label(text="Bone:")
            col.prop_search(md, "bone_to", obj.data, "bones", text="Bone To")
        col.separator()

        col.prop(md, "strength")
        col.prop(md, "use_volume_preserve")

        row = col.row()
        row.prop_search(md, "vertex_group", ob, "vertex_groups", text="Vertex Group")
        row.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')

        col.use_property_split = False
        pref = get_preferences().modifier
        col.prop(pref, "warp_falloff", text="Falloff:")
        if pref.warp_falloff:
            col.use_property_split = True
            col.prop(md, "falloff_type")
            if use_falloff:
                col.prop(md, "falloff_radius")
            if md.falloff_type == 'CURVE':
                col.template_curve_mapping(md, "falloff_curve")

        col.use_property_split = False
        pref = get_preferences().modifier
        col.prop(pref, "warp_textures", text="Texture:")
        if pref.warp_textures:
            col.use_property_split = True
            col.template_ID(md, "texture", new="texture.new")
            col.prop(md, "texture_coords")

            if md.texture_coords == 'OBJECT':
                col.prop(md, "texture_coords_object", text="Object")
                obj = md.texture_coords_object
                if obj and obj.type == 'ARMATURE':
                    col.prop_search(md, "texture_coords_bone", obj.data, "bones", text="Bone")
            elif md.texture_coords == 'UV' and ob.type == 'MESH':
                col.prop_search(md, "uv_layer", ob.data, "uv_layers")

    def WAVE(self, layout, ob, md):
        layout.use_property_split = True
        col = layout.column()
        col.separator()

        row = col.row(align=True, heading='Motion')
        row.prop(md, "use_x", toggle=True)
        row.prop(md, "use_y", toggle=True)

        col.prop(md, "use_cyclic")

        row = col.row(align=True, heading='Along Normals')
        row.active = md.use_normal
        row.prop(md, "use_normal", text="")
        row.prop(md, "use_normal_x", text="X", toggle=True)
        row.prop(md, "use_normal_y", text="Y", toggle=True)
        row.prop(md, "use_normal_z", text="Z", toggle=True)

        col.prop(md, "falloff_radius", text="Falloff")
        col.prop(md, "height", slider=True)
        col.prop(md, "width", slider=True)
        col.prop(md, "narrowness", slider=True)

        row = col.row()
        row.prop_search(md, "vertex_group", ob, "vertex_groups", text="Vertex Group")
        row.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')

        col.use_property_split = False
        pref = get_preferences().modifier
        col.prop(pref, "wave_start", text="Start position")
        if pref.wave_start:
            col.use_property_split = True
            col.prop(md, "start_position_object", text="Object")
            col.prop(md, "start_position_x", text="Start position X")
            col.prop(md, "start_position_y", text="Y")

        col.use_property_split = False
        pref = get_preferences().modifier
        col.prop(pref, "wave_time", text="Time")
        if pref.wave_time:
            col.use_property_split = True
            col.prop(md, "time_offset", slider=True)
            col.prop(md, "lifetime", slider=True)
            col.prop(md, "damping_time", slider=True)
            col.prop(md, "speed", slider=True)

        col.use_property_split = False
        pref = get_preferences().modifier
        col.prop(pref, "wave_texture", text="Texture")
        if pref.wave_texture:
            col.use_property_split = True

            col.template_ID(md, "texture", new="texture.new")
            col.prop(md, "texture_coords")
            if md.texture_coords == 'UV' and ob.type == 'MESH':
                col.prop_search(md, "uv_layer", ob.data, "uv_layers")
            elif md.texture_coords == 'OBJECT':
                col.prop(md, "texture_coords_object")
                obj = md.texture_coords_object
                if obj and obj.type == 'ARMATURE':
                    col.prop_search(md, "texture_coords_bone", obj.data, "bones")


    def REMESH(self, layout, _ob, md):

        layout.separator()
        row = layout.row()

        row.prop(md, "mode", expand=True)

        col = layout.column(align=True)

        col.use_property_split = True
        col.separator()

        if md.mode == 'VOXEL':
            col.prop(md, "voxel_size")
            col.prop(md, "adaptivity")
        else:
            col.prop(md, "octree_depth")
            col.prop(md, "scale")

            if md.mode == 'SHARP':
                col.prop(md, "sharpness")

            col.prop(md, "use_remove_disconnected")
            col.prop(md, "threshold")

        col.prop(md, "use_smooth_shade")

    @staticmethod
    def vertex_weight_mask(layout, ob, md):
        layout.label(text="Influence/Mask Options:")

        split = layout.split(factor=0.4)
        split.label(text="Global Influence:")
        split.prop(md, "mask_constant", text="")

        if not md.mask_texture:
            split = layout.split(factor=0.4)
            split.label(text="Vertex Group Mask:")
            row = split.row(align=True)
            row.prop_search(md, "mask_vertex_group", ob, "vertex_groups", text="")
            row.prop(md, "invert_mask_vertex_group", text="", icon='ARROW_LEFTRIGHT')

        if not md.mask_vertex_group:
            split = layout.split(factor=0.4)
            split.label(text="Texture Mask:")
            split.template_ID(md, "mask_texture", new="texture.new")
            if md.mask_texture:
                split = layout.split()

                col = split.column()
                col.label(text="Texture Coordinates:")
                col.prop(md, "mask_tex_mapping", text="")

                col = split.column()
                col.label(text="Use Channel:")
                col.prop(md, "mask_tex_use_channel", text="")

                if md.mask_tex_mapping == 'OBJECT':
                    layout.prop(md, "mask_tex_map_object", text="Object")
                    obj = md.mask_tex_map_object
                    if obj and obj.type == 'ARMATURE':
                        layout.prop_search(md, "mask_tex_map_bone", obj.data, "bones", text="Bone")
                elif md.mask_tex_mapping == 'UV' and ob.type == 'MESH':
                    layout.prop_search(md, "mask_tex_uv_layer", ob.data, "uv_layers")

    def VERTEX_WEIGHT_EDIT(self, layout, ob, md):
        split = layout.split()

        col = split.column()
        col.label(text="Vertex Group:")
        col.prop_search(md, "vertex_group", ob, "vertex_groups", text="")

        col.label(text="Default Weight:")
        col.prop(md, "default_weight", text="")

        col = split.column()
        col.prop(md, "use_add")
        sub = col.column()
        sub.active = md.use_add
        sub.prop(md, "add_threshold")

        col = col.column()
        col.prop(md, "use_remove")
        sub = col.column()
        sub.active = md.use_remove
        sub.prop(md, "remove_threshold")

        layout.separator()

        row = layout.row(align=True)
        row.prop(md, "falloff_type")
        row.prop(md, "invert_falloff", text="", icon='ARROW_LEFTRIGHT')
        if md.falloff_type == 'CURVE':
            layout.template_curve_mapping(md, "map_curve")

        # Common mask options
        layout.separator()
        self.vertex_weight_mask(layout, ob, md)

    def VERTEX_WEIGHT_MIX(self, layout, ob, md):
        split = layout.split()

        col = split.column()
        col.label(text="Vertex Group A:")
        col.prop_search(md, "vertex_group_a", ob, "vertex_groups", text="")
        col.label(text="Default Weight A:")
        col.prop(md, "default_weight_a", text="")

        col.label(text="Mix Mode:")
        col.prop(md, "mix_mode", text="")

        col = split.column()
        col.label(text="Vertex Group B:")
        col.prop_search(md, "vertex_group_b", ob, "vertex_groups", text="")
        col.label(text="Default Weight B:")
        col.prop(md, "default_weight_b", text="")

        col.label(text="Mix Set:")
        col.prop(md, "mix_set", text="")

        # Common mask options
        layout.separator()
        self.vertex_weight_mask(layout, ob, md)

    def VERTEX_WEIGHT_PROXIMITY(self, layout, ob, md):
        split = layout.split()

        col = split.column()
        col.label(text="Vertex Group:")
        col.prop_search(md, "vertex_group", ob, "vertex_groups", text="")

        col = split.column()
        col.label(text="Target Object:")
        col.prop(md, "target", text="")

        split = layout.split()

        col = split.column()
        col.label(text="Distance:")
        col.prop(md, "proximity_mode", text="")
        if md.proximity_mode == 'GEOMETRY':
            col.row().prop(md, "proximity_geometry")

        col = split.column()
        col.label()
        col.prop(md, "min_dist")
        col.prop(md, "max_dist")

        layout.separator()
        row = layout.row(align=True)
        row.prop(md, "falloff_type")
        row.prop(md, "invert_falloff", text="", icon='ARROW_LEFTRIGHT')

        # Common mask options
        layout.separator()
        self.vertex_weight_mask(layout, ob, md)

    def SKIN(self, layout, _ob, md):
        layout.use_property_split = True
        col = layout.column()
        col.separator()

        col.prop(md, "branch_smoothing")
        row = col.row(align=True, heading='Symmetry')
        row.prop(md, "use_x_symmetry", toggle=True)
        row.prop(md, "use_y_symmetry", toggle=True)
        row.prop(md, "use_z_symmetry", toggle=True)
        col.prop(md, "use_smooth_shade")

        split = layout.split()
        col = split.column()
        col.operator("object.skin_armature_create", text="Create Armature").modifier = md.name
        col = split.column()
        col.operator("mesh.customdata_skin_add")

        col = layout.column()
        row = col.row(align=True)
        row.operator("object.skin_loose_mark_clear", text="Mark Loose").action = 'MARK'
        row.operator("object.skin_loose_mark_clear", text="Clear Loose").action = 'CLEAR'

        col.operator("object.skin_root_mark", text="Mark Root")
        col.operator("object.skin_radii_equalize", text="Equalize Radii")

    def TRIANGULATE(self, layout, _ob, md):
        layout.use_property_split = True
        col = layout.column()
        col.separator()

        col.prop(md, "quad_method")
        col.prop(md, "ngon_method")
        col.prop(md, "min_vertices")
        col.prop(md, "keep_custom_normals")

    def UV_WARP(self, layout, ob, md):
        layout.use_property_split = True
        col = layout.column()
        col.separator()

        col.prop_search(md, "uv_layer", ob.data, "uv_layers")

        col.prop(md, "center")
        col.separator()

        col.prop(md, "axis_u", text="Axis U")
        col.prop(md, "axis_v", text="V")
        col.separator()

        col.prop(md, "object_from")
        obj = md.object_from
        if obj and obj.type == 'ARMATURE':
            col.prop_search(md, "bone_from", obj.data, "bones", text="Bone from")

        col.prop(md, "object_to")
        obj = md.object_to
        if obj and obj.type == 'ARMATURE':
            col.prop_search(md, "bone_to", obj.data, "bones", text="Bone to")
        col.separator()

        row = col.row()
        row.prop_search(md, "vertex_group", ob, "vertex_groups", text="Vertex Group")
        row.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')

        col.use_property_split = False
        pref = get_preferences().modifier
        col.prop(pref, "uvwarp_transform", text="Transform")
        if pref.uvwarp_transform:
            col.use_property_split = True

            col.prop(md, "offset", text="")
            col.prop(md, "scale", text="")
            col.prop(md, "rotation", text="")

    def WIREFRAME(self, layout, ob, md):
        has_vgroup = bool(md.vertex_group)
        layout.use_property_split = True
        col = layout.column()
        col.separator()

        col.prop(md, "thickness", text="Thickness")
        col.prop(md, "offset")
        col.separator()
        col.prop(md, "use_boundary", text="Boundary")
        col.prop(md, "use_replace", text="Replace Original")
        col.separator()
        row = col.row(heading='Thickness')
        row.prop(md, "use_even_offset", text="Even")
        col.prop(md, "use_relative_offset", text="Relative")
        col.separator()
        row = col.row(heading='Crease Edges')
        row.prop(md, "use_crease", text="")
        row.prop(md, "crease_weight", text="")
        col.prop(md, "material_offset", text="Material Offset")

        col.separator()

        col.use_property_split = False
        pref = get_preferences().modifier
        col.prop(pref, "wireframe_vgroup", text="Profile:")
        if pref.wireframe_vgroup:
            col.use_property_split = True
            row = col.row()
            row.prop_search(md, "vertex_group", ob, "vertex_groups", text="Vertex Group")
            sub = row.row(align=True)
            sub.active = has_vgroup
            sub.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')
            row = col.row(align=True)
            row.active = has_vgroup
            row.prop(md, "thickness_vertex_group", text="Factor")

    def WELD(self, layout, ob, md):
        layout.use_property_split = True
        col = layout.column()
        col.separator()

        col.prop(md, "merge_threshold", text="Distance")
        col.prop(md, "max_interactions")

        row = col.row()
        row.prop_search(md, "vertex_group", ob, "vertex_groups", text='Vertex Group')
        row.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')

    def DATA_TRANSFER(self, layout, ob, md):
        layout.use_property_split = True
        col = layout.column()
        col.separator()

        row = col.row(align=True)
        row.prop(md, "object", text='Source')
        row.prop(md, "use_object_transform", text="", icon='GROUP')

        col.prop(md, "mix_mode")
        col.prop(md, "mix_factor")

        row = col.row()
        row.prop_search(md, "vertex_group", ob, "vertex_groups", text="Vertex Group")
        sub = row.row(align=True)
        sub.active = bool(md.vertex_group)
        sub.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')
        col.operator("object.datalayout_transfer", text="Generate Data Layers")

        col.separator()

        col.use_property_split = False
        col.prop(md, "use_vert_data")
        if md.use_vert_data:
            row = col.row(align=True)
            row.prop(md, "data_types_verts", expand=True)
            col.use_property_split = True
            col.prop(md, "vert_mapping")

            pref = get_preferences().modifier
            col.prop(pref, "datatransfer_vgroups", text="Vertex Groups")
            if pref.datatransfer_vgroups:

                col.prop(md, "layers_vgroup_select_src", text="Layer Selection")
                col.prop(md, "layers_vgroup_select_dst", text="Layer Mapping")

        col.use_property_split = False
        col.prop(md, "use_edge_data")
        if md.use_edge_data:
            row = col.row(align=True)
            row.prop(md, "data_types_edges", expand=True)
            col.use_property_split = True
            col.prop(md, "edge_mapping")

        col.use_property_split = False
        col.prop(md, "use_loop_data")
        if md.use_loop_data:
            row = col.row(align=True)
            row.prop(md, "data_types_loops", expand=True)
            col.use_property_split = True
            col.prop(md, "loop_mapping", text="Mapping")

            pref = get_preferences().modifier
            col.prop(pref, "datatransfer_vcolors", text="Vertex Colors")
            if pref.datatransfer_vcolors:
                col.prop(md, "layers_vcol_select_src", text="Layer Selection")
                col.prop(md, "layers_vcol_select_dst", text="Layer Mapping")

            pref = get_preferences().modifier
            col.prop(pref, "datatransfer_uv", text="UVs")
            if pref.datatransfer_uv:
                col.prop(md, "layers_uv_select_src", text="Layer Selection")
                col.prop(md, "layers_uv_select_dst", text="Layer Mapping")
                col.prop(md, "islands_precision")

        col.use_property_split = False
        col.prop(md, "use_poly_data")
        if md.use_poly_data:
            row = col.row(align=True)
            row.prop(md, "data_types_polys", expand=True)
            col.use_property_split = True
            col.prop(md, "poly_mapping")

        col.use_property_split = False
        pref = get_preferences().modifier
        col.prop(pref, "datatransfer_toplogy", text="Topology Mapping")
        if pref.datatransfer_toplogy:
            col.use_property_split = True
            row = col.row(align=True, heading='Max Distance')
            row.prop(md, "use_max_distance", text="")
            row.prop(md, "max_distance",  text="")
            col.prop(md, "ray_radius")

    def NORMAL_EDIT(self, layout, ob, md):
        has_vgroup = bool(md.vertex_group)
        do_polynors_fix = not md.no_polynors_fix

        layout.use_property_split = True
        col = layout.column()
        col.separator()

        row = col.row()
        row.prop(md, "mode", expand=True)
        col.prop(md, "target")

        row = col.row(align=True)
        row.active = (md.mode == 'DIRECTIONAL')
        row.prop(md, "use_direction_parallel")

        col.use_property_split = False
        pref = get_preferences().modifier
        col.prop(pref, "normaledit_mix", text="Mix")
        if pref.normaledit_mix:
            col.use_property_split = True

            col.prop(md, "mix_mode")
            col.prop(md, "mix_factor")
            row = col.row()
            row.prop_search(md, "vertex_group", ob, "vertex_groups", text="Vertex Group")
            sub = row.row(align=True)
            sub.active = has_vgroup
            sub.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')
            row = col.row(align=True)
            row.prop(md, "mix_limit")
            row.prop(md, "no_polynors_fix", text="", icon='UNLOCKED' if do_polynors_fix else 'LOCKED')

        col.use_property_split = False
        pref = get_preferences().modifier
        col.prop(pref, "normaledit_offset", text="Offset")
        if pref.normaledit_offset:
            col.use_property_split = True
            col.prop(md, "offset")

    def CORRECTIVE_SMOOTH(self, layout, ob, md):
        is_bind = md.is_bind

        layout.use_property_split = True
        col = layout.column()
        col.separator()

        col.prop(md, "factor", text="Factor")
        col.prop(md, "iterations")
        col.prop(md, "scale")
        col.prop(md, "smooth_type")

        row = col.row()
        row.prop_search(md, "vertex_group", ob, "vertex_groups", text="Vertex Group")
        row.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')

        col.prop(md, "use_only_smooth")
        col.prop(md, "use_pin_boundary")

        col.prop(md, "rest_source")
        if md.rest_source == 'BIND':
            col.operator("object.correctivesmooth_bind", text="Unbind" if is_bind else "Bind").modifier = md.name

    def WEIGHTED_NORMAL(self, layout, ob, md):
        layout.use_property_split = True
        col = layout.column()
        col.separator()

        col.prop(md, "mode")
        col.prop(md, "weight")
        col.prop(md, "thresh", text="Threshold")
        col.prop(md, "keep_sharp")
        col.prop(md, "face_influence")

        row = col.row()
        row.prop_search(md, "vertex_group", ob, "vertex_groups", text="Vertex Group")
        row.active = bool(md.vertex_group)
        row.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')
