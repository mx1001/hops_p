import bpy, bmesh
from bpy.props import IntProperty, BoolProperty, FloatProperty
from ... utils.addons import addon_exists
#from ... utils.operations import invoke_individual_resizing
from ... preferences import get_preferences
from ... ui_framework.master import Master
from ...ui_framework.utils.mods_list import get_mods_list
from ... utility.base_modal_controls import Base_Modal_Controls

# Cursor Warp imports
from ... utils.toggle_view3d_panels import collapse_3D_view_panels
from ... utils.modal_frame_drawing import draw_modal_frame
from ... utils.cursor_warp import mouse_warp
from ... addon.utility import method_handler


class HOPS_OT_VertcircleOperator(bpy.types.Operator):
    bl_idname = "view3d.vertcircle"
    bl_label = "Vert To Circle"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}
    bl_description = """Vert To_Circle
    
LMB - convert vert to circle
LMB + CTRL - convert nth vert to circle
Shift - Bypass Scale

**Requires Looptools**

"""

    divisions: IntProperty(name="Division Count", description="Amount Of Vert divisions", default=5, )
    radius: FloatProperty(name="Circle Radius", description="Circle Radius", default=0.2)
    message = "< Default >"
    nth_mode: BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"


    def draw(self, context):

        layout = self.layout
        if addon_exists("mesh_looptools"):
            layout.prop(self, "divisions")
            layout.prop(self, "c_offset")
        else:
            layout.label(text = "Looptools is not installed. Enable looptools in prefs")


    def invoke(self, context, event):

        if 'vertex_only' in bmesh.ops.bevel.__doc__:
            self.bm_bevel = bm_bevel_28
        else:
            self.bm_bevel = bm_bevel_29

        self.base_controls = Base_Modal_Controls(context=context, event=event)
        self.master = None

        if addon_exists("mesh_looptools"):
            self.c_offset = 40

            #self.divisions = get_preferences().property.circle_divisions
            self.div_past = self.divisions
            self.object = context.active_object

            if event.ctrl:
                bpy.ops.mesh.select_nth()

            self.object.update_from_editmode()
            self.bm = bmesh.from_edit_mesh(self.object.data)
            self.backup = self.object.data.copy()

            setup_verts(self.object, self.bm , self.divisions,  self.c_offset, self.bm_bevel)
            bpy.ops.mesh.looptools_circle(custom_radius=True, radius = self.radius)

            if not event.shift:

                #UI System
                self.master = Master(context=context)
                self.master.only_use_fast_ui = True
                self.original_tool_shelf, self.original_n_panel = collapse_3D_view_panels()
                self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.safe_draw_shader, (context,), 'WINDOW', 'POST_PIXEL')
                context.window_manager.modal_handler_add(self)
                return {'RUNNING_MODAL'}

        else:
            self.report({'INFO'}, "Looptools is not installed. Enable looptools in prefs")

        return {"FINISHED"}



    def modal (self, context, event):

        # Base Systems
        self.master.receive_event(event=event)
        self.base_controls.update(context, event)
        mouse_warp(context, event)

        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        if self.base_controls.scroll:
            self.divisions += self.base_controls.scroll
            if self.divisions <1 :
                self.divisions = 1

            restore(self.bm, self.object.data)
            setup_verts(self.object, self.bm , self.divisions,  self.c_offset, self.bm_bevel)
            bpy.ops.mesh.looptools_circle(custom_radius=True, radius = self.radius)

        elif self.base_controls.mouse:
            if get_preferences().property.modal_handedness == 'LEFT':
                self.radius -= self.base_controls.mouse
            else:
                self.radius += self.base_controls.mouse
            if self.radius <= 0.001:
                 self.radius =0.001
            bpy.ops.mesh.looptools_circle(custom_radius=True, radius = self.radius)

        if self.base_controls.confirm:
            bpy.data.meshes.remove(self.backup)
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            return {'FINISHED'}

        if self.base_controls.cancel:
            restore(self.bm, self.object.data)
            bmesh.update_edit_mesh(self.object.data, destructive = True)
            bpy.data.meshes.remove(self.backup)
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            return {'CANCELLED'}

        self.draw_ui(context)

        return {'RUNNING_MODAL'}


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
                win_list.append("{:.0f}".format(self.divisions))
                win_list.append("{:.3f}".format(self.radius))
            else:
                win_list.append("Circle")
                win_list.append("Divisions: {:.0f}".format(self.divisions))
                win_list.append("Radius: {:.3f}".format(self.radius))

            # Help
            help_list.append(["LMB", "Apply"])
            help_list.append(["RMB", "Cancel"])
            help_list.append(["Scroll", "Add divisions"])
            help_list.append(["Mouse", "Adjust the radius"])

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


def setup_verts(object, bm , divisions,  c_offset, bevel):
    '''Set up verts to be converted to circle by loop tools.'''
    
    selected_verts = [v for v in bm.verts if v.select]
    result = bevel(bm, input_geo=selected_verts, divisions=divisions, c_offset=c_offset)

    faces = result['faces']
    faces_clean = bmesh.ops.dissolve_faces (bm, faces = faces)

    for f in faces_clean['region']:
        f.select = True

    bmesh.update_edit_mesh(object.data, destructive = True)


def restore (bm, mesh):
    '''Reasign original mesh data back to the selected object.'''

    bmesh.ops.delete(bm, geom = bm.verts, context = 'VERTS')
    bm.from_mesh(mesh)


def bm_bevel_28(bm, input_geo= [], divisions = 2, c_offset = 40):
    return bmesh.ops.bevel (bm, geom = input_geo, vertex_only = True , offset = c_offset,
loop_slide = True, offset_type = 'PERCENT', clamp_overlap = True, segments = divisions, profile = 0 )

def bm_bevel_29(bm, input_geo= [], divisions = 2, c_offset = 40):
    return bmesh.ops.bevel (bm, geom = input_geo, affect = 'VERTICES' , offset = c_offset,
loop_slide = True, offset_type = 'PERCENT', clamp_overlap = True, segments = divisions, profile = 0 )
