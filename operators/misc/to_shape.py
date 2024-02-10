import bpy
import bmesh
import bpy.utils.previews
from math import radians
from ... preferences import get_preferences
from ... utils.blender_ui import get_dpi_factor
from ... utils.context import ExecutionContext
from bpy.props import EnumProperty, FloatProperty, BoolProperty
from mathutils import Vector, Matrix, Euler
from ... utility import collections, object, math , modifier

class HOPS_OT_Conv_To_Shape(bpy.types.Operator):
    bl_idname = "hops.to_shape"
    bl_label = "To_Shape"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """To_Shape
Convert selection to a myriad of shapes including empties
    
LMB - Converts selection to single primitive
LMB+SHIFT - Creates primitive per object
LMB+CTRL - Parent selection to empties

"""
#general
    individual: bpy.props.BoolProperty(
    name="Individual", description="Create shape per object using its local space", default = False)

    equalize: bpy.props.BoolProperty(
    name="Equalize", description="Make all dimensions equal", default = False)

    equalize_radius: bpy.props.BoolProperty(
    name="Radius only", description="Make all but longest dimension equal", default = False)

    modified: bpy.props.BoolProperty(
        name="Modified",
        description="Take the bounding box dimensions from the modified object",
        default=True)

    alignment: bpy.props.EnumProperty(
        name="Alignment",
        description="What axis to allign along",
        items=[
            ('AUTO_OBJECT', "AUTO_OBJECT", "Allign along longest object dimension"),
            ('AUTO_MESH', "AUTO_MESH", "Allign along longest mesh dimension"),
            ('X', "X", "Allign along X axis"),
            ('Y', "Y", "Allign along Y axis"),
            ('Z', "Z", "Allign along Z axis"),
            ],
        default='AUTO_OBJECT')
    scale: bpy.props.FloatProperty(
        name="Scale",
        description="Scale",
        default=1)
    
    copy_1st_bvl: bpy.props.BoolProperty(
        name="Copy 1st bevel",
        description="Copy 1st bevel of targe object",
        default=False)
    copy_1st_bvl_angle_only: bpy.props.BoolProperty(
        name="Angle only",
        description="Only consider Angle limit mode Bevels",
        default=False)

    parent_shape: bpy.props.BoolProperty(
        name="Parent shape to selection",
        description="Parent shape to selectio",
        default=False)
    parent_shape_inverse: bpy.props.BoolProperty(
        name="Inverse",
        description="Invert parenting",
        default=False)

##cylinder
    cyl_segments: bpy.props.IntProperty(
        name="Segments",
        description="Number of segments",
        default=32,
        min=3)
    cyl_diameter1: bpy.props.FloatProperty(
        name="Diameter 1",
        description="Diameter 1",
        default=1)

    cyl_diameter2: bpy.props.FloatProperty(
        name="Diameter 2",
        description="Diameter 2",
        default=1)

##sphere
    sphere_segments: bpy.props.IntProperty(
        name="Segments",
        description="Nmber of segments",
        default=32,
        min=3)
    sphere_rings: bpy.props.IntProperty(
        name="Rings",
        description="Number of rings",
        default=16,
        min=3)

    sphere_diameter: bpy.props.FloatProperty(
        name="Diameter",
        description="Diameter",
        default=1)

##plane
    axis: bpy.props.EnumProperty(
        name="Axis",
        description="What side to create planeo on",
        items=[
            ('+X', "+X", "Create a plane on the +X axis"),
            ('+Y', "+Y", "Create a plane on the +Y axis"),
            ('+Z', "+Z", "Create a plane on the +Z axis"),
            ('-X', "-X", "Create a plane on the -X axis"),
            ('-Y', "-Y", "Create a plane on the -Y axis"),
            ('-Z', "-Z", "Create a plane on the -Z axis")],
        default='+X')

    offset: bpy.props.FloatProperty(
        name="Offset",
        description="Offset plane from selection",
        default=0)
# empty
    empty_display: bpy.props.EnumProperty(
        name="Display type",
        description="Empty display type",
        items=[
        ('PLAIN_AXES', 'PLAIN_AXES', 'PLAIN_AXES'), 
        ('SINGLE_ARROW', 'SINGLE_ARROW', 'SINGLE_ARROW'),
        ('CIRCLE', 'CIRCLE', 'CIRCLE'),
        ('CUBE', 'CUBE', 'CUBE'),
        ('SPHERE', 'SPHERE', 'SPHERE'),
        ('ARROWS', 'ARROWS', 'ARROWS'),
        ('CONE', 'CONE', 'CONE') ],
        default='PLAIN_AXES')


#selector
    primitive_type: bpy.props.EnumProperty(
        name="Primitive",
        description="Primitive type",
        items=[
            ('Cube', "Cube", "Cube"),
            ('Plane', "Plane", "Plane"),
            ('Cylinder', "Cylinder", "Cylinder"),
            ('Sphere', "Sphere", "Sphereylinder"),
           # ('Monkey', "Monkey", "Monkey"),
            ('Empty', 'Empty', 'Empty')
            ],

        default='Cube')

    def draw(self, context):
        self.layout.prop(self, 'primitive_type')
        self.layout.prop(self, 'individual')
        self.layout.prop(self, 'equalize')
        if self.equalize:
            self.layout.prop(self, 'equalize_radius')
        self.layout.prop(self, 'modified')
        self.layout.prop(self, 'scale')
        self.layout.prop(self, 'parent_shape')
        if self.parent_shape:
            self.layout.prop(self, 'parent_shape_inverse')
        if self.primitive_type not in self.no_bevel_club :
            self.layout.prop(self, 'copy_1st_bvl')
            if self.copy_1st_bvl:
                self.layout.prop(self, 'copy_1st_bvl_angle_only')
        if self.primitive_type == 'Cylinder':
            self.layout.prop(self, 'cyl_segments')
            self.layout.prop(self, 'cyl_diameter1')
            self.layout.prop(self, 'cyl_diameter2')
            self.layout.prop(self, 'alignment')
        if self.primitive_type == 'Plane':
            self.layout.prop(self, "axis")
            self.layout.prop(self, "offset")
        if self.primitive_type == 'Sphere':
            self.layout.prop(self, "sphere_segments")
            self.layout.prop(self, "sphere_rings")
            self.layout.prop(self, "sphere_diameter")
            self.layout.prop(self, 'alignment')
        if self.primitive_type == 'Empty':
            self.layout.prop(self, "empty_display")



    @classmethod
    def poll(cls, context):
        return context.active_object or context.selected_objects

    def invoke (self, context, event):
        if event.shift:
            self.individual = True
        else:
            self.individual = False
        
        if event.ctrl:
            self.primitive_type = 'Empty'
            self.individual = True
            self.parent_shape = True
            self.parent_shape_inverse = True
            self.empty_display = 'CUBE'

        self.no_bevel_club = {'Plane', 'Empty'}

        return self.execute(context)

    def execute(self, context):
        bpy.context.view_layer.update()
        self.active_obj = context.active_object
        self.selected = context.selected_objects[:]
        if self.active_obj and context.mode =='EDIT_MESH':
            if self.active_obj not in self.selected:
                self.selected.append(self.active_obj)

        if self.individual:

            if context.mode == 'OBJECT':
                for obj in self.selected:
                    bounds = self.get_coords_obj(obj)
                    mesh_location = math.coords_to_center( bounds)
                    dimensions= [1,1,1] if obj.type == 'EMPTY' else math.dimensions(bounds)
                    if self.primitive_type == 'Empty':
                        location = obj.matrix_world @ mesh_location
                        primitive = self.add_empty(context, obj,  dimensions)
                        primitive.empty_display_size *= max (obj.matrix_world.to_scale())
                        primitive.empty_display_size *= self.scale
                        primitive.matrix_world = matrix_transfrom (obj.matrix_world, location=location, scale= Vector ((1,1,1)) )
                   
                    else:
                        primitive = self.pirmitive_add(context, obj, mesh_location, dimensions, scale_object= obj.matrix_world.to_scale())
                        primitive.matrix_world = matrix_transfrom (obj.matrix_world, scale= Vector ((1,1,1)) )
                        self.center_origin(primitive)
                    
                    obj.select_set(False)
                    set_active(primitive)
                    if self.parent_shape:
                        if self.parent_shape_inverse:
                            set_parent(obj, primitive)
                        else:
                            set_parent (primitive, obj)

            elif context.mode =='EDIT_MESH':
                for obj in self.selected:

                    coords = self.get_coords_edit (context, obj)
                    if len (coords)<2:continue
                    bounds = math.coords_to_bounds(coords)
                    mesh_location = math.coords_to_center(bounds)
                    dimensions= math.dimensions(bounds)

                    if self.primitive_type == 'Empty':
                        location = obj.matrix_world @ mesh_location
                        primitive = self.add_empty(context, obj,  dimensions)
                        primitive.empty_display_size *= max (obj.matrix_world.to_scale())
                        primitive.empty_display_size *= self.scale
                        primitive.matrix_world = matrix_transfrom (obj.matrix_world, location=location, scale= Vector ((1,1,1)) )
                    else:

                        primitive = self.pirmitive_add(context, obj, mesh_location, dimensions, scale_object= obj.matrix_world.to_scale())
                        primitive.matrix_world = matrix_transfrom (obj.matrix_world, scale= Vector ((1,1,1)) )
                        self.center_origin(primitive)

                    if self.parent_shape:
                        if self.parent_shape_inverse:
                            set_parent(obj, primitive)
                        else:
                            set_parent (primitive, obj)
        else:

            bbox_array=[]

            if context.mode == 'OBJECT':
                for obj in self.selected:
                    bbox_array.extend( self.get_coords_obj (obj, obj.matrix_world ) )
                    obj.select_set(False)
            elif context.mode =='EDIT_MESH':
                for obj in self.selected:
                    bbox_array.extend(self.get_coords_edit (context, obj, obj.matrix_world))
            if len (bbox_array) <2:
                return {'CANCELLED'}

            bounds = math.coords_to_bounds(bbox_array)
            mesh_location = math.coords_to_center(bounds)
            dimensions = math.dimensions(bbox_array)

            if self.primitive_type == 'Empty':
                primitive = self.add_empty(context, obj, dimensions)
                primitive.empty_display_size *= self.scale
                primitive.matrix_world = matrix_transfrom ( Matrix(), location=mesh_location, scale= Vector ((1,1,1)) ) 
            else:
                primitive = self.pirmitive_add(context, obj,  mesh_location, dimensions)
                self.center_origin(primitive)
                
            if self.parent_shape:
                if self.parent_shape_inverse:
                    for obj in self.selected:
                        set_parent(obj, primitive)
                else:
                    set_parent (primitive, obj)

            if context.mode == 'OBJECT':
                set_active(primitive)
        
        return {'FINISHED'}



    def pirmitive_add (self, context, object, vector, dimensions, scale_object = Vector((1,1,1)) ) :
        primitive = self.primitive_type
        primitive_mesh = bpy.data.meshes.new(primitive)
        primitive_obj = bpy.data.objects.new(primitive, primitive_mesh)
        col = collections.find_collection(context, object)
        col.objects.link(primitive_obj)
        bm = bmesh.new()

        fit_matrix  = math.get_sca_matrix(scale_object) @ Matrix.Translation(vector) @ math.get_sca_matrix(dimensions)

        scale_center = Vector((0,0,0))

        max_vec = fit_matrix @ Vector((0.5,0.5,0.5))
        min_vec = fit_matrix @ Vector((-0.5,-0.5,-0.5))

        final_dimesnions = math.dimensions(  (min_vec, max_vec) )
        final_dim_max = axle = max(final_dimesnions)

        if primitive == 'Cube':
            bmesh.ops.create_cube(bm)

        elif primitive == 'Cylinder':
            bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=self.cyl_segments, diameter1=self.cyl_diameter1/2, diameter2=self.cyl_diameter2/2, depth =1)

        elif primitive == 'Monkey':
            bmesh.ops.create_monkey(bm, matrix = math.get_sca_matrix([0.5, 0.5 ,0.5]))

        elif primitive == 'Plane':
           bm = self.plane_mesh ()
           bm.faces.ensure_lookup_table()
           scale_center = bm.faces[0].calc_center_median()


        elif primitive == 'Sphere':
            bmesh.ops.create_uvsphere (bm, u_segments = self.sphere_segments, v_segments = self.sphere_rings, diameter = self.sphere_diameter/2 )


        if primitive in {'Cylinder', 'Sphere'}:
            XYZ = 'XYZ'
            
            if self.alignment == 'AUTO_OBJECT':
                
                index = list(final_dimesnions).index(axle)
                
                alignment = XYZ[index]

            elif self.alignment == 'AUTO_MESH':
                
                index = list(dimensions).index(max(dimensions))
                
                alignment = XYZ[index]

            else:
                alignment = self.alignment
                index = XYZ.index(self.alignment)

            if alignment == 'X':
                eul = Euler((0.0, radians(90.0), 0.0), XYZ)
            elif alignment == 'Y':
                eul = Euler((radians(-90.0), 0.0, 0.0), XYZ)
            elif alignment == 'Z':
                eul = Euler((0.0, 0.0, 0.0), XYZ)

            axle = final_dimesnions[index]

            bmesh.ops.transform(bm, matrix = math.get_rot_matrix(eul.to_quaternion()), verts = bm.verts)
        
        bmesh.ops.transform(bm, matrix = fit_matrix , verts = bm.verts)
        
        scale_vector = Vector((1,1,1))

        if self.equalize:

            if self.equalize_radius:
                
                dims = list(final_dimesnions)
                dims.remove(axle)
                max_dim = max(dims)

            else:

                axle = max_dim = final_dim_max
                
            for i in range(3):
                if final_dimesnions[i] == axle:
                    continue
                scale_vector[i] = max_dim/final_dimesnions[i] if final_dimesnions[i] else final_dimesnions[i]

        scale_vector*=self.scale
        
        bmesh.ops.scale(bm, vec = scale_vector, verts = bm.verts, space = Matrix.Translation(-(fit_matrix @ scale_center)) )

        if self.copy_1st_bvl and primitive not in self.no_bevel_club:
            if self.individual:
                source = object
            else:
                source = self.active_obj if self.active_obj else None
            if source:
                bevels = [mod for mod in source.modifiers if mod.type =='BEVEL']
                if bevels:
                    source_bvl = bevels[0]

                    if self.copy_1st_bvl_angle_only:
                        angles = [bvl for bvl in bevels if bvl.limit_method =='ANGLE']
                        if angles:
                            source_bvl = angles[0]
                        else:
                            source_bvl = None

                    if source_bvl:

                        stored_source = modifier.stored(source_bvl)

                        modifier.new(primitive_obj, name=source_bvl.name, mod = stored_source)

                        del stored_source

                        dest_bvl = primitive_obj.modifiers[0]

                        if dest_bvl.limit_method not in {'NONE', 'ANGLE'}:
                            dest_bvl.limit_method = 'ANGLE'
                            dest_bvl.angle_limit = radians(30)
                        primitive_mesh.use_auto_smooth = True
                        primitive_mesh.auto_smooth_angle = object.data.auto_smooth_angle
                        for face in bm.faces:
                            face.smooth = True
       
        bm.to_mesh(primitive_mesh)
        bm. free()
        return primitive_obj


    def get_coords_obj(self, obj, matrix = Matrix()):
        if self.modified:
            bb = [matrix @ Vector(v) for v in obj.bound_box]

        else:

            tmp = bpy.data.objects.new("Bounding Box", obj.data)
            bb = [matrix @ Vector (v) for v in tmp.bound_box]
            bpy.data.objects.remove(tmp)
       
        return bb

    def get_coords_edit (self, context, obj, matrix = Matrix()):

        coords = []
        if self.modified:
            obj.update_from_editmode()
            depsgraph = context.evaluated_depsgraph_get()
            obj_eval = obj.evaluated_get(depsgraph)
            data_eval = obj_eval.to_mesh()
            coords = [matrix @ v.co for v in data_eval.vertices if v.select]
            obj_eval.to_mesh_clear()
        if not coords :
            bm = bmesh.from_edit_mesh(obj.data)
            coords = [matrix @ v.co for v in bm.verts if v.select]
       
        return coords


    def center_origin(self, obj) :
        center = object.center(obj)
        obj.matrix_world = matrix_transfrom (obj.matrix_world, location=obj.matrix_world @ center)
        obj.data.transform(Matrix.Translation(-center))


    def plane_mesh (self):
            bm = bmesh.new()
            bmesh.ops.create_cube(bm)
            if self.axis == '+X':
                verts = [v for v in bm.verts if v.co[0]==-0.5]    
            elif self.axis == '+Y':
               verts = [v for v in bm.verts if v.co[1]==-0.5]
            elif self.axis == '+Z':
                verts = [v for v in bm.verts if v.co[2]==-0.5]
            elif self.axis == '-X':
                verts = [v for v in bm.verts if v.co[0]==0.5]
            elif self.axis == '-Y':
                verts = [v for v in bm.verts if v.co[1]==0.5]
            elif self.axis == '-Z':
               verts = [v for v in bm.verts if v.co[2]==0.5]
               
            bmesh.ops.delete(bm, geom = verts, context = 'VERTS')
           
            offset = self.offset
            if self.axis in {'-X', '-Y', '-Z'}:
                offset*= -1
            if self.axis in {'+X', '-X'}:
                bmesh.ops.transform(bm, matrix = Matrix.Translation(Vector((offset,0,0))), verts = bm.verts)
            elif self.axis in {'+Y', '-Y'}:
                bmesh.ops.transform(bm, matrix = Matrix.Translation(Vector((0,offset,0))), verts = bm.verts)
            elif self.axis in {'+Z', '-Z'}:
                bmesh.ops.transform(bm, matrix = Matrix.Translation(Vector((0,0,offset))), verts = bm.verts)

            return bm

    def add_empty(self, context, object, dimensions):
        primitive = self.primitive_type
        primitive_obj = bpy.data.objects.new(primitive, None)
        col = collections.find_collection(context, object)
        col.objects.link(primitive_obj)
        primitive_obj.empty_display_type = self.empty_display
        primitive_obj.empty_display_size = max (dimensions)*0.6


        return primitive_obj

def set_parent (chlid, parent):
    buffer = chlid.matrix_world.copy()
    chlid.parent = parent
    chlid.matrix_parent_inverse = parent.matrix_world.inverted() 
    chlid.matrix_world = buffer

def matrix_transfrom (matrix, location = None, rotation = None, scale = None):
    loc, rot, sca = matrix.decompose()
    loc = location if location else loc
    rot = rotation if rotation else rot
    sca = scale if scale else sca

    mat_loc = Matrix.Translation(loc)
    mat_rot = rot.to_matrix().to_4x4()
    mat_sca = math.get_sca_matrix (sca)

    return mat_loc @ mat_rot @  mat_sca

def apply_scale_matrix(obj):
    obj.data.transform(math.get_sca_matrix(obj.scale))
    obj.matrix_world = matrix_transfrom(obj.matrix_world, scale= Vector((1,1,1,)) )

def set_active(obj):
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj