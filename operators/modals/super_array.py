import bpy
import gpu
import math
import copy
import bmesh
import mathutils
from bgl import *
from enum import Enum
from mathutils import Vector
from math import cos, sin, pi, radians, degrees
from gpu_extras.batch import batch_for_shader
from bpy.props import IntProperty, FloatProperty
from mathutils import Matrix, Vector, geometry, Quaternion
from ... graphics.drawing2d import draw_text
from ... addon.utility import method_handler
from ... preferences import get_preferences
from ... utils.space_3d import get_3D_point_from_mouse, get_3D_raycast_from_mouse
from ... ui_framework.master import Master
from ... ui_framework.utils.mods_list import get_mods_list
from ... utils.toggle_view3d_panels import collapse_3D_view_panels


class Axis(Enum):

    X = 1
    Y = 2
    Z = 3


class Logic_States(Enum):

    VANILLA_ARRAY   = 1
    RADIAL_ARRAY    = 2
    TWIST_ARRAY     = 3


class props():

    #GLOBAL
    intersection_point = (0, 0, 0)
    start_dims_magnitude = .5
    current_axis = Axis.X
    gizmo_normal = (0, 0, 1)
    logic_state = Logic_States.VANILLA_ARRAY

    #RADIAL RENDERING
    use_radial_widget = False


class Vanilla_Behavior():


    def __init__(self, context):

        self.context = context
        self.obj = self.context.active_object
        self.run_setup = True

        self.active_mod = None
        self.use_relative = False
        self.axis = Axis.Z
        self.gizmo_normal = (0, 0, 1)
        self.intersection_point = (0, 0, 0)
        self.offset_vec = Vector((0,0,0))

        #UI Data
        self.ui_data = {
            "mod_name" : "?",
            "offset_vec" : "?",
            "mod_count" : "?",
            "mod_offset" : "?",
            "axis" : "?",
            "count" : "?"}


    def update(self, event):

        if self.run_setup:
            self.setup()

        #Add an array
        if event.type == "A" and event.value == "PRESS" and event.alt != True:
            self.add_array_mod()

        #Remove active array
        elif event.type == "A" and event.value == "PRESS" and event.alt == True:
            self.remove_array()

        #Cycle active array
        elif event.type == "Q" and event.value == "PRESS":
            self.cycle_active_mod()

        #Switch arrays to Relative
        elif event.type == "R" and event.value == "PRESS" and event.alt == False:
            self.use_relative_offset()

        #Switch arrays to Constant
        elif event.type == "C" and event.value == "PRESS" and event.alt == False:
            self.use_constant_offset()

        #Snap to cursor
        elif event.type == "S" and event.value == "PRESS" and event.alt == False:
            self.snap_to_cursor()

        #Count increment
        elif event.type == 'WHEELUPMOUSE' and event.ctrl == True:
            self.add_count(count=1)

        #Count decrement
        elif event.type == 'WHEELDOWNMOUSE' and event.ctrl == True:
            self.add_count(count=-1)

        #Change the axis
        elif event.type == 'X' and event.value == "PRESS" and  event.ctrl == False:
            self.cycle_axis()

        #Clear the axis and toggle
        elif event.type == 'X' and event.value == "PRESS" and  event.ctrl == True:
            self.clear_offsset_axis()

        #Set offset
        elif event.type in {'NUMPAD_0', 'NUMPAD_1', 'NUMPAD_2', 'NUMPAD_3', 'NUMPAD_4', 'NUMPAD_5', 'NUMPAD_6', 'NUMPAD_7', 'NUMPAD_8', 'NUMPAD_9'} and event.value == "PRESS" and event.ctrl == True:

            if(event.type == "NUMPAD_0" and event.value == "PRESS"):
                self.set_offset(0)
            elif(event.type == "NUMPAD_1" and event.value == "PRESS"):
                self.set_offset(1)
            elif(event.type == "NUMPAD_2" and event.value == "PRESS"):
                self.set_offset(2)
            elif(event.type == "NUMPAD_3" and event.value == "PRESS"):
                self.set_offset(3)
            elif(event.type == "NUMPAD_4" and event.value == "PRESS"):
                self.set_offset(4)
            elif(event.type == "NUMPAD_5" and event.value == "PRESS"):
                self.set_offset(5)
            elif(event.type == "NUMPAD_6" and event.value == "PRESS"):
                self.set_offset(6)
            elif(event.type == "NUMPAD_7" and event.value == "PRESS"):
                self.set_offset(7)
            elif(event.type == "NUMPAD_8" and event.value == "PRESS"):
                self.set_offset(9)
            elif(event.type == "NUMPAD_9" and event.value == "PRESS"):
                self.set_offset(9)

        #Adjsut the X, Y, Z of the active array
        elif event.type == 'MOUSEMOVE' and event.ctrl == True and event.shift == False:
            self.adjust_axis_offset(event=event)

        #Ray cast onto object
        elif event.type == 'MOUSEMOVE' and event.ctrl == True and event.shift == True:
            self.ray_snap(event=event)

        #Add count
        elif event.type == "NUMPAD_PLUS" and event.value == "PRESS":
            self.set_offset(offset=1, use_additive=True)

        #Add count
        elif event.type == "NUMPAD_MINUS" and event.value == "PRESS":
            self.set_offset(offset=-1, use_additive=True)

        self.finish()


    def setup(self):

        #Rendering
        props.use_radial_widget = False

        self.active_mod = None

        if self.active_mod == None:
            for mod in self.obj.modifiers:
                if mod.type == 'ARRAY':
                    self.active_mod = mod
                    self.axis = self.get_probable_axis()
                    break

        if self.active_mod == None:
            self.add_array_mod()

        else:
            self.active_mod.show_expanded = False


    def finish(self):

        if self.active_mod != None:

            self.ui_data["mod_name"] = self.active_mod.name

            # Set the offset
            if self.axis == Axis.X:
                if self.active_mod.use_relative_offset == True:
                    self.ui_data["offset_vec"] = f'{self.active_mod.relative_offset_displace[0] : .2f}'
                else:
                    self.ui_data["offset_vec"] = f'{self.active_mod.constant_offset_displace[0] : .2f}'

            elif self.axis == Axis.Y:
                if self.active_mod.use_relative_offset == True:
                    self.ui_data["offset_vec"] = f'{self.active_mod.relative_offset_displace[1] : .2f}'
                else:
                    self.ui_data["offset_vec"] = f'{self.active_mod.constant_offset_displace[1] : .2f}'

            elif self.axis == Axis.Z:
                if self.active_mod.use_relative_offset == True:
                    self.ui_data["offset_vec"] = f'{self.active_mod.relative_offset_displace[2] : .2f}'
                else:
                    self.ui_data["offset_vec"] = f'{self.active_mod.constant_offset_displace[2] : .2f}'

            mod_count = 0
            for mod in self.obj.modifiers:

                if mod.type == 'ARRAY':
                    mod_count += 1

            self.ui_data["mod_count"] = mod_count

            if self.active_mod.use_relative_offset and self.active_mod.use_constant_offset:
                self.ui_data["mod_offset"] = "Mixed"

            elif self.active_mod.use_object_offset:
                self.ui_data["mod_offset"] = "Object"

            elif self.active_mod.use_relative_offset:
                self.ui_data["mod_offset"] = "Relative"

            else:
                self.ui_data["mod_offset"] = "Constant"

            self.ui_data["axis"] = self.axis.name

            self.ui_data["count"] = self.active_mod.count

            # Global Props Update
            props.current_axis = self.axis
            props.gizmo_normal = self.gizmo_normal
            props.intersection_point = self.intersection_point


    def snap_to_cursor(self):

        self.obj.location = self.context.scene.cursor.location


    def ray_snap(self, event):

        self.obj.hide_set(True)

        result, location, normal, index, object, matrix = get_3D_raycast_from_mouse(event=event, context=self.context)

        if result and object.name != self.obj.name:

            #Rendering
            self.intersection_point = location

            self.obj.rotation_euler.zero()

            up = Vector((0, 0, 1))
            angle = normal.rotation_difference(up)
            angle.invert()
            rot = angle.to_euler()

            self.obj.rotation_euler = rot

            #Set obj location
            self.obj.location = location

        self.obj.hide_set(False)


    def add_array_mod(self):

        self.active_mod = self.obj.modifiers.new("Array", 'ARRAY')
        self.active_mod.show_expanded = False

        if self.use_relative:
            self.active_mod.use_relative_offset = True
            self.active_mod.use_constant_offset = False
        else:
            self.active_mod.use_relative_offset = False
            self.active_mod.use_constant_offset = True

        self.cycle_axis()
        self.set_offset(offset=2)


    def set_offset(self, offset=0, use_additive=False):

        if self.active_mod != None and self.active_mod.type == 'ARRAY':

            #Kick it out if the array is the Twist array
            if self.active_mod.name[:11] == "Twist Array":
                props.logic_state = Logic_States.TWIST_ARRAY
                return

            #Kick it out if the array is the Radial array
            elif self.active_mod.name[:12] == "Radial Array":
                props.logic_state = Logic_States.RADIAL_ARRAY
                return

            elif self.active_mod.use_relative_offset == True:
                if use_additive:
                    if self.axis == Axis.X:
                        self.active_mod.relative_offset_displace[0] += offset
                    elif self.axis == Axis.Y:
                        self.active_mod.relative_offset_displace[1] += offset
                    elif self.axis == Axis.Z:
                        self.active_mod.relative_offset_displace[2] += offset
                else:
                    if self.axis == Axis.X:
                        self.active_mod.relative_offset_displace[0] = offset
                    elif self.axis == Axis.Y:
                        self.active_mod.relative_offset_displace[1] = offset
                    elif self.axis == Axis.Z:
                        self.active_mod.relative_offset_displace[2] = offset

            elif self.active_mod.use_constant_offset == True:
                if use_additive:
                    if self.axis == Axis.X:
                        self.active_mod.constant_offset_displace[0] += offset
                    elif self.axis == Axis.Y:
                        self.active_mod.constant_offset_displace[1] += offset
                    elif self.axis == Axis.Z:
                        self.active_mod.constant_offset_displace[2] += offset
                else:
                    if self.axis == Axis.X:
                        self.active_mod.constant_offset_displace[0] = offset
                    elif self.axis == Axis.Y:
                        self.active_mod.constant_offset_displace[1] = offset
                    elif self.axis == Axis.Z:
                        self.active_mod.constant_offset_displace[2] = offset


    def remove_array(self):

        #Make sure delete is not called on None
        if self.active_mod == None:

            self.add_array_mod()

        # Delete Radial Array
        elif self.active_mod.name[:12] == "Radial Array":

            array_index = self.obj.modifiers.find(self.active_mod.name)

            displace_index = 0
            for mod in self.obj.modifiers:
                if mod.type == 'DISPLACE':
                    displace_index = self.obj.modifiers.find(mod.name)

            if displace_index == array_index - 1:
                self.obj.modifiers.remove(self.obj.modifiers[displace_index])

                for child in self.obj.children:
                    if child.name == 'Radial Empty':
                        bpy.data.objects.remove(child, do_unlink=True, do_id_user=True, do_ui_user=True)
                        break

            #Delete radial array
            self.obj.modifiers.remove(self.obj.modifiers[self.active_mod.name])

            mod_count = 0
            for mod in self.obj.modifiers:
                if mod.type == 'ARRAY':
                    mod_count += 1

            if mod_count > 1:
                for mod in self.obj.modifiers:
                    if mod.type == 'ARRAY':
                        self.active_mod = mod
                        axis = self.get_probable_axis()
                        if axis != None:
                            props.current_axis = axis

            else:
                self.add_array_mod()


        # Delete Twist Array
        elif self.active_mod.name[:11] == "Twist Array":

            array_index = self.obj.modifiers.find(self.active_mod.name)

            # Get displace
            displace_index = 0
            for mod in self.obj.modifiers:
                if mod.type == 'DISPLACE':
                    displace_index = self.obj.modifiers.find(mod.name)
                    break

            if displace_index == array_index - 1:
                self.obj.modifiers.remove(self.obj.modifiers[displace_index])

            array_index = self.obj.modifiers.find(self.active_mod.name)

            # Get deform
            displace_index = 0
            for mod in self.obj.modifiers:
                if mod.type == 'SIMPLE_DEFORM':
                    displace_index = self.obj.modifiers.find(mod.name)

            if displace_index == array_index + 1:
                self.obj.modifiers.remove(self.obj.modifiers[displace_index])

            array_index = self.obj.modifiers.find(self.active_mod.name)

            # Get deform 2
            displace_index = 0
            for mod in self.obj.modifiers:
                if mod.type == 'DISPLACE':
                    displace_index = self.obj.modifiers.find(mod.name)

            if displace_index == array_index + 1:
                self.obj.modifiers.remove(self.obj.modifiers[displace_index])

            #Delete radial array
            self.obj.modifiers.remove(self.obj.modifiers[self.active_mod.name])

            mod_count = 0
            for mod in self.obj.modifiers:
                if mod.type == 'ARRAY':
                    mod_count += 1

            if mod_count > 1:
                for mod in self.obj.modifiers:
                    if mod.type == 'ARRAY':
                        self.active_mod = mod
                        axis = self.get_probable_axis()
                        if axis != None:
                            props.current_axis = axis

            else:
                self.add_array_mod()

        #Regular delete mod
        else:

            mod_count = 0
            for mod in self.obj.modifiers:
                if mod.type == 'ARRAY':
                    mod_count += 1

            if mod_count > 1:

                self.obj.modifiers.remove(self.active_mod)

                for mod in self.obj.modifiers:
                    if mod.type == 'ARRAY':
                        self.active_mod = mod
                        axis = self.get_probable_axis()
                        if axis != None:
                            props.current_axis = axis


    def adjust_axis_offset(self, event):

        self.offset_vec = Vector((0,0,0))

        mouse_pos = Vector((event.mouse_region_x, event.mouse_region_y))

        #Get mouse offset
        if self.axis == Axis.Z:

            #Get the normal from local space matrix
            object_normal = Vector((0,1,0)) @ self.obj.matrix_local.inverted()
            self.intersection_point = get_3D_point_from_mouse(mouse_pos, self.context, self.obj.location, object_normal)
            self.offset_vec = self.intersection_point - self.obj.location

        else:

            #Get the normal from local space matrix
            object_normal = Vector((0,0,1)) @ self.obj.matrix_local.inverted()
            self.intersection_point = get_3D_point_from_mouse(mouse_pos, self.context, self.obj.location, object_normal)
            self.offset_vec = self.intersection_point - self.obj.location

        #Get magnitude
        magnitude = math.sqrt( ((self.intersection_point[0] - self.obj.location[0]) ** 2) +
                                ((self.intersection_point[1] - self.obj.location[1]) ** 2) +
                                ((self.intersection_point[2] - self.obj.location[2]) ** 2))

        inter_vec = Vector((self.intersection_point[0], self.intersection_point[1], self.intersection_point[2]))
        trans_inter = self.obj.matrix_local.inverted() @  inter_vec

        #Apply Offsets
        if self.axis == Axis.X:

            if trans_inter[0] < 0:
                magnitude *= -1

            if self.active_mod.use_relative_offset == True:
                self.add_relative_offset((magnitude, 0, 0))
            else:
                self.add_constant_offset((magnitude, 0, 0))

        elif self.axis == Axis.Y:

            if trans_inter[1] < 0:
                magnitude *= -1

            if self.active_mod.use_relative_offset == True:
                self.add_relative_offset((0, magnitude, 0))
            else:
                self.add_constant_offset((0, magnitude, 0))

        elif self.axis == Axis.Z:

            if trans_inter[2] < 0:
                magnitude *= -1

            if self.active_mod.use_relative_offset == True:
                self.add_relative_offset((0, 0, magnitude))
            else:
                self.add_constant_offset((0, 0, magnitude))


    def add_offset(self, count=1):
        '''Called from UI Elements'''

        #Apply Offsets
        if self.axis == Axis.X:

            if self.active_mod.use_relative_offset == True:
                self.add_relative_offset((count, 0, 0), additive=True)
            else:
                self.add_constant_offset((count, 0, 0), additive=True)

        elif self.axis == Axis.Y:

            if self.active_mod.use_relative_offset == True:
                self.add_relative_offset((0, count, 0), additive=True)
            else:
                self.add_constant_offset((0, count, 0), additive=True)

        elif self.axis == Axis.Z:

            if self.active_mod.use_relative_offset == True:
                self.add_relative_offset((0, 0, count), additive=True)
            else:
                self.add_constant_offset((0, 0, count), additive=True)


    def get_probable_axis(self):

        if self.active_mod != None and self.active_mod.type == 'ARRAY':
            if self.active_mod.use_relative_offset:
                vec = self.active_mod.relative_offset_displace
                index = 0
                compare = 0
                for i in range(len(vec)):
                    if abs(vec[i]) > abs(compare):
                        compare = vec[i]
                        index = i
                if index == 0:
                    return Axis.X
                if index == 1:
                    return Axis.Y
                if index == 2:
                    return Axis.Z
            elif self.active_mod.use_constant_offset:
                vec = self.active_mod.constant_offset_displace
                index = 0
                compare = 0
                for i in range(len(vec)):
                    if abs(vec[i]) > abs(compare):
                        compare = vec[i]
                        index = i
                if index == 0:
                    return Axis.X
                if index == 1:
                    return Axis.Y
                if index == 2:
                    return Axis.Z
            elif self.active_mod.use_object_offset:
                return self.axis

        else:
            return self.axis


    def cycle_active_mod(self):

        mod_locs = []
        matched_loc = 0

        for i in range(len(self.obj.modifiers)):
            if self.obj.modifiers[i].type == 'ARRAY':
                mod_locs.append(i)
                if self.obj.modifiers[i] == self.active_mod:
                    matched_loc = i

        if len(mod_locs) > 1:
            for i in range(len(mod_locs)):
                if matched_loc == mod_locs[i]:
                    if i == len(mod_locs) - 1:
                        self.active_mod = self.obj.modifiers[mod_locs[0]]
                        self.axis = self.get_probable_axis()
                        self.update_gizmo_normal_from_axis()
                        break
                    else:
                        self.active_mod = self.obj.modifiers[mod_locs[i + 1]]
                        self.axis = self.get_probable_axis()
                        self.update_gizmo_normal_from_axis()
                        break


    def clear_offsset_axis(self):

        #Relative
        if self.active_mod.use_relative_offset == True:
            self.zero_out_relative_offset_axis()
            self.cycle_axis()

        #Constant
        if self.active_mod.use_constant_offset == True:
            self.zero_out_constant_offset_axis()
            self.cycle_axis()


    def toggle_offset_type(self):

        if self.active_mod.use_relative_offset:
            self.use_constant_offset()
        elif self.active_mod.use_constant_offset:
            self.use_relative_offset()


    #RELATIVE OFFSET
    def use_relative_offset(self):

        self.active_mod.use_relative_offset = True
        self.active_mod.use_constant_offset = False
        self.use_relative = True


    def zero_out_relative_offset_axis(self):

        if self.active_mod != None and self.active_mod.type == 'ARRAY':
            if self.axis == Axis.X:
                self.active_mod.relative_offset_displace[0] = 0
            elif self.axis == Axis.Y:
                self.active_mod.relative_offset_displace[1] = 0
            elif self.axis == Axis.Z:
                self.active_mod.relative_offset_displace[2] = 0


    def add_relative_offset(self, offset=(0,0,0), additive=False):

        if self.active_mod != None and self.active_mod.type == 'ARRAY':
            #Kick it out if the array is the Twist array
            if self.active_mod.name[:11] == "Twist Array":
                props.logic_state = Logic_States.TWIST_ARRAY
                return

            #Kick it out if the array is the Radial array
            elif self.active_mod.name[:12] == "Radial Array":
                props.logic_state = Logic_States.RADIAL_ARRAY
                return

            if additive:
                self.active_mod.relative_offset_displace[0] += offset[0]
                self.active_mod.relative_offset_displace[1] += offset[1]
                self.active_mod.relative_offset_displace[2] += offset[2]

            else:
                if abs(offset[0]) > 0:
                    self.active_mod.relative_offset_displace[0] = offset[0] / 5
                elif abs(offset[1]) > 0:
                    self.active_mod.relative_offset_displace[1] = offset[1] / 5
                elif abs(offset[2]) > 0:
                    self.active_mod.relative_offset_displace[2] = offset[2] / 5
        else:
            return

    #CONSTANT OFFSET
    def use_constant_offset(self):

        self.active_mod.use_relative_offset = False
        self.active_mod.use_constant_offset = True
        self.use_relative = False


    def zero_out_constant_offset_axis(self):

        if self.active_mod != None and self.active_mod.type == 'ARRAY':
            if self.axis == Axis.X:
                self.active_mod.constant_offset_displace[0] = 0
            elif self.axis == Axis.Y:
                self.active_mod.constant_offset_displace[1] = 0
            elif self.axis == Axis.Z:
                self.active_mod.constant_offset_displace[2] = 0


    def add_constant_offset(self, offset=(0,0,0), additive=False):

        if self.active_mod != None and self.active_mod.type == 'ARRAY':
            #Kick it out if the array is the Twist array
            if self.active_mod.name[:11] == "Twist Array":
                props.logic_state = Logic_States.TWIST_ARRAY
                return

            #Kick it out if the array is the Radial array
            elif self.active_mod.name[:12] == "Radial Array":
                props.logic_state = Logic_States.RADIAL_ARRAY
                return

            if additive:
                self.active_mod.constant_offset_displace[0] += offset[0]
                self.active_mod.constant_offset_displace[1] += offset[1]
                self.active_mod.constant_offset_displace[2] += offset[2]

            else:
                if abs(offset[0]) > 0:
                    self.active_mod.constant_offset_displace[0] = offset[0]
                elif abs(offset[1]) > 0:
                    self.active_mod.constant_offset_displace[1] = offset[1]
                elif abs(offset[2]) > 0:
                    self.active_mod.constant_offset_displace[2] = offset[2]
        else:
            return


    def add_count(self, count):

        if self.active_mod != None and self.active_mod.type == 'ARRAY':
            #Kick it out if the array is the Twist array
            if self.active_mod.name[:11] == "Twist Array":
                props.logic_state = Logic_States.TWIST_ARRAY
                return
            self.active_mod.count += count


    def update_gizmo_normal_from_axis(self):

        val = self.axis.value

        if(val == 1):
            self.axis = Axis.X
            self.gizmo_normal = (0,0,1)
        elif(val == 2):
            self.axis = Axis.Y
            self.gizmo_normal = (0,0,1)
        elif(val == 3):
            self.axis = Axis.Z
            self.gizmo_normal = (0,0,0)


    def cycle_axis(self):

        val = self.axis.value

        if(val == 1):
            self.axis = Axis.Y
            self.gizmo_normal = (0,0,1)
        elif(val == 2):
            self.axis = Axis.Z
            self.gizmo_normal = (0,0,0)
        elif(val == 3):
            self.axis = Axis.X
            self.gizmo_normal = (0,0,1)


class Radial_Behavior():


    def __init__(self, context):

        self.context = context
        self.obj = self.context.active_object
        self.run_setup = True

        self.radial_array_mod = None
        self.displace_mod = None
        self.radial_empty = None
        self.axis = Axis.Y
        self.displace = 1
        self.segments = 6
        self.intersection_point = (0, 0, 0)
        self.angle_index = 0

        #UI Data
        self.ui_data = {
            "segments" : "?",
            "displace" : "?",
            "direction" : "?",
            "mod_name" : "?"}


    def update(self, event):

        if self.run_setup:
            self.setup()

        #Count increment
        if event.type == 'WHEELUPMOUSE' and event.ctrl == True:
            self.add_count(count=1)

        #Count decrement
        elif event.type == 'WHEELDOWNMOUSE' and event.ctrl == True:
            self.add_count(count=-1)

        #Adjsut the X, Y, Z of the active array
        elif event.type == 'MOUSEMOVE' and  event.ctrl == True and event.shift == False:
            self.set_offset(event=event)

        #Snap to cursor
        elif event.type == "S" and event.value == "PRESS" and event.alt == False:
            self.snap_to_cursor()

        #Ray cast onto object
        elif event.type == 'MOUSEMOVE' and  event.ctrl == True and event.shift == True:
            self.ray_snap(event=event)

        #Switch the offset direction
        elif event.type == 'X' and event.value == "PRESS":
            self.switch_axis()

        # Set the radial sweep angle
        elif event.type == 'R' and event.value == 'PRESS':
            self.adjust_angle()

        self.finish()


    def setup(self):

        #Delete twist setup
        for a, b, c, d in zip(self.obj.modifiers[:-3], self.obj.modifiers[1:-2], self.obj.modifiers[2:-1], self.obj.modifiers[3:]):
            if a.type == 'DISPLACE' and b.type == 'ARRAY' and c.type == 'SIMPLE_DEFORM' and d.type == 'DISPLACE':
                self.obj.modifiers.remove(a)
                self.obj.modifiers.remove(b)
                self.obj.modifiers.remove(c)
                self.obj.modifiers.remove(d)
                break

        #Have to reset radial each update
        #If the user switches back to Vanilla and deletes it, then the values ref nothing while still not None value
        self.radial_array_mod = None
        self.displace_mod = None
        self.radial_empty = None

        #Rendering
        props.use_radial_widget = True

        #Check to see if array and dispalce are setup
        if self.radial_array_mod == None and self.displace_mod == None:

            #Check for correct ordering
            for displace, array in zip(self.obj.modifiers[:-1], self.obj.modifiers[1:]):
                if displace.type == 'DISPLACE' and array.type == 'ARRAY':
                    self.displace_mod = displace
                    self.radial_array_mod = array

                #If zip found items, name them
                if self.displace_mod and self.radial_array_mod:
                    self.displace_mod.name = "Radial Displace"
                    self.radial_array_mod.name = "Radial Array"

            #Check for incorrect ordering if zip found nothing
            if self.radial_array_mod == None and self.displace_mod == None:

                for displace, array in zip(self.obj.modifiers[1:], self.obj.modifiers[:-1]):
                    if displace.type == 'DISPLACE' and array.type == 'ARRAY':
                        self.displace_mod = displace
                        self.radial_array_mod = array

                #If zip found items, name them
                if self.displace_mod and self.radial_array_mod:
                    self.displace_mod.name = "Radial Displace"
                    self.radial_array_mod.name = "Radial Array"

                    bpy.ops.object.modifier_move_up(modifier=self.displace_mod.name)

        #Zip did not find radial setup, check for only one array
        if self.radial_array_mod == None and self.displace_mod == None:

            #Check for single array mod
            array_count = 0
            array_temp = None
            array_index = 0

            for mod in self.obj.modifiers:
                if mod.type == 'ARRAY':
                    array_count += 1
                    array_temp = mod
                array_index += 1

            #If only one array is found, make that the radial array and add displace
            if array_count == 1:
                self.radial_array_mod = array_temp

                self.radial_array_mod.name = "Radial Array"
                self.radial_array_mod.use_constant_offset = False
                self.radial_array_mod.use_relative_offset = False
                self.radial_array_mod.use_object_offset = True
                self.segments = self.radial_array_mod.count

                #Add displace, zip would have found it otherwise
                self.displace_mod = self.obj.modifiers.new("Radial Displace", 'DISPLACE')

                self.displace_mod.mid_level = 0.0
                self.displace_mod.direction = self.axis.name
                self.displace_mod.strength = self.displace

                #Move the displace above the array
                error_out = 0
                while self.obj.modifiers.find(self.displace_mod.name) != array_index - 1:
                    bpy.ops.object.modifier_move_up(modifier=self.displace_mod.name)
                    error_out += 1
                    if error_out > 1000:
                        break

        #Zip did not find mods, there was more than one array
        if self.radial_array_mod == None and self.displace_mod == None:

            self.displace_mod = self.obj.modifiers.new("Radial Displace", 'DISPLACE')
            self.displace_mod.mid_level = 0.0
            self.displace_mod.direction = self.axis.name
            self.displace_mod.strength = self.displace

            self.radial_array_mod = self.obj.modifiers.new("Radial Array", 'ARRAY')
            self.radial_array_mod.use_constant_offset = False
            self.radial_array_mod.use_relative_offset = False
            self.radial_array_mod.use_object_offset = True
            self.radial_array_mod.count = self.segments

        #Check for radial empty, create if not found, add drivers
        if self.radial_empty == None:

            #Check to see if there is a child emptpy 'Radial Empty'
            for child in self.obj.children:
                if child.name == 'Radial Empty':
                    self.radial_empty = child
                    break

            #Found radial empty in children
            if self.radial_empty != None:
                self.radial_array_mod.offset_object = self.radial_empty

            #There was no child radial empty
            if self.radial_empty == None:

                self.radial_empty = bpy.data.objects.new("Radial Empty", None)
                self.radial_empty.empty_display_type = 'SPHERE'
                self.radial_empty.parent = self.obj

                for col in self.obj.users_collection:
                    col.objects.link(self.radial_empty)

                self.radial_array_mod.offset_object = self.radial_empty

                #Target the Empty
                self.radial_empty.parent = self.obj

            #Create drivers
            if self.radial_empty:

                #Creat the drivers
                for index in range(3):
                    self.radial_empty.driver_remove("rotation_euler", index)
                    driver = self.radial_empty.driver_add("rotation_euler", index).driver

                    count = driver.variables.new()
                    count.name = "count"
                    count.targets[0].id = self.obj
                    count.targets[0].data_path = "modifiers[\"Radial Array\"].count"

                    direction = driver.variables.new()
                    direction.name = "direction"
                    direction.targets[0].id = self.obj
                    direction.targets[0].data_path = "modifiers[\"Radial Displace\"].direction"

                    driver.expression = f"{math.radians(360)} / count if direction == {[2,0,1][index]} else 0"

        self.segments = self.radial_array_mod.count
        self.displace = self.displace_mod.strength

        self.radial_array_mod.show_render = get_preferences().property.Hops_twist_radial_sort
        self.radial_array_mod.show_in_editmode = not get_preferences().property.Hops_twist_radial_sort

        self.displace_mod.show_render = get_preferences().property.Hops_twist_radial_sort
        self.displace_mod.show_in_editmode = not get_preferences().property.Hops_twist_radial_sort

        self.radial_array_mod.show_expanded = False
        self.displace_mod.show_expanded = False


    def finish(self):

        #UI
        self.ui_data["segments"] = str(self.segments)
        self.ui_data["displace"] = str( "%.4f" % self.displace)
        self.ui_data["direction"] = str(self.axis.name)
        self.ui_data["mod_name"] = str(self.radial_array_mod.name)

        #Rendering
        props.intersection_point = self.intersection_point


    def adjust_angle(self):

        rotations = ['360', '180', '90', '60', '45', '30', '15']
        self.angle_index += 1
        if self.angle_index + 1 == len(rotations):
            self.angle_index = 0
        rotation = int(rotations[self.angle_index])

        #Create drivers
        if self.radial_empty:

            #Creat the drivers
            for index in range(3):
                self.radial_empty.driver_remove("rotation_euler", index)
                driver = self.radial_empty.driver_add("rotation_euler", index).driver

                count = driver.variables.new()
                count.name = "count"
                count.targets[0].id = self.obj
                count.targets[0].data_path = "modifiers[\"Radial Array\"].count"

                direction = driver.variables.new()
                direction.name = "direction"
                direction.targets[0].id = self.obj
                direction.targets[0].data_path = "modifiers[\"Radial Displace\"].direction"

                driver.expression = f"{math.radians(rotation)} / count if direction == {[2,0,1][index]} else 0"


    def snap_to_cursor(self):

        self.obj.location = self.context.scene.cursor.location


    def add_count(self, count):

        self.radial_array_mod.count += count
        self.segments = self.radial_array_mod.count


    def add_offset(self, count):

        if self.displace_mod != None and self.displace_mod.type == 'DISPLACE':

            #Offset object
            self.displace_mod.strength += count
            self.displace = self.displace_mod.strength


    def set_offset(self, event):

        if self.displace_mod != None and self.displace_mod.type == 'DISPLACE':

            mouse_pos = Vector((event.mouse_region_x, event.mouse_region_y))

            #Get the normal from local space matrix
            object_normal = Vector((0,0,1)) @ self.obj.matrix_local.inverted()
            self.intersection_point = get_3D_point_from_mouse(mouse_pos, self.context, self.obj.location, object_normal)

            #Get magnitude between
            magnitude = math.sqrt( ((self.intersection_point[0] - self.obj.location[0]) ** 2) +
                                   ((self.intersection_point[1] - self.obj.location[1]) ** 2) +
                                   ((self.intersection_point[2] - self.obj.location[2]) ** 2))

            #Offset object
            self.displace_mod.strength = magnitude
            self.displace = self.displace_mod.strength


    def ray_snap(self, event):

        self.obj.hide_set(True)

        result, location, normal, index, object, matrix = get_3D_raycast_from_mouse(event=event, context=self.context)

        if result and object.name != self.obj.name:

            #Rendering
            self.intersection_point = location

            self.obj.rotation_euler.zero()

            up = Vector((0, 0, 1))
            angle = normal.rotation_difference(up)
            angle.invert()
            rot = angle.to_euler()

            self.obj.rotation_euler = rot

            #Set obj location
            self.obj.location = location

        self.obj.hide_set(False)


    def switch_axis(self):

        if self.displace_mod != None:

            val = self.axis.value

            if(val == 1):
                self.axis = Axis.Y
            elif(val == 2):
                self.axis = Axis.Z
            elif(val == 3):
                self.axis = Axis.X

            self.displace_mod.direction = self.axis.name


class Twist_Behavior():


    def __init__(self, context):

        self.context = context
        self.obj = self.context.active_object
        self.run_setup = True

        self.displace_mod_one = None
        self.array_mod = None
        self.deform_mod = None
        self.displace_mod_two = None
        self.intersection_point = (0,0,0)
        self.axis = 'Z'
        self.count = 8
        self.angle = 360

        #UI Data
        self.ui_data = {
            "count" : "?",
            "offset" : "?",
            "axis" : "?",
            "mod_name" : "?",
            "angle" : "?"}


    def update(self, event):

        if self.run_setup:
            self.setup()

        #Count increment
        if event.type == 'WHEELUPMOUSE' and event.ctrl == True:
            self.add_count(count=1)

        #Count decrement
        elif event.type == 'WHEELDOWNMOUSE' and event.ctrl == True:
            self.add_count(count=-1)

        #Switch axis
        elif event.type == "X" and event.value == "PRESS" and event.alt == False:
            self.switch_axis()

        #Snap to cursor
        elif event.type == "S" and event.value == "PRESS" and event.alt == False:
            self.snap_to_cursor()

        #Adjsut the offset on displace
        elif event.type == 'MOUSEMOVE' and  event.ctrl == True and event.shift == False:
            self.set_offset(event=event)

        #Ray cast onto object
        elif event.type == 'MOUSEMOVE' and  event.ctrl == True and event.shift == True:
            self.ray_snap(event=event)

        #Adjust sweep angle
        elif event.type == 'MOUSEMOVE' and event.alt == True and  event.ctrl == False and event.shift == True:
            self.adjust_sweep(event=event)

        self.center(self.context)

        self.finish()


    def setup(self):

        #Delete Radial mods and empty
        for displace, array in zip(self.obj.modifiers[:-1], self.obj.modifiers[1:]):
            if displace.type == 'DISPLACE' and displace.name[:15] == "Radial Displace" and array.type == 'ARRAY' and array.name[:12] == "Radial Array":
                self.obj.modifiers.remove(displace)
                self.obj.modifiers.remove(array)

        #Check to see if there is a child emptpy 'Radial Empty'
        for child in self.obj.children:
            if child.name == 'Radial Empty':
                bpy.data.objects.remove(child)
                break


        #Rendering
        props.use_radial_widget = True

        self.displace_mod_one = None
        self.array_mod = None
        self.deform_mod = None
        self.displace_mod_two = None


        #Check for initial setup
        for a, b, c, d in zip(self.obj.modifiers[:-3], self.obj.modifiers[1:-2], self.obj.modifiers[2:-1], self.obj.modifiers[3:]):
            if a.type == 'DISPLACE' and b.type == 'ARRAY' and c.type == 'SIMPLE_DEFORM' and d.type == 'DISPLACE':
                self.displace_mod_one = a
                self.array_mod = b
                self.array_mod.name = "Twist Array"
                self.deform_mod = c
                self.displace_mod_two = d
                break


        if not self.displace_mod_one:
            self.displace_mod_one = self.obj.modifiers.new("Displace One", 'DISPLACE')
            self.displace_mod_one.mid_level = 0.0
            self.displace_mod_one.direction = 'X' if self.axis == 'Y' else 'Y'
            self.displace_mod_one.strength = -2
            self.displace_new_one = True

        if not self.array_mod:
            self.array_mod = self.obj.modifiers.new("Twist Array", 'ARRAY')
            self.array_mod.count = self.count
            self.array_new = True

        if not self.deform_mod:
            self.deform_mod = self.obj.modifiers.new("Simple Deform", 'SIMPLE_DEFORM')
            self.deform_mod.angle = math.radians(self.angle)
            self.deform_mod.deform_method = 'BEND'
            self.deform_mod.deform_axis = self.axis
            self.deform_new = True

        if not self.displace_mod_two:
            self.displace_mod_two = self.obj.modifiers.new("Displace Two", 'DISPLACE')
            self.displace_mod_two.mid_level = 0.0
            self.displace_mod_two.direction = 'X' if self.axis == 'Y' else 'Y'
            self.displace_mod_two.strength = -1.0
            self.displace_new_two = True


        #Check for a single array about the twist stack
        temp_mod = None
        arrays_before_displace = 0

        for mod in self.obj.modifiers:
            if mod.type == 'ARRAY':
                arrays_before_displace += 1
                temp_mod = mod
            if mod.type == 'DISPLACE' and mod.name == "Displace One":
                break

        if arrays_before_displace == 1 and temp_mod != None:
            self.array_mod.count = temp_mod.count
            self.obj.modifiers.remove(temp_mod)


        self.array_mod.use_constant_offset = False
        self.array_mod.use_relative_offset = True
        self.array_mod.use_object_offset = False
        self.array_mod.relative_offset_displace = (1.0, 0.0, 0.0) if self.deform_mod.deform_axis == 'Z' else (0.0, 0.0, 1.0)


        self.axis = self.deform_mod.deform_axis
        self.count = self.array_mod.count
        self.angle = math.degrees(self.deform_mod.angle)

        if self.array_mod.count < 4:
            self.count = 3
            self.array_mod.count = self.count


        self.array_mod.show_render = get_preferences().property.Hops_twist_radial_sort
        self.displace_mod_two.show_render = not get_preferences().property.Hops_twist_radial_sort
        self.array_mod.show_expanded = False

        self.displace_mod_two.show_render = get_preferences().property.Hops_twist_radial_sort
        self.displace_mod_two.show_in_editmode = not get_preferences().property.Hops_twist_radial_sort
        self.displace_mod_two.show_expanded = False

        self.displace_mod_one.show_render = get_preferences().property.Hops_twist_radial_sort
        self.displace_mod_one.show_in_editmode = not get_preferences().property.Hops_twist_radial_sort
        self.displace_mod_one.show_expanded = False

        self.deform_mod.show_render = get_preferences().property.Hops_twist_radial_sort
        self.deform_mod.show_in_editmode = not get_preferences().property.Hops_twist_radial_sort
        self.deform_mod.show_expanded = False


    def finish(self):

        #Rendering
        props.intersection_point = self.intersection_point

        if self.array_mod != None:

            self.ui_data["count"] = str(self.array_mod.count)
            self.ui_data["offset"] = str( "%.4f" % self.displace_mod_one.strength)
            self.ui_data["axis"] = str(self.axis)
            self.ui_data["mod_name"] = self.array_mod.name
            self.ui_data["angle"] = str( "%.2f" % self.angle)


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


    def add_count(self, count):

        if self.array_mod != None:
            if self.array_mod.count < 4:
                self.array_mod.count = 3
                if count > 0:
                    self.array_mod.count += count
                return
            else:
                self.array_mod.count += count


    def add_angle(self, count):

        if self.deform_mod != None:

            #Offset object
            self.deform_mod.angle += radians(count)
            self.angle = degrees(self.deform_mod.angle)

            if self.deform_mod.angle > radians(360):
                self.deform_mod.angle = radians(360)
                self.angle = 360

            elif self.deform_mod.angle < 0:
                self.deform_mod.angle = 0
                self.angle = 0


    def adjust_sweep(self, event):

        if self.deform_mod != None:

            mouse_pos = Vector((event.mouse_region_x, event.mouse_region_y))

            #Get the normal from local space matrix
            object_normal = Vector((0,0,1)) @ self.obj.matrix_local.inverted()
            self.intersection_point = get_3D_point_from_mouse(mouse_pos, self.context, self.obj.location, object_normal)

            #Get magnitude between
            magnitude = math.sqrt( ((self.intersection_point[0] - self.obj.location[0]) ** 2) +
                                    ((self.intersection_point[1] - self.obj.location[1]) ** 2) +
                                    ((self.intersection_point[2] - self.obj.location[2]) ** 2))

            #Offset object
            self.deform_mod.angle = magnitude * .5 - 1

            if self.deform_mod.angle > radians(360):
                self.deform_mod.angle = radians(360)

            elif self.deform_mod.angle < radians(0):
                self.deform_mod.angle = radians(0)

            self.angle = degrees(self.deform_mod.angle)


    def snap_to_cursor(self):

        self.obj.location = self.context.scene.cursor.location


    def switch_axis(self):

        self.axis = "YZX"["XYZ".find(self.axis)]
        self.displace_mod_one.direction = 'X' if self.axis == 'Y' else 'Y'
        self.array_mod.relative_offset_displace = (1.0, 0.0, 0.0) if self.axis == 'Z' else (0.0, 0.0, 1.0)
        self.deform_mod.deform_axis = self.axis
        self.displace_mod_two.direction = 'X' if self.axis == 'Y' else 'Y'


    def add_offset(self, count):

        if self.displace_mod_one != None and self.displace_mod_one.type == 'DISPLACE':

            #Offset object
            self.displace_mod_one.strength += count


    def set_offset(self, event):

        if self.displace_mod_one != None and self.displace_mod_one.type == 'DISPLACE':

            mouse_pos = Vector((event.mouse_region_x, event.mouse_region_y))

            #Get the normal from local space matrix
            object_normal = Vector((0,0,1)) @ self.obj.matrix_local.inverted()
            self.intersection_point = get_3D_point_from_mouse(mouse_pos, self.context, self.obj.location, object_normal)

            #Get magnitude between
            magnitude = math.sqrt( ((self.intersection_point[0] - self.obj.location[0]) ** 2) +
                                    ((self.intersection_point[1] - self.obj.location[1]) ** 2) +
                                    ((self.intersection_point[2] - self.obj.location[2]) ** 2))

            #Offset object
            self.displace_mod_one.strength = -magnitude - self.displace_mod_two.strength


    def ray_snap(self, event):

        self.obj.hide_set(True)

        result, location, normal, index, object, matrix = get_3D_raycast_from_mouse(event=event, context=self.context)

        if result and object.name != self.obj.name:

            #Rendering
            self.intersection_point = location

            self.obj.rotation_euler.zero()

            up = Vector((0, 0, 1))
            angle = normal.rotation_difference(up)
            angle.invert()
            rot = angle.to_euler()

            self.obj.rotation_euler = rot

            #Set obj location
            self.obj.location = location

        self.obj.hide_set(False)


class Behavior_Controller():


    def __init__(self, context, event, logic_state):

        self.vanilla_behavior = Vanilla_Behavior(context)
        self.radial_behavior = Radial_Behavior(context)
        self.twist_behavior = Twist_Behavior(context)
        #self.update(context, event, logic_state)


    def update(self, context, event, logic_state):

        if logic_state == Logic_States.VANILLA_ARRAY:
            self.vanilla_behavior.update(event)

            self.vanilla_behavior.run_setup = False
            self.radial_behavior.run_setup = True
            self.twist_behavior.run_setup = True

        if logic_state == Logic_States.RADIAL_ARRAY:
            self.radial_behavior.update(event)

            self.vanilla_behavior.run_setup = True
            self.radial_behavior.run_setup = False
            self.twist_behavior.run_setup = True

        if logic_state == Logic_States.TWIST_ARRAY:
            self.twist_behavior.update(event)

            self.vanilla_behavior.run_setup = True
            self.radial_behavior.run_setup = True
            self.twist_behavior.run_setup = False


class HOPS_OT_SuperArray(bpy.types.Operator):

    """Multi Array - V1"""
    bl_idname = "hops.super_array"
    bl_label = "Multi Tool Array"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = """Array V1
Standard, Radial, Twist 360, all in one.

LMB   - Adjust / Create Array
CTRL  - Adjust / Create Radial Array
Shift - Adjust / Create Twist 360 Array

Opt In available for Array V2 via hops dropdown
"""

    def __init__(self):

        # Widget UI
        self.intersection_draw_handle = None

        # Modal UI
        self.master = None

        # Positional Data
        self.start_mouse_position = (0,0)

        # States Data
        self.current_axis = Axis.X

        # Behavior Controller
        self.controller = None

        # For Cancel
        self.start_mods = []

        # For finish
        self.finish_trigger = False
        self.completed = False

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)


    def invoke(self, context, event):

        #Get the start dims
        mod_visible = []
        self.start_mods = context.active_object.modifiers[:]

        for mod in self.start_mods:
            mod_visible.append(mod.show_viewport)
            mod.show_viewport = False

        bpy.context.view_layer.update()
        props.start_dims_magnitude = context.active_object.dimensions.to_2d().magnitude

        for i in range(len(self.start_mods)):
            context.active_object.modifiers[i].show_viewport = mod_visible[i]

        if event.ctrl == True:
            props.logic_state = Logic_States.RADIAL_ARRAY
        elif event.shift == True:
            props.logic_state = Logic_States.TWIST_ARRAY
        else:
            props.logic_state = Logic_States.VANILLA_ARRAY

        self.controller = Behavior_Controller(context, event, props.logic_state)

        props.intersection_point = context.active_object.location

        self.mouse_coords = Vector((event.mouse_region_x, event.mouse_region_y))
        self.obj = context.active_object

        #UI System
        self.master = Master(context=context)
        self.original_tool_shelf, self.original_n_panel = collapse_3D_view_panels()

        self.intersection_draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_intersection, (context,), 'WINDOW', 'POST_VIEW')

        context.window_manager.modal_handler_add(self)

        #Set the current state
        if event.type == "ONE" and event.value == "PRESS":
            props.logic_state = Logic_States.VANILLA_ARRAY
        if event.type == "TWO" and event.value == "PRESS":
            props.logic_state = Logic_States.RADIAL_ARRAY
        if event.type == "THREE" and event.value == "PRESS":
            props.logic_state = Logic_States.TWIST_ARRAY

        return {'RUNNING_MODAL'}


    def modal(self, context, event):

        # Fade effect
        self.master.receive_event(event=event)

        #Set the current state
        if event.type in {'ONE', 'TWO', 'THREE'}:
            if event.type == "ONE" and event.value == "PRESS":
                props.logic_state = Logic_States.VANILLA_ARRAY
            if event.type == "TWO" and event.value == "PRESS":
                props.logic_state = Logic_States.RADIAL_ARRAY
            if event.type == "THREE" and event.value == "PRESS":
                props.logic_state = Logic_States.TWIST_ARRAY

        #Set the current state : To help with people that have numpad emulate on
        if event.type in {'V', 'B', 'N'}:
            if event.type == "V" and event.value == "PRESS":
                props.logic_state = Logic_States.VANILLA_ARRAY
            if event.type == "B" and event.value == "PRESS":
                props.logic_state = Logic_States.RADIAL_ARRAY
            if event.type == "N" and event.value == "PRESS":
                props.logic_state = Logic_States.TWIST_ARRAY

        #Update controller with current state
        self.controller.update(context, event, props.logic_state)

        #Navigation
        if (event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} and event.ctrl != True):

            if not self.master.is_mouse_over_ui():
                return {'PASS_THROUGH'}

        #Confirm
        elif (event.type == 'LEFTMOUSE'):

            if not self.master.is_mouse_over_ui():
                self.remove_intersection()
                self.master.run_fade()
                collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
                return {'FINISHED'}

        #Cancel
        elif (event.type in {'RIGHTMOUSE', 'ESC'}):

            if not self.master.is_mouse_over_ui():
                self.remove_intersection()

                try:
                    self.cancel(context)
                except:
                    print("Error: Could not revert.")

                self.master.run_fade()
                collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
                return {'CANCELLED'}


        self.new_ui(context=context)

        context.area.tag_redraw()

        return {'RUNNING_MODAL'}


    def cancel(self, context):

        keep_mod_names = []

        for mod in self.start_mods:
            keep_mod_names.append(mod.name)

        delete_mods = []

        for i in range(len(context.active_object.modifiers)):
            if context.active_object.modifiers[i].name not in keep_mod_names:
                delete_mods.append(context.active_object.modifiers[i])

        for mod in delete_mods:
            context.active_object.modifiers.remove(mod)


    def toggle_arrays_from_ui(self):

        if props.logic_state == Logic_States.VANILLA_ARRAY:
            props.logic_state = Logic_States.RADIAL_ARRAY

        elif props.logic_state == Logic_States.RADIAL_ARRAY:
            props.logic_state = Logic_States.TWIST_ARRAY

        elif props.logic_state == Logic_States.TWIST_ARRAY:
            props.logic_state = Logic_States.VANILLA_ARRAY


    def new_ui(self, context):

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

            if props.logic_state == Logic_States.VANILLA_ARRAY:

                # Main
                if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1: #Fast Floating
                    win_list.append(self.controller.vanilla_behavior.ui_data["mod_name"])
                    win_list.append(self.controller.vanilla_behavior.ui_data["count"])
                    win_list.append(self.controller.vanilla_behavior.axis.name)
                    win_list.append(self.controller.vanilla_behavior.ui_data["offset_vec"])
                    win_list.append(self.controller.vanilla_behavior.ui_data["mod_offset"])
                else:
                    #win_list.append("Array")
                    win_list.append(self.controller.vanilla_behavior.ui_data["mod_name"])
                    win_list.append(self.controller.vanilla_behavior.ui_data["count"])
                    win_list.append("Standard")
                    win_list.append(self.controller.vanilla_behavior.ui_data["mod_offset"])
                    win_list.append(self.controller.vanilla_behavior.ui_data["offset_vec"])
                    win_list.append(self.controller.vanilla_behavior.axis.name)

                # Help
                help_list.append(["1, 2, 3",           "Numbers across top of keyboard change mode."])
                help_list.append(["V, B, N",           "Change the mode."])
                help_list.append(["Ctrl + Shift",      "Raycast snap to another object"])
                help_list.append(["NUMPAD",            "Set the current offset to the numpad value"])
                help_list.append(["Ctrl + Wheel Down", "Minus the count of the array"])
                help_list.append(["Ctrl + Wheel Up",   "Add to the count of the array"])
                help_list.append(["Numpad +",          "Adjust the offset by + 1"])
                help_list.append(["Numpad -",          "Adjust the offset by - 1"])
                help_list.append(["S",                 "Snap to the cursor"])
                help_list.append(["C",                 "Set array to constant offset"])
                help_list.append(["R",                 "Set array to relative offset"])
                help_list.append(["X",                 "Change the current axis being modified"])
                help_list.append(["Ctrl + X",          "Clear the axis offset"])
                help_list.append(["Alt + A",           "Remove current array"])
                help_list.append(["A",                 "Add additional array"])
                help_list.append(["Q",                 "Cycle active array"])
                help_list.append(["Ctrl + Move",       "Adjust array offset"])
                help_list.append(["M",                 "Toggle mods list."])
                help_list.append(["H",                 "Toggle help."])
                help_list.append(["~",                 "Toggle viewport displays."])
                #help_list.append(["1",                 "To remove, switch to standard and press alt + A"])

                # Mods
                active_mod = self.controller.vanilla_behavior.ui_data["mod_name"]
                mods_list = get_mods_list(mods=bpy.context.active_object.modifiers)

            elif props.logic_state == Logic_States.RADIAL_ARRAY:

                # Main
                if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1: #Fast Floating
                    win_list.append(self.controller.radial_behavior.ui_data["segments"])
                    win_list.append(self.controller.radial_behavior.ui_data["direction"])
                    win_list.append(self.controller.radial_behavior.ui_data["displace"])
                else:
                    win_list.append(self.controller.vanilla_behavior.ui_data["mod_name"])
                    win_list.append(self.controller.radial_behavior.ui_data["segments"])
                    win_list.append("Radial")
                    win_list.append(self.controller.radial_behavior.ui_data["direction"])
                    win_list.append(self.controller.radial_behavior.ui_data["displace"])

                # Help
                help_list.append(["1, 2, 3",          "Numbers across top of keyboard change mode."])
                help_list.append(["V, B, N",          "Change the mode."])
                help_list.append(["Ctrl + MouseWheel", "Adjust the count of the arrays"])
                help_list.append(["Ctrl + MouseMove", "Adjust the offset of array"])
                help_list.append(["Ctrl + Shift",     "Raycast snap to another object"])
                help_list.append(["S",                "Snap to the cursor"])
                help_list.append(["R",                "Change radial to 180/90/45/30"])
                help_list.append(["X",                "Switch offset direction"])
                help_list.append(["Ctrl + Move",      "Adjust displacement offset"])
                help_list.append(["M",                "Toggle mods list."])
                help_list.append(["H",                "Toggle help."])
                help_list.append(["~",                "Toggle viewport displays."])
                help_list.append(["1",                 "To remove, switch to standard and press alt + A"])

                # Mods
                active_mod = self.controller.radial_behavior.ui_data["mod_name"]
                mods_list = get_mods_list(mods=bpy.context.active_object.modifiers)

            elif props.logic_state == Logic_States.TWIST_ARRAY:

                # Main
                if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1: #Fast Floating
                    win_list.append(self.controller.twist_behavior.ui_data["count"])
                    win_list.append(self.controller.twist_behavior.ui_data["axis"])
                    win_list.append(self.controller.twist_behavior.ui_data["offset"])
                    win_list.append(self.controller.twist_behavior.ui_data["angle"])
                else:
                    win_list.append(self.controller.vanilla_behavior.ui_data["mod_name"])
                    win_list.append(self.controller.twist_behavior.ui_data["count"])
                    win_list.append("Twist")
                    win_list.append(self.controller.twist_behavior.ui_data["offset"])
                    win_list.append(self.controller.twist_behavior.ui_data["axis"])
                    win_list.append(self.controller.twist_behavior.ui_data["angle"])

                # Help
                help_list.append(["1, 2, 3",           "Numbers across top of keyboard change mode."])
                help_list.append(["V, B, N",           "Change the mode."])
                help_list.append(["Shift + Alt",       "Adjust the angle of simple deform"])
                help_list.append(["Ctrl + MouseWheel", "Adjust the count of the arrays"])
                help_list.append(["Ctrl + Shift",      "Raycast snap to another object"])
                help_list.append(["Ctrl + MouseMove",  "Adjust the offset of array"])
                help_list.append(["S",                 "Snap to the cursor"])
                help_list.append(["X",                 "Change the current axis being modified"])
                help_list.append(["Ctrl + Move",       "Adjust twist displacement offset"])
                help_list.append(["M",                 "Toggle mods list."])
                help_list.append(["H",                 "Toggle help."])
                help_list.append(["~",                 "Toggle viewport displays."])
                help_list.append(["1",                 "To remove, switch to standard and press alt + A"])

                # Mods
                active_mod = self.controller.twist_behavior.ui_data["mod_name"]
                mods_list = get_mods_list(mods=bpy.context.active_object.modifiers)

            # for mod in reversed(context.active_object.modifiers):
            #     mods_list.append([mod.name, str(mod.type)])

            if props.logic_state == Logic_States.RADIAL_ARRAY:
                self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="ArrayCircle", mods_list=mods_list, active_mod_name=active_mod)
            elif props.logic_state == Logic_States.TWIST_ARRAY:
                self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="ATwist360", mods_list=mods_list, active_mod_name=active_mod)
            else:
                self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="Array", mods_list=mods_list, active_mod_name=active_mod)

        else:

            ########################
            #   Main
            ########################

            main_window = {
                "main_count" : [],
                "header_sub_text" : [],
                "last_col_cell_1" : [],
                "last_col_cell_2" : [],
                "last_col_cell_3" : []
            }

            window_name = ""

            if props.logic_state == Logic_States.VANILLA_ARRAY:
                main_window["main_count"] = [self.controller.vanilla_behavior.ui_data["count"], self.controller.vanilla_behavior.add_count, (1,), (-1,), True]
                #main_window["header_sub_text"] = ["Standard Array", self.toggle_arrays_from_ui]
                main_window["header_sub_text"] = ["Standard Array", self.toggle_arrays_from_ui]

                main_window["last_col_cell_1"] = [self.controller.vanilla_behavior.axis.name, self.controller.vanilla_behavior.cycle_axis]
                main_window["last_col_cell_2"] = [self.controller.vanilla_behavior.ui_data["mod_offset"], self.controller.vanilla_behavior.toggle_offset_type]
                main_window["last_col_cell_3"] = [self.controller.vanilla_behavior.ui_data["offset_vec"], self.controller.vanilla_behavior.add_offset, (.25,), (-.25,), True]

                window_name = "Standard Array"

            elif props.logic_state == Logic_States.RADIAL_ARRAY:
                main_window["main_count"] = [self.controller.radial_behavior.ui_data["segments"], self.controller.radial_behavior.add_count, (1,), (-1,), True]
                main_window["header_sub_text"] = ["Radial Array", self.toggle_arrays_from_ui]
                main_window["last_col_cell_1"] = [self.controller.radial_behavior.ui_data["direction"], self.controller.radial_behavior.switch_axis]
                main_window["last_col_cell_2"] = [self.controller.radial_behavior.ui_data["displace"], self.controller.radial_behavior.add_offset, (1,), (-1,), True]

                window_name = "Radial Array"

            elif props.logic_state == Logic_States.TWIST_ARRAY:
                main_window["main_count"] = [self.controller.twist_behavior.ui_data["count"], self.controller.twist_behavior.add_count, (1,), (-1,), True]
                main_window["header_sub_text"] = ["Twist Array", self.toggle_arrays_from_ui]
                main_window["last_col_cell_1"] = [self.controller.twist_behavior.ui_data["axis"], self.controller.twist_behavior.switch_axis]
                main_window["last_col_cell_2"] = [self.controller.twist_behavior.ui_data["offset"], self.controller.twist_behavior.add_offset, (1,), (-1,), True]
                main_window["last_col_cell_3"] = [self.controller.twist_behavior.ui_data["angle"], self.controller.twist_behavior.add_angle, (15,), (-15,), True]

                window_name = "Twist Array"

            self.master.receive_main(win_dict=main_window, window_name=window_name)


            ########################
            #   Help
            ########################


            hot_keys_dict = {}
            quick_ops_dict = {}

            if props.logic_state == Logic_States.VANILLA_ARRAY:

                hot_keys_dict["V, B, N"] = "Change the mode."
                hot_keys_dict["R"] = ["Set array to relative offset", self.controller.vanilla_behavior.use_relative_offset]
                hot_keys_dict["C"] = ["Set array to constant offset", self.controller.vanilla_behavior.use_constant_offset]
                hot_keys_dict["Ctrl + Shift"] = "Raycast snap to another object"
                hot_keys_dict["Ctrl + Wheel Down"] = ["Minus the count of the array", self.controller.vanilla_behavior.add_count, (-1, )]
                hot_keys_dict["Ctrl + Wheel Up"] = ["Add to the count of the array", self.controller.vanilla_behavior.add_count, (1, )]
                hot_keys_dict["Q"] = ["Cycle active array", self.controller.vanilla_behavior.cycle_active_mod]
                hot_keys_dict["S"] = ["Snap to the cursor", self.controller.vanilla_behavior.snap_to_cursor]
                hot_keys_dict["NUMPAD + CTRL"] = "Set the current offset to the numpad value"
                hot_keys_dict["Numpad +"] = ["Adjust the offset by + 1", self.controller.vanilla_behavior.set_offset, (1, True)]
                hot_keys_dict["Numpad -"] = ["Adjust the offset by - 1", self.controller.vanilla_behavior.set_offset, (-1, True)]
                hot_keys_dict["Ctrl + X"] = ["Clear the axis offset", self.controller.vanilla_behavior.clear_offsset_axis]
                hot_keys_dict["X"] = ["Change the current axis being modified", self.controller.vanilla_behavior.cycle_axis]
                hot_keys_dict["Alt + A"] = ["Remove current array", self.controller.vanilla_behavior.remove_array]
                hot_keys_dict["A"] = ["Add an array", self.controller.vanilla_behavior.add_array_mod]
                hot_keys_dict["1, 2, 3"] = "Numbers across top of keyboard change mode."

            elif props.logic_state == Logic_States.RADIAL_ARRAY:

                hot_keys_dict["1, 2, 3"] = "Numbers across top of keyboard change mode."
                hot_keys_dict["V, B, N"] = "Change the mode."
                hot_keys_dict["Ctrl + MouseWheel"] = ["Adjust the count of the arrays",  self.controller.radial_behavior.add_count, (1,), (-1,)]
                hot_keys_dict["Ctrl + MouseMove"] = ["Adjust the offset of array", self.controller.radial_behavior.add_offset, (1,), (-1,)]
                hot_keys_dict["Ctrl + Shift"] = "Raycast snap to another object"
                hot_keys_dict["S"] = ["Snap to the cursor", self.controller.radial_behavior.snap_to_cursor]
                hot_keys_dict["R"] = ["Change radial to 180/90/45/30", self.controller.radial_behavior.adjust_angle]
                hot_keys_dict["X"] = ["Switch offset direction", self.controller.radial_behavior.switch_axis]

            elif props.logic_state == Logic_States.TWIST_ARRAY:

                hot_keys_dict["1, 2, 3"] = "Numbers across top of keyboard change mode."
                hot_keys_dict["V, B, N"] = "Change the mode."
                hot_keys_dict["Shift + Alt"] = ["Adjust the angle of simple deform", self.controller.twist_behavior.add_angle, (15,), (-15,)]
                hot_keys_dict["Ctrl + MouseWheel"] = ["Adjust the count of the arrays", self.controller.twist_behavior.add_count, (1,), (-1,)]
                hot_keys_dict["Ctrl + Shift"] = "Raycast snap to another object"
                hot_keys_dict["Ctrl + MouseMove"] = ["Adjust the offset of array", self.controller.twist_behavior.add_offset, (1,), (-1,)]
                hot_keys_dict["S"] = ["Snap to the cursor", self.controller.twist_behavior.snap_to_cursor]
                hot_keys_dict["X"] = ["Change the current axis being modified", self.controller.twist_behavior.switch_axis]

            self.master.receive_help(hot_keys_dict=hot_keys_dict, quick_ops_dict={})


            ########################
            #   Mods
            ########################


            win_dict = {}

            for mod in reversed(context.active_object.modifiers):
                win_dict[mod.name] = str(mod.type)

            active_mod = ""
            if props.logic_state == Logic_States.VANILLA_ARRAY:
                active_mod = self.controller.vanilla_behavior.ui_data["mod_name"]

            elif props.logic_state == Logic_States.RADIAL_ARRAY:
                active_mod = self.controller.radial_behavior.ui_data["mod_name"]

            elif props.logic_state == Logic_States.TWIST_ARRAY:
                active_mod = self.controller.twist_behavior.ui_data["mod_name"]

            self.master.receive_mod(win_dict=win_dict, active_mod_name=active_mod)

        # Finished
        self.master.finished()

    #INTERSECTION DRAWING
    def draw_intersection(self, context):

        method_handler(self._draw_intersection,
            arguments = (context, ),
            identifier = 'Array Intersection Shader',
            exit_method = self.remove_intersection)


    def remove_intersection(self):

        if self.intersection_draw_handle:
            self.intersection_draw_handle = bpy.types.SpaceView3D.draw_handler_remove(self.intersection_draw_handle, "WINDOW")


    def _draw_intersection(self, context):

        radius = props.start_dims_magnitude * .5
        if get_preferences().property.array_type == "DOT":
            radius = .0125
            width = 12
        else:
            width = 3
        vertices = []
        indices = []
        segments = 64
        #width = 12
        color = (0,0,0,1)


        #Build ring
        for i in range(segments):
            index = i + 1
            angle = i * 3.14159 * 2 / segments

            x = cos(angle) * radius
            y = sin(angle) * radius
            z = 0
            vert = Vector((x, y, z))

            if props.current_axis == Axis.Z and props.use_radial_widget == False:

                plane_normal = Vector((0,1,0)) @ context.active_object.matrix_local.inverted()
                up = Vector((0,0,1))
                angle = plane_normal.rotation_difference(up)

                rot_mat = angle.to_matrix()

                vert = vert @ rot_mat

            else:

                rot_mat = context.active_object.rotation_euler.to_matrix()
                rot_mat = rot_mat.inverted()
                vert = vert @ rot_mat

            vert[0] = vert[0] + props.intersection_point[0]
            vert[1] = vert[1] + props.intersection_point[1]
            vert[2] = vert[2] + props.intersection_point[2]

            vertices.append(vert)

            if(index == segments):
                indices.append((i, 0))
            else:
                indices.append((i, i + 1))

        if props.use_radial_widget == True:
            color = (1,0,1,1)

        elif props.current_axis == Axis.X:
            color = (1, 0, 0, 1)

        elif props.current_axis == Axis.Y:
            color = (0, 1, 0, 1)

        elif props.current_axis == Axis.Z:
            color = (0, 1, 1, 1)

        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'LINES', {'pos': vertices}, indices=indices)
        shader.bind()

        shader.uniform_float('color', color)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)
        glLineWidth(width)
        batch.draw(shader)

        del shader
        del batch


#HELPER FUNCTIONS
def cycle_axis():

    val = props.current_axis.value

    if(val == 1):
        props.current_axis = Axis.Y
        props.gizmo_normal = (0,0,1)
    elif(val == 2):
        props.current_axis = Axis.Z
        props.gizmo_normal = (0,0,0)
    elif(val == 3):
        props.current_axis = Axis.X
        props.gizmo_normal = (0,0,1)
