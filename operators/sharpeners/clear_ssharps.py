import bpy
from bpy.props import BoolProperty
import bpy.utils.previews
from ... preferences import get_preferences
from ...ui_framework.operator_ui import Master

# _____________________________________________________________clear ssharps (OBJECT MODE)________________________


class HOPS_OT_ClearCustomData(bpy.types.Operator):
    bl_idname = "clean.customdata"
    bl_label = "Clean Custom Data"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """clean custom data"""

    def execute(self, context):
        active = bpy.context.active_object
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                bpy.ops.mesh.customdata_custom_splitnormals_clear()
        bpy.context.view_layer.objects.active = active
        return {'FINISHED'}


class HOPS_OT_UnSharpOperator(bpy.types.Operator):
    bl_idname = "clean.sharps"
    bl_label = "Remove Ssharps"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """Sharp Mark Removal 
    
    REMOVES all BEVEL modifiers and EDGE markings / Resets mesh to FLAT shading
    Also can remove normal data
    
    F6 for additional parameters
    
    """

    removeMods: BoolProperty(default=True)
    clearsharps: BoolProperty(default=True)
    clearbevel: BoolProperty(default=True)
    clearcrease: BoolProperty(default=True)
    clearseam: BoolProperty(default=True)
    clearcustomdata: BoolProperty(default=False)

    text = "SSharps Removed"
    op_tag = "Clean Ssharp"
    op_detail = "Selected Ssharps Removed"

    called_ui = False

    def __init__(self):

        HOPS_OT_UnSharpOperator.called_ui = False

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        # DRAW YOUR PROPERTIES IN A BOX
        box.prop(self, 'removeMods', text="RemoveModifiers?")
        box.prop(self, 'clearsharps', text="Clear Sharps")
        box.prop(self, 'clearbevel', text="Clear Bevels")
        box.prop(self, 'clearcrease', text="Clear Crease")
        box.prop(self, 'clearseam', text="Clear Seam")
        box.prop(self, 'clearcustomdata', text="Clear Custom Data")

    def execute(self, context):
        clear_ssharps_active_object(
            context,
            self.removeMods,
            self.clearsharps,
            self.clearbevel,
            self.clearcrease,
            self.clearseam,
            self.clearcustomdata,
            self.text)

        # Operator UI
        if not HOPS_OT_UnSharpOperator.called_ui:
            HOPS_OT_UnSharpOperator.called_ui = True

            ui = Master()
            draw_data = [
                ["Clear Sharp Classic"],
                ["Clear Custom Normal Data", self.clearcustomdata],
                ["Clear Seam ", self.clearseam],
                ["Clear Crease ", self.clearcrease],
                ["Clear Bevel ", self.clearbevel],
                ["Clear Sharps ", self.clearsharps]]
            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return {'FINISHED'}

# _____________________________________________________________clear ssharps________________________


def clear_ssharps_active_object(context, removeMods, clearsharps, clearbevel, clearcrease, clearseam, clear_custom_data, text):
    object = bpy.context.active_object
    remove_mods_shadeflat(removeMods, object)
    clear_sharps(
        context,
        clearsharps,
        clearbevel,
        clearcrease,
        clearseam,
        clear_custom_data)
    # show_message(text)
    object.hops.status = "UNDEFINED"
    try:
        bpy.data.collections['Hardops'].objects.unlink(object)
    except:
        pass
    bpy.ops.object.shade_flat()


def clear_sharps(context, clearsharps, clearbevel, clearcrease, clearseam, clear_custom_data):
    active = bpy.context.active_object
    for obj in context.selected_objects:
        if obj.type == 'MESH':

            bpy.context.view_layer.objects.active = obj

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.reveal()
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_all(action='TOGGLE')

            if clearsharps:
                bpy.ops.mesh.mark_sharp(clear=True)
            if clearbevel:
                bpy.ops.transform.edge_bevelweight(value=-1)
            if clearcrease:
                bpy.ops.transform.edge_crease(value=-1)
            if clearseam:
                bpy.ops.mesh.mark_seam(clear=True)
            if clear_custom_data:
                bpy.ops.mesh.customdata_custom_splitnormals_clear()

            bpy.ops.object.editmode_toggle()
    bpy.context.view_layer.objects.active = active


def remove_mods_shadeflat(removeMods, obj):
    if removeMods:
        for mod in obj.modifiers:
            if mod.type == 'WEIGHTED_NORMAL' or 'BEVEL' or 'SOLIDIFY':
                obj.modifiers.remove(mod)
    else:
        return {"FINISHED"}


def show_message(text):
    pass
