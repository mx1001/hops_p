import bpy, bmesh, mathutils, math, copy
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... preferences import get_preferences
from ... utility.renderer import cycles
from ... utils.objects import set_active
from ... utility import collections,  object
from ... utility import math as hops_math
from ... utility.base_modal_controls import Base_Modal_Controls
from ...ui_framework.utils.mods_list import get_mods_list
from . import operator
from .. meshtools.applymod import apply_mod
from ...ui_framework.master import Master
from ...ui_framework.utils.mods_list import get_mods_list
from mathutils import Vector, Matrix

# Cursor Warp imports
from ... utils.toggle_view3d_panels import collapse_3D_view_panels
from ... utils.modal_frame_drawing import draw_modal_frame
from ... utils.cursor_warp import mouse_warp
from ... addon.utility import method_handler


class HOPS_OT_BoolDice(bpy.types.Operator):
    bl_idname = "hops.bool_dice"
    bl_label = "Hops Boolean Dice"
    bl_options = {'REGISTER', 'UNDO', 'BLOCKING'}
    bl_description = """Dice Loopcut

LMB - Dice on last used axes
Shift + LMB - Dice active from selection
Ctrl + LMB - Dice on all axes
Alt + LMB - Smart Apply Dice (applies select modifiers)
"""

    axis: bpy.props.EnumProperty(
        name="Axis",
        description="What axis to dice on",
        items=[
            ('X', "X", "Dice on the X axis"),
            ('Y', "Y", "Dice on the Y axis"),
            ('Z', "Z", "Dice on the Z axis")],
        default='X')

    axes: bpy.props.BoolVectorProperty(
        name="Axes",
        description="Which axes to dice on",
        default=(True, False, False),
        size=3)

    count: bpy.props.IntProperty(
        name="Count",
        description="How many cutting planes to make on each axis",
        min=1,
        soft_max=100,
        default=5)

    use_knife_project: bpy.props.BoolProperty(
        name="Use Knife Project",
        description="Otherwise use mesh intersect",
        default=True)

    smart_apply: bpy.props.BoolProperty(
        name="Smart Apply",
        description="Uses smart apply prior to dice to ensure dicing is received",
        default=False)

    to_twist = 'None'

    def __init__(self):

        # Modal UI
        self.master = None


    @classmethod
    def poll(cls, context):

        obj = context.active_object
        return obj and obj.type == 'MESH' and obj.mode in {'OBJECT', 'EDIT'}


    def draw(self, context):

        axes = ", ".join(a for i,a in enumerate("XYZ") if self.axes[i])
        self.layout.label(text=f"Axes: {axes}")
        self.layout.label(text=f"Segments: {self.count}")
        self.layout.label(text=f"Method: {'Knife Project' if self.use_knife_project else 'Mesh Intersect'}")

    # Without execute, draw doesn't work
    def execute(self, context):

        return {'FINISHED'}


    def invoke(self, context, event):

        self.modal_scale = get_preferences().ui.Hops_modal_scale
        self.obj = context.active_object
        self.mode = self.obj.mode
        if  not self.obj.select_get():
            self.obj.select_set(True)
        self.smart_apply = event.alt or get_preferences().property.smart_apply_dice != 'NONE'
        if event.alt or get_preferences().property.smart_apply_dice == 'SMART_APPLY':
            if context.object.mode == 'OBJECT':
                apply_mod(self, self.obj, clear_last=False)
                bpy.ops.hops.display_notification(info=f'Smart Apply', name="")
                self.report({'INFO'}, F'Smart Applied')
            else:
                self.report({'INFO'}, F'Smart Apply Skipped')
        elif get_preferences().property.smart_apply_dice == 'APPLY':
            bpy.ops.object.convert(target='MESH')
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
            bpy.ops.hops.display_notification(info=f'Converted To Mesh', name="")
            self.report({'INFO'}, F'Converted To Mesh')

        self.selected = [o for o in context.selected_objects if o.type == 'MESH']
        self.sources = self.selected[:]

        if event.shift and len(self.sources)>1:
            self.sources.remove(self.obj)

        if len(self.sources)>1:
            self.big_box = True
            bound_boxes =[]
            if context.mode == "EDIT_MESH":
                for o in self.sources:
                    o.update_from_editmode()
                    bound_boxes.extend([o.matrix_world @ v.co for v in o.data.vertices if v.select])
            if context.mode == "OBJECT" or len(bound_boxes)<2 :
                for o in self.sources:
                    bound_boxes.extend( self.get_bound_box( o, o.matrix_world))

            self.bound_box = hops_math.coords_to_bounds(bound_boxes)
        else:
            self.big_box = False
            if context.mode == "EDIT_MESH":
                self.sources[0].update_from_editmode()
                bounds = [v.co for v in self.sources[0].data.vertices if v.select]
                if len(bounds)>1:
                    self.bound_box = hops_math.coords_to_bounds(bounds)
            if context.mode == "OBJECT" or len(bounds)<2:
                self.bound_box = self.get_bound_box( self.sources[0])
                set_active(self.sources[0], select=True, only_select=True)

        self.size = self.get_size(context, self.bound_box)

        self.adjusting = get_preferences().property.dice_adjust
        if event.ctrl and event.type == 'LEFTMOUSE':
            self.adjusting = 'NONE'

        self.axis_buffer = float("XYZ".find(self.axis))
        self.count_buffer = self.count

        self.plane_x = self.create_plane(context, 'X')
        self.plane_y = self.create_plane(context, 'Y')
        self.plane_z = self.create_plane(context, 'Z')

        if event.type == 'LEFTMOUSE' and event.ctrl:
            self.axes[0] = True
            self.axes[1] = True
            self.axes[2] = True

        self.plane_x.hide_set(not self.axes[0])
        self.plane_y.hide_set(not self.axes[1])
        self.plane_z.hide_set(not self.axes[2])

        self.use_knife_project = get_preferences().property.dice_method == 'KNIFE_PROJECT'
   #     if event.shift and event.type == 'LEFTMOUSE':
   #         self.use_knife_project = not self.use_knife_project

        self.mouse_prev_x = event.mouse_region_x
        self.mouse_start_x = event.mouse_region_x
        self.mouse_start_y = event.mouse_region_y

        # Base Systems
        self.master = Master(context=context)
        self.master.only_use_fast_ui = True
        self.base_controls = Base_Modal_Controls(context, event)
        self.original_tool_shelf, self.original_n_panel = collapse_3D_view_panels()
        self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.safe_draw_shader, (context,), 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    def modal(self, context, event):

        # Base Systems
        self.master.receive_event(event=event)
        self.base_controls.update(context, event)
        mouse_warp(context, event)
        original_remove_setting = get_preferences().property.Hops_sharp_remove_cutters

        if event.type == 'MIDDLEMOUSE':
            return {'PASS_THROUGH'}

        elif event.type == 'Z' and (event.shift or event.alt):
            return {'PASS_THROUGH'}

        elif event.type in {'LEFTMOUSE', 'SPACE'}:

            if not event.shift:
                if self.obj in self.sources:
                    targets = self.sources
                else:
                    targets = [self.obj]

                for obj in targets:
                    set_active(obj, select=True, only_select=True)
                    self.dice_target = obj
                    if self.axes[0]:
                        self.knife(context, 'X')
                    if self.axes[1]:
                        self.knife(context, 'Y')
                    if self.axes[2]:
                        self.knife(context, 'Z')

                self.remove_plane(context, self.plane_x)
                self.remove_plane(context, self.plane_y)
                self.remove_plane(context, self.plane_z)

            else:
                if not self.axes[0]:
                    self.remove_plane(context, self.plane_x)
                else:
                    collections.unlink_obj(context, self.plane_x)
                    collections.link_obj(context, self.plane_x, "Cutters")

                if not self.axes[1]:
                    self.remove_plane(context, self.plane_y)
                else:
                    collections.unlink_obj(context, self.plane_y)
                    collections.link_obj(context, self.plane_y, "Cutters")

                if not self.axes[2]:
                    self.remove_plane(context, self.plane_z)
                else:
                    collections.unlink_obj(context, self.plane_z)
                    collections.link_obj(context, self.plane_z, "Cutters")

            set_active(self.obj)
            for obj in self.selected:
                obj.select_set(True)
            if self.mode == 'EDIT':
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.mode_set(mode='EDIT')

            self.obj.show_wire = False
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()

            if self.to_twist == True:
                bpy.ops.array.twist('INVOKE_DEFAULT')
            self.report({'INFO'}, "Finished")
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:

            self.remove_plane(context, self.plane_x)
            self.remove_plane(context, self.plane_y)
            self.remove_plane(context, self.plane_z)

            set_active(self.obj)
            for obj in self.selected:
                obj.select_set(True)

            self.report({'INFO'}, "Cancelled")
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            return {'CANCELLED'}

        elif event.type == 'A' and event.value == 'PRESS':
            self.adjusting = 'NONE' if self.adjusting == 'AXIS' else 'AXIS'
            self.report({'INFO'}, f"{'Started' if self.adjusting != 'NONE' else 'Stopped'} Adjusting Axis")

        elif event.type == 'S' and event.shift and event.value == 'PRESS':
            self.adjusting = 'NONE' if self.adjusting == 'SEGMENTS' else 'SEGMENTS'
            self.report({'INFO'}, f"{'Started' if self.adjusting != 'NONE' else 'Stopped'} Adjusting Segments")

        elif event.type == 'S' and not event.shift and event.value == 'PRESS':
            if original_remove_setting:
                    get_preferences().property.Hops_sharp_remove_cutters = False
            bpy.ops.hops.apply_modifiers('INVOKE_DEFAULT')
            get_preferences().property.Hops_sharp_remove_cutters = original_remove_setting
            self.report({'INFO'}, f"Smart Apply")

        elif event.type == 'T' and not event.shift and event.value == 'PRESS':
            mod = None
            obj = bpy.context.object

            if self.to_twist is 'None':
                self.to_twist = True
                for mod in obj.modifiers:
                    if mod.type == 'BOOLEAN':
                        if original_remove_setting:
                                get_preferences().property.Hops_sharp_remove_cutters = False
                        bpy.ops.hops.apply_modifiers('INVOKE_DEFAULT')
                        get_preferences().property.Hops_sharp_remove_cutters = original_remove_setting
            else:
                self.to_twist = not self.to_twist
            self.report({'INFO'}, f"To_Twist {self.to_twist}")

        #elif event.type == 'W' and event.value == 'PRESS':

        elif event.type == 'MOUSEMOVE' and self.adjusting == 'AXIS':
            divisor = self.modal_scale * (2500 if event.shift else 250)
            offset = event.mouse_region_x - self.mouse_prev_x

            self.axis_buffer -= offset / divisor / get_dpi_factor()
            self.axis = "XYZ"[round(self.axis_buffer) % 3]

            self.axes[0] = self.axis == 'X'
            self.axes[1] = self.axis == 'Y'
            self.axes[2] = self.axis == 'Z'

            self.plane_x.hide_set(not self.axes[0])
            self.plane_y.hide_set(not self.axes[1])
            self.plane_z.hide_set(not self.axes[2])

            context.area.tag_redraw()

        elif event.type == 'MOUSEMOVE' and self.adjusting == 'SEGMENTS':
            divisor = self.modal_scale * (1000 if event.shift else 100)
            offset = event.mouse_region_x - self.mouse_prev_x

            self.count_buffer -= offset / divisor / get_dpi_factor()
            self.count_buffer = max(self.count_buffer, 1)
            self.count = round(self.count_buffer)

            for index, plane in enumerate([self.plane_x, self.plane_y, self.plane_z]):
                distance = self.size[index] / (self.count + 1)
                plane.modifiers["Array"].count = self.count
                plane.modifiers["Array"].constant_offset_displace[index] = distance
                plane.modifiers["Displace"].strength = distance

            context.area.tag_redraw()

        elif event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} or event.type in {'NUMPAD_PLUS', 'NUMPAD_MINUS'} and event.value == 'PRESS':
            offset = 1 if event.type in {'WHEELUPMOUSE', 'NUMPAD_PLUS'} else -1
            self.count_buffer += offset
            self.count_buffer = max(self.count_buffer, 1)
            self.count = round(self.count_buffer)

            for index, plane in enumerate([self.plane_x, self.plane_y, self.plane_z]):
                distance = self.size[index] / (self.count + 1)
                plane.modifiers["Array"].count = self.count
                plane.modifiers["Array"].constant_offset_displace[index] = distance
                plane.modifiers["Displace"].strength = distance

            context.area.tag_redraw()

        elif event.type == 'W' and event.value == 'PRESS':
            self.obj.show_wire = not self.obj.show_wire
            wire ={True:"ON", False:"OFF"}
            self.report({'INFO'}, F'Wireframe:{wire[self.obj.show_wire]}')

        elif event.type == 'X' and event.value == 'PRESS' and (self.axes[1] or self.axes[2]):
            self.adjusting = 'NONE'
            self.axes[0] = not self.axes[0]

            if self.axes[0]:
                self.axis = 'X'
                self.axis_buffer = 0

            self.plane_x.hide_set(not self.axes[0])
            self.report({'INFO'}, f"{'Enabled' if self.axes[0] else 'Disabled'} Axis X")

        elif event.type == 'Y' and event.value == 'PRESS' and (self.axes[0] or self.axes[2]):
            self.adjusting = 'NONE'
            self.axes[1] = not self.axes[1]

            if self.axes[1]:
                self.axis = 'Y'
                self.axis_buffer = 1

            self.plane_y.hide_set(not self.axes[1])
            self.report({'INFO'}, f"{'Enabled' if self.axes[1] else 'Disabled'} Axis Y")

        elif event.type == 'Z' and event.value == 'PRESS' and (self.axes[0] or self.axes[1]):
            self.adjusting = 'NONE'
            self.axes[2] = not self.axes[2]

            if self.axes[2]:
                self.axis = 'Z'
                self.axis_buffer = 2

            self.plane_z.hide_set(not self.axes[2])
            self.report({'INFO'}, f"{'Enabled' if self.axes[2] else 'Disabled'} Axis Z")

        elif event.type == 'Q' and event.value == 'PRESS':
            self.use_knife_project = not self.use_knife_project
            self.report({'INFO'}, f"Method: {'Knife Project' if self.use_knife_project else 'Mesh Intersect'}")

        elif event.type in {'ONE', 'TWO', 'THREE', 'FOUR'} and event.value == 'PRESS':
            if event.type == 'ONE':
                self.count = self.count_buffer = 7
            elif event.type == 'TWO':
                self.count = self.count_buffer = 15
            elif event.type == 'THREE':
                self.count = self.count_buffer = 23
            elif event.type == 'FOUR':
                self.count = self.count_buffer = 31

            for index, plane in enumerate([self.plane_x, self.plane_y, self.plane_z]):
                distance = self.size[index] / (self.count + 1)
                plane.modifiers["Array"].count = self.count
                plane.modifiers["Array"].constant_offset_displace[index] = distance
                plane.modifiers["Displace"].strength = distance

            context.area.tag_redraw()

        self.mouse_prev_x = event.mouse_region_x

        self.draw_master(context=context)

        context.area.tag_redraw()

        return {'RUNNING_MODAL'}


    def get_bound_box(self, obj, matrix = Matrix()):
        temp = bpy.data.objects.new("Bounding Box", obj.data)
        bound_box = object.bound_coordinates(temp, matrix)
        bpy.data.objects.remove(temp)
        return bound_box


    def get_size(self, context, bb):
        size_x = bb[6][0] - bb[0][0]
        size_y = bb[6][1] - bb[0][1]
        size_z = bb[6][2] - bb[0][2]
        return (size_x, size_y, size_z)


    def create_plane(self, context, axis):
        bb = [list(v) for v in self.bound_box]

        if axis != 'X':
            bb[0][0] -= 0.01
            bb[1][0] -= 0.01
            bb[2][0] -= 0.01
            bb[3][0] -= 0.01
            bb[4][0] += 0.01
            bb[5][0] += 0.01
            bb[6][0] += 0.01
            bb[7][0] += 0.01

        if axis != 'Y':
            bb[0][1] -= 0.01
            bb[1][1] -= 0.01
            bb[2][1] += 0.01
            bb[3][1] += 0.01
            bb[4][1] -= 0.01
            bb[5][1] -= 0.01
            bb[6][1] += 0.01
            bb[7][1] += 0.01

        if axis != 'Z':
            bb[0][2] -= 0.01
            bb[1][2] += 0.01
            bb[2][2] += 0.01
            bb[3][2] -= 0.01
            bb[4][2] -= 0.01
            bb[5][2] += 0.01
            bb[6][2] += 0.01
            bb[7][2] -= 0.01

        if axis == 'X':
            bb = [bb[0], bb[1], bb[2], bb[3]]
        if axis == 'Y':
            bb = [bb[0], bb[4], bb[5], bb[1]]
        if axis == 'Z':
            bb = [bb[0], bb[3], bb[7], bb[4]]

        plane_bm = bmesh.new()
        for vert in bb:
            plane_bm.verts.new(vert)
        plane_bm.faces.new(plane_bm.verts)

        plane_mesh = bpy.data.meshes.new(f"Cutter {axis}")
        plane_bm.to_mesh(plane_mesh)
        plane_bm.free()

        if self.obj in self.sources:
            plane_obj = self.obj.copy()
        else:
            plane_obj = self.sources[0].copy()
        for col in self.obj.users_collection:
            if col not in plane_obj.users_collection:
                col.objects.link(plane_obj)

        plane_obj.name = f"Cutter {axis}"
        plane_obj.data = plane_mesh
        plane_obj.modifiers.clear()
        plane_obj.select_set(False)

        cycles.hide_preview(context, plane_obj)
        plane_obj.hops.status = 'BOOLSHAPE'
        plane_obj.display_type = 'WIRE'
        plane_obj.hide_render = True

        array = plane_obj.modifiers.new("Array", 'ARRAY')
        array.use_relative_offset = False
        array.use_constant_offset = True
        array.fit_type = 'FIXED_COUNT'
        array.count = self.count

        displace = plane_obj.modifiers.new("Displace", 'DISPLACE')
        displace.direction = axis
        displace.mid_level = 0.0

        axis = "XYZ".find(axis)
        distance = self.size[axis] / (self.count + 1)
        array.constant_offset_displace[axis] = distance
        displace.strength = distance

        if self.big_box:
            object.clear_transforms(plane_obj)

        return plane_obj


    def remove_plane(self, context, obj):
        mesh = obj.data
        bpy.data.objects.remove(obj)
        bpy.data.meshes.remove(mesh)


    def knife(self, context, axis):
        bpy.ops.object.mode_set(mode='OBJECT')

        self.plane_x.select_set(axis == 'X')
        self.plane_y.select_set(axis == 'Y')
        self.plane_z.select_set(axis == 'Z')

        if self.use_knife_project:
            self.knife_project(context, axis)
        else:
            self.knife_intersect(context, axis)

        bpy.ops.object.mode_set(mode=self.mode)


    def knife_project(self, context, axis):
        perspective = copy.copy(context.region_data.view_perspective)
        camera_zoom = copy.copy(context.region_data.view_camera_zoom)
        distance = copy.copy(context.region_data.view_distance)
        location = copy.copy(context.region_data.view_location)
        rotation = copy.copy(context.region_data.view_rotation)

        view = {'X': 'FRONT', 'Y': 'TOP', 'Z': 'RIGHT'}[axis]
        if axis == 'X':
            plane = self.plane_x
        elif axis == 'Y':
            plane = self.plane_y
        elif axis == 'Z':
            plane = self.plane_z
        set_active(plane)
        bpy.ops.view3d.view_axis(type=view, align_active=True)
        set_active(self.dice_target)
        context.region_data.view_perspective = 'ORTHO'
        context.region_data.update()

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.knife_project(cut_through=True)
        bpy.ops.object.mode_set(mode='OBJECT')

        context.region_data.view_perspective = perspective
        context.region_data.view_camera_zoom = camera_zoom
        context.region_data.view_distance = distance
        context.region_data.view_location = location
        context.region_data.view_rotation = rotation
        context.region_data.update()

        if perspective == 'ORTHO':
            axis = [int(math.degrees(a)) for a in mathutils.Quaternion(rotation).to_euler()]

            if axis == [90, 0, 90]:
                bpy.ops.view3d.view_axis(type='RIGHT')
            elif axis == [90, 0, 0]:
                bpy.ops.view3d.view_axis(type='FRONT')
            elif axis == [0, 0, 0]:
                bpy.ops.view3d.view_axis(type='TOP')
            elif axis == [90, 0, -90]:
                bpy.ops.view3d.view_axis(type='LEFT')
            elif axis == [90, 0, 180]:
                bpy.ops.view3d.view_axis(type='BACK')
            elif axis == [180, 0, 0]:
                bpy.ops.view3d.view_axis(type='BOTTOM')


    def knife_intersect(self, context, axis):
        bpy.ops.object.mode_set(mode='OBJECT')
        operator.knife(context, knife_project=False)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')


    def draw_master(self, context):

        # Start
        self.master.setup()

        ########################
        #   Fast UI
        ########################

        if self.master.should_build_fast_ui():

            win_list = []
            help_list = []
            mods_list = []
            active_mod = ""

            # Main
            if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1:
                axes = ", ".join(a for i,a in enumerate("XYZ") if self.axes[i])
                win_list.append(axes)
                win_list.append(str(self.count))
                if self.to_twist is not 'None':
                    win_list.append('To_Twist')
                if len(context.active_object.modifiers[:]) >= 1:
                    win_list.append(f'[S]mart Apply')
                #win_list.append(f": {'Knife Project' if self.use_knife_project else 'Mesh Intersect'}")
            else:
                # Main
                axes = ", ".join(a for i,a in enumerate("XYZ") if self.axes[i])
                win_list.append(axes)
                win_list.append(str(self.count))
                win_list.append(f"Method: {'Knife Project' if self.use_knife_project else 'Mesh Intersect'}")
                if self.to_twist is not 'None':
                    win_list.append(f'To_Twist {self.to_twist}')
                if len(context.active_object.modifiers[:]) >= 1:
                    win_list.append(f'S -  Smart Apply')

            # Help
            help_list.append(["Shift + LMB / Space", "Create cutters but don't perform cut"])
            help_list.append(["X / Y / Z",           "Toggle dicing per axis"])
            help_list.append(["1 / 2 / 3 / 4",       "Set segments to 7 / 15 / 23 / 31"])
            help_list.append(["Shift + S",           "Adjust Segments"])
            help_list.append(["T",                   "Twist / Smart Apply"])
            help_list.append(["S",                   "Smart Apply"])
            help_list.append(["W",                   "Show Wire"])
            help_list.append(["Q",                   "Toggle Knife Project / Mesh Intersect"])
            help_list.append(["M",                   "Toggle mods list."])
            help_list.append(["H",                   "Toggle help"])
            help_list.append(["~",                   "Toggle viewport displays."])
            help_list.append(["O",             "Toggle viewport rendering"])

            # Mods
            mods_list = get_mods_list(mods=bpy.context.active_object.modifiers)

            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="Dice", mods_list=mods_list, active_mod_name=active_mod)

        # Finished
        self.master.finished()


    ####################################################
    #   CURSOR WARP
    ####################################################

    def safe_draw_shader(self, context):
        method_handler(self.draw_shader,
            arguments = (context,),
            identifier = 'UI Framework',
            exit_method = self.remove_shader)


    def remove_shader(self):
        '''Remove shader handle.'''

        if self.draw_handle:
            self.draw_handle = bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle, "WINDOW")


    def draw_shader(self, context):
        '''Draw shader handle.'''

        draw_modal_frame(context)