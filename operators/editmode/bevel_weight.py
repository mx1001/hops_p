import bpy
import bmesh
from mathutils import Vector
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... graphics.drawing2d import draw_text, set_drawing_dpi, draw_box
from ... preferences import Hops_text_color, Hops_text2_color, Hops_border_color, Hops_border2_color

class AdjustBevelWeightOperator(bpy.types.Operator):
    bl_idname = "hops.bevel_weight"
    bl_label = "Adjust Bevel Weight"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = "Change the bevel weight of selected edge"
   
    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return(ob and ob.type == 'MESH' and context.mode == 'EDIT_MESH')

    def invoke(self, context, event):

        self.start_value = self.detect(context)
        self.offset = 0
        self.start_mouse_position = Vector((event.mouse_region_x, event.mouse_region_y))
        self.last_mouse_x = event.mouse_region_x

        args = (context, )
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw, args, "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}


    def modal(self, context, event):
        divisor = 5000 if event.shift else 230
        offset_x = event.mouse_region_x - self.last_mouse_x
        self.offset += offset_x / divisor / get_dpi_factor()
        self.value_base = float("{:.2f}".format(self.start_value - self.offset))
        self.value = max(self.value_base, 0) and min(self.value_base, 1)

        if not event.ctrl and not event.shift:
            self.value = round(self.value, 1)

        obj = bpy.context.object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        bw = bm.edges.layers.bevel_weight.verify()
        me.show_edge_bevel_weight = True
        
        selected = [ e for e in bm.edges if e.select ]
        for e in selected:
            e[bw] = self.value

        bmesh.update_edit_mesh(me)


        if event.type in ("ESC", "RIGHTMOUSE"):
            self.value = self.detect(context)
            return self.finish()

        if event.type in ("SPACE", "LEFTMOUSE"):
            return self.finish() 


        self.last_mouse_x = event.mouse_region_x
        context.area.tag_redraw()
        return {"RUNNING_MODAL"}


    def finish(self):
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
        return {"FINISHED"}

    def detect(self, context):

        obj = bpy.context.object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        bw = bm.edges.layers.bevel_weight.verify()
        me.show_edge_bevel_weight = True

        selected = [ e for e in bm.edges if e.select ]

        bmesh.update_edit_mesh(me)
        
        if len(selected) > 0:
            return selected[-1][bw]
        else:
            return 0

    def draw(self, context):
        x, y = self.start_mouse_position
        value = self.value

        set_drawing_dpi(get_dpi())
        factor = get_dpi_factor()
        color_text1 = Hops_text_color()
        color_text2 = Hops_text2_color()
        color_border = Hops_border_color()
        color_border2 = Hops_border2_color()


        draw_box(x -8 * factor, y + 8 * factor, 204 * factor , 34* factor, color = color_border2)

        draw_box(x + 45 * factor, y + 8 * factor, 150 * factor , 30* factor, color = color_border)

        #if bevel.segments >= 10 :
           # draw_text(str(bevel.segments), x -8 * factor, y, size = 23, color = color_text1)
        #else:
           # draw_text(str(bevel.segments), x + 3 * factor, y, size = 23, color = color_text1)


        draw_text(" {:.2f} - B-Weight".format(value),
                  x -8 * factor, y, size = 20, color = color_text2)


        #this never worked anyway, do we need it ?
        '''draw_text(self.get_description_text(), x + 24 * factor, y - 28 * factor,
                                          size = 12, color = color)'''
