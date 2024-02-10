import bpy, bmesh
from ... ui_framework.operator_ui import Master
from ... preferences import get_preferences, get_addon_name


class HOPS_OT_ToRope(bpy.types.Operator):
    bl_idname = 'hops.to_rope'
    bl_label = 'To Rope'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = '''Converts selection to Smart Ropes
LMB - Regular Smart Rope
SHIFT - Subdivided Smart Rope
CTRL - Alternative Smart Rope'''

    called_ui = False


    @classmethod
    def poll(cls, context):
        active = context.active_object
        return active and active.type in {'MESH', 'CURVE'} and active.mode in {'OBJECT', 'EDIT'}


    def invoke(self, context, event):
        HOPS_OT_ToRope.called_ui = False

        self.selection = context.selected_objects
        self.generated_objects = []
        self.generated_curves = []
        self.result_dict = {}

        if context.mode == 'EDIT_MESH':
            context.active_object.select_set(True)

        return self.execute(context)


    def execute(self, context):
        for obj in self.selection:
            if obj.mode not in {'OBJECT', 'EDIT'}:
                continue

            if obj.type == 'MESH':
                if obj.mode == 'OBJECT':
                    bm = bmesh.new()
                    bm.from_mesh(obj.data)

                    if bm.verts:
                        self.result_dict[obj.name] = 'Success'
                    else:
                        self.result_dict[obj.name] = 'Failed, invalid selection'
                        continue

                elif obj.mode == 'EDIT':
                    bm = bmesh.from_edit_mesh(obj.data).copy()
                    deselect_geom = [elem for elem in bm.edges if not elem.select]

                    if deselect_geom:
                        bmesh.ops.delete(bm, geom=deselect_geom, context='EDGES')

                    if bm.verts:
                        self.result_dict[obj.name] = 'Success'
                    else:
                        self.result_dict[obj.name] = 'Failed, invalid selection'
                        continue

                new_mesh = bpy.data.meshes.new(f'{obj.data.name}_Rope')
                bm.to_mesh(new_mesh)
                bm.free()

                gen_obj = obj.copy()
                gen_obj.name = f'{obj.name}_Rope'
                gen_obj.data = new_mesh

                for col in obj.users_collection:
                    if col not in gen_obj.users_collection:
                        col.objects.link(gen_obj)

                self.generated_objects.append(gen_obj)

            elif obj.type == 'CURVE':
                for index, spline in enumerate(obj.data.splines):
                    valid_spline = len(spline.points) > 1 or len(spline.bezier_points) > 1

                    if obj.mode == 'EDIT':
                        points_select = any(p.select for p in spline.points)
                        bezier_select = any(p.select_control_point for p in spline.bezier_points)
                        valid_spline = valid_spline and (points_select or bezier_select)

                    if valid_spline:
                        new_curve = obj.data.copy()
                        index_str = f'0{index+1}' if index < 10 else f'{index+1}'
                        new_curve.name = f'{obj.name}_Spline{index_str}'

                        other_splines = [s for i, s in enumerate(new_curve.splines) if i != index]
                        for new_spline in other_splines:
                            new_curve.splines.remove(new_spline)

                        new_obj = obj.copy()
                        new_obj.name = new_curve.name
                        new_obj.data = new_curve

                        for col in obj.users_collection:
                            if col not in new_obj.users_collection:
                                col.objects.link(new_obj)

                        self.generated_curves.append(new_obj)

        if self.generated_objects:
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')

            for gen_obj in self.generated_objects:
                gen_obj.select_set(True)

                context.view_layer.objects.active = gen_obj
                bpy.ops.hops.reset_status()

                bpy.ops.object.convert(target='CURVE')
                if gen_obj.type == 'CURVE':
                    self.generated_curves.append(gen_obj)

                else:
                    bpy.ops.object.convert(target='MESH')
                    bm = bmesh.new()
                    bm.from_mesh(gen_obj.data)
                    bmesh.ops.delete(bm, geom=bm.faces, context='FACES_ONLY')
                    bm.to_mesh(gen_obj.data)
                    bm.free()

                    bpy.ops.object.convert(target='CURVE')
                    if gen_obj.type == 'CURVE':
                        self.generated_curves.append(gen_obj)

                    else:
                        self.result_dict[self.gen_obj.name] = 'Failed, too complex'
                        bpy.data.objects.remove(gen_obj)
                        del gen_obj
                        continue

                gen_obj.select_set(False)

        if self.generated_curves:
            for obj in self.generated_curves:
                context.view_layer.objects.active = obj
                bpy.ops.hops.add_rope('INVOKE_DEFAULT')

        if not HOPS_OT_ToRope.called_ui:
            HOPS_OT_ToRope.called_ui = True
            ui = Master()
            draw_data = [['To_Rope']]

            result = [[f'{obj} {result}'] for obj, result in self.result_dict.items()]
            draw_data.extend(result)
            draw_data.append([f'Conversion to Rope'])
            ui.receive_draw_data(draw_data=draw_data)

            prefs = get_preferences()
            draw_bg = prefs.ui.Hops_operator_draw_bg
            draw_border = prefs.ui.Hops_operator_draw_border
            ui.draw(draw_bg=draw_bg, draw_border=draw_border)

        return {'FINISHED'}
