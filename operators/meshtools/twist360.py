import bpy
import bmesh
import math
import mathutils
from ... preferences import get_preferences
from ... utility import modifier
from ... utility.base_modal_controls import Base_Modal_Controls
from ... ui_framework.master import Master
from ... ui_framework.utils.mods_list import get_mods_list

# Cursor Warp imports
from ... utils.toggle_view3d_panels import collapse_3D_view_panels
from ... utils.modal_frame_drawing import draw_modal_frame
from ... utils.cursor_warp import mouse_warp
from ... addon.utility import method_handler


class HOPS_OT_MOD_Twist360(bpy.types.Operator):
    bl_idname = "array.twist"
    bl_label = "Array Twist"
    bl_options = {'REGISTER', 'UNDO', 'GRAB_CURSOR'}
    bl_description = """Adds an array modifier and deforms the mesh 360 degrees
LMB + Shift - Don't merge segments

Press H for help"""

    axis: bpy.props.EnumProperty(
        name="Axis",
        description="What axis to twist around on",
        items=[
            ('X', "X", "Twist around the X axis"),
            ('Y', "Y", "Twist around the Y axis"),
            ('Z', "Z", "Twist around the Z axis")],
        default='Z')

    count: bpy.props.IntProperty(
        name="Count",
        description="How many segments to make",
        min=1,
        soft_max=100,
        default=8)

    displace: bpy.props.FloatProperty(
        name="Displace",
        description="How far in or out to displace",
        default=-1)

    angle: bpy.props.FloatProperty(
        name="Angle",
        description="How many degrees to twist",
        default=360)

    rotation: bpy.props.FloatProperty(
        name="Rotation",
        description="How many degrees to rotate the segment",
        default=0)

    merge: bpy.props.BoolProperty(
        name="Merge",
        description="Merge vertices of adjacent segments",
        default=True)

    duplicating: bpy.props.BoolProperty(
        name="Duplicating",
        description="Whether this operator is called from Shift + D by another instance of itself",
        default=False)

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and obj.mode == 'OBJECT'

    def draw(self, context):
        self.layout.label(text=f"Axis: {self.axis}")
        self.layout.label(text=f"Segments: {self.count}")
        self.layout.label(text=f"Displace: {self.displace:.3f}")
        self.layout.label(text=f"Angle: {self.angle:.0f}")
        self.layout.label(text=f"Rotation: {self.rotation:.0f}")
        self.layout.label(text=f"Merge: {'Enabled' if self.merge else 'Disabled'}")

    # Without execute, draw doesn't work
    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):

        self.modal_scale = get_preferences().ui.Hops_modal_scale
        self.obj = context.active_object
        self.merge = not event.shift
        self.adjusting = 'DISPLACE'
        self.displace_mod_one = None
        self.array_mod = None
        self.deform_mod = None
        self.displace_mod_two = None
        self.weld_mod = None

        for a, b, c, d, e in zip(self.obj.modifiers[:-3], self.obj.modifiers[1:-2], self.obj.modifiers[2:-1], self.obj.modifiers[3:], self.obj.modifiers[4:] + [None]):
            if a.type == 'DISPLACE' and b.type == 'ARRAY' and c.type == 'SIMPLE_DEFORM' and d.type == 'DISPLACE':
                self.displace_mod_one = a
                self.array_mod = b
                self.deform_mod = c
                self.displace_mod_two = d

                if e and e.type == 'WELD':
                    self.weld_mod = e

                break

        self.displace_new_one = False
        self.array_new = False
        self.deform_new = False
        self.displace_new_two = False
        self.weld_new = False

        if not self.displace_mod_one:
            self.displace_mod_one = self.obj.modifiers.new("Displace One", 'DISPLACE')
            self.displace_mod_one.show_expanded = False

            self.displace_mod_one.show_in_editmode = not get_preferences().property.Hops_twist_radial_sort
            self.displace_mod_one.show_render = get_preferences().property.Hops_twist_radial_sort

            self.displace_mod_one.mid_level = 0.0
            self.displace_mod_one.direction = 'X' if self.axis == 'Y' else 'Y'
            self.displace_mod_one.strength = self.displace
            self.displace_new_one = True

        if not self.array_mod:
            self.array_mod = self.obj.modifiers.new("Array", 'ARRAY')
            self.array_mod.show_expanded = False

            self.array_mod.show_in_editmode = not get_preferences().property.Hops_twist_radial_sort
            self.array_mod.show_render = get_preferences().property.Hops_twist_radial_sort

            self.array_mod.count = self.count
            self.array_new = True

        if not self.deform_mod:
            self.deform_mod = self.obj.modifiers.new("Simple Deform", 'SIMPLE_DEFORM')
            self.deform_mod.show_expanded = False

            self.deform_mod.show_in_editmode = not get_preferences().property.Hops_twist_radial_sort
            self.deform_mod.show_render = get_preferences().property.Hops_twist_radial_sort

            self.deform_mod.angle = math.radians(self.angle)
            self.deform_mod.deform_method = 'BEND'
            self.deform_mod.deform_axis = self.axis
            self.deform_new = True

        if not self.displace_mod_two:
            self.displace_mod_two = self.obj.modifiers.new("Displace Two", 'DISPLACE')
            self.displace_mod_two.show_expanded = False

            self.displace_mod_two.show_in_editmode = not get_preferences().property.Hops_twist_radial_sort
            self.displace_mod_two.show_render = get_preferences().property.Hops_twist_radial_sort

            self.displace_mod_two.mid_level = 0.0
            self.displace_mod_two.direction = 'X' if self.axis == 'Y' else 'Y'
            self.displace_mod_two.strength = -1.0
            self.displace_new_two = True

        if not self.weld_mod:
            try:
                self.weld_mod = self.obj.modifiers.new("Weld", 'WELD')
                self.weld_mod.show_expanded = False

                self.weld_mod.show_in_editmode = not get_preferences().property.Hops_twist_radial_sort
                self.weld_mod.show_render = get_preferences().property.Hops_twist_radial_sort

                self.weld_new = True

            except:
                self.report({'INFO'}, "Unable to add Weld modifier")

        self.displace_settings_one = {}
        self.displace_settings_one["direction"] = self.displace_mod_one.direction
        self.displace_settings_one["strength"] = self.displace_mod_one.strength

        self.array_settings = {}
        self.array_settings["use_constant_offset"] = self.array_mod.use_constant_offset
        self.array_settings["use_relative_offset"] = self.array_mod.use_relative_offset
        self.array_settings["use_object_offset"] = self.array_mod.use_object_offset
        self.array_settings["displace_x"] = self.array_mod.relative_offset_displace[0]
        self.array_settings["displace_y"] = self.array_mod.relative_offset_displace[1]
        self.array_settings["displace_z"] = self.array_mod.relative_offset_displace[2]
        self.array_settings["use_merge_vertices"] = self.array_mod.use_merge_vertices
        self.array_settings["fit_type"] = self.array_mod.fit_type
        self.array_settings["count"] = self.array_mod.count

        self.deform_settings = {}
        self.deform_settings["deform_method"] = self.deform_mod.deform_method
        self.deform_settings["deform_axis"] = self.deform_mod.deform_axis
        self.deform_settings["angle"] = self.deform_mod.angle

        self.displace_settings_two = {}
        self.displace_settings_two["direction"] = self.displace_mod_two.direction
        self.displace_settings_two["strength"] = self.displace_mod_two.strength

        if not self.array_new:
            self.merge = self.array_mod.use_merge_vertices

        self.array_mod.use_constant_offset = False
        self.array_mod.use_relative_offset = True
        self.array_mod.use_object_offset = False
        self.array_mod.relative_offset_displace = (1.0, 0.0, 0.0) if self.deform_mod.deform_axis == 'Z' else (0.0, 0.0, 1.0)
        self.array_mod.use_merge_vertices = self.merge

        if self.weld_mod:
            self.weld_settings = {}
            self.weld_settings["show_viewport"] = self.weld_mod.show_viewport
            self.weld_mod.show_viewport = self.merge

        self.axis = self.deform_mod.deform_axis
        self.count = self.count_buffer = self.array_mod.count
        self.displace = self.displace_buffer = self.displace_mod_one.strength
        self.angle = self.angle_buffer = math.degrees(self.deform_mod.angle)
        self.rotation = 0

        if self.duplicating:
            self.rotate(self.axis, 180)
            self.duplicating = False

        self.center(context)

        # Base Systems
        self.master = Master(context=context)
        self.master.only_use_fast_ui = True
        self.base_controls = Base_Modal_Controls(context, event)
        self.original_tool_shelf, self.original_n_panel = collapse_3D_view_panels()
        self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.safe_draw_shader, (context,), 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):

        # Base Systems
        self.master.receive_event(event=event)
        self.base_controls.update(context, event)
        mouse_warp(context, event)

        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        if event.type == 'Z' and (event.shift or event.alt):
            return {'PASS_THROUGH'}

        elif self.base_controls.confirm:
            self.confirm(context)
            self.report({'INFO'}, "Finished")
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            return {'FINISHED'}

        elif self.base_controls.cancel:
            self.cancel(context)
            self.report({'INFO'}, "Cancelled")
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            return {'CANCELLED'}

        elif event.shift and event.type == 'D' and event.value == 'RELEASE':
            # self.remove_draw_handler(context)
            self.confirm(context)
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            bpy.ops.object.duplicate(mode='INIT')
            bpy.ops.hops.display_notification(info="Duplicated")
            self.report({'INFO'}, "Duplicating")
            bpy.ops.array.twist('INVOKE_DEFAULT', duplicating=True)
            return {'FINISHED'}

        elif self.base_controls.scroll:
            self.count_buffer += self.base_controls.scroll

            self.count_buffer = max(self.count_buffer, 1)
            self.count = round(self.count_buffer)
            self.array_mod.count = self.count
            self.center(context)
            self.report({'INFO'}, f"Segments: {self.array_mod.count}")

        elif event.type == 'MOUSEMOVE' and self.adjusting != 'NONE':
            if self.adjusting == 'ANGLE':

                self.angle_buffer += self.base_controls.mouse * 10
                self.angle_buffer = min(max(self.angle_buffer, 0), 360)
                self.angle = round(15 * round(self.angle_buffer / 15, 0) if event.ctrl else self.angle_buffer)
                self.deform_mod.angle = math.radians(self.angle)
                self.center(context)

            elif self.adjusting == 'DISPLACE':

                self.displace_buffer -= self.base_controls.mouse * 2.5
                digits = 2 if event.ctrl and event.shift else 1 if event.ctrl else 3
                self.displace = round(self.displace_buffer, digits)
                self.displace_mod_one.strength = self.displace
                self.center(context)

            elif self.adjusting == 'SEGMENTS':

                self.count_buffer += self.base_controls.mouse * 10
                self.count_buffer = max(self.count_buffer, 1)
                self.count = round(self.count_buffer)
                self.array_mod.count = self.count
                self.center(context)

        elif event.type in {'S', 'D', 'A'} and event.value == 'PRESS':
            if event.type == 'S':
                self.adjusting = 'NONE' if self.adjusting == 'SEGMENTS' else 'SEGMENTS'
            elif event.type == 'D' and not event.shift:
                self.adjusting = 'NONE' if self.adjusting == 'DISPLACE' else 'DISPLACE'
            elif event.type == 'A':
                self.adjusting = 'NONE' if self.adjusting == 'ANGLE' else 'ANGLE'

            if self.adjusting != 'NONE':
                self.report({'INFO'}, f"Adjusting {str(self.adjusting).capitalize()}")
            else:
                self.report({'INFO'}, "Stopped Adjusting")

        elif event.type == 'X' and event.value == 'PRESS':
            self.unrotate(context)
            self.axis = "YZX"["XYZ".find(self.axis)]
            self.displace_mod_one.direction = 'X' if self.axis == 'Y' else 'Y'
            self.array_mod.relative_offset_displace = (1.0, 0.0, 0.0) if self.axis == 'Z' else (0.0, 0.0, 1.0)
            self.deform_mod.deform_axis = self.axis
            self.displace_mod_two.direction = 'X' if self.axis == 'Y' else 'Y'
            self.center(context)
            self.report({'INFO'}, f"Deform Axis: {self.axis}")

        elif event.type in {'R', 'F'} and event.value == 'PRESS':
            angle = 90 if event.type == 'R' else 180
            self.rotation = (self.rotation + angle) % 360
            self.rotate(self.axis, angle)
            self.center(context)
            self.report({'INFO'}, f"Rotation: {self.rotation:.0f}")

        elif event.type == 'M' and event.value == 'PRESS' and event.shift == True:
            self.merge = not self.merge
            self.array_mod.use_merge_vertices = self.merge
            if self.weld_mod:
                self.weld_mod.show_viewport = self.merge
            self.report({'INFO'}, f"Merge: {'Enabled' if self.merge else 'Disabled'}")

        self.draw_master(context=context)

        context.area.tag_redraw()

        return {"RUNNING_MODAL"}

    def rotate(self, axis, angle):
        bm = bmesh.new()
        bm.from_mesh(self.obj.data)

        matrix = mathutils.Matrix.Rotation(math.radians(angle), 4, axis)
        bmesh.ops.rotate(bm, cent=self.obj.location, matrix=matrix, verts=bm.verts, space=self.obj.matrix_world)

        bm.to_mesh(self.obj.data)
        bm.free()

    def unrotate(self, context):
        self.rotate(self.axis, -self.rotation)
        self.rotation = 0

    def center(self, context):
        temp = bpy.data.objects.new("Bounding Box", self.obj.data)
        bb = temp.bound_box[:]
        bpy.data.objects.remove(temp)

        right = left = bb[7][0]
        front = back = bb[7][1]
        top = bottom = bb[7][2]

        for i in range(7):
            x = bb[i][0]
            if x > right:
                right = x
            if x < left:
                left = x

            y = bb[i][1]
            if y > front:
                front = y
            if y < back:
                back = y

            z = bb[i][2]
            if z > top:
                top = z
            if z < bottom:
                bottom = z

        middle_x = (right + left) * 0.5
        middle_y = (front + back) * 0.5
        middle_z = (top + bottom) * 0.5

        verts = [v for v in bb]
        verts.append((right, middle_y, middle_z))
        verts.append((left, middle_y, middle_z))
        verts.append((middle_x, front, middle_z))
        verts.append((middle_x, back, middle_z))
        verts.append((middle_x, middle_y, top))
        verts.append((middle_x, middle_y, bottom))

        bm = bmesh.new()
        bm.from_mesh(self.obj.data)
        verts = [bm.verts.new(v) for v in verts]
        bm.to_mesh(self.obj.data)

        self.displace_mod_two.strength = 0.0
        context.view_layer.update()

        bb = self.obj.bound_box
        axis = 0 if self.axis == 'Y' else 1
        pos = neg = bb[7][axis]

        for i in range(7):
            val = bb[i][axis]
            if val > pos:
                pos = val
            if val < neg:
                neg = val

        offset = -0.5 * (pos + neg)
        self.displace_mod_two.strength = offset

        verts = [bm.verts.remove(v) for v in verts]
        bm.to_mesh(self.obj.data)
        bm.free()

    def confirm(self, context):
        context.space_data.overlay.show_overlays = True
        modifier.sort(self.obj, sort_types=['WEIGHTED_NORMAL'])

        if get_preferences().property.workflow == 'DESTRUCTIVE':
            for mod in [self.displace_mod_one, self.array_mod, self.deform_mod, self.displace_mod_two, self.weld_mod]:
                if mod:
                    modifier.apply(self.obj, mod=mod)

    def cancel(self, context):
        context.space_data.overlay.show_overlays = True
        self.unrotate(context)

        if self.displace_new_one:
            self.obj.modifiers.remove(self.displace_mod_one)
        else:
            self.displace_mod_one.direction = self.displace_settings_one["direction"]
            self.displace_mod_one.strength = self.displace_settings_one["strength"]

        if self.array_new:
            self.obj.modifiers.remove(self.array_mod)
        else:
            self.array_mod.use_constant_offset = self.array_settings["use_constant_offset"]
            self.array_mod.use_relative_offset = self.array_settings["use_relative_offset"]
            self.array_mod.use_object_offset = self.array_settings["use_object_offset"]
            self.array_mod.relative_offset_displace[0] = self.array_settings["displace_x"]
            self.array_mod.relative_offset_displace[1] = self.array_settings["displace_y"]
            self.array_mod.relative_offset_displace[2] = self.array_settings["displace_z"]
            self.array_mod.use_merge_vertices = self.array_settings["use_merge_vertices"]
            self.array_mod.fit_type = self.array_settings["fit_type"]
            self.array_mod.count = self.array_settings["count"]

        if self.deform_new:
            self.obj.modifiers.remove(self.deform_mod)
        else:
            self.deform_mod.deform_method = self.deform_settings["deform_method"]
            self.deform_mod.deform_axis = self.deform_settings["deform_axis"]
            self.deform_mod.angle = self.deform_settings["angle"]

        if self.displace_new_two:
            self.obj.modifiers.remove(self.displace_mod_two)
        else:
            self.displace_mod_two.direction = self.displace_settings_two["direction"]
            self.displace_mod_two.strength = self.displace_settings_two["strength"]

        if self.weld_new:
            self.obj.modifiers.remove(self.weld_mod)
        elif self.weld_mod:
            self.weld_mod.show_viewport = self.weld_settings["show_viewport"]

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
            win_list.append("Twist 360")
            win_list.append(f"{self.axis}")
            win_list.append(f"{self.count}")
            win_list.append(f"{self.displace:.3f}")
            win_list.append(f"{self.angle:.0f}")

            # Help
            help_list.append(["X",         "Increment Axis"])
            help_list.append(["Scroll",    "Increment Segments"])
            help_list.append(["S",         "Adjust Segments"])
            help_list.append(["D",         "Adjust Displacement"])
            help_list.append(["A",         "Adjust Angle"])
            help_list.append(["R",         "Rotate 90 degrees"])
            help_list.append(["F",         "Rotate 180 degrees"])
            help_list.append(["Shift + D", "Duplicate"])
            help_list.append(["M + Shift", "Toggle Merge"])
            help_list.append(["H",         "Toggle help."])
            help_list.append(["M",         "Toggle mods list."])
            help_list.append(["~",         "Toggle viewport displays."])
            help_list.append(["O",         "Toggle viewport rendering"])

            # Mods
            if self.array_mod != None:
                active_mod = self.array_mod.name

            mods_list = get_mods_list(mods=bpy.context.active_object.modifiers)

            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="ATwist360", mods_list=mods_list, active_mod_name=active_mod)

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