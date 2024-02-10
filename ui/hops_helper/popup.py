import bpy
from bpy.props import EnumProperty
from . utility import options, draw_panel, init_panels
from ... preferences import get_preferences
from ... utils.blender_ui import get_dpi_factor
from ... import bl_info


class HOPS_OT_helper(bpy.types.Operator):
    bl_idname = 'hops.helper'
    bl_label = 'HOps Helper '
    bl_description = f'''Display HOps Helper - {bl_info['version'][0]}.{bl_info['version'][1]}.{bl_info['version'][2]}.{bl_info['version'][3]}
    
    HOPS Helper gives access to most things essential to the #b3d experience.
    Modifiers, materials and workflow options are available here.
    *protip: use the hotkey*
    
    '''

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

        if options().context == '':
            options().context = 'TOOL'

        if preference.use_helper_popup:
            self.label = True
            return context.window_manager.invoke_popup(self, width=preference.Hops_helper_width * get_dpi_factor(force=False))
        else:
            return context.window_manager.invoke_props_dialog(self, width=preference.Hops_helper_width * get_dpi_factor(force=False))


    def execute(self, context):
        return {'FINISHED'}


    def draw(self, context):
        layout = self.layout
        option = options()

        if options().context == '':
            options().context = 'TOOL'

        if self.label:
            layout.label(text='HOps Helper')

        split = layout.split(factor=0.1, align=True)

        column = split.column(align=True)
        column.scale_y = 1.25
        column.prop(option, 'context', expand=True, icon_only=True)

        column = split.column()

        init_panels(self)

        for pt in self.panels[option.context]:
            draw_panel(self, pt, column)

        # column.separator()
        column.row()
