import bpy

from bpy.types import Menu
from bpy.utils import register_class, unregister_class

from . import icon
from . utility import active_tool, addon, active_tool


class HARDFLOW_MT_pie(Menu):
    bl_label = 'BoxCutter'


    @classmethod
    def poll(cls, context):

        return active_tool().idname == 'BoxCutter'


    def draw(self, context):
        layout = self.layout.menu_pie()


classes = [
    HARDFLOW_MT_pie]


def register():

    for cls in classes:
        register_class(cls)


def unregister():

    for cls in classes:
        unregister_class(cls)
