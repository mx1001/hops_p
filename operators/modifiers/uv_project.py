import bpy, math
from ...preferences import get_preferences
from ...ui_framework.operator_ui import Master


class HOPS_OT_MOD_UV_Project(bpy.types.Operator):
    bl_idname = 'hops.mod_uv_project'
    bl_label = 'Add UV Project modifier'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = '''LMB - Add a UV Project modifier and empties
Shift + LMB - Also add a grid material

Requires UV Set
'''


    add_material: bpy.props.BoolProperty(
        name='Add Grid Material',
        description='Remove materials on this object and create a grid material for previewing your UVs',
        default=False,
    )


    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.mode == 'OBJECT' and obj.type == 'MESH'


    def invoke(self, context, event):
        self.add_material = event.shift

        context.active_object.select_set(True)
        selected = context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')

        for obj in selected:
            if obj.type != 'MESH':
                continue

            size = obj.dimensions[2] / obj.scale[2] / 2

            con = self.create_empty(f'{obj.name}_triplanar_controller', 'SPHERE', size / 4, obj)
            context.view_layer.objects.active = con
            con.location.z = size * 2

            xp = self.create_empty(f'{obj.name}_triplanar_x+', 'SINGLE_ARROW', size, con)
            xn = self.create_empty(f'{obj.name}_triplanar_x-', 'SINGLE_ARROW', size, con)
            yp = self.create_empty(f'{obj.name}_triplanar_y+', 'SINGLE_ARROW', size, con)
            yn = self.create_empty(f'{obj.name}_triplanar_y-', 'SINGLE_ARROW', size, con)
            zp = self.create_empty(f'{obj.name}_triplanar_z+', 'SINGLE_ARROW', size, con)
            zn = self.create_empty(f'{obj.name}_triplanar_z-', 'SINGLE_ARROW', size, con)

            xp.rotation_euler = [math.radians(90), 0, math.radians(90)]
            xn.rotation_euler = [math.radians(90), 0, math.radians(-90)]
            yp.rotation_euler = [math.radians(-90), math.radians(180), 0]
            yn.rotation_euler = [math.radians(90), 0, 0]
            zp.rotation_euler = [0, 0, 0]
            zn.rotation_euler = [0, math.radians(180), 0]

            mod = obj.modifiers.new(name='HOPS UV Project', type='UV_PROJECT')
            mod.projector_count = 6

            for index, empty in enumerate([xp, xn, yp, yn, zp, zn]):
                mod.projectors[index].object = empty

            if self.add_material:
                self.create_material(obj)

        prefs = get_preferences()
        count = len(selected)
        self.draw_ui(prefs, count)
        return {'FINISHED'}


    def create_empty(self, name, display_type, display_size, parent):
        empty = bpy.data.objects.new(name, None)
        empty.empty_display_type = display_type
        empty.empty_display_size = display_size
        empty.parent = parent

        for col in parent.users_collection:
            if col not in empty.users_collection:
                col.objects.link(empty)

        empty.select_set(True)
        return empty


    def create_material(self, obj):
        obj.data.materials.clear()
        mat = bpy.data.materials.new(f'{obj.name}_grid')
        obj.data.materials.append(mat)

        mat.use_nodes = True
        tree = mat.node_tree

        out = tree.nodes["Material Output"]
        bsd = tree.nodes["Principled BSDF"]

        hsv = tree.nodes.new("ShaderNodeHueSaturation")
        img = tree.nodes.new("ShaderNodeTexImage")
        mpn = tree.nodes.new("ShaderNodeMapping")
        tco = tree.nodes.new("ShaderNodeTexCoord")

        hsv.location = [-200, 300]
        img.location = [-500, 300]
        mpn.location = [-700, 300]
        tco.location = [-900, 300]

        tree.links.new(bsd.inputs["Base Color"], hsv.outputs["Color"])
        tree.links.new(hsv.inputs["Color"], img.outputs["Color"])
        tree.links.new(img.inputs["Vector"], mpn.outputs["Vector"])
        tree.links.new(mpn.inputs["Vector"], tco.outputs["UV"])

        grid = self.get_image()
        img.image = grid


    def get_image(self):
        grid = bpy.data.images.get("Color Grid")

        if not grid:
            grid = bpy.data.images.new("Color Grid", 1024, 1024)
            grid.generated_type = 'COLOR_GRID'

        return grid


    def draw_ui(self, prefs, count):
        ui = Master()

        draw_data = [
            ['UV Project'],
            ['Empties created', (count * 7)],
            ['Modifiers added', (count)],
        ]

        draw_bg = prefs.ui.Hops_operator_draw_bg
        draw_border = prefs.ui.Hops_operator_draw_border

        ui.receive_draw_data(draw_data=draw_data)
        ui.draw(draw_bg=draw_bg, draw_border=draw_border)
