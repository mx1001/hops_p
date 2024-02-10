import bpy
import bpy.utils.previews
from bpy.types import WindowManager
from bpy.props import BoolProperty, IntProperty, FloatProperty, EnumProperty
from bpy.props import *
from .. utils.addons import addon_exists
from .. preferences import get_preferences
from ..ui_framework.operator_ui import Master

#############################
# RenderSet1
#############################

# Sets Up The Render / As Always

class HOPS_OT_renset1Operator(bpy.types.Operator):
    '''
    Sets Eevee / Cycles settings to render High Quality
    Configurable in HOPS Dropdown render section

    Enables Cavity / Shadow in viewport shading.
    F9 for fine adjustments

    '''

    bl_idname = 'render.setup'
    bl_label = 'HQ RenderSetup'
    bl_options = {'REGISTER', 'UNDO'}

    use_square_samples: BoolProperty(name="use_square_samples", default=True)
    sample_clamp_indirect: IntProperty(name="sample_clamp_indirect", default=2)
    sample_clamp_direct: IntProperty(name="sample_clamp_direct", default=2)
    preview_samples: IntProperty(name="preview_samples", default=40)
    samples: IntProperty(name="samples", default=15)
    min_bounces: IntProperty(name="min_bounces", default=5)
    glossy_bounces: IntProperty(name="glossy_bounces", default=16)
    diffuse_bounces: IntProperty(name="diffuse_bounces", default=16)
    blur_glossy: FloatProperty(name="blur_glossy", default=1)
    sample_as_light: BoolProperty(name="sample_as_light", default=True)
    sample_map_resolution: IntProperty(name="sample_map_resolution", default=512)
    light_sampling_threshold: IntProperty(name="light_sampling_threshold", default=0)


    use_gtao: BoolProperty(name="use_gtao", default=True)
    use_ssr: BoolProperty(name="use_ssr", default=True)
    use_ssr_halfres: BoolProperty(name="use_ssr_halfres", default=False)
    use_soft_shadows: BoolProperty(name="use_soft_shadows", default=True)
    use_shadow_high_bitdepth: BoolProperty(name="use_shadow_high_bitdepth", default=True)
    gi_diffuse_bounces: IntProperty(name="gi_diffuse_bounces", default=4)
    taa_samples: IntProperty(name="taa_samples", default=64)
    show_shadows: BoolProperty(name="show_shadows", default=True)
    show_cavity: BoolProperty(name="show_cavity", default=True)
    use_scene_lights: BoolProperty(name="use_scene_lights", default=True)
    curvature_valley_factor: FloatProperty(name="curvature_valley_factor", default=0.745455)
    curvature_ridge_factor: FloatProperty(name="curvature_ridge_factor", default=0.690909)
    cavity_valley_factor: FloatProperty(name="cavity_valley_factor", default=0.475)
    cavity_ridge_factor: FloatProperty(name="cavity_ridge_factor", default=0.225)

    called_ui = False

    def __init__(self):

        HOPS_OT_renset1Operator.called_ui = False

    def draw(self, context):
        layout = self.layout
        column = layout.column(align=True)

        if context.scene.render.engine == 'CYCLES':
            column.prop(self, "use_square_samples")
            column.prop(self, "sample_clamp_indirect")
            column.prop(self, "sample_clamp_direct")
            column.prop(self, "preview_samples")
            column.prop(self, "samples")
            column.prop(self, "min_bounces")
            column.prop(self, "glossy_bounces")
            column.prop(self, "diffuse_bounces")
            column.prop(self, "blur_glossy")
            column.prop(self, "sample_as_light")
            column.prop(self, "sample_map_resolution")
            column.prop(self, "light_sampling_threshold")

        if context.scene.render.engine == 'BLENDER_EEVEE':

            column.prop(self, "use_gtao")
            column.prop(self, "use_ssr")
            column.prop(self, "use_ssr_halfres")
            column.prop(self, "use_soft_shadows")
            column.prop(self, "use_shadow_high_bitdepth")

            row = column.row(align=True)
            row.prop(get_preferences().property, "Eevee_preset_HQ", expand=True)

            column.prop(self, "gi_diffuse_bounces")
            column.prop(self, "taa_samples")
            column.prop(self, "show_shadows")
            column.prop(self, "show_cavity")
            column.prop(self, "use_scene_lights")
            column.prop(self, "curvature_valley_factor")
            column.prop(self, "curvature_ridge_factor")
            column.prop(self, "cavity_valley_factor")
            column.prop(self, "cavity_ridge_factor")

    def execute(self, context):
        c = bpy.context.scene
        c2 = bpy.context.space_data.shading

        if c.render.engine == 'CYCLES':
            c.cycles.progressive = 'PATH'
            c.cycles.use_square_samples = self.use_square_samples
            c.cycles.sample_clamp_indirect = self.sample_clamp_indirect
            c.cycles.sample_clamp_direct = self.sample_clamp_direct
            c.cycles.preview_samples = self.preview_samples
            c.cycles.samples = self.samples
            c.cycles.min_bounces = self.min_bounces
            c.cycles.glossy_bounces = self.glossy_bounces
            c.cycles.diffuse_bounces = self.diffuse_bounces
            c.cycles.blur_glossy = self.blur_glossy
            c.world.cycles.sample_as_light = self.sample_as_light
            c.world.cycles.sample_map_resolution = self.sample_map_resolution
            c.cycles.light_sampling_threshold = self.light_sampling_threshold
        if c.render.engine == 'BLENDER_EEVEE':
            c.render.engine = 'BLENDER_EEVEE'
            c.eevee.use_gtao = self.use_gtao
            c.eevee.use_ssr = self.use_ssr
            c.eevee.use_ssr_halfres = self.use_ssr_halfres
            c.eevee.use_soft_shadows = self.use_soft_shadows
            c.eevee.use_shadow_high_bitdepth = self.use_shadow_high_bitdepth
            c.eevee.shadow_cube_size = get_preferences().property.Eevee_preset_HQ
            c.eevee.gi_cubemap_resolution = get_preferences().property.Eevee_preset_HQ
            c.eevee.shadow_cascade_size = get_preferences().property.Eevee_preset_HQ
            c.eevee.gi_diffuse_bounces = self.gi_diffuse_bounces
            c.eevee.taa_samples = self.taa_samples

            #Shading
            c2.show_shadows = self.show_shadows
            c2.show_cavity = self.show_cavity
            c2.use_scene_lights = self.use_scene_lights
            c2.cavity_type = 'BOTH'
            c2.curvature_valley_factor = self.curvature_valley_factor
            c2.curvature_ridge_factor = self.curvature_ridge_factor
            c2.cavity_valley_factor = self.cavity_valley_factor
            c2.cavity_ridge_factor = self.cavity_ridge_factor

        else:
            pass

        # Operator UI
        if not HOPS_OT_renset1Operator.called_ui:
            HOPS_OT_renset1Operator.called_ui = True

            ui = Master()

            if c.render.engine == 'BLENDER_EEVEE':
                draw_data = [
                    ["Eevee HQ "],
                    ["Eevee configured to high quality", ""],
                    ["Resolution", get_preferences().property.Eevee_preset_HQ],
                    ["Soft Shadows", self.use_soft_shadows],
                    ["Reflections", self.use_ssr],
                    ["Viewport Cavity/Shadows ", self.show_cavity],
                    ]
            else:
                draw_data = [
                    ["Cycles HQ "],
                    ["Cycles configured to high quality", ""],
                    ["Samples", self.samples],
                    ["Preview Samples", self.preview_samples],
                    ["Glossy Bounces", self.glossy_bounces]
                    ]
            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return {'FINISHED'}

#############################
# RenderSet2
#############################

# Sets Up The Render / As Always
class HOPS_OT_renset2Operator(bpy.types.Operator):
    '''
    Sets Eevee / Cycles settings to render Lower Quality
    Configurable in HOPS Dropdown render section

    Disables Cavity / Shadow in viewport shading.
    F9 for fine adjustments

    '''
    bl_idname = "renderb.setup"
    bl_label = "LQ RenderSetup"
    bl_options = {'REGISTER', 'UNDO'}

    use_square_samples: BoolProperty(name="use_square_samples", default=True)
    sample_clamp_indirect: IntProperty(name="sample_clamp_indirect", default=10)
    sample_clamp_direct: IntProperty(name="sample_clamp_direct", default=0)
    preview_samples: IntProperty(name="preview_samples", default=40)
    samples: IntProperty(name="samples", default=40)
    min_bounces: IntProperty(name="min_bounces", default=5)
    glossy_bounces: IntProperty(name="glossy_bounces", default=8)
    transparent_max_bounces: IntProperty(name="transparent_max_bounces", default=8)
    transmission_bounces: IntProperty(name="transmission_bounces", default=8)
    volume_bounces: IntProperty(name="volume_bounces", default=8)
    diffuse_bounces: IntProperty(name="diffuse_bounces", default=8)
    blur_glossy: FloatProperty(name="blur_glossy", default=1)
    sample_map_resolution: IntProperty(name="sample_map_resolution", default=512)
    light_sampling_threshold: IntProperty(name="light_sampling_threshold", default=0)
    caustics_reflective: BoolProperty(name="caustics_reflective", default=True)
    caustics_refractive: BoolProperty(name="caustics_refractive", default=True)

    use_gtao: BoolProperty(name="use_gtao", default=False)
    use_ssr: BoolProperty(name="use_ssr", default=False)
    use_bloom: BoolProperty(name="use_bloom", default=False)
    use_ssr_halfres: BoolProperty(name="use_ssr_halfres", default=True)
    use_soft_shadows: BoolProperty(name="use_soft_shadows", default=False)
    use_taa_reprojection: BoolProperty(name="use_taa_reprojection", default=False)
    use_shadow_high_bitdepth: BoolProperty(name="use_shadow_high_bitdepth", default=False)
    gi_diffuse_bounces: IntProperty(name="gi_diffuse_bounces", default=2)
    taa_samples: IntProperty(name="taa_samples", default=2)
    show_shadows: BoolProperty(name="show_shadows", default=False)
    show_cavity: BoolProperty(name="show_cavity", default=False)

    called_ui = False

    def __init__(self):

        HOPS_OT_renset2Operator.called_ui = False

    def draw(self, context):
        layout = self.layout
        column = layout.column(align=True)

        if context.scene.render.engine == 'CYCLES':

            column.prop(self, "use_square_samples")
            column.prop(self, "sample_clamp_indirect")
            column.prop(self, "sample_clamp_direct")
            column.prop(self, "preview_samples")
            column.prop(self, "samples")
            column.prop(self, "min_bounces")
            column.prop(self, "glossy_bounces")
            column.prop(self, "transparent_max_bounces")
            column.prop(self, "transmission_bounces")
            column.prop(self, "volume_bounces")
            column.prop(self, "diffuse_bounces")
            column.prop(self, "blur_glossy")
            column.prop(self, "sample_map_resolution")
            column.prop(self, "light_sampling_threshold")
            column.prop(self, "caustics_reflective")
            column.prop(self, "caustics_refractive")

        if context.scene.render.engine == 'BLENDER_EEVEE':

            column.prop(self, "use_gtao")
            column.prop(self, "use_ssr")
            column.prop(self, "use_bloom")
            column.prop(self, "use_ssr_halfres")
            column.prop(self, "use_soft_shadows")
            column.prop(self, "use_taa_reprojection")
            column.prop(self, "use_shadow_high_bitdepth")
            column.prop(self, "gi_diffuse_bounces")

            row = column.row(align=True)
            row.prop(get_preferences().property, "Eevee_preset_LQ", expand=True)

            column.prop(self, "taa_samples")
            column.prop(self, "show_shadows")
            column.prop(self, "show_cavity")

    def execute(self, context):
        c = bpy.context.scene
        c2 = bpy.context.space_data.shading
        if bpy.context.scene.render.engine == 'CYCLES':
            c.cycles.progressive = 'PATH'
            c.cycles.use_square_samples = self.use_square_samples
            c.cycles.samples = self.samples
            c.cycles.glossy_bounces = self.glossy_bounces
            c.cycles.transparent_max_bounces = self.transparent_max_bounces
            c.cycles.transmission_bounces = self.transmission_bounces
            c.cycles.volume_bounces = self.volume_bounces
            c.cycles.diffuse_bounces = self.diffuse_bounces
            c.cycles.sample_clamp_direct = self.sample_clamp_direct
            c.cycles.sample_clamp_indirect = self.sample_clamp_indirect
            c.cycles.blur_glossy = self.blur_glossy
            c.cycles.caustics_reflective = self.caustics_reflective
            c.cycles.caustics_refractive = self.caustics_refractive
            c.cycles.device = 'GPU'
        if c.render.engine == 'BLENDER_EEVEE':
            c.render.engine = 'BLENDER_EEVEE'
            c.eevee.use_gtao = self.use_gtao
            c.eevee.use_ssr = self.use_ssr
            #c.eevee.use_dof = self.use_dof
            c.eevee.use_bloom = self.use_bloom
            c.eevee.use_shadow_high_bitdepth = self.use_shadow_high_bitdepth
            c.eevee.use_taa_reprojection = self.use_taa_reprojection
            c.eevee.use_ssr_halfres = self.use_ssr_halfres
            c.eevee.use_soft_shadows = self.use_soft_shadows
            #bpy.context.space_data.overlay.show_overlays = True
            c.eevee.shadow_cube_size = get_preferences().property.Eevee_preset_LQ
            c.eevee.gi_cubemap_resolution = get_preferences().property.Eevee_preset_LQ
            c.eevee.shadow_cascade_size = get_preferences().property.Eevee_preset_LQ
            c.eevee.taa_samples = self.taa_samples
            #Shading
            c2.show_shadows = self.show_shadows
            c2.show_cavity = self.show_cavity
        else:
            pass

        # Operator UI
        if not HOPS_OT_renset2Operator.called_ui:
            HOPS_OT_renset2Operator.called_ui = True

            ui = Master()

            if c.render.engine == 'BLENDER_EEVEE':
                draw_data = [
                    ["Eevee LQ "],
                    ["Eevee configured to low quality", ""],
                    ["Resolution", get_preferences().property.Eevee_preset_LQ],
                    ["Soft Shadows", self.use_soft_shadows],
                    ["Reflections", self.use_ssr],
                    ["Viewport Cavity/Shadows ", self.show_cavity]
                    ]
            else:
                draw_data = [
                    ["Cycles LQ "],
                    ["Cycles configured to low quality", ""],
                    ["Samples", self.samples],
                    ["Preview Samples", self.preview_samples],
                    ["Glossy Bounces", self.glossy_bounces]
                    ]
            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return {'FINISHED'}

#############################
# RenderSet3
#############################

class HOPS_OT_renset3Operator(bpy.types.Operator):
    '''
    Sets Eevee / Cycles settings to render HighQuality
    '''

    bl_idname = 'renderc.setup'
    bl_label = 'RenderSetupc'
    bl_options = {'REGISTER', 'UNDO'}

    colmgm : BoolProperty(default=False)

    def draw(self, context):
        layout = self.layout
        column = layout.column(align=True)
        row = column.row(align=True)
        row.prop(get_preferences().property, "Eevee_preset_HQ", expand=True)

    def execute(self, context):
        c = bpy.context.scene
        c2 = bpy.context.space_data.shading

        if c.render.engine == 'CYCLES':
            c.cycles.device = 'GPU'
            c.render.tile_x = 256
            c.render.tile_y = 256
            c.view_settings.look = 'High Contrast'
            c.cycles.progressive = 'PATH'
            c.cycles.use_square_samples = True
            c.cycles.sample_clamp_indirect = 2
            c.cycles.sample_clamp_direct = 2
            c.cycles.preview_samples = 40
            c.cycles.samples = 25
            c.cycles.min_bounces = 5
            c.cycles.max_bounces = 16
            c.cycles.diffuse_bounces = 16
            c.cycles.glossy_bounces = 16
            c.cycles.transparent_max_bounces = 16
            c.cycles.transmission_bounces = 16
            c.cycles.volume_bounces = 0
            c.cycles.blur_glossy = 0.8
            c.world.cycles.sample_as_light = True
            c.world.cycles.sample_map_resolution = 2048
            c.cycles.light_sampling_threshold = 0
        if c.render.engine == 'BLENDER_EEVEE':
            c.render.engine = 'BLENDER_EEVEE'
            c.eevee.use_gtao = True
            c.eevee.use_ssr = True
            c.eevee.use_ssr_halfres = False
            c.eevee.use_soft_shadows = True
            c.eevee.use_shadow_high_bitdepth = True
            c.eevee.shadow_cube_size = get_preferences().property.Eevee_preset_HQ
            c.eevee.gi_cubemap_resolution = get_preferences().property.Eevee_preset_HQ
            c.eevee.shadow_cascade_size = get_preferences().property.Eevee_preset_HQ
            c.eevee.gi_diffuse_bounces = 4
            c.eevee.taa_samples = 64

            #Shading
            c2.show_shadows = True
            c2.show_cavity = True
            c2.use_scene_lights = True
            c2.cavity_type = 'BOTH'
            c2.curvature_valley_factor = 0.745455
            c2.curvature_ridge_factor = 0.690909
            c2.cavity_valley_factor = 0.475
            c2.cavity_ridge_factor = 0.225

        else:
            pass

        return {'FINISHED'}


#############################
# Set UI Ops Start Here
#############################

# Return The UI Back To Normal


class HOPS_OT_ReguiOperator(bpy.types.Operator):
    """
    Solid / Texture Toggle

    Toggle general viewport and material view in viewport.
    Useful for uprez tasks and tasks involving a material reference

    """
    bl_idname = "ui.reg"
    bl_label = "regViewport"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.context.space_data.shading.type = 'SOLID'
        if bpy.context.space_data.shading.light != 'FLAT':
            bpy.context.space_data.shading.light = 'FLAT'
            bpy.context.space_data.shading.color_type = 'TEXTURE'
        else:
            bpy.context.space_data.shading.light = 'STUDIO'
            bpy.context.space_data.shading.color_type = 'MATERIAL'
        return {'FINISHED'}


# Attempting To Clean Up UI For A Clean Workspace

class HOPS_OT_CleanuiOperator(bpy.types.Operator):
    """
    Regular viewport elements hidden / simplified view.

    """
    bl_idname = "ui.clean"
    bl_label = "cleanViewport"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        c = bpy.context.screen
        if bpy.context.scene.render.engine == 'BLENDER_EEVEE':
            bpy.context.space_data.overlay.show_overlays = False
        if bpy.context.scene.render.engine == 'CYCLES':
            bpy.context.space_data.overlay.show_overlays = True
        else:
            pass
        return {'FINISHED'}

# Sets the final frame. Experimental


class HOPS_OT_EndframeOperator(bpy.types.Operator):
    """Frame Range Popup

    Allows user to specify start / end frame

    """
    bl_idname = "setframe.end"
    bl_label = "Frame Range"
    bl_options = {'REGISTER', 'UNDO'}

    #this should be a property next to the option

    firstframe: IntProperty(name="StartFrame", description="SetStartFrame.", default=1, min=1, max=20000)
    lastframe: IntProperty(name="EndFrame", description="SetStartFrame.", default=6000, min=1, max=20000)

    def execute(self, context):
        lastframe = self.lastframe  # needed to get var involved
        firstframe = self.firstframe
        bpy.context.scene.frame_start = firstframe
        bpy.context.scene.frame_end = lastframe
        if get_preferences().ui.Hops_extra_info:
            bpy.ops.hops.display_notification(info=f"Last Frame: {lastframe}", name="")
        return {'FINISHED'}

# Sets the final frame. Experimental


class HOPS_OT_MeshdispOperator(bpy.types.Operator):
    """
    Hides Marked Edges from view.

    """
    bl_idname = "hops.meshdisp"
    bl_label = "Mesh Disp"
    bl_options = {'REGISTER', 'UNDO'}

    # this should be a property next to the option

    # firstframe = IntProperty(name="StartFrame", description="SetStartFrame.", default=1, min = 1, max = 20000)
    # lastframe = IntProperty(name="EndFrame", description="SetStartFrame.", default=100, min = 1, max = 20000)

    def execute(self, context):
        if bpy.context.space_data.overlay.show_edge_sharp:
            bpy.context.space_data.overlay.show_edge_crease = False
            bpy.context.space_data.overlay.show_edge_sharp = False
            bpy.context.space_data.overlay.show_edge_bevel_weight = False
            bpy.context.space_data.overlay.show_edge_seams = False
        else:
            bpy.context.space_data.overlay.show_edge_crease = True
            bpy.context.space_data.overlay.show_edge_sharp = True
            bpy.context.space_data.overlay.show_edge_bevel_weight = True
            bpy.context.space_data.overlay.show_edge_seams = True

        return {'FINISHED'}
