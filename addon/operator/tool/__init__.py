import bpy


from . import editmesh, object


def register():
    object.register()
    editmesh.register()


def unregister():
    editmesh.unregister()
    object.unregister()
