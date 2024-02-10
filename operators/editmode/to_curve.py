import bpy, bmesh
from ...ui_framework.operator_ui import Master
from ... preferences import get_preferences, get_addon_name


class HOPS_OT_Edge2Curve(bpy.types.Operator):
    bl_idname = "hops.edge2curve"
    bl_label = "Curve/Plate Extraction"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """Curve/Plate Extraction

LMB - Converts edge to_curve.
LMB+SHIFT - Converts selection to_plate.
LMB+CTRL - New object from selection.
ALT - Destructive to_curve
ALT+SHIFT - Destructive to_plate

"""

    called_ui = False


    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'MESH'


    def invoke(self, context, event):
        HOPS_OT_Edge2Curve.called_ui = False
        self.original_active = context.active_object
        self.new_active = None
        self.selection = [o for o in context.selected_objects if o.type == 'MESH']
        self.generated_objects = []
        self.generated_curves = []
        self.result_dict = {}
        if context.mode == 'EDIT_MESH':
            context.active_object.select_set(True)

        self.mode = "Curve"
        self.destructive = False
        if event.shift and not event.ctrl:
            self.mode = "Plate"
        if event.ctrl and not event.shift:
            self.mode = "Piece"
        if event.alt:
            self.destructive = True
        return self.execute(context)


    def execute(self, context):
        if self.mode == "Curve":
            bm_context = 'EDGES'
            
        elif self.mode == "Plate":
            bm_context = 'FACES'

        elif self.mode == "Piece" and context.mode == 'EDIT_MESH':
            select_mode = bpy.context.tool_settings.mesh_select_mode
            if select_mode[0]:
                bm_context = 'VERTS'
            elif select_mode[1]:
                bm_context = 'EDGES'
            else:
                bm_context = 'FACES'

        for obj in self.selection:
            deselect_geom =[]

            if obj.mode == 'EDIT':
                
                bm = bmesh.from_edit_mesh(obj.data).copy()
                geo_type = getattr(bm, str.lower(bm_context))
                deselect_geom = [elem for elem in geo_type if not elem.select]

                if deselect_geom:
                    bmesh.ops.delete(bm, geom= deselect_geom, context= bm_context)
                    if not bm.verts:
                        self.result_dict[obj.name] = "Failed, Invalid selection"
                        continue
                    else:
                        self.result_dict[obj.name] = "Success"

                    if self.destructive:
                        bm_edit = bmesh.from_edit_mesh(obj.data)
                        selected_geom = [f for f in bm_edit.faces if f.select ]
                        bmesh.ops.delete(bm_edit, geom= selected_geom, context= 'FACES')
                        if bm_context != 'FACES':
                            floaters = [f for f in bm_edit.verts if f.select and not f.link_faces ]
                            bmesh.ops.delete(bm_edit, geom= floaters, context= 'VERTS')

                if self.mode == 'Plate':
                    floaters = [f for f in bm.verts if not f.link_faces ]
                    bmesh.ops.delete(bm, geom= floaters, context= 'VERTS')
                    if not bm.verts:
                        self.result_dict[obj.name] = "Failed, Invalid selection"
                        continue
                    else:
                        self.result_dict[obj.name] = "Success"

            else:

                bm = bmesh.new()
                bm.from_mesh(obj.data)
                if self.mode == "Plate":
                    floaters = [f for f in bm.verts if not f.link_faces ]
                    bmesh.ops.delete(bm, geom= floaters, context= 'VERTS')
                if not bm.verts:
                    self.result_dict[obj.name] = "Failed, Invalid selection"
                    continue
                else:
                    self.result_dict[obj.name] = "Success"

            new_mesh = obj.data.copy()
            new_mesh.name = F"{obj.data.name}_{self.mode}"
            bm.to_mesh(new_mesh)
            bm.free()
            gen_obj= obj.copy()
            gen_obj.name = F"{obj.name}_{self.mode}"
            gen_obj.data = new_mesh

            for col in obj.users_collection:
                col.objects.link(gen_obj)

            for mod in gen_obj.modifiers:
                if mod.type in {'WEIGHTED_NORMAL'}:
                    gen_obj.modifiers.remove(mod)

            self.generated_objects.append(gen_obj)
            if obj is context.active_object:
                self.new_active = gen_obj

        if self.generated_objects:

            bpy.ops.object.mode_set (mode = 'OBJECT')
            bpy.ops.object.select_all(action='DESELECT')

            for gen_obj in self.generated_objects:
                gen_obj.select_set(True)
                bpy.context.view_layer.objects.active = gen_obj
                bpy.ops.hops.reset_status()

                if self.mode == "Curve":
                    bpy.ops.object.convert(target='CURVE')
                    if context.active_object.type == 'CURVE':
                        self.generated_curves.append(gen_obj)
                    else:
                        bpy.ops.object.convert(target='MESH')
                        bm = bmesh.new()
                        bm.from_mesh(gen_obj.data)
                        bmesh.ops.delete(bm, geom = bm.faces, context= 'FACES_ONLY')
                        bm.to_mesh(gen_obj.data)
                        bm.free()
                        bpy.ops.object.convert(target='CURVE')
                        if context.active_object.type == 'CURVE':
                            self.generated_curves.append(gen_obj)
                        else:
                            self.result_dict[gen_obj.name.replace(F"_{self.mode}", "") ] = "Failed. Geo is too complex or Modifiers took it to another castle"
                            bpy.data.objects.remove(gen_obj)
                            del gen_obj
                            continue
                gen_obj.select_set(False)

            if self.mode == "Curve":

                if self.generated_curves:
                    context.view_layer.objects.active = self.new_active if self.new_active else self.generated_curves[0]
                    
                    for obj in self.generated_curves:
                        obj.select_set(True)
                    bpy.ops.hops.adjust_curve('INVOKE_DEFAULT')

            elif  self.generated_objects:

                context.view_layer.objects.active = self.new_active if self.new_active else self.generated_objects[0]
                
                for obj in self.generated_objects:
                    obj.select_set(True)
                if self.mode == "Plate":
                    bpy.ops.hops.adjust_tthick('INVOKE_DEFAULT')

        # Operator UI
        if not HOPS_OT_Edge2Curve.called_ui:
            HOPS_OT_Edge2Curve.called_ui = True

            ui = Master()
            draw_data = [
                ["To_" + self.mode],
                
                ]
            result = [[F"{obj} {result}" ] for obj, result in self.result_dict.items() ]
            draw_data.extend(result)
            draw_data.append( [F"Conversion to {self.mode}"])
            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return {"FINISHED"}
