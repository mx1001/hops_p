import bpy

from bpy.types import Operator

from ... utility import active_tool, addon, active_tool, activate_by_name


class Hardflow_OT_topbar_activate(Operator):
    bl_idname = 'hardflow.topbar_activate'
    bl_label = 'Activate Hardflow'

    def execute(self, context):
        preference = addon.preference()

        if active_tool().idname != 'Hops':
            activate_by_name('Hops')
            self.report({'INFO'}, 'Activated Hardops')

            return {'FINISHED'}

        else:
            return {'PASS_THROUGH'}
