import os
import bpy
import bmesh
from bpy.props import *
import bgl
import blf
from . utils.blender_ui import get_dpi, get_dpi_factor


    
def gui_update(self,context):

    xvalue = round(bpy.context.object.modifiers["Array"].constant_offset_displace[0] *10000)/10000
    yvalue = round(bpy.context.object.modifiers["Array"].constant_offset_displace[1] *10000)/10000
    zvalue = round(bpy.context.object.modifiers["Array"].constant_offset_displace[2] *10000)/10000

    font_id = 0  # XXX, need to find out how best to get this.
    
    is_bool = False
    is_bevel = False
    is_bevel_3 = False
    is_bevel_2 = False
    is_solidify = False
    is_multiselected = False
    is_notselected = False
    is_noactiveobject = False
    multislist = bpy.context.selected_objects
    activeobject = bpy.context.scene.objects.active
    is_formerge = False
    current_dir = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    user_preferences = bpy.context.user_preferences
    addon_pref = user_preferences.addons[current_dir].preferences

    if len(multislist) > 1:
        is_multiselected = True
    if len(multislist) < 1:
        is_notselected = True
    if activeobject == None:
        is_noactiveobject = True

    for obj in bpy.context.selected_objects:
        if obj.name.startswith("AP"):
            is_formerge = True
            pass

    for mode in bpy.context.object.modifiers :
            if mode.type == 'BEVEL' :
                if mode.limit_method == 'WEIGHT':
                    is_bevel = True
            if mode.type == "BEVEL":
                if mode.profile > 0.70 and mode.profile < 0.72:
                    is_bevel_3 = True
                    #print("Bevel 3 is true")
            if mode.type == "BEVEL":
                if mode.limit_method == 'ANGLE' or mode.limit_method == 'NONE':
                    is_bevel_2 = True
                    #print("Bevel 2 is true")
            if mode.type == 'BOOLEAN' :
                is_bool = True
            if mode.type == 'SOLIDIFY':
                is_solidify = True
                
    arraycount = 0,
    try:
        arraycount = bpy.context.object.modifiers[self.id].count
    except:
        arraycount = 0
    
    #Show Count
    bgl.glEnable(bgl.GL_BLEND)
    blf.position(font_id, self.click_pos[0], self.click_pos[1]+0.55 * get_dpi() , 0)
    bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
    blf.size(font_id, 36, get_dpi())
    blf.draw(font_id, str(bpy.context.object.modifiers[self.id].count))
    
    # Underline Up Top
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
    bgl.glLineWidth(int(0.032* get_dpi()) )
    bgl.glBegin(bgl.GL_LINE_STRIP)
    #bgl.glVertex2d(20, 40)
    for n in range(-1,int(2.9 * get_dpi()) ): bgl.glVertex2i(self.click_pos[0]+n+2, self.click_pos[1]+int(get_dpi()/2.2))
    bgl.glEnd() 
     
    # draw some text / Needs To Show Axis
    bgl.glEnable(bgl.GL_BLEND)
    blf.position(font_id, self.click_pos[0], self.click_pos[1]+0.277 * get_dpi(), 0)
    bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
    blf.size(font_id, 12, get_dpi())
    blf.draw(font_id, "Array | Axis(X/Y/Z)" )
    
    # draw some text / Needs To Show Axis
    bgl.glEnable(bgl.GL_BLEND)
    blf.position(font_id, self.click_pos[0], self.click_pos[1]+0.083 * get_dpi(), 0)
    bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
    blf.size(font_id, 12, get_dpi())
    blf.draw(font_id, "Q >> X/Y/Z - Additional Array Axis" )
    
    # And Underline Up Top
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
    bgl.glLineWidth(int(0.032* get_dpi()) )
    bgl.glBegin(bgl.GL_LINE_STRIP)

    for n in range(-1,int(2.9 * get_dpi()) ): bgl.glVertex2i(self.click_pos[0]+n+2, self.click_pos[1]+int(get_dpi()/26))
    bgl.glEnd()   

    #Show X
    bgl.glEnable(bgl.GL_BLEND)
    blf.position(font_id, self.click_pos[0], self.click_pos[1]-0.166 * get_dpi(), 0)
    bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
    blf.size(font_id, 12, get_dpi())
    blf.draw(font_id, "x:  " + str(xvalue))

    #Show y
    bgl.glEnable(bgl.GL_BLEND)
    blf.position(font_id, self.click_pos[0], self.click_pos[1]-0.347 * get_dpi(), 0)
    bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
    blf.size(font_id, 12, get_dpi())
    blf.draw(font_id, "y:  " + str(yvalue))

    #Show z
    bgl.glEnable(bgl.GL_BLEND)
    blf.position(font_id, self.click_pos[0], self.click_pos[1]-0.527 * get_dpi(), 0)
    bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
    blf.size(font_id, 12, get_dpi())
    blf.draw(font_id, "z:  " + str(zvalue))
    
    #Show Additional Mesh Information 
    bgl.glEnable(bgl.GL_BLEND)           
    blf.position(font_id, self.click_pos[0], self.click_pos[1]-0.722 * get_dpi(), 0)
    bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
    blf.size(font_id, 12, get_dpi())
    if is_bevel_2 == True:
        #blf.draw(font_id, "Standard Mesh")
        blf.draw(font_id, "Adding Array On A Bevelled Mesh")
    elif is_bevel_3 == True:
        #blf.draw(font_id, "CStep / Sstep")
        blf.draw(font_id, "Adding Array On A (C/S)Stepped Mesh")
    elif is_bevel == True:
        #blf.draw(font_id, "CSsharp / Ssharp")
        blf.draw(font_id, "Adding Array On A CSharpened Mesh")
    elif is_bool == True:
        #blf.draw(font_id, "Pending Boolean")
        blf.draw(font_id, "There Is A Pending Boolean On This Mesh")
    else:
        blf.draw(font_id, "Normal Mesh ")
    
    if addon_pref.Diagnostics_Mode :
        #Diagnostic
        bgl.glEnable(bgl.GL_BLEND)
        blf.position(font_id, self.click_pos[0], self.click_pos[1]-27, 0)
        bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
        blf.size(font_id, 12, get_dpi())
        blf.draw(font_id, "Standard is - " + str(is_bevel_2) + "      " + "Sstep is - " + str(is_bevel_3)+ "      "  + "CSharp is - " + str(is_bevel))       

 

class a_rray(bpy.types.Operator):
    """Sets An Array To Modal"""
    bl_idname = "nw.a_rray"
    bl_label = "nw "
    bl_options = {'REGISTER', 'UNDO'} 

    first_mouse_x = IntProperty()
    first_mouse_y = IntProperty()
    first_mouse_z = IntProperty()
    first_valuex = FloatProperty()
    first_valuey = FloatProperty()
    first_valuez = FloatProperty()
    axis = StringProperty()
    value_fix_x = 0
    value_fix_y = 0
    value_fix_z = 0
    nd = 0
    def vdist(self):
      area=bpy.context.window.screen.areas[0]
      for x in bpy.context.window.screen.areas:
          if x.type=='VIEW_3D': area=x

      area.spaces[0].region_3d.view_distance
      return area.spaces[0].region_3d.view_distance

    def modal(self, context, event):
        context.area.tag_redraw()
        axis = 'x'


        deltax = self.first_mouse_x - event.mouse_x
        deltay = self.first_mouse_y - event.mouse_x
        deltaz = self.first_mouse_z - event.mouse_x
 


        
        if event.type == 'Q' and event.value=='PRESS':

            bpy.context.object.modifiers[self.id].name = "Array001"
            bpy.context.object.modifiers.new("Array", "ARRAY")
            bpy.context.object.modifiers["Array"].use_relative_offset = False
            bpy.context.object.modifiers["Array"].use_constant_offset = True

        elif event.type == 'X' and event.shift:
            self.nd=0
            axis = 'x'
            self.value_fix_y = bpy.context.object.modifiers["Array"].constant_offset_displace[1]
            self.value_fix_z = bpy.context.object.modifiers["Array"].constant_offset_displace[2]
            self.first_valuex = 0
            self.first_valuey = 0
            self.first_valuez = 0

        elif event.type == 'X':
            self.nd=0
            bpy.context.object.modifiers["Array"].constant_offset_displace[1]=0
            bpy.context.object.modifiers["Array"].constant_offset_displace[2]=0
            axis = 'x'
            self.value_fix_y = bpy.context.object.modifiers["Array"].constant_offset_displace[1]
            self.value_fix_z = bpy.context.object.modifiers["Array"].constant_offset_displace[2]
            self.first_valuex = 0
            self.first_valuey = 0
            self.first_valuez = 0

        elif event.type == 'Y' and event.shift:
            self.nd=1
            axis = 'y'
            self.value_fix_x = bpy.context.object.modifiers["Array"].constant_offset_displace[0]
            self.value_fix_z = bpy.context.object.modifiers["Array"].constant_offset_displace[2]
            self.first_valuex = 0
            self.first_valuey = 0
            self.first_valuez = 0

        elif event.type == 'Y':
            self.nd=1
            bpy.context.object.modifiers["Array"].constant_offset_displace[0]=0
            bpy.context.object.modifiers["Array"].constant_offset_displace[2]=0
            axis = 'y'
            self.value_fix_x = bpy.context.object.modifiers["Array"].constant_offset_displace[0]
            self.value_fix_z = bpy.context.object.modifiers["Array"].constant_offset_displace[2]
            self.first_valuex = 0
            self.first_valuey = 0
            self.first_valuez = 0
        
        elif event.type =='Z' and event.shift:
            self.nd=2
            axis = 'z'
            self.value_fix_x = bpy.context.object.modifiers["Array"].constant_offset_displace[0]
            self.value_fix_y = bpy.context.object.modifiers["Array"].constant_offset_displace[1]
            self.first_valuex = 0
            self.first_valuey = 0
            self.first_valuez = 0

        elif event.type =='Z':
            self.nd=2
            bpy.context.object.modifiers["Array"].constant_offset_displace[1]=0
            bpy.context.object.modifiers["Array"].constant_offset_displace[0]=0
            axis = 'z'
            self.value_fix_x = bpy.context.object.modifiers["Array"].constant_offset_displace[0]
            self.value_fix_y = bpy.context.object.modifiers["Array"].constant_offset_displace[1]
            self.first_valuex = 0
            self.first_valuey = 0
            self.first_valuez = 0
        
            
        elif event.type == 'WHEELUPMOUSE':
            bpy.context.object.modifiers["Array"].count+=1

        elif event.type == 'NUMPAD_PLUS' and event.value=='PRESS':
            bpy.context.object.modifiers["Array"].count+=1

        elif event.type == 'NUMPAD_MINUS' and event.value=='PRESS':
            bpy.context.object.modifiers["Array"].count-=1

        elif event.type == 'WHEELDOWNMOUSE':
            bpy.context.object.modifiers["Array"].count-=1

        
        elif event.type == 'MOUSEMOVE':
 
            if self.nd == 0:
                #self.first_valuex = 0
                self.first_valuey = 0
                self.first_valuez = 0       
                bpy.context.object.modifiers["Array"].constant_offset_displace[self.nd] = -1 * (self.first_valuex + deltax * 0.008) - self.value_fix_y - self.value_fix_z
            elif self.nd == 1:
                self.first_valuex = 0
                #self.first_valuey = 0
                self.first_valuez = 0
                bpy.context.object.modifiers["Array"].constant_offset_displace[self.nd] = -1 * (self.first_valuey + deltay * 0.008) - self.value_fix_x - self.value_fix_z
            elif self.nd == 2:
                self.first_valuex = 0
                self.first_valuey = 0
                #self.first_valuez = 0
                bpy.context.object.modifiers["Array"].constant_offset_displace[self.nd] = -1 * (self.first_valuez + deltaz * 0.008) - self.value_fix_x - self.value_fix_y

        elif event.type == 'LEFTMOUSE':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        elif event.type == 'LEFTMOUSE':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}


        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.object.location.x = self.first_value
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.object:
            #self.value_fix_x = 0
            #self.value_fix_y = 0
            #self.value_fix_z = 0

            self.first_mouse_x = event.mouse_x
            self.first_value = context.object.location.x
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(gui_update, args, 'WINDOW', 'POST_PIXEL')
            #self._handle = bpy.types.SpaceView3D.draw_handler_add(gui_update, args, 'WINDOW', 'POST_PIXEL')

            #self.start=2
            #self.nd=0
            cArrID=-1
            n=-1
            nrf=False


            #NARRAY takes priority
            for x in bpy.context.object.modifiers:
                n+=1
                if x.name=="Array":
                    cArrID=n
                    oo=bpy.context.object.modifiers["Array"].constant_offset_displace

                    ixx=0
                    if oo[1]>0 or oo[1]<0 : ixx=1
                    if oo[2]>0 or oo[2]<0 : ixx=2
                    self.nd=ixx
                    if self.nd == 0:
                        self.start=oo[0]
                    elif self.nd == 1:
                        self.start=oo[1]
                    elif self.nd == 2:
                        self.start=oo[2]
                    nrf=True
                    
            is_array = False


            for mode in bpy.context.object.modifiers :
                if mode.type == 'ARRAY' :
                    is_array = True

            if is_array == False :
                bpy.context.object.modifiers.new("Array", "ARRAY")


            self.first_valuex = -1 * bpy.context.object.modifiers["Array"].constant_offset_displace[0]
            self.first_valuey = -1 * bpy.context.object.modifiers["Array"].constant_offset_displace[1]
            self.first_valuez = -1 * bpy.context.object.modifiers["Array"].constant_offset_displace[2]
            
            self.click_pos=[event.mouse_region_x,event.mouse_region_y];
            self.mouse_pos = event.mouse_x
            self.first_mouse_x = event.mouse_x
            self.first_mouse_y = event.mouse_x
            self.first_mouse_z = event.mouse_x
            
            args = (self, context)
            
            self.id=int(cArrID)
            bpy.context.object.modifiers["Array"].use_relative_offset = False
            bpy.context.object.modifiers["Array"].use_constant_offset = True
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}
        