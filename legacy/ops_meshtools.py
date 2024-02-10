import bpy, bmesh
from bpy.props import *
import bpy.utils.previews
from .. utility.base_modal_controls import Base_Modal_Controls
from .. ui_framework.master import Master
from .. ui_framework.utils.mods_list import get_mods_list
from .. preferences import get_preferences

# Cursor Warp imports
from .. utils.toggle_view3d_panels import collapse_3D_view_panels
from .. utils.modal_frame_drawing import draw_modal_frame
from .. utils.cursor_warp import mouse_warp
from .. addon.utility import method_handler

#############################
# FaceOps Start Here
#############################

# Sets Up Faces For Grating


class HOPS_OT_FacegrateOperator(bpy.types.Operator):
    """
    Convert QUAD(s) To Grate Pattern

    """
    bl_idname = "fgrate.op"
    bl_label = "FaceGrate"
    bl_options = {'REGISTER', 'UNDO', 'BLOCKING'}

    # def execute(self, context):
    #     bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
    #     bpy.ops.mesh.poke()

    #     # Threshold is a tricky devil
    #     bpy.ops.mesh.tris_convert_to_quads(face_threshold=0.698132, shape_threshold=1.39626)
    #     bpy.ops.mesh.inset(thickness=0.004, use_individual=True)
    #     return {'FINISHED'}
    inset: bpy.props.FloatProperty(
        name = "Inset",
        description = "Amount by which to inset",
        default = 0.05,
        min = 0)

    ridge: bpy.props.FloatProperty(
        name = "Ridge",
        description = "Ridge depth",
        default = 0,
        min = 0)
    
    def invoke(self, context, event):
        obj = bpy.context.active_object
        obj.update_from_editmode()
        self.mesh = obj.data
        self.bm =  bmesh.from_edit_mesh(self.mesh)
        bmesh.update_edit_mesh(self.mesh)
        self.backup = obj.data.copy()

        self.selection = [f for f in self.bm.faces if f.select and len(f.edges)==4]
        self.divisions = 0
        if len(self.selection) ==1:
            self.divisions = 1

        if not self.selection:
            self.report({'INFO'}, "NO SELECTED QUADS")
            return {'CANCELLED'}

        context.window_manager.modal_handler_add(self)
        self.grate_faces(self.bm, self.selection)

        # Base Systems
        self.master = Master(context=context)
        self.master.only_use_fast_ui = True
        self.base_controls = Base_Modal_Controls(context, event)
        self.original_tool_shelf, self.original_n_panel = collapse_3D_view_panels()
        self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.safe_draw_shader, (context,), 'WINDOW', 'POST_PIXEL')
        return {'RUNNING_MODAL'}


    def modal(self, context, event):
        
        # Base Systems
        self.master.receive_event(event=event)
        self.base_controls.update(context, event)
        mouse_warp(context, event)

        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        elif self.base_controls.mouse:
            if  event.ctrl:
                self.inset += self.base_controls.mouse
            else:
                self.ridge += self.base_controls.mouse

            restore_bmesh(self.bm, self.backup)

            self.selection = [elem for elem in self.bm.faces if elem.select]
            self.grate_faces(self.bm, self.selection)
        elif self.base_controls.scroll:
            self.divisions += self.base_controls.scroll
            if self.divisions== -1:
                self.divisions =0

            restore_bmesh(self.bm, self.backup)
            self.selection = [elem for elem in self.bm.faces if elem.select]
            self.grate_faces(self.bm, self.selection)
            
        elif self.base_controls.confirm:
            bpy.data.meshes.remove(self.backup)
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            self.report({'INFO'}, "FINISHED")
            return {'FINISHED'}
        elif self.base_controls.cancel:
            restore_bmesh(self.bm, self.backup)
            bmesh.update_edit_mesh(self.mesh)
            bpy.data.meshes.remove(self.backup)
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            self.report({'INFO'}, "CANCELLED")
            return {'CANCELLED'}
        
        self.draw_ui(context)
        return {'RUNNING_MODAL'}


    def grate_faces(self, bm, selection ):
        if self.divisions>0:
            edges = set()
            for face in selection:
                edges.update(face.edges)
            retrun= bmesh.ops.subdivide_edges(bm, edges = list(edges), cuts = self.divisions, use_grid_fill = True)
            selection = [f for f in retrun['geom_inner'] if type(f) == bmesh.types.BMFace] + selection
        
        poke = bmesh.ops.poke(bm, faces = selection )
        join= bmesh.ops.join_triangles(bm, faces = poke['faces'], angle_face_threshold = 3.14, angle_shape_threshold = 1.57)# cmp_seam, cmp_sharp, cmp_uvs, cmp_vcols, cmp_materials)
        result = bmesh.ops.inset_individual(bm, faces= join['faces'], thickness = self.inset , 
           use_even_offset= True, use_interpolate = True , use_relative_offset = False,  )
        result2 = bmesh.ops.inset_individual(bm, faces= join['faces'], thickness = 0, depth = -self.ridge, 
           use_even_offset = True, use_interpolate = True , use_relative_offset = False,  )
        bmesh.update_edit_mesh(self.mesh, destructive = True)
    

    def draw_ui(self, context):

            self.master.setup()

            # -- Fast UI -- #
            if self.master.should_build_fast_ui():

                win_list = []
                help_list = []
                mods_list = []
                active_mod = ""

                # Main
                if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1:
                    win_list.append("{:.3f}".format(self.inset))
                    win_list.append("{:.3f}".format(self.ridge))
                else:
                    win_list.append("Grate")
                    win_list.append("Inset: {:.3f}".format(self.inset))
                    win_list.append("Ridge: {:.3f}".format(self.ridge))
                    win_list.append(F"Divisions: {self.divisions}" )

                # Help
                help_list.append(["LMB", "Apply"])
                help_list.append(["RMB", "Cancel"])
                help_list.append(["Scroll", "Divisions"])
                help_list.append(["CTRL+Mouse", "Adjust Inset"])
                help_list.append(["Mouse", "Adjust Ridge"])

                # Mods
                mods_list = get_mods_list(mods=bpy.context.active_object.modifiers)

                self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="Tthick", mods_list=mods_list, active_mod_name=active_mod)

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


# Sets Up Faces For Knurling


class HOPS_OT_FaceknurlOperator(bpy.types.Operator):
    """
    Convert Face To Knurl Pattern

    """
    bl_idname = "fknurl.op"
    bl_label = "FaceKnurl"
    bl_options = {'REGISTER', 'UNDO', 'BLOCKING'}
    """
    knurlSubd = IntProperty(name="KnurlSubdivisions", description="Amount Of Divisions", default=0, min = 0, max = 5)"""


    inset: bpy.props.FloatProperty(
    name = "Inset",
    description = "Amount by which to inset",
    default = 0.05,
    min = 0)

    height: bpy.props.FloatProperty(
        name = "Height",
        description = "Knurling height",
        default = 0)
    
    def invoke(self, context, event):
        obj = bpy.context.active_object
        obj.update_from_editmode()
        self.mesh = obj.data
        self.bm =  bmesh.from_edit_mesh(self.mesh)
        self.backup = self.mesh.copy()

        self.selection = [f for f in self.bm.faces if f.select and len(f.edges)==4]
        self.flat = False
        self.divisions = 0
        # if len(self.selection) ==1:
        #     self.divisions = 1

        if not self.selection:
            self.report({'INFO'}, "NO SELECTED QUADS")
            return {'CANCELLED'}

        self.knurl_faces(self.bm, self.selection)

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
        
        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        elif self.base_controls.mouse:
            if  event.ctrl:
                self.inset += self.base_controls.mouse
            else:
                self.height += self.base_controls.mouse
            self.edit()

        elif self.base_controls.scroll:
            self.divisions += self.base_controls.scroll
            if self.divisions== -1:
                self.divisions =0
            self.edit()
        
        elif event.type == 'F' and event.value == 'PRESS':
            self.flat = not self.flat
            self.edit()

        elif self.base_controls.confirm:
            bpy.data.meshes.remove(self.backup)
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            self.report({'INFO'}, "FINISHED")
            return {'FINISHED'}

        elif self.base_controls.cancel:
            restore_bmesh(self.bm, self.backup)
            bmesh.update_edit_mesh(self.mesh)
            bpy.data.meshes.remove(self.backup)
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            self.report({'INFO'}, "CANCELLED")
            return {'CANCELLED'}
        
        self.draw_ui(context)
        return {'RUNNING_MODAL'}

    def edit (self):
        restore_bmesh(self.bm, self.backup)
        self.selection = [elem for elem in self.bm.faces if elem.select]
        self.knurl_faces(self.bm, self.selection)


    def knurl_faces(self, bm, selection ):
        if self.divisions>0:
            edges = set()
            for face in selection:
                edges.update(face.edges)
            retrun= bmesh.ops.subdivide_edges(bm, edges = list(edges), cuts = self.divisions, use_grid_fill = True)
            selection = [f for f in retrun['geom_inner'] if type(f) == bmesh.types.BMFace] + selection
        
        result = bmesh.ops.inset_individual(bm, faces= selection, thickness = self.inset , 
           use_even_offset= True, use_interpolate = True , use_relative_offset = False,  depth = self.height if self.flat else 0 )
        
        if not self.flat:
            poke = bmesh.ops.poke(bm, faces = selection, offset = self.height ) 

        bmesh.update_edit_mesh(self.mesh, destructive = True)
    

    def draw_ui(self, context):

            self.master.setup()

            # -- Fast UI -- #
            if self.master.should_build_fast_ui():

                win_list = []
                help_list = []
                mods_list = []
                active_mod = ""

                # Main
                if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1:
                    win_list.append("{:.3f}".format(self.inset))
                    win_list.append("{:.3f}".format(self.height))
                else:
                    win_list.append("Knurl")
                    win_list.append("Inset: {:.3f}".format(self.inset))
                    win_list.append("Height: {:.3f}".format(self.height))
                    win_list.append(F"Divisions: {self.divisions}" )
                    win_list.append(F"FLat: {self.flat}" )

                # Help
                help_list.append(["F", "Toggle Flat"])
                help_list.append(["LMB", "Apply"])
                help_list.append(["RMB", "Cancel"])
                help_list.append(["Scroll", "Divisions"])
                help_list.append(["CTRL+Mouse", "Adjust Inset"])
                help_list.append(["Mouse", "Adjust Height"])
               

                # Mods
                mods_list = get_mods_list(mods=bpy.context.active_object.modifiers)

                self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="Tthick", mods_list=mods_list, active_mod_name=active_mod)

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


#############################
# Panelling Operators Start Here
#############################

# Panel From An Edge Ring Selection
# Scale Dependant for now.


class HOPS_OT_EntrenchOperatorA(bpy.types.Operator):
    """
    Extrude the face selection modally.

    """
    bl_idname = "entrench.selection"
    bl_label = "Entrench"
    bl_options = {'REGISTER', 'UNDO', 'BLOCKING'}


    depth: bpy.props.FloatProperty(
        name = "depth",
        description = "",
        default = 0)

    shrink: bpy.props.FloatProperty(
        name = "shrink",
        description = "",
        default = 0,
        min = 0)    

    b_width: bpy.props.FloatProperty(
        name = "b_width",
        description = "",
        default = 0,
        min = 0)

    b_profile: bpy.props.FloatProperty(
        name = "b_profile",
        description = "",
        default = 1,
        min = 0,
        max = 1)

    b_segments: bpy.props.IntProperty(
        name = "b_segments",
        description = "",
        default = 2,
        min = 1)
    
    def invoke(self, context, event):

        if 'vertex_only' in bmesh.ops.bevel.__doc__:
            self.bm_bevel = self.bm_bevel_28
        else:
            self.bm_bevel = self.bm_bevel_29

        obj = bpy.context.active_object
        obj.update_from_editmode()
        self.mesh = obj.data
        self.bm =  bmesh.from_edit_mesh(self.mesh)
        self.backup = self.mesh.copy()
        self.selection = [f for f in self.bm.faces if f.select]
        self.b_mode_both = False
        self.shrink_mode = False
        if not self.selection:
            self.report({'INFO'}, "NO SELECTED EDGES/FACES")
            return {'CANCELLED'}

        self.entrench_faces(self.bm, self.selection)

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
        
        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        elif self.base_controls.mouse:

            if not event.ctrl:
                if not self.shrink_mode:
                    self.depth += self.base_controls.mouse
                else:
                    self.shrink += self.base_controls.mouse
            else:
                self.b_width += self.base_controls.mouse

            self.edit_bm()
        elif self.base_controls.scroll:
            if not event.ctrl:
                self.b_segments +=self.base_controls.scroll
            else:
                self.b_profile += self.base_controls.scroll*0.1
            self.edit_bm ()
        
        elif event.type == 'S' and event.value == 'PRESS':
            self.shrink_mode = not self.shrink_mode
            self.report({'INFO'}, F'Shirnk : {"ON" if self.shrink_mode else "OFF"}')
        
        elif event.type == 'B' and event.value == 'PRESS':
            self.b_mode_both = not self.b_mode_both
            self.edit_bm()
            self.report({'INFO'}, F'BMode : {"BOTH" if self.b_mode_both else "BOTTOM"}')

        elif self.base_controls.confirm:
            bpy.data.meshes.remove(self.backup)
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            self.report({'INFO'}, "FINISHED")
            return {'FINISHED'}

        elif self.base_controls.cancel:
            restore_bmesh(self.bm, self.backup)
            bmesh.update_edit_mesh(self.mesh)
            bpy.data.meshes.remove(self.backup)

            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            self.report({'INFO'}, "CANCELLED")
            return {'CANCELLED'}
        
        self.draw_ui(context)
        return {'RUNNING_MODAL'}

        
    def edit_bm(self):
        restore_bmesh(self.bm, self.backup)
        self.selection = [elem for elem in self.bm.faces if elem.select]
        self.entrench_faces(self.bm, self.selection)
        


    def entrench_faces(self, bm, selection ):
        result = bmesh.ops.inset_region(bm, faces= selection, thickness = self.shrink, depth=-self.depth , use_boundary = True,
        use_even_offset= True, use_interpolate = True , use_relative_offset = False, use_edge_rail = True,  use_outset = False)
        select_boundary = []
        if self.b_mode_both:
            select_boundary = region_bounds(result['faces'])
        else:
            select_boundary = region_bounds(selection)
        if self.b_width:
            self.bm_bevel(bm, input_geo = select_boundary)
        
        bmesh.update_edit_mesh(self.mesh, destructive = True)

    def bm_bevel_28(self, bm, input_geo = []):
        return bmesh.ops.bevel(bm, geom =input_geo, offset = self.b_width, offset_type = 'WIDTH',
        segments = self.b_segments, profile = self.b_profile, vertex_only = False)

    def bm_bevel_29(self, bm, input_geo = []):
        return bmesh.ops.bevel(bm, geom =input_geo, offset = self.b_width, offset_type = 'WIDTH',
        segments = self.b_segments, profile = self.b_profile, affect = 'EDGES')

    def draw_ui(self, context):

            self.master.setup()

            # -- Fast UI -- #
            if self.master.should_build_fast_ui():

                win_list = []
                help_list = []
                mods_list = []
                active_mod = ""

                # Main
                if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1:
                    win_list.append("{:.3f}".format(self.depth))
                    win_list.append("{:.3f}".format(self.shrink))
                    
                else:
                    win_list.append("Entrench")
                    win_list.append("Depth: {:.3f}".format(self.depth))
                    win_list.append("Shrink: {:.3f}".format(self.shrink))
                    win_list.append("Bevel: {:.3f}".format(self.b_width))
                    win_list.append(F"Segments:{self.b_segments}")
                    win_list.append("Profile: {:.3f}".format(self.b_profile))

                # Help
                help_list.append(["LMB", "Apply"])
                help_list.append(["RMB", "Cancel"])
                help_list.append(["S", "Toggle Shrink"])
                help_list.append(["CTRL+Scroll", "Adjust Profile"])
                help_list.append(["CTRL+Mouse", "Adjust Bevel"])
                help_list.append(["Mouse", "Adjust Depth"])

                # Mods
                mods_list = get_mods_list(mods=bpy.context.active_object.modifiers)

                self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="Tthick", mods_list=mods_list, active_mod_name=active_mod)

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



# Make A Panel Loop From Face Selection
# Scale Dependant for now.
class HOPS_OT_PanelOperatorA(bpy.types.Operator):
    """
    Convert edge selection to panel modally.

    """
    bl_idname = "quick.panel"
    bl_label = "Sharpen"
    bl_options = {'REGISTER', 'UNDO', 'BLOCKING'}

    inset: bpy.props.FloatProperty(
        name = "Inset",
        description = "Amount by which to inset",
        default = 0.1,
        min = 0)

    ridge: bpy.props.FloatProperty(
        name = "Ridge",
        description = "Ridge depth",
        default = 0,
        min = 0)

    ridge_shrink: bpy.props.FloatProperty(
        name = "Ridge Scale",
        description = "Ridge Scale",
        default = 0,
        min = 0)
    
    def invoke(self, context, event):

        if 'vertex_only' in bmesh.ops.bevel.__doc__:
            self.bm_bevel = self.bm_bevel_28
        else:
            self.bm_bevel = self.bm_bevel_29

        obj = bpy.context.active_object
        obj.update_from_editmode()
        self.mesh = obj.data
        self.bm =  bmesh.from_edit_mesh(self.mesh)
        self.backup = self.mesh.copy()
        self.selection = [f for f in self.bm.faces if f.select]
        self.mode = 'faces'
        self.ridge_shrink_mode = False
        self.make_panel = self.panel_faces
        self.mode_dict = {"faces":self.panel_faces, "edges": self.panel_edges}
        self.edge_boudnary = False
        if not self.selection:
            self.selection = [e for e in self.bm.edges if e.select]
            self.make_panel = self.panel_edges
            self.mode = 'edges'
        if not self.selection:
            self.report({'INFO'}, "NO SELECTED EDGES/FACES")
            return {'CANCELLED'}

        self.make_panel(self.bm, self.selection)

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
        
        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        elif self.base_controls.mouse:
            if  event.ctrl:
                self.inset += self.base_controls.mouse
            else:
                if not self.ridge_shrink_mode:
                    self.ridge += self.base_controls.mouse
                else:
                    self.ridge_shrink += self.base_controls.mouse
            self.edit_bm()
        elif event.type == 'S' and event.value == 'PRESS':
            self.ridge_shrink_mode = not self.ridge_shrink_mode
            self.report({'INFO'}, F'Shirnk : {"ON" if self.ridge_shrink_mode else "OFF"}')
        elif event.type == 'A' and event.value == 'PRESS':
            self.mode = "faces" if self.mode == "edges" else "edges"
            self.make_panel = self.mode_dict[self.mode]
            self.edit_bm()
            self.report({'INFO'}, F'Mode : {self.mode.capitalize()}')
        elif event.type == 'B' and event.value == 'PRESS':
            self.edge_boudnary = not self.edge_boudnary
            if self.edge_boudnary:
                self.mode = "edges"
                self.make_panel = self.panel_edges
            self.edit_bm()
            self.report({'INFO'}, F'Boundary : {"ON" if self.edge_boudnary else "OFF"}')
        elif self.base_controls.confirm:
            bpy.data.meshes.remove(self.backup)
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            self.report({'INFO'}, "FINISHED")
            return {'FINISHED'}
        elif self.base_controls.cancel:
            restore_bmesh(self.bm, self.backup)
            bmesh.update_edit_mesh(self.mesh)
            bpy.data.meshes.remove(self.backup)

            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            self.report({'INFO'}, "CANCELLED")
            return {'CANCELLED'}
        
        self.draw_ui(context)
        return {'RUNNING_MODAL'}
    

    def edit_bm (self):
        restore_bmesh(self.bm, self.backup)
        #bmesh.update_edit_mesh(self.mesh)
        if self.edge_boudnary and self.mode == "edges":
            bpy.ops.mesh.region_to_loop()

        self.selection = [elem for elem in getattr(self.bm, self.mode) if elem.select]
        self.make_panel(self.bm, self.selection)


    def panel_faces(self, bm, selection ):
        result = bmesh.ops.inset_region(bm, faces= selection, thickness = self.inset , use_boundary = True,
        use_even_offset= True, use_interpolate = True , use_relative_offset = False, use_edge_rail = True,  use_outset = False)
        result2 = bmesh.ops.inset_region(bm, faces= result['faces'], thickness = self.ridge_shrink, depth = -self.ridge , use_boundary = True,
        use_even_offset= True, use_interpolate = True, use_relative_offset= False, use_edge_rail = True,  use_outset = False)
        bmesh.update_edit_mesh(self.mesh, destructive = True)


    def panel_edges(self, bm, selection ):
        result = self.bm_bevel( bm, input_geo=selection)
        result2 = bmesh.ops.inset_region(bm, faces= result['faces'], thickness = self.ridge_shrink, depth = -self.ridge , use_boundary = True,
        use_even_offset= True, use_interpolate = True, use_relative_offset= False, use_edge_rail = True,  use_outset = False)
        bmesh.update_edit_mesh(self.mesh, destructive = True)

    def bm_bevel_28(self, bm, input_geo = []):
        return bmesh.ops.bevel(bm, geom =input_geo, offset = self.inset, offset_type = 'WIDTH', segments = 1, profile =1,  vertex_only = False)

    def bm_bevel_29(self, bm, input_geo = []):
        return bmesh.ops.bevel(bm, geom =input_geo, offset = self.inset, offset_type = 'WIDTH', segments = 1, profile =1, affect = 'EDGES')


    def draw_ui(self, context):

            self.master.setup()

            # -- Fast UI -- #
            if self.master.should_build_fast_ui():

                win_list = []
                help_list = []
                mods_list = []
                active_mod = ""

                # Main
                if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1:
                    win_list.append("{:.3f}".format(self.inset))
                    win_list.append("{:.3f}".format(self.ridge))
                    
                else:
                    win_list.append("Panel")
                    win_list.append(F"Mode: {self.mode.capitalize()}")
                    if self.mode == "edges":
                        win_list.append(F'Boundary : {"ON" if self.edge_boudnary else "OFF"}')
                    win_list.append("Inset: {:.3f}".format(self.inset))
                    win_list.append("Ridge: {:.3f}".format(self.ridge))
                    win_list.append("Shrink: {:.3f}".format(self.ridge_shrink))

                # Help
                help_list.append(["LMB", "Apply"])
                help_list.append(["RMB", "Cancel"])
                help_list.append(["B", "Boundary"])
                help_list.append(["A", "Toggle EDGES/FACES mode"])
                help_list.append(["S", "Shrink Ridge"])
                help_list.append(["CTRL+Mouse", "Adjust Inset"])
                help_list.append(["Mouse", "Adjust Ridge"])

                # Mods
                mods_list = get_mods_list(mods=bpy.context.active_object.modifiers)

                self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="Tthick", mods_list=mods_list, active_mod_name=active_mod)

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

#############################
# OrginAndApply Operators Start Here
#############################

# apply all 2 except Loc at once and be done


class HOPS_OT_StompObjectnoloc(bpy.types.Operator):
    """
    Apply rotation and scale.

    """
    bl_idname = "stomp2.object"
    bl_label = "stompObjectnoLoc"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        # bpy.ops.object.location_clear()
        return {'FINISHED'}


def region_bounds(faces):
    faces = set(faces)

    edges = [edge 
    for face in faces
    for edge in face.edges
    if  not edge.link_faces or not faces.issuperset(edge.link_faces) ]  

    return edges

def restore_bmesh (bm, mesh):

    bmesh.ops.delete(bm, geom = bm.verts, context = 'VERTS')
    bm.from_mesh(mesh)
    
