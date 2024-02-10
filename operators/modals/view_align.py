import bpy, math, bmesh
from math import cos, sin, pi, radians, degrees
from mathutils import Matrix, Vector, geometry, Quaternion
from ... ui_framework.master import Master
from ... preferences import get_preferences
from ... utility.base_modal_controls import Base_Modal_Controls
from ... utils.toggle_view3d_panels import collapse_3D_view_panels
from ... utils.bmesh import get_verts_center

description = """View Align Modal

Shift + Scroll - Roll View
Ctrl + Scroll - Orbit View

Assists with view alignment
Press H for help

"""

class HOPS_OT_ViewAlign(bpy.types.Operator):

    """View Align"""
    bl_idname = "view3d.view_align"
    bl_label = "View Align"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}
    bl_description = description


    def invoke(self, context, event):

        # Set to ortho
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if hasattr(space, 'region_3d'):
                            space.region_3d.view_perspective = 'ORTHO'
                            break

        # Set initial look to Shift 7
        if context.active_object != None:
            if hasattr(context.active_object, 'mode'):
                if context.active_object.mode != 'OBJECT':
                    bpy.ops.view3d.view_axis(type='TOP', align_active=True, relative=False)

        # Views
        self.v_align_index = 2
        self.views = ['LEFT', 'RIGHT', 'BOTTOM', 'TOP', 'FRONT', 'BACK']

        # Object refs
        self.start_object = context.active_object
        if self.start_object == None:
            if len(context.selected_objects) > 0:
                self.start_object = context.selected_objects[0]

        self.original_selection_set = self.get_original_selection_set(context)
        self.empty_obj_index = 0
        self.empty_objects = [o for o in context.view_layer.objects if o.name[:11] == "Align_Empty" and o.visible_get() == True]

        # WARNING : Make sure to check for None type in this list
        # Putting the start obj in this collection to be scrolled on
        self.empty_objects.append(self.start_object)

        # Props
        self.set_to_top_view = False

        # Base Systems
        self.master = Master(context=context)
        self.master.only_use_fast_ui = True
        self.base_controls = Base_Modal_Controls(context, event)
        self.original_tool_shelf, self.original_n_panel = collapse_3D_view_panels()
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


    def modal(self, context, event):

        self.master.receive_event(event=event)
        self.base_controls.update(context=context, event=event)

        # Snap to empty after switching : this is up top because of update cycle    
        if self.set_to_top_view == True:
            self.set_to_top_view = False
            bpy.ops.view3d.view_axis('INVOKE_DEFAULT', type='TOP', align_active=True, relative=False)
            self.v_align_index = 3

        # Navigation
        if self.base_controls.pass_through:
            if not self.master.is_mouse_over_ui():
                return {'PASS_THROUGH'}

        # Confirm
        elif self.base_controls.confirm:
            if not self.master.is_mouse_over_ui():
                self.master.run_fade()
                collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
                if get_preferences().ui.Hops_extra_info:
                    bpy.ops.hops.display_notification(info=F'Aligned', name="")
                self.select_all_objects(self.original_selection_set)
                return {'FINISHED'}

        # Cancel
        elif self.base_controls.cancel:
            if not self.master.is_mouse_over_ui():
                self.master.run_fade()
                collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
                self.select_all_objects(self.original_selection_set)
                return {'CANCELLED'}

        # Scroll views
        elif self.base_controls.scroll:
            
            # Cycle objects
            if event.ctrl and event.shift:
                if len(self.empty_objects) > 0:
                    self.deselect_all_objects(context)

                    current_obj = self.empty_objects[self.empty_obj_index]

                    if current_obj != None:
                        current_obj.select_set(True)
                        context.view_layer.objects.active = current_obj
                    else:
                        context.view_layer.objects.active = None

                    # Notification
                    if current_obj != None:
                        if hasattr(current_obj, 'name'):
                            bpy.ops.hops.display_notification(info=f"Target : {current_obj.name}")

                    else:
                        bpy.ops.hops.display_notification(info="Target : None")

                    self.empty_obj_index = (self.empty_obj_index + 1) % len(self.empty_objects)
                    context.view_layer.update()
                    self.set_to_top_view = True
                    
            # # Try to switch back to start object
            # else:
            #     if self.start_object != None:
            #         if self.start_object.select_get() == False:
            #             self.deselect_all_objects(context)
            #             self.start_object.select_set(True)
            #             context.view_layer.objects.active = self.start_object

            # Spin
            if event.ctrl:
                if self.base_controls.scroll > 0:
                    bpy.ops.view3d.view_roll(angle=radians(15), type='ANGLE')
                else:
                    bpy.ops.view3d.view_roll(angle=radians(-15), type='ANGLE')

            # Orbit
            elif event.shift:
                if self.base_controls.scroll > 0:
                    bpy.ops.view3d.view_orbit(angle=radians(15), type='ORBITUP')
                else:
                    bpy.ops.view3d.view_orbit(angle=radians(15), type='ORBITDOWN')

            # Z Orbit
            elif event.alt:
                if self.base_controls.scroll > 0:
                    bpy.ops.view3d.view_orbit(angle=radians(15), type='ORBITRIGHT')
                else:
                    bpy.ops.view3d.view_orbit(angle=radians(15), type='ORBITLEFT')

            # Switch
            else:
                self.v_align_index = (self.v_align_index + 1) % len(self.views)
                view = self.views[self.v_align_index]
                bpy.ops.view3d.view_axis(
                    type=view,
                    align_active=True,
                    relative=False)

        # Arrow Keys
        elif event.type == 'RIGHT_ARROW' and event.value == "PRESS":
            bpy.ops.view3d.view_roll(angle=radians(15), type='ANGLE')

        elif event.type == 'LEFT_ARROW' and event.value == "PRESS":
            bpy.ops.view3d.view_roll(angle=radians(-15), type='ANGLE')

        # Toggle perspective
        elif event.type in {'P', 'NUMPAD_5', 'FIVE'}:
            if event.value == 'PRESS':
                bpy.ops.view3d.view_persportho()

        # Drop empty to view
        elif event.type == 'E' and event.value == "PRESS":

            active_obj = context.active_object
            bpy.ops.hops.display_notification(info=F'Empty Added', name="")

            # Get view angle
            view_rot = None
            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    if area.type == 'VIEW_3D':
                        for space in area.spaces:
                            if hasattr(space, 'region_3d'):
                                view_rot = space.region_3d.view_rotation
                                break

            # Failed to get view angle
            if view_rot == None:
                bpy.ops.object.empty_add(
                    type='SINGLE_ARROW',
                    align='VIEW',
                    location=(0, 0, 0),
                    rotation=active_obj.matrix_world.to_translation())

            # Obtained view angle
            else:

                # Create empty
                new_empty = bpy.data.objects.new('Align_Empty', None)
                context.collection.objects.link(new_empty)
                new_empty.empty_display_size = 1
                new_empty.empty_display_type = 'SINGLE_ARROW'
                new_empty.rotation_euler = view_rot.to_euler()

                self.empty_objects.append(new_empty)

                # Add empty at active mesh in edit mode
                if bpy.context.mode != 'OBJECT':
                    if active_obj.type == 'MESH':
                        me = active_obj.data
                        bm = bmesh.from_edit_mesh(me)

                        use_face = False
                        if bm.faces.active != None and bm.select_mode in {'FACE'}:
                            use_face = True

                        # No active face, place at vert avg
                        if use_face == False:
                            verts = [v for v in bm.verts if v.select]
                            loc = get_verts_center(verts)
                            loc = active_obj.matrix_world @ loc
                            new_empty.location = loc

                        # Place at active face center
                        elif use_face == True:
                            face = bm.faces.active
                            loc = face.calc_center_median()
                            loc = active_obj.matrix_world @ loc
                            new_empty.location = loc

                        del bm

                    elif active_obj.type == 'CURVE':

                        if hasattr(active_obj.data.splines.active, 'bezier_points'):
                            for point in active_obj.data.splines.active.bezier_points:
                                if point.select_control_point == True:
                                    loc = point.co
                                    loc = active_obj.matrix_world @ loc
                                    new_empty.location = loc       
                                    break

                # Add empty at object location
                elif bpy.context.mode == 'OBJECT':
                    if active_obj != None:
                        loc = active_obj.matrix_world.to_translation()
                        new_empty.location = loc

        # Toggle viewport display
        elif event.type == 'Z' and event.alt:
            if event.value == "PRESS":
                if hasattr(context.space_data, 'shading'):
                    if context.space_data.shading.type != 'WIREFRAME':
                        context.space_data.shading.type = 'WIREFRAME'
                    else:
                        context.space_data.shading.type = 'SOLID'

        # Set the orientation gizmo to view align
        elif event.type == 'T' and event.value == "PRESS":
            bpy.context.scene.transform_orientation_slots[0].type = 'VIEW'

        #####################
        # Numpad emulation
        #####################

        # 0
        elif event.type in {'ZERO', 'NUMPAD_0'} and event.value == "PRESS":
            bpy.ops.view3d.view_camera()

        # 1
        elif event.type in {'ONE', 'NUMPAD_1'} and event.value == "PRESS":
            if event.shift and event.ctrl:
                bpy.ops.view3d.view_axis(type='BACK', align_active=True, relative=False)
                self.v_align_index = 5
            elif event.shift:
                bpy.ops.view3d.view_axis(type='FRONT', align_active=True, relative=False)
                self.v_align_index = 4
            elif event.alt:
                bpy.ops.view3d.view_axis(type='BACK')
                self.v_align_index = 5
            else:
                bpy.ops.view3d.view_axis(type='FRONT')
                self.v_align_index = 4

        # 2
        elif event.type in {'TWO', 'NUMPAD_2'} and event.value == "PRESS":
            if event.ctrl:
                bpy.ops.view3d.view_pan('INVOKE_DEFAULT', type='PANDOWN')
            else:
                bpy.ops.view3d.view_orbit(angle=radians(15), type='ORBITDOWN')

        # 3
        elif event.type in {'THREE', 'NUMPAD_3'} and event.value == "PRESS":
            if event.shift and event.ctrl:
                bpy.ops.view3d.view_axis(type='LEFT', align_active=True, relative=False)
                self.v_align_index = 0
            elif event.shift:
                bpy.ops.view3d.view_axis(type='RIGHT', align_active=True, relative=False)
                self.v_align_index = 1
            elif event.ctrl:
                bpy.ops.view3d.view_axis(type='LEFT')
                self.v_align_index = 0
            else:
                bpy.ops.view3d.view_axis(type='RIGHT')
                self.v_align_index = 1

        # 4
        elif event.type in {'FOUR', 'NUMPAD_4'} and event.value == "PRESS":
            if event.shift:
                bpy.ops.view3d.view_roll(type='LEFT')
            elif event.ctrl:
                bpy.ops.view3d.view_pan('INVOKE_DEFAULT', type='PANLEFT')
            else:
                bpy.ops.view3d.view_orbit(angle=radians(15), type='ORBITLEFT')

        # 6
        elif event.type in {'SIX', 'NUMPAD_6'} and event.value == "PRESS":
            if event.shift:
                bpy.ops.view3d.view_roll(type='RIGHT')
            elif event.ctrl:
                bpy.ops.view3d.view_pan('INVOKE_DEFAULT', type='PANRIGHT')
            else:
                bpy.ops.view3d.view_orbit(angle=radians(15), type='ORBITRIGHT')

        # 7
        elif event.type in {'SEVEN', 'NUMPAD_7'} and event.value == "PRESS":
            if event.shift and event.ctrl:
                bpy.ops.view3d.view_axis(type='BOTTOM', align_active=True, relative=False)
                self.v_align_index = 2
            elif event.shift:
                bpy.ops.view3d.view_axis(type='TOP', align_active=True, relative=False)
                self.v_align_index = 3
            elif event.ctrl:
                bpy.ops.view3d.view_axis(type='BOTTOM')
                self.v_align_index = 2
            else:
                bpy.ops.view3d.view_axis(type='TOP')
                self.v_align_index = 3

        # 8
        elif event.type in {'EIGHT', 'NUMPAD_8'} and event.value == "PRESS":
            if event.ctrl:
                bpy.ops.view3d.view_pan('INVOKE_DEFAULT', type='PANUP')
            else:
                bpy.ops.view3d.view_orbit(angle=radians(15), type='ORBITUP')

        # 9
        elif event.type in {'NINE', 'NUMPAD_9', 'F'} and event.value == "PRESS":
            bpy.ops.view3d.view_orbit(angle=radians(180), type='ORBITRIGHT')

        # Focus
        elif event.type in {'A', 'PERIOD'} and event.value == "PRESS":
            bpy.ops.view3d.view_selected(use_all_regions=False)
            if get_preferences().ui.Hops_extra_info:
                bpy.ops.hops.display_notification(info=F'Focused On Selected', name="")

        self.build_ui(context=context)

        return {'RUNNING_MODAL'}


    def build_ui(self, context):

        self.master.setup()

        #--- Fast UI ---#
        if self.master.should_build_fast_ui():

            win_list = []
            help_list = []

            # Main
            win_list.append(self.views[self.v_align_index])

            # Help
            help_list.append(["Ctrl + Shift Scroll",  "Cycle Empties"])
            
            help_list.append(["Shift + Scroll", "Roll View"])
            help_list.append(["Ctrl + Scroll",  "Orbit View"])
            help_list.append(["Alt + Scroll",   "Orbit View Z axis"])
            
            help_list.append(["Alt + Z",        "Toggle Seethrough"])
            help_list.append(["5 / P",          "Toggle Ortho"])
            help_list.append(["A / Period",     "Focus On Selected"])
            help_list.append(["E",              "Add empty at location"])
            help_list.append(["Numbers",        "Emulation of numpad"])
            help_list.append(["T",              "Set gizmo to view align"])
            help_list.append(["F",              "Flip View"])
            help_list.append(["H",              "Toggle help"])
            help_list.append(["~",              "Toggle viewport displays"])
            help_list.append(["O",              "Toggle viewport rendering"])
            help_list.append(["Scroll",         "Cycle views"])
            

            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="ArrayCircle")

        self.master.finished()


    def get_original_selection_set(self, context):
        '''Create and return a list of the original objects that where selected.'''

        selection_set = []

        for obj in context.view_layer.objects:
            if obj.select_get() == True:
                selection_set.append(obj)
                if obj != self.start_object:
                    obj.select_set(False)

        return selection_set


    def select_all_objects(self, objects):
        '''Create and return a list of the original objects that where selected.'''

        for obj in objects:
            obj.select_set(True)


    def deselect_all_objects(self, context):
        '''Deselect all objects.'''

        for obj in context.view_layer.objects:
            if obj.select_get() == True:
                obj.select_set(False)