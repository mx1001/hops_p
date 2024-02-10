import bpy
import bmesh
import statistics
from mathutils import Vector, Matrix
from ... utility import collections, object, math
from ... preferences import get_preferences
from ...ui_framework.operator_ui import Master
from ...utils.objects import set_active


class HOPS_OT_MOD_Lattice(bpy.types.Operator):
    bl_idname = "hops.mod_lattice"
    bl_label = "Add Lattice Modifier"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """LMB - Add Lattice Modifier for selection with world-oriented Lattice
LMB + Shift - Add Lattice Modifier for each object with object-oriented lattice
CTRL - Force new lattice modifier

"""
    modified: bpy.props.BoolProperty(
    name="Modified", description="Use final geometry. Edit mode only", default = False)
    #i've set it false by default, as calculation of final geo can get quite heavy
    individual: bpy.props.BoolProperty(
    name="Individual", description="Assign individual lattice per object", default = False)

    called_ui = False

    def __init__(self):

        HOPS_OT_MOD_Lattice.called_ui = False

    def draw (self, context):
        if self.edit_init:
            self.layout.prop(self, 'modified')
        self.layout.prop(self, 'individual')

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        self.selected = []
        self.edit_init= False
        if context.mode == 'EDIT_MESH':
            self.edit_init = True

        self.ctrl_event = False
        if event.ctrl:
            self.ctrl_event=True

        if event.shift:
            self.individual = True

        return self.execute(context)

    def execute (self, context):
        context.view_layer.update()
        self.selected = [ob for ob in context.selected_objects if ob.type in {'MESH', 'CURVE', 'FONT', 'SURFACE'}]

        if self.individual:
            lattices = []
            for obj in self.selected:

                if self.ctrl_event or not self.lattice_modifiers(obj):
                    coords = self.get_vert_coords(obj,context)
                    lattice_object = self.add_lattice_obj(context, obj)
                    self.add_lattice_modifier(context, obj, lattice_object)
                    self.lattice_transform(obj, lattice_object,coords)
                    lattices.append(lattice_object)

            if lattices:
                bpy.ops.object.mode_set(mode = 'OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                for l in lattices:
                    set_active (l, select=True)
        else:
            coords_all=[]
            for obj in self.selected:

                if self.ctrl_event or not self.lattice_modifiers(obj):
                    coords= []
                    if context.mode == 'EDIT_MESH':
                        coords= self.get_vert_coords(obj, context, obj.matrix_world)
                        if coords != None:
                            coords_all.extend(coords)

                    else:
                        coords_all.extend(object.bound_coordinates(obj, obj.matrix_world ))

            if len(coords_all)>0:
                lattice_object = self.add_lattice_obj(context, context.active_object)
                self.lattice_transform(obj, lattice_object, coords_all)
                for obj in self.selected :
                    self.add_lattice_modifier(context, obj, lattice_object)
                if context.mode == 'EDIT_MESH':
                    bpy.ops.object.mode_set(mode = 'OBJECT')
                set_active(lattice_object, select=True, only_select= True)


        # Operator UI
        if not HOPS_OT_MOD_Lattice.called_ui:
            HOPS_OT_MOD_Lattice.called_ui = True

            ui = Master()
            draw_data = [
                ["LATTICE"],
                ["Modified", self.modified]]
            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return {"FINISHED"}

    @staticmethod
    def lattice_modifiers(obj):
        return [modifier for modifier in obj.modifiers if modifier.type == "LATTICE"]

    def add_lattice_modifier(self, context, obj, lattice_object):
        lattice_modifier = obj.modifiers.new(name="Lattice", type="LATTICE")
        lattice_modifier.object = lattice_object
        if context.mode == 'EDIT_MESH' and obj.type == 'MESH':

            lattice_modifier.vertex_group = obj.vertex_groups.active.name

    def add_lattice_obj(self, context, obj, ):
        lattice_data = bpy.data.lattices.new('lattice')
        lattice_obj = bpy.data.objects.new('lattice', lattice_data)
        collection = collections.find_collection(context, obj)
        collection.objects.link(lattice_obj)
        lattice_obj.data.use_outside = True

        return lattice_obj

    def lattice_transform (self, obj, lattice_obj, coords = None  ):
        if coords != None:

            box = math.coords_to_bounds(coords)
            lattice_obj.location =  math.coords_to_center(box)
            lattice_obj.dimensions = math.dimensions(box)
            if self.individual:
                lattice_obj.location =  obj.matrix_world @ math.coords_to_center(box)
                obj_scale = obj.matrix_world.to_scale()
                for i in range(3):
                     lattice_obj.scale[i] *= obj_scale[i]
                lattice_obj.rotation_euler = obj.matrix_world.to_euler()

        else:
            lattice_obj.location = obj.matrix_world @ math.coords_to_center(obj.bound_box)
            lattice_obj.dimensions = obj.dimensions
            lattice_obj.rotation_euler = obj.matrix_world.to_euler() 

        lattice_obj.scale *=1.01 #increase lattice szize a bit to avoid potential with bounding verts


    def get_vert_coords(self, obj, context, matrix = Matrix()):
        if context.mode == 'EDIT_MESH' and obj.type == 'MESH':
            coords = []
            lattice_verts = obj.vertex_groups.new(name='HardOps_Lattice')
            group_idx = lattice_verts.index


            bm = bmesh.from_edit_mesh(obj.data)
            bm.verts.layers.deform.verify()

            bm_deform = bm.verts.layers.deform.active
            
            selected_vert = [v for v in bm.verts if v.select]
            if not selected_vert:
                return None
            for v in selected_vert:
                v[bm_deform][group_idx] = 1
                    
            obj.update_from_editmode()

            if self.modified :
                coords = self.mod_coord(context,obj,group_idx, matrix)

            else:
                coords = [ matrix @ v.co for v in obj.data.vertices if group_idx in [ vg.group for vg in v.groups]]
               
            return coords
        else:
            return None


    @staticmethod
    #return vertex coordinates from final vertex groups
    def mod_coord (context, obj, group_idx, matrix = Matrix()):
        depsgraph = context.evaluated_depsgraph_get()
        bm = bmesh.new()
        bm.from_object(obj,depsgraph, True)

        vert_deform = bm.verts.layers.deform.active
        coords_b = [matrix @ v.co for v in bm.verts if group_idx in v[vert_deform ]]

        bm.free()

        return coords_b
