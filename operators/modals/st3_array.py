import bpy, mathutils, math, gpu
from math import cos, sin
from enum import Enum
from mathutils import Vector, Matrix
from bgl import *
from gpu_extras.batch import batch_for_shader
from ... preferences import get_preferences
from ... utility import modifier
from ... utility.base_modal_controls import Base_Modal_Controls
from ... ui_framework.master import Master
from ... ui_framework.utils.mods_list import get_mods_list
from ... utils.toggle_view3d_panels import collapse_3D_view_panels
from ... utils.modal_frame_drawing import draw_modal_frame
from ... utils.cursor_warp import mouse_warp
from ... utils.modifiers import get_mod_copy, transfer_mod_data
from ... utils.space_3d import get_3D_point_from_mouse, get_3D_raycast_from_mouse
from ... addon.utility import method_handler


'''
Class -> Obj_Data
    Used to store each mesh object.
Class -> Mod_Data
    Used to store a list of all the array modifiers.
    Stored inside of Obj_Data

--- Running structure ---
    For each mesh object:
        -> Obj_Data
            Contains a list of:
                -> Mod_Data
'''


class Axis(Enum):

    X = 1
    Y = 2
    Z = 3


class Edit_Space(Enum):

    View_2D = 1
    View_3D = 2


class Mod_Data:
    '''Represented as m in loops.'''

    def __init__(self):
        self.array_mod = None
        self.array_mod_copy = None
        self.array_was_created = False
        self.logically_deleted = False


class Obj_Data:
    '''Represented as o in loops.'''

    def __init__(self):

        self.mesh_obj = None
        self.mesh_obj_dims = (0,0,0)
        self.mod_data = []
        self.active_mod_index = 0


class HOPS_OT_ST3_Array(bpy.types.Operator):
    bl_idname = "hops.st3_array"
    bl_label = "Adjust Array V2"
    bl_description = """Array V2 

    Adds an array on the mesh. 
    Supports multiple modifiers.
    V during modal for 2d / 3d mode.

    Press H for help
    """
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)


    def invoke(self, context, event):

        # UI Data
        self.ui_offset_data = (0,0,0)  # The array offset values
        self.ui_object_data = None     # Get an object to read data from
        self.ui_count_data = 0         # Get the array count
        self.ui_mods_list = []         # The objects modifiers
        self.ui_active_mod_name = ""   # The actuve mod name
        self.ui_drawing_radius = 0     # The radius for the circle gizmo
        self.ui_show_guides = False    # Show graphical guides
        self.ui_defualt_object_dims = (0,0,0) # The defualt objects dimensions before array modifiers
        self.ui_offset_type = "Constant"      # Gets set in ui setup function
        self.ui_3D_circle_loc = (0,0,0)       # The intersection poing of the mouse

        # Controler Vars
        self.intersection_point = Vector((0,0,0)) # Where the mouse is in 3D space : Used to draw the circle gizmo
        self.mouse_x_offset_2D = 0                # Tracked for 2D offseting
        self.mouse_accumulation = 0               # This is used as a sudo timer for 2D offset snaps
        self.axis = Axis.X                        # The current axis to offset with
        self.edit_space = Edit_Space.View_2D      # The offset space
        self.freeze_controls = False              # Used to freeze the mouse
        self.use_snaps = False                    # Used to offset by object dimensions

        # Setup
        self.obj_data = self.setup_objects(context)
        self.set_initial_axis()

        # Base Systems
        self.master = Master(context=context)
        self.master.only_use_fast_ui = True
        self.base_controls = Base_Modal_Controls(context, event)
        self.original_tool_shelf, self.original_n_panel = collapse_3D_view_panels()
        self.draw_handle_2D = bpy.types.SpaceView3D.draw_handler_add(self.safe_draw_2D, (context,), 'WINDOW', 'POST_PIXEL')
        self.draw_handle_3D = bpy.types.SpaceView3D.draw_handler_add(self.safe_draw_3D, (context,), 'WINDOW', 'POST_VIEW')

        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}


    def modal(self, context, event):

        # Base Systems
        self.master.receive_event(event=event)
        self.base_controls.update(context, event)

        if self.edit_space == Edit_Space.View_2D:
            mouse_warp(context, event)

        self.mouse_x_offset_2D = self.base_controls.mouse

        #######################
        #   Base Controls
        #######################

        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        elif self.base_controls.cancel:
            self.remove_shaders()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            self.revert_objects()
            return {'CANCELLED'}

        elif self.base_controls.confirm:
            self.store_axis_on_object()
            self.remove_shaders()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            self.modal_finished_cleanup()
            return {'FINISHED'}

        #######################
        #   Modal Controls
        #######################

        # Displace 2D
        if self.edit_space == Edit_Space.View_2D:
            if event.type == "MOUSEMOVE":
                if self.freeze_controls == False:
                    if event.ctrl == True:
                        self.adjust_2D(accelerated=True)
                    else:
                        self.adjust_2D(accelerated=False)

        # Displace 3D
        elif self.edit_space == Edit_Space.View_3D:
            if self.freeze_controls == False:
                self.adjust_3D(context=context, event=event)

        # Toggle 2D / 3D manipulation
        if event.type == 'V' and event.value == "PRESS":
            if self.edit_space == Edit_Space.View_2D:
                self.edit_space = Edit_Space.View_3D
            elif self.edit_space == Edit_Space.View_3D:
                self.edit_space = Edit_Space.View_2D

        # Cycle the current array : W
        if event.type == 'W' and event.value == "PRESS":
            self.goto_next_array()

        # Cycle the current array : Ctrl Scroll
        if self.base_controls.scroll:
            if event.ctrl == True:
                self.goto_next_array()

        # Toggle perspective
        elif event.type == 'P' or event.type == 'NUMPAD_5':
            if event.value == 'PRESS':
                bpy.ops.view3d.view_persportho()

        # Toggle freeze controls
        elif event.type in {'F', 'TAB'} and event.value == "PRESS":
            self.freeze_controls = not self.freeze_controls

        # Toggle graphics guides
        elif event.type == 'G' and event.value == "PRESS":
            self.ui_show_guides = not self.ui_show_guides

        # Toggle Axis : If CTRL -> Clear the axis
        elif event.type == 'X' and event.value == "PRESS":
            if event.ctrl == True:
                self.toggle_axis(clear_axis_on_change=False)
                if get_preferences().ui.Hops_extra_info:
                    bpy.ops.hops.display_notification(info=f"Axis Switched To: {self.axis.name}")
            else:
                self.toggle_axis(clear_axis_on_change=True)
                if get_preferences().ui.Hops_extra_info:
                    bpy.ops.hops.display_notification(info=f"Axis Reset To: {self.axis.name}")
                
        # Toggle snap mode
        elif event.type == 'S' and event.value == "PRESS":
            self.mouse_accumulation = 0
            self.use_snaps = not self.use_snaps

        # Add Array
        elif event.type == 'A' and event.value == "PRESS" and event.alt == False:
            self.add_an_array()
            if get_preferences().ui.Hops_extra_info:
                bpy.ops.hops.display_notification(info=f"Array Added")

        # Remove Array
        elif event.type == 'A' and event.value == "PRESS" and event.alt == True:
            self.remove_an_array()
            if get_preferences().ui.Hops_extra_info:
                bpy.ops.hops.display_notification(info=f"Array Removed")

        # Toggle Relative / Constant
        elif event.type == 'R' and event.value == "PRESS":
            self.toggle_relative_constant()

        # Set every thing to one
        elif event.type == 'ONE' or event.type == 'NUMPAD_1' and event.value == "PRESS":
            if event.shift == True:
                self.set_arrays_to_one(negative=True)
            else:
                self.set_arrays_to_one(negative=False)
            if get_preferences().ui.Hops_extra_info:
                if self.edit_space == Edit_Space.View_3D:
                    bpy.ops.hops.display_notification(info=f"Not Possible In 3D")
                else:
                    bpy.ops.hops.display_notification(info=f"Set to 1")

        # Increment / Decrement
        if self.base_controls.scroll:
            if self.freeze_controls == False:
                if event.ctrl == False:
                    if event.shift == False:
                        self.increment_decrement_count(count=self.base_controls.scroll)

        # Move mod up or down
        if self.base_controls.scroll:
            if event.shift == True:
                if self.base_controls.scroll > 0:
                    self.move_mod(context, up=True)
                if self.base_controls.scroll < 0:
                    self.move_mod(context, up=False)

        # This is to smooth the mouse snapping motion
        if self.use_snaps:
            if self.edit_space == Edit_Space.View_2D:
                self.mouse_accumulation += self.base_controls.mouse

        # Navigation for frozen state
        if self.freeze_controls == True:
            if event.ctrl == False:
                if event.shift == False:
                    if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
                        return {'PASS_THROUGH'}

        self.draw_master(context=context)
        context.area.tag_redraw()
        return {"RUNNING_MODAL"}


    def draw_master(self, context):

        self.setup_ui_data()

        # Start
        self.master.setup()

        #---  Fast UI ---#
        if self.master.should_build_fast_ui():

            win_list = []
            help_list = []
            mods_list = []
            active_mod = ""

            # Main
            if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1: #Micro UI
                win_list.append(str(int(self.ui_count_data)))
                if self.axis.name == 'X':
                    win_list.append("X : {:.3f}".format(self.ui_offset_data[0]))
                elif self.axis.name == 'Y':
                    win_list.append("Y : {:.3f}".format(self.ui_offset_data[1]))
                elif self.axis.name == 'Z':
                    win_list.append("Z : {:.3f}".format(self.ui_offset_data[2]))
                win_list.append(self.edit_space.name[-2:])
                if self.ui_offset_type == "Relative":
                    win_list.append("R")
                elif self.ui_offset_type == "Constant":
                    win_list.append("C")
                if self.freeze_controls:
                    win_list.append("[F] Unpause")

            else:
                win_list.append(str(int(self.ui_count_data)))
                win_list.append(self.axis.name)
                win_list.append("  X: {:.3f}  Y: {:.3f}  Z: {:.3f} ".format(self.ui_offset_data[0], self.ui_offset_data[1], self.ui_offset_data[2]))
                win_list.append(self.edit_space.name[-2:])
                win_list.append(self.ui_offset_type)
                if self.freeze_controls:
                    win_list.append("[F] Unpause")
                else:
                    win_list.append("[F] Pause")

            # Help
            help_list.append(["M",              "Toggle mods list"])
            help_list.append(["H",              "Toggle help"])
            help_list.append(["~",              "Toggle UI Display Type"])
            help_list.append(["O",              "Toggle viewport rendering"])
            help_list.append(["Scroll",         "Adjust segments."])
            help_list.append(["S",              "Toggle Snap Mode"])
            help_list.append(["P / 5",          "Toggle Perspective"])
            help_list.append(["W",              "Goto Next Array"])
            help_list.append(["Ctrl + Scroll",  "Goto Next Array"])
            help_list.append(["Shift + Scroll", "Move Modifier Up / Down"])
            help_list.append(["R",              "Toggle Relative / Constant"])
            help_list.append(["1 / Shift",      "Set to 1 or -1 on current Axis"])
            help_list.append(["G",              "Toggle Graphics"])
            if self.freeze_controls:
                help_list.append(["F / TAB", "Unpause Modal / Freeze Rotation"])
            else:
                help_list.append(["F / TAB", "Pause Modal / Free Rotation"])
            help_list.append(["Alt + A",        "Remove Active Array"])
            help_list.append(["A",              f"Add New Array"])
            help_list.append(["Ctrl + X",       "Toggle Axis"])
            help_list.append(["X",              "Toggle Axis & Clear Current"])
            help_list.append(["V",              f"Toggle {(str(self.edit_space)[-2:])} Mode"])

            # Mods
            mods_list = get_mods_list(mods=self.ui_mods_list)

            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="Array", mods_list=mods_list, active_mod_name=self.ui_active_mod_name)

        # Finished
        self.master.finished()


    def setup_ui_data(self):
        '''Sets all the data for the UI drawing.'''

        for o in self.obj_data:

            if o.mesh_obj == self.ui_object_data:

                # Set the UI variables
                mod = o.mod_data[o.active_mod_index].array_mod
                self.ui_active_mod_name = mod.name

                if mod.use_relative_offset:
                    self.ui_offset_data = mod.relative_offset_displace
                    self.ui_offset_type = "Relative"
                elif mod.use_constant_offset:
                    self.ui_offset_data = mod.constant_offset_displace
                    self.ui_offset_type = "Constant"

                self.ui_count_data = mod.count

                self.ui_mods_list = []
                for mod in self.ui_object_data.modifiers:
                    if mod.show_viewport == True:
                        self.ui_mods_list.append(mod)
                return

    ####################################################
    #   MODAL FUNCTIONS
    ####################################################

    def setup_objects(self, context):
        '''Capture the array modifier on each object or create the modifier if not found.'''

        # Try to get the active object for UI only
        if context.active_object.type == 'MESH':
            self.ui_object_data = context.active_object
            self.ui_defualt_object_dims = self.get_obj_dims(context, obj=context.active_object)
            self.ui_drawing_radius = self.ui_defualt_object_dims[0] * .5

        finalized_objs = []
        mesh_objects = [o for o in context.selected_objects if o.type == 'MESH']

        for obj in mesh_objects:

            # Set the UI object to the first mesh object if it was not set already
            if self.ui_object_data == None:
                self.ui_object_data = obj
                self.ui_defualt_object_dims = self.get_obj_dims(context, obj=context.active_object)
                self.ui_drawing_radius = self.ui_defualt_object_dims[0] * .5

            # Create the obj container
            obj_data = Obj_Data()
            obj_data.mesh_obj = obj
            obj_data.mesh_obj_dims = self.get_obj_dims(context, obj=obj)

            found_mod = False
            for mod in obj.modifiers:
                if mod.type == 'ARRAY':

                    if mod.show_viewport == True:
                        # Found an array modifier
                        found_mod = True
                        mod.show_expanded = False
                        
                        # Create mod data container
                        mod_data = Mod_Data()
                        mod_data.array_mod = mod
                        mod_data.array_was_created = False
                        mod_data.array_mod_copy = get_mod_copy(mod=mod)
                        if mod_data.array_mod.use_relative_offset:
                            mod_data.array_mod.use_constant_offset = False
                        if mod_data.array_mod.use_constant_offset:
                            mod_data.array_mod.use_relative_offset = False

                        obj_data.mod_data.append(mod_data)
            
            if found_mod == False:
                mod = obj.modifiers.new("Array", 'ARRAY')
                mod.show_expanded = False

                # Create mod data container
                mod_data = Mod_Data()
                mod_data.array_mod = mod
                mod_data.array_mod_copy = get_mod_copy(mod=mod)
                mod_data.array_was_created = True
                mod_data.array_mod.use_relative_offset = False
                mod_data.array_mod.use_constant_offset = True

                obj_data.mod_data.append(mod_data)

            finalized_objs.append(obj_data)

        return finalized_objs


    def set_initial_axis(self):
        '''Sets the first edit axis to the saved object axis.'''

        if self.ui_object_data != None:
            if self.ui_object_data.hops.last_array_axis == 'X':
                self.axis = Axis.X
            elif self.ui_object_data.hops.last_array_axis == 'Y':
                self.axis = Axis.Y
            elif self.ui_object_data.hops.last_array_axis == 'Z':
                self.axis = Axis.Z
            

    def store_axis_on_object(self):
        '''Store the axis on the object.'''

        if self.ui_object_data != None:
            if self.axis == Axis.X:
                self.ui_object_data.hops.last_array_axis = 'X'
            elif self.axis == Axis.Y:
                self.ui_object_data.hops.last_array_axis = 'Y'
            elif self.axis == Axis.Z:
                self.ui_object_data.hops.last_array_axis = 'Z'


    def revert_objects(self):
        '''Revert back all the objects.'''

        # Loop over all the obj data objects
        for o in self.obj_data:
            # Loop over all the mod datas
            for m in o.mod_data:
                if m.array_was_created == True:
                    o.mesh_obj.modifiers.remove(m.array_mod)
                if m.array_was_created == False:
                    transfer_mod_data(active_mod=m.array_mod, copied_mod=m.array_mod_copy)


    def modal_finished_cleanup(self):
        '''Delete all the modifiers that where logically deleted.'''

        for o in self.obj_data:
            for m in o.mod_data:
                if m.logically_deleted == True:
                    o.mesh_obj.modifiers.remove(m.array_mod)


    def get_obj_dims(self, context, obj=None):
        '''Get the object dimensions without and array mods.'''

        original_states = {}

        for mod in obj.modifiers:
            if mod.type == 'ARRAY':
                original_states[mod] = mod.show_viewport
                mod.show_viewport = False

        context.view_layer.update()

        x_scale = abs(obj.scale[0]) if abs(obj.scale[0]) > 0 else 1
        y_scale = abs(obj.scale[1]) if abs(obj.scale[1]) > 0 else 1
        z_scale = abs(obj.scale[2]) if abs(obj.scale[2]) > 0 else 1

        dims = (
            obj.dimensions[0] / x_scale,
            obj.dimensions[1] / y_scale,
            obj.dimensions[2] / z_scale)

        for key, val in original_states.items():
            key.show_viewport = val

        return dims

    #--- ADJUST 2D ---#

    def adjust_2D(self, accelerated=True):
        '''Adjust arrays 2D.'''

        speed_bonus = 10 if accelerated else 5

        for o in self.obj_data:
            mod = o.mod_data[o.active_mod_index].array_mod

            if mod.use_constant_offset == True:
                self.adjust_constant_arrays_2D(o, mod, speed_bonus)
            else:
                self.adjust_relative_arrays_2D(o, mod, speed_bonus)

        # Reset the mouse accumulation for snaps
        if abs(self.mouse_accumulation) > .25:
            self.mouse_accumulation = 0


    def adjust_constant_arrays_2D(self, ob_data, mod, speed_bonus=0):
        '''Adjust arrays based on 2D screen coordinates.'''

        o = ob_data
        offset = self.mouse_x_offset_2D * speed_bonus

        if self.axis == Axis.X:

            if self.use_snaps:
                
                # Limit this operation
                if abs(self.mouse_accumulation) > .25:
                    
                    # 1/2 of the mesh dims
                    snap_factor = abs(o.mesh_obj_dims[0] * .5)

                    # Reverse the offset direction
                    if self.mouse_x_offset_2D > 0:
                        snap_factor = -snap_factor

                    # Clamp the offset to a snapped value
                    vec = mod.constant_offset_displace[0]
                    remainder = abs(vec) % abs(snap_factor) if abs(snap_factor) > 0 else 0

                    if (vec + remainder) % abs(snap_factor) == 0:
                        mod.constant_offset_displace[0] += remainder
                    else:
                        mod.constant_offset_displace[0] -= remainder

                    # Assign the snap factor
                    mod.constant_offset_displace[0] += snap_factor

            else:
                mod.constant_offset_displace[0] -= offset

        elif self.axis == Axis.Y:

            if self.use_snaps:

                # Limit this operation
                if abs(self.mouse_accumulation) > .25:

                    # 1/2 of the mesh dims
                    snap_factor = abs(o.mesh_obj_dims[1] * .5)

                    # Reverse the offset direction
                    if self.mouse_x_offset_2D > 0:
                        snap_factor = -snap_factor

                    # Clamp the offset to a snapped value
                    vec = mod.constant_offset_displace[1]
                    remainder = abs(vec) % abs(snap_factor) if abs(snap_factor) > 0 else 0

                    if (vec + remainder) % abs(snap_factor) == 0:
                        mod.constant_offset_displace[1] += remainder
                    else:
                        mod.constant_offset_displace[1] -= remainder

                    # Assign the snap factor
                    mod.constant_offset_displace[1] += snap_factor
            else:
                mod.constant_offset_displace[1] -= offset

        elif self.axis == Axis.Z:

            if self.use_snaps:

                # Limit this operation
                if abs(self.mouse_accumulation) > .25:

                    # 1/2 of the mesh dims
                    snap_factor = abs(o.mesh_obj_dims[2] * .5)

                    # Reverse the offset direction
                    if self.mouse_x_offset_2D > 0:
                        snap_factor = -snap_factor

                    # Clamp the offset to a snapped value
                    vec = mod.constant_offset_displace[2]
                    remainder = abs(vec) % abs(snap_factor) if abs(snap_factor) > 0 else 0

                    if (vec + remainder) % abs(snap_factor) == 0:
                        mod.constant_offset_displace[2] += remainder
                    else:
                        mod.constant_offset_displace[2] -= remainder

                    # Assign the snap factor
                    mod.constant_offset_displace[2] += snap_factor

            else:
                mod.constant_offset_displace[2] -= offset


    def adjust_relative_arrays_2D(self, ob_data, mod, speed_bonus=0):
        '''Adjust arrays based on 2D screen coordinates.'''

        o = ob_data
        offset = self.mouse_x_offset_2D * speed_bonus
        offset *= .25

        if self.axis == Axis.X:

            if self.use_snaps:

                # Limit this operation
                if abs(self.mouse_accumulation) > .25:
                    if abs(mod.relative_offset_displace[0]) % .25 != 0:
                         mod.relative_offset_displace[0] = round_quarter(mod.relative_offset_displace[0])

                    snap_factor = .25 if self.mouse_x_offset_2D > 0 else -.25
                    mod.relative_offset_displace[0] -= snap_factor

            else:
                mod.relative_offset_displace[0] -= offset

        elif self.axis == Axis.Y:

            if self.use_snaps:

                # Limit this operation
                if abs(self.mouse_accumulation) > .25:
                    if abs(mod.relative_offset_displace[1]) % .25 != 0:
                         mod.relative_offset_displace[1] = round_quarter(mod.relative_offset_displace[1])

                    snap_factor = .25 if self.mouse_x_offset_2D > 0 else -.25
                    mod.relative_offset_displace[1] -= snap_factor

            else:
                mod.relative_offset_displace[1] -= offset

        elif self.axis == Axis.Z:

            if self.use_snaps:

                # Limit this operation
                if abs(self.mouse_accumulation) > .25:
                    if abs(mod.relative_offset_displace[2]) % .25 != 0:
                         mod.relative_offset_displace[2] = round_quarter(mod.relative_offset_displace[2])

                    snap_factor = .25 if self.mouse_x_offset_2D > 0 else -.25
                    mod.relative_offset_displace[2] -= snap_factor

            else:
                mod.relative_offset_displace[2] -= offset

    #--- ADJUST 3D ---#

    def adjust_3D(self, context, event):
        '''Adjust the arrays 3D.'''

        for o in self.obj_data:
            mod = o.mod_data[o.active_mod_index].array_mod
            if mod.use_constant_offset == True:
                self.adjust_constant_arrays_3D(ob_data=o, mod=mod, context=context, event=event)
            else:
                self.adjust_relative_arrays_3D(ob_data=o, mod=mod, context=context, event=event)


    def adjust_constant_arrays_3D(self, ob_data, mod, context, event):
        '''Adjust constant arrays based on 3D mouse coordinates.'''

        mouse_pos = Vector((event.mouse_region_x, event.mouse_region_y))
        o = ob_data
        obj = o.mesh_obj

        normal = (0,0,0)

        if self.axis == Axis.Z:
            normal = Vector((0,1,0)) @ obj.matrix_world.inverted()
        else:
            normal = Vector((0,0,1)) @ obj.matrix_world.inverted()

        self.intersection_point = get_3D_point_from_mouse(mouse_pos, context, obj.matrix_world.to_translation(), normal)
        self.ui_3D_circle_loc = self.intersection_point
        self.intersection_point = obj.matrix_world.inverted() @ self.intersection_point

        if self.axis == Axis.X:

            distance = self.intersection_point[0]
            count = mod.count - 1
            vec = distance / count

            if self.use_snaps:
                x_dim = o.mesh_obj_dims[0]
                vec -= vec % (x_dim * .25) if (x_dim * .25) > 0 else 1

            mod.constant_offset_displace[0] = vec

        elif self.axis == Axis.Y:
            distance = self.intersection_point[1]
            count = mod.count - 1
            vec = distance / count

            if self.use_snaps:
                x_dim = o.mesh_obj_dims[1]
                vec -= vec % (x_dim * .25) if (x_dim * .25) > 0 else 1

            mod.constant_offset_displace[1] = vec

        elif self.axis == Axis.Z:
            distance = self.intersection_point[2]
            count = mod.count - 1
            vec = distance / count

            if self.use_snaps:
                x_dim = o.mesh_obj_dims[2]
                vec -= vec % (x_dim * .25) if (x_dim * .25) > 0 else 1

            mod.constant_offset_displace[2] = vec

        # Put the intersection point back for drawing
        self.intersection_point = obj.matrix_local @ self.intersection_point


    def adjust_relative_arrays_3D(self, ob_data, mod, context, event):
        '''Adjust relative arrays based on 3D mouse coordinates.'''

        mouse_pos = Vector((event.mouse_region_x, event.mouse_region_y))
        o = ob_data
        obj = o.mesh_obj

        normal = (0,0,0)

        if self.axis == Axis.Z:
            normal = Vector((0,1,0)) @ obj.matrix_world.inverted()
        else:
            normal = Vector((0,0,1)) @ obj.matrix_world.inverted()

        self.intersection_point = get_3D_point_from_mouse(mouse_pos, context, obj.matrix_world.to_translation(), normal)
        self.ui_3D_circle_loc = self.intersection_point
        self.intersection_point = obj.matrix_world.inverted() @ self.intersection_point
        self.intersection_point = Vector((
            self.intersection_point[0] * obj.matrix_world.to_scale()[0],
            self.intersection_point[1] * obj.matrix_world.to_scale()[1], 
            self.intersection_point[2] * obj.matrix_world.to_scale()[2]))

        if self.axis == Axis.X:
            offset = self.intersection_point[0] / (o.mesh_obj_dims[0] * obj.scale[0]) if o.mesh_obj_dims[0] > 0 else 1
            offset /= mod.count - 1
            offset = round_quarter(offset) if self.use_snaps else offset
            mod.relative_offset_displace[0] = offset

        elif self.axis == Axis.Y:
            offset = self.intersection_point[1] / (o.mesh_obj_dims[1] * obj.scale[1]) if o.mesh_obj_dims[1] > 0 else 1
            offset /= mod.count - 1
            offset = round_quarter(offset) if self.use_snaps else offset
            mod.relative_offset_displace[1] = offset

        elif self.axis == Axis.Z:
            offset = self.intersection_point[2] / (o.mesh_obj_dims[2] * obj.scale[2]) if o.mesh_obj_dims[2] > 0 else 1
            offset /= mod.count - 1
            offset = round_quarter(offset) if self.use_snaps else offset
            mod.relative_offset_displace[2] = offset

        # Put the intersection point back for drawing
        self.intersection_point = obj.matrix_local @ self.intersection_point


    def toggle_relative_constant(self):
        '''Toggle relative / constant and set the current array.'''

        # Determine what to set the other arrays to based on defualt obj
        use_relative = False
        for o in self.obj_data:
            if o.mesh_obj == self.ui_object_data:
                mod = o.mod_data[0].array_mod
                if mod.use_relative_offset:
                    use_relative = True

        # Set to the inverse of what defualt was using
        for o in self.obj_data:
            mod = o.mod_data[o.active_mod_index].array_mod
            if use_relative:
                mod.use_constant_offset = True
                mod.use_relative_offset = False
            else:
                mod.use_constant_offset = False
                mod.use_relative_offset = True


    def clear_axis(self, axis=Axis.Y):
        '''Clear the offset on the selected axis.'''

        for o in self.obj_data:
            mod = o.mod_data[o.active_mod_index]
            if axis == Axis.X:
                mod.array_mod.constant_offset_displace[0] = 0
                mod.array_mod.relative_offset_displace[0] = 0
            elif axis == Axis.Y:
                mod.array_mod.constant_offset_displace[1] = 0
                mod.array_mod.relative_offset_displace[1] = 0
            elif axis == Axis.Z:
                mod.array_mod.constant_offset_displace[2] = 0
                mod.array_mod.relative_offset_displace[2] = 0


    def increment_decrement_count(self, count=0):
        '''Add or substract the count param from the array mods.'''

        for o in self.obj_data:
            mod = o.mod_data[o.active_mod_index].array_mod
            if mod.count + count >= 2:
                mod.count += count


    def add_an_array(self):
        '''Adds a new array to the data structure.'''

        for o in self.obj_data:

            obj = o.mesh_obj

            mod = obj.modifiers.new("Array", 'ARRAY')
            mod.show_expanded = False

            # Create mod data container
            mod_data = Mod_Data()
            mod_data.array_mod = mod
            mod_data.array_mod_copy = get_mod_copy(mod=mod)
            mod_data.array_was_created = True
            mod_data.array_mod.use_relative_offset = False
            mod_data.array_mod.use_constant_offset = True

            o.mod_data.append(mod_data)
            o.active_mod_index = len(o.mod_data) - 1

        self.toggle_axis()


    def remove_an_array(self):
        '''Remove the active array from all the objects if possible.'''

        for o in self.obj_data:
            if len(o.mod_data) < 1:
                continue

            # Check if there is more than 1 obj that is not logically deleted
            active_count = 0
            for md in o.mod_data:
                if md.array_mod.show_viewport == True:
                    if md.logically_deleted == False:
                        active_count += 1

            # If there are 2 arrays active than active can be logically removed
            if active_count > 1:
                mod = o.mod_data[o.active_mod_index].array_mod
                mod.show_viewport = False
                o.mod_data[o.active_mod_index].logically_deleted = True

            # Will be the new active mod for this object
            new_active_mod = None

            # Get the mods before the active index : Try to get a new mod from list
            mods_data = o.mod_data[ 0 : o.active_mod_index ]
            for md in reversed(mods_data):
                if md.array_mod.show_viewport == True:
                    if md.logically_deleted == False:
                        new_active_mod = md.array_mod

            # If the new mod was found in first part of list : Try to set the new index
            if new_active_mod != None:
                for index, md in enumerate(o.mod_data):
                    if md.array_mod == new_active_mod:
                        o.active_mod_index = index

            # The mod was not found in the first part of the list
            # Go through all the mods and see if one can be used : Skipping over the current index
            for index, md in enumerate(o.mod_data):
                if index == o.active_mod_index:
                    continue
                if md.array_mod.show_viewport == True:
                    if md.logically_deleted == False:
                        o.active_mod_index = index


    def toggle_axis(self, clear_axis_on_change=False):
        '''Toggle the current axis, also setting some other values.'''

        self.mouse_accumulation = 0

        if self.axis == Axis.X:
            self.axis = Axis.Y
            if clear_axis_on_change:
                self.clear_axis(axis=Axis.X)
        elif self.axis == Axis.Y:
            self.axis = Axis.Z
            if clear_axis_on_change:
                self.clear_axis(axis=Axis.Y)
        elif self.axis == Axis.Z:
            self.axis = Axis.X
            if clear_axis_on_change:
                self.clear_axis(axis=Axis.Z)


    def goto_next_array(self):
        '''Go to the next available array.'''

        for o in self.obj_data:
            
            # Try to set the array after the current one
            was_set = False
            for i, md in enumerate(o.mod_data):
                if i > o.active_mod_index:
                    if md.array_mod.show_viewport == True:
                        if md.logically_deleted == False:
                            o.active_mod_index = i
                            was_set = True
                            break

            if was_set == True:
                continue

            # The array was not set : Try and set on first half
            for i, md in enumerate(o.mod_data):
                if i < o.active_mod_index:
                    if md.array_mod.show_viewport == True:
                        if md.logically_deleted == False:
                            o.active_mod_index = i
                            break


    def set_arrays_to_one(self, negative=False):
        '''Set all arrays to one on the current axis.'''

        for o in self.obj_data:
            mod = o.mod_data[o.active_mod_index].array_mod

            if self.axis == Axis.X:
                if mod.use_relative_offset:
                    mod.relative_offset_displace[0] = 1 if negative == False else -1
                else:
                    snap_factor = abs(o.mesh_obj_dims[0])
                    mod.constant_offset_displace[0] = snap_factor if negative == False else -snap_factor

            elif self.axis == Axis.Y:
                if mod.use_relative_offset:
                    mod.relative_offset_displace[1] = 1 if negative == False else -1
                else:
                    snap_factor = abs(o.mesh_obj_dims[1])
                    mod.constant_offset_displace[1] = snap_factor if negative == False else -snap_factor

            elif self.axis == Axis.Z:
                if mod.use_relative_offset:
                    mod.relative_offset_displace[2] = 1 if negative == False else -1
                else:
                    snap_factor = abs(o.mesh_obj_dims[2])
                    mod.constant_offset_displace[2] = snap_factor if negative == False else -snap_factor


    def move_mod(self, context, up=True):
        '''Move mods up or down on the stack.'''

        original_obj = context.active_object
        for o in self.obj_data:
            obj = o.mesh_obj
            mod = o.mod_data[o.active_mod_index].array_mod
            context.view_layer.objects.active = obj
            if up == True:
                bpy.ops.object.modifier_move_up(modifier=mod.name)
            else:
                bpy.ops.object.modifier_move_down(modifier=mod.name)
        context.view_layer.objects.active = original_obj

    ####################################################
    #   SHADERS
    ####################################################

    def remove_shaders(self):
        '''Remove shader handle.'''

        if self.draw_handle_2D:
            self.draw_handle_2D = bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle_2D, "WINDOW")

        if self.draw_handle_3D:
            self.draw_handle_3D = bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle_3D, "WINDOW")

    # 2D SHADER
    def safe_draw_2D(self, context):
        method_handler(self.draw_shader_2D,
            arguments = (context,),
            identifier = 'Modal Shader 2D',
            exit_method = self.remove_shaders)


    def draw_shader_2D(self, context):
        '''Draw shader handle.'''

        if self.edit_space == Edit_Space.View_2D:
            draw_modal_frame(context)

    # 3D SHADER
    def safe_draw_3D(self, context):
        method_handler(self.draw_shader_3D,
            arguments = (context,),
            identifier = 'Modal Shader 3D',
            exit_method = self.remove_shaders)


    def draw_shader_3D(self, context):
        '''Draw shader handle.'''

        if self.freeze_controls == True:
            return
        elif self.ui_show_guides == False:
            return

        if self.edit_space == Edit_Space.View_3D:
            self.draw_circle_3D()
            self.draw_plane_3D()
        elif self.edit_space == Edit_Space.View_2D:
            self.draw_plane_3D()


    def draw_circle_3D(self):
        '''Draw the circle where the mouse is in 3D.'''

        radius = self.ui_drawing_radius
        if get_preferences().property.array_type == "DOT":
            radius = .0125
            width = 12
        else:
            width = 3

        vertices = []
        indices = []
        segments = 64
        color = (0,0,0,1)

        #Build ring
        for i in range(segments):
            index = i + 1
            angle = i * 3.14159 * 2 / segments

            x = cos(angle) * radius
            y = sin(angle) * radius
            z = 0
            vert = Vector((x, y, z))

            if self.axis == Axis.Z:
                plane_normal = Vector((0,1,0)) @ self.ui_object_data.matrix_world.inverted()
                up = Vector((0,0,1))
                angle = plane_normal.rotation_difference(up)
                rot_mat = angle.to_matrix()
                vert = vert @ rot_mat

            else:
                rot_mat = self.ui_object_data.matrix_world.to_quaternion() 
                rot_mat = rot_mat.to_matrix()
                rot_mat = rot_mat.inverted()
                vert = vert @ rot_mat

            vert[0] = vert[0] + self.ui_3D_circle_loc[0]
            vert[1] = vert[1] + self.ui_3D_circle_loc[1]
            vert[2] = vert[2] + self.ui_3D_circle_loc[2]

            vertices.append(vert)

            if(index == segments):
                indices.append((i, 0))
            else:
                indices.append((i, i + 1))

        if self.axis == Axis.X:
            color = (1, 0, 0, 1)

        elif self.axis == Axis.Y:
            color = (0, 1, 0, 1)

        elif self.axis == Axis.Z:
            color = (0, 1, 1, 1)

        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'LINES', {'pos': vertices}, indices=indices)
        shader.bind()

        shader.uniform_float('color', color)
        
        # Lines
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)

        glLineWidth(width)
        batch.draw(shader)

        del shader
        del batch


    def draw_plane_3D(self):
        '''Draw a 3D plane to represent the editing axis.'''

        vertices = []
        indices = []
        obj = self.ui_object_data
        mat = obj.matrix_world
        x_offset = 1
        y_offset = 1
        
        scale = self.ui_object_data.matrix_world.inverted()
        scale = scale.to_scale()

        if self.axis == Axis.X:
            x_offset = (obj.dimensions[0] + .25) * scale[0]
            y_offset = self.ui_defualt_object_dims[0] * scale[0]
        elif self.axis == Axis.Y:
            x_offset = self.ui_defualt_object_dims[0] * scale[0]
            y_offset = (obj.dimensions[1]  + .25) * scale[0]
        elif self.axis == Axis.Z:
            x_offset = self.ui_defualt_object_dims[0] * scale[0]
            y_offset = (obj.dimensions[2] + .25) * scale[0]


        if self.axis == Axis.Z:
            mat_rot = Matrix.Rotation(math.radians(90.0), 4, 'X')
            mat = mat @ mat_rot

        # Bottom Left
        vert = Vector(( -x_offset, -y_offset, 0 ))
        vert = mat @ vert
        vertices.append(vert)

        # Top Left
        vert = Vector(( -x_offset, y_offset, 0 ))
        vert = mat @ vert
        vertices.append(vert)

        # Top Right
        vert = Vector(( x_offset, y_offset, 0 ))
        vert = mat @ vert
        vertices.append(vert)

        # Bottom Right
        vert = Vector(( x_offset, -y_offset, 0 ))
        vert = mat @ vert
        vertices.append(vert)

        indices.append((0, 1, 2 ))
        indices.append((0, 2, 3 ))

        color = (0,0,0,1)
        if self.axis == Axis.X:
            color = (1, 0, 0, .03125)
        elif self.axis == Axis.Y:
            color = (0, 1, 0, .03125)
        elif self.axis == Axis.Z:
            color = (0, 1, 1, .03125)

        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRIS', {'pos': vertices}, indices=indices)
        shader.bind()

        shader.uniform_float('color', color)

        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        batch.draw(shader)
        del shader
        del batch

        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glDisable(GL_DEPTH_TEST)


def round_quarter(x):
    '''Rounds the decimal point to the nearest quarter (.0, .25, .5, .75)'''
    return round(x * 4) / 4.0
