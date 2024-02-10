import bpy
from ... utils.context import ExecutionContext


class HOPS_OT_ResetStatus(bpy.types.Operator):
    bl_idname = "hops.reset_status"
    bl_label = "Reset Status"
    bl_description = """Resets properties related to hops w/ selected mesh
    EX: reset a boolshape to a normal mesh
    """
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        object = bpy.context.active_object
        if hasattr(object, 'cycles_visibility'):
            if bpy.context.scene.render.engine == 'CYCLES':
                enableCyclesVisibility(object)
        enableVisibility(object)
        object.hops.status = "UNDEFINED"
        try:
            bpy.data.collections['Hardops'].objects.unlink(object)
        except:
            pass

        # bpy.ops.object.mode_set(mode='EDIT')
        # original_selection_mode = tuple(bpy.context.tool_settings.mesh_select_mode)
        # bpy.context.tool_settings.mesh_select_mode = (False, True, False)
        # bpy.ops.mesh.mark_sharp(clear=True)
        # bpy.ops.transform.edge_bevelweight(value=-1)
        # bpy.ops.transform.edge_crease(value=-1)
        # bpy.context.tool_settings.mesh_select_mode = original_selection_mode
        # bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.hops.display_notification(info="Status Reset")


        return {"FINISHED"}


def enableCyclesVisibility(object):
    with ExecutionContext(mode="OBJECT", active_object=object):
        if bpy.context.scene.render.engine == 'CYCLES':
            if hasattr(object, 'cycles_visibility'):
                bpy.context.object.cycles_visibility.camera = True
                bpy.context.object.cycles_visibility.diffuse = True
                bpy.context.object.cycles_visibility.glossy = True
                bpy.context.object.cycles_visibility.transmission = True
                bpy.context.object.cycles_visibility.scatter = True
                bpy.context.object.cycles_visibility.shadow = True
            bpy.context.object.display_type = 'SOLID'

        else:
            pass

def enableVisibility(object):
    with ExecutionContext(mode="OBJECT", active_object=object):
        #Enable Renderability
        bpy.context.object.hide_render = False
        bpy.context.object.display_type = 'TEXTURED'
