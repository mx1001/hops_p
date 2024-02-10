import bpy


from . import modifier, add, select, tool, topbar, shape, camera, bc_notifications


def register():
    shape.register()
    modifier.register()
    add.register()
    select.register()
    tool.register()
    topbar.register()
    camera.register()
    bc_notifications.register()


def unregister():
    modifier.unregister()
    add.unregister()
    select.unregister()
    tool.unregister()
    topbar.unregister()
    shape.unregister()
    camera.unregister()
    bc_notifications.unregister()
