import bpy
from bpy.types import Panel

from bl_ui.properties_data_modifier import DATA_PT_modifiers as modifier_old
from ... ui.hops_helper.mods_data import DATA_PT_modifiers as modifier

from .. utility.addon import preference


class HARDFLOW_PT_dots(Panel):
    bl_label = 'Modifier'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOL_HEADER'


    def draw(self, context):
        hardflow = bpy.context.window_manager.hardflow

        obj = context.active_object

        layout = self.layout
        layout.ui_units_x = 15

        layout.label(text=hardflow.dots.description)

        if hardflow.dots.mod:
            mod = obj.modifiers[hardflow.dots.mod]

            if bpy.app.version < (2, 90, 0):

                modifier_ = modifier_old
                mod = obj.modifiers[hardflow.dots.mod]
                box = layout.template_modifier(mod)

                if box:
                    getattr(modifier_, mod.type)(modifier_, box, obj, mod)
                    profile_buttons(box, obj, mod)

            else:
                box = layout.column()
                col = box.column(align=True)
                col.separator()

                row = col.row(align=True)
                row.prop(mod, 'show_expanded', text="")

                # TODO: get correct icons names for all  mods
                try:
                    row.label(icon=f"MOD_{mod.type}")
                except TypeError:
                    row.label(icon="MODIFIER")

                row.prop(mod, 'name', text="")
                row.prop(mod, 'show_on_cage', text="")
                row.prop(mod, 'show_in_editmode', text="")
                row.prop(mod, 'show_viewport', text="")
                row.prop(mod, 'show_render', text="")

                up = row.operator("object.modifier_move_up", text="", icon="TRIA_UP")
                up.modifier = mod.name
                down = row.operator("object.modifier_move_down", text="", icon="TRIA_DOWN")
                down.modifier = mod.name
                remove = row.operator("object.modifier_remove", text="", icon="X")
                remove.modifier = mod.name

                row = box.row()
                apply_ = row.operator("object.modifier_apply", text="Apply")
                # apply_.apply_as = 'DATA'
                apply_.modifier = mod.name
                copy = row.operator("object.modifier_copy", text="Copy")
                copy.modifier = mod.name
                # box.separator()

                getattr(modifier, mod.type)(modifier, box, obj, mod)


def profile_buttons(layout, ob, md):
    if md.type == 'BEVEL' and getattr(md, 'use_custom_profile', True) == True and getattr(md, 'profile_type', 'CUSTOM') == 'CUSTOM':
        row = layout.row(align=True)
        op = row.operator('hops.save_bevel_profile', text='Save Profile')
        op.obj, op.mod = ob.name, md.name
        op = row.operator('hops.load_bevel_profile', text='Load Profile')
        op.obj, op.mod = ob.name, md.name
