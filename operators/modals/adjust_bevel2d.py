import bpy
from mathutils import Vector
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... graphics.drawing2d import draw_horizontal_line, draw_text, set_drawing_dpi, draw_box
from ... preferences import Hops_text_color, Hops_text2_color, Hops_border_color, Hops_border2_color

class TwoDBevelOperator(bpy.types.Operator):
    bl_idname = "hops.2d_bevel"
    bl_label = "2 Dimensional Bevel"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = "Change the bevel modifier of the active object via vertex"

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def invoke(self, context, event):
        self.object = context.active_object
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.view3d.clean_mesh()
        self.bevel = self.get_bevel_modifier()
        self.start_mouse_position = Vector((event.mouse_region_x, event.mouse_region_y))
        self.start_bevel_width = self.bevel.width
        self.start_bevel_profile = self.bevel.profile
        self.start_bevel_segments = self.bevel.segments
        self.bevel_offset = 0
        self.profile_offset = 0
        self.last_mouse_x = event.mouse_region_x

        args = (context, )
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw, args, "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def get_bevel_modifier(self):
        object = bpy.context.active_object
        bevel_modifier = None
        for modifier in object.modifiers:
            if modifier.type == "BEVEL":
                bevel_modifier = modifier
                self.created_bevel_modifier = False
        if bevel_modifier is None:
            bevel_modifier = object.modifiers.new("Bevel", "BEVEL")
            bevel_modifier.limit_method = "NONE"
            bevel_modifier.width = 0.200
            bevel_modifier.profile = 0.70
            bevel_modifier.segments = 6
            bevel_modifier.use_only_vertices = True
            bevel_modifier.use_clamp_overlap = False
            self.created_bevel_modifier = True
        return bevel_modifier


    def modal(self, context, event):
        divisor = 10000 if event.shift else 10000000 if event.ctrl else 1000
        divisor_profile = 500 if event.ctrl else 100000000000
        offset_x = event.mouse_region_x - self.last_mouse_x
        self.bevel_offset += offset_x / divisor / get_dpi_factor()
        self.bevel.width = self.start_bevel_width - self.bevel_offset
        self.profile_offset += offset_x / divisor_profile / get_dpi_factor()


        if event.ctrl:
            self.bevel.profile = self.start_bevel_profile - self.profile_offset

        if event.type == "WHEELUPMOUSE" or event.type == 'NUMPAD_PLUS' and event.value=='PRESS':
            self.bevel.segments += 1
        if event.type == "WHEELDOWNMOUSE" or event.type == 'NUMPAD_MINUS' and event.value=='PRESS':
            self.bevel.segments -= 1

        if event.type in ("ESC", "RIGHTMOUSE"):
            self.reset_object()
            return self.finish()

        if event.type in ("SPACE", "LEFTMOUSE"):
            return self.finish() 

        if event.type == 'W' and event.value =='PRESS':
            ofset_list =['OFFSET','WIDTH', 'DEPTH', 'PERCENT']
            if self.bevel.offset_type == ofset_list[0]:
                self.bevel.offset_type = ofset_list[1]
            elif self.bevel.offset_type == ofset_list[1]:
                self.bevel.offset_type = ofset_list[2]
            elif self.bevel.offset_type == ofset_list[2]:
                self.bevel.offset_type = ofset_list[3]
            elif self.bevel.offset_type == ofset_list[3]:
                self.bevel.offset_type = ofset_list[0]

           

        self.last_mouse_x = event.mouse_region_x
        context.area.tag_redraw()
        return {"RUNNING_MODAL"}

    def reset_object(self):
        self.bevel.width = self.start_bevel_width
        self.bevel.segments = self.start_bevel_segments
        self.bevel.profile = self.start_bevel_profile
        if self.created_bevel_modifier:
            self.object.modifiers.remove(self.bevel)

    def finish(self):
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
        return {"FINISHED"}

    def draw(self, context):
        x, y = self.start_mouse_position
        bevel = self.bevel

        set_drawing_dpi(get_dpi())
        factor = get_dpi_factor()
        color_text1 = Hops_text_color()
        color_text2 = Hops_text2_color()
        color_border = Hops_border_color()
        color_border2 = Hops_border2_color()


        draw_box(x -8 * factor, y + 8 * factor, 214 * factor , 34* factor, color = color_border2)

        draw_box(x + 24 * factor, y + 8 * factor, 180 * factor , 30* factor, color = color_border)

        if bevel.segments >= 10 :
            draw_text(str(bevel.segments), x -8 * factor, y, size = 23, color = color_text1)
        else:
            draw_text(str(bevel.segments), x + 3 * factor, y, size = 23, color = color_text1)

                 
        draw_text("2d Bevel - {:.3f} // (W) - {}".format(bevel.width, bevel.offset_type),
                  x + 27 * factor, y + 9 * factor , size = 12, color = color_text2)

        draw_text("Profile- {:.2f} ".format(bevel.profile),
                  x + 27 * factor, y - 4 * factor, size = 12, color = color_text2)


        #this never worked anyway, do we need it ?
        '''draw_text(self.get_description_text(), x + 24 * factor, y - 28 * factor,
                                          size = 12, color = color)'''

    def get_description_text(self):
        if self.object.hops.status == "CSHARP":
            return "CSsharp / Ssharp"
        if self.object.hops.status == "CSTEP":
            return "CStep / Sstep - Warning: Bevels could not be showing due to bevel baking."
        if self.object.hops.is_pending_boolean:
            return "Pending Boolean - Warning: Bevels could not be showing due to boolean pending."
        return "Standard Mesh"
