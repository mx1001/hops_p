import os
import bpy
import bmesh
from bpy.props import *
import bgl
import blf
from . utils.blender_ui import get_dpi, get_dpi_factor


##############################
#NEW MODAL BEVEL
#############################


def draw_callback_pb(self, context):

    font_id = 0  # XXX, need to find out how best to get this.
    #set_drawing_dpi(display.get_dpi() * scale_factor)
    #dpi_factor = display.get_dpi_factor() * scale_factor
    #line_height = 18 * dpi_factor
    
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
    x = get_dpi()
    scale_factor = 0.9
    dpi_factor = get_dpi_factor() * scale_factor

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
    #Min and Max Idea
    if self.lvl == 1:
        #Show Segments Size
        bgl.glEnable(bgl.GL_BLEND)
        blf.position(font_id, self.click_pos[0], self.click_pos[1]+0.83 * get_dpi(), 0)
        bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
        blf.size(font_id, 12, get_dpi())
        blf.draw(font_id, "          (Min)")
    
    if self.lvl == 16:
        #Show Segments Size
        bgl.glEnable(bgl.GL_BLEND)
        blf.position(font_id, self.click_pos[0], self.click_pos[1]+0.83 * get_dpi(), 0)
        bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
        blf.size(font_id, 12, get_dpi())
        blf.draw(font_id, "                  (Max)")
    
    #Show Segments Size
    bgl.glEnable(bgl.GL_BLEND)
    blf.position(font_id, self.click_pos[0], self.click_pos[1]+0.55 * get_dpi() , 0)
    bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
    blf.size(font_id, 36, get_dpi())
    blf.draw(font_id, str(self.lvl))
        
    # And Underline Up Top
    #blf.position(font_id, self.click_pos[0], self.click_pos[1]+34, 0)
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
    bgl.glLineWidth(int(0.032* get_dpi()) )
    bgl.glBegin(bgl.GL_LINE_STRIP)
    #bgl.glVertex2d(20, 40)
    for n in range(-1,int(2.7 * get_dpi()) ): bgl.glVertex2i(self.click_pos[0]+n+2, self.click_pos[1]+int(get_dpi()/2.2))
    bgl.glEnd() 
    
    #Show All Bevel Information  
    bgl.glEnable(bgl.GL_BLEND)          
    blf.position(font_id, self.click_pos[0], self.click_pos[1]+0.208 * get_dpi(), 0)
    bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
    blf.size(font_id, 12, get_dpi())
    blf.draw(font_id, "B-Width - "  + '%.3f'%( self.mouse_pos) + " / " + " / " + "(W) - " + bpy.context.object.modifiers["Bevel"].offset_type)
    #blf.draw(font_id, "Bevel Width - "  + '%.3f'%( self.mouse_pos) + " / " + "Segments - " + str(self.lvl) + " / " + "(W)idth Method - " + bpy.context.object.modifiers["Bevel"].offset_type)
    
    # And Underline Up Bottom

    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
    bgl.glLineWidth(int(0.032* get_dpi()) )
    bgl.glBegin(bgl.GL_LINE_STRIP)

    for n in range(-1,int(2.7 * get_dpi()) ): bgl.glVertex2i(self.click_pos[0]+n+2, self.click_pos[1]+int(get_dpi()/10.2))
    bgl.glEnd()   
    
    #Show Additional Mesh Information 
    bgl.glEnable(bgl.GL_BLEND)           
    blf.position(font_id, self.click_pos[0], self.click_pos[1]-0.13* get_dpi(), 0)
    bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
    blf.size(font_id, 12, get_dpi())
    if is_bevel_2 == True:
        blf.draw(font_id, "Standard Mesh")
    elif is_bevel_3 == True:
        blf.draw(font_id, "CStep / Sstep - Warning: Bevels could not be showing due to bevel baking.")
    elif is_bevel == True:
        blf.draw(font_id, "CSsharp / Ssharp")
    elif is_bool == True:
        blf.draw(font_id, "Pending Boolean - Warning: Bevels could not be showing due to boolean pending.")
        
    if addon_pref.Diagnostics_Mode :
        #Diagnostic
        bgl.glEnable(bgl.GL_BLEND)
        blf.position(font_id, self.click_pos[0], self.click_pos[1]-0.37* get_dpi, 0)
        bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
        blf.size(font_id, 12, get_dpi())
        blf.draw(font_id, "Standard is - " + str(is_bevel_2) + "      " + "Sstep is - " + str(is_bevel_3)+ "      "  + "CSharp is - " + str(is_bevel))

    
class nwBevel(bpy.types.Operator):
    bl_idname = "view3d.bevelx"
    bl_label = "BevelSpecial (NW)"
    bl_options = {'REGISTER', 'UNDO'} 

    first_mouse_x = IntProperty()
    first_value = FloatProperty()
    angle = FloatProperty()
    
    def vdist(self):
      area=bpy.context.window.screen.areas[0]
      for x in bpy.context.window.screen.areas:
          if x.type=='VIEW_3D': area=x

      area.spaces[0].region_3d.view_distance
      return area.spaces[0].region_3d.view_distance
      
    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'MOUSEMOVE':

            delta = self.first_mouse_x - event.mouse_x
        
            self.mouse_pos=round(self.mouse_pos*10000)/10000
            #print (self.activeA)

            bpy.context.object.modifiers[self.bname].width = self.first_value + delta * 0.0008
            self.mouse_pos = round(bpy.context.object.modifiers[self.bname].width *10000)/10000

        if event.type == 'MOUSEMOVE' and event.shift:

            delta = self.first_mouse_x - event.mouse_x
        
            self.mouse_pos=round(self.mouse_pos*10000)/10000
            #print (self.activeA)

            bpy.context.object.modifiers[self.bname].width = self.first_value + delta * 0.0001
            self.mouse_pos = round(bpy.context.object.modifiers[self.bname].width *10000)/10000

        elif event.type == 'W' and event.value=='PRESS':
            modt=bpy.context.object.modifiers[self.bname].offset_type
            i=0
            
            for x in self.atype:
              i+=1
              if modt==x: break
            if i==3: i=0 

            bpy.context.object.modifiers[self.bname].offset_type=self.atype[i]
            self.activeA=self.atype[i]

        elif event.type == 'LEFTMOUSE':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        elif event.type == 'SPACE':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}


        elif event.type == 'WHEELUPMOUSE':

            if(self.lvl<16): self.lvl+=1
            bpy.context.object.modifiers[self.bname].segments=self.lvl

        elif event.type == 'NUMPAD_PLUS' and event.value=='PRESS':

            if(self.lvl<16): self.lvl+=1
            bpy.context.object.modifiers[self.bname].segments=self.lvl
            
            
        elif event.type == 'WHEELDOWNMOUSE':
      
            if(self.lvl>1): self.lvl-=1
            bpy.context.object.modifiers[self.bname].segments=self.lvl    

        elif event.type == 'NUMPAD_MINUS' and event.value=='PRESS':
      
            if(self.lvl>1): self.lvl-=1
            bpy.context.object.modifiers[self.bname].segments=self.lvl          

        elif event.type in {'DEL', 'BACK_SPACE'}:
            bpy.ops.object.modifier_remove(modifier=self.bname)
            return {'CANCELLED'}    
        
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            i=-1
            
            if event.type == 'ESC' and self.newlyCreated: bpy.ops.object.modifier_remove(modifier=self.bname)    

            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            bpy.context.object.draw_type = 'TEXTURED'
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            # the arguments we pass the the callback
            obj=bpy.context.object
            is_bevel = False


            for mode in bpy.context.object.modifiers :
                if mode.type == 'BEVEL' :
                    is_bevel = True

            if is_bevel == False:
                bpy.context.object.modifiers.new("Bevel", "BEVEL")
                bpy.context.object.modifiers["Bevel"].use_clamp_overlap = False
                bpy.context.object.modifiers["Bevel"].show_in_editmode = False
                #bpy.context.object.modifiers["Bevel"].width = bevelwidth
                bpy.context.object.modifiers["Bevel"].segments = 3
                bpy.context.object.modifiers["Bevel"].profile = 0.70
                bpy.context.object.modifiers["Bevel"].show_in_editmode = True
                
            self.first_value = context.object.modifiers["Bevel"].width
            hasBevel=False
            subd=0
            i=0
            bname=""
            self.newlyCreated=False
            
            for mod in obj.modifiers:
                i+=1
                #print (mod.type)
                if mod.type=="SUBSURF":
                    subd=i
                    #print ("SUBSURFACE!!")
                if mod.type=="BEVEL" and mod.limit_method!='WEIGHT':
                  hasBevel=True
                  bname=mod.name
            
            if subd==0:
               for mod in obj.modifiers:
                if mod.type=="SUBSURF":
                    subd=i

            
            if not hasBevel:

                #bpy.ops.object.modifier_add(type='BEVEL')
                bname=bpy.context.object.modifiers["Bevel"].name
                #bpy.context.object.modifiers[len(bpy.context.object.modifiers)-1].use_clamp_overlap = False
                #elf.newlyCreated=True


                #bpy.context.object.modifiers[len(bpy.context.object.modifiers)-1].limit_method='WEIGHT'
                #bpy.context.object.modifiers[len(bpy.context.object.modifiers)-1].width=self.vdist()/50


            obj.update_from_editmode() # Loads edit-mode data into object data
            self.bname=bname
            bpy.ops.object.mode_set(mode='OBJECT')
            
            self.lvl=bpy.context.object.modifiers[self.bname].segments 
            self.slvl=self.lvl
            self.click_pos=[event.mouse_region_x,event.mouse_region_y];
            self.mouse_pos = event.mouse_x
            self.first_mouse_x = event.mouse_x
            self.startPos=bpy.context.object.modifiers[self.bname].width;
            args = (self, context)

            
            self.atype=['OFFSET', 'WIDTH', 'DEPTH', 'PERCENT']
            self.btype=['NONE', 'ANGLE', 'WEIGHT', 'VGROUP']
            
            modt=bpy.context.object.modifiers[self.bname].offset_type
            i=0
            for x in self.atype:
              i+=1
              if modt==x: break
            #if i>3: i=0 
            self.activeA=self.atype[i-1]
            
            
            modL=bpy.context.object.modifiers[self.bname].limit_method
            i=0
            for x in self.atype:
              i+=1
              if modL==x: break
            if i>=3: i=0 
            self.activeL=self.btype[i]
            

           
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_pb, args, 'WINDOW', 'POST_PIXEL')


            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}
