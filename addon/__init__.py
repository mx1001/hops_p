__all__ = ('menu', 'operator', 'panel', 'property', 'utility', 'icon', 'keymap', 'pie', 'topbar')


import bpy

from bpy.utils import register_class, unregister_class

from . import menu, operator, panel, property, keymap, pie, topbar, gizmo, handler


def register():
    menu.register()
    operator.register()
    # gizmo.register()
    panel.register()
    property.register()
    keymap.register()
    pie.register()
    topbar.register()
    handler.register()


def unregister():
    menu.unregister()
    operator.unregister()
    # gizmo.unregister()
    panel.unregister()
    property.unregister()
    keymap.unregister()
    pie.unregister()
    topbar.unregister()
    handler.unregister()
