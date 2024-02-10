import bpy, mathutils, math, bmesh
from enum import Enum
from ... preferences import get_preferences
from ... utility.base_modal_controls import Base_Modal_Controls
from ... ui_framework.master import Master
from ... ui_framework.utils.mods_list import get_mods_list
from ... ui_framework.graphics.draw import render_text
from ... ui_framework.flow_ui.flow import Flow_Menu, Flow_Form
from ... addon.utility.screen import dpi_factor
from ... utils.toggle_view3d_panels import collapse_3D_view_panels
from ... utils.modal_frame_drawing import draw_modal_frame
from ... utils.cursor_warp import mouse_warp
from ... addon.utility import method_handler

'''
OVERVIEW
1) Copy the active selected geometry
2) Create a new mesh
3) Add the copied geometry to the new mesh
4) Go into edit mode on new mesh
5) Modal adjust the size of plane(s)
6) Modal adjust the cut depth
7) Drop user options: Edit bool, Edit original
'''


class Edit_States(Enum):
    OFFSET = 0
    INSET = 1
    EXTRUDING = 2


class HOPS_OT_Sel_To_Bool_V2(bpy.types.Operator):
    bl_idname = "hops.sel_to_bool_v2"
    bl_label = "Selection To Boolean V2"
    bl_description = """Selection to Boolean
    Convert active face(s) to boolean
    Press H for help
    """
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}

    @classmethod
    def poll(cls, context: bpy.context):
        if context.active_object != None:
            if context.active_object.type == 'MESH':
                if context.active_object.mode == 'EDIT':
                    return True
        return False


    def invoke(self, context, event):

        # Props
        self.obj = None
        self.bool_obj = None
        self.bool_mod = None
        self.edit_state = Edit_States.INSET
        self.bm_backup = None

        # Drawing
        self.mouse_pos = (event.mouse_region_x, event.mouse_region_y)
        prefs = get_preferences()
        self.color = (
            prefs.color.Hops_UI_cell_background_color[0],
            prefs.color.Hops_UI_cell_background_color[1],
            prefs.color.Hops_UI_cell_background_color[2], 1)

        # Edit props
        self.offset_value = 0.035 if bpy.app.version[1] >= 90 else -0.035
        self.inset_value = 0.025
        self.extrude_value = 0.1

        # Editor
        self.og_xray = context.space_data.shading.show_xray
        self.og_shading = context.space_data.shading.type

        # Setup
        self.obj = context.active_object
        self.create_boolean_object(context=context)
        if self.setup_boolean_object(context=context) == False:
            self.cancel_cleanup()
            return {'FINISHED'}

        # Flow menu
        self.context = context
        self.flow = Flow_Menu()
        self.setup_flow_menu()

        # Base Systems
        self.master = Master(context=context)
        self.master.only_use_fast_ui = True
        self.base_controls = Base_Modal_Controls(context, event)
        self.original_tool_shelf, self.original_n_panel = collapse_3D_view_panels()
        self.draw_handle_2D = bpy.types.SpaceView3D.draw_handler_add(self.safe_draw_2D, (context,), 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}


    def setup_flow_menu(self):
        '''Setup flow menu system.'''

        flow_data = [
            Flow_Form(text="TOOLS"  , font_size=18, tip_box="Pick a tool"),
            Flow_Form(text="OFFSET" , font_size=14, func=self.flow_func, pos_args=(Edit_States.OFFSET, self.context)   , tip_box="Adjust the offset."),
            Flow_Form(text="INSET"  , font_size=14, func=self.flow_func, pos_args=(Edit_States.INSET, self.context)    , tip_box="Adjust the inset of the face."),
            Flow_Form(text="EXTRUDE", font_size=14, func=self.flow_func, pos_args=(Edit_States.EXTRUDING, self.context), tip_box="Extrude the faces in."),
        ]
        self.flow.setup_flow_data(flow_data)


    def flow_func(self, state, context):
        '''Func to switch tools from flow menu.'''

        self.edit_state = state
        if self.edit_state == Edit_States.INSET:
            context.space_data.shading.show_xray = False
        elif self.edit_state == Edit_States.EXTRUDING:
            context.space_data.shading.show_xray = True
        elif self.edit_state == Edit_States.OFFSET:
            context.space_data.shading.show_xray = False

        bpy.ops.hops.display_notification(info=f'Switched tool to: {state.name}')


    def modal(self, context, event):

        #######################
        #   Base Systems
        #######################

        self.master.receive_event(event=event)
        self.base_controls.update(context, event)
        mouse_warp(context, event)
        self.mouse_pos = (event.mouse_region_x, event.mouse_region_y)
        self.flow.run_updates(context, event)

        #######################
        #   Controls
        #######################

        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        elif self.base_controls.cancel:
            # Flow system
            self.flow.shut_down()
            self.cancel_cleanup()
            self.remove_shaders()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            context.space_data.shading.show_xray = self.og_xray
            context.space_data.shading.type = self.og_shading
            return {'CANCELLED'}

        # Exit / Cycle Tool
        elif self.base_controls.confirm:
            if self.flow.is_open == False:
                if self.edit_state == Edit_States.EXTRUDING:
                    # Flow system
                    self.flow.shut_down()
                    self.remove_shaders()
                    collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
                    self.master.run_fade()
                    context.space_data.shading.show_xray = self.og_xray
                    context.space_data.shading.type = self.og_shading
                    bpy.ops.object.editmode_toggle()
                    return {'FINISHED'}
                else:
                    self.update_edit_states(context)

        # Toggle viewport Wireframe / Solid
        if event.type == "Z" and event.value == "PRESS":
            if context.space_data.shading.type == 'SOLID':
                context.space_data.shading.type = 'WIREFRAME'
            elif context.space_data.shading.type == 'WIREFRAME':
                context.space_data.shading.type = 'SOLID'
            else:
                context.space_data.shading.type = 'WIREFRAME'

        # Cycle tools
        if event.type == 'X' and event.value == "PRESS" or self.base_controls.scroll:
            self.update_edit_states(context)

        # Adjust bmesh
        if self.flow.is_open == False:
            if self.base_controls.mouse != 0:
                if self.edit_state == Edit_States.OFFSET:
                    self.offset_value += self.base_controls.mouse
                elif self.edit_state == Edit_States.INSET:
                    self.inset_value += self.base_controls.mouse
                elif self.edit_state == Edit_States.EXTRUDING:
                    self.extrude_value += self.base_controls.mouse

        # Setup bmesh 
        self.setup_modal_bmesh()

        self.draw_master(context=context)
        return {"RUNNING_MODAL"}


    def draw_master(self, context):

        # Start
        self.master.setup()

        #---  Fast UI ---#
        if self.master.should_build_fast_ui():

            win_list = []
            help_list = []
            mods_list = []
            active_mod = ""

            # States builder
            if self.edit_state == Edit_States.OFFSET:
                # Main
                win_list.append("Offset : {:.3f}".format(self.offset_value))
                # Help
                help_list.append(["X or Scroll", "Inset"])
                help_list.append(["Click", "Inset"])
                help_list.append(["",  "______TOOL______"])

            elif self.edit_state == Edit_States.INSET:
                # Main
                win_list.append("Offset : {:.3f}".format(self.offset_value))
                win_list.append("Inset : {:.3f}".format(self.inset_value))
                # Help
                help_list.append(["X or Scroll", "Extrude"])
                help_list.append(["Click", "Extrude"])
                help_list.append(["",  "______TOOL______"])

            elif self.edit_state == Edit_States.EXTRUDING:
                # Main
                win_list.append("Offset : {:.3f}".format(self.offset_value))
                win_list.append("Inset : {:.3f}".format(self.inset_value))
                win_list.append("Extrude : {:.3f}".format(self.extrude_value))
                # Help
                help_list.append(["X or Scroll", "Inset"])
                help_list.append(["Click", "Confirm"])
                help_list.append(["",  "______TOOL______"])

            # Help
            help_list.append(["Z", "Toggle Wireframe / Solid"])
            help_list.append(["M", "Toggle mods list"])
            help_list.append(["H", "Toggle help"])
            help_list.append(["~", "Toggle UI Display Type"])
            help_list.append(["O", "Toggle viewport rendering"])
            help_list.append(["",  "______GLOBAL______"])

            # Mods
            mods_list = get_mods_list(mods=self.obj.modifiers)

            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="Booleans", mods_list=mods_list)

        # Finished
        self.master.finished()

    ####################################################
    #   SETUP / CANCEL
    ####################################################

    def create_boolean_object(self, context):
        '''Create and return new boolean object.'''

        # Going to object mode writes bm history
        bpy.ops.object.mode_set(mode='OBJECT')

        # Update data blocks
        context.view_layer.update()
        context.view_layer.depsgraph.update()

        # Create new mesh object
        mesh = self.obj.data.copy()
        self.bool_obj = bpy.data.objects.new(mesh.name, mesh)
        self.bool_obj.hops.status = "BOOLSHAPE"

        # Append new mesh to collection
        col = None
        if "Cutters" in bpy.data.collections:
            col = bpy.data.collections.get("Cutters")
        else:
            col = bpy.data.collections.new("Cutters")
            context.scene.collection.children.link(col)
        col.objects.link(self.bool_obj)

        # Assign boolean mod to original object
        self.bool_mod = self.obj.modifiers.new("HOPS Boolean", 'BOOLEAN')
        self.bool_mod.show_render = False
        self.simple_mod_sort()
        
        # Parent / Move / Display
        self.bool_obj.parent = self.obj
        self.bool_obj.matrix_world = self.obj.matrix_world
        self.bool_obj.display_type = 'WIRE'

        # Go into edit mode on bool obj
        self.obj.select_set(False)
        self.bool_obj.select_set(True)
        context.view_layer.objects.active = self.bool_obj
        bpy.ops.object.mode_set(mode='EDIT')


    def setup_boolean_object(self, context):
        '''Copy selected geometry into a new mesh and switch edit modes.'''

        # Create bmesh from original object
        bm = bmesh.from_edit_mesh(self.bool_obj.data)

        # Remove all unselected verts
        verts = [v for v in bm.verts if v.select == False]        
        for vert in verts:
            bm.verts.remove(vert)

        # Remove all verts not in a face
        face_verts = [v for f in bm.faces for v in f.verts]
        for vert in bm.verts:
            if vert not in face_verts:
                bm.verts.remove(vert)

        # Remove all faces that maybe are
        faces = [f for f in bm.faces if f.select == False]
        bmesh.ops.delete(bm, geom=faces, context='FACES')

        # Update data block
        bmesh.update_edit_mesh(self.bool_obj.data)

        # Clean mesh
        bpy.ops.mesh.remove_doubles(threshold=get_preferences().property.meshclean_remove_threshold)
        bpy.ops.mesh.dissolve_limited(angle_limit=get_preferences().property.meshclean_dissolve_angle)

        # Setup modal BM
        self.bm_backup = bm.copy()

        # If selection was not good return false
        if len(bm.verts) < 3:
            return False

        # Correct normal direction
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

        return True


    def cancel_cleanup(self):
        '''Remove: bool mod, bool obj'''

        bpy.ops.hops.display_notification(info="Failed: Select faces")

        if self.obj != None:
            if self.bool_mod != None:
                self.obj.modifiers.remove(self.bool_mod)
            if self.bool_obj != None:
                mesh = self.bool_obj.data
                bpy.data.objects.remove(self.bool_obj, do_unlink=True)
                bpy.data.meshes.remove(mesh, do_unlink=True)

    ####################################################
    #   MODAL FUNCTIONS
    ####################################################

    def update_edit_states(self, context):
        '''Update the edit states.'''

        if self.edit_state == Edit_States.OFFSET:
            self.edit_state = Edit_States.INSET
            context.space_data.shading.show_xray = False

        elif self.edit_state == Edit_States.INSET:
            self.edit_state = Edit_States.EXTRUDING
            context.space_data.shading.show_xray = True

        elif self.edit_state == Edit_States.EXTRUDING:
            self.edit_state = Edit_States.OFFSET
            context.space_data.shading.show_xray = False


    def setup_modal_bmesh(self):
        '''Sets up the modal bmesh for the next cycle.'''
    
        # Reset mesh for next cycle
        bpy.ops.object.mode_set(mode='OBJECT')
        self.bm_backup.to_mesh(self.bool_obj.data)
        bpy.ops.object.mode_set(mode='EDIT')

        bm = bmesh.from_edit_mesh(self.bool_obj.data)

        # Edit the mesh
        if self.edit_state == Edit_States.OFFSET:
            self.offset_bm_faces(offset=self.offset_value)
            self.bool_mod.object = None

        elif self.edit_state == Edit_States.INSET:
            self.offset_bm_faces(offset=self.offset_value)
            self.inset_bm_faces(bm, offset=self.inset_value)
            self.bool_mod.object = None

        elif self.edit_state == Edit_States.EXTRUDING:
            self.offset_bm_faces(offset=self.offset_value)
            self.inset_bm_faces(bm, offset=self.inset_value)
            self.extrude_bm_faces(bm, offset=self.extrude_value)
            self.bool_mod.object = self.bool_obj
            
        bmesh.update_edit_mesh(self.bool_obj.data)


    def offset_bm_faces(self, offset=0):
        '''Offset the faces (Like Alt S)'''

        bpy.ops.transform.shrink_fatten(value=offset, use_even_offset=True)


    def inset_bm_faces(self, bm, offset=0):
        '''Inset the faces (Like I/Inset)'''

        result = bmesh.ops.inset_region(
            bm, 
            faces=bm.faces,
            use_boundary=True,
            use_even_offset=True,
            use_interpolate=True,
            use_relative_offset=False,
            use_edge_rail=True,
            thickness=offset,
            depth=0,
            use_outset=False)

        bmesh.ops.delete(bm, geom=result['faces'], context='FACES')


    def extrude_bm_faces(self, bm, offset=0):
        '''Extrude the bmesh faces (Like E)'''

        bmesh.ops.solidify(
            bm,
            geom=bm.faces,
            thickness=offset)

        for face in bm.faces:
            face.select = True


    def simple_mod_sort(self):
        '''Place the bool mod in the mod stack.'''

        moves = 0
        for mod in reversed(self.obj.modifiers):
            if mod.type == 'BEVEL':
                break
            moves += 1

        while moves != 0:
            moves -= 1
            bpy.ops.object.modifier_move_up(modifier=self.bool_mod.name)

    ####################################################
    #   SHADERS
    ####################################################

    def remove_shaders(self):
        '''Remove shader handle.'''

        if self.draw_handle_2D:
            self.draw_handle_2D = bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle_2D, "WINDOW")


    def safe_draw_2D(self, context):
        method_handler(self.draw_shader_2D,
            arguments = (context,),
            identifier = 'Modal Shader 2D',
            exit_method = self.remove_shaders)


    def draw_shader_2D(self, context):
        '''Draw shader handle.'''

        self.flow.draw_2D()
        draw_modal_frame(context)

        if self.flow.is_open == True:
            return

        factor = dpi_factor()
        up = 40 * factor
        right = 40 * factor
        font_size = 16
        text_pos = (self.mouse_pos[0] + up, self.mouse_pos[1] + right)

        if self.edit_state == Edit_States.OFFSET:
            text = "Click to Inset"
            render_text(text=text, position=text_pos, size=font_size, color=self.color)

        elif self.edit_state == Edit_States.INSET:
            text = "Click to Extrude"
            render_text(text=text, position=text_pos, size=font_size, color=self.color)

        elif self.edit_state == Edit_States.EXTRUDING:
            text = "Click to Finish"
            render_text(text=text, position=text_pos, size=font_size, color=self.color)