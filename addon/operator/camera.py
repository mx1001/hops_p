import bpy
import math
from bpy.types import Operator
from bpy.props import IntProperty, BoolProperty
from bpy.utils import register_class, unregister_class
from math import radians
from ...ui_framework.operator_ui import Master
from ... preferences import get_preferences

class HOPS_OT_camera_rig(Operator):
    bl_idname = 'hops.camera_rig'
    bl_label = 'Camera Rig'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = '''Set up a turntable camera rig

Ctrl + LMB - Don't make the new camera active in the scene
Shift + LMB - Camera bounce alternative (boomerang)
Ctrl + Shift + LMB - Don't enable passepartout on the new camera'''

    rotations: IntProperty(
        name='Rotations',
        description='How many circles the camera should turn',
        min=1,
        soft_max=15,
        default=2)

    make_active: BoolProperty(
        name='Make Active',
        description='Make the new camera the active one in the scene',
        default=True)

    passepartout: BoolProperty(
        name='Passepartout',
        description='Enable passepartout on the camera',
        default=True)

    bounce: BoolProperty(
        name='Bounce',
        description='Enable bounce camera',
        default=False)

    called_ui = False

    def __init__(self):

        HOPS_OT_camera_rig.called_ui = False


    def invoke(self, context, event):
        
        self.view_reset_location = None
        self.bounce = event.shift
        self.make_active = not event.ctrl
        if event.ctrl:
            self.passepartout = not event.shift
        return self.execute(context)


    def draw(self, context):

        self.layout.prop(self, 'rotations')
        row = self.layout.row()

        row.prop(self, 'make_active')
        row.prop(self, 'passepartout')
        row.prop(self, 'bounce')


    def execute(self, context):

        if context.area.type != 'VIEW_3D':
            bpy.ops.hops.display_notification(info="Mouse must be in 3D View")
            return {"FINISHED"}

        # Fix camera align operators
        bpy.ops.view3d.view_persportho()

        # Get camera and set camera settings
        camera = self.get_camera(context)
        self.set_camera_settings(context, camera)

        # Get empty and set the empty settings
        empty = self.get_empty(context, camera)
        self.set_driver(context, empty)

        # Add tracked constraints
        self.set_camera_constraints(camera, empty)

        # Keying
        self.set_marker(context, camera)

        # For view align camera
        if get_preferences().property.to_cam == 'VIEW':
            if self.view_reset_location == None:
                bpy.ops.view3d.camera_to_view()
                self.view_reset_location = (camera.location[0], camera.location[1], camera.location[2])
            else:
                camera.location = self.view_reset_location
                bpy.ops.view3d.view_camera()

        # For center align camera
        else:
            camera.location = (0, -12, 6)
            camera.rotation_euler = (math.radians(90), 0, 0)
            bpy.ops.view3d.view_camera()   
        
        # Operator UI
        self.draw_ui()

        return {"FINISHED"}


    def get_camera(self, context):
        '''Trys to find or create a new camera.'''

        data = bpy.data.cameras.new(name='Hops_Camera_Data')
        camera = bpy.data.objects.new(name='Hops_Camera', object_data=data)
        context.collection.objects.link(camera)
        
        return camera


    def set_camera_settings(self, context, camera):
        '''Setup the camera settings.'''

        # Make camera active
        if self.make_active:
            context.scene.camera = camera

        # Enable passepartout
        if self.passepartout:
            camera.data.passepartout_alpha = 1

        camera.select_set(True)


    def get_empty(self, context, camera):
        '''Looks for the hops camera empty, if not there it will create one.'''

        empty = bpy.data.objects.new(name='Hops_Cam_Empty', object_data=None)
        empty.location = context.scene.cursor.location
        context.collection.objects.link(empty)
        camera.parent = empty
        return empty


    def set_driver(self, context, empty):
        '''Creates and returns the drivers.'''

        driver = empty.driver_add('rotation_euler', 2).driver

        if self.bounce:
            driver.expression = f'cos((frame - frame_start) * (2 * pi) / (1 + frame_end - frame_start)) * {self.rotations}'

        else:
            driver.expression = f'(frame - frame_start) * (2 * pi) / (1 + frame_end - frame_start) * {self.rotations}'

        # create frame start variable
        frame_start = driver.variables.new()
        frame_start.name = 'frame_start'
        frame_start.targets[0].id_type = 'SCENE'
        frame_start.targets[0].id = context.scene
        frame_start.targets[0].data_path = 'frame_start'

        # create frame end variable
        frame_end = driver.variables.new()
        frame_end.name = 'frame_end'
        frame_end.targets[0].id_type = 'SCENE'
        frame_end.targets[0].id = context.scene
        frame_end.targets[0].data_path = 'frame_end'


    def set_marker(self, context, camera):
        '''Place a marker on the timeline.'''

        scene = context.scene
        marker_name = camera.name
        marker = scene.timeline_markers.new(marker_name, frame=context.scene.frame_current)
        marker.camera = camera


    def set_camera_constraints(self, camera, empty):
        '''Setup the camera constraints.'''

        con = camera.constraints.new(type='DAMPED_TRACK')
        con.target = empty
        con.track_axis = 'TRACK_NEGATIVE_Z'

        con = camera.constraints.new(type='TRACK_TO')
        con.target = empty
        con.up_axis = 'UP_Y'
        con.track_axis = 'TRACK_NEGATIVE_Z'


    def draw_ui(self):
        '''Draw the operator UI.'''

        if not HOPS_OT_camera_rig.called_ui:
            HOPS_OT_camera_rig.called_ui = True

            ui = Master()
            word = "Bounce" if self.bounce else "Camera"
            draw_data = [
                [f"{word} Turntable"],
                [" "],
                ["Numpad 0 to jump to Camera "],
                ["F9 to adjust settings "],
                ["Revolutions :" , self.rotations]]

            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)


def register():
    register_class(HOPS_OT_camera_rig)


def unregister():
    unregister_class(HOPS_OT_camera_rig)
