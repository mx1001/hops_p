import bpy

from bpy.types import Panel
from math import radians
from ... icons import get_icon_id
from ... ui.hops_helper.utility import draw_panel, init_panels
from ... preferences import get_preferences
from ... import bl_info

def menu():
    wm = bpy.context.window_manager
    option = wm.Hard_Ops_button_options

    if 'options' not in option.panels:
        option.name = 'HardOps Helper'

        new = option.panels.add()
        new.name = 'options'

        new.operators.add().name = 'Operators'
        # new.tool.add().name = 'Tool'

    return option


class HOPS_PT_Button(Panel):
    bl_label = f'''HOps: {bl_info['version'][0]}.{bl_info['version'][1]}.{bl_info['version'][2]}_{bl_info['version'][3]}'''
    bl_description = f'''{bl_info['description']}'''
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HardOps'

    panels: dict = {}
    label: bool = False
    mods: list = []

    def draw(self, context):
        layout = self.layout
        wm = bpy.context.window_manager
        button = wm.Hard_Ops_button_options

        if not button.context:
            button.context = 'OPERATORS'
        # option = options()

        # split = layout.split(factor=0.1, align=True)
        row = layout.column().row()

        # column = split.column(align=True)
        row.scale_x = 1.25
        row.scale_y = 1.25

        if self.is_popover:
            layout.ui_units_x = 8

        label = {
            'OPERATORS': ' ',
            'TOOL': 'Render',
            'OPT': 'Opt-ins',
            'KITOPS': ' ',
            'HELPER': f'''{bl_info['version'][0]}.{bl_info['version'][1]}{bl_info['version'][2]}.{bl_info['version'][3]} Helper''',
            'BEVEL_HELPER': 'Bevel Helper',
            'HELP': ' ',
            'KEYMAP': 'Hops Keymap'}

        if button.context not in {'OPERATORS', 'KITOPS'}:
            row.label(text=label[button.context])

        else:
            row.alignment = 'RIGHT'

        row.prop(menu(), 'context', expand=True, icon_only=True)
        layout.separator()

        column = layout.column()

        if button.context == 'OPERATORS':

            #column.label(text=f"HOps: {bl_info['version'][1]}.{bl_info['version'][2]}{bl_info['version'][3]}.{bl_info['version'][4]}")
            if get_preferences().needs_update == 'Connection Failed':
                column.label(text=f'''{bl_info['description']}''')
                column.operator("hops.about", text = f"HOps: {bl_info['version'][0]}.{bl_info['version'][1]}.{bl_info['version'][2]}_{bl_info['version'][3]}",  icon_value=get_icon_id("logo_grey"))
            elif get_preferences().needs_update:# and not 'Connection Failed':
                column.label(text=f'''{bl_info['description']}''', icon='ERROR')
                column.operator("hops.about", text = f"HOps: {bl_info['version'][0]}.{bl_info['version'][1]}.{bl_info['version'][2]}_{bl_info['version'][3]}",  icon_value=get_icon_id("logo_red"))

                split = column.row(align=True)
                row = split.row(align=True)
                col = row.column(align=True)
                col.scale_x = 1.5
                col.scale_y = 1.5

                row.operator("wm.url_open", text="", icon_value=get_icon_id("bmarket")).url = "https://www.blendermarket.com/account/orders"
                row.operator("wm.url_open", text="", icon_value=get_icon_id("artstation")).url = "https://www.artstation.com/marketplace/orders"
                row.operator("wm.url_open", text="", icon_value=get_icon_id("gumroad")).url = "https://gumroad.com/library"
                row.label(text="Update")
                row.operator("wm.url_open", text="", icon="INFO").url = "https://hardops-manual.readthedocs.io/en/latest/faq/#how-do-i-update-hard-ops-boxcutter"
            else:
                column.label(text=f'''{bl_info['description']}''')
                column.operator("hops.about", text = f"HOps: {bl_info['version'][0]}.{bl_info['version'][1]}.{bl_info['version'][2]}_{bl_info['version'][3]}",  icon_value=get_icon_id("logo_green"))

            #column.label(text=f"{bl_info['description']}")


            object = context.active_object
            
            if object is None or len(bpy.context.selected_objects) == 0:
                column.label(text='No Selection')

            elif object and object.mode == 'OBJECT' and object.type == 'MESH':
                column.separator()
                #box = column.box().column()
                column.label(text='Operators')
                box = column.box().column()
                #box.operator("hops.soft_sharpen", text="(S) Sharpen", icon_value=get_icon_id("Ssharpen"))
                #box.operator("hops.complex_sharpen", text="(C) Sharpen", icon_value=get_icon_id("CSharpen"))
                box.operator("hops.sharpen", text="Sharpen", icon_value=get_icon_id("Ssharpen"))
                box.operator("hops.adjust_bevel", text="Bevel", icon_value=get_icon_id("AdjustBevel"))
                #box.operator("hops.apply_modifiers", text="Smart Apply", icon_value=get_icon_id("Applyall"))
                box.operator("hops.mirror_array", text="Mirror / Array", icon_value=get_icon_id("Mirror"))

                column.separator()
                column.label(text='Modifiers')

                maincol = layout.box().column()
                split = maincol.row(align=True)
                row = split.row(align=True)
                col = row.column(align=True)
                col.scale_x = 1.25
                col.scale_y = 1.25

                col.operator("hops.adjust_tthick", text="", icon="MOD_SOLIDIFY")
                col.operator("hops.mod_screw", text="", icon="MOD_SCREW")
                col.operator("hops.mod_simple_deform", text="", icon="MOD_SIMPLEDEFORM")
                col.operator("hops.mod_shrinkwrap", text="", icon="MOD_SHRINKWRAP")
                row = split.row(align=True)
                col = row.column(align=True)
                col.scale_x = 1.25
                col.scale_y = 1.25

                if get_preferences().property.menu_array_type == 'ST3':
                    col.operator("hops.super_array", text="", icon_value=get_icon_id("Display_operators"))
                elif get_preferences().property.menu_array_type == 'ST3_V2':
                    col.operator("hops.st3_array", text="", icon_value=get_icon_id("GreyArrayX"))
                else:
                    col.operator("hops.adjust_array", text="", icon="MOD_ARRAY")
                col.operator("hops.mod_triangulate", text="", icon="MOD_TRIANGULATE")
                col.operator("hops.mod_wireframe", text="", icon="MOD_WIREFRAME")
                col.operator("hops.mod_cast", text="", icon="MOD_CAST")
                row = split.row(align=True)
                col = row.column(align=True)
                col.scale_x = 1.25
                col.scale_y = 1.25

                col.operator("hops.mod_lattice", text="", icon="MOD_LATTICE")
                col.operator("hops.mod_weighted_normal", text="", icon="MOD_NORMALEDIT")
                col.operator("hops.mod_displace", text="", icon="MOD_DISPLACE")
                col.operator("hops.mod_decimate", text="", icon="MOD_DECIM")
                row = split.row(align=True)
                col = row.column(align=True)
                col.scale_x = 1.25
                col.scale_y = 1.25

                col.operator("hops.adjust_bevel", text="", icon="MOD_BEVEL")
                col.operator("hops.mod_subdivision", text="", icon="MOD_SUBSURF")
                # col.operator("hops.mod_displace", text="", icon="MOD_DISPLACE")
                col.operator("hops.mod_weld", text="", icon="AUTOMERGE_OFF")
                col.operator("hops.mod_apply", text="", icon="REC")

                split.separator()
                split.separator()
                split.separator()

                row = split.row(align=True)
                col = row.column(align=True)
                col.scale_x = 1.25
                col.scale_y = 1.25

                col.operator("hops.bool_difference", text="", icon_value=get_icon_id("red"))
                col.operator("hops.bool_union", text="", icon_value=get_icon_id("green"))
                #col.operator("hops.bool_intersect", text="", icon_value=get_icon_id("orange"))
                col.operator("hops.bool_inset", text="", icon_value=get_icon_id("purple"))
                col.operator("hops.slash", text="", icon_value=get_icon_id("yellow"))

                if context.active_object and context.active_object.type == "MESH":
                    column = self.layout.column()
                    column.label(text='Shading')
                    box = column.box().column()

                    mesh = bpy.context.object.data
                    box.prop(mesh, "use_auto_smooth", text="Autosmooth")

                    row = column.row(align=True)
                    box = column.row().column()
                    row.operator('hops.set_autosmoouth', text='10').angle = radians(10)
                    row.operator('hops.set_autosmoouth', text='15').angle = radians(15)
                    row.operator('hops.set_autosmoouth', text='30').angle = radians(30)
                    row.operator('hops.set_autosmoouth', text='45').angle = radians(45)
                    row.operator('hops.set_autosmoouth', text='60').angle = radians(60)

                    box = column.box().column()
                    if bpy.context.object.data.use_auto_smooth == True:
                        box.prop(mesh, "auto_smooth_angle", text="Angle")

                    box.operator("object.shade_smooth", text="Smooth")
                    box.operator("object.shade_flat", text="Flat")

                    column.label(text='Materials')
                    box = column.box().column()
                    box.operator("material.hops_new", text = 'Add Blank Material', icon="PLUS")
                    box.operator("hops.material_scroll", text = 'Material Scroll', icon_value=get_icon_id("StatusReset"))

                    column.label(text='Lights')
                    box = column.box().column()
                    box.operator("hops.blank_light", text = 'Blank Light', icon='LIGHT')

            elif object and object.mode == "EDIT" and object.type == "MESH":
                maincol = layout.box().column()
                split = maincol.row(align=True)
                row = split.row(align=True)
                col = row.column(align=True)
                col.scale_x = 1.25
                col.scale_y = 1.25

                box = column.box().column()
                box.separator()
                column.separator()
                row = split.row(align=True)
                box.operator_context = 'INVOKE_DEFAULT'
                box.operator("hops.edit_multi_tool", text="Mark", icon_value=get_icon_id("MakeSharpE"))

                column.label(text='Modifiers / Booleans')
                box = column.box().column()

                row = split.row(align=True)
                box.menu("HOPS_MT_ModSubmenu", text = 'Add Modifier',  icon_value=get_icon_id("Tris"))
                box.menu("HOPS_MT_BoolSumbenu", text="Booleans", icon_value=get_icon_id("Booleans"))
                box.separator()

                column.label(text='Operations')
                box = column.box().column()

                box.operator("hops.edge2curve", text="Curve/Extract", icon_value=get_icon_id("Curve"))
                box.operator("view3d.vertcircle", text="Circle ", icon_value=get_icon_id("NthCircle"))
                box.operator("hops.bool_dice", text="Dice", icon_value=get_icon_id("NGui"))
                box.operator_context = 'INVOKE_DEFAULT'
                box.operator("hops.flatten_align", text="Reset Axis/Align/Select", icon_value=get_icon_id("Xslap"))
                #box.operator("hops.to_shape", text="To_Shape", icon_value=get_icon_id("Display_boolshapes"))
                #box.operator("hops.reset_axis_modal", text="Flatten", icon_value=get_icon_id("Xslap"))

                box.separator()
                # if get_preferences().property.st3_meshtools:
                box.operator("hops.edit_mesh_macro", text="EM Macro", icon="RADIOBUT_OFF")
                box.menu("HOPS_MT_ST3MeshToolsSubmenu", text="ST3 Mesh Tools", icon="MESH_ICOSPHERE")
                box.separator()
                # else:
                #     box.prop(get_preferences().property, 'st3_meshtools', text='ST3 Meshtools Unlock')

                column.label(text='Menus')
                box = column.box().column()

                box.menu("HOPS_MT_MeshOperatorsSubmenu", text="Operations", icon_value=get_icon_id("StatusOveride"))
                if bpy.context.object and bpy.context.object.type == 'MESH':
                    box.menu("HOPS_MT_MaterialListMenu", text="Material List", icon_value=get_icon_id("StatusOveride"))

                row = split.row(align=True)
                column.label(text='Materials')
                box = column.box().column()
                box.operator("material.hops_new", text = 'Add Blank Material', icon="PLUS")
                box.operator("hops.material_scroll", text = 'Material Scroll', icon_value=get_icon_id("StatusReset"))

            elif object and object.mode == "SCULPT" and object.type == "MESH":
                box = column.box().column()
                box.operator("view3d.sculpt_ops_window", text="Brush", icon="BRUSH_DATA")
                box.operator("sculpt.toggle_brush", text="Toggle Brush")
                layout.separator()
                box.operator_context = "INVOKE_DEFAULT"
                box.operator("sculpt.decimate_mesh", text="Decimate Mesh")
                if context.sculpt_object.use_dynamic_topology_sculpting == False:
                    box.prop(context.active_object.data, 'remesh_voxel_size', text='Voxel Size')
                    box.operator("view3d.voxelizer", text = "Voxel Remesh")
                box.separator()
                box.operator_context = "INVOKE_DEFAULT"
                box.operator("view3d.sculpt_ops_window", text="Brush", icon="BRUSH_DATA")
                box.separator()
            elif object.mode == "PAINT_GPENCIL":
                column.label(text='Grease')
                box = column.box().column()
                box.operator("hops.mirror_gizmo", text="Mirror", icon_value=get_icon_id("Mirror"))
                box.operator("hops.copy_move", text="Copy / Move", icon_value=get_icon_id("dots"))
                box.operator("hops.surfaceoffset", text="Surface OffSet", icon_value=get_icon_id("Display_dots"))
            else:
                column.label(text='No Selection')
                column.label(text='Lights')
                box = column.box().column()
                box.operator("hops.blank_light", text = 'Blank Light', icon='LIGHT')

        elif button.context == 'TOOL':
            if self.is_popover:
                layout.ui_units_x = 11
            # column.label(text='Render')

            scene = context.scene
            rd = scene.render
            props = scene.eevee
            box = column.box().column()

            if rd.has_multiple_engines:
                box.prop(rd, "engine")#, text="Render Engine")

            if bpy.context.scene.render.engine == 'CYCLES':
                box = column.box().column()
                box.operator("renderb.setup", text="Cycles LQ")
                box.operator("render.setup", text="Cycles HQ")
                box = column.box().column()
                box.operator("hops.blank_light", text = 'Blank Light', icon='LIGHT')
                box.operator("hops.adjust_viewport", text="Lookdev+ ", icon_value=get_icon_id("RGui"))
                box = column.box().column()

                expandable_header(button, box, 'render_expand')

            elif bpy.context.scene.render.engine == 'BLENDER_EEVEE':
                box = column.box().column()
                box.operator("hops.adjust_viewport", text="Lookdev+ / Adjust Lookdev", icon_value=get_icon_id("RGui"))
                box.operator("hops.blank_light", text = 'Blank Light', icon='LIGHT')
                box = column.box().column()
                box.operator("renderb.setup", text="Eevee LQ")
                column2 = box.column(align=True)
                row2 = column2.row(align=True)
                row2.prop(get_preferences().property, "Eevee_preset_LQ", expand=True)
                box.operator("render.setup", text="Eevee HQ")
                column2 = box.column(align=True)
                row2 = column2.row(align=True)
                row2.prop(get_preferences().property, "Eevee_preset_HQ", expand=True)
                box = column.box().column()

                expandable_header(button, box, 'render_expand')

            if button.render_expand:
                if bpy.context.scene.render.engine == 'BLENDER_EEVEE':
                    box.prop(props, "taa_render_samples", text="Render")
                    box.prop(props, "taa_samples", text="Viewport")
                    box.prop(props, "use_taa_reprojection")

                    # box = column.box().column()
                    box.separator()
                    box.prop(props, "use_gtao", text="Ambient Occlusion")

                    if scene.eevee.use_gtao == True:
                        box.prop(props, "gtao_distance")
                        box.prop(props, "gtao_factor")

                    box.prop(props, "use_ssr", text="Screen Space Reflections")

                    if scene.eevee.use_ssr == True:
                        box.prop(props, "use_ssr_refraction", text="Refraction")

                        if scene.eevee.use_ssr_refraction == True:
                            box.prop(props, "use_ssr_halfres", text = "Half Res Trace")

                    box.prop(props, "use_motion_blur", text="Motion Blur")

                    if scene.eevee.use_motion_blur == True:
                        box.prop(props, "motion_blur_samples")
                        box.prop(props, "motion_blur_shutter")
                    box.prop(props, "use_bloom", text="Bloom")

                    if scene.eevee.use_bloom == True:
                        box.prop(props, "bloom_threshold")
                        box.prop(props, "bloom_intensity")
                        box.prop(props, "bloom_radius")

                    box.prop(props, "use_volumetric_shadows", text="Volumetric Shadows")

                    if scene.eevee.use_volumetric_shadows == True:
                        box.prop(props, "volumetric_shadow_samples", text="Shadow Samples")

                    box.separator()
                    box.prop(rd, "film_transparent", text="Transparent")
                
                elif bpy.context.scene.render.engine == 'CYCLES':
                    column.label(text='TBD')

            box = column.box().column()
            expandable_header(button, box, 'bake_expand')

            if button.bake_expand:
                box.operator("scene.light_cache_bake", text="Bake Indirect Lighting", icon='RENDER_STILL')
                box.operator("scene.light_cache_bake", text="Bake Cubemap Only", icon='LIGHTPROBE_CUBEMAP').subset = 'CUBEMAPS'
                box.label(text="Cube Size")
                box.prop(props, "shadow_cube_size", text="")
                box.label(text="Cascade Size")
                box.prop(props, "shadow_cascade_size", text="")
                box.prop(props, "gi_diffuse_bounces")

            box = column.box().column()

            expandable_header(button, box, 'export_expand')

            if button.export_expand:
                ot = box.operator("export_scene.obj", text="OBJ")
                ot.use_selection = True
                ot.use_triangles = True

                ot = box.operator("export_scene.fbx", text="FBX")
                ot.use_selection = True

                ot = box.operator("wm.alembic_export", text="ABC")
                ot.selected = True

        elif button.context == 'OPT':
            from ... ui.Panels.opt_ins import HOPS_PT_opt_ins as opt_helper

            if self.is_popover:
                layout.ui_units_x = 10

            opt_helper.draw(self, context)

        elif button.context == 'KITOPS':
            from ... ui_popup import HOPS_OT_InsertsPopupPreview as kitops_helper

            if self.is_popover:
                layout.ui_units_x = 8

            kitops_helper.draw(self, context)

        elif button.context == 'HELPER':
            from ... ui.hops_helper import HOPS_OT_helper as hops_helper

            if self.is_popover:
                layout.ui_units_x = 15

            hops_helper.draw(self, context)

        elif button.context == 'BEVEL_HELPER':
            from ... ui.bevel_helper import HOPS_OT_bevel_helper as bevel_helper

            if self.is_popover:
                layout.ui_units_x = 15

            self.mods = [mod for mod in context.active_object.modifiers if mod.type == 'BEVEL']
            # self.draw_bevel = bevel_helper.draw_bevel
            bevel_helper.draw(self, context)

        elif button.context == 'HELP':
            # from .... ui_popup import HOPS_OT_LearningPopup as hops_help
            from ... ui_popup import weblinks

            if self.is_popover:
                layout.ui_units_x = 10

            if get_preferences().needs_update:# and not 'Connection Failed':
                text = "Needs Update"
                layout.label(text=f'''{bl_info['version'][0]}.{bl_info['version'][1]}.{bl_info['version'][2]}.{bl_info['version'][3]} : {text}''', icon='ERROR')
            elif get_preferences().needs_update == 'Connection Failed':
                text = "Unknown"
                layout.label(text=f'''{bl_info['version'][0]}.{bl_info['version'][1]}.{bl_info['version'][2]}.{bl_info['version'][3]} : {text}''', icon='ERROR')
            else:
                text = "Current"
                layout.label(text=f'''{bl_info['version'][0]}.{bl_info['version'][1]}.{bl_info['version'][2]}.{bl_info['version'][3]} : {text}''', icon='FUND')

            box = column.box().column(align=True)
            expandable_header(button, box, 'Help_expand')

            if button.Help_expand:

                split = column.row(align=True)
                row = split.row(align=True)
                col = row.column(align=True)
                col.scale_x = 1.5
                col.scale_y = 1.5
                row.operator("wm.url_open", text="", icon_value=get_icon_id("bmarket")).url = "https://www.blendermarket.com/account/orders"
                row.operator("wm.url_open", text="", icon_value=get_icon_id("artstation")).url = "https://www.artstation.com/marketplace/orders"
                row.operator("wm.url_open", text="", icon_value=get_icon_id("gumroad")).url = "https://gumroad.com/library"
                row.operator("wm.url_open", text="", icon="INFO").url = "https://hardops-manual.readthedocs.io/en/latest/faq/#how-do-i-update-hard-ops-boxcutter"

                for name, url in weblinks:
                    box.operator("wm.url_open", text=name).url = url

        elif button.context == 'KEYMAP':
            from .. property.preference.keymap import HOPS_PT_Keys_info as keymap_draw

            if self.is_popover:
                layout.ui_units_x = 10

            keymap_draw.draw(self, context)

    def draw_bevel(self, context, mod, index=0):
        from ... ui.bevel_helper import HOPS_OT_bevel_helper as bevel_helper

        bevel_helper.draw_bevel(self, context, mod, index=index)


    def expanded(self, context, layout, mod):
        from ... ui.bevel_helper import HOPS_OT_bevel_helper as bevel_helper

        bevel_helper.expanded(self, context, layout, mod)


    def label_row(self, context, layout, path, prop, label='Label'):
        from ... ui.bevel_helper import HOPS_OT_bevel_helper as bevel_helper

        bevel_helper.label_row(self, context, layout, path, prop, label=label)


def expandable_header(button, box, prop):
    row = box.row(align=True)

    sub = row.row(align=True)
    sub.alignment = 'LEFT'
    icon = 'TRIA_DOWN' if getattr(button, prop) else 'TRIA_RIGHT'
    sub.prop(button, prop, text='', icon=icon, emboss=False)
    sub.prop(button, prop, text=prop[:-7].title(), toggle=True, emboss=False)
    sub.prop(button, prop, text=' ', toggle=True, emboss=False)
    row.prop(button, prop, text=' ', toggle=True, emboss=False)
