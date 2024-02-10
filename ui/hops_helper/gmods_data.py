import bpy
from bpy.types import Panel
from bpy.app.translations import pgettext_iface as iface_
from ... preferences import get_preferences

gmods_dic = {
    'GP_NOISE': 'MOD_NOISE',
    'GP_SMOOTH': 'MOD_SMOOTH',
    'GP_SUBDIV': 'MOD_SUBSURF',
    'GP_SIMPLIFY': 'MOD_SIMPLIFY',
    'GP_THICK': 'MOD_THICKNESS',
    'GP_TEXTURE': 'TEXTURE',
    'GP_TINT': 'MOD_TINT',
    'GP_TIME': 'MOD_TIME',
    'GP_COLOR': 'MOD_HUE_SATURATION',
    'GP_OPACITY': 'MOD_OPACITY',
    'GP_ARRAY': 'MOD_ARRAY',
    'GP_BUILD': 'MOD_BUILD',
    'GP_LATTICE': 'MOD_LATTICE',
    'GP_MIRROR': 'MOD_MIRROR',
    'GP_HOOK': 'HOOK',
    'GP_OFFSET': 'MOD_OFFSET',
    'GP_ARMATURE': 'MOD_ARMATURE',
    'GP_MULTIPLY': 'GP_MULTIFRAME_EDITING'
}


class ModifierButtonsPanel:
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "modifier"
    bl_options = {'HIDE_HEADER'}


class DATA_PT_gpencil_modifiers(ModifierButtonsPanel, Panel):
    bl_label = "Modifiers"

    def check_conflicts(self, layout, ob):
        for md in ob.grease_pencil_modifiers:
            if md.type == 'GP_TIME':
                row = layout.row()
                row.label(text="Build and Time Offset modifier not compatible", icon='ERROR')
                break

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type == 'GPENCIL'

    def draw(self, context):
        layout = self.layout

        ob = context.object

        layout.operator_menu_enum("object.gpencil_modifier_add", "type")

        for md in ob.grease_pencil_modifiers:
            box = layout.template_greasepencil_modifier(md)
            if box:
                # match enum type to our functions, avoids a lookup table.
                getattr(self, md.type)(box, ob, md)

    # the mt.type enum is (ab)used for a lookup on function names
    # ...to avoid lengthy if statements
    # so each type must have a function here.

    def gpencil_masking(self, layout, ob, md, use_vertex, use_curve=False, use_mat=True):

        layout.use_property_split = True
        layout.use_property_decorate = True

        gpd = ob.data

        row = layout.row(align=True)
        layout.use_property_split = False
        row.prop_search(md, "layer", gpd, "layers", icon='GREASEPENCIL')
        layout.use_property_split = True
        row.prop(md, "invert_layers", text="", icon='ARROW_LEFTRIGHT')

        row = layout.row(align=True)
        layout.use_property_split = False
        row.prop(md, "layer_pass", text="Pass")
        layout.use_property_split = True
        row.prop(md, "invert_layer_pass", text="", icon='ARROW_LEFTRIGHT')

        if use_mat:
            row = layout.row(align=True)
            valid = md.material in (slot.material for slot in ob.material_slots) or md.material is None
            if valid:
                icon = 'SHADING_TEXTURE'
            else:
                icon = 'ERROR'

            row.alert = not valid
            layout.use_property_split = False
            row.prop_search(md, "material", gpd, "materials", icon=icon)
            layout.use_property_split = True
            row.prop(md, "invert_materials", text="", icon='ARROW_LEFTRIGHT')

            row = layout.row(align=True)
            layout.use_property_split = False
            row.prop(md, "pass_index", text="Pass")
            layout.use_property_split = True
            row.prop(md, "invert_material_pass", text="", icon='ARROW_LEFTRIGHT')

        if use_vertex:
            row = layout.row(align=True)
            layout.use_property_split = False
            row.prop_search(md, "vertex_group", ob, "vertex_groups")
            layout.use_property_split = True
            row.prop(md, "invert_vertex", text="", icon='ARROW_LEFTRIGHT')

        if use_curve:
            col = layout.column()
            col.separator()
            col.prop(md, "use_custom_curve")
            if md.use_custom_curve:
                col.template_curve_mapping(md, "curve")

    def GP_NOISE(self, layout, ob, md):
        layout.use_property_split = True
        layout.use_property_decorate = True
        layout.separator()

        layout.prop(md, "factor", text="Position")
        layout.prop(md, "factor_strength", text="Strength")
        layout.prop(md, "factor_thickness", text="Thickness")
        layout.prop(md, "factor_uvs", text="UV")
        layout.prop(md, "noise_scale")

        layout.use_property_split = False
        layout.prop(md, "random", text="Randomize")
        layout.use_property_split = True

        if md.random:
            layout.prop(md, "step")
            layout.prop(md, "seed")

        layout.use_property_split = False
        pref = get_preferences().modifier
        layout.prop(pref, "gnoice_influence", text="Influence")
        if get_preferences().modifier.gnoice_influence:
            layout.use_property_split = True
            self.gpencil_masking(self, layout, ob, md, True, True)

        layout.separator()

    def GP_SMOOTH(self, layout, ob, md):
        layout.use_property_split = False
        layout.use_property_decorate = True
        layout.separator()

        row = layout.row(align=True)
        row.prop(md, "use_edit_position", text="Position", toggle=True)
        row.prop(md, "use_edit_strength", text="Strength", toggle=True)
        row.prop(md, "use_edit_thickness", text="Thickness", toggle=True)
        row.prop(md, "use_edit_uv", text="UV", toggle=True)

        layout.use_property_split = True
        layout.prop(md, "factor")
        layout.prop(md, "step", text="Repeat")

        layout.use_property_split = False
        pref = get_preferences().modifier
        layout.prop(pref, "gsmooth_influence", text="Influence")
        if get_preferences().modifier.gsmooth_influence:
            layout.use_property_split = True
            self.gpencil_masking(self, layout, ob, md, True, True)

    def GP_SUBDIV(self, layout, ob, md):
        layout.use_property_split = True
        layout.use_property_decorate = True
        layout.separator()

        layout.row().prop(md, "subdivision_type")
        layout.prop(md, "level", text="Subdivisions")

        layout.use_property_split = False
        pref = get_preferences().modifier
        layout.prop(pref, "gsubsurf_influence", text="Influence")
        if get_preferences().modifier.gsubsurf_influence:
            layout.use_property_split = True
            self.gpencil_masking(self, layout, ob, md, False)

        layout.separator()

    def GP_SIMPLIFY(self, layout, ob, md):
        layout.use_property_split = True
        layout.use_property_decorate = True
        layout.separator()

        layout.prop(md, "mode")

        if md.mode == 'FIXED':
            layout.prop(md, "step")
        elif md.mode == 'ADAPTIVE':
            layout.prop(md, "factor")
        elif md.mode == 'SAMPLE':
            layout.prop(md, "length")
        elif md.mode == 'MERGE':
            layout.prop(md, "distance")

        layout.use_property_split = False
        pref = get_preferences().modifier
        layout.prop(pref, "gsimplify_influence", text="Influence")
        if get_preferences().modifier.gsimplify_influence:
            layout.use_property_split = True
            self.gpencil_masking(self, layout, ob, md, False)

        layout.separator()

    def GP_THICK(self, layout, ob, md):
        layout.use_property_split = True
        layout.use_property_decorate = True
        layout.separator()

        layout.prop(md, "normalize_thickness")

        if md.normalize_thickness:
            layout.prop(md, "thickness")
        else:
            layout.prop(md, "thickness_factor")

        layout.use_property_split = False
        pref = get_preferences().modifier
        layout.prop(pref, "gthick_influence", text="Influence")
        if get_preferences().modifier.gthick_influence:
            layout.use_property_split = True
            self.gpencil_masking(self, layout, ob, md, True, True)

        layout.separator()

    def GP_TEXTURE(self, layout, ob, md):
        layout.use_property_split = True
        layout.use_property_decorate = True
        layout.separator()

        layout.prop(md, "mode")
        if md.mode in {'STROKE', 'STROKE_AND_FILL'}:
            layout.prop(md, "fit_method")
            layout.prop(md, "uv_offset")
            layout.prop(md, "uv_scale")

        if md.mode == 'STROKE_AND_FILL':
            layout.separator()

        if md.mode in {'FILL', 'STROKE_AND_FILL'}:
            layout.prop(md, "fill_rotation", text="Rotation")
            layout.prop(md, "fill_offset", text="Location")
            layout.prop(md, "fill_scale", text="Scale")

        layout.use_property_split = False
        pref = get_preferences().modifier
        layout.prop(pref, "gtex_influence", text="Influence")
        if get_preferences().modifier.gtex_influence:
            layout.use_property_split = True
            self.gpencil_masking(self, layout, ob, md, True)

        layout.separator()

    def GP_TINT(self, layout, ob, md):
        layout.use_property_split = True
        layout.use_property_decorate = True
        layout.separator()

        layout.prop(md, "vertex_mode")
        layout.prop(md, "factor")
        layout.row().prop(md, "tint_type", expand=True)

        if md.tint_type == 'UNIFORM':
            layout.prop(md, "color")

        if md.tint_type == 'GRADIENT':
            layout.template_color_ramp(md, "colors")
            layout.prop(md, "object", text="Object")
            layout.prop(md, "radius")

        layout.use_property_split = False
        pref = get_preferences().modifier
        layout.prop(pref, "gtint_influence", text="Influence")
        if get_preferences().modifier.gtint_influence:
            layout.use_property_split = True
            self.gpencil_masking(self, layout, ob, md, True, True)

        layout.separator()

    def GP_TIME(self, layout, ob, md):
        layout.use_property_split = True
        layout.use_property_decorate = True
        layout.separator()

        gpd = ob.data

        row = layout.row()
        row.prop(md, "mode", text="Mode")

        row = layout.row()
        if md.mode == 'FIX':
            txt = "Frame"
        else:
            txt = "Frame Offset"
        row.prop(md, "offset", text=txt)

        row = layout.row()
        row.enabled = md.mode != 'FIX'
        row.prop(md, "frame_scale")

        row = layout.row()
        row.enabled = md.mode != 'FIX'
        row.prop(md, "use_keep_loop")

        row = layout.row()
        row.separator()

        row = layout.row()
        row.enabled = md.mode != 'FIX'
        row.use_property_split = False
        row.prop(md, "use_custom_frame_range")
        row.use_property_split = True

        if md.use_custom_frame_range:
            col = layout.column(align=True)
            col.enabled = md.mode != 'FIX' and md.use_custom_frame_range is True
            col.prop(md, "frame_start")
            col.prop(md, "frame_end")

        layout.use_property_split = False
        pref = get_preferences().modifier
        layout.prop(pref, "gtime_influence", text="Influence")
        if get_preferences().modifier.gtime_influence:
            layout.use_property_split = True
            self.gpencil_masking(self, layout, ob, md, False, use_mat=False)

        layout.separator()

    def GP_COLOR(self, layout, ob, md):
        layout.use_property_split = True
        layout.use_property_decorate = True
        layout.separator()

        layout.prop(md, "modify_color")
        layout.prop(md, "hue", text="H", slider=True)
        layout.prop(md, "saturation", text="S", slider=True)
        layout.prop(md, "value", text="V", slider=True)

        layout.use_property_split = False
        pref = get_preferences().modifier
        layout.prop(pref, "gcolor_influence", text="Influence")
        if get_preferences().modifier.gcolor_influence:
            layout.use_property_split = True
            self.gpencil_masking(self, layout, ob, md, False, True)

        layout.separator()

    def GP_OPACITY(self, layout, ob, md):
        layout.use_property_split = True
        layout.use_property_decorate = True
        layout.separator()

        layout.prop(md, "modify_color")

        if md.modify_color == 'HARDNESS':
            layout.prop(md, "hardness")
            show = False
        else:
            layout.prop(md, "normalize_opacity")
            if md.normalize_opacity is True:
                text = "Strength"
            else:
                text = "Opacity Factor"

            layout.prop(md, "factor", text=text)
            show = True

        layout.use_property_split = False
        pref = get_preferences().modifier
        layout.prop(pref, "gopacity_influence", text="Influence")
        if get_preferences().modifier.gopacity_influence:
            layout.use_property_split = True
            self.gpencil_masking(self, layout, ob, md, show, show)

        layout.separator()

    def GP_ARRAY(self, layout, ob, md):

        layout.use_property_split = True
        layout.use_property_decorate = True
        layout.separator()

        layout.prop(md, "count")
        layout.prop(md, "replace_material", text='Material Override')

        layout.use_property_split = False
        layout.prop(md, "use_relative_offset", text="Relative Offset")
        if md.use_relative_offset:
            layout.use_property_split = True
            layout.prop(md, "relative_offset", expand=True)

        layout.use_property_split = False
        layout.prop(md, "use_constant_offset", text="Constant Offset")
        if md.use_constant_offset:
            layout.use_property_split = True
            layout.prop(md, "constant_offset", expand=True)

        layout.use_property_split = False
        layout.prop(md, "use_object_offset")
        if md.use_object_offset:
            layout.use_property_split = True
            layout.prop(md, "offset_object", expand=True)

        layout.use_property_split = False
        pref = get_preferences().modifier
        layout.prop(pref, "garray_random", text="Randomize")
        if get_preferences().modifier.garray_random:
            layout.use_property_split = True
            layout.prop(md, "random_offset")
            layout.prop(md, "random_rotation")
            layout.prop(md, "random_scale")
            layout.prop(md, "seed")
            layout.separator()

        layout.use_property_split = False
        pref = get_preferences().modifier
        layout.prop(pref, "garray_influence", text="Influence")
        if get_preferences().modifier.garray_influence:
            layout.use_property_split = True
            self.gpencil_masking(self, layout, ob, md, False)

        layout.separator()

    def GP_BUILD(self, layout, ob, md):

        layout.use_property_split = True
        layout.use_property_decorate = True

        layout.separator()
        self.check_conflicts(self, layout, ob)

        layout.prop(md, "mode")
        if md.mode == 'CONCURRENT':
            layout.prop(md, "concurrent_time_alignment")

        layout.separator()
        layout.prop(md, "transition")
        layout.prop(md, "start_delay")
        layout.prop(md, "length")

        row = layout.row(heading="Use Factor", align=True)
        layout.use_property_split = False
        row.prop(md, "use_percentage", text='')
        row.prop(md, "percentage_factor", text='')

        layout.use_property_split = False
        layout.prop(md, "use_restrict_frame_range", text='Custom Range')
        if md.use_restrict_frame_range:
            layout.use_property_split = True
            layout.prop(md, "frame_start", text="Start")
            layout.prop(md, "frame_end", text="End")

        layout.use_property_split = False
        pref = get_preferences().modifier
        layout.prop(pref, "build_influence", text="Influence")
        if get_preferences().modifier.build_influence:
            layout.use_property_split = True
            self.gpencil_masking(self, layout, ob, md, False, use_mat=False)

        layout.separator()

    def GP_LATTICE(self, layout, ob, md):

        layout.use_property_split = True
        layout.use_property_decorate = True
        layout.separator()

        layout.prop(md, "object")
        if md.object and md.object.type == 'ARMATURE':
            layout.prop_search(md, "subtarget", md.object.data, "bones", text="")

        row = layout.row(align=True)
        layout.use_property_split = False
        row.prop_search(md, "vertex_group", ob, "vertex_groups")
        layout.use_property_split = True
        row.prop(md, "invert_vertex", text="", icon='ARROW_LEFTRIGHT')

        layout.prop(md, "strength", slider=True)

        layout.use_property_split = False
        pref = get_preferences().modifier
        layout.prop(pref, "glattice_influence", text="Influence")
        if get_preferences().modifier.glattice_influence:
            layout.use_property_split = True
            self.gpencil_masking(self, layout, ob, md, False)

        layout.separator()

    def GP_MIRROR(self, layout, ob, md):

        layout.use_property_split = True
        layout.use_property_decorate = True

        layout.separator()

        row = layout.row(heading='Axis', align=True)

        row.prop(md, "x_axis", toggle=True)
        row.prop(md, "y_axis", toggle=True)
        row.prop(md, "z_axis", toggle=True)

        layout.prop(md, "object")

        layout.use_property_split = False
        pref = get_preferences().modifier
        layout.prop(pref, "gmirror_influence", text="Influence")
        if get_preferences().modifier.gmirror_influence:
            layout.use_property_split = True
            self.gpencil_masking(self, layout, ob, md, False)

        layout.separator()

    def GP_HOOK(self, layout, ob, md):
        layout.use_property_split = True
        layout.use_property_decorate = True
        layout.separator()

        layout.prop(md, "object")
        if md.object and md.object.type == 'ARMATURE':
            layout.prop_search(md, "subtarget", md.object.data, "bones", text="")

        row = layout.row(align=True)
        layout.use_property_split = False
        row.prop_search(md, "vertex_group", ob, "vertex_groups")
        layout.use_property_split = True
        row.prop(md, "invert_vertex", text="", icon='ARROW_LEFTRIGHT')

        layout.prop(md, "strength", slider=True)

        use_falloff = (md.falloff_type != 'NONE')

        layout.use_property_split = False
        pref = get_preferences().modifier
        layout.prop(pref, "ghook_falloff", text="Falloff")
        if get_preferences().modifier.ghook_falloff:
            layout.use_property_split = True
            layout.prop(md, "falloff_type")
            layout.prop(md, "falloff_radius")

            if use_falloff:
                if md.falloff_type == 'CURVE':
                    layout.template_curve_mapping(md, "falloff_curve")

            layout.prop(md, "use_falloff_uniform")

        layout.use_property_split = False
        pref = get_preferences().modifier
        layout.prop(pref, "ghook_influence", text="Influence")
        if get_preferences().modifier.ghook_influence:
            layout.use_property_split = True
            self.gpencil_masking(self, layout, ob, md, False)

        layout.separator()

    def GP_OFFSET(self, layout, ob, md):
        layout.use_property_split = True
        layout.use_property_decorate = True
        layout.separator()

        layout.column().prop(md, "location")
        layout.column().prop(md, "rotation")
        layout.column().prop(md, "scale")

        layout.use_property_split = False
        pref = get_preferences().modifier
        layout.prop(pref, "goffset_influence", text="Influence")
        if get_preferences().modifier.goffset_influence:
            layout.use_property_split = True
            self.gpencil_masking(self, layout, ob, md, True)

        layout.separator()

    def GP_ARMATURE(self, layout, ob, md):
        layout.use_property_split = True
        layout.use_property_decorate = True
        layout.separator()

        layout.prop(md, "object")

        row = layout.row(align=True)
        layout.use_property_split = False
        row.prop_search(md, "vertex_group", ob, "vertex_groups")
        layout.use_property_split = True
        sub = row.row(align=True)
        sub.active = bool(md.vertex_group)
        sub.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')

        col = layout.column(heading='Bind to')
        col.prop(md, "use_vertex_groups", text="Vertex Groups")
        col.prop(md, "use_bone_envelopes", text="Bone Envelopes")

        layout.separator()

    def GP_MULTIPLY(self, layout, ob, md):

        layout.use_property_split = True
        layout.use_property_decorate = True
        layout.separator()


        layout.prop(md, "duplicates")
        subcol = layout.column()
        subcol.enabled = md.duplicates > 0
        subcol.prop(md, "distance")
        subcol.prop(md, "offset", slider=True)

        subcol.separator()

        layout.use_property_split = False
        layout.prop(md, "use_fade")
        if md.use_fade:
            layout.use_property_split = True
            layout.prop(md, "fading_center")
            layout.prop(md, "fading_thickness", slider=True)
            layout.prop(md, "fading_opacity", slider=True)

        layout.use_property_split = False
        pref = get_preferences().modifier
        layout.prop(pref, "gmulistroke_influence", text="Influence")
        if get_preferences().modifier.gmulistroke_influence:
            layout.use_property_split = True
            self.gpencil_masking(self, layout, ob, md, False)

        layout.separator()