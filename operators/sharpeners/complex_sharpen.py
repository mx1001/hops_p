import bpy
from math import radians
from bpy.props import EnumProperty, IntProperty, FloatProperty, BoolProperty
from .. utils import update_bevel_modifier_if_necessary, update_Weight_modifier_if_necessary
from ... utils.context import ExecutionContext
from . soft_sharpen import soft_sharpen_object
from ... preferences import get_preferences
from ... utils.objects import apply_modifiers
from ... utils.objects import get_modifier_with_type
from ... utility import modifier
from ... preferences import get_preferences
from ...ui_framework.operator_ui import Master


class HOPS_OT_ComplexSharpenOperator(bpy.types.Operator):
    bl_idname = "hops.complex_sharpen"
    bl_label = "Hops Csharpen"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = """Classic Csharpen System
    
*CSharp is now part of Sharpen under CTRL*
Adds Bevel Modifier / Shade Smooth / Enable Autosmooth
Mark Sharp Edges / Destructively Bakes - Ignores Modifiers via F6

Hold shift - Bypass modifier apply / Sstatus change
"""

    items: [(x.identifier, x.name, x.description, x.icon)
            for x in bpy.types.Modifier.bl_rna.properties['type'].enum_items]

    boolean: BoolProperty(name="boolean", default=True)

    mirror: BoolProperty(name="mirror", default=False)

    bevel: BoolProperty(name="bevel", default=False)

    solidify: BoolProperty(name="solidify", default=True)

    array: BoolProperty(name="array", default=False)

    others: BoolProperty(name="others", default=False)

    bevel_vg: BoolProperty(name="only bevel with vertex group", default=True)

    segment_amount: IntProperty(name="Segments", description="Segments For Bevel", default=3, min=1, max=12)

    bevelwidth: FloatProperty(name="Bevel Width Amount",
                              description="Set Bevel Width",
                              default=0.0200,
                              precision=3,
                              min=0.000,
                              max=100)

    segment_modal: IntProperty(name="Segments", description="Segments For Bevel", default=3, min=1, max=12)

    bevelwidth_modal: FloatProperty(name="Bevel Width Global",
                                    description="Set Global Bevel Width",
                                    default=0.0200,
                                    precision=3,
                                    min=0.000,
                                    max=100)

    additive_mode: BoolProperty(name="Additive Mode",
                                description="Don't clear existing edge properties",
                                default=True)

    auto_smooth_angle: FloatProperty(name="angle edge marks are applied to",
                                     default=radians(60),
                                     min=radians(1),
                                     max=radians(180),
                                     precision=3,
                                     unit='ROTATION')

    is_global: BoolProperty(name="Is Global", default=True)

    to_bwidth: BoolProperty(name="To Bevel Width", default=False)

    reveal_mesh = True

    called_ui = False

    def __init__(self):

        HOPS_OT_ComplexSharpenOperator.called_ui = False

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

        col.label(text="Modifiers Applied By Csharp")
        colrow = col.row(align=True)
        colrow.prop(self, "boolean", text='Bool', toggle=True)
        colrow.prop(self, "solidify", text='Sol', toggle=True)
        colrow.prop(self, "bevel", text='Bev', toggle=True)
        colrow.prop(self, "mirror", text='Mir', toggle=True)
        colrow.prop(self, "array", text='Arr', toggle=True)
        colrow.prop(self, "others", text='Others', toggle=True)
        col.separator()
        if self.bevel:
            colrow = col.row(align=True)
            colrow.prop(self, "bevel_vg", text='Vertex Group bevels applied only')
        col.separator()
        col.label(text="General Parameters")
        col = layout.column(align=True)
        colrow = col.row(align=True).split(factor=0.3, align=True)
        colrow.prop(self, "segment_modal", text='')
        colrow.prop(self, "segment_amount")
        colrow = col.row(align=True).split(factor=0.3, align=True)
        colrow.prop(self, "bevelwidth_modal", text='')
        colrow.prop(self, "bevelwidth")
        col.separator()

        col.label(text="Sharpening Parameters")
        col = layout.column(align=True)
        colrow = col.row(align=True).split(factor=0.3, align=True)
        colrow.prop(self, "additive_mode", toggle=True)
        colrow.prop(get_preferences().property, "sharpness", text="Sharpness")
        colrow = col.row(align=True).split(factor=0.3, align=True)
        colrow.prop(self, "is_global", text="Global", toggle=True)
        if self.is_global:
            colrow.prop(get_preferences().property, "auto_smooth_angle", text="Auto Smooth Angle")
        else:
            colrow.prop(self, "auto_smooth_angle", text="Auto Smooth Angle")
        col.separator()


    def invoke(self, context, event):

        selected = context.selected_objects
        object = context.active_object

        self.is_global = context.active_object.hops.is_global
        self.auto_smooth_angle = context.active_object.data.auto_smooth_angle

        self.apply_mods = True
        if event.shift:
            self.apply_mods = False

        for obj in selected:
            bevels = [mod for mod in object.modifiers if (mod.type in "BEVEL") and not mod.vertex_group]
            bevel = next(iter(bevels or []), None)
            if bevel is not None:
                self.segment_amount = bevel.segments
                self.bevelwidth = bevel.width
            else:
                self.segment_amount = self.segment_modal
                self.bevelwidth = self.bevelwidth_modal

        self.execute(context)
        if event.shift:
            object.hops.status = "UNDEFINED"

        if get_preferences().property.auto_bweight:
            bpy.ops.hops.adjust_bevel("INVOKE_DEFAULT", ignore_ctrl=True)
        #Assistive to Sharpen
        elif self.to_bwidth:
            bpy.ops.hops.adjust_bevel("INVOKE_DEFAULT", ignore_ctrl=True)

        return {"FINISHED"}


    def execute(self, context):

        selected = context.selected_objects
        object = context.active_object

        for obj in selected:

            complex_sharpen_active_object(
                self,
                obj,
                get_preferences().property.sharpness,
                get_preferences().property.auto_smooth_angle,
                self.additive_mode,
                self.segment_amount,
                self.bevelwidth,
                self.reveal_mesh,
                self.apply_mods)

            update_bevel_modifier_if_necessary(
                obj,
                self.segment_amount,
                self.bevelwidth,
                get_preferences().property.bevel_profile)

            if get_preferences().property.add_weighten_normals_mod:
                update_Weight_modifier_if_necessary(obj)

            obj.hops.is_global = self.is_global
            obj.data.auto_smooth_angle = get_preferences().property.auto_smooth_angle if self.is_global else self.auto_smooth_angle

        bpy.ops.object.select_all(action='DESELECT')
        for obj in selected:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = object

        # Operator UI
        if not HOPS_OT_ComplexSharpenOperator.called_ui:
            HOPS_OT_ComplexSharpenOperator.called_ui = True

            ui = Master()
            draw_data = [
                ["Csharp Classic"],
                #["Array",           self.array],
                #["Solidify",        self.solidify],
                ["Bevel",           self.bevel],
                ["Boolean ",        self.boolean],
                ["Modifiers Applied"],
                ]
            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)


        return {"FINISHED"}


def complex_sharpen_active_object(self, object, sharpness, auto_smooth_angle, additive_mode, segment_amount, bevelwidth, reveal_mesh, apply_mods):

    if apply_mods:
        apply_mod(self, object)

    soft_sharpen_object(object, sharpness, auto_smooth_angle, additive_mode, reveal_mesh)
    object = bpy.context.active_object


def apply_mod(self, object):

    mod_types = []
    others = []
    bevel = []
    last_bevel = None
    if self.boolean:
        mod_types.append('BOOLEAN')
    if self.mirror:
        mod_types.append('MIRROR')
    if self.bevel:
        if self.bevel_vg:
            bevel = [mod for mod in object.modifiers if (mod.type in "BEVEL") and mod.vertex_group]
        else:
            mod_types.append('BEVEL')
            bevels = [mod for mod in object.modifiers if (mod.type in "BEVEL")]
            if bevels:
                last_bevel = bevels[-1]
    if self.solidify:
        mod_types.append('SOLIDIFY')
    if self.array:
        mod_types.append('ARRAY')

    mods = [mod for mod in object.modifiers if mod.type in mod_types]
    if self.others:
        others = [mod for mod in object.modifiers if mod.type not in {'BOOLEAN', 'MIRROR', 'BEVEL', 'SOLIDIFY', 'ARRAY'}]
    mod = mods + others + bevel
    if last_bevel:
        mod.remove(last_bevel)
    if mod:
        modifier.apply(object, modifiers=mod)
