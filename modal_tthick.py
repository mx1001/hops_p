import os
import bpy
import bmesh
from bpy.props import *
import bgl
import blf
#from . utils.blender_ui import get_dpi, get_dpi_factor
from math import log,sqrt


def draw_callback_pt(self, context):


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
                
    #Number
    blf.position(font_id, self.click_pos[0], self.click_pos[1]+36, 0)
    bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
    blf.size(font_id, 21, 132)
    blf.draw(font_id, '%.2f'%( self.mouse_pos))
    
    # And Underline Up Top
    blf.position(font_id, self.click_pos[0], self.click_pos[1]+34, 0)
    blf.size(font_id, 12, 62)
    blf.draw(font_id, "_____________________________")
    
    # Tthick
    blf.position(font_id, self.click_pos[0], self.click_pos[1]+15, 0)
    blf.size(font_id, 14, 62)
    #blf.draw(font_id, "T-thick - " + '%.3f'%( self.mouse_pos))
    blf.draw(font_id, "T-Thick -")

    # And Underline Up Top
    blf.position(font_id, self.click_pos[0], self.click_pos[1]+11, 0)
    blf.size(font_id, 12, 62)
    blf.draw(font_id, "_____________________________")
    
    #Show Additional Mesh Information            
    blf.position(font_id, self.click_pos[0], self.click_pos[1]-10, 0)
    bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
    blf.size(font_id, 14, 60)
    if is_bevel_2 == True:
        #blf.draw(font_id, "Standard Mesh")
        blf.draw(font_id, "Adding Solidify On A Bevelled Mesh")
    elif is_bevel_3 == True:
        #blf.draw(font_id, "CStep / Sstep")
        blf.draw(font_id, "Adding Solidify On A (C/S)Stepped Mesh")
    elif is_bevel == True:
        #blf.draw(font_id, "CSsharp / Ssharp")
        blf.draw(font_id, "Adding Solidify On A CSharpened Mesh")
    elif is_bool == True:
        #blf.draw(font_id, "Pending Boolean")
        blf.draw(font_id, "There Is A Pending Boolean On This Mesh")
    else:
        blf.draw(font_id, "Normal Mesh ")
    
    if addon_pref.Diagnostics_Mode :
        #Diagnostic
        blf.position(font_id, self.click_pos[0], self.click_pos[1]-27, 0)
        bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
        blf.size(font_id, 14, 70)
        blf.draw(font_id, "Standard is - " + str(is_bevel_2) + "      " + "Sstep is - " + str(is_bevel_3)+ "      "  + "CSharp is - " + str(is_bevel))
    
    glDisable(GL_BLEND)
    glDisable(GL_LINE_SMOOTH)
        
    
class nwSolidify(bpy.types.Operator):
    """Draw a line with the mouse"""
    bl_idname = "nw.solidify"
    bl_label = "nw solidify"
    bl_options = {'REGISTER', 'UNDO'}
    
    def vdist(self):
      area=bpy.context.window.screen.areas[0]
      for x in bpy.context.window.screen.areas:
          if x.type=='VIEW_3D': area=x

      area.spaces[0].region_3d.view_distance
      return area.spaces[0].region_3d.view_distance
      
      
      
      
    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'MOUSEMOVE':
            XD=self.vdist()
            self.mouse_pos=((event.mouse_region_x-self.click_pos[0])/1000*XD+self.startPos) #*(0.1+self.lvl)
            self.mouse_pos=round(self.mouse_pos*10000)/10000

            bpy.context.object.modifiers[self.bname].thickness=self.mouse_pos
           
        
        elif event.type == 'LEFTMOUSE':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        elif event.type == 'WHEELUPMOUSE':
            self.lvl+=1
            
        elif event.type == 'WHEELDOWNMOUSE':
            if(self.lvl>0): self.lvl-=1    
 
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
            
            hasSolidify=False
            subd=0
            i=0
            bname=""
            self.newlyCreated=False
            for mod in obj.modifiers:
                i+=1
                if mod.type=="SUBSURF" and subd==0: subd=i
                if mod.type=="SOLIDIFY":
                  hasSolidify=True
                  bname=mod.name
            
            
            if not hasSolidify:
                 bpy.ops.object.modifier_add(type='SOLIDIFY')
                 bname="Solidify"
                 bpy.context.object.modifiers[len(bpy.context.object.modifiers)-1].name=bname
                 bpy.context.object.modifiers["Solidify"].use_quality_normals = True
                 bpy.context.object.modifiers["Solidify"].use_even_offset = True

                 
                 self.newlyCreated=True
            
            if hasSolidify:
                bname="Solidify"
                #XD=len(bpy.context.object.modifiers)-subd
                
                #for x in range (0, XD):
                    #bpy.ops.object.modifier_move_up(modifier=bname)
            
            """
            #This Area May Not Need To Exist
            try:
                self.first_value = context.object.modifiers["Bevel"].width
            except:
                print("could not find second bevel... adding")
                bpy.context.object.modifiers.new("Bevel", "BEVEL")
                bpy.context.object.modifiers["Bevel"].use_clamp_overlap = False
                bpy.context.object.modifiers["Bevel"].show_in_editmode = False
                bpy.context.object.modifiers["Bevel"].segments = 3
                bpy.context.object.modifiers["Bevel"].profile = 0.70
                bpy.context.object.modifiers["Bevel"].show_in_editmode = True
                bpy.context.object.modifiers["Bevel"].limit_method = 'ANGLE'
                print("Added bevel modifier - Via 3rd")
            """
            
            obj.update_from_editmode() # Loads edit-mode data into object data
            self.bname=bname
            bpy.ops.object.mode_set(mode='OBJECT')
            
            self.lvl=abs(round(log(abs(bpy.context.object.modifiers[self.bname].thickness+0.0000001), 2)))
            self.slvl=self.lvl
            self.click_pos=[event.mouse_region_x,event.mouse_region_y];
            self.mouse_pos=0
            self.startPos=bpy.context.object.modifiers[self.bname].thickness;
            args = (self, context)
            
   
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_pt, args, 'WINDOW', 'POST_PIXEL')


            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}
