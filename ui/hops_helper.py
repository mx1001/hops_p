import bpy
from bpy.types import PropertyGroup
from bpy.props import *
from .. utils.blender_ui import get_dpi_factor
from bl_ui.properties_data_modifier import DATA_PT_modifiers
from .. preferences import get_preferences

class helper_options(PropertyGroup):

    status = BoolProperty(
        name = "Status",
        description = "Display status settings",
        default = False
    )

    surface = BoolProperty(
        name = "Surface",
        description = "Display surface settings",
        default = False
    )

    settings = BoolProperty(
        name = "Settings",
        description = "Display additional settings",
        default = False
    )

    cutting_material = BoolProperty(
        name = "Cutting Material",
        description = "Display cutting material settings",
        default = True
    )

def find_node(material, nodetype):
    if material and material.node_tree:
        ntree = material.node_tree

        active_output_node = None
        for node in ntree.nodes:
            if getattr(node, "type", None) == nodetype:
                if getattr(node, "is_active_output", True):
                    return node
                if not active_output_node:
                    active_output_node = node
        return active_output_node

    return None

def find_node_input(node, name):
    for input in node.inputs:
        if input.name == name:
            return input

    return None


def panel_node_draw(layout, id_data, output_type, input_name):
    if not id_data.use_nodes:
        layout.operator("cycles.use_shading_nodes", icon='NODETREE')
        return False

    ntree = id_data.node_tree

    node = find_node(id_data, output_type)
    if not node:
        layout.label(text="No output node")
    else:
        input = find_node_input(node, input_name)
        layout.template_node_view(ntree, node, input)

    return True

helper_tabs_items = [
    ("MODIFIERS", "Modifiers", ""),
    ("MATERIALS", "Materials", ""),
    ("MISC", "Misc", "") ]

hops_status = [
    ("UNDEFINED", "Undefined", ""),
    ("CSHARP", "Csharp", ""),
    ("CSTEP", "Cstep", ""),
    ("BOOLSHAPE", "Boolshape", "")]


class HOpsHelperPopup(bpy.types.Operator):
    bl_idname = "view3d.hops_helper_popup"
    bl_label = "HOps Helper"

    tab = EnumProperty(name = "Tab", default = "MODIFIERS",
            options = {"SKIP_SAVE"}, items = helper_tabs_items)

    status = EnumProperty(name = "Status", default = "UNDEFINED",
            options = {"SKIP_SAVE"}, items = hops_status)


    def execute(self, context):
        self.set_helper_default(context)
        self.set_hops_status(context)
        return {'FINISHED'}

    def cancel(self, context):
        self.set_helper_default(context)
        self.set_hops_status(context)

    def check(self, context):
        return True

    def invoke(self, context, event):
        object = bpy.context.active_object
        if object is not None:
            if object.type == "MESH":
                self.status = object.hops.status
        self.tab = get_preferences().helper_tab
        return context.window_manager.invoke_props_dialog(self, width = 300 * get_dpi_factor())

    def set_helper_default(self, context):
        if self.tab == "MODIFIERS":
            get_preferences().helper_tab = "MODIFIERS"
        elif self.tab == "MATERIALS":
            get_preferences().helper_tab = "MATERIALS"
        elif self.tab == "MISC":
            get_preferences().helper_tab = "MISC"

    def set_hops_status(self, context):
        object = bpy.context.active_object
        if object is not None:
            if object.type == "MESH":
                if self.status == "UNDEFINED":
                    object.hops.status = "UNDEFINED"
                elif self.status == "CSHARP":
                    object.hops.status = "CSHARP"
                elif self.status == "CSTEP":
                    object.hops.status = "CSTEP"
                elif self.status == "BOOLSHAPE":
                    object.hops.status = "BOOLSHAPE"

    def draw(self, context):
        layout = self.layout
        self.draw_tab_bar(layout)

        if self.tab == "MODIFIERS":
            self.draw_modifier_tab(layout)
        elif self.tab == "MATERIALS":
            self.draw_material_tab(context, layout)
        elif self.tab == "MISC":
            self.draw_misc_tab(context, layout)

    def draw_tab_bar(self, layout):
        row = layout.row()
        row.prop(self, "tab", expand = True)
        layout.separator()

    def draw_modifier_tab(self, layout):
        row = layout.row()

        object = bpy.context.active_object
        if object is None:
            row.alignment = "CENTER"
            row.label("No active object", icon = "INFO")
            return

        row.operator_menu_enum("object.modifier_add", "type")
        row.operator("object.make_links_data", text = "Copy Modifiers From").type = "MODIFIERS"

        modifiers_panel = DATA_PT_modifiers(bpy.context)
        for modifier in object.modifiers:
            box = layout.template_modifier(modifier)
            if box:
                getattr(modifiers_panel, modifier.type)(box, object, modifier)

    def draw_material_tab(self, context, layout):

        object = context.active_object
        option = context.window_manager.Hard_Ops_helper_options

        if object:
            material = object.active_material
            is_sortable = len(object.material_slots) > 1
            rows = 2

            if (is_sortable):
                rows = 4
            row = layout.row()
            row.context_pointer_set('material', object.active_material)

            row.template_list("MATERIAL_UL_matslots", "", object, "material_slots", object, "active_material_index", rows=rows)

            col = row.column(align=True)
            col.operator("object.material_slot_add", icon='ZOOMIN', text="")
            col.operator("object.material_slot_remove", icon='ZOOMOUT', text="")

            col.menu("MATERIAL_MT_specials", icon='DOWNARROW_HLT', text="")

            if is_sortable:
                col.separator()
                col.operator("object.material_slot_move", icon='TRIA_UP', text="").direction = 'UP'
                col.operator("object.material_slot_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

            if object.mode == 'EDIT':
                row = layout.row(align=True)
                row.operator("object.material_slot_assign", text="Assign")
                row.operator("object.material_slot_select", text="Select")
                row.operator("object.material_slot_deselect", text="Deselect")

        if object:
            split = layout.split(percentage=0.65)
            slot = object.material_slots[object.active_material_index] if object.material_slots else None
            split.template_ID(object, "active_material", new="material.hops_new")
            row = split.row()

            if slot:
                row.prop(slot, "link", text="")

            else:
                row.label()

        if object and object.material_slots and object.active_material:
            box = layout.box()
            row = box.row()
            row.prop(option, "surface", icon="TRIA_DOWN" if option.surface else "TRIA_RIGHT", text="", emboss=False)
            row.label("Surface")

            if option.surface:

                if not panel_node_draw(box, object.active_material, 'OUTPUT_MATERIAL', 'Surface'):
                    row = layout.row()
                    row.prop(object.active_material, "diffuse_color")

            box = layout.box()
            row = box.row()
            row.prop(option, "settings", icon="TRIA_DOWN" if option.settings else "TRIA_RIGHT", text="", emboss=False)
            row.label("Settings")

            if option.settings:
                col = box.column()
                split = col.split()
                col = split.column(align=True)
                col.label("Viewport Color:")
                col.prop(object.active_material, "diffuse_color", text="")
                col.prop(object.active_material, "alpha")
                col.label("Viewport Alpha:")
                col.prop(object.active_material.game_settings, "alpha_blend", text="")
                col.prop(object, "show_transparent", text="Transparency")

                col = split.column(align=True)
                col.label("Viewport Specular:")
                col.prop(object.active_material, "specular_color", text="")
                col.prop(object.active_material, "specular_hardness", text="Hardness")
                col.separator()
                col.prop(object.active_material, "pass_index")

        box = layout.box()
        row = box.row()
        row.prop(option, "cutting_material", icon="TRIA_DOWN" if option.cutting_material else "TRIA_RIGHT", text="", emboss=False)
        row.label("Cutting Material")

        if option.cutting_material:

            material_option = context.window_manager.Hard_Ops_material_options

            col = box.column(align=True)
            row = col.row(align=True)
            row.prop(material_option, "material_mode", expand=True)
            row = col.row(align=True)

            if material_option.material_mode == "ALL":
                row.prop_search(material_option, "active_material", bpy.data, "materials", text="")

            else:
                row.prop_search(material_option, "active_material", context.active_object, "material_slots", text="")

            row.prop(material_option, "force", text="", icon="FORCE_FORCE")

    def draw_misc_tab(self, context, layout):
        #layout.label("Coming To 008!", icon = "INFO")

        ob = context.object
        active_object = context.active_object
        option = context.window_manager.Hard_Ops_helper_options
        
        box = layout.box().column(1)
        row = box.row(1)
        row.prop(option, "status", icon="TRIA_DOWN" if option.surface else "TRIA_RIGHT", text="", emboss=False)
        row.label("Status")

        if option.status:
            row.prop(self, "status", expand = True)


        if ob:
            if active_object.type == "MESH":
                box = layout.box().column(1)
                row = box.row(1)
                ssmooth = bpy.ops.object
                row.operator("object.shade_smooth", text = "Set Smooth")
                row.operator("object.shade_flat", text = "Shade Flat")

                box = layout.box().column(1)
                row = box.row(1)
                asmooth = bpy.context.object.data
                row.prop(asmooth, "auto_smooth_angle", text="Auto Smooth Angle")
                row.prop(asmooth, "use_auto_smooth", text="Auto Smooth")

                box = layout.box().column(1)
                row = box.row(1)
                row.label(text="Parent:")
                row.prop(ob, "parent", text="")

            elif active_object.type == "CURVE":
                layout.label("Curve Stuff Soon", icon = "INFO")

                #the idea is that curve stuff will be here for quick options for things the q menu cant do.

        box = layout.box()
        box.label(text="Cutting Material:")
        material_option = context.window_manager.Hard_Ops_material_options

        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(material_option, "material_mode", expand=True)
        row = col.row(align=True)

        if material_option.material_mode == "ALL":
            row.prop_search(material_option, "active_material", bpy.data, "materials", text="")

        else:
            row.prop_search(material_option, "active_material", context.active_object, "material_slots", text="")

        row.prop(material_option, "force", text="", icon="FORCE_FORCE")

        layout.separator()
