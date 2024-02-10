import bpy

from bpy.app.handlers import persistent, depsgraph_update_post
from . utility import addon


class post:
    bc_running: bool = False


    @persistent
    def depsgraph(_): # do not use for heavy logic
        if not addon.bc():
            return

        if not post.bc_running and bpy.context.scene.bc.running:
            post.bc_running = True

            if addon.preference().display.bc_notifications:
                bpy.ops.hops.bc_notifications()

        elif not bpy.context.scene.bc.running:
            post.bc_running = False


def register():
    depsgraph_update_post.append(post.depsgraph)


def unregister():
    depsgraph_update_post.remove(post.depsgraph)
