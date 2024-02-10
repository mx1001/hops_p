import bpy

from bpy.utils import register_class, unregister_class
from bpy.types import AddonPreferences
from bpy.props import EnumProperty, PointerProperty, StringProperty, BoolProperty

from . import behavior, display, expand, modifiers, color, info, keymap, links, addons, ui, property
from . operators import operators, mirror
from ....preferences import get_preferences
from ... utility import addon
from .... icons import get_icon_id
from .... import bl_info
from .... utils.blender_ui import get_dpi_factor

# label row text names


class Hardops(AddonPreferences):
    bl_idname = addon.name

    settings: EnumProperty(
        name = 'Settings',
        description = 'Settings to display',
        items = [
            ('UI', 'Ui', ''),
            ('PROPERTY', 'Properties', ''),
            # ('BEHAVIOR', 'Behaviors', ''),
            ('COLOR', 'Color', ''),
            # ('DISPLAY', 'Display', ''),
            ('INFO', 'Info', ''),
            ('KEYMAP', 'Keymap', ''),
            ('LINKS', 'Links/Help', ''),
            ('ADDONS', 'Addons', '')],
        default = 'UI')

    # TODO: add update handler to gizmo toggles that calls gizmo ot

    behavior: PointerProperty(type=behavior.hardflow)
    ui: PointerProperty(type=ui.hops)
    color: PointerProperty(type=color.hops)
    display: PointerProperty(type=display.hardflow)
    expand: PointerProperty(type=expand.hardflow)
    property: PointerProperty(type=property.hops)
    keymap: PointerProperty(type=keymap.hops)
    needs_update: StringProperty()
    wrap_text: BoolProperty(default=True)
    operator: PointerProperty(type=operators)
    modifier: PointerProperty(type=modifiers.props)

    def draw(self, context):
        layout = self.layout

        if self.needs_update:
            col = layout.column_flow()
            row = col.row()
            row.separator()
            row.alert = True
            row.label(text=self.needs_update)

            row.operator("wm.url_open", text="", icon_value=get_icon_id("bmarket")).url = "https://www.blendermarket.com/account/orders"
            row.operator("wm.url_open", text="", icon_value=get_icon_id("artstation")).url = "https://www.artstation.com/marketplace/orders"
            row.operator("wm.url_open", text="", icon_value=get_icon_id("gumroad")).url = "https://gumroad.com/library"
            row.operator("wm.url_open", text="", icon="INFO").url = "https://hardops-manual.readthedocs.io/en/latest/faq/#how-do-i-update-hard-ops-boxcutter"
        else:
            col = layout.column_flow()
            row = col.row()
            row.separator()
            row.label(text='Hardops is up-to-date')

        column = layout.column(align=True)

        row = column.row(align=True)
        row.prop(get_preferences(), 'settings', expand=True)

        box = column.box()
        globals()[get_preferences().settings.lower()].draw(get_preferences(), context, box)
        # context.area.tag_redraw()


class HOPS_OT_pref_helper(bpy.types.Operator):
    bl_idname = 'hops.pref_helper'
    bl_description = f'''Configure the preferences of {bl_info['description']}
    ***save prefs to keep across sessions***

    '''
    bl_label = '''Keymap'''
    bl_options = {'UNDO'}

    panels: dict = {}
    label: bool = False

    @classmethod
    def poll(cls, context): # need a poll for panel lookup
        return True

    def check(self, context):
        return True

    def invoke(self, context, event):
        preference = get_preferences().ui

        self.settings = get_preferences().settings
        self.behavior = get_preferences().behavior
        self.ui = get_preferences().ui
        self.color = get_preferences().color
        self.display = get_preferences().display
        self.expand = get_preferences().expand
        self.property = get_preferences().property
        self.keymap = get_preferences().keymap
        self.needs_update = get_preferences().needs_update
        self.wrap_text = get_preferences().needs_update
        self.operator = get_preferences().operator
        self.modifier = get_preferences().modifier

        get_preferences().wrap_text = False

        if preference.use_helper_popup:
            self.label = True
            return context.window_manager.invoke_popup(self, width=400 * get_dpi_factor(force=False))
        else:
            return context.window_manager.invoke_props_dialog(self, width=400 * get_dpi_factor(force=False))

    def cancel(self, context):
        get_preferences().wrap_text = True
        return {'FINISHED'}

    def execute(self, context):
        get_preferences().wrap_text = True
        return {'FINISHED'}

    def draw(self, context):
        Hardops.draw(self, context)

        row = self.layout.row()

        row.menu("USERPREF_MT_save_load", text="", icon='COLLAPSEMENU')

        prefs = context.preferences

        row.operator_context = 'EXEC_AREA'

        if prefs.use_preferences_save and (not bpy.app.use_userpref_skip_save_on_exit):
            pass
        else:
            # Show '*' to let users know the preferences have been modified.
            row.operator(
                "wm.save_userpref",
                text="Save Preferences{:s}".format(" *" if prefs.is_dirty else ""),
            )


classes = (
    modifiers.props,
    mirror.props,
    operators,
    keymap.hops,
    HOPS_OT_pref_helper,
    property.hops,
    behavior.hardflow,
    color.hops,
    ui.hops,
    display.hardflow,
    expand.hardflow,
    Hardops)


def register():
    for cls in classes:
        register_class(cls)
    ui.update_hops_panels(None,None)


def unregister():
    for cls in classes:
        unregister_class(cls)
