import bpy
from ... utility import modifier
from bpy.props import EnumProperty
from ... preferences import get_preferences
from ...ui_framework.operator_ui import Master


class HOPS_OT_LateParen_t(bpy.types.Operator):
    bl_idname = "hops.late_paren_t"
    bl_label = "Late Parent "
    bl_description = '\n Connects cutters as children to parent'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {"REGISTER", "UNDO"}


    def execute(self, context):
        targets = {}

        for obj in context.visible_objects:
            for mod in obj.modifiers:
                if mod.type == 'BOOLEAN' and mod.object and mod.object.select_get():
                    if obj not in targets:
                        targets[obj] = [mod.object]
                    elif mod.object not in targets[obj]:
                        targets[obj].append(mod.object)

        count = 0
        for obj in targets:
            context_override = context.copy()
            context_override['object'] = obj
            bpy.ops.object.parent_set(context_override, keep_transform=True)

            for _ in targets[obj]:
                count += 1

        del targets

        self.report({'INFO'}, F'{str(count) + " " if count > 0 else ""}Cutter{"s" if count > 1 else ""} Parented')

        return {'FINISHED'}


class HOPS_OT_LateParent(bpy.types.Operator):
    bl_idname = "hops.late_parent"
    bl_label = "Late Parent "
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = '''Late Parent 
    
    Connects cutters as children to parent.
    *Used to retroactively connect cutters to parent*
    Now supporting recursion. (cutters of cutters)
    
    '''

    called_ui = False

    def __init__(self):

        HOPS_OT_LateParent.called_ui = False

    def execute(self, context):

        lst = late_parent(context)
        self.report({'INFO'}, F'Cutters Parented')
        # Operator UI
        if not HOPS_OT_LateParent.called_ui:
            HOPS_OT_LateParent.called_ui = True

            ui = Master()
            draw_data = [
                ["Late Parent"],
                ["Selected Objects", lst[0]],
                ["Cutters Parented", lst[1]],
                ["Booleans Total", lst[2]]
                ]
            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return {"FINISHED"}


def late_parent(context):

    cutters = 0
    bools = 0

    if len (context.selected_objects) == 1:
        return  late_parent_recursive(context.selected_objects[0])

    for obj in context.selected_objects:

        for mod in obj.modifiers:
            if mod.type == 'BOOLEAN' and mod.object != None:
                bools +=1

                if  mod.object.parent == None:
                    cutters+=1
                    mod.object.parent = obj
                    mod.object.matrix_parent_inverse = obj.matrix_world.inverted()


    return [len(context.selected_objects), cutters , bools]


def late_parent_recursive(obj, out = [0,0,0]):

    for mod in obj.modifiers:
        if mod.type == 'BOOLEAN' and mod.object != None:
            out[2] +=1

            if  mod.object.parent == None:
                out[1]+=1
                mod.object.parent = obj
                mod.object.matrix_parent_inverse = obj.matrix_world.inverted()
                out[0] = 1
                out[1] += 1

            if mod.object.modifiers:
                late_parent_recursive(mod.object, out)
    return out
