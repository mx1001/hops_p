import bpy, mathutils, math, gpu, bmesh, time
from math import cos, sin
from enum import Enum
from mathutils import Vector, Matrix
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


class Knife_Data:

    def __init__(self):
        self.reset()


    def reset(self):
        self.edge_to_vert_thresh = .1
        self.edge_snap_percent = .25
        self.ray_data = None
        self.gl_point_loc = None

        # Edge snap data
        self.bm_edge = None
        self.start_vert = None
        self.distance_percent = None


    def get_and_gen_bm_vert(self, dont_perform_cut=False):
        '''Generate the and return the bm vert from ray loc.'''
        
        if self.validate_state() == False:
            return None

        if dont_perform_cut == True:
            return self.start_vert

        if self.distance_percent == 0:
            return self.start_vert
        elif self.distance_percent == 1:
            for vert in self.bm_edge.verts:
                if vert != self.start_vert:
                    return vert

        edge, vert = bmesh.utils.edge_split(self.bm_edge, self.start_vert, self.distance_percent)
        self.bm_edge = edge
        self.start_vert = vert
        return vert


    def set_bm_edge(self, bm, edge, obj, ray_data, use_snaps=False):
        '''Set bm edge data for drawing and for edge split loc.'''

        # Assign incoming
        self.bm_edge = edge
        self.ray_data = ray_data

        # Ensure new data
        if self.validate_state() == False:
            self.reset()

        # Ray data
        ray_loc = ray_data['location']
        ray_norm = ray_data['normal']

        # Object world matrix
        world_mat = obj.matrix_world

        # Validate
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()

        # Edge length
        edge_length = self.bm_edge.calc_length()

        # Verts on edge
        vert_one = edge.verts[0]
        vert_two = edge.verts[1]

        # Vert locations
        vert_one_loc = world_mat @ vert_one.co
        vert_two_loc = world_mat @ vert_two.co

        # Vert distances from ray loc
        vert_one_dist = ray_loc - vert_one_loc
        vert_one_dist = abs(vert_one_dist.magnitude)

        vert_two_dist = ray_loc - vert_two_loc
        vert_two_dist = abs(vert_two_dist.magnitude)
        
        # Get closest vert
        shortest_distance = 0
        closest_vert = None
        if vert_one_dist < vert_two_dist:
            shortest_distance = vert_one_dist
            closest_vert = vert_one
            self.gl_point_loc = vert_one_loc
        else:
            shortest_distance = vert_two_dist
            closest_vert = vert_two
            self.gl_point_loc = vert_two_loc

        # Check if we should just use the vert because its inside the thresh
        finished = False
        thresh_length = edge_length * self.edge_to_vert_thresh
        if shortest_distance <= thresh_length:
            self.start_vert = closest_vert
            self.distance_percent = 0
            finished = True
        else:
            self.gl_point_loc = None
        if finished:
            return True

        # Get the closest point to the edge and a percent from the first vert to the point
        point, distance = mathutils.geometry.intersect_point_line(ray_loc, vert_one_loc, vert_two_loc)
        self.start_vert = vert_one

        if math.isnan(distance):
            return False

        # # Clamp distance
        # if distance < 0:
        #     distance = 0

        # Get a point along the line closest to the ray location
        if use_snaps == False:
            self.distance_percent = distance

            # # Clamp point drawing
            # if distance == 0:
            #     self.gl_point_loc = vert_one_loc
            # else:
            #     self.gl_point_loc = point
            self.gl_point_loc = point

        # Snap to the nearest rounded position
        else:            
            self.distance_percent = round(distance * 4) / 4.0
            position = self.start_vert.co.lerp(vert_two.co, self.distance_percent)
            self.gl_point_loc = world_mat @ position

        return True


    def validate_state(self):
        '''Make sure data is valid.'''

        if self.bm_edge == None:
            return False

        if type(self.ray_data) != dict:
            return False

        ray_data_keys = {'result', 'location', 'normal', 'index', 'object', 'matrix'}
        for key, val in self.ray_data.items():
            if key not in ray_data_keys:
                return False
        
        if isinstance(self.bm_edge, bmesh.types.BMEdge):
            return True
        else:
            return False


    def transfer_data_knife(self, other):
        '''Transfer data over from other knife to make swap chain.'''

        self.ray_data = other.ray_data
        self.gl_point_loc = other.gl_point_loc

        # Edge snap data
        self.bm_edge = other.bm_edge
        self.start_vert = other.start_vert
        self.distance_percent = other.distance_percent


class Tool(Enum):
    SELECT = 0
    SPIN = 1
    MERGE = 2
    DISSOLVE = 3
    JOIN = 4
    KNIFE = 5


class HOPS_OT_FastMeshEditor(bpy.types.Operator):
    bl_idname = "hops.fast_mesh_editor"
    bl_label = "Fast mesh editor"
    bl_description = """Fast Mesh Editor 
    Quickly do basic edits on the mesh
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
        self.tool = Tool.SELECT

        # Starting Data
        self.obj = context.active_object
        self.mesh = self.obj.data
        self.revert_mesh_backup = self.mesh.copy()
        self.mesh_lookup_key = f'HOPSBACKUP {time.time()}'
        self.revert_mesh_backup.name = self.mesh_lookup_key

        # Bmesh
        self.bm = bmesh.from_edit_mesh(self.mesh)
        self.bm_copy = self.bm.copy()
        self.undo_steps = 0

        # Screen
        self.region = bpy.context.region
        self.rv3d = bpy.context.space_data.region_3d

        # Controls
        self.mouse_pos = (event.mouse_region_x, event.mouse_region_y)
        self.left_click_down = False
        self.mouse_accumulation = 0

        # Tools
        self.setup_tool_data()

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

        # Locked adjust state
        self.locked = False
        self.tool_mesh_backup = None

        # Selector Gizmo
        self.select_radius = 30

        # Select
        self.started_selection = False
        self.select_vert_count_draw = 0
        self.select_locked_bevel = False

        # Spin
        self.spin_edge_draw = None

        # Merge
        self.merge_start = False
        self.first_merge_vert = None
        self.second_merge_vert = None

        # Dissolve
        self.dissolve_vert = None
        self.dissolve_edge = None
        self.dissolve_vert_draw = None
        self.dissolve_edge_draw = None

        # Join
        self.join_start = False
        self.first_join_vert = None
        self.second_join_vert = None

        # Knife
        self.knife_start = False
        self.knife_chain_running = False
        self.knife_first = Knife_Data()
        self.knife_second = Knife_Data()
        self.knife_draw_points = []


    def setup_flow_menu(self):
        '''Setup flow menu system.'''

        flow_data = [
            Flow_Form(text="TOOLS",    font_size=18, tip_box="Pick a tool;TIP: Cant switch during bevel."),
            Flow_Form(text="SELECT",   font_size=14, func=self.flow_func, pos_args=(Tool.SELECT,  ), tip_box="Select tool."),
            Flow_Form(text="SPIN",     font_size=14, func=self.flow_func, pos_args=(Tool.SPIN,    ), tip_box="Spin tool."),
            Flow_Form(text="MERGE",    font_size=14, func=self.flow_func, pos_args=(Tool.MERGE,   ), tip_box="Merge tool."),
            Flow_Form(text="DISSOLVE", font_size=14, func=self.flow_func, pos_args=(Tool.DISSOLVE,), tip_box="Dissolve tool."),
            Flow_Form(text="JOIN",     font_size=14, func=self.flow_func, pos_args=(Tool.JOIN,    ), tip_box="Join tool."),
            Flow_Form(text="KNIFE",    font_size=14, func=self.flow_func, pos_args=(Tool.KNIFE,   ), tip_box="Knife tool.")
        ]
        self.flow.setup_flow_data(flow_data)


    def flow_func(self, tool=Tool.SELECT):
        '''Func to switch tools from flow menu.'''

        if self.locked == False:
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

        # Confirm exit
        if self.flow.is_open == False:
            if event.type in {'RET', 'SPACE'}:
                self.confirmed_exit()
                return {'FINISHED'}

        # Toggle perspective
        if event.type == 'P' or event.type == 'NUMPAD_5':
            if event.value == 'PRESS':
                bpy.ops.view3d.view_persportho()

        # Undo
        elif event.type == 'Z' and event.ctrl and event.value == "PRESS":

            # No undo when in locked mode
            if self.locked == False:

                # Undo
                if self.undo_steps > 1:
                    self.undo_steps -= 1
                    self.bm.free()
                    bpy.ops.ed.undo()
                    # Recapture refs since blender breaks refs
                    # NOTE: The reason for this recapture is because of the locked tool states going to object mode
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.ops.object.mode_set(mode='EDIT')
                    self.obj = context.active_object
                    self.mesh = self.obj.data
                    # Ensure we can get the mesh backup
                    if self.mesh_lookup_key in bpy.data.meshes.keys():
                        self.revert_mesh_backup = bpy.data.meshes[self.mesh_lookup_key]
                    self.bm = bmesh.from_edit_mesh(self.mesh)
                    # Attempt to touch the bmesh data
                    try:
                        if len(self.bm.verts) > 0: pass
                    except:
                        self.remove_shaders()
                    self.ensure_selection_change()

        # Check for tool switch
        if self.locked == False:
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

        # Cycle Tools
        if event.type == 'X' and event.value == "PRESS":
            if self.left_click_down == False:

                if self.tool == Tool.SELECT:
                    self.tool = Tool.SPIN
                elif self.tool == Tool.SPIN:
                    self.tool = Tool.MERGE
                elif self.tool == Tool.MERGE:
                    self.tool = Tool.DISSOLVE
                elif self.tool == Tool.DISSOLVE:
                    self.tool = Tool.JOIN
                elif self.tool == Tool.JOIN:
                    self.tool = Tool.KNIFE
                elif self.tool == Tool.KNIFE:
                    self.tool = Tool.SELECT

                self.ensure_selection_change()

        # SELECT
        elif event.type == 'S' and event.value == "PRESS" and event.shift == False:
            self.tool = Tool.SELECT
            self.ensure_selection_change()

        # SPIN
        elif event.type == 'S' and event.value == "PRESS" and event.shift == True:
            self.tool = Tool.SPIN
            self.ensure_selection_change()

        # MERGE
        elif event.type == 'M' and event.value == "PRESS" and event.shift == False:
            self.tool = Tool.MERGE
            self.ensure_selection_change()

        # DISSOLVE
        elif event.type == 'D' and event.value == "PRESS" and event.shift == False:
            self.tool = Tool.DISSOLVE
            self.ensure_selection_change()

        # JOIN
        elif event.type == 'J' and event.value == "PRESS" and event.shift == False:
            self.tool = Tool.JOIN
            self.ensure_selection_change()

        # KNIFE
        elif event.type == 'K' and event.value == "PRESS" and event.shift == False:
            self.tool = Tool.KNIFE
            self.ensure_selection_change()


    def draw_master(self, context):

        self.master.setup()
        if self.master.should_build_fast_ui():
            win_list = []
            help_list = []
            mods_list = []
            active_mod = ""

            # Main / Help
            if self.tool == Tool.SELECT:
                win_list.append("TOOL: SELECT")
                win_list.append(f'Verts: {self.select_vert_count_draw}')

                help_list.append(["Shift + L",     "Select loop ring"])
                help_list.append(["L",             "Select Loop"])
                help_list.append(["B",             "Boundary Bevel"])
                help_list.append(["E",             "Toggle mark sharp"])
                help_list.append(["Alt + A",       "Deselect all"])
                help_list.append(["A",             "Select all"])
                help_list.append(["C",             "Clean selection"])
                help_list.append(["Ctrl + Scroll", "Grow / Shrink Selection"])
                help_list.append(["3 / Shift",     "Select Faces / Append"])
                help_list.append(["2 / Shift",     "Select Edges / Append"])
                help_list.append(["1 / Shift",     "Select Verts / Append"])
                help_list.append(["Scroll",        "Increase brush size"])
                help_list.append(["Ctrl Click",    "Subtract Select"])
                help_list.append(["Alt Click",     "Append Select"])
                help_list.append(["Click",         "Select"])
                help_list.append(["", "________SELECT________"])

            elif self.tool == Tool.SPIN:
                win_list.append("TOOL: SPIN")

                help_list.append(["Shift Click", "Spin the edge (Counter Clock Wise)"])
                help_list.append(["Click",       "Spin the edge (Clock Wise)"])
                help_list.append(["", "________SPIN________"])

            elif self.tool == Tool.MERGE:
                win_list.append("TOOL: MERGE")

                help_list.append(["C",     "Cancel selection"])
                help_list.append(["Click", "Click 2 verts to merge at last"])
                help_list.append(["", "________MERGE________"])

            elif self.tool == Tool.DISSOLVE:
                win_list.append("TOOL: DISSOLVE")

                help_list.append(["2",     "Select Edges"])
                help_list.append(["1",     "Select Verts"])
                help_list.append(["Click", "Dissolve selection"])
                help_list.append(["", "________DISSOLVE________"])

            elif self.tool == Tool.JOIN:
                win_list.append("TOOL: JOIN")

                help_list.append(["C",     "Cancel selection"])
                help_list.append(["Click", "Click 2 verts to join at last"])
                help_list.append(["", "________JOIN________"])
                
            elif self.tool == Tool.KNIFE:
                win_list.append("TOOL: KNIFE")

                help_list.append(["C",     "Cancel cut chain"])
                help_list.append(["Ctrl",  "Snap along at 25% increments"])
                help_list.append(["Click", "Click 2 verts / edges to knife at last"])
                help_list.append(["", "________KNIFE________"])

            # Base Help
            help_list.append(["K",         "KNIFE"])
            help_list.append(["J",         "JOIN"])
            help_list.append(["D",         "DISSOLVE"])
            help_list.append(["M",         "MERGE"])
            help_list.append(["S + Shift", "SPIN"])
            help_list.append(["S",         "SELECT"])
            help_list.append(["X",         "Toggle through tools"])

            help_list.append(["", "________SWITCH________"])

            help_list.append(["Ctrl + Z",    "Undo"])
            help_list.append(["M",           "Toggle mods list"])
            help_list.append(["H",           "Toggle help"])
            help_list.append(["~",           "Toggle UI Display Type"])
            help_list.append(["O",           "Toggle viewport rendering"])
            help_list.append(["P / 5",       "Toggle Perspective"])
            help_list.append(["Shift Space", "Spawn tool switcher"])

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
        # Close out shaders and ui
        self.shut_down()


    def confirmed_exit(self):
        '''Remove backup data.'''

        # Close out shaders and ui
        self.remove_shaders()
        self.master.run_fade()
        # Remove the mesh backup
        bpy.data.meshes.remove(self.revert_mesh_backup)
        # Close out shaders and ui
        self.shut_down()


    def shut_down(self):
        '''Shut down modal.'''

        # Flow system
        self.flow.shut_down()
        # Set the cursor back
        bpy.context.window.cursor_set("CROSSHAIR")
        # Remove the tool mesh backup
        if self.tool_mesh_backup != None:
            bpy.data.meshes.remove(self.tool_mesh_backup)
        # Set the tool panels back
        collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)

    ####################################################
    #   TOOLS
    ####################################################

    def update_tools(self, context, event):
        '''Do tool actions.'''

        # Select
        if self.tool == Tool.SELECT:
            self.circle_select(context, event)

        # Spin
        elif self.tool == Tool.SPIN:
            self.spin_edges(context, event)

        # Merge
        elif self.tool == Tool.MERGE:
            self.merge_verts(context, event)

        # Dissolve
        elif self.tool == Tool.DISSOLVE:
            self.dissolve(context, event)

        # Join
        elif self.tool == Tool.JOIN:
            self.join(context, event)

        # Kinfe
        elif self.tool == Tool.KNIFE:
            self.knife(context, event)

                
    def circle_select(self, context, event):
        '''Keep the mesh updated.'''

        # LOCKED : Bevel
        if self.select_locked_bevel == True:
            self.mouse_accumulation -= self.base_controls.mouse

            # Cancel
            if event.type == 'C' and event.value == "PRESS":
                self.locked = False
                self.select_locked_bevel = False
                # Remove all mesh data
                bmesh.ops.delete(self.bm, geom=self.bm.verts, context='VERTS')
                # Reload bmesh based on mesh backup
                self.bm.from_mesh(self.tool_mesh_backup)
                bpy.data.meshes.remove(self.tool_mesh_backup)
                self.tool_mesh_backup = None
                return

            # Unlock / Remove backup
            elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
                self.locked = False
                self.select_locked_bevel = False
                bpy.data.meshes.remove(self.tool_mesh_backup)
                self.tool_mesh_backup = None
                bpy.ops.mesh.select_all(action='DESELECT')

                bpy.ops.ed.undo_push()
                self.undo_steps += 1
                return

            mouse_warp(context, event)

            # Remove all mesh data
            bmesh.ops.delete(self.bm, geom=self.bm.verts, context='VERTS')
            # Reload bmesh based on mesh backup
            self.bm.from_mesh(self.tool_mesh_backup)

            # --- BMESH --- #

            # Bevel
            edges = [e for e in self.bm.edges if e.select == True]

            if bpy.app.version[1] < 90:
                bmesh.ops.bevel(
                    self.bm,
                    geom=edges,
                    offset=self.mouse_accumulation,
                    offset_type='OFFSET',
                    segments=2,
                    profile=1,
                    vertex_only=False,
                    clamp_overlap=True,
                    material=-1,
                    loop_slide=False,
                    mark_seam=False,
                    mark_sharp=False,
                    harden_normals=False)

            elif bpy.app.version[1] >= 90:
                bmesh.ops.bevel(
                    self.bm,
                    geom=edges,
                    offset=self.mouse_accumulation,
                    offset_type='OFFSET',
                    segments=2,
                    profile=1,
                    affect='EDGES',
                    clamp_overlap=True,
                    material=-1,
                    loop_slide=False,
                    mark_seam=False,
                    mark_sharp=False,
                    harden_normals=False)
            return

        # Vert mode
        if event.type == 'ONE' and event.value == "PRESS":
            extend = True if event.shift else False
            bpy.ops.mesh.select_mode(use_extend=extend, type="VERT")

        # Edge mode
        elif event.type == 'TWO' and event.value == "PRESS":
            extend = True if event.shift else False
            bpy.ops.mesh.select_mode(use_extend=extend, type="EDGE")

        # Face mode
        elif event.type == 'THREE' and event.value == "PRESS":
            extend = True if event.shift else False
            bpy.ops.mesh.select_mode(use_extend=extend, type="FACE")

        # Select all
        elif event.type == 'A' and event.value == "PRESS" and event.alt == False and event.shift == False:
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.ed.undo_push()
            self.undo_steps += 1

        # Deselect all
        elif event.type == 'A' and event.value == "PRESS" and event.alt == True and event.shift == False:
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.ed.undo_push()
            self.undo_steps += 1

        # Mark edges sharp
        elif event.type == 'E' and event.value == "PRESS":
            bpy.ops.hops.set_edit_sharpen()
            bpy.ops.ed.undo_push()
            self.undo_steps += 1

        # Clean faces
        elif event.type == 'C' and event.value == "PRESS":
            bpy.ops.mesh.remove_doubles(threshold=get_preferences().property.meshclean_remove_threshold)
            bpy.ops.mesh.dissolve_limited(angle_limit=get_preferences().property.meshclean_dissolve_angle)

        # LOCK STATE : Boundary bevel
        elif event.type == 'B' and event.value == "PRESS":

            bpy.ops.mesh.region_to_loop()

            # If edge count is 0
            edge_count = len([e for e in self.bm.edges if e.select == True])
            if edge_count == 0:
                bpy.ops.hops.display_notification(info="Select an edge / edges")
                return
            # If edge count is 1
            elif edge_count == 1:
                bpy.ops.mesh.loop_multi_select(ring=False)
                # Loop ring didnt get anything
                if len([e for e in self.bm.edges if e.select == True]) == 0:
                    bpy.ops.hops.display_notification(info="Select an edge / edges")
                    
            self.locked = True
            self.select_locked_bevel = True
            self.mouse_accumulation = 0

            # Update the current mesh
            bmesh.update_edit_mesh(self.mesh)

            # Write data blocks
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='EDIT')

            # Capture refreshed data block
            self.bm = bmesh.from_edit_mesh(self.mesh)

            # Get a copy of the refreshed data block
            self.tool_mesh_backup = self.mesh.copy()

        # Edge loop
        elif event.type == 'L' and event.value == "PRESS" and event.shift == False:
            bpy.ops.mesh.loop_multi_select(ring=False)
            bpy.ops.ed.undo_push()
            self.undo_steps += 1

        # Edge loop ring
        elif event.type == 'L' and event.value == "PRESS" and event.shift == True:
            bpy.ops.mesh.loop_multi_select(ring=True)
            bpy.ops.ed.undo_push()
            self.undo_steps += 1

        # Grow / Shrink Selection
        elif event.ctrl == True:
            if self.base_controls.scroll > 0:
                bpy.ops.mesh.select_more(use_face_step=True)
                bpy.ops.ed.undo_push()
                self.undo_steps += 1
            elif self.base_controls.scroll < 0:
                bpy.ops.mesh.select_less(use_face_step=True)
                bpy.ops.ed.undo_push()
                self.undo_steps += 1

        # Increse / Decrease brush size
        if self.base_controls.scroll:
            if self.locked == False:
                if self.base_controls.scroll > 0:
                    if self.select_radius + 5 < context.area.width * .25:
                        self.select_radius += 5
                if self.base_controls.scroll < 0:
                    if self.select_radius - 5 > 5:
                        self.select_radius -= 5

        # Circle select
        if self.left_click_down:
            self.started_selection = True

            # Click select
            if event.shift == False and event.ctrl == False:
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.view3d.select_circle(
                    x=self.mouse_pos[0],
                    y=self.mouse_pos[1],
                    radius=self.select_radius,
                    wait_for_input=True,
                    mode='ADD')

            # Append select
            elif event.shift == True and event.ctrl == False:
                bpy.ops.view3d.select_circle(
                    x=self.mouse_pos[0],
                    y=self.mouse_pos[1],
                    radius=self.select_radius,
                    wait_for_input=True,
                    mode='ADD')

            # Subtract select
            elif event.ctrl == True:
                bpy.ops.view3d.select_circle(
                    x=self.mouse_pos[0],
                    y=self.mouse_pos[1],
                    radius=self.select_radius,
                    wait_for_input=True,
                    mode='SUB')

        # Save undo after selection is over
        else:
            if self.started_selection == True:
                self.started_selection = False
                bpy.ops.ed.undo_push()
                self.undo_steps += 1

        self.select_vert_count_draw = len( [v for v in self.bm.verts if v.select == True] )


    def spin_edges(self, context, event):
        '''Spin the edges under the click.'''

        if event.type == "MOUSEMOVE":
            self.spin_edge_draw = self.get_edge_under_mouse(context, event, as_copy=True)

        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            edge = self.get_edge_under_mouse(context, event)
            if edge != None:
                bpy.ops.ed.undo_push()
                self.undo_steps += 1
                use_ccw = True if event.shift else False
                bmesh.ops.rotate_edges(self.bm, edges=[edge], use_ccw=use_ccw)


    def merge_verts(self, context, event):
        '''Merge the verts under the circle.'''

        # Cancel
        if event.type == 'C' and event.value == "PRESS":
            self.merge_start = False
            self.first_merge_vert = None
            self.second_merge_vert = None

        # (1) First click : Get vert under mouse
        if self.merge_start == False:
            if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                self.first_merge_vert = self.get_vert_under_mouse(context, event)
                if self.first_merge_vert != None:
                    self.merge_start = True

        # (2) Mouse move : Show line to next vert under mouse
        if self.merge_start == True:
            if event.type == "MOUSEMOVE":
                self.second_merge_vert = self.get_vert_under_mouse(context, event)
                if self.first_merge_vert == self.second_merge_vert:
                    self.second_merge_vert = None

        # (3) Second click : Join the (first vert, second vert) and start over
        if self.merge_start == True:
            if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                if self.first_merge_vert != None:
                    if self.second_merge_vert != None:
                        self.merge_start = False

                        bpy.ops.ed.undo_push()
                        self.undo_steps += 1

                        verts = [self.first_merge_vert, self.second_merge_vert]
                        bmesh.ops.pointmerge(self.bm, verts=verts, merge_co=self.second_merge_vert.co)
                        self.first_merge_vert = None
                        self.second_merge_vert = None


    def dissolve(self, context, event):
        '''Dissolve V, E below mouse.'''

        # Vert mode
        if event.type == 'ONE' and event.value == "PRESS":
            bpy.ops.mesh.select_mode(use_extend=False, type="VERT")

        # Edge mode
        elif event.type == 'TWO' and event.value == "PRESS":
            bpy.ops.mesh.select_mode(use_extend=False, type="EDGE")

        # Get vert / edge
        if event.type == "MOUSEMOVE":
            if 'VERT' in self.bm.select_mode:
                self.dissolve_vert = self.get_vert_under_mouse(context, event)
                if self.dissolve_vert != None:
                    self.dissolve_vert_draw = self.obj.matrix_world @ self.dissolve_vert.co
            else:
               self.dissolve_vert = None
               self.dissolve_vert_draw = None

            if 'EDGE' in self.bm.select_mode:
                self.dissolve_edge = self.get_edge_under_mouse(context, event)
                if self.dissolve_edge != None:
                    self.dissolve_edge_draw = self.get_edge_copy(self.dissolve_edge)
            else:
                self.dissolve_edge = None
                self.dissolve_edge_draw = None

        # Close the deal
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':

            if self.dissolve_edge != None or self.dissolve_vert != None:
                bpy.ops.ed.undo_push()
                self.undo_steps += 1

            if self.dissolve_edge != None:
                if self.dissolve_edge in self.bm.edges:
                    bmesh.ops.dissolve_edges(self.bm, edges=[self.dissolve_edge])

                self.dissolve_edge = None
                self.dissolve_edge_draw = None

            if self.dissolve_vert != None:
                if self.dissolve_vert in self.bm.verts:
                    bmesh.ops.dissolve_verts(self.bm, verts=[self.dissolve_vert], use_face_split=False, use_boundary_tear=False)

                self.dissolve_edge = None
                self.dissolve_edge_draw = None
                self.dissolve_vert = None
                self.dissolve_vert_draw = None


    def join(self, context, event):
        '''Join verts tool.'''

        # Cancel
        if event.type == 'C' and event.value == "PRESS":
            self.join_start = False
            self.first_join_vert = None
            self.second_join_vert = None

        # (1) First click : Get vert under mouse
        if self.join_start == False:
            if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                self.first_join_vert = self.get_vert_under_mouse(context, event)
                if self.first_join_vert != None:
                    self.join_start = True

        # (2) Mouse move : Show line to next vert under mouse
        if self.join_start == True:
            if event.type == "MOUSEMOVE":
                self.second_join_vert = self.get_vert_under_mouse(context, event)
                if self.first_join_vert == self.second_join_vert:
                    self.second_join_vert = None

        # (3) Second click : Join the (first vert, second vert) and start over
        if self.join_start == True:
            if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                if self.first_join_vert != None:
                    if self.second_join_vert != None:
                        self.join_start = False

                        bpy.ops.ed.undo_push()
                        self.undo_steps += 1

                        verts = [self.first_join_vert, self.second_join_vert]
                        bmesh.ops.connect_vert_pair(self.bm, verts=verts)
                        self.first_join_vert = None
                        self.second_join_vert = None


    def knife(self, context, event):
        '''Knife edges / verts tool.'''

        # Cancel
        if event.type == 'C' and event.value == "PRESS":
            self.knife_start = False
            self.knife_chain_running = False
            self.knife_first.reset()
            self.knife_second.reset()

        # (1) Scan for first edge under mouse
        if self.knife_start == False:
            if event.type == 'MOUSEMOVE':
                edge, ray_data = self.get_edge_under_mouse(context, event, ret_with_ray_data=True)
                if edge != None:
                    snap = True if event.ctrl == True else False
                    if self.knife_first.set_bm_edge(self.bm, edge, self.obj, ray_data, use_snaps=snap) == False:
                        self.knife_start = False
                        self.knife_first.reset()
                        self.knife_second.reset()

        # (2) Confirm first edge edge
        if self.knife_start == False:
            if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                if self.knife_first.validate_state():
                    self.knife_start = True

        # (3) Scan for second edge under mouse
        if self.knife_start == True:
            if event.type == "MOUSEMOVE":
                edge, ray_data = self.get_edge_under_mouse(context, event, ret_with_ray_data=True)
                if edge != None:
                    # Make sure its not the first edge
                    if edge != self.knife_first.bm_edge:
                        snap = True if event.ctrl == True else False
                        if self.knife_second.set_bm_edge(self.bm, edge, self.obj, ray_data, use_snaps=snap) == False:
                            self.knife_start = False
                            self.knife_first.reset()
                            self.knife_second.reset()

        # (4) Confirm operation
        if self.knife_start == True:
            if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                
                if self.knife_first.validate_state():
                    if self.knife_second.validate_state():

                        first_vert = self.knife_first.get_and_gen_bm_vert(dont_perform_cut=self.knife_chain_running)
                        second_vert = self.knife_second.get_and_gen_bm_vert()

                        # Something failed
                        if first_vert == None or second_vert == None:
                            self.knife_start = False
                            self.knife_first.reset()
                            self.knife_second.reset()
                            return

                        if first_vert != second_vert:
                            verts = [first_vert, second_vert]
                            bmesh.ops.connect_vert_pair(self.bm, verts=verts)

                            bpy.ops.ed.undo_push()
                            self.undo_steps += 1                        
                        else:
                            self.knife_second.reset()
                            return
                        
                        self.knife_start = True
                        self.knife_chain_running = True
                        self.knife_first.transfer_data_knife(self.knife_second)
                        self.knife_second.reset()

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
            return None

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

        # For drawing knife
        if self.tool == Tool.KNIFE:
            self.knife_draw_points = []
            for vert in closest_edge.verts:
                self.knife_draw_points.append(self.obj.matrix_world @ vert.co)

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


    def ensure_selection_change(self):
        '''Make sure the correct selection mode is active.'''

        self.setup_tool_data()

        if self.tool == Tool.SELECT:
            bpy.context.window.cursor_set("CROSSHAIR")

        elif self.tool == Tool.SPIN:
            bpy.context.window.cursor_set("SCROLL_XY")
            if 'EDGE' not in self.bm.select_mode:
                bpy.ops.mesh.select_mode(use_extend=False, type="EDGE")

        elif self.tool == Tool.MERGE:
            bpy.context.window.cursor_set("SCROLL_XY")
            if 'EDGE' in self.bm.select_mode:
                bpy.ops.mesh.select_mode(use_extend=False, type="VERT")

        elif self.tool == Tool.DISSOLVE:
            bpy.context.window.cursor_set("ERASER")
            bpy.ops.mesh.select_mode(use_extend=False, type="EDGE")

        elif self.tool == Tool.JOIN:
            bpy.context.window.cursor_set("SCROLL_XY")
            if self.bm.select_mode != 'VERT':
                bpy.ops.mesh.select_mode(use_extend=False, type="VERT")

        elif self.tool == Tool.KNIFE:
            bpy.context.window.cursor_set("KNIFE")
            
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

        if self.tool == Tool.SELECT:
            self.draw_select_2D(context)

        if self.tool == Tool.KNIFE:
            self.draw_knife_2D(context)


    def draw_select_2D(self, context):
        '''Draw the circle where the mouse is in 2D.'''

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

        # Bevel locked
        if self.select_locked_bevel == True:
            draw_modal_frame(context)

            # Draw label
            label = "OFFSET  "
            dims = get_blf_text_dims(label, 16)[0]
            text_pos = (self.mouse_pos[0] + self.select_radius, self.mouse_pos[1] + self.select_radius)
            render_text(text=label, position=text_pos, size=16, color=(0,1,1,1))

            # Draw label
            cancel_pos = (self.mouse_pos[0] + self.select_radius, self.mouse_pos[1] + self.select_radius + (25 * dpi_factor()))
            render_text(text="Press C for cancel", position=cancel_pos, size=16, color=(0,1,1,1))

            # Draw annotation line
            verts = (self.mouse_pos, text_pos)
            draw_2D_lines(vertices=verts, width=.5, color=(0,1,1,1))

            # Draw offset
            offset_color = (0,1,0,1) if self.mouse_accumulation > 0 else (1,0,0,1)
            offset_text = "{:.3f}".format(self.mouse_accumulation)
            text_pos = (self.mouse_pos[0] + self.select_radius + dims, self.mouse_pos[1] + self.select_radius)
            render_text(text=offset_text, position=text_pos, size=18, color=offset_color)


    def draw_knife_2D(self, context):
        '''Draw knife tool.'''

        factor = dpi_factor()
        up = 40 * factor
        right = 40 * factor
        font_size = 12

        if self.knife_first.gl_point_loc != None:
            point = self.get_2d_point_from_3d(self.knife_first.gl_point_loc)
            if point != None:
                text_loc = (point[0] + up, point[1] + right)
                text = f'{int(self.knife_first.distance_percent * 100)} %'
                render_text(text=text, position=text_loc, size=font_size, color=(0,1,1,1))

                verts = (point, text_loc)
                draw_2D_lines(vertices=verts, width=.5, color=(0,1,1,.25))


        if self.knife_second.gl_point_loc != None:
            point = self.get_2d_point_from_3d(self.knife_second.gl_point_loc)
            if point != None:
                text_loc = (point[0] + up, point[1] + right)
                text = f'{int(self.knife_second.distance_percent * 100)} %'
                render_text(text=text, position=text_loc, size=font_size, color=(0,1,1,1))

                verts = (point, text_loc)
                draw_2D_lines(vertices=verts, width=.5, color=(0,1,1,.25))

    # 3D SHADER
    def safe_draw_3D(self, context):
        method_handler(self.draw_shader_3D,
            arguments = (context,),
            identifier = 'Modal Shader 3D',
            exit_method = self.remove_shaders)


    def draw_shader_3D(self, context):
        '''Draw shader handle.'''

        if self.tool == Tool.SPIN:
            self.draw_spin_3D()

        elif self.tool == Tool.MERGE:
            self.draw_merge_3D()

        elif self.tool == Tool.DISSOLVE:
            self.draw_dissolve_3D()

        elif self.tool == Tool.JOIN:
            self.draw_join_3D()

        elif self.tool == Tool.KNIFE:
            self.draw_knife_3D()


    def draw_spin_3D(self):
        '''Draw the spin tool.'''

        if self.spin_edge_draw == None:
            return

        verts = []
        indices = []
        push = 0
        for index, vert in enumerate(self.spin_edge_draw.verts):
            verts.append( (vert[0], vert[1], vert[2]) )
            indices.append( (index + push, index + push + 1) )
            push += 1

        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'LINES', {'pos': verts}, indices=indices)
        shader.bind()
        shader.uniform_float('color', (1,0,0,1))
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)
        glLineWidth(3)
        batch.draw(shader)
        del shader
        del batch


    def draw_merge_3D(self):
        '''Draw the merge tool.'''

        if self.first_merge_vert != None:

            shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'POINTS', {'pos': [self.obj.matrix_world @ self.first_merge_vert.co]})
            shader.bind()
            shader.uniform_float('color', (1,0,0,1))
            glEnable(GL_BLEND)
            glPointSize(6)
            batch.draw(shader)
            del shader
            del batch

        if self.second_merge_vert != None:

            shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'POINTS', {'pos': [self.obj.matrix_world @ self.second_merge_vert.co]})
            shader.bind()
            shader.uniform_float('color', (1,0,0,1))
            glEnable(GL_BLEND)
            glPointSize(6)
            batch.draw(shader)
            del shader
            del batch

            first_pos = self.obj.matrix_world @ self.first_merge_vert.co
            second_pos = self.obj.matrix_world @ self.second_merge_vert.co

            verts = [first_pos, second_pos]
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


    def draw_dissolve_3D(self):
        '''Draw the dissolve tool.'''

        if self.dissolve_vert_draw != None:

            shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'POINTS', {'pos': [self.dissolve_vert_draw]})
            shader.bind()
            shader.uniform_float('color', (1,0,0,1))
            glEnable(GL_BLEND)
            glPointSize(6)
            batch.draw(shader)
            del shader
            del batch

        if self.dissolve_edge_draw != None:

            verts = []
            indices = []
            push = 0
            for index, vert in enumerate(self.dissolve_edge_draw.verts):
                verts.append( (vert[0], vert[1], vert[2]) )
                indices.append( (index + push, index + push + 1) )
                push += 1
            shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'LINES', {'pos': verts}, indices=indices)
            shader.bind()
            shader.uniform_float('color', (1,0,0,1))
            glEnable(GL_LINE_SMOOTH)
            glEnable(GL_BLEND)
            glLineWidth(3)
            batch.draw(shader)
            del shader
            del batch


    def draw_join_3D(self):
        '''Draw the join too.'''

        if self.first_join_vert != None:

            shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'POINTS', {'pos': [self.obj.matrix_world @ self.first_join_vert.co]})
            shader.bind()
            shader.uniform_float('color', (1,0,0,1))
            glEnable(GL_BLEND)
            glPointSize(6)
            batch.draw(shader)
            del shader
            del batch

        if self.second_join_vert != None:

            first_pos = self.obj.matrix_world @ self.first_join_vert.co
            second_pos = self.obj.matrix_world @ self.second_join_vert.co

            verts = [first_pos, second_pos]
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

        if self.first_join_vert != None and self.second_join_vert != None:

            shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'POINTS', {'pos': [self.obj.matrix_world @ self.second_join_vert.co]})
            shader.bind()
            shader.uniform_float('color', (1,0,0,1))
            glEnable(GL_BLEND)
            glPointSize(6)
            batch.draw(shader)
            del shader
            del batch


    def draw_knife_3D(self):
        '''Draw the knife tool.'''

        if self.knife_draw_points != []:

            verts = [self.knife_draw_points[0], self.knife_draw_points[1]]
            indices = [(0,1)]

            shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'LINES', {'pos': verts}, indices=indices)
            shader.bind()
            shader.uniform_float('color', (1,1,0,1))
            glEnable(GL_LINE_SMOOTH)
            glEnable(GL_BLEND)
            glLineWidth(3)
            batch.draw(shader)
            del shader
            del batch

        if self.knife_first.gl_point_loc != None:

            shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'POINTS', {'pos': [self.knife_first.gl_point_loc]})
            shader.bind()
            shader.uniform_float('color', (1,0,0,1))
            glEnable(GL_BLEND)
            glPointSize(6)
            batch.draw(shader)
            del shader
            del batch

        if self.knife_second.gl_point_loc != None:

            shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'POINTS', {'pos': [self.knife_second.gl_point_loc]})
            shader.bind()
            shader.uniform_float('color', (1,0,0,1))
            glEnable(GL_BLEND)
            glPointSize(6)
            batch.draw(shader)
            del shader
            del batch

        if self.knife_second.gl_point_loc != None and self.knife_first.gl_point_loc != None:

            verts = [self.knife_first.gl_point_loc, self.knife_second.gl_point_loc]
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