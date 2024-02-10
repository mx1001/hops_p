import bpy
import re


from bl_ui import (
    properties_object,
    properties_constraint,
    properties_data_modifier,
    properties_data_shaderfx,
    properties_data_mesh,
    properties_data_curve,
    properties_data_metaball,
    properties_data_gpencil,
    # properties_grease_pencil_common,
    properties_data_armature,
    properties_data_bone,
    properties_data_lattice,
    properties_data_empty,
    properties_data_speaker,
    properties_data_camera,
    properties_data_light,
    properties_data_lightprobe,
    properties_material,
    properties_material_gpencil,
)

from bl_ui.properties_animviz import (
    MotionPathButtonsPanel,
    MotionPathButtonsPanel_display,
)

from .. Panels import cutting_material, workflow, sharp_options, bool_options, dice_options, operator_options, mesh_clean_options, special_options, opt_ins, operators
panel_node_draw = None

from ... addon.utility.addon import preference
from ... utility import active_tool
from . mods_data import DATA_PT_modifiers, mods_dic
from . gmods_data import DATA_PT_gpencil_modifiers, gmods_dic
from . con_data import ConstraintButtonsPanel


def options():
    wm = bpy.context.window_manager
    option = wm.Hard_Ops_helper_options

    if 'options' not in option.panels:
        option.name = 'HardOps Helper'

        new = option.panels.add()
        new.name = 'options'

        new.tool.add().name = 'Tool'
        new.object.add().name = 'Object'
        new.constraint.add().name = 'Constraint'
        new.modifier.add().name = 'Modifier'

        data = new.data.add()
        data.name = 'Data'

        data.mesh.add().name = 'Mesh'
        data.curve.add().name = 'Curve'
        data.surface.add().name = 'Surface'
        data.meta.add().name = 'Meta'
        data.font.add().name = 'Font'
        data.gpencil.add().name = 'GPencil'
        data.armature.add().name = 'Armature'
        data.lattice.add().name = 'Lattice'
        data.empty.add().name = 'Empty'
        data.speaker.add().name = 'Speaker'
        data.camera.add().name = 'Camera'
        data.light.add().name = 'Light'
        data.light_probe.add().name = 'Light_Probe'

        new.shaderfx.add().name = 'ShaderFX'
        new.bone.add().name = 'Bone'
        new.bone_constraint.add().name = 'Bone Constraint'
        new.material.add().name = 'Material'

    return option


def expand(pt):
    if not pt:
        return

    context = bpy.context
    wm = context.window_manager
    option = options()
    obj = context.active_object
    # re.split(pattern, string, maxsplit=0, flags=0)
    if not hasattr(pt, 'bl_options') or 'HIDE_HEADER' not in pt.bl_options:
        if option.context != 'DATA':
            panel = getattr(option.panels[0], option.context.lower())[0]
            return getattr(panel, F'expand_{re.split(".*_PT_", pt.__name__)[1]}')

        else:
            panel = getattr(option.panels[0].data[0], obj.type.lower())[0]
            return getattr(panel, F'expand_{re.split(".*_PT_", pt.__name__)[1]}')
    else:
        return True


def header_prop(pt):
    if not pt:
        return

    if pt.__name__ == 'OBJECT_PT_display_bounds':
        return bpy.context.active_object, 'show_bounds'

    elif pt.__name__ == 'DATA_PT_pathanim':
        return bpy.context.active_object.data, 'use_path'

    elif pt.__name__ == 'DATA_PT_camera_safe_areas':
        return bpy.context.active_object.data, 'show_safe_areas'

    elif pt.__name__ == 'DATA_PT_camera_safe_areas_center_cut':
        return bpy.context.active_object.data, 'show_safe_center'

    elif pt.__name__ == 'DATA_PT_camera_background_image':
        return bpy.context.active_object.data, 'show_background_images'

    elif pt.__name__ == 'DATA_PT_display_passepartout':
        return bpy.context.active_object.data, 'show_passepartout'

    elif pt.__name__ == 'DATA_PT_normals_auto_smooth':
        return bpy.context.active_object.data, 'use_auto_smooth'

    elif pt.__name__ == 'DATA_PT_EEVEE_light_distance':
        return bpy.context.active_object.data, 'use_custom_distance'

    elif pt.__name__ == 'DATA_PT_EEVEE_shadow':
        return bpy.context.active_object.data, 'use_shadow'

    elif pt.__name__ == 'DATA_PT_EEVEE_shadow_contact':
        return bpy.context.active_object.data, 'use_contact_shadow'

    elif pt.__name__ == 'DATA_PT_lightprobe_parallax':
        return bpy.context.active_object.data, 'use_custom_parallax'

    elif pt.__name__ == 'BONE_PT_deform':
        if active_tool().mode == 'POSE':
            bone = bpy.context.active_object.data.bones[bpy.context.active_pose_bone.name]
        else:
            bone = bpy.context.active_object.data.bones[bpy.context.active_bone.name]
        return bone, 'use_deform'

    return None


def header_presets(pt):
    return None


def child_panels(pt, ot):
    items = []
    for panel in ot.panels[options().context]:
        if hasattr(panel, 'bl_parent_id') and panel.bl_parent_id == pt.__name__:
            items.append(panel)

    return items


def init_panels(ot):
    context = bpy.context
    option = options()

    ot.panels = {
        'OPERATORS': [
            operators.HOPS_PT_operators],
        'TOOL': [
            special_options.HOPS_PT_specialoptions,
            workflow.HOPS_PT_workflow,
            sharp_options.HOPS_PT_sharp_options,
            bool_options.HOPS_PT_bool_options,
            dice_options.HOPS_PT_dice_options,
            mesh_clean_options.HOPS_PT_mesh_clean_options,
            operator_options.HOPS_PT_operator_options,
            opt_ins.HOPS_PT_opt_ins],

        'OBJECT': [],
        'CONSTRAINT': [],
        'MODIFIER': [],
        'SHADERFX': [],
        'DATA': [],
        # 'BONE': [],
        # 'BONE_CONSTRAINT': [],
        'MATERIAL': []}

    obj = context.active_object
    if obj:
        if bpy.app.version < (2, 90, 0):
            ot.panels['OBJECT'] = [
                properties_object.OBJECT_PT_context_object,
                properties_object.OBJECT_PT_transform,
                properties_object.OBJECT_PT_delta_transform,
                properties_object.OBJECT_PT_relations,
                properties_object.OBJECT_PT_display,
                properties_object.OBJECT_PT_display_bounds
                ]
        else:
            ot.panels['OBJECT'] = [
                properties_object.OBJECT_PT_context_object,
                properties_object.OBJECT_PT_transform,
                properties_object.OBJECT_PT_delta_transform,
                properties_object.OBJECT_PT_relations,
                properties_object.OBJECT_PT_display,
                ]

        ot.panels['CONSTRAINT'] = [
            properties_constraint.OBJECT_PT_constraints]

        if obj.type in {'MESH', 'CURVE', 'SURFACE', 'FONT', 'META', 'GPENCIL', 'LATTICE'}:
            if obj.type != 'GPENCIL':
                ot.panels['MODIFIER'] = [properties_data_modifier.DATA_PT_modifiers]
            else:
                ot.panels['MODIFIER'] = [properties_data_modifier.DATA_PT_gpencil_modifiers]
                ot.panels['SHADERFX'] = [properties_data_shaderfx.DATA_PT_shader_fx]

        if obj.type == 'MESH':
            if bpy.app.version < (2, 90, 0):
                ot.panels['DATA'] = [
                    properties_data_mesh.DATA_PT_context_mesh,
                    properties_data_mesh.DATA_PT_vertex_groups,
                    properties_data_mesh.DATA_PT_shape_keys,
                    properties_data_mesh.DATA_PT_uv_texture,
                    properties_data_mesh.DATA_PT_vertex_colors,
                    properties_data_mesh.DATA_PT_face_maps,
                    properties_data_mesh.DATA_PT_normals,
                    properties_data_mesh.DATA_PT_normals_auto_smooth,
                    properties_data_mesh.DATA_PT_texture_space,
                    getattr(properties_data_mesh, 'DATA_PT_remesh', None),
                    properties_data_mesh.DATA_PT_customdata]
            else:
                ot.panels['DATA'] = [
                    properties_data_mesh.DATA_PT_context_mesh,
                    properties_data_mesh.DATA_PT_vertex_groups,
                    properties_data_mesh.DATA_PT_shape_keys,
                    properties_data_mesh.DATA_PT_uv_texture,
                    properties_data_mesh.DATA_PT_vertex_colors,
                    properties_data_mesh.DATA_PT_face_maps,
                    properties_data_mesh.DATA_PT_normals,
                    # properties_data_mesh.DATA_PT_normals_auto_smooth,
                    properties_data_mesh.DATA_PT_texture_space,
                    getattr(properties_data_mesh, 'DATA_PT_remesh', None),
                    properties_data_mesh.DATA_PT_customdata]

        elif obj.type in {'CURVE', 'SURFACE', 'FONT'}:
            ot.panels['DATA'] = [
                properties_data_curve.DATA_PT_context_curve,
                properties_data_curve.DATA_PT_shape_curve,
                properties_data_curve.DATA_PT_geometry_curve,
                properties_data_curve.DATA_PT_geometry_curve_bevel,
                properties_data_curve.DATA_PT_pathanim,
                properties_data_curve.DATA_PT_active_spline,
                properties_data_curve.DATA_PT_curve_texture_space]

            if obj.type != 'FONT':
                ot.panels['DATA'].append(properties_data_mesh.DATA_PT_shape_keys)
            else:
                ot.panels['DATA'].append(properties_data_curve.DATA_PT_font)
                ot.panels['DATA'].append(properties_data_curve.DATA_PT_font_transform)
                ot.panels['DATA'].append(properties_data_curve.DATA_PT_paragraph)
                ot.panels['DATA'].append(properties_data_curve.DATA_PT_paragraph_alignment)
                ot.panels['DATA'].append(properties_data_curve.DATA_PT_paragraph_spacing)
                ot.panels['DATA'].append(properties_data_curve.DATA_PT_text_boxes)


        elif obj.type == 'META':
            ot.panels['DATA'] = [
                properties_data_metaball.DATA_PT_context_metaball,
                properties_data_metaball.DATA_PT_metaball,
                properties_data_metaball.DATA_PT_metaball_element,
                properties_data_metaball.DATA_PT_mball_texture_space]

        elif obj.type == 'GPENCIL':
            ot.panels['DATA'] = [
                properties_data_gpencil.DATA_PT_gpencil_layers,
                properties_data_gpencil.DATA_PT_gpencil_onion_skinning,
                properties_data_gpencil.DATA_PT_gpencil_vertex_groups,
                properties_data_gpencil.DATA_PT_gpencil_strokes,
                properties_data_gpencil.DATA_PT_gpencil_display,
                properties_data_gpencil.DATA_PT_gpencil_canvas]

            if context.active_gpencil_layer:
                ot.panels['DATA'].extend([
                    properties_data_gpencil.DATA_PT_gpencil_layer_adjustments,
                    properties_data_gpencil.DATA_PT_gpencil_layer_relations])

        elif obj.type == 'ARMATURE':
            ot.panels['DATA'] = [
                properties_data_armature.DATA_PT_context_arm,
                properties_data_armature.DATA_PT_skeleton,
                properties_data_armature.DATA_PT_display,
                properties_data_armature.DATA_PT_bone_groups,
                properties_data_armature.DATA_PT_pose_library,
                properties_data_armature.DATA_PT_iksolver_itasc]

            ot.panels['BONE'] = [
                properties_data_bone.BONE_PT_context_bone,
                properties_data_bone.BONE_PT_transform,
                properties_data_bone.BONE_PT_curved,
                properties_data_bone.BONE_PT_relations,
                properties_data_bone.BONE_PT_display,
                properties_data_bone.BONE_PT_inverse_kinematics,
                properties_data_bone.BONE_PT_deform]

            ot.panels['BONE_CONSTAINT'] = [properties_constraint.BONE_PT_constraints]

        elif obj.type == 'LATTICE':
            ot.panels['DATA'] = [
                properties_data_lattice.DATA_PT_context_lattice,
                properties_data_lattice.DATA_PT_lattice,
                properties_data_mesh.DATA_PT_vertex_groups,
                properties_data_mesh.DATA_PT_shape_keys]

        elif obj.type == 'EMPTY':
            ot.panels['DATA'] = [properties_data_empty.DATA_PT_empty]

        elif obj.type == 'SPEAKER':
            ot.panels['DATA'] = [
                properties_data_speaker.DATA_PT_context_speaker,
                properties_data_speaker.DATA_PT_speaker,
                properties_data_speaker.DATA_PT_distance,
                properties_data_speaker.DATA_PT_cone]

        elif obj.type == 'CAMERA':
            if context.scene.render.engine in {'BLENDER_WORKBENCH', 'BLENDER_EEVEE'}:
                ot.panels['DATA'] = [
                    properties_data_camera.DATA_PT_context_camera,
                    properties_data_camera.DATA_PT_lens,
                    properties_data_camera.DATA_PT_camera_dof,
                    properties_data_camera.DATA_PT_camera_dof_aperture,
                    properties_data_camera.DATA_PT_camera_stereoscopy,
                    properties_data_camera.DATA_PT_camera,
                    properties_data_camera.DATA_PT_camera_safe_areas,
                    properties_data_camera.DATA_PT_camera_safe_areas_center_cut,
                    properties_data_camera.DATA_PT_camera_background_image,
                    properties_data_camera.DATA_PT_camera_display,
                    properties_data_camera.DATA_PT_camera_display_passepartout]

            else:
                from cycles import ui

                ot.panels['DATA'] = [
                    properties_data_camera.DATA_PT_context_camera,
                    properties_data_camera.DATA_PT_lens,
                    ui.CYCLES_CAMERA_PT_camera_dof,
                    ui.CYCLES_CAMERA_PT_camera_dof_aperture,
                    ui.CYCLES_CAMERA_PT_camera_dof_viewport,
                    properties_data_camera.DATA_PT_camera_stereoscopy,
                    properties_data_camera.DATA_PT_camera,
                    properties_data_camera.DATA_PT_camera_safe_areas,
                    properties_data_camera.DATA_PT_camera_background_image,
                    properties_data_camera.DATA_PT_camera_display,
                    properties_data_camera.DATA_PT_camera_display_passepartout]

        elif obj.type == 'LIGHT':
            if context.scene.render.engine == 'BLENDER_WORKBENCH':
                ot.panels['DATA'] = [
                    properties_data_light.DATA_PT_context_light,
                    properties_data_light.DATA_PT_preview,
                    properties_data_light.DATA_PT_light,
                    properties_data_light.DATA_PT_area]


            elif context.scene.render.engine == 'BLENDER_EEVEE':
                ot.panels['DATA'] = [
                    properties_data_light.DATA_PT_context_light,
                    properties_data_light.DATA_PT_preview,
                    properties_data_light.DATA_PT_EEVEE_light,
                    properties_data_light.DATA_PT_EEVEE_light_distance,
                    properties_data_light.DATA_PT_spot,
                    properties_data_light.DATA_PT_EEVEE_shadow,
                    properties_data_light.DATA_PT_EEVEE_shadow_contact]

                if bpy.context.active_object.data.type == 'SUN':
                    ot.panels['DATA'].append(properties_data_light.DATA_PT_EEVEE_shadow_cascaded_shadow_map)

            else:
                from cycles import ui

                ot.panels['DATA'] = [
                    properties_data_light.DATA_PT_context_light,
                    ui.CYCLES_LIGHT_PT_preview,
                    ui.CYCLES_LIGHT_PT_light,
                    ui.CYCLES_LIGHT_PT_nodes,
                    ui.CYCLES_LIGHT_PT_spot]

        elif obj.type == 'LIGHT_PROBE':
            ot.panels['DATA'] = [
                properties_data_lightprobe.DATA_PT_context_lightprobe,
                properties_data_lightprobe.DATA_PT_lightprobe,
                properties_data_lightprobe.DATA_PT_lightprobe_visibility,
                properties_data_lightprobe.DATA_PT_lightprobe_parallax,
                properties_data_lightprobe.DATA_PT_lightprobe_display]

        if obj.type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'GPENCIL'}:
            if obj.type != 'GPENCIL':
                if context.scene.render.engine == 'BLENDER_WORKBENCH':
                    ot.panels['MATERIAL'] = [
                        properties_material.EEVEE_MATERIAL_PT_context_material,
                        properties_material.MATERIAL_PT_viewport,
                        cutting_material.HOPS_PT_material_hops]

                elif context.scene.render.engine == 'BLENDER_EEVEE':
                    ot.panels['MATERIAL'] = [
                        properties_material.EEVEE_MATERIAL_PT_context_material,
                        properties_material.MATERIAL_PT_preview,
                        properties_material.EEVEE_MATERIAL_PT_surface,
                        properties_material.EEVEE_MATERIAL_PT_volume,
                        properties_material.MATERIAL_PT_viewport,
                        properties_material.EEVEE_MATERIAL_PT_settings,
                        cutting_material.HOPS_PT_material_hops]

                else:
                    from cycles import ui

                    ot.panels['MATERIAL'] = [
                        ui.CYCLES_PT_context_material,
                        ui.CYCLES_MATERIAL_PT_preview,
                        ui.CYCLES_MATERIAL_PT_surface,
                        ui.CYCLES_MATERIAL_PT_volume,
                        ui.CYCLES_MATERIAL_PT_displacement,
                        properties_material.MATERIAL_PT_viewport,
                        ui.CYCLES_MATERIAL_PT_settings,
                        ui.CYCLES_MATERIAL_PT_settings_surface,
                        ui.CYCLES_MATERIAL_PT_settings_volume,
                        cutting_material.HOPS_PT_material_hops]
            else:
                ot.panels['MATERIAL'] = [
                    properties_material_gpencil.MATERIAL_PT_gpencil_slots,
                    properties_material_gpencil.MATERIAL_PT_gpencil_preview,
                    properties_material_gpencil.MATERIAL_PT_gpencil_surface,
                    properties_material_gpencil.MATERIAL_PT_gpencil_strokecolor,
                    properties_material_gpencil.MATERIAL_PT_gpencil_fillcolor,
                    properties_material_gpencil.MATERIAL_PT_gpencil_options]


class context_copy:


    def __init__(self):
        copy = bpy.context.copy()

        obj = copy['active_object']
        if obj:
            copy['object'] = obj

            copy['curve'] = obj.data
            copy[obj.type.lower()] = obj.data
            copy['material'] = obj.active_material

            copy['space_data'] = None
            for area in copy['workspace'].screens[0].areas:
                if area.type == 'PROPERTIES':
                    copy['space_data'] = area.spaces[0]

            if len(obj.material_slots):
                copy['material_slot'] = obj.material_slots[obj.active_material_index]
            else:
                copy['material_slot'] = None

            copy['armature'] = obj.data
            copy['pose_bone'] = copy['active_pose_bone']
            copy['bone'] = obj.data.bones[copy['pose_bone'].name] if active_tool().mode == 'POSE' else None
            copy['edit_bone'] = copy['active_bone']
            copy['lightprobe'] = obj.data if obj.type == 'LIGHT_PROBE' else None
            copy['meta_ball'] = obj.data if obj.type == 'META' else None

        for key in copy:
            setattr(self, key, copy[key])


    def __new__(self):
        self.__init__(self)

        return self


class draw_panel:


    def __init__(self, ot, pt, layout):
        if not pt:
            return

        context = context_copy()
        self.bl_space_type = 'PROPERTIES'

        if (not hasattr(pt, 'poll') or pt.poll(context)) and not hasattr(pt, 'bl_parent_id'):
            if options().context not in {'MODIFIER', 'CONSTRAINT', 'BONE_CONSTAINT', 'SHADERFX', 'OPERATORS'}:
                self.layout = layout.box()
            else:
                self.layout = layout

            self.layout.operator_context = 'INVOKE_DEFAULT'

            option_context = {'nothing'}
            if bpy.app.version > (2, 89, 0):
                option_context = {'CONSTRAINT', 'BONE_CONSTAINT'}

            if options().context in option_context:
                layout.operator_menu_enum("object.constraint_add", "type", text="Add Object Constraint")
                panel = ConstraintButtonsPanel
                ob = context.object
                for con in ob.constraints:
                    box = layout.column()
                    col = box.column(align=True)
                    col.separator()

                    row = col.row(align=True)
                    row.prop(con, 'show_expanded', text="")
                    row.template_constraint_header(con)

                    if con.show_expanded:
                        row = box.row(align=True)
                        getattr(panel, con.type)(panel, context, box, con)

            else:
                self.setup_overrides(pt)

                bl_options = getattr(pt, 'bl_options') if hasattr(pt, 'bl_options') else None
                if (bl_options and 'HIDE_HEADER' not in bl_options) or not bl_options:
                    self.header(pt, context, expand(pt), header_prop(pt), header_presets(pt))

                if (bl_options and 'HIDE_HEADER' in bl_options) or expand(pt):
                    self.panel(pt, context)

                if expand(pt):
                    for child in child_panels(pt, ot):
                        if (bl_options and 'HIDE_HEADER' not in bl_options) or not bl_options:
                            self.layout = layout.box()
                            self.header(child, context, expand(child), header_prop(child), header_presets(child))

                        if (bl_options and 'HIDE_HEADER' in bl_options) or expand(child):
                            self.panel(child, context)

    def header(self, pt, context, expand, prop=None, presets=None, emboss=False):
        layout = self.layout

        if options().context != 'DATA':
            option = getattr(options().panels[0], options().context.lower())[0]
        else:
            obj = context.active_object
            option = getattr(options().panels[0].data[0], obj.type.lower())[0]

        expand_prop = F'expand_{re.split(".*_PT_", pt.__name__)[1]}'

        row = layout.row(align=True)
        row.alignment = 'LEFT'
        row.prop(option, expand_prop, text='', icon=F'DISCLOSURE_TRI_{"DOWN" if expand else "RIGHT"}', emboss=emboss)
        if prop:
            row.prop(prop[0], prop[1], text='')

        row.prop(option, expand_prop, toggle=True, text=pt.bl_label, emboss=emboss)
        sub = row.row(align=True)
        sub.scale_x = 0.70
        sub.prop(option, expand_prop, toggle=True, text=' ', emboss=emboss)


    def panel(self, pt, context):
        if options().context not in {'MODIFIER', 'SHADERFX'} and (options().context != 'MATERIAL' or not hasattr(self, 'draw')):
            pt.draw(self, context)
        else:
            self.draw(self, context)


    def setup_overrides(self, pt):
        global panel_node_draw

        option = options()
        obj = bpy.context.active_object

        if bpy.context.scene.render.engine in {'BLENDER_WORKBENCH', 'BLENDER_EEVEE'}:
            from bl_ui.properties_material import panel_node_draw
        else:
            from cycles.ui import panel_node_draw

        if option.context in {'CONSTRAINT', 'BONE_CONSTAINT'}:
            panel = properties_constraint.ConstraintButtonsPanel

            def draw_constraint(context, con):
                layout = self.layout

                box = layout.template_constraint(con)

                if box:
                    getattr(panel, con.type)(panel, context, box, con)

                    if con.type not in {'RIGID_BODY_JOINT', 'NULL'}:
                        box.prop(con, 'influence')

            self.draw_constraint = draw_constraint

        elif option.context == 'MODIFIER' and obj.type != 'GPENCIL':


            def profile_buttons(layout, ob, md):
                if md.type == 'BEVEL' and getattr(md, 'use_custom_profile', True) == True and getattr(md, 'profile_type', 'CUSTOM') == 'CUSTOM':
                    row = layout.row(align=True)
                    op = row.operator('hops.save_bevel_profile', text='Save Profile')
                    op.obj, op.mod = ob.name, md.name
                    op = row.operator('hops.load_bevel_profile', text='Load Profile')
                    op.obj, op.mod = ob.name, md.name


            def draw(self, context):
                layout = self.layout

                ob = context.object

                # layout.operator_menu_enum('object.modifier_add', 'type')

                row = layout.row(align=True)
                row.operator_menu_enum("object.modifier_add", "type")
                # row.operator("hops.bool_toggle_viewport", text="", icon="HIDE_OFF")
                row.operator("hops.open_modifiers", text="", icon="TRIA_DOWN")
                row.operator("hops.collapse_modifiers", text="", icon="TRIA_UP")

                if bpy.app.version < (2, 90, 0):

                    panel = properties_data_modifier.DATA_PT_modifiers
                    for md in ob.modifiers:
                        box = layout.template_modifier(md)
                        if box:
                            getattr(panel, md.type)(panel, box, ob, md)
                            profile_buttons(box, ob, md)

                else:
                    panel = DATA_PT_modifiers
                    for md in ob.modifiers:
                        box = layout.column()
                        col = box.column(align=True)
                        col.separator()

                        row = col.row(align=True)
                        row.prop(md, 'show_expanded', text="")

                        row.label(icon=f"{mods_dic.get(md.type)}")

                        row.prop(md, 'name', text="")
                        row.prop(md, 'show_on_cage', text="")
                        row.prop(md, 'show_in_editmode', text="")
                        row.prop(md, 'show_viewport', text="")
                        row.prop(md, 'show_render', text="")

                        up = row.operator("object.modifier_move_up", text="", icon="TRIA_UP")
                        up.modifier = md.name
                        down = row.operator("object.modifier_move_down", text="", icon="TRIA_DOWN")
                        down.modifier = md.name
                        remove = row.operator("object.modifier_remove", text="", icon="X")
                        remove.modifier = md.name

                        if md.show_expanded:
                            row = box.row()
                            apply_ = row.operator("object.modifier_apply", text="Apply")
                            # apply_.apply_as = 'DATA'
                            apply_.modifier = md.name
                            copy = row.operator("object.modifier_copy", text="Copy")
                            copy.modifier = md.name

                            getattr(panel, md.type)(panel, box, ob, md)


            self.draw = draw

        elif option.context == 'MODIFIER' and obj.type == 'GPENCIL':
            panel = properties_data_modifier.DATA_PT_gpencil_modifiers

            def draw(self, context):
                layout = self.layout

                ob = context.object

                # layout.operator_menu_enum('object.gpencil_modifier_add', 'type')
                row = layout.row(align=True)
                row.operator_menu_enum("object.gpencil_modifier_add", "type")
                # row.operator("hops.bool_toggle_viewport", text="", icon="HIDE_OFF")
                row.operator("hops.open_modifiers", text="", icon="TRIA_DOWN")
                row.operator("hops.collapse_modifiers", text="", icon="TRIA_UP")

                if bpy.app.version < (2, 90, 0):

                    panel = properties_data_modifier.DATA_PT_gpencil_modifiers
                    for md in ob.grease_pencil_modifiers:
                        box = layout.template_greasepencil_modifier(md)
                        if box:
                            # match enum type to our functions, avoids a lookup table.
                            getattr(panel, md.type)(panel, box, ob, md)

                else:
                    panel = DATA_PT_gpencil_modifiers
                    for md in ob.grease_pencil_modifiers:
                        box = layout.column()
                        col = box.column(align=True)
                        col.separator()

                        row = col.row(align=True)
                        row.prop(md, 'show_expanded', text="")

                        row.label(icon=f"{gmods_dic.get(md.type)}")

                        row.prop(md, 'name', text="")
                        row.prop(md, 'show_in_editmode', text="")
                        row.prop(md, 'show_viewport', text="")
                        row.prop(md, 'show_render', text="")

                        up = row.operator("object.gpencil_modifier_move_up", text="", icon="TRIA_UP")
                        up.modifier = md.name
                        down = row.operator("object.gpencil_modifier_move_down", text="", icon="TRIA_DOWN")
                        down.modifier = md.name
                        remove = row.operator("object.gpencil_modifier_remove", text="", icon="X")
                        remove.modifier = md.name

                        if md.show_expanded:
                            row = box.row()
                            apply_ = row.operator("object.gpencil_modifier_apply", text="Apply")
                            apply_.apply_as = 'DATA'
                            apply_.modifier = md.name
                            copy = row.operator("object.gpencil_modifier_copy", text="Copy")
                            copy.modifier = md.name

                            getattr(panel, md.type)(panel, box, ob, md)

            self.draw = draw

        elif option.context == 'SHADERFX':
            panel = properties_data_shaderfx.DATA_PT_shader_fx

            def draw(self, context):
                layout = self.layout

                ob = context.object

                layout.operator_menu_enum('object.shaderfx_add', 'type')

                for fx in ob.shader_effects:
                    box = layout.template_shaderfx(fx)
                    if box:
                        # match enum type to our functions, avoids a lookup table.
                        getattr(panel, fx.type)(panel, box, fx)

            self.draw = draw

        elif option.context == 'DATA' and obj and obj.type == 'GPENCIL':

            def draw_layers(context, layout, gpd):

                row = layout.row()

                col = row.column()
                layer_rows = 7
                col.template_list('GPENCIL_UL_layer', '', gpd, 'layers', gpd.layers, 'active_index',
                                  rows=layer_rows, sort_reverse=True, sort_lock=True)

                gpl = context.active_gpencil_layer
                if gpl:
                    srow = col.row(align=True)
                    srow.prop(gpl, 'blend_mode', text='Blend')

                    srow = col.row(align=True)
                    srow.prop(gpl, 'opacity', text='Opacity', slider=True)
                    srow.prop(gpl, 'mask_layer', text='',
                              icon='MOD_MASK' if gpl.mask_layer else 'LAYER_ACTIVE')

                    srow = col.row(align=True)
                    srow.prop(gpl, 'use_solo_mode', text='Show Only On Keyframed')

                col = row.column()

                sub = col.column(align=True)
                sub.operator('gpencil.layer_add', icon='ADD', text='')
                sub.operator('gpencil.layer_remove', icon='REMOVE', text='')

                if gpl:
                    sub.menu('GPENCIL_MT_layer_context_menu', icon='DOWNARROW_HLT', text='')

                    if len(gpd.layers) > 1:
                        col.separator()

                        sub = col.column(align=True)
                        sub.operator('gpencil.layer_move', icon='TRIA_UP', text='').type = 'UP'
                        sub.operator('gpencil.layer_move', icon='TRIA_DOWN', text='').type = 'DOWN'

                        col.separator()

                        sub = col.column(align=True)
                        sub.operator('gpencil.layer_isolate', icon='LOCKED', text='').affect_visibility = False
                        sub.operator('gpencil.layer_isolate', icon='RESTRICT_VIEW_ON', text='').affect_visibility = True

            self.draw_layers = draw_layers

        elif option.context == 'MATERIAL':

            if pt.__name__ == 'CYCLES_PT_context_material':
                def draw(self, context):
                    layout = self.layout

                    mat = context.material
                    ob = context.object
                    slot = context.material_slot
                    space = context.space_data

                    if ob:
                        is_sortable = len(ob.material_slots) > 1
                        rows = 1
                        if (is_sortable):
                            rows = 4

                        row = layout.row()

                        row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index", rows=rows)

                        col = row.column(align=True)
                        col.operator("object.material_slot_add", icon='ADD', text="")
                        col.operator("object.material_slot_remove", icon='REMOVE', text="")

                        col.menu("MATERIAL_MT_context_menu", icon='DOWNARROW_HLT', text="")

                        if is_sortable:
                            col.separator()

                            col.operator("object.material_slot_move", icon='TRIA_UP', text="").direction = 'UP'
                            col.operator("object.material_slot_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

                        if ob.mode == 'EDIT':
                            row = layout.row(align=True)
                            row.operator("object.material_slot_assign", text="Assign")
                            row.operator("object.material_slot_select", text="Select")
                            row.operator("object.material_slot_deselect", text="Deselect")

                    split = layout.split(factor=0.65)

                    if ob:
                        split.template_ID(ob, "active_material", new="hops.helper_add_mat")
                        #split.template_ID(ob, "active_material", new="material.hops_new")
                        row = split.row()

                        if slot:
                            row.prop(slot, "link", text="")
                        else:
                            row.label()
                    elif mat:
                        split.template_ID(space, "pin_id")
                        split.separator()

                self.draw = draw

            elif pt.__name__ == 'EEVEE_MATERIAL_PT_context_material':
                def draw(self, context):
                    layout = self.layout

                    mat = context.material
                    ob = context.object
                    slot = context.material_slot
                    space = context.space_data

                    if ob:
                        is_sortable = len(ob.material_slots) > 1
                        rows = 3
                        if is_sortable:
                            rows = 5

                        row = layout.row()

                        row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index", rows=rows)

                        col = row.column(align=True)
                        col.operator("object.material_slot_add", icon='ADD', text="")
                        col.operator("object.material_slot_remove", icon='REMOVE', text="")

                        col.separator()

                        col.menu("MATERIAL_MT_context_menu", icon='DOWNARROW_HLT', text="")

                        if is_sortable:
                            col.separator()

                            col.operator("object.material_slot_move", icon='TRIA_UP', text="").direction = 'UP'
                            col.operator("object.material_slot_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

                    row = layout.row()

                    if ob:
                        row.template_ID(ob, "active_material", new="hops.helper_add_mat")
                        #row.template_ID(ob, "active_material", new="material.hops_new")

                        if slot:
                            icon_link = 'MESH_DATA' if slot.link == 'DATA' else 'OBJECT_DATA'
                            row.prop(slot, "link", icon=icon_link, icon_only=True)

                        if ob.mode == 'EDIT':
                            row = layout.row(align=True)
                            row.operator("object.material_slot_assign", text="Assign")
                            row.operator("object.material_slot_select", text="Select")
                            row.operator("object.material_slot_deselect", text="Deselect")

                    elif mat:
                        row.template_ID(space, "pin_id")

                self.draw = draw

            elif pt.__name__ == 'MATERIAL_PT_viewport':
                def draw_shared(self, mat):
                    layout = self.layout
                    layout.use_property_split = True

                    col = layout.column()
                    col.prop(mat, 'diffuse_color', text='Color')
                    col.prop(mat, 'metallic')
                    col.prop(mat, 'roughness')

                self.draw_shared = draw_shared

            elif pt.__name__ == 'EEVEE_MATERIAL_PT_settings':
                def draw_shared(self, mat):
                    layout = self.layout
                    layout.use_property_split = True

                    layout.prop(mat, "blend_method")

                    if mat.blend_method != 'OPAQUE':
                        layout.prop(mat, "transparent_shadow_method")

                        row = layout.row()
                        row.active = ((mat.blend_method == 'CLIP') or (mat.transparent_shadow_method == 'CLIP'))
                        row.prop(mat, "alpha_threshold")

                    if mat.blend_method not in {'OPAQUE', 'CLIP', 'HASHED'}:
                        layout.prop(mat, "show_transparent_back")

                    layout.prop(mat, "use_screen_refraction")
                    layout.prop(mat, "refraction_depth")
                    layout.prop(mat, "use_sss_translucency")
                    layout.prop(mat, "pass_index")

                self.draw_shared = draw_shared

class HOPS_OT_helper_add_mat(bpy.types.Operator):
    bl_idname = "hops.helper_add_mat"
    bl_label = "Hops Helper mat add"
    bl_description = """Add a new material

Shift - Glass Material per object
Alt - Emission Material per object

"""
    bl_options = {'INTERNAL', 'UNDO'}
    
    def invoke (self, contex, event):
        #blank material passthrough
        bpy.ops.material.hops_new('INVOKE_DEFAULT', helper_call = True)

        return {'FINISHED'}
        