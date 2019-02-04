import bpy
from mathutils import Vector
from bpy.props import IntProperty, FloatProperty
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... graphics.drawing2d import draw_horizontal_line, draw_text, set_drawing_dpi, draw_box
from ... preferences import Hops_text_color, Hops_text2_color, Hops_border_color, Hops_border2_color

class AdjustCurveOperator(bpy.types.Operator):
    bl_idname = "hops.adjust_curve"
    bl_label = "Adjust Curve"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = "Adjust a curve with a simple modal"

    first_mouse_x = IntProperty()
    first_value = FloatProperty()
    second_value = IntProperty()

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "CURVE"
    
    def modal(self, context, event):
        
        bpy.context.object.show_wire = True

        divisor = 10000 if event.shift else 10000000 if event.ctrl else 1000
        divisor_profile = 500 if event.ctrl else 100000000000
        offset_x = event.mouse_region_x - self.last_mouse_x

        self.depth_offset += offset_x / divisor / get_dpi_factor()
        context.object.data.bevel_depth = self.start_depth_offset - self.depth_offset

        if event.ctrl:          
            if event.type == "WHEELUPMOUSE" or event.type == 'NUMPAD_PLUS' and event.value=='PRESS':
                context.object.data.resolution_u += 1
                context.object.data.render_resolution_u += 1
            
            if event.type == "WHEELDOWNMOUSE" or event.type == 'NUMPAD_MINUS' and event.value=='PRESS':
                context.object.data.resolution_u -= 1
                context.object.data.render_resolution_u -= 1

        else:
            if event.type == "WHEELUPMOUSE" or event.type == 'NUMPAD_PLUS' and event.value=='PRESS':
                context.object.data.bevel_resolution += 1
                
            if event.type == "WHEELDOWNMOUSE" or event.type == 'NUMPAD_MINUS' and event.value=='PRESS':
                context.object.data.bevel_resolution -= 1
        
        if event.type == 'S' and event.value =='PRESS':
            bpy.ops.object.shade_smooth()
            
        if event.type == 'ONE' and event.value=='PRESS':
            bpy.context.object.data.resolution_u = 6
            bpy.context.object.data.render_resolution_u = 12
            bpy.context.object.data.bevel_resolution = 6
            bpy.context.object.data.fill_mode = 'FULL'
        
        if event.type == 'TWO' and event.value=='PRESS':    
            bpy.context.object.data.resolution_u = 64
            bpy.context.object.data.render_resolution_u = 64
            bpy.context.object.data.bevel_resolution = 16
            bpy.context.object.data.fill_mode = 'FULL'
        
        elif event.type == 'LEFTMOUSE':
            return self.finish() 

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.reset_object()
            bpy.context.object.show_wire = False
            context.object.data.fill_mode = 'HALF'
            return self.finish() 
        
        self.last_mouse_x = event.mouse_region_x
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def reset_object(self):
        self.depth_offset = self.start_depth_offset

    def invoke(self, context, event):

        self.start_depth_offset = context.object.data.bevel_depth
        self.last_mouse_x = event.mouse_region_x
        self.depth_offset = 0
        self.profile_offset = 0

        if context.object:
            context.object.data.fill_mode = 'FULL'
            self.start_mouse_position = Vector((event.mouse_region_x, event.mouse_region_y))
            self.curve = bpy.ops
            
            self.first_mouse_x = event.mouse_x
            self.first_value = context.object.data.bevel_depth

            args = (context, )
            self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw, args, "WINDOW", "POST_PIXEL")
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}

    def reset_object(self):
        #self.bevel.width = self.start_bevel_width
        #self.bevel.segments = self.start_bevel_segments
        #self.bevel.profile = self.start_bevel_profile
        #if self.created_bevel_modifier:
        #    self.object.modifiers.remove(self.bevel)
        self.curve = bpy.context
        self.curve.object.data.bevel_depth = 0
        self.curve.object.data.resolution_u = 6
        self.curve.object.data.render_resolution_u = 12
        self.curve.object.data.bevel_resolution = 6
        self.curve.object.data.fill_mode = 'FULL'   

    def finish(self):
        bpy.context.object.show_wire = False
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
        return {"FINISHED"}
    
    def draw(self, context):
        x, y = self.start_mouse_position
        first_value = self.first_value

        set_drawing_dpi(get_dpi())
        factor = get_dpi_factor()
        color_text1 = Hops_text_color()
        color_text2 = Hops_text2_color()
        color_border = Hops_border_color()
        color_border2 = Hops_border2_color()

        draw_box(x -14 * factor, y + 8 * factor, 224 * factor , 34* factor, color = color_border2)

        draw_box(x + 68 * factor, y + 8 * factor, 140 * factor , 30 * factor, color = color_border)

        draw_text("{:.3f}".format(context.object.data.bevel_depth),  x -12 * factor, y, size = 23, color = color_text1)
        
        draw_text("Segments (ctrl) -  {:.0f}".format(context.object.data.render_resolution_u),
                  x + 70 * factor, y + 11 * factor, size = 12, color = color_text2)
        
        draw_text("Resolution          -  {:.0f}".format(context.object.data.bevel_resolution),
                  x + 70 * factor, y - 4 * factor, size = 12, color = color_text2)
