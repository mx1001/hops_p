import bpy, bmesh, mathutils, math, copy
from ... preferences import get_preferences
from ... utils.objects import set_active
from ... utility import object, math as hops_math
from mathutils import Matrix, Vector


class HOPS_OT_Conv_To_Plane(bpy.types.Operator):
    bl_idname = "hops.to_plane"
    bl_label = "Hops To Plane"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """LMB - Creates plane from selection.
LMB+SHIFT - Creates plane for each selected object from selection.

"""
    axis: bpy.props.EnumProperty(
        name="Axis",
        description="What axis to dice on",
        items=[
            ('+X', "+X", "Create a plane on the +X axis"),
            ('+Y', "+Y", "Create a plane on the +Y axis"),
            ('+Z', "+Z", "Create a plane on the +Z axis"),
            ('-X', "-X", "Create a plane on the -X axis"),
            ('-Y', "-Y", "Create a plane on the -Y axis"),
            ('-Z', "-Z", "Create a plane on the -Z axis")],
        default='+X')

    modified: bpy.props.BoolProperty(
        name="Modified",
        description="Take the bounding box dimensions from the modified object",
        default=True)
    offset: bpy.props.FloatProperty(
        name="Offset",
        description="Offset plane from selection",
        default=0.03)

    individual: bpy.props.BoolProperty(
    name="Individual", description="Create plane per object", default = False)

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH'

    def draw(self, context):
        self.layout.prop(self, "axis")
        self.layout.prop(self, "modified")
        self.layout.prop(self, "individual")
        self.layout.prop(self, "offset")

    def invoke (self, context, event):
        if event.shift:
            self.individual = True
        else:
            self.individual = False

        return self.execute(context)


    def execute(self, context):
        bpy.context.view_layer.update()
        selected = context.selected_objects[:]
        if self.individual:

            if context.mode == 'OBJECT':
                for obj in selected:
                    plane = obj.copy()
                    for col in obj.users_collection:
                        col.objects.link(plane)

                    plane.name = f"{obj.name} Plane {self.axis}"
                    plane.modifiers.clear()
                    plane.select_set(True)

                    obj.select_set(False)
                    context.view_layer.objects.active = plane
                    bb = self.get_coords_obj( obj)

                    plane.data = self.plane_mesh( bb, obj.name)

                    self.center_origin(plane, context )

            elif context.mode =='EDIT_MESH':
                for obj in selected:
                    coords = self.get_coords_edit(context, obj)

                    if len (coords) <2:
                        continue

                    plane = obj.copy()
                    for col in obj.users_collection:
                        col.objects.link(plane)

                    plane.name = f"{obj.name} Plane {self.axis}"
                    plane.modifiers.clear()
                    plane.select_set(True)

                    bb = hops_math.coords_to_bounds(coords)

                    plane.data= self.plane_mesh( bb, obj.name)

                    self.center_origin(plane,context )

        else:

            coords = []
            if context.mode == 'OBJECT':
                for obj in selected:

                    coords.extend(self.get_coords_obj(obj, obj.matrix_world))

                    obj.select_set(False)

            elif context.mode =='EDIT_MESH':
                for obj in selected:

                    coords.extend(self.get_coords_edit(context, obj, obj.matrix_world))
                    obj.select_set(False)

            if len (coords) <2:
                return {'CANCELLED'}

            bb = hops_math.coords_to_bounds(coords)

            plane_mesh = self.plane_mesh( bb, obj.name)
            plane = bpy.data.objects.new(f"{obj.name} Plane {self.axis}", plane_mesh)

            for col in obj.users_collection:
                col.objects.link(plane)

            if context.mode == 'OBJECT':
                plane.select_set(True)
                context.view_layer.objects.active = plane

        return {'FINISHED'}

    @staticmethod
    def center_origin(plane, context) :
        context.view_layer.update()
        center = object.center(plane)
        plane.location = plane.matrix_world @ center
        plane.data.transform(Matrix.Translation(-center))


    def plane_mesh (self, bb, name = ""):
            if self.axis == '+X':
                bb = (bb[7], bb[6], bb[5], bb[4])
            elif self.axis == '+Y':
                bb = (bb[3], bb[2], bb[6], bb[7])
            elif self.axis == '+Z':
                bb = (bb[5], bb[6], bb[2], bb[1])
            elif self.axis == '-X':
                bb = (bb[0], bb[1], bb[2], bb[3])
            elif self.axis == '-Y':
                bb = (bb[0], bb[4], bb[5], bb[1])
            elif self.axis == '-Z':
                bb = (bb[0], bb[3], bb[7], bb[4])

            bm = bmesh.new()
            verts = [bm.verts.new(v) for v in bb]
            bm.faces.new(verts)

            plane_mesh = bpy.data.meshes.new(f"{name} Plane {self.axis}")

            bpy.context.view_layer.update()
            offset = self.offset
            if self.axis in {'-X', '-Y', '-Z'}:
                offset*= -1
            if self.axis in {'+X', '-X'}:
                bmesh.ops.transform(bm, matrix = Matrix.Translation(Vector((offset,0,0))), verts = bm.verts)
            elif self.axis in {'+Y', '-Y'}:
                bmesh.ops.transform(bm, matrix = Matrix.Translation(Vector((0,offset,0))), verts = bm.verts)
            elif self.axis in {'+Z', '-Z'}:
                bmesh.ops.transform(bm, matrix = Matrix.Translation(Vector((0,0,offset))), verts = bm.verts)

            bm.to_mesh(plane_mesh)
            bm.free()

            return plane_mesh

    def get_coords_obj(self, obj, matrix =None):

        if self.modified:

            if matrix == None:
                bb = [Vector(v) for v in obj.bound_box]
            else:
                bb = [matrix @ Vector(v) for v in obj.bound_box]
        else:

            if matrix == None:
                coord = [v.co for v in obj.data.vertices]
            else:
                coord = [matrix @ v.co for v in obj.data.vertices]
            bb = hops_math.coords_to_bounds(coord)

        return bb

    def get_coords_edit (self, context, obj, matrix = None):


        me = obj.data
        if self.modified:
            depsgraph = context.evaluated_depsgraph_get()
            bm = bmesh.new()
            bm.from_object(obj,depsgraph, True)
            bmesh.update_edit_mesh(me)
        else:
            bm = bmesh.from_edit_mesh(me)
        if matrix == None:
          coords = [v.co for v in bm.verts if v.select]
        else:
            coords = [matrix @ v.co for v in bm.verts if v.select]
        bm.free()

        return coords
