import bpy
import gpu
import mathutils
import math

from bgl import *
from bpy.types import (
    Panel,
    Gizmo,
    GizmoGroup,
    Operator
)
from mathutils import Matrix, Vector, Euler
from math import radians
from ... preferences import get_preferences
from ... addon.utility import modifier
from ... utils.toggle_view3d_panels import collapse_3D_view_panels

from bl_ui.space_view3d import VIEW3D_HT_header
from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active as view3d_tools
from bl_ui.space_statusbar import STATUSBAR_HT_header

from ... ui_framework.master import Master
from ... ui_framework.utils.mods_list import get_mods_list


# Tracking props for UI
creating_empty = False


class HOPS_OT_MirrorExecuteFinal(Operator):
    bl_idname = "hops.mirror_exit"
    bl_label = "Mirror finish"
    bl_description = "Mirror Finish"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        preference = get_preferences()
        preference.operator.mirror.running = False
        return {'FINISHED'}


class HOPS_OT_MirrorOperator():

    def invoke(self, context, event):
        if event.shift:
            self.shift = True
        self.execute(context)
        return {'FINISHED'}

    def execute(self, context):

        preference = get_preferences()
        active = context.active_object

        self.edit_mode = False
        if context.mode == 'EDIT_MESH':
            self.edit_mode = True

        # BISECT
        if preference.operator.mirror.mode in {"BISECTMOD", "BISECT"}:
            if active.type in {"MESH"}:
                fill = False
                if preference.operator.mirror.mode == "BISECT":
                    fill = True
                self.bisect(context, fill)

        # MODIFIER
        if preference.operator.mirror.mode in {"MODIFIER", "NEWMODIFIER", "BISECTMOD", "MODIFIERAPPLY"}:

            new = False
            if preference.operator.mirror.mode in {"NEWMODIFIER", "MODIFIERAPPLY"}:
                new = True

            mirror_object = active
            if preference.operator.mirror.orientation in {"GLOBAL", "VIEW", "CURSOR"} or preference.operator.mirror.pivot in {"MEDIAN", "CURSOR"}:
                if preference.operator.mirror.advanced:
                    empty = self.create_empty(context)
                    mirror_object = empty

            if preference.operator.mirror.orientation == "LOCAL" and preference.operator.mirror.pivot in {"INDIVIDUAL"}:
                mirror_object = None

            selected = context.selected_objects
            for obj in selected:
                if obj.type in {"MESH", "CURVE", "GPENCIL"}:

                    if obj == active:
                        if preference.operator.mirror.advanced:
                            if preference.operator.mirror.orientation == "LOCAL" and preference.operator.mirror.pivot in {"ACTIVE", "INDIVIDUAL"}:
                                if len(selected) == 1 or preference.operator.mirror.include_active:
                                    self.mirror_mod(context, selected, obj, *self.data(), new=new)
                            else:
                                self.mirror_mod(context, selected, obj, *self.data(), mirror_object=mirror_object, new=new)
                        else:
                            if len(selected) == 1 or preference.operator.mirror.include_active:
                                self.mirror_mod(context, selected, obj, *self.data(), new=new)
                    else:
                        self.mirror_mod(context, selected, obj, *self.data(), mirror_object=mirror_object, new=new)

                    if obj.type == "MESH":
                        modifier.sort(obj, sort_types=['WEIGHTED_NORMAL'])

        # SYMMETRY
        if preference.operator.mirror.mode in {"SYMMETRY"}:
            if active.type in {"MESH"}:
                self.symmetry(context)

        if preference.operator.mirror.advanced:
            if preference.operator.mirror.orientation in {"GLOBAL", "VIEW", "CURSOR"} or preference.operator.mirror.pivot in {"MEDIAN", "CURSOR"}:
                if preference.operator.mirror.mode == 'MODIFIERAPPLY':
                    bpy.data.objects.remove(empty, do_unlink=True)

        if preference.operator.mirror.close is True:
            preference.operator.mirror.running = False

        return {'FINISHED'}

    def xform(self, context):
        preference = get_preferences()
        active = context.active_object
        selected = context.selected_objects

        matrix_world = active.matrix_world.copy()
        obloc, obrot, obscale = matrix_world.decompose()

        if preference.operator.mirror.orientation == "GLOBAL":
            rot = Euler((0, 0, 0), "XYZ")
        elif preference.operator.mirror.orientation == "CURSOR":
            rot = context.scene.cursor.rotation_euler
        elif preference.operator.mirror.orientation == "LOCAL":
            rot = obrot.to_euler()
        elif preference.operator.mirror.orientation == "VIEW":
            rot = context.region_data.view_rotation.to_euler()

        if preference.operator.mirror.pivot in {"ACTIVE", "INDIVIDUAL"}:
            loc = obloc
        elif preference.operator.mirror.pivot == "CURSOR":
            loc = context.scene.cursor.location
        elif preference.operator.mirror.pivot == "MEDIAN":
            if len(selected) > 0:
                selected_loc = [obj.matrix_world.translation for obj in selected]
                loc = sum(selected_loc, Vector()) / len(selected)
            else:
                loc = obloc

        if preference.operator.mirror.mode == 'SYMMETRY' or not preference.operator.mirror.advanced:
            rot, loc = obrot, obloc

        return loc, rot

    def symmetry(self, context):
        normal = self.data()[0]
        if normal == Vector((1, 0, 0)):
            direction = "NEGATIVE_X"
        elif normal == Vector((-1, 0, 0)):
            direction = "POSITIVE_X"
        elif normal == Vector((0, 1, 0)):
            direction = "NEGATIVE_Y"
        elif normal == Vector((0, -1, 0)):
            direction = "POSITIVE_Y"
        elif normal == Vector((0, 0, 1)):
            direction = "NEGATIVE_Z"
        elif normal == Vector((0, 0, -1)):
            direction = "POSITIVE_Z"

        if not self.edit_mode:
            bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.symmetrize(direction=direction)
        bpy.ops.mesh.select_all(action='DESELECT')
        if not self.edit_mode:
            bpy.ops.object.mode_set(mode='OBJECT')

    def bisect(self, context, fill=False):
        loc, rot = self.xform(context)
        position = loc
        normal = self.data()[0]
        normal.rotate(rot)

        if not self.edit_mode:
            bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.bisect(plane_co=(position.x, position.y, position.z), plane_no=(normal.x, normal.y, normal.z), use_fill=fill, clear_inner=False, clear_outer=True)
        bpy.ops.mesh.select_all(action='DESELECT')
        if not self.edit_mode:
            bpy.ops.object.mode_set(mode='OBJECT')

    def create_empty(self, context):

        preference = get_preferences()
        active = context.active_object
        add_empty = False
        if preference.operator.mirror.mode == "NEWMODIFIER" and preference.operator.mirror.mode != "MODIFIERAPPLY":
            add_empty = True
            bpy.ops.hops.display_notification(info="Empty Created")
        else:
            mods = [mod for mod in active.modifiers if mod.type == "MIRROR"]
            if len(mods) > 0:
                activemod = [mod for mod in mods if mod.name == preference.operator.mirror.modifier]
                mod = activemod[0]
                if mod.mirror_object:
                    empty = mod.mirror_object
                    bpy.data.objects.remove(empty)
                    del empty

            add_empty = True

        if add_empty is True:
            empty = bpy.data.objects.new("empty", None)
            if preference.operator.mirror.mode != "MODIFIERAPPLY":
                bpy.ops.hops.display_notification(info="Empty Created")
            context.collection.objects.link(empty)

            loc, rot = self.xform(context)
            empty.rotation_euler = rot
            empty.location = loc

            if preference.operator.mirror.parent_empty:
                empty.parent = active
                empty.matrix_parent_inverse = active.matrix_world.inverted()

        return empty

    def mirror_mod(self, context, selected, object, normal, axisv, axism, axisx, axisy, axisz, mirror_object=None, new=False):
        preference = get_preferences()

        # GPENCIL
        if object.type == "GPENCIL":
            if new:
                mod = object.grease_pencil_modifiers.new('Hops_Mirror', 'GP_MIRROR')
                bpy.ops.hops.display_notification(info="Modifier Added")
            else:
                mods = [mod for mod in object.grease_pencil_modifiers if mod.type == "GP_MIRROR"]
                if len(mods) > 0:
                    activemod = [mod for mod in mods if mod.name == preference.operator.mirror.modifier]
                    mod = activemod[0]
                else:
                    new = True
                    mod = object.grease_pencil_modifiers.new('Hops_Mirror', 'GP_MIRROR')

            if new:
                mod.x_axis = axisx[0]
                mod.y_axis = axisy[0]
                mod.z_axis = axisz[0]
            else:
                if normal == Vector((1, 0, 0)) or normal == Vector((-1, 0, 0)):
                    if mod.x_axis is False:
                        mod.x_axis = True
                    else:
                        mod.x_axis = False
                elif normal == Vector((0, 1, 0)) or normal == Vector((0, -1, 0)):
                    if mod.y_axis is False:
                        mod.y_axis = True
                    else:
                        mod.y_axis = False
                elif normal == Vector((0, 0, 1)) or normal == Vector((0, 0, -1)):
                    if mod.z_axis is False:
                        mod.z_axis = True
                    else:
                        mod.z_axis = False

            if mirror_object:
                mod.object = mirror_object

        # MESH CURVE
        elif object.type in {"MESH", "CURVE"}:

            if new:
                mod = object.modifiers.new('Hops_Mirror', 'MIRROR')

            else:
                mods = [mod for mod in object.modifiers if mod.type == 'MIRROR']
                if len(mods) > 0:
                    activemod = [mod for mod in mods if mod.name == preference.operator.mirror.modifier]
                    if len(activemod) > 0:
                        mod = activemod[0]
                    else:
                        mod = mods[-1]
                else:
                    new = True
                    mod = object.modifiers.new('Hops_Mirror', 'MIRROR')

            if new:
                mod.use_axis[0], mod.use_bisect_axis[0], mod.use_bisect_flip_axis[0] = axisx
                mod.use_axis[1], mod.use_bisect_axis[1], mod.use_bisect_flip_axis[1] = axisy
                mod.use_axis[2], mod.use_bisect_axis[2], mod.use_bisect_flip_axis[2] = axisz
            else:
                if len(selected) == 1:
                    if mod.use_axis[axisv] is False:
                        mod.use_axis[axisv], mod.use_bisect_axis[axisv], mod.use_bisect_flip_axis[axisv] = axism
                    else:
                        mod.use_axis[axisv], mod.use_bisect_axis[axisv], mod.use_bisect_flip_axis[axisv] = (False, False, False)
                else:
                    mod.use_axis[axisv], mod.use_bisect_axis[axisv], mod.use_bisect_flip_axis[axisv] = axism

            mod.use_clip = True
            if mirror_object:
                mod.mirror_object = mirror_object

            mod.use_mirror_u = preference.operator.mirror.mirror_u
            mod.use_mirror_v = preference.operator.mirror.mirror_v

            if preference.operator.mirror.mode == "MODIFIERAPPLY":
                if object.type in {"MESH"}:
                    if self.edit_mode:
                        bpy.ops.object.mode_set(mode='OBJECT')
                    modifier.apply(object, modifiers=[mod])
                    if self.edit_mode:
                        bpy.ops.object.mode_set(mode='EDIT')

    def data(self):
        value = 0
        x = (False, False, False)
        y = (False, False, False)
        z = (False, False, False)
        main = x
        normal = Vector((1, 0, 0))

        return normal, value, main, x, y, z


class HOPS_OT_MirrorExecuteXGizmo(Operator, HOPS_OT_MirrorOperator):
    bl_idname = "hops.mirror_execute_x_gizmo"
    bl_label = "Mirror -X axis"
    bl_description = "Mirror via -X"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def data(self):
        preference = get_preferences()

        value = 0
        x = (True, True, True)
        y = (False, False, False)
        z = (False, False, False)
        normal = Vector((1, 0, 0))

        if preference.operator.mirror.revert:
            x = (True, True, False)
            normal = Vector((-1, 0, 0))

        main = x
        return normal, value, main, x, y, z


class HOPS_OT_MirrorExecuteXmGizmo(Operator, HOPS_OT_MirrorOperator):
    bl_idname = "hops.mirror_execute_xm_gizmo"
    bl_label = "Mirror X axis"
    bl_description = "Mirror via X"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def data(self):
        preference = get_preferences()

        value = 0
        x = (True, True, False)
        y = (False, False, False)
        z = (False, False, False)
        normal = Vector((-1, 0, 0))

        if preference.operator.mirror.revert:
            x = (True, True, True)
            normal = Vector((1, 0, 0))

        main = x
        return normal, value, main, x, y, z


class HOPS_OT_MirrorExecuteYGizmo(Operator, HOPS_OT_MirrorOperator):
    bl_idname = "hops.mirror_execute_y_gizmo"
    bl_label = "Mirror -Y axis"
    bl_description = "Mirror via -Y"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def data(self):
        preference = get_preferences()

        value = 1
        x = (False, False, False)
        y = (True, True, True)
        z = (False, False, False)
        normal = Vector((0, 1, 0))

        if preference.operator.mirror.revert:
            y = (True, True, False)
            normal = Vector((0, -1, 0))

        main = y
        return normal, value, main, x, y, z


class HOPS_OT_MirrorExecuteYmGizmo(Operator, HOPS_OT_MirrorOperator):
    bl_idname = "hops.mirror_execute_ym_gizmo"
    bl_label = "Mirror Y axis"
    bl_description = "Mirror via Y"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def data(self):
        preference = get_preferences()

        value = 1
        x = (False, False, False)
        y = (True, True, False)
        z = (False, False, False)
        normal = Vector((0, -1, 0))

        if preference.operator.mirror.revert:
            y = (True, True, True)
            normal = Vector((0, 1, 0))

        main = y
        return normal, value, main, x, y, z


class HOPS_OT_MirrorExecuteZGizmo(Operator, HOPS_OT_MirrorOperator):
    bl_idname = "hops.mirror_execute_z_gizmo"
    bl_label = "Mirror -Z axis"
    bl_description = "Mirror via -Z"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def data(self):
        preference = get_preferences()

        value = 2
        x = (False, False, False)
        y = (False, False, False)
        z = (True, True, True)
        normal = Vector((0, 0, 1))

        if preference.operator.mirror.revert:
            z = (True, True, False)
            normal = Vector((0, 0, -1))

        main = z
        return normal, value, main, x, y, z


class HOPS_OT_MirrorExecuteZmGizmo(Operator, HOPS_OT_MirrorOperator):
    bl_idname = "hops.mirror_execute_zm_gizmo"
    bl_label = "Mirror Z axis"
    bl_description = "Mirror via Z"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def data(self):
        preference = get_preferences()

        value = 2
        x = (False, False, False)
        y = (False, False, False)
        z = (True, True, False)

        normal = Vector((0, 0, -1))

        if preference.operator.mirror.revert:
            z = (True, True, True)
            normal = Vector((0, 0, 1))

        main = z
        return normal, value, main, x, y, z


class HOPS_OT_MirrorRemoveGizmo(Operator):
    bl_idname = "hops.mirror_remove_gizmo"
    bl_label = "Mirror Gizmo Remove"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        ob = context.object
        return getattr(ob, "type", "") in {"MESH", "EMPTY", "CURVE"}

    def execute(self, context):
        preference = get_preferences()
        preference.property.Hops_gizmo_mirror = False
        context.area.tag_redraw()
        bpy.types.WindowManager.gizmo_group_type_remove("Hops_mirror_gizmo")
        # bpy.types.WindowManager.Hops_mirror_gizmo

        return {'FINISHED'}


class HOPS_OT_MirrorGizmo(Operator):
    bl_idname = "hops.mirror_gizmo"
    bl_label = "Mirror Gizmo"
    bl_options = {"REGISTER"}
    bl_description = """Interactive Mirror Gizmo - Mir3
    
    Active tool. UI up top of 3d view for adjustment.

    D - Menu for Adjustment
    A - Add additional mirror
    X - Reset To Default

    """

    other_gizmos = False
    close = False

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return getattr(ob, "type", "") in {"MESH", "EMPTY", "CURVE", "GPENCIL"}


    def invoke(self, context, event):

        self.preference = get_preferences()
        active = context.active_object

        self.display_msg = self.preference.operator.mirror.mode
        bpy.ops.hops.display_notification(info=self.display_msg)

        mods = [mod for mod in active.modifiers if mod.type == "MIRROR"]
        if len(mods) > 0:
            self.preference.operator.mirror.modifier = mods[-1].name

        bpy.context.space_data.show_gizmo_tool = True
        bpy.context.space_data.show_gizmo = True

        if bpy.context.space_data.show_gizmo_context:
            self.other_gizmos = True
            bpy.context.space_data.show_gizmo_context = False

        current_tool = view3d_tools.tool_active_from_context(bpy.context).idname
        self.current_tool = current_tool

        bpy.ops.wm.tool_set_by_id(name="builtin.select", space_type='VIEW_3D')

        if context.space_data.type == 'VIEW_3D':
            wm = context.window_manager
            wm.gizmo_group_type_ensure(HOPS_OT_MirrorGizmoGroup.bl_idname)

        self.preference.operator.mirror.running = True
        if context.space_data.type == 'VIEW_3D':
            context.area.tag_redraw()

        VIEW3D_HT_header._orgin_draw = VIEW3D_HT_header.draw
        VIEW3D_HT_header.draw = draw_header
        STATUSBAR_HT_header.draw = infobar
        context.window_manager.modal_handler_add(self)

        self.master = Master(context=context)
        self.master.only_use_fast_ui = True
        self.original_tool_shelf, self.original_n_panel = collapse_3D_view_panels()

        return {"RUNNING_MODAL"}


    def modal(self, context, event):

        self.master.receive_event(event=event)

        if self.display_msg != self.preference.operator.mirror.mode:
            self.display_msg = self.preference.operator.mirror.mode
            bpy.ops.hops.display_notification(info=self.display_msg)

        active = context.active_object
        overlap = 0 if context.preferences.system.use_region_overlap else 22 * context.preferences.system.ui_scale
        within_region_3d_x = event.mouse_region_x > 0 and event.mouse_region_x < context.region.width
        within_region_3d = within_region_3d_x and event.mouse_region_y > 0 - overlap and event.mouse_region_y < context.region.height + overlap

        if within_region_3d:

            if event.shift:
                if self.close is False:
                    if self.preference.operator.mirror.close is True:
                        self.preference.operator.mirror.close = False
                        self.close = True
                        context.area.tag_redraw()
                if event.type == "RIGHTMOUSE":
                    if event.value == "PRESS":
                        self.preference.operator.mirror.close = True
            else:
                if self.close:
                    self.preference.operator.mirror.close = True
                    self.close = False
                    context.area.tag_redraw()

            if self.preference.operator.mirror.running is False or event.type in ("ESC", "RIGHTMOUSE", "SPACE"):
                bpy.ops.wm.tool_set_by_id(name=self.current_tool, space_type='VIEW_3D')
                context.window_manager.gizmo_group_type_unlink_delayed(HOPS_OT_MirrorGizmoGroup.bl_idname)
                VIEW3D_HT_header.draw = VIEW3D_HT_header._orgin_draw
                STATUSBAR_HT_header.draw = STATUSBAR_HT_header._draw_orig
                if self.other_gizmos:
                    bpy.context.space_data.show_gizmo_context = True
                # bpy.ops.hops.display_notification(info="Closed")
                collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
                self.master.run_fade()
                context.area.tag_redraw()
                return {"FINISHED"}

            if event.type == "TAB":
                if event.value == "PRESS":
                    self.preference.operator.mirror.advanced = not self.preference.operator.mirror.advanced
                    bpy.ops.hops.display_notification(info="Advanced" if self.preference.operator.mirror.advanced else "Simple")

            if event.type == "D":
                if event.value == "PRESS":
                    bpy.ops.wm.call_menu(name=HOPS_MT_MirrorMenu.bl_idname)

            if event.type == "A":
                if event.value == "PRESS":
                    self.preference.operator.mirror.mode = 'NEWMODIFIER' if self.preference.operator.mirror.mode == 'MODIFIER' else 'MODIFIER'
                    bpy.ops.hops.display_notification(info=self.preference.operator.mirror.mode)

            if event.type == "V":
                if event.value == "PRESS":
                    self.preference.operator.mirror.advanced = True
                    self.preference.operator.mirror.orientation = "VIEW"
                    bpy.ops.hops.display_notification(info=self.preference.operator.mirror.orientation)

            if self.preference.operator.mirror.advanced:
                if event.type == "W":
                    if event.value == "PRESS":
                        orientation = ["LOCAL", "GLOBAL", "VIEW", "CURSOR"]
                        self.preference.operator.mirror.orientation = orientation[(orientation.index(self.preference.operator.mirror.orientation) + 1) % len(orientation)]
                        bpy.ops.hops.display_notification(info=self.preference.operator.mirror.orientation)

                if event.type == "S":
                    if event.value == "PRESS":
                        pivot = ["ACTIVE", "MEDIAN", "CURSOR", "INDIVIDUAL"]
                        self.preference.operator.mirror.pivot = pivot[(pivot.index(self.preference.operator.mirror.pivot) + 1) % len(pivot)]
                        bpy.ops.hops.display_notification(info= self.preference.operator.mirror.pivot)

            if event.type == "X":
                if event.value == "PRESS":
                    self.preference.operator.mirror.mode = "MODIFIER"
                    self.preference.operator.mirror.orientation = "LOCAL"
                    self.preference.operator.mirror.pivot = "ACTIVE"
                    #bpy.ops.hops.display_notification(info="Reset To Default")
                    bpy.ops.hops.display_notification(info=self.preference.operator.mirror.mode)

            if event.type == "H":
                if event.value == "PRESS":
                    get_preferences().property.hops_modal_help = not get_preferences().property.hops_modal_help

            if event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
                if event.ctrl or event.alt:
                    if event.ctrl:
                        mode = ["MODIFIER", "MODIFIERAPPLY", "BISECTMOD"]
                    if event.alt:
                        mode = ["MODIFIER", "NEWMODIFIER", "MODIFIERAPPLY", "BISECT", 'BISECTMOD', 'SYMMETRY']
                    option = self.preference.operator.mirror.mode if self.preference.operator.mirror.mode in mode else "MODIFIER"
                    if event.type == 'WHEELUPMOUSE':
                        self.preference.operator.mirror.mode = mode[(mode.index(option) + 1) % len(mode)]
                    else:
                        self.preference.operator.mirror.mode = mode[(mode.index(option) - 1) % len(mode)]
                    bpy.ops.hops.display_notification(info=self.preference.operator.mirror.mode)
                else:
                    return {"PASS_THROUGH"}

            if event.type == 'MOUSEMOVE':
                return {"PASS_THROUGH"}

            if event.type in {'MIDDLEMOUSE'}:
                return {"PASS_THROUGH"}

            elif event.type == 'LEFTMOUSE':
                return {"PASS_THROUGH"}

        self.draw_ui(context=context)

        return {"RUNNING_MODAL"}


    def draw_ui(self, context):

        # Start
        self.master.setup()

        if self.master.should_build_fast_ui():

            # Help
            preference = get_preferences()
            help_list = []
            mods_list = []

            #Empty Status
            if self.preference.operator.mirror.orientation != "LOCAL" or self.preference.operator.mirror.pivot != "ACTIVE":
                help_list.append([" ", "X to Reset"])
            help_list.append([" ", " "])
            if preference.operator.mirror.include_active and len(context.selected_objects) >= 2:
                help_list.append([" ", "Active selection included"])
            if creating_empty == True:
                help_list.append([" ", "Empty will be created (X)"])
            else:
                help_list.append([" ", "No Empty Will be created"])

            help_list.append([" ", " "])

            if self.preference.operator.mirror.advanced: 
                #Pivot
                #pivot = ["ACTIVE", "MEDIAN", "CURSOR", "INDIVIDUAL"]
                if self.preference.operator.mirror.pivot == "ACTIVE":
                    help_list.append([" ", "Default - Local Origin"])
                elif self.preference.operator.mirror.pivot == "MEDIAN":
                    help_list.append([" ", "Median - Median Origin"])
                elif self.preference.operator.mirror.pivot == "CURSOR":
                    help_list.append([" ", "Cursor - Cursor Origin"])
                elif self.preference.operator.mirror.pivot == "INDIVIDUAL":
                    help_list.append([" ", "Individual - Individual Origin"])

                #Orientation
                if self.preference.operator.mirror.orientation == "LOCAL":
                    help_list.append([" ", "Default - Local Orientation"])
                elif self.preference.operator.mirror.orientation == "GLOBAL":
                    help_list.append([" ", "Global - World Orientation"])
                elif self.preference.operator.mirror.orientation == "VIEW":
                    help_list.append([" ", "View - View Orientation"])
                elif self.preference.operator.mirror.orientation == "CURSOR":
                    help_list.append([" ", "Cursor - 3d Cursor Orientation"])
                #help_list.append([" ", " "])

                #Modes
                if self.preference.operator.mirror.mode == "MODIFIER": #"NEWMODIFIER", "BISECTMOD", "MODIFIERAPPLY"}:
                    help_list.append([" ", "Add / Adjust mirror mod"])
                elif self.preference.operator.mirror.mode == "NEWMODIFIER":
                    help_list.append([" ", "Add new mirror mod"])
                elif self.preference.operator.mirror.mode == "BISECTMOD":
                    help_list.append([" ", "Split mesh / mirror "])
                elif self.preference.operator.mirror.mode == "MODIFIERAPPLY":
                    help_list.append([" ", "Add & Apply mirror mod"])
                elif self.preference.operator.mirror.mode == "SYMMETRY":
                    help_list.append([" ", "Mesh Symetrization "])
                elif self.preference.operator.mirror.mode == "BISECT":
                    help_list.append([" ", "Split Mesh - No Mirror"])

            help_list.append([" ", " "])
            help_list.append(["RMB", "Exit"])
            help_list.append(["ALT + Scroll ", "Full List"])
            help_list.append(["CTRL + Scroll ", "Short List"])
            if self.preference.operator.mirror.close:
                help_list.append(["Shift", "Append Axis"])
            help_list.append(["A", "Add New Mirror Modifier"])
            if self.preference.operator.mirror.advanced:
                help_list.append(["S", f"Cycle Pivot Points - {self.preference.operator.mirror.pivot}"])
                help_list.append(["W", f"Cycle Orientations - {self.preference.operator.mirror.orientation}"])
            help_list.append(["V", "View Orientation - " + "True" if self.preference.operator.mirror.orientation == "VIEW" else "View Orientation - " + "False"])
            help_list.append(["X", "Reset To Default Options"])
            help_list.append(["D", "Mirror Menu"])
            help_list.append(["M", "Modifier List"])
            help_list.append(["H", "Display Help"])
            help_list.append(["TAB    ", "Simple Mode" if self.preference.operator.mirror.advanced else "Advanced Mode"])
            help_list.append([" ", " "])
            #Modes
            if self.preference.operator.mirror.mode == "MODIFIER": #"NEWMODIFIER", "BISECTMOD", "MODIFIERAPPLY"}:
                if len([mod for mod in bpy.context.active_object.modifiers if mod.type == 'MIRROR']):
                    help_list.append([" ", "Adjust mirror mod"])
                else:
                    if len(context.selected_objects) >= 2:
                        if preference.operator.mirror.include_active:
                            help_list.append([" ", "Mirror all across primary selection"])
                        else:
                            help_list.append([" ", "Mirror across primary selection"])
                    else:
                        help_list.append([" ", "Add mirror mod"])
            elif self.preference.operator.mirror.mode == "NEWMODIFIER":
                help_list.append([" ", "Add new mirror mod"])
            elif self.preference.operator.mirror.mode == "BISECTMOD":
                #help_list.append([" ", "Add mirror modifier "])
                help_list.append([" ", "Delete half / Add mirror"])
            elif self.preference.operator.mirror.mode == "MODIFIERAPPLY":
                help_list.append([" ", "Add & Apply mirror mod"])
            elif self.preference.operator.mirror.mode == "SYMMETRY":
                help_list.append([" ", "Mesh Symetrization "])
            elif self.preference.operator.mirror.mode == "BISECT":
                help_list.append([" ", "Split Mesh - No Mirror"])
            if len(bpy.context.selected_objects) >= 2 and self.preference.operator.mirror.mode == 'MODIFIER':
                help_list.append([" ", f"To_{self.preference.operator.mirror.mode}"]) 
            else:
                help_list.append([" ", f"{self.preference.operator.mirror.mode}"]) 

            # Mods
            active_mod = ""
            if preference.operator.mirror.mode == 'MODIFIER':
                if preference.operator.mirror.modifier and preference.operator.mirror.modifier != 'new':
                    active_mod = preference.operator.mirror.modifier

            mods_list = get_mods_list(mods=bpy.context.active_object.modifiers)
            self.master.receive_fast_ui(help_list=help_list, mods_list=mods_list, active_mod_name=active_mod)

        # Finished
        self.master.finished()


class HOPS_OT_MirrorGizmoGroup(GizmoGroup):
    bl_idname = "hops.mirror_gizmogroup"
    bl_label = "Mirror Gizmo Group"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D'}

    @classmethod
    def poll(cls, context):
        ob = context.object
        if len(context.selected_objects) > 0:
            return getattr(ob, "type", "") in {"MESH", "EMPTY", "CURVE", "GPENCIL"}

    def setup(self, context):
        selected = context.selected_objects
        if len(selected) == 1:
            self.multiselection = False
        else:
            self.multiselection = True

        self.cross_p = self.gizmos.new("GIZMO_GT_arrow_3d")
        self.draw_cross(context, self.cross_p, "hops.mirror_execute_z_gizmo", (0.157, 0.565, 1))
        self.cross_n = self.gizmos.new("GIZMO_GT_arrow_3d")
        self.draw_cross(context, self.cross_n, "hops.mirror_execute_z_gizmo", (0.157, 0.565, 1))

        self.arrow_z_p = self.gizmos.new("GIZMO_GT_arrow_3d")
        self.draw_arrow(context, self.arrow_z_p, "hops.mirror_execute_z_gizmo", (0.157, 0.565, 1))
        self.arrow_z_n = self.gizmos.new("GIZMO_GT_arrow_3d")
        self.draw_arrow(context, self.arrow_z_n, "hops.mirror_execute_zm_gizmo", (0.157, 0.565, 1))
        self.arrow_x_p = self.gizmos.new("GIZMO_GT_arrow_3d")
        self.draw_arrow(context, self.arrow_x_p, "hops.mirror_execute_x_gizmo", (1, 0.2, 0.322))
        self.arrow_x_n = self.gizmos.new("GIZMO_GT_arrow_3d")
        self.draw_arrow(context, self.arrow_x_n, "hops.mirror_execute_xm_gizmo", (1, 0.2, 0.322))
        self.arrow_y_p = self.gizmos.new("GIZMO_GT_arrow_3d")
        self.draw_arrow(context, self.arrow_y_p, "hops.mirror_execute_y_gizmo", (0.545, 0.863, 0))
        self.arrow_y_n = self.gizmos.new("GIZMO_GT_arrow_3d")
        self.draw_arrow(context, self.arrow_y_n, "hops.mirror_execute_ym_gizmo", (0.545, 0.863, 0))

    def draw_prepare(self, context):
        preference = get_preferences()

        active = context.active_object
        selected = context.selected_objects
        if len(selected) == 1:
            self.multiselection = False
        else:
            self.multiselection = True

        ob = context.active_object
        matrix_world = ob.matrix_world.copy()

        self.cross_p.matrix_basis = self.redraw_arrow(context, matrix_world, 180, 'X')
        self.cross_n.matrix_basis = self.redraw_arrow(context, matrix_world, -90, 'Y')

        self.arrow_z_p.matrix_basis = self.redraw_arrow(context, matrix_world, 180, 'X')
        self.arrow_z_n.matrix_basis = self.redraw_arrow(context, matrix_world, 0, 'X')
        self.arrow_x_p.matrix_basis = self.redraw_arrow(context, matrix_world, -90, 'Y')
        self.arrow_x_n.matrix_basis = self.redraw_arrow(context, matrix_world, 90, 'Y')
        self.arrow_y_p.matrix_basis = self.redraw_arrow(context, matrix_world, 90, 'X')
        self.arrow_y_n.matrix_basis = self.redraw_arrow(context, matrix_world, -90, 'X')

        if preference.operator.mirror.advanced:
            self.arrow_z_p.hide = self.arrow_z_n.hide = True if preference.operator.mirror.orientation == "VIEW" and preference.operator.mirror.mode != 'SYMMETRY' else False
            self.cross_p.hide = self.cross_n.hide = True if ((preference.operator.mirror.orientation == "LOCAL" and preference.operator.mirror.pivot in {"ACTIVE", "INDIVIDUAL"}) or preference.operator.mirror.mode in {'SYMMETRY', 'MODIFIERAPPLY'}) else False
        else:
            self.arrow_z_p.hide = self.arrow_z_n.hide = False
            self.cross_p.hide = self.cross_n.hide = True

        global creating_empty
        if self.cross_p.hide == True:
            creating_empty = False
        else:
            creating_empty = True


        if preference.operator.mirror.mode == "MODIFIER":

            if active.type == "GPENCIL":
                mods = [mod for mod in active.grease_pencil_modifiers if mod.type == "GP_MIRROR"]

                if len(mods) > 0:
                    activemod = [mod for mod in mods if mod.name == preference.operator.mirror.modifier]
                    mod = activemod[0]
                    if mod.x_axis:
                        self.arrow_x_p.color = 0.4, 0.4, 0.4
                        self.arrow_x_n.color = 0.4, 0.4, 0.4
                    else:
                        self.arrow_x_p.color = 1, 0.2, 0.322
                        self.arrow_x_n.color = 1, 0.2, 0.322
                    if mod.y_axis:
                        self.arrow_y_p.color = 0.4, 0.4, 0.4
                        self.arrow_y_n.color = 0.4, 0.4, 0.4
                    else:
                        self.arrow_y_p.color = 0.545, 0.863, 0
                        self.arrow_y_n.color = 0.545, 0.863, 0
                    if mod.z_axis:
                        self.arrow_z_p.color = 0.4, 0.4, 0.4
                        self.arrow_z_n.color = 0.4, 0.4, 0.4
                    else:
                        self.arrow_z_p.color = 0.157, 0.565, 1
                        self.arrow_z_n.color = 0.157, 0.565, 1

            else:
                mods = [mod for mod in active.modifiers if mod.type == "MIRROR"]

                if len(mods) > 0:
                    activemod = [mod for mod in mods if mod.name == preference.operator.mirror.modifier]
                    mod = activemod[0]

                    if mod.use_axis[0]:
                        self.arrow_x_p.color = 0.4, 0.4, 0.4
                        self.arrow_x_n.color = 0.4, 0.4, 0.4
                    else:
                        self.arrow_x_p.color = 1, 0.2, 0.322
                        self.arrow_x_n.color = 1, 0.2, 0.322
                    if mod.use_axis[1]:
                        self.arrow_y_p.color = 0.4, 0.4, 0.4
                        self.arrow_y_n.color = 0.4, 0.4, 0.4
                    else:
                        self.arrow_y_p.color = 0.545, 0.863, 0
                        self.arrow_y_n.color = 0.545, 0.863, 0
                    if mod.use_axis[2]:
                        self.arrow_z_p.color = 0.4, 0.4, 0.4
                        self.arrow_z_n.color = 0.4, 0.4, 0.4
                    else:
                        self.arrow_z_p.color = 0.157, 0.565, 1
                        self.arrow_z_n.color = 0.157, 0.565, 1

        else:
            self.arrow_x_p.color = 1, 0.2, 0.322
            self.arrow_x_n.color = 1, 0.2, 0.322
            self.arrow_y_p.color = 0.545, 0.863, 0
            self.arrow_y_n.color = 0.545, 0.863, 0
            self.arrow_z_p.color = 0.157, 0.565, 1
            self.arrow_z_n.color = 0.157, 0.565, 1

    def draw_cross(self, context, cross, operaotr, color):
        
        cross.target_set_operator(operaotr)

        cross.line_width = 1
        cross.draw_style = 'CROSS'
        cross.hide_select = True

        cross.color = 0.1, 0.1, 0.1
        cross.alpha = 1
        cross.scale_basis = 0.7
        # cross.color_highlight = color[0] * 1.6, color[1] * 1.6, color[2] * 1.6
        # cross.alpha_highlight = 0.8

    def draw_arrow(self, context, arrow, operaotr, color,):

        arrow.target_set_operator(operaotr)

        arrow.line_width = 0.1
        arrow.draw_style = 'BOX'

        arrow.color = color[0], color[1], color[2]
        arrow.alpha = 0.5
        arrow.scale_basis = 2.2

        arrow.color_highlight = color[0] * 1.6, color[1] * 1.6, color[2] * 1.6
        arrow.alpha_highlight = 0.8

    def redraw_arrow(self, context, matrix, angle, axis):
        preference = get_preferences()
        obloc, obrot, obscale = matrix.decompose()
        selected = context.selected_objects

        if preference.operator.mirror.orientation == "GLOBAL":
            rot = Euler((0, 0, 0), "XYZ").to_quaternion()
        elif preference.operator.mirror.orientation == "CURSOR":
            rot = context.scene.cursor.rotation_euler.to_quaternion()
        elif preference.operator.mirror.orientation == "LOCAL":
            rot = obrot
        elif preference.operator.mirror.orientation == "VIEW":
            rot = context.region_data.view_rotation

        if preference.operator.mirror.pivot in {"ACTIVE", "INDIVIDUAL"}:
            loc = obloc
        elif preference.operator.mirror.pivot == "CURSOR":
            loc = context.scene.cursor.location
        elif preference.operator.mirror.pivot == "MEDIAN":
            if len(selected) > 0:
                selected_loc = [obj.matrix_world.translation for obj in selected]
                loc = sum(selected_loc, Vector()) / len(selected)
            else:
                loc = obloc

        if preference.operator.mirror.mode == 'SYMMETRY' or not preference.operator.mirror.advanced:
            rot, loc = obrot, obloc

        rotation = rot.to_matrix().to_4x4() @ Matrix.Rotation(radians(angle), 4, axis)
        matrix_basis = Matrix.Translation(loc) @ rotation @ Matrix.Scale(1, 4, (1.0, 1.0, 1.0))

        return matrix_basis.normalized()


class HOPS_MT_MirrorMenu(bpy.types.Menu):
    bl_idname = "HOPS_MT_MirrorMenu"
    bl_label = "Mirror Menu"

    def draw(self, context):
        preference = get_preferences()
        layout = self.layout
        layout.label(text="Mode")
        layout.prop(preference.operator.mirror, 'mode', expand=True)
        layout.separator()
        if preference.operator.mirror.advanced:
            layout.label(text="Orientation")
            layout.prop(preference.operator.mirror, 'orientation', expand=True)
            layout.separator()
            layout.label(text="Pivot Point")
            layout.prop(preference.operator.mirror, 'pivot', expand=True)
        else:
            layout.prop(preference.operator.mirror, 'advanced', text="Advanced", toggle=True, icon='ORIENTATION_GIMBAL')


class HOPS_PT_MirrorOptions(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_label = "Mirror Options"

    def draw(self, context):
        preference = get_preferences()
        layout = self.layout
        layout.label(text="Mirror Settings")
        layout.separator()
        layout.prop(preference.operator.mirror, 'mirror_u', text="Textures Flip u")
        layout.prop(preference.operator.mirror, 'mirror_v', text="Textures Flip v")
        layout.separator()
        layout.prop(preference.operator.mirror, 'include_active', text="Include active in multi mirroring")
        layout.prop(preference.operator.mirror, 'parent_empty', text="Parent empty to active object")
        layout.separator()
        layout.prop(preference.operator.mirror, 'revert', text="Revert Gizmo handlers")


class HOPS_PT_mirror_mode(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_label = "Mirror Mode"
    bl_ui_units_x = 8

    def draw(self, context):
        preference = get_preferences()
        layout = self.layout
        layout.label(text="Mirror Mode")

        row = layout.row()
        col = row.column()
        col.prop(preference.operator.mirror, 'mode', expand=True)


class HOPS_PT_mirror_transform_orientations(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_label = "Mirror Transform Orientations"
    bl_ui_units_x = 8

    def draw(self, context):
        preference = get_preferences()
        layout = self.layout
        layout.label(text="Transform Orientations")

        row = layout.row()
        col = row.column()
        col.prop(preference.operator.mirror, 'orientation', expand=True)


class HOPS_PT_mirror_pivot(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_label = "Mirror Pivot Point"
    bl_ui_units_x = 8

    def draw(self, context):
        preference = get_preferences()
        layout = self.layout
        layout.label(text="Mirror Pivot Point")

        row = layout.row()
        col = row.column()
        col.prop(preference.operator.mirror, 'pivot', expand=True)


def draw_header(ht, context):
    preference = get_preferences()
    mir = preference.operator.mirror
    selected = context.selected_objects
    layout = ht.layout
    mir_string = f'{"Empty will be created" if mir.orientation != "LOCAL" and mir.mode != "MODIFIERAPPLY" or mir.pivot != "ACTIVE" else "No Empty Will be created"}'
    #if self.preference.operator.mirror.orientation != "LOCAL" and self.preference.operator.mirror.mode != "MODIFIERAPPLY" or self.preference.operator.mirror.pivot != "ACTIVE" else
    if len(selected) < 1:
        mir_string = f'No Selection - Please make selection'
    layout.label(text=f'Mirror Gizmo - {mir_string}')

    layout.separator_spacer()

    layout.prop_with_popover(preference.operator.mirror, "mode", text="", panel="HOPS_PT_mirror_mode")
    if preference.operator.mirror.mode == 'MODIFIER':
        layout.prop(preference.operator.mirror, "modifier", text="")

    layout.prop(preference.operator.mirror, 'advanced', text="", toggle=True, icon='ORIENTATION_GIMBAL')

    if preference.operator.mirror.advanced:
        if preference.operator.mirror.mode != 'SYMMETRY':
            layout.prop_with_popover(preference.operator.mirror, "orientation", text="", panel="HOPS_PT_mirror_transform_orientations")
            layout.prop_with_popover(preference.operator.mirror, "pivot", text="", panel="HOPS_PT_mirror_pivot")
    layout.popover('HOPS_PT_MirrorOptions', text='', icon="SETTINGS")

    layout.separator_spacer()

    layout.prop(preference.operator.mirror, 'close', text="Close after operation", toggle=True)
    layout.operator('hops.mirror_exit', text='Exit')


def infobar(self, context):
    layout = self.layout
    row = self.layout.row(align=True)
    preference = get_preferences()

    row.label(text="", icon='MOUSE_LMB')
    row.label(text="Mirror")

    row.separator(factor=8.0)

    row.label(text="", icon='MOUSE_MMB')
    row.label(text="Rotate View")

    row.separator(factor=8.0)

    row.label(text="", icon='MOUSE_RMB')
    row.label(text="Exit")

    row.separator(factor=12.0)

    row.label(text="", icon='EVENT_SHIFT')
    row.label(text="Multi Mirror")

    row.separator(factor=2.0)

    row.label(text="", icon='EVENT_TAB')
    row.label(text="Advenced mode")

    row.separator(factor=2.0)

    row.label(text="", icon='EVENT_D')
    row.label(text="Menu")

    row.separator(factor=2.0)

    row.label(text="", icon='EVENT_A')
    row.label(text="Mod Modes")

    if preference.operator.mirror.advanced:
        row.separator(factor=2.0)

        row.label(text="", icon='EVENT_S')
        row.label(text="Cycle Pivot Points")

        row.separator(factor=2.0)

        row.label(text="", icon='EVENT_W')
        row.label(text="Cycle Orientation")

    row.separator(factor=2.0)

    row.label(text="", icon='EVENT_V')
    row.label(text="View Orientation")

    row.separator(factor=2.0)

    row.label(text="", icon='EVENT_X')
    row.label(text="Reset")

    row.separator(factor=2.0)

    row.label(text="", icon='EVENT_H')
    row.label(text="HELP")

    row.separator(factor=2.0)

    row.label(text="", icon='EVENT_M')
    row.label(text="MODS")

    layout.separator_spacer()

    layout.template_reports_banner()
    layout.template_running_jobs()

    layout.separator_spacer()

    scene = context.scene
    view_layer = context.view_layer

    if bpy.app.version < (2, 90, 0):
        layout.label(text=scene.statistics(view_layer), translate=False)