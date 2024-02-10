import bpy
from math import radians, degrees
from bpy.props import EnumProperty, IntProperty, FloatProperty, BoolProperty
from .... operators.utils import update_Weight_modifier_if_necessary, set_smoothing, mark_ssharps_bmesh, update_bevel_modifier_if_necessary
from .... preferences import get_preferences
from ... utility import modifier
from ....ui_framework.operator_ui import Master
from .... operators.misc.late_parent import late_parent

def iterate_titled_as_string(iter, separator=','):
    applied_types = ''
    separator = f'{separator} '
    for i in iter:
        applied_types += i.title() + separator
    return applied_types[:-len(separator)]

class HOPS_OT_Sharpen(bpy.types.Operator):
    bl_idname = "hops.sharpen"
    bl_label = "Hops sharpen"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = """ Sharpen - Shading Assistant
    
LMB            -  Sharpen (Ssharp)
Ctrl             -  Sharpen / Apply Mods (CSharp)
Shift            -  Autosmooth (Interactive)
Alt              -  Weighted Normal
Ctrl+Shift     -  Recalculate (Resharp)

"""
#Sharpen refers to marking specific angles ex: 30º

    items: [(x.identifier, x.name, x.description, x.icon)
            for x in bpy.types.Modifier.bl_rna.properties['type'].enum_items]

    behavior: EnumProperty(
        name="Operator Modes",
        default='SSHARP',
        items=(("SSHARP", "Ssharp", ""),
               ("CSHARP", "Csharp", ""),
               ("RESHARP", "Resharp", ""),
               ("CSHARPBEVEL", "CsharpBevel", ""),
               ("SSHARPWN", "SsharpWN", ""),
               ("AUTOSMOOVE", "Autosmooth", ""),
               ("CLEANSHARP", "Cleansharp", "")))

    mode: EnumProperty(
        name="Operator Modes",
        default='SSHARP',
        items=(("SSHARP", "Ssharp", ""),
               ("CSHARP", "Csharp", ""),
               ("CLEANSHARP", "Cleansharp", "")))

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

    add_bevel: BoolProperty(name="Add Bevel",
                            description="Add Bevel Modifier if not there",
                            default=False)

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

    removeMods: BoolProperty(default=True)

    clearsharps: BoolProperty(default=True)

    clearbevel: BoolProperty(default=True)

    clearcrease: BoolProperty(default=True)

    clearseam: BoolProperty(default=True)

    clearcustomdata: BoolProperty(default=False)

    use_resharp: BoolProperty(name="triggers resharp notification", default=False)

    text = "Sharps Removed"

    reveal_mesh = True

    called_ui = False

    def __init__(self):

        HOPS_OT_Sharpen.called_ui = False

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

        colrow = col.row(align=True)
        colrow.prop(self, "mode", expand=True)

        col.separator()

        if self.mode == 'CSHARP':
            col.prop(self, "add_bevel", text='Add bevel modifier', toggle=True, expand=True)

            col.label(text="Modifiers Applied By Csharp")

            colrow = col.row(align=True)
            colrow.prop(self, "boolean", text='Bool', toggle=True)
            colrow.prop(self, "solidify", text='Sol', toggle=True)
            colrow.prop(self, "bevel", text='Bev', toggle=True)
            colrow.prop(self, "mirror", text='Mir', toggle=True)
            colrow.prop(self, "array", text='Arr', toggle=True)
            colrow.prop(self, "others", text='Others', toggle=True)
            col.separator()

            colrow = col.row(align=True)
            colrow.prop(get_preferences().property, "Hops_sharp_remove_cutters", text='Remove Cutters', toggle=True)

            col.separator()
            if self.bevel:
                colrow = col.row(align=True)
                colrow.prop(self, "bevel_vg", text='Vertex Group bevels applied only')

        if self.mode in{'SSHARP'}:
            col.separator()
            col.separator()
            col.separator()
            col.separator()
            col.separator()
            col.separator()
            col.separator()

        if self.mode in {'SSHARP', 'CSHARP'}:
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

        if self.mode == 'CLEANSHARP':
            col.separator()
            col.prop(self, 'removeMods', text="RemoveModifiers?")
            col.prop(self, 'clearsharps', text="Clear Sharps")
            col.prop(self, 'clearbevel', text="Clear Bevels")
            col.prop(self, 'clearcrease', text="Clear Crease")
            col.prop(self, 'clearseam', text="Clear Seam")
            col.prop(self, 'clearcustomdata', text="Clear Custom Data")
            col.separator()
            col.separator()


    def invoke(self, context, event):

        self.is_global = context.active_object.hops.is_global
        self.auto_smooth_angle = context.active_object.data.auto_smooth_angle

        self.apply_mods = True

        if event.shift and not event.ctrl and not event.alt:
            self.behavior = get_preferences().keymap.sharp_shift
        elif event.ctrl and not event.shift and not event.alt:
            self.behavior = get_preferences().keymap.sharp_ctrl
        elif event.alt and not event.shift and not event.ctrl:
            self.behavior = get_preferences().keymap.sharp_alt
        elif event.ctrl and event.shift and not event.alt:
            self.behavior = get_preferences().keymap.sharp_shift_ctrl
        elif event.ctrl and event.alt and not event.shift:
            self.behavior = get_preferences().keymap.sharp_alt_ctrl
        elif event.shift and event.alt and not event.ctrl:
            self.behavior = get_preferences().keymap.sharp_alt_shift
        else:
            self.behavior = get_preferences().keymap.sharp

        if self.behavior in {'SSHARP', 'SSHARPWN', 'AUTOSMOOVE'}:
            self.mode = 'SSHARP'
            self.additive_mode = True
        elif self.behavior == 'RESHARP':
            self.mode = 'SSHARP'
            self.additive_mode = False
        elif self.behavior == 'CSHARP':
            self.mode = 'CSHARP'
        elif self.behavior == 'CLEANSHARP':
            self.mode = 'CLEANSHARP'
        elif self.behavior == 'CSHARPBEVEL':
            self.mode = 'CSHARP'

            #return {"FINISHED"}

        self.execute(context)

        if self.behavior == 'CSHARPBEVEL':
            bpy.ops.hops.adjust_bevel("INVOKE_DEFAULT", ignore_ctrl=True)

        if self.mode == 'CSHARP':
            if get_preferences().property.auto_bweight:
                bpy.ops.hops.adjust_bevel("INVOKE_DEFAULT", ignore_ctrl=True)

        return {"FINISHED"}


    def execute(self, context):
        applied = None
        selected = context.selected_objects
        # object = context.active_object

        for obj in selected:

            if self.mode == 'SSHARP':

                if self.behavior == 'SSHARPWN':
                    for mod in obj.modifiers:
                        if mod.type == 'WEIGHTED_NORMAL':
                            obj.modifiers.remove(mod)

                    mod = obj.modifiers.new(name="Weighted Normal", type='WEIGHTED_NORMAL')
                    mod.keep_sharp = True
                    self.report({'INFO'}, F'Weighted Normal')

                elif self.behavior == 'AUTOSMOOVE':
                    bpy.context.object.hops.is_global = False
                    bpy.ops.hops.adjust_auto_smooth("INVOKE_DEFAULT")

                else:
                    soft_sharpen_object(
                        self,
                        obj,
                        get_preferences().property.sharpness,
                        get_preferences().property.auto_smooth_angle,
                        self.additive_mode,
                        self.reveal_mesh,)
                    if self.additive_mode is False:
                        self.report({'INFO'}, F'Resharpened')
                    else:
                        if self.behavior == 'SSHARP':
                            self.report({'INFO'}, F'SSharpened')

                    # self.report({'INFO'}, F'Weighted Normal')

            elif self.mode == 'CSHARP':
                applied = complex_sharpen_active_object(
                    self,
                    obj,
                    get_preferences().property.sharpness,
                    get_preferences().property.auto_smooth_angle,
                    self.additive_mode,
                    self.reveal_mesh,
                    self.apply_mods,
                    self.add_bevel)
                self.report({'INFO'}, F'CSharpened ')

            elif self.mode == 'CLEANSHARP':
                clear_ssharps_active_object(
                    context,
                    obj,
                    self.removeMods,
                    self.clearsharps,
                    self.clearbevel,
                    self.clearcrease,
                    self.clearseam,
                    self.clearcustomdata,
                    self.text)
                self.report({'INFO'}, F'Sharps Unmarked')

        # Operator UI
        if not HOPS_OT_Sharpen.called_ui:
            HOPS_OT_Sharpen.called_ui = True

            ui = Master()
            #not_applied = [mod for mod in context.active_object.modifiers]
            if not context.active_object:
                applied = '0'

            if self.behavior == "CSHARP":
                draw_data = [
                    ["Csharp (apply)"],
                    #["Additive Mode", self.additive_mode],
                    ["Bevel Added ",  (self.add_bevel)],
                    ["Cutters Removed ", (get_preferences().property.Hops_sharp_remove_cutters)],
                    ["Auto Smooth ", "%.0f" % degrees(obj.data.auto_smooth_angle) + "°"],
                    ["Sharpness   ", "%.0f" % degrees(get_preferences().property.sharpness) + "°"],
                    #["Modifiers Applied : ", iterate_titled_as_string([mod.name for mod in applied]) if applied else ''],
                    #["Modifiers Remaining", len(context.active_object.modifiers[:])],
                    [f"Modifiers Applied / Remain", f"{len(applied)} / {len(context.active_object.modifiers[:])}"],
                    ]

                if len(context.active_object.modifiers[:]) >= 1:
                    draw_data.insert(-5, ["Remaining Modifiers ", len(context.active_object.modifiers[:])]),
                    for mod in reversed(context.active_object.modifiers):
                        draw_data.insert(-6, [" ", mod.name]),

                # for i, mod in enumerate(reversed(applied)):
                #     if i < 3:
                #         try: draw_data.insert(-1, [" ", mod.name])
                #         except: pass
                #     else:
                #         #draw_data.insert(-1, [" ", '...'])
                #         break
            elif self.behavior == "RESHARP":
                draw_data = [
                    ["Resharp (shading)"],
                    ["Auto Smooth", "%.1f" % degrees(obj.data.auto_smooth_angle) + "°"],
                    ["Sharpness", "%.1f" % degrees(get_preferences().property.sharpness) + "°"],
                    ["Additive Mode", self.additive_mode],
                    ["Global Mode", bpy.context.object.hops.is_global],
                    ["Sharpening Recalculated"]]
            elif self.behavior == "CSHARPBEVEL":
                draw_data = [
                    ["Csharp to Bevel"],
                    ["Cutters Removed", (get_preferences().property.Hops_sharp_remove_cutters)],
                    ["Modifiers Applied", len(applied)],
                    ["Bevel Initialzied"]]
            elif self.behavior == "SSHARPWN":
                draw_data = [
                    ["Weighted Normal"],
                    ["Weighted Normal Mod w/ Keep Sharp Added"]]
            elif self.behavior == "CLEANSHARP":
                draw_data = [
                    ["Sharps Cleared"],
                    ["Clear Custom Normal Data", self.clearcustomdata],
                    ["Clear Seam ", self.clearseam],
                    ["Clear Crease ", self.clearcrease],
                    ["Clear Bevel ", self.clearbevel],
                    ["Clear Sharps ", self.clearsharps]]
            elif self.behavior == "SSHARP":
                if get_preferences().property.parent_boolshapes and (self.parent_details[1] * self.parent_details[2]) != 0:
                    draw_data = [
                        ["Sharpen + Parent"],
                        ["Modifiers Applied", "0"],
                        ["Parent Shapes  ",  (get_preferences().property.parent_boolshapes)],
                        ["Bools Total / Parented", F"{self.parent_details[2]} / {self.parent_details[1]}"],
                        ["Additive Mode", self.additive_mode],
                        ["Auto Smooth", "%.1f" % degrees(obj.data.auto_smooth_angle) + "°"],
                        ["Sharpness", "%.1f" % degrees(get_preferences().property.sharpness) + "°"]]
                else:
                    draw_data = [
                        ["Sharpen"],
                        ["Modifiers Applied", "0"],
                        ["", ""],
                        ["Additive Mode", self.additive_mode],
                        ["Auto Smooth", "%.1f" % degrees(obj.data.auto_smooth_angle) + "°"],
                        ["Sharpness", "%.1f" % degrees(get_preferences().property.sharpness) + "°"]]

                    # if get_preferences().property.sharp_use_crease:
                    #     draw_data.insert(1, ["Mark Crease", get_preferences().property.sharp_use_crease])
                    # if get_preferences().property.sharp_use_sharp:
                    #     draw_data.insert(1, ["Mark Sharp", get_preferences().property.sharp_use_sharp])
                    # if get_preferences().property.sharp_use_bweight:
                    #     draw_data.insert(1, ["Mark Bevel Weight", get_preferences().property.sharp_use_bweight])
                    # if get_preferences().property.sharp_use_seam:
                    #     draw_data.insert(1, ["Mark UV Seam", get_preferences().property.sharp_use_seam])
            elif self.behavior == "AUTOSMOOVE":
                draw_data = [
                ['Autosmooth '],
                ["Additive Mode", self.additive_mode],
                ["Auto Smooth", "%.1f" % degrees(obj.data.auto_smooth_angle) + "°"],
                ["Sharpness", "%.1f" % degrees(get_preferences().property.sharpness) + "°"]
                ]
            else:
                draw_data = [
                    [self.behavior],
                    ["Additive Mode", self.additive_mode],
                    ["Auto Smooth", "%.1f" % degrees(obj.data.auto_smooth_angle) + "°"],
                    ["Sharpness", "%.1f" % degrees(get_preferences().property.sharpness) + "°"]
                    ]

            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        del applied
        return {"FINISHED"}


def soft_sharpen_object(self, object, sharpness, auto_smooth_angle, additive_mode, reveal_mesh):

    mark_ssharps_bmesh(object, sharpness, reveal_mesh, additive_mode)
    set_smoothing(object, auto_smooth_angle)

    object.hops.is_global = self.is_global
    object.data.auto_smooth_angle = get_preferences().property.auto_smooth_angle if self.is_global else self.auto_smooth_angle

    if self.behavior == "SSHARP":
        if get_preferences().property.parent_boolshapes:
            self.parent_details = late_parent(bpy.context)


def complex_sharpen_active_object(self, obj, sharpness, auto_smooth_angle, additive_mode, reveal_mesh, apply_mods, add_bevel):

    apply = None
    if apply_mods:
        apply = apply_mod(self, obj)
        #bpy.ops.mesh.customdata_custom_splitnormals_clear()

    soft_sharpen_object(self, obj, sharpness, auto_smooth_angle, additive_mode, reveal_mesh)

    if add_bevel:
        update_bevel_modifier_if_necessary(
            obj,
            self.segment_amount,
            self.bevelwidth,
            get_preferences().property.bevel_profile)

    if get_preferences().property.add_weighten_normals_mod:
        update_Weight_modifier_if_necessary(obj)

    return apply


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

    if get_preferences().property.Hops_sharp_remove_cutters:
        cutters = [mod.object for mod in object.modifiers if mod.type == 'BOOLEAN']

    if self.others:
        others = [mod for mod in object.modifiers if mod.type not in {'BOOLEAN', 'MIRROR', 'BEVEL', 'SOLIDIFY', 'ARRAY'}]
    mod = mods + others + bevel
    if last_bevel:
        mod.remove(last_bevel)
    if mod:
        modifier.apply(object, modifiers=mod)

    if get_preferences().property.Hops_sharp_remove_cutters:
        for cutter in cutters:
            try:
                bpy.data.objects.remove(cutter)
            except:
                get_preferences().property.Hops_sharp_remove_cutters = False
                self.report({'ERROR_INVALID_INPUT'}, F'Cannot remove same Cutter from multiple objects')

    return mod
    #print(len(mod))
    #print(mod)
            # del cutter


def clear_ssharps_active_object(context, obj, removeMods, clearsharps, clearbevel, clearcrease, clearseam, clearcustomdata, text):

    remove_mods_shadeflat(removeMods, obj)
    clear_sharps(
        context,
        clearsharps,
        clearbevel,
        clearcrease,
        clearseam,
        clearcustomdata)
    object = bpy.context.active_object
    object.hops.status = "UNDEFINED"
    try:
        bpy.data.collections['Hardops'].objects.unlink(object)
    except:
        pass
    bpy.ops.object.shade_flat()
    bpy.context.object.data.use_auto_smooth = False


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
        # bevel = obj.modifiers.get("Bevel")
        # solidify = obj.modifiers.get("Solidify")
        # if bevel:
        #     obj.modifiers.remove(bevel)
        # if solidify:
        #     obj.modifiers.remove(obj.modifiers.get(solidify))
        for mod in obj.modifiers:
            if mod.type == 'WEIGHTED_NORMAL' or 'BEVEL' or 'SOLIDIFY':
                obj.modifiers.remove(mod)
    else:
        return {"FINISHED"}
