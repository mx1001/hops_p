import bpy
import math
from bpy.props import EnumProperty, IntProperty, FloatProperty, BoolProperty
import bpy.utils.previews
from ... operators.utils import update_bevel_modifier_if_necessary
from ... utils.context import ExecutionContext
from ... utils.modifiers import apply_modifiers
from ... preferences import get_preferences
from ...ui_framework.operator_ui import Master

mod_types = [
    ("BOOLEAN", "Boolean", ""),
    ("MIRROR", "Mirror", ""),
    ("BEVEL", "Bevel", ""),
    ("SOLIDIFY", "Solidify", ""),
    ("ARRAY", "Array", "")]

def iterate_titled_as_string(iter, separator=','):
    applied_types = ''
    separator = f'{separator} '
    for i in iter:
        applied_types += i.title() + separator
    return applied_types[:-len(separator)]

class HOPS_OT_StepOperator(bpy.types.Operator):
    bl_idname = "hops.step"
    bl_label = "Hops Step Operator"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = """HOPS Step

Non-Destructive: (newer)
Adds new bevel at 50% width of previous bevel (default)

Destructive: (classic)
Applies Csharp / Hides mesh in edit mode / Adds new BEVEL modifier
Typically used for booleans and should decrement.

"""

    items = [(x.identifier, x.name, x.description, x.icon)
             for x in bpy.types.Modifier.bl_rna.properties['type'].enum_items]

    modifier_types: EnumProperty(name="Modifier Types", default={'BEVEL', 'BOOLEAN'},
                                 options={"ENUM_FLAG"}, items=mod_types)

    bevelwidth: FloatProperty(name="Bevel Width Amount", description="Set Bevel Width", default=0.01, min=0.002, max=0.25)

    segment_amount: IntProperty(name="Segments", description="Segments For Bevel", default=6, min=1, max=12)

    bevelwidth: FloatProperty(name="Bevel Width Amount",
                              description="Set Bevel Width",
                              default=0.0200,
                              min=0.002,
                              max=1.50)

    hide_mesh: BoolProperty(name="Hide Mesh",
                            description="Hide Mesh",
                            default=True)

    profile_value = 0.70

    called_ui = False

    def __init__(self):

        HOPS_OT_StepOperator.called_ui = False

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        object = context.active_object
        if object is None: return False
        if object.mode == "OBJECT" and all(obj.type == "MESH" for obj in selected):
            return True

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        if get_preferences().property.workflow_mode == "WEIGHT":
            col.label(text='Apply Mods')
            col.prop(self, 'modifier_types')
            col.separator()
            col.prop(self, 'bevelwidth')
            col.prop(self, 'segment_amount')
        else:
            col.label(text='Half Bevel Added')

    def execute(self, context):
        selected = context.selected_objects
        object = context.active_object

        for obj in selected:
            bpy.context.view_layer.objects.active = obj

            if get_preferences().property.workflow_mode == "WEIGHT":
                self.step_active_object(
                    object,
                    self.modifier_types)

                update_bevel_modifier_if_necessary(
                    context.active_object,
                    self.segment_amount,
                    self.bevelwidth,
                    self.profile_value)

            else:
                # self.step_active_object(
                #     object,
                #     self.modifier_types,
                #     mark_edges=False)

                bpy.ops.object.shade_smooth()
                bpy.ops.hops.bevel_half_add()

        self.report({'INFO'}, F'Step')
        bpy.context.view_layer.objects.active = object

        # Operator UI
        if not HOPS_OT_StepOperator.called_ui:
            HOPS_OT_StepOperator.called_ui = True

            ui = Master()
            if get_preferences().property.workflow_mode == "WEIGHT":
                draw_data = [
                    ["STEP - Destructive"],
                    ["Workflow : ", get_preferences().property.workflow_mode],
                    ["Modifiers Applied : ", iterate_titled_as_string(self.modifier_types)]]
            if get_preferences().property.workflow_mode == "ANGLE":
                draw_data = [
                    ["STEP - Non-Destructive"],
                    ["No Modifiers Were Applied"],
                    ["New Bevel Added at 50% of previous"],
                    ["Workflow :", get_preferences().property.workflow_mode]
                    ]
            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return {"FINISHED"}

    def step_active_object(self, object, modifier_types, mark_edges=True):
        with ExecutionContext(mode="OBJECT", active_object=object):
            active = [object]
            apply_modifiers(active, modifier_types)

        if mark_edges:
            with ExecutionContext(mode="EDIT", active_object=object):
                bpy.ops.mesh.reveal()
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.transform.edge_bevelweight(value=-1)
                bpy.ops.transform.edge_crease(value=-1)
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.mesh.select_all(action='SELECT')

                if self.hide_mesh:
                    bpy.ops.mesh.hide()

    def bevel(self, object, segment_amount, bevelwidth, profile_value):
        bevel = object.modifiers.new("Bevel", "BEVEL")
        bevel.use_clamp_overlap = False
        bevel.show_in_editmode = False
        bevel.width = bevelwidth
        bevel.profile = profile_value
        bevel.limit_method = get_preferences().property.workflow_mode
        bevel.show_in_editmode = True
        bevel.harden_normals = False
        bevel.miter_outer = 'MITER_ARC'
        bevel.segments = segment_amount
        bevel.loop_slide = get_preferences().property.bevel_loop_slide
        bevel.angle_limit = math.radians(60)

    def titled_list_as_string(list, separator=','):
        applied_types = ''
        separator = f'{separator} '
        for i in self.modifier_types:
            applied_types += i.title() + separator
        return applied_types[:-len(separator)]
