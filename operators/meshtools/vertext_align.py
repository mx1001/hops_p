import bpy, mathutils, math, gpu, bmesh, time
from math import cos, sin, radians
from enum import Enum
from mathutils import Vector, Matrix, Quaternion
from bgl import *
from gpu_extras.batch import batch_for_shader
from bpy_extras import view3d_utils, mesh_utils
from ... preferences import get_preferences
from ... utility.base_modal_controls import Base_Modal_Controls
from ... ui_framework.master import Master
from ... ui_framework.utils.mods_list import get_mods_list
from ... ui_framework.utils.geo import get_blf_text_dims
from ... ui_framework.graphics.draw import render_quad, render_geo, render_text, draw_border_lines, draw_2D_lines
from ... ui_framework.flow_ui.flow import Flow_Menu, Flow_Form
from ... utils.toggle_view3d_panels import collapse_3D_view_panels
from ... utils.modifiers import get_mod_copy, transfer_mod_data
from ... utils.cursor_warp import mouse_warp
from ... utils.modal_frame_drawing import draw_modal_frame
from ... addon.utility import method_handler
from ... addon.utility.screen import dpi_factor

# Selection utils
from ... utils.space_3d import get_3D_point_from_mouse, scene_ray_cast


class Vert_Data:
    def __init__(self):
        self.vert = None                # The bmesh vert
        self.new_co = None              # The point after snapping
        self.old_co = None              # The point before snapping
        self.grab_move_start_pos = None # The point at the start of grab move


class Tool(Enum):
    DRAW = 0
    SNAP = 1
    GRAB = 2


class HOPS_OT_VertextAlign(bpy.types.Operator):
    bl_idname = "hops.vertext_align"
    bl_label = "Vertext Align"
    bl_description = """Quickly align vertices 
    Draw a line from vert to vert snapping others to the line
    Press H for help
    """
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}

    @classmethod
    def poll(cls, context):
        if context.active_object != None:
            if context.active_object.type == 'MESH':
                return True
        return False


    def invoke(self, context, event):

        # Ensure data will be fresh : Solves some unusual problems
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Tool state
        self.tool = Tool.DRAW

        # Starting Data
        self.obj = context.active_object
        self.mesh = self.obj.data
        self.revert_mesh_backup = self.mesh.copy()
        self.mesh_lookup_key = f'HOPSBACKUP {time.time()}'
        self.revert_mesh_backup.name = self.mesh_lookup_key

        # Bmesh
        self.bm = bmesh.from_edit_mesh(self.mesh)
        bpy.ops.mesh.select_mode(use_extend=False, type="VERT")

        # Screen
        self.region = bpy.context.region
        self.rv3d = bpy.context.space_data.region_3d

        # Controls
        self.mouse_pos = (event.mouse_region_x, event.mouse_region_y)
        self.left_click_down = False
        self.mouse_accumulation = 0

        # Tools
        self.setup_tool_data()

        # Intial start
        if self.initial_is_grab() == True:
            self.tool = Tool.GRAB
            self.ensure_selection_change()

        # Flow menu
        self.flow = Flow_Menu()
        self.setup_flow_menu()

        # Base Systems
        self.master = Master(context=context)
        self.master.only_use_fast_ui = True
        self.base_controls = Base_Modal_Controls(context, event)
        self.original_tool_shelf, self.original_n_panel = collapse_3D_view_panels()
        self.draw_handle_2D = bpy.types.SpaceView3D.draw_handler_add(self.safe_draw_2D, (context,), 'WINDOW', 'POST_PIXEL')
        self.draw_handle_3D = bpy.types.SpaceView3D.draw_handler_add(self.safe_draw_3D, (context,), 'WINDOW', 'POST_VIEW')
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}


    def setup_tool_data(self):
        '''Init all the tool data'''

        # LOCK
        self.tool_lock = False

        # DRAW
        self.draw_first_vert = None
        self.draw_second_vert = None
        self.draw_first_vert_pos = None
        self.draw_second_vert_pos = None

        # SNAP
        self.snapped_points = []
        self.select_radius = 15

        # GRAB
        self.grab_center_point = None
        self.grab_moving = False
        self.grab_warping = False
        self.grab_v_arcing = False
        self.grab_intersection = None
        self.grab_curve_points = []
        self.grab_normal_quat = Quaternion()


    def initial_is_grab(self):
        '''Try to use the start selection.'''

        # Initial verts
        verts = [v for v in self.bm.verts if v.select == True]

        # Validate verts
        if len(verts) < 3:
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.hops.display_notification(info="Select 3 or more verts for initial setup.")
            return False

        # 1) Get the vert that is the farthest away from all other verts on avg
        largest = None
        for vert in verts:
            
            dist = None
            farthest_vert = None
            for other in verts:
                if vert == other:
                    continue

                if dist == None:
                    dist = (other.co - vert.co).magnitude
                    farthest_vert = other

                else:
                    if (other.co - vert.co).magnitude > dist:
                        dist = (other.co - vert.co).magnitude
                        farthest_vert = other

            if largest == None:
                largest = dist
                self.draw_first_vert = vert

            else:
                if dist > largest:
                    largest = dist
                    self.draw_first_vert = vert

        # 2) Get the vert farthest away from the first draw vert
        dist = None
        for vert in verts:
            if vert == self.draw_first_vert:
                continue

            if dist == None:
                dist = (vert.co - self.draw_first_vert.co).magnitude
                self.draw_second_vert = vert
            
            else:
                if (vert.co - self.draw_first_vert.co).magnitude > dist:
                    dist = (vert.co - self.draw_first_vert.co).magnitude
                    self.draw_second_vert = vert

        # 3) Setup snap points
        next_vert = self.draw_first_vert
        for vert in verts:
            if vert == self.draw_first_vert or vert == self.draw_second_vert:
                continue
            
            # Keep getting the next closest available vert
            dist = None
            closest = None
            for other in verts:
                if other == self.draw_first_vert or other == self.draw_second_vert:
                    continue
                con = False
                for saved in self.snapped_points:
                    if other == saved.vert:
                        con = True
                if con:
                    continue

                if dist == None:
                    dist = (other.co - next_vert.co).magnitude
                    closest = other
                else:
                    if (other.co - next_vert.co).magnitude < dist:
                        dist = (other.co - next_vert.co).magnitude
                        closest = other

            next_vert = closest

            v_data = Vert_Data()
            v_data.vert = closest
            v_data.new_co = closest.co.copy()
            v_data.old_co = closest.co.copy()

            self.snapped_points.append(v_data)

        # 4) Snap verts
        for v_data in self.snapped_points:
            vert = v_data.vert

            # Get the closest point to the edge and a percent from the first vert to the point
            point, percent = mathutils.geometry.intersect_point_line(vert.co, self.draw_first_vert.co, self.draw_second_vert.co)
            
            # Validate
            if math.isnan(percent):
                percent = 100

            # Clamp position of vert
            if percent > 100:
                point = self.draw_second_vert.co
            elif percent < 0:
                point = self.draw_first_vert.co

            v_data.vert.co = point

        # 5) Setup drawing points
        self.draw_first_vert_pos = self.obj.matrix_world @ self.draw_first_vert.co
        self.draw_first_vert_pos = (self.draw_first_vert_pos[0], self.draw_first_vert_pos[1], self.draw_first_vert_pos[2])

        self.draw_second_vert_pos = self.obj.matrix_world @ self.draw_second_vert.co
        self.draw_second_vert_pos = (self.draw_second_vert_pos[0], self.draw_second_vert_pos[1], self.draw_second_vert_pos[2])

        return True


    def setup_flow_menu(self):
        '''Setup flow menu system.'''

        flow_data = [
            Flow_Form(text="TOOLS", font_size=18, tip_box="Pick a tool;TIP: Cant switch during a move operation"),
            Flow_Form(text="DRAW",  font_size=14, func=self.flow_func, pos_args=(Tool.DRAW,  ), tip_box="Draw tool;Use this tool to draw a line between two verts;Once you have the line drawn you can switch to snap tool"),
            Flow_Form(text="SNAP",  font_size=14, func=self.flow_func, pos_args=(Tool.SNAP,)  , tip_box="Snap tool;Use this tool to snap verts to your line;If there is no line drawn you cant enter this mode"),
            Flow_Form(text="GRAB",  font_size=14, func=self.flow_func, pos_args=(Tool.GRAB, ) , tip_box="Grab tool;Use this tool to move the verts;Click drag to move and Shift Click drag to curve drag")
        ]
        self.flow.setup_flow_data(flow_data)


    def flow_func(self, tool):
        '''Func to switch tools from flow menu.'''

        if self.tool_lock == False:
            self.tool = tool
            self.ensure_selection_change()
        else:
            bpy.ops.hops.display_notification(info="Cancel locked state first")


    def modal(self, context, event):

        # Base Systems
        self.mouse_pos = (event.mouse_region_x, event.mouse_region_y)
        self.master.receive_event(event=event)
        self.base_controls.update(context, event)
        self.flow.run_updates(context, event)

        # Click down
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self.left_click_down = True
        elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            self.left_click_down = False

        #######################
        #   Base Controls
        #######################

        # Navigation
        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        # Cancel
        elif self.base_controls.cancel:
            self.cancelled_exit()
            return {'CANCELLED'}

        # Aligns
        self.view_aligns(event)

        # Confirm exit
        if event.type in {'RET', 'SPACE'}:
            if self.flow.is_open == False:
                self.confirmed_exit()
                return {'FINISHED'}

        # Toggle perspective
        if event.type == 'P' or event.type == 'NUMPAD_5':
            if event.value == 'PRESS':
                bpy.ops.view3d.view_persportho()

        # Toggle viewport Wireframe / Solid
        elif event.type == "Z" and event.value == "PRESS":
            if context.space_data.shading.type == 'SOLID':
                context.space_data.shading.type = 'WIREFRAME'
            elif context.space_data.shading.type == 'WIREFRAME':
                context.space_data.shading.type = 'SOLID'
            else:
                context.space_data.shading.type = 'WIREFRAME'

        # Check for tool switch
        if self.tool_lock == False:
            self.tool_switcher(context, event)

        # Update tools
        if event.type != 'TIMER':
            if self.flow.is_open == False:
                method_handler(self.update_tools,
                    arguments = (context, event),
                    identifier = 'Tools Update',
                    exit_method = self.remove_shaders)

        # Bmesh update
        bmesh.update_edit_mesh(self.mesh, loop_triangles=True)
        self.mesh.calc_loop_triangles()
        self.draw_master(context=context)
        return {"RUNNING_MODAL"}


    def tool_switcher(self, context, event):
        '''Check for tool switches.'''

        # DRAW
        if event.type == 'D' and event.value == "PRESS":
            self.tool = Tool.DRAW
            self.ensure_selection_change()

        # SNAP
        elif event.type == 'S' and event.value == "PRESS":
            self.tool = Tool.SNAP
            self.ensure_selection_change()

        # GRAB
        elif event.type == 'G' and event.value == "PRESS":
            self.tool = Tool.GRAB
            self.ensure_selection_change()


    def view_aligns(self, event):

        # 1
        if event.type in {'ONE', 'NUMPAD_1'} and event.value == "PRESS":
            bpy.ops.view3d.view_axis(type='FRONT')

        # 2
        elif event.type in {'TWO', 'NUMPAD_2'} and event.value == "PRESS":
            bpy.ops.view3d.view_orbit(angle=radians(15), type='ORBITDOWN')

        # 3
        elif event.type in {'THREE', 'NUMPAD_3'} and event.value == "PRESS":
            bpy.ops.view3d.view_axis(type='RIGHT')

        # 4
        elif event.type in {'FOUR', 'NUMPAD_4'} and event.value == "PRESS":
            bpy.ops.view3d.view_orbit(angle=radians(15), type='ORBITLEFT')

        # 6
        elif event.type in {'SIX', 'NUMPAD_6'} and event.value == "PRESS":
            bpy.ops.view3d.view_orbit(angle=radians(15), type='ORBITRIGHT')

        # 7
        elif event.type in {'SEVEN', 'NUMPAD_7'} and event.value == "PRESS":
            bpy.ops.view3d.view_axis(type='TOP')

        # 8
        elif event.type in {'EIGHT', 'NUMPAD_8'} and event.value == "PRESS":
            bpy.ops.view3d.view_orbit(angle=radians(15), type='ORBITUP')

        # 9
        elif event.type in {'NINE', 'NUMPAD_9'} and event.value == "PRESS":
            bpy.ops.view3d.view_orbit(angle=radians(180), type='ORBITRIGHT')


    def draw_master(self, context):

        self.master.setup()
        if self.master.should_build_fast_ui():
            win_list = []
            help_list = []
            mods_list = []
            active_mod = ""

            # Main / Help
            if self.tool == Tool.DRAW:
                # WIN
                win_list.append("TOOL: DRAW")
                # HELP
                help_list.append(["Click", "Select (Pick 2 verts)"])
                help_list.append(["", "________DRAW________"])

            if self.tool == Tool.SNAP:
                # WIN
                win_list.append("TOOL: SNAP")
                # HELP
                help_list.append(["E",             "Equalize vert distances"])
                help_list.append(["Click",         "Select and snap"])
                help_list.append(["Shift + Click", "Deselect verts revert snap"])
                help_list.append(["", "________SNAP________"])

            if self.tool == Tool.GRAB:
                # WIN
                win_list.append("TOOL: GRAB")
                # HELP
                help_list.append(["Scroll",         "Shift verts (left/right)"])
                help_list.append(["Shift + Scroll", "Scale verts along line (up/down)"])
                help_list.append(["E",              "Equalize vert distances"])
                help_list.append(["Alt Click",      "Move drag verts (V ARC)"])
                help_list.append(["Shift Click",    "Move drag verts (CURVE)"])
                help_list.append(["Click",          "Move drag verts (LINEAR)"])
                help_list.append(["", "________GRAB________"])

            # Base Help
            help_list.append(["D",         "DRAW"])
            help_list.append(["S",         "SNAP"])
            help_list.append(["G",         "GRAB"])

            help_list.append(["", "________SWITCH________"])

            help_list.append(["1-9",   "Adjust the view alignment"])
            help_list.append(["Z",     "Wire frame"])
            help_list.append(["M",     "Toggle mods list"])
            help_list.append(["H",     "Toggle help"])
            help_list.append(["~",     "Toggle UI Display Type"])
            help_list.append(["O",     "Toggle viewport rendering"])
            help_list.append(["P / 5", "Toggle Perspective"])

            help_list.append(["", "________GLOBAL________"])

            # Mods
            mods_list = get_mods_list(mods=self.obj.modifiers)

            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="logo_blue", mods_list=mods_list)
        self.master.finished()

    ####################################################
    #   EXIT
    ####################################################

    def cancelled_exit(self):
        '''Revert the bmesh.'''

        # Flow system
        self.flow.shut_down()
        # Close out shaders and ui
        self.remove_shaders()
        self.master.run_fade()
        # Delect all the current geo
        bmesh.ops.delete(self.bm, geom=self.bm.verts, context='VERTS')
        # Load the revert mesh into the bmesh
        self.bm.from_mesh(self.revert_mesh_backup)
        # Update the bmesh into the starting mesh
        bmesh.update_edit_mesh(self.mesh)
        # Remove the backup revert mesh
        bpy.data.meshes.remove(self.revert_mesh_backup)
        # Set the cursor back
        bpy.context.window.cursor_set("CROSSHAIR")
        # Set the tool panels back
        collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)


    def confirmed_exit(self):
        '''Remove backup data.'''

        # Flow system
        self.flow.shut_down()
        # Close out shaders and ui
        self.remove_shaders()
        self.master.run_fade()
        # Remove the mesh backup
        bpy.data.meshes.remove(self.revert_mesh_backup)
        # Set the cursor back
        bpy.context.window.cursor_set("CROSSHAIR")
        # Set the tool panels back
        collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)

    ####################################################
    #   TOOLS
    ####################################################

    def update_tools(self, context, event):
        '''Do tool actions.'''

        # DRAW
        if self.tool == Tool.DRAW:
            self.draw_tool(context, event)

        # SNAP
        elif self.tool == Tool.SNAP:
            self.snap_tool(context, event)

        # GRAB
        elif self.tool == Tool.GRAB:
            self.grab_tool(context, event)

                
    def draw_tool(self, context, event):
        '''Keep the mesh updated.'''

        # Select vert
        if event.type == 'LEFTMOUSE' and event.value == "PRESS":

            # Reset
            if self.draw_first_vert != None and self.draw_second_vert != None:
                self.draw_first_vert = None
                self.draw_second_vert = None
                self.draw_first_vert_pos = None
                self.draw_second_vert_pos = None

            # Get first vert
            if self.draw_first_vert == None:
                vert = self.get_vert_under_mouse(context, event)
                if vert != None:
                    self.draw_first_vert = vert
                    self.draw_first_vert_pos = self.obj.matrix_world @ vert.co
                    self.draw_first_vert_pos = (self.draw_first_vert_pos[0], self.draw_first_vert_pos[1], self.draw_first_vert_pos[2])

            # Get second vert
            elif self.draw_second_vert == None:
                vert = self.get_vert_under_mouse(context, event)
                if vert != self.draw_first_vert:
                    if vert != None:
                        self.draw_second_vert = vert
                        self.draw_second_vert_pos = self.obj.matrix_world @ vert.co
                        self.draw_second_vert_pos = (self.draw_second_vert_pos[0], self.draw_second_vert_pos[1], self.draw_second_vert_pos[2])


    def snap_tool(self, context, event):
        '''Spin the edges under the click.'''

        # Clean selection
        bpy.ops.mesh.select_all(action='DESELECT')

        # Equalize 
        if event.type == 'E' and event.value == "PRESS":
            self.equalize_vert_spacing()

        # Increse / Decrease brush size
        if self.base_controls.scroll:
            if self.base_controls.scroll > 0:
                if self.select_radius + 5 < context.area.width * .25:
                    self.select_radius += 5
            if self.base_controls.scroll < 0:
                if self.select_radius - 5 > 5:
                    self.select_radius -= 5

        # Snap vert
        if self.left_click_down:

            # Snap back
            snap_back_to_original = False
            if event.shift == True:
                snap_back_to_original = True

            bpy.ops.view3d.select_circle(
                x=self.mouse_pos[0],
                y=self.mouse_pos[1],
                radius=self.select_radius,
                wait_for_input=True,
                mode='ADD')
            
            # Selected verts
            verts = [v for v in self.bm.verts if v.select == True]

            if len(verts) == 0:
                return

            # Clean selection
            bpy.ops.mesh.select_all(action='DESELECT')

            # Move back old verts
            if snap_back_to_original == True:
                # Check if the selected verts are in the v_data
                for vert in verts:
                    for v_data in self.snapped_points:
                        if v_data.vert == vert:
                            vert.co = v_data.old_co
                            self.snapped_points.remove(v_data)
                            break
                        
            # Add / move new verts
            elif snap_back_to_original == False:
                for vert in verts:
                    if vert != self.draw_first_vert:
                        if vert != self.draw_second_vert:

                            # Get the closest point to the edge and a percent from the first vert to the point
                            point, percent = mathutils.geometry.intersect_point_line(vert.co, self.draw_first_vert.co, self.draw_second_vert.co)
                            
                            # Validate
                            if math.isnan(percent):
                                continue

                            # Clamp position of vert
                            if percent > 100:
                                point = self.draw_second_vert.co
                            elif percent < 0:
                                point = self.draw_first_vert.co

                            # Check if the vert has already been saved before
                            already_stored = False
                            for v_data in self.snapped_points:
                                if v_data.vert == vert:
                                    already_stored = True
                                    # Assign new pos
                                    vert.co = point

                            # Save the verts
                            if already_stored == False:    
                                v_data = Vert_Data()
                                v_data.vert = vert
                                v_data.new_co = point
                                v_data.old_co = vert.co.copy()
                                # Assign new pos
                                vert.co = point
                                self.snapped_points.append(v_data)


    def grab_tool(self, context, event):
        '''Merge the verts under the circle.'''

        # Validate
        if self.draw_first_vert == None and self.draw_second_vert == None:
            self.tool = Tool.DRAW
            self.tool_lock = False
            self.grab_warping = False
            self.grab_moving = False
            self.grab_v_arcing = False
            self.ensure_selection_change()
            self.grab_intersection = None
            return
        if len(self.snapped_points) < 1:
            self.tool = Tool.SNAP
            self.tool_lock = False
            self.grab_warping = False
            self.grab_moving = False
            self.grab_v_arcing = False
            self.ensure_selection_change()
            self.grab_intersection = None
            return

        # Get half the distance from first vert to second vert
        self.grab_center_point = self.draw_first_vert.co.lerp(self.draw_second_vert.co, .5)
        self.grab_center_point = self.obj.matrix_world @ self.grab_center_point

        # Equalize 
        if event.type == 'E' and event.value == "PRESS":
            self.equalize_vert_spacing()

        # Scroll points mods
        if self.base_controls.scroll:
            
            # Shift left right
            if event.shift == False:
                direction = self.draw_first_vert.co - self.draw_second_vert.co
                direction.normalize()
                direction *= .0625
                if self.base_controls.scroll > 0:
                    self.draw_first_vert.co += direction
                    self.draw_second_vert.co += direction
                    for v_data in self.snapped_points:
                        v_data.vert.co += direction
                elif self.base_controls.scroll < 0:
                    self.draw_first_vert.co -= direction
                    self.draw_second_vert.co -= direction
                    for v_data in self.snapped_points:
                        v_data.vert.co -= direction

            # Scale verts
            elif event.shift == True:
                direction = self.draw_first_vert.co - self.draw_second_vert.co
                direction.normalize()
                direction *= .0625

                if self.base_controls.scroll > 0:
                    self.draw_first_vert.co += direction
                    self.draw_second_vert.co -= direction

                elif self.base_controls.scroll < 0:
                    if (self.draw_first_vert.co - self.draw_second_vert.co).magnitude < .2:
                        return
                    self.draw_first_vert.co -= direction
                    self.draw_second_vert.co += direction

                self.equalize_vert_spacing()

            # Reset drawing points
            self.draw_first_vert_pos = self.obj.matrix_world @ self.draw_first_vert.co
            self.draw_first_vert_pos = (self.draw_first_vert_pos[0], self.draw_first_vert_pos[1], self.draw_first_vert_pos[2])
            self.draw_second_vert_pos = self.obj.matrix_world @ self.draw_second_vert.co
            self.draw_second_vert_pos = (self.draw_second_vert_pos[0], self.draw_second_vert_pos[1], self.draw_second_vert_pos[2])

        # LOCKED : move
        if self.grab_moving == True:
            
            # View normal
            view_quat = context.region_data.view_rotation
            up = Vector((0,0,1))
            view_normal = view_quat @ up

            # Get ray point
            self.grab_intersection = get_3D_point_from_mouse(
                mouse_pos=self.mouse_pos,
                context=context,
                point=self.grab_center_point,
                normal=view_normal)
            
            # Move point
            for v_data in self.snapped_points:
                offset_vec = self.grab_intersection - self.grab_center_point
                quat = self.obj.matrix_world.to_quaternion()
                quat = quat.inverted()
                offset_vec = quat @ offset_vec

                v_data.vert.co = Vector(v_data.grab_move_start_pos) + offset_vec

            # Finished
            if self.left_click_down == False:
                self.grab_moving = False
                self.tool_lock = False
                self.grab_intersection = None

            return

        # LOCKED : warp
        elif self.grab_warping == True:

            # View normal
            view_quat = context.region_data.view_rotation
            up = Vector((0,0,1))
            view_normal = view_quat @ up

            # Get ray point
            self.grab_intersection = get_3D_point_from_mouse(
                mouse_pos=self.mouse_pos,
                context=context,
                point=self.grab_center_point,
                normal=view_normal)

            self.grab_intersection = self.obj.matrix_world.inverted() @ self.grab_intersection

            # Set the points back to
            for v_data in self.snapped_points:
                v_data.vert.co = v_data.new_co

            # Bezier segments
            resolution = len(self.snapped_points) + 1

            # Get points from bezier
            points = mathutils.geometry.interpolate_bezier(
                self.draw_first_vert.co,
                self.grab_intersection.lerp(self.draw_first_vert.co, .5),
                self.grab_intersection.lerp(self.draw_second_vert.co, .5),
                self.draw_second_vert.co,
                resolution)

            # Reverse list if selection is backwards
            a_dist = self.draw_first_vert.co - self.snapped_points[0].vert.co
            b_dist = self.draw_first_vert.co - self.snapped_points[-1].vert.co
            if a_dist.magnitude > b_dist.magnitude:
                self.snapped_points.reverse()

            # Get points for drawing
            self.grab_intersection = self.obj.matrix_world @ self.grab_intersection
            self.grab_curve_points = []
            for point in points:
                point = self.obj.matrix_world @ point
                self.grab_curve_points.append((point[0], point[1], point[2]))
            extra = self.obj.matrix_world @ self.draw_second_vert.co
            self.grab_curve_points.append( (extra[0],extra[1],extra[2] ))

            # Go through all the points for each v_data and assign the closest point
            for index, v_data in enumerate(self.snapped_points):
                point_1 = points[index]
                point_2 = points[index + 1]
                new_loc = point_1.lerp(point_2, .5)
                v_data.vert.co = new_loc

            # Finished
            if self.left_click_down == False:
                self.grab_warping = False
                self.tool_lock = False
                self.grab_intersection = None

            return

        # LOCKED : v arc
        elif self.grab_v_arcing == True:

            # View normal
            view_quat = context.region_data.view_rotation
            up = Vector((0,0,1))
            view_normal = view_quat @ up

            # Get ray point
            self.grab_intersection = get_3D_point_from_mouse(
                mouse_pos=self.mouse_pos,
                context=context,
                point=self.grab_center_point,
                normal=view_normal)
            self.grab_intersection = self.obj.matrix_world.inverted() @ self.grab_intersection

            # For drawing
            self.grab_curve_points = [
                self.draw_first_vert_pos,
                self.grab_intersection,
                self.draw_second_vert_pos]

            # Snap only one vert
            if len(self.snapped_points) == 1:
                self.snapped_points[0].vert.co = self.grab_intersection

            # Snap multi verts
            elif len(self.snapped_points) > 1:

                # Reverse list if selection is backwards
                a_dist = self.draw_first_vert.co - self.snapped_points[0].vert.co
                b_dist = self.draw_first_vert.co - self.snapped_points[-1].vert.co
                if a_dist.magnitude > b_dist.magnitude:
                    self.snapped_points.reverse()

                center_index = int(len(self.snapped_points) / 2)

                a_count = center_index + 1
                b_count = len(self.snapped_points) - center_index

                a_percent = 1 / a_count
                b_percent = 1 / b_count

                a_accumulation = a_percent
                b_accumulation = b_percent

                # Make lines to mouse
                for index, v_data in enumerate(self.snapped_points):
                    # Center vert
                    if index == center_index:
                        v_data.vert.co = self.grab_intersection
                  
                    # a side
                    elif index < center_index:
                        v_data.vert.co = self.draw_first_vert.co.lerp(self.grab_intersection, a_accumulation)
                        a_accumulation += a_percent
                    
                    # b side
                    elif index > center_index:
                        v_data.vert.co = self.grab_intersection.lerp(self.draw_second_vert.co, b_accumulation)
                        b_accumulation += b_percent

            # Get points for drawing
            self.grab_intersection = self.obj.matrix_world @ self.grab_intersection

            # Finished
            if self.left_click_down == False:
                self.grab_v_arcing = False
                self.tool_lock = False
                self.grab_intersection = None

            return

        # Setup grab locks
        if self.left_click_down:

            # Move verts
            if event.shift == False and event.ctrl == False:
                self.grab_moving = True
                self.tool_lock = True

                # Save initial start pos
                for v_data in self.snapped_points:
                    if v_data.grab_move_start_pos == None:
                        v_data.grab_move_start_pos = (v_data.vert.co[0], v_data.vert.co[1], v_data.vert.co[2])

            # Warp verts
            elif event.shift == True and event.ctrl == False:
                if len(self.snapped_points) > 2:
                    self.grab_warping = True
                    self.tool_lock = True
                    bpy.ops.hops.display_notification(info="TIP: Selection order matters")
                else:
                    bpy.ops.hops.display_notification(info="Needs 3 or more verts for curve deform")

            # V arc move
            elif event.ctrl == True:
                if len(self.snapped_points) < 3:
                    bpy.ops.hops.display_notification(info="Needs 3 or more verts for V align arc")
                    return
                self.tool_lock = True
                self.grab_v_arcing = True

    ####################################################
    #   UTILS
    ####################################################

    def raycast_onto_object(self, context, event):
        '''Raycast into scene and only return if hit active object. Returns dictionary'''

        ray_data = {
            'result' : None,
            'location' : None,
            'normal' : None,
            'index' : None,
            'object' : None,
            'matrix' : None}

        result, location, normal, index, object, matrix = scene_ray_cast(context, event)

        if object == self.obj:
            ray_data['result'] = result
            ray_data['location'] = location
            ray_data['normal'] = normal
            ray_data['index'] = index
            ray_data['object'] = object
            ray_data['matrix'] = matrix

        return ray_data


    def get_2d_point_from_3d(self, point3d):
        '''Get 2D Screen point from mouse.'''

        if self.rv3d is not None and self.region is not None:
            return view3d_utils.location_3d_to_region_2d(self.region, self.rv3d, point3d)


    def get_vert_under_mouse(self, context, event):
        '''Get the closest vert to the mouse point.'''

        ray_data = self.raycast_onto_object(context, event)
        if ray_data['result'] == None:
            # Use circle selection method if ray failed
            origin = view3d_utils.region_2d_to_origin_3d(bpy.context.region, bpy.context.region_data, self.mouse_pos)
            og_verts = [v for v in self.bm.verts if v.select == True]
            bpy.ops.mesh.select_all(action='DESELECT')

            bpy.ops.view3d.select_circle(
                x=self.mouse_pos[0],
                y=self.mouse_pos[1],
                radius=25,
                wait_for_input=True,
                mode='ADD')

            new_verts = [v for v in self.bm.verts if v.select == True]

            closest_vert = None
            dist = None
            for vert in new_verts:
                if closest_vert == None:
                    closest_vert = vert
                    dist = origin - vert.co
                else:
                    if dist > (origin - vert.co):
                        closest_vert = vert
                        dist = origin - vert.co

            bpy.ops.mesh.select_all(action='DESELECT')
            for vert in og_verts:
                vert.select = True

            return closest_vert

        closest_vert = None
        check_distance = -1

        for index, vert in enumerate(self.bm.verts):
            distance = ray_data['location'] - (self.obj.matrix_world @ vert.co)
            distance = abs(distance.magnitude)

            if index == 0:
                closest_vert = vert
                check_distance = distance
                continue

            if distance < check_distance:
                closest_vert = vert
                check_distance = distance

        return closest_vert


    def get_edge_under_mouse(self, context, event, as_copy=False, ret_with_ray_data=False):
        '''Gets edge under the mouse.'''

        ray_data = self.raycast_onto_object(context, event)
        if ray_data['result'] == None:
            if ret_with_ray_data == True:
                return None, None

            return None

        ray_loc = ray_data['location']
        ray_normal = ray_data['normal']

        self.bm.faces.ensure_lookup_table()
        self.bm.edges.ensure_lookup_table()
        self.bm.verts.ensure_lookup_table()
        
        # Get the closest edge
        closest_edge = None
        check_distance = -1
        edges = [e for e in self.bm.edges]
        for index, edge in enumerate(edges):

            # Take ray location and get closest point to edge
            vert_one_loc = self.obj.matrix_world @ edge.verts[0].co
            vert_two_loc = self.obj.matrix_world @ edge.verts[1].co

            # Get the closest point to the edge and a percent from the first vert to the point
            point, percent = mathutils.geometry.intersect_point_line(ray_loc, vert_one_loc, vert_two_loc)

            # Validate
            if math.isnan(percent):
                continue

            # Get distance from point and ray location
            distance = ray_loc - point
            distance = distance.magnitude

            # Save initial edge and distance
            if index == 0:
                closest_edge = edge
                check_distance = distance
                continue
            
            # Edge is not under mouse
            if percent > 1:
                continue
            elif percent < 0:
                continue

            # Check if the next edge is closer to ray poit
            if distance < check_distance:
                closest_edge = edge
                check_distance = distance

        # Return edge
        if as_copy == False:

            # Return edge and ray data
            if ret_with_ray_data == True:
                return closest_edge, ray_data

            # Return edge only
            return closest_edge

        # Return simple data copy version
        else:
            return self.get_edge_copy(closest_edge)


    def get_edge_copy(self, edge):
        '''Return a value copy of the edge and vert locations associated.'''

        class Edge:
            def __init__(self):
                self.verts = []

        copied_edge = Edge()
        for vert in edge.verts:
            pos = self.obj.matrix_world @ vert.co
            copied_edge.verts.append( pos )

        return copied_edge


    def equalize_vert_spacing(self):
        '''Space all the verts evenly.'''
        
        # Validate
        validated = True
        if self.draw_first_vert == None:
            if self.draw_second_vert == None:
                validated = False
        if self.snapped_points == []:
            validated = False
        if validated == False:
            bpy.ops.hops.display_notification(info="Need to snap points first.")
            return
        
        line = self.draw_first_vert.co - self.draw_second_vert.co
    
        if len(self.snapped_points) == 1:
            self.snapped_points[0].vert.co = self.draw_first_vert.co.lerp(self.draw_second_vert.co, .5)

        elif len(self.snapped_points) > 2:

            # Reverse list if selection is backwards
            first_dist = self.draw_first_vert.co - self.snapped_points[0].vert.co
            second_dist = self.draw_first_vert.co - self.snapped_points[-1].vert.co
            if first_dist.magnitude > second_dist.magnitude:
                self.snapped_points.reverse()

            # Equalize
            factor = 1 / (len(self.snapped_points) + 1)
            next_factor = factor
            for v_data in self.snapped_points:
                v_data.vert.co = self.draw_first_vert.co.lerp(self.draw_second_vert.co, next_factor)
                next_factor += factor


    def ensure_selection_change(self):
        '''Make sure the correct selection mode is active.'''

        # DRAW
        if self.tool == Tool.DRAW:
            self.snapped_points = []
            self.grab_center_point = None
            self.draw_first_vert = None
            self.draw_second_vert = None
            self.draw_first_vert_pos = None
            self.draw_second_vert_pos = None

        # SNAP
        elif self.tool == Tool.SNAP:
            if self.draw_first_vert == None or self.draw_second_vert == None:
                self.tool = Tool.DRAW
                self.grab_center_point = None
                bpy.ops.hops.display_notification(info="Could not switch tool: Create a line first in draw tool")
                return

        # GRAB
        elif self.tool == Tool.GRAB:
            if self.draw_first_vert == None or self.draw_second_vert == None:
                self.tool = Tool.DRAW
                bpy.ops.hops.display_notification(info="Could not switch tool: Create a line first in draw tool")
                return
            
        bpy.ops.hops.display_notification(info=f'Switched tool to: {self.tool.name}')

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

        self.flow.draw_2D()

        # DRAW
        if self.tool == Tool.SNAP:
            self.draw_snap_2D(context)

    
    def draw_snap_2D(self, context):
        '''Draw the draw tool.'''

        width=1
        color=(0,0,0,1)
        segments = 64
        vertices = []
        for i in range(segments):
            index = i + 1
            angle = i * 3.14159 * 2 / segments
            x = math.cos(angle) * self.select_radius
            y = math.sin(angle) * self.select_radius
            x += self.mouse_pos[0]
            y += self.mouse_pos[1]
            vertices.append((x, y))

        first_vert = vertices[0]
        vertices.append(first_vert)

        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)
        glLineWidth(width)
        batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": vertices})
        shader.bind()
        shader.uniform_float("color", color)
        batch.draw(shader)
        glDisable(GL_BLEND)

        del shader
        del batch

    # 3D SHADER
    def safe_draw_3D(self, context):
        method_handler(self.draw_shader_3D,
            arguments = (context,),
            identifier = 'Modal Shader 3D',
            exit_method = self.remove_shaders)


    def draw_shader_3D(self, context):
        '''Draw shader handle.'''

        # DRAW
        if self.tool == Tool.DRAW:
            self.draw_draw_tool_3D(context)

        # SNAP
        elif self.tool == Tool.SNAP:
            self.draw_snap_tool_3D(context)

        # GRAB
        elif self.tool == Tool.GRAB:
            self.draw_grab_tool_3D(context)


    def draw_draw_tool_3D(self, context):
        '''Draw the draw tool.'''

        verts = []

        # Get first vert point / draw
        if self.draw_first_vert != None:
            if self.draw_first_vert_pos != None:
                verts.append(self.draw_first_vert_pos)

                shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
                batch = batch_for_shader(shader, 'POINTS', {'pos': [self.draw_first_vert_pos]})
                shader.bind()
                shader.uniform_float('color', (1,0,0,1))
                glEnable(GL_BLEND)
                glPointSize(6)
                batch.draw(shader)
                del shader
                del batch

        # Get second vert point / draw
        if self.draw_second_vert != None:
            if self.draw_second_vert_pos != None:
                verts.append(self.draw_second_vert_pos)

                shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
                batch = batch_for_shader(shader, 'POINTS', {'pos': [self.draw_second_vert_pos]})
                shader.bind()
                shader.uniform_float('color', (1,0,0,1))
                glEnable(GL_BLEND)
                glPointSize(6)
                batch.draw(shader)
                del shader
                del batch

        # Draw line
        if len(verts) == 2:
            indices = [(0,1)]
            shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'LINES', {'pos': verts}, indices=indices)
            shader.bind()
            shader.uniform_float('color', (0,0,0,1))
            glEnable(GL_LINE_SMOOTH)
            glEnable(GL_BLEND)
            glLineWidth(3)
            batch.draw(shader)
            del shader
            del batch


    def draw_snap_tool_3D(self, context, with_snap_line=True):
        '''Draw the snap tool.'''

        # Draw the snap line
        if with_snap_line == True:
            self.draw_draw_tool_3D(context)

        # Draw the active points
        if len(self.snapped_points) > 0:
            for v_data in self.snapped_points:

                vert_co = self.obj.matrix_world @ v_data.vert.co

                shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
                batch = batch_for_shader(shader, 'POINTS', {'pos': [vert_co]})
                shader.bind()
                shader.uniform_float('color', (1,1,0,1))
                glEnable(GL_BLEND)
                glPointSize(6)
                batch.draw(shader)
                del shader
                del batch


    def draw_grab_tool_3D(self, context):
        '''Draw the grab tool.'''

        # Draw the points
        self.draw_snap_tool_3D(context, with_snap_line=False)

        # Draw curve
        if self.grab_warping == True:
            if self.grab_curve_points != []:
                indices = []
                for index, point in enumerate(self.grab_curve_points):
                    if index == len(self.grab_curve_points) - 2:
                        break
                    indices.append((index, index + 1))
                shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
                batch = batch_for_shader(shader, 'LINES', {'pos': self.grab_curve_points}, indices=indices)
                shader.bind()
                shader.uniform_float('color', (0,0,0,1))
                glEnable(GL_LINE_SMOOTH)
                glEnable(GL_BLEND)
                glLineWidth(3)
                batch.draw(shader)
                del shader
                del batch

        # Draw V Arc
        if self.grab_v_arcing == True:
            if self.grab_curve_points != []:
                shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
                batch = batch_for_shader(shader, 'LINES', {'pos': self.grab_curve_points}, indices=[(0,1), (1,2)])
                shader.bind()
                shader.uniform_float('color', (0,0,0,1))
                glEnable(GL_LINE_SMOOTH)
                glEnable(GL_BLEND)
                glLineWidth(3)
                batch.draw(shader)
                del shader
                del batch

        # Draw gizmo dot
        if self.grab_intersection != None:

            # Intersection point
            mouse_dot = (self.grab_intersection[0], self.grab_intersection[1], self.grab_intersection[2])

            # Draw line
            if self.grab_center_point != None:
                verts = [mouse_dot, self.grab_center_point]
                indices = [(0,1)]
                shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
                batch = batch_for_shader(shader, 'LINES', {'pos': verts}, indices=indices)
                shader.bind()
                shader.uniform_float('color', (0,0,0,1))
                glEnable(GL_LINE_SMOOTH)
                glEnable(GL_BLEND)
                glLineWidth(3)
                batch.draw(shader)
                del shader
                del batch

            # Draw dot at mouse
            shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'POINTS', {'pos': [mouse_dot]})
            shader.bind()
            shader.uniform_float('color', (1,0,0,1))
            glEnable(GL_BLEND)
            glPointSize(12)
            batch.draw(shader)
            del shader
            del batch

        # Draw the center dot
        if self.grab_center_point != None:
            shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'POINTS', {'pos': [self.grab_center_point]})
            shader.bind()
            shader.uniform_float('color', (0,1,0,1))
            glEnable(GL_BLEND)
            glPointSize(12)
            batch.draw(shader)
            del shader
            del batch
