import os
import bpy
import bmesh
from bpy.props import *
import bgl
import blf
from mathutils import Quaternion, Vector, Matrix
#from . utils.blender_ui import get_dpi, get_dpi_factor

def get_dpi(): return 120
def get_dpi_factor(): return 1

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
    #addon_pref = user_preferences.addons[current_dir].preferences

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
    #blf.draw(font_id, str(bpy.context.object.modifiers[self.id].count))
    
    # Underline Up Top
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
    bgl.glLineWidth(int(0.032* get_dpi()) )
    bgl.glBegin(bgl.GL_LINE_STRIP)
    #bgl.glVertex2d(20, 40)
    for n in range(-1,int(2.9 * get_dpi()) ): bgl.glVertex2i(self.click_pos[0]+n+2, self.click_pos[1]+int(get_dpi()/3.2))
    bgl.glEnd() 
     
    # draw some text / Needs To Show Axis
    bgl.glEnable(bgl.GL_BLEND)
    blf.position(font_id, self.click_pos[0], self.click_pos[1]+0.1 * get_dpi(), 0)
    bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
    blf.size(font_id, 12, get_dpi())
    blf.draw(font_id, "Array | Axis(X/Y/Z)" )
    
    # draw some text / Needs To Show Axis
    '''
    bgl.glEnable(bgl.GL_BLEND)
    blf.position(font_id, self.click_pos[0], self.click_pos[1]+0.083 * get_dpi(), 0)
    bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
    blf.size(font_id, 12, get_dpi())
    blf.draw(font_id, "Q >> X/Y/Z - Additional Array Axis" )
    '''
    
    # draw some text / Needs To Show Axis
    bgl.glEnable(bgl.GL_BLEND)
    blf.position(font_id, self.click_pos[0], self.click_pos[1]-0.1* get_dpi(), 0)
    bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
    blf.size(font_id, 12, get_dpi())
    blf.draw(font_id, "R >> Radial Array Toggle" )
    

    # And Underline Up Top
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
    bgl.glLineWidth(int(0.032* get_dpi()) )
    bgl.glBegin(bgl.GL_LINE_STRIP)

    for n in range(-1,int(2.9 * get_dpi()) ): bgl.glVertex2i(self.click_pos[0]+n+2, self.click_pos[1]+int(get_dpi()/26)-30)
    bgl.glEnd()   

    #Show X
    bgl.glEnable(bgl.GL_BLEND)
    blf.position(font_id, self.click_pos[0], self.click_pos[1]-0.400 * get_dpi(), 0)
    bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
    blf.size(font_id, 12, get_dpi())
    blf.draw(font_id, "x:  " + str(xvalue))

    #Show y
    bgl.glEnable(bgl.GL_BLEND)
    blf.position(font_id, self.click_pos[0], self.click_pos[1]-0.600 * get_dpi(), 0)
    bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
    blf.size(font_id, 12, get_dpi())
    blf.draw(font_id, "y:  " + str(yvalue))

    #Show z
    bgl.glEnable(bgl.GL_BLEND)
    blf.position(font_id, self.click_pos[0], self.click_pos[1]-0.800 * get_dpi(), 0)
    bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
    blf.size(font_id, 12, get_dpi())
    blf.draw(font_id, "z:  " + str(zvalue))
    
    #Show Additional Mesh Information 
    bgl.glEnable(bgl.GL_BLEND)           
    blf.position(font_id, self.click_pos[0], self.click_pos[1]-1 * get_dpi(), 0)
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

    ''' 
    if addon_pref.Diagnostics_Mode :
        #Diagnostic
        bgl.glEnable(bgl.GL_BLEND)
        blf.position(font_id, self.click_pos[0], self.click_pos[1]-27, 0)
        bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
        blf.size(font_id, 12, get_dpi())
        blf.draw(font_id, "Standard is - " + str(is_bevel_2) + "      " + "Sstep is - " + str(is_bevel_3)+ "      "  + "CSharp is - " + str(is_bevel))      
    '''
    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0) 

class radialArray(bpy.types.Operator):
    """Sets An Array To Modal"""
    bl_idname = "nw.radial_array"
    bl_label = "HOps Radial Array "
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}

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
    
    
    # offset strenght depends on viewport zoom level (could be also bbox width)
    def vdist(self):
      area=bpy.context.window.screen.areas[0]
      for x in bpy.context.window.screen.areas:
          if x.type=='VIEW_3D': area=x

      area.spaces[0].region_3d.view_distance
      return area.spaces[0].region_3d.view_distance


    # return a hidden vertex
    def tag_vert(self):
      
      obj=bpy.context.object
      bm = bmesh.new() # create an empty BMesh
      bm.from_mesh(obj.data) # fill it in from a Mesh

      center=Vector((0,0,0))
      for vert in bm.verts:
          if vert.hide: return vert.index
          center+=vert.co*obj.matrix_world
      
      center/=len(bm.verts)
      print ("center:", center)
      

      # create vert
      vertex1 = bm.verts.new( center )
      vertex1.hide= True # tag the vertex 
      
      bm.to_mesh(obj.data)  
      
      return vertex1.index
      
    
    def counter_rot_mesh(self, quat):
      print("counter rotating")
      bm = bmesh.new() # create an empty BMesh
      bm.from_mesh(self.mesh_bu.copy()) 

      rot=(quat.inverted()).to_matrix()

      bmesh.ops.rotate(bm, cent=bpy.context.object.location, matrix=rot, verts=bm.verts, space=self.start_mat )#, space=self.start_rot.to_matrix()) 
      
      bm.to_mesh(bpy.context.object.data)

      bpy.context.object.data.update()
      bpy.context.object.data.update()
      


    def modal(self, context, event):
        #context.area.tag_redraw()
        axis = 'x'


        deltax = self.first_mouse_x - event.mouse_x
        deltay = self.first_mouse_y - event.mouse_x
        deltaz = self.first_mouse_z - event.mouse_x
 
        # not sure how to make this function well with 360
        '''
        if event.type == 'Q' and event.value=='PRESS':

            bpy.context.object.modifiers[self.id].name = "Array001"
            bpy.context.object.modifiers.new("Array", "ARRAY")
            bpy.context.object.modifiers["Array"].use_relative_offset = False
            bpy.context.object.modifiers["Array"].use_constant_offset = True
        '''

        if event.type == 'X' and event.shift:
            self.nd=0
            axis = 'x'
            self.value_fix_y = bpy.context.object.modifiers["Array"].constant_offset_displace[1]
            self.value_fix_z = bpy.context.object.modifiers["Array"].constant_offset_displace[2]
            self.first_valuex = 0
            self.first_valuey = 0
            self.first_valuez = 0
            
               
               
        elif event.type == 'X' and event.value=='PRESS':
            self.nd=0
            bpy.context.object.modifiers["Array"].constant_offset_displace[1]=0
            bpy.context.object.modifiers["Array"].constant_offset_displace[2]=0
            axis = 'x'
            self.value_fix_y = bpy.context.object.modifiers["Array"].constant_offset_displace[1]
            self.value_fix_z = bpy.context.object.modifiers["Array"].constant_offset_displace[2]
            self.first_valuex = 0
            self.first_valuey = 0
            self.first_valuez = 0
            
            
            #for radial array
            if self.bend360:
               bpy.context.object.rotation_mode = 'QUATERNION'
               bpy.context.object.rotation_quaternion=  self.start_rot* self.Q[0]
               self.counter_rot_mesh(self.Q[0])
               bpy.context.object.modifiers["Array"].use_relative_offset = True
               bpy.context.object.modifiers["Array"].use_constant_offset = False

               
               
               

        elif event.type == 'Y' and event.shift:
            self.nd=1
            axis = 'y'
            self.value_fix_x = bpy.context.object.modifiers["Array"].constant_offset_displace[0]
            self.value_fix_z = bpy.context.object.modifiers["Array"].constant_offset_displace[2]
            self.first_valuex = 0
            self.first_valuey = 0
            self.first_valuez = 0



        elif event.type == 'Y' and event.value=='PRESS':
            self.nd=1
            bpy.context.object.modifiers["Array"].constant_offset_displace[0]=0
            bpy.context.object.modifiers["Array"].constant_offset_displace[2]=0
            axis = 'y'
            self.value_fix_x = bpy.context.object.modifiers["Array"].constant_offset_displace[0]
            self.value_fix_z = bpy.context.object.modifiers["Array"].constant_offset_displace[2]
            self.first_valuex = 0
            self.first_valuey = 0
            self.first_valuez = 0
            
            if self.bend360:               
               bpy.context.object.rotation_mode = 'QUATERNION'   
               bpy.context.object.rotation_quaternion=  self.start_rot*self.Q[1]
               self.counter_rot_mesh(self.Q[1])
               bpy.context.object.modifiers["Array"].use_relative_offset = True
               bpy.context.object.modifiers["Array"].use_constant_offset = False
   
        
        elif event.type =='Z' and event.shift:
            self.nd=2
            axis = 'z'
            self.value_fix_x = bpy.context.object.modifiers["Array"].constant_offset_displace[0]
            self.value_fix_y = bpy.context.object.modifiers["Array"].constant_offset_displace[1]
            self.first_valuex = 0
            self.first_valuey = 0
            self.first_valuez = 0


        elif event.type =='Z' and event.value=='PRESS':
            self.nd=2
            bpy.context.object.modifiers["Array"].constant_offset_displace[1]=0
            bpy.context.object.modifiers["Array"].constant_offset_displace[0]=0
            axis = 'z'
            self.value_fix_x = bpy.context.object.modifiers["Array"].constant_offset_displace[0]
            self.value_fix_y = bpy.context.object.modifiers["Array"].constant_offset_displace[1]
            self.first_valuex = 0
            self.first_valuey = 0
            self.first_valuez = 0

            #radial array part
            if self.bend360:               
               bpy.context.object.rotation_mode = 'QUATERNION'                      
               bpy.context.object.rotation_quaternion=  self.start_rot* self.Q[2]
               self.counter_rot_mesh(self.Q[2])
               bpy.context.object.modifiers["Array"].use_relative_offset = True
               bpy.context.object.modifiers["Array"].use_constant_offset = False 
               
               
               
        #radial array       
        elif event.type=='R' and event.value=='PRESS':
            
            if self.bend360:
              bpy.ops.object.modifier_remove(modifier=self.bend360_mod.name)
              self.bend360=False
              bpy.context.object.modifiers["Array"].use_constant_offset=True
              bpy.context.object.modifiers["Array"].use_relative_offset=False
              
            else:
              bpy.context.object.data=self.mesh_bu.copy()
              
              bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
              self.bend360=True
              self.bend360_mod=context.object.modifiers[len(context.object.modifiers)-1]
              self.bend360_mod.angle = 6.28319
              self.bend360_mod.deform_method = 'BEND'
              bpy.context.object.modifiers["Array"].use_constant_offset=False
              bpy.context.object.modifiers["Array"].use_relative_offset=True
  
              bpy.context.object.modifiers["Array"].count=max(5, bpy.context.object.modifiers["Array"].count) 
              
            bpy.context.object.data=self.mesh_bu.copy()
            bpy.context.object.rotation_quaternion=  self.start_rot
           
            return {'RUNNING_MODAL'}        
                    
        elif event.type == 'WHEELUPMOUSE':
            bpy.context.object.modifiers["Array"].count+=1

        elif event.type == 'NUMPAD_PLUS' and event.value=='PRESS':
            bpy.context.object.modifiers["Array"].count+=1

        elif event.type == 'NUMPAD_MINUS' and event.value=='PRESS':
            bpy.context.object.modifiers["Array"].count-=1

        elif event.type == 'WHEELDOWNMOUSE':
            bpy.context.object.modifiers["Array"].count-=1

        
        elif event.type == 'MOUSEMOVE':

    
            if self.bend360:
            
              delta= (event.mouse_x-self.first_mouse_x)   * 0.1 
              
              if delta<0: self.bend360_mod.angle = -6.28319
              else: self.bend360_mod.angle = 6.28319
              
              bpy.context.object.data.update()
              bpy.context.object.data.vertices[self.vert].co=Vector((delta/11,0,0))
            
              return {'RUNNING_MODAL'}
            

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

        elif event.type in {'RIGHTMOUSE', 'ESC', 'LEFTMOUSE'}:

            
            # serialize array data
            bpy.data.objects[context.object.name]['arrAxis']=self.nd
            bpy.data.objects[context.object.name]['arrBaseRot']=self.start_rot
            bpy.data.objects[context.object.name]['a0']= self.start_mat[0]
            bpy.data.objects[context.object.name]['a1']= self.start_mat[1]
            bpy.data.objects[context.object.name]['a2']= self.start_mat[2]
            bpy.data.objects[context.object.name]['a3']= self.start_mat[3]
            
            if event.type=='ESC' and not self.exists:
                bpy.ops.object.modifier_remove(modifier="Array")
                bpy.context.object.data=self.mesh_bu
                if self.bend360: bpy.ops.object.modifier_remove(modifier=self.bend360_mod.name)

           ##############################
           
           
            if event.type in {'RIGHTMOUSE', 'ESC'}: 
                context.object.location.x = self.first_value
                return {'CANCELLED'}
            
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')   
            
            return {'FINISHED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.object:
            #self.value_fix_x = 0
            #self.value_fix_y = 0
            #self.value_fix_z = 0
            
            
            
            #################
            # for 360 array #
            #################
            self.bend360=False
            self.vert= self.tag_vert()

            
            print("TV:", self.vert)
            
            self.Q=[Quaternion((1,0,0,0))]*3
            self.Q[1]=Quaternion((0.707,0.707,0,0))  #Y
            self.Q[2]=Quaternion((0.707,0,0.707,0))  #Z
            
            #mesh dupe
            self.mesh=context.object.data
            self.mesh_bu=context.object.data.copy()
            
            
            self.start_rot=bpy.context.object.rotation_quaternion.copy()
            self.start_mat=Matrix.Identity(4) 
            self.start_mat.translation=bpy.context.object.matrix_world.translation
            
            ##############
            

            self.first_mouse_x = event.mouse_x
            self.first_value = context.object.location.x

   
            cArrID=-1
            n=-1



            is_array = False
            for mode in bpy.context.object.modifiers :
                if mode.type == 'ARRAY' :
                    is_array = True
                
                
            #legacy mess         
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

                    


            if is_array == False :
                bpy.context.object.modifiers.new("Array", "ARRAY")
                bpy.context.object.modifiers["Array"].use_relative_offset = False
                bpy.context.object.modifiers["Array"].use_constant_offset = True


            self.first_valuex = -1 * bpy.context.object.modifiers["Array"].constant_offset_displace[0]
            self.first_valuey = -1 * bpy.context.object.modifiers["Array"].constant_offset_displace[1]
            self.first_valuez = -1 * bpy.context.object.modifiers["Array"].constant_offset_displace[2]
            
            self.click_pos=[event.mouse_region_x,event.mouse_region_y];
            self.mouse_pos = event.mouse_x
            self.first_mouse_x = event.mouse_x
            self.first_mouse_y = event.mouse_x
            self.first_mouse_z = event.mouse_x

            
            self.exists=False  
            
            # detect serialized state. restore original
            if bpy.data.objects[context.object.name].get('arrAxis')!=None:
                self.exists=True
    
                s360=None
                for m in context.object.modifiers:
                  if m.type=='SIMPLE_DEFORM':
                    s360=m
                    break
                
                if s360:  
                  self.bend360=True
                  self.bend360_mod=s360
                  self.bend360_mod.angle = 6.28319
                  self.bend360_mod.deform_method = 'BEND'

                self.dir=bpy.data.objects[context.object.name].get('arrAxis')
                br=bpy.data.objects[context.object.name].get('arrBaseRot')
                self.start_rot=Quaternion((br[0],br[1],br[2],br[3]))
                A=Matrix.Identity(4)
                self.start_mat[0]=bpy.data.objects[context.object.name].get('a0')
                self.start_mat[1]=bpy.data.objects[context.object.name].get('a1')
                self.start_mat[2]=bpy.data.objects[context.object.name].get('a2')
                self.start_mat[3]=bpy.data.objects[context.object.name].get('a3')
                A.translation=self.start_mat.translation
                self.start_mat=A  
                bm = bmesh.new()
                bm.from_mesh(self.mesh_bu.copy()) 

                rot=( self.Q[self.dir]).to_matrix()

                bmesh.ops.rotate(bm, cent=bpy.context.object.location,matrix=rot, verts=bm.verts, space=self.start_mat )#, 
                
                bm.to_mesh(self.mesh_bu)
                self.mesh_bu.update()
 
            ############
            
            
            
            args = (self, context)
            
            self.id=int(cArrID)

            
            self._handle = bpy.types.SpaceView3D.draw_handler_add(gui_update, args, 'WINDOW', 'POST_PIXEL')
            
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}
 
 

        
        
def register():
    bpy.utils.register_class(radialArray)



def unregister():
    bpy.utils.unregister_class(radialArray)



if __name__ == "__main__":
    register()
     