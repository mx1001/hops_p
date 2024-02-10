import bpy, bmesh
import random
from mathutils import Color
from . import infobar
from . materials.capaint import carpaint_material
from . materials.emission_glow import emission_glow_material
from ... preferences import get_preferences
from ... ui_framework.master import Master
from ... utility.base_modal_controls import Base_Modal_Controls

# Cursor Warp imports
from ... utils.toggle_view3d_panels import collapse_3D_view_panels
from ... utils.modal_frame_drawing import draw_modal_frame
from ... utils.cursor_warp import mouse_warp
from ... addon.utility import method_handler


class HOPS_OT_MaterialScroll(bpy.types.Operator):
    bl_idname = "hops.material_scroll"
    bl_label = "Material Scroll"
    bl_options = {'REGISTER', 'UNDO', 'GRAB_CURSOR'}
    bl_description = """Interactively scroll through materials
    
Ctrl + LMB - Blank material scroll
(Generate new random material each scroll)

Shift + LMB - Non-Destructive material scroll
(non-destructive / keeps indice connections)

Press H for help
"""

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT'} and obj.mode in {'OBJECT', 'EDIT'}


    def invoke(self, context, event):
        
        self.copy_view = get_preferences().behavior.mat_viewport

        #self.scroll_modes = {'NORMAL', 'BLANK', 'DESTRUCTIVE'} enum prop placeholder
        self.scroll_mode = 'NORMAL'
        if event.ctrl:
            self.scroll_mode = 'BLANK'
        elif event.shift:
            self.scroll_mode = 'DESTRUCTIVE'
        hide_flag = not  context.preferences.filepaths.show_hidden_files_datablocks 
        self.materials = [mat.name for mat in bpy.data.materials if not mat.grease_pencil and (not mat.name.startswith(".") or hide_flag)]
        if self.scroll_mode != 'BLANK' and not self.materials:
            self.report({'INFO'}, "No materials found")
            return {'CANCELLED'}

        self.overlay_orig = context.space_data.overlay.show_overlays
        context.space_data.overlay.show_overlays = False

        self.mode = context.mode
        self.active = context.active_object
        self.edit_mode_init = False
        if self.mode == 'EDIT_MESH':
            self.active.select_set(True)
            self.edit_mode_init = True
            bpy.ops.object.mode_set(mode = 'OBJECT')

        self.objects = [obj for obj in context.selected_objects if obj.type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT'} ]

        if not self.objects:
            self.report({'INFO'}, "No valid object is selected")
            return {'CANCELLED'}
        #grab whatever object if active was excluded from valid objects, for whatever reason 
        if self.active not in self.objects:
            self.active = self.objects[0] 

        #backup and junk
        self.slot_backup = dict()
        self.created_mats = set()
        self.created_slots = []
        self.data_index_back = dict()

        #sroll stuff
        self.material_types = ['PRINCIPLED', 'CARPAINT', 'EMISSION']
        self.material_type = 'PRINCIPLED'
        self.force_enable = set()
        self.slot_modes = ['ACTIVE', 'ALL', 'NOT ACTIVE']
        self.slot_index =0
        self.slot_mode = 'ACTIVE'
        self.enable_color = False
        
        self.obj_slots = {}
        
        #mappring for material slots to object index, their original material, and current material index
        for  o in  self.objects:
            
            back = [s.material.name if s.material else None for s in o.material_slots ]
            self.slot_backup.update ( {o:back} )
            if self.mode == 'EDIT_MESH' and self.scroll_mode == 'BLANK' :

                self.data_index_back.update( {o:[p.material_index for p in o.data.polygons]} )
                
                self.random_mat()
                o.data.materials.append(bpy.data.materials[ self.materials[-1] ])
                index = len (o.data.materials) -1

                for polygon in o.data.polygons:
                    if polygon.select:
                        polygon.material_index = index

                o.active_material_index =  index
                self.created_slots.append(o)

            if not o.material_slots:
                o.data.materials.append(None)
                self.created_slots.append(o)

            piece = [self.materials.index(s.material.name) if s.material else 0 for  s in o.material_slots ]  
            self.obj_slots.update({o:piece})

        # filepathprefs = bpy.context.preferences.filepaths
        # for material in [mat for mat in bpy.data.materials if not mat.name.startswith('.')] if filepathprefs.show_hidden_files_datablocks else bpy.data.materials:
        #     self.materials.append(material)


        # Base Systems
        self.master = Master(context=context)
        self.master.only_use_fast_ui = True
        self.base_controls = Base_Modal_Controls(context, event)
        self.original_tool_shelf, self.original_n_panel = collapse_3D_view_panels()
        self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.safe_draw_shader, (context,), 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)
        #infobar.initiate(self)
        return {"RUNNING_MODAL"}


    def modal(self, context, event):

        # Base Systems
        self.master.receive_event(event=event)
        self.base_controls.update(context, event)
        mouse_warp(context, event)
        
        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        elif event.type == 'Z' and (event.shift or event.alt):
            return {'PASS_THROUGH'}

        elif self.base_controls.confirm:
            if self.overlay_orig:
                context.space_data.overlay.show_overlays = True
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            self.clean_mats()
            self.report({'INFO'}, "Finished")
            if self.edit_mode_init:
                bpy.ops.object.mode_set(mode = 'EDIT')
            return {'FINISHED'}

        elif self.base_controls.cancel:
            self.restore_slots()
            if self.overlay_orig:
                context.space_data.overlay.show_overlays = True
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            self.clean_mats()
            self.report({'INFO'}, "Cancelled")
            if self.edit_mode_init:
                bpy.ops.object.mode_set(mode = 'EDIT')
            return {'CANCELLED'}

        elif self.base_controls.scroll or (event.type in {'Z', 'X'} and event.value == 'PRESS'):
            direction = -1 if (event.type in {'X'} or self.base_controls.scroll == -1) else 1

            if event.shift:
                if event.type in {'NUMPAD_PLUS', 'EQUAL','NUMPAD_MINUS', 'MINUS'}:
                    direction*=-1
                for o in self.objects:
                    max_index = len (o.material_slots) -1
                    index = o.active_material_index
                    index -= direction
                    index = 0 if index > max_index else index
                    index = max_index if index < 0  else index
                    o.active_material_index = index
            else:
                
                self.material_scroll( direction = direction)

        elif event.type == 'T' and event.value == 'PRESS': #and self.blank_material_scroll:
            if self.scroll_mode == 'NORMAL':
                self.scroll_mode = 'BLANK'
            #types = ['PRINCIPLED', 'EMISSION', 'GLASS', 'CARPAINT']
            types = self.material_types
            self.material_type = types[(types.index(self.material_type) + 1) % len(types)]
            self.report({'INFO'}, f"Material Type: {self.material_type.capitalize()}")

        elif event.type == 'B' and event.value == 'PRESS':
            self.scroll_mode = 'BLANK' if self.scroll_mode != 'BLANK' else 'NORMAL'  
            self.report({'INFO'}, f"Scroll Mode: {self.scroll_mode}")

        elif event.type == 'D' and event.value == 'PRESS':
            self.scroll_mode = 'DESTRUCTIVE' if self.scroll_mode != 'DESTRUCTIVE' else 'NORMAL'
            self.report({'INFO'}, f"Scroll Mode: {self.scroll_mode}")

        elif event.type == 'R' and event.value == 'PRESS':
            if self.scroll_mode != 'DESTRUCTIVE':
                self.randomize_mats()
                self.report({'INFO'}, "Randmized ALL")

        elif event.type == 'A' and event.value == 'PRESS':
            self.slot_index = self.slot_index +1 if self.slot_index<2 else 0
            self.slot_mode = self.slot_modes[self.slot_index]
            self.report({'INFO'}, F"Affected slots: {self.slot_mode}")
        
        elif self.scroll_mode != 'NORMAL' and event.type == 'C' and event.value == 'PRESS':
            self.enable_color = not self.enable_color
            msg = "ON" if self.enable_color else "OFF"
            self.report({'INFO'}, F"COLOR: {msg}")

        elif self.base_controls.tilde and event.shift == True:
            context.space_data.overlay.show_overlays = not context.space_data.overlay.show_overlays

        elif event.type == 'ONE' and event.value == 'PRESS':
            if 0 not in self.force_enable :
                self.force_enable.add(0)
            else :
                self.force_enable.discard(0)
        elif event.type == 'TWO' and event.value == 'PRESS':
            if 1 not in self.force_enable :
                self.force_enable.add(1)
            else :
                self.force_enable.discard(1)

        elif event.type == 'THREE' and event.value == 'PRESS':
            if 2 not in self.force_enable :
                self.force_enable.add(2)
            else :
                self.force_enable.discard(2)

        elif event.type == 'FOUR' and event.value == 'PRESS':
            if 3 not in self.force_enable :
                self.force_enable.add(3)
            else :
                self.force_enable.discard(3)

        elif event.type == 'V' and event.value == 'PRESS':
            self.clean_mats()
            context.area.header_text_set(text=None)
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            bpy.ops.hops.adjust_viewport('INVOKE_DEFAULT')
            return {'FINISHED'}


        self.draw_master(context=context)

        context.area.tag_redraw()

        return {"RUNNING_MODAL"}

    ####################################################
    #   CURSOR WARP
    ####################################################

    def safe_draw_shader(self, context):
        method_handler(self.draw_shader,
            arguments = (context,),
            identifier = 'UI Framework',
            exit_method = self.remove_shader)


    def remove_shader(self):
        '''Remove shader handle.'''

        if self.draw_handle:
            self.draw_handle = bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle, "WINDOW")


    def draw_shader(self, context):
        '''Draw shader handle.'''

        draw_modal_frame(context)


    # def remove_slot(self):
    #     if self.active.mode == 'EDIT':
    #         bpy.ops.object.editmode_toggle()
    #         bpy.ops.object.material_slot_remove()
    #         bpy.ops.object.editmode_toggle()
            
    def material_scroll(self,  direction =0):
        max_index = len(self.materials) -1
        dup_filter =set()
        for obj, slot_data in self.obj_slots.items():
            
            allowed = set( range( len(obj.material_slots) ) )
            if self.slot_mode == 'ACTIVE':
                allowed = {obj.active_material_index}
                allowed.update(self.force_enable)
            elif self.slot_mode == "NOT ACTIVE" :
                allowed.discard (obj.active_material_index)

            for index , slot in enumerate(obj.material_slots):
               
                if index not in allowed:
                    continue
                if self.scroll_mode == 'DESTRUCTIVE':
                    if slot.material:
                        if slot.material.name not in dup_filter:
                            dup_filter.add (slot.material.name)
                        else:
                            continue
                        self.random_mat(slot.material)
                    else:
                        self.random_mat()
                        slot_data[index] = len(self.materials) -1
                        slot.material = bpy.data.materials[self.materials[-1]]
                    continue

                if self.scroll_mode == 'BLANK' and (slot_data[index]+direction>max_index):# direction ==1:
                    self.random_mat()
                    slot_data[index] = len(self.materials) -1
                    slot.material = bpy.data.materials[self.materials[-1]]
                    continue

                scroll = slot_data[index] +direction
                scroll = 0 if scroll > max_index else scroll
                scroll = max_index if scroll<0  else scroll
                slot_data[index] = scroll
                slot.material = bpy.data.materials[self.materials[scroll]]


    def randomize_mats(self):
        max_index = len(self.materials) -1
        for obj, slot_data in self.obj_slots.items():

            allowed = set( range( len(obj.material_slots) ) )
            if self.slot_mode == 'ACTIVE':
                allowed = {obj.active_material_index}
                allowed.update(self.force_enable)
            elif self.slot_mode == "NOT ACTIVE" :
                allowed.discard (obj.active_material_index)

            for index , slot in enumerate(obj.material_slots):
                if index not in allowed:
                    continue
                mat_index = random.randint(0, max_index)
                slot_data[index] = mat_index
                slot.material = bpy.data.materials[ self.materials[mat_index] ]
  

    def clean_mats(self):

        for mat_name  in self.created_mats:
            material = bpy.data.materials[mat_name]
            if not material.users:
                bpy.data.materials.remove(material )
                
            del material
        del self.slot_backup 
        del self.created_mats 
        del self.created_slots 
        del self.materials
        del self.data_index_back
        del self.objects


    def restore_slots(self):
        
        for obj in self.objects:
            back_list = self.slot_backup [obj]
            for slot, mat_name in zip(obj.material_slots , back_list ):
                slot.material = bpy.data.materials[mat_name] if mat_name else None

        if self.data_index_back:
            for obj, index_list in self.data_index_back.items():
                for poly , index in zip (obj.data.polygons , index_list):
                    poly.material_index = index
        
        for obj in self.created_slots:
            obj.data.materials.pop()


    def draw_master(self, context):

        # Start
        self.master.setup()

        ########################
        #   Fast UI
        ########################

        if self.master.should_build_fast_ui():
            
            win_list = []
            help_list = []
            mods_list =  list(reversed([(i+1, mat.name) for i, mat in enumerate(self.active.material_slots)]))
            active_mod = self.active.active_material_index +1
            active_slot = F"{active_mod}/{len(self.active.material_slots)}"
            force_enabld = ''
            if not len (self.force_enable):
                force_enabld = None 
            else:
                force_enabld = sorted([e+1 for e in self.force_enable])
            
            #Main
            if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1: #Fast Floating
                win_list.append(len(self.materials))
                if self.scroll_mode != 'NORMAL':
                    win_list.append(self.material_type)
                else:
                    win_list.append(self.scroll_mode)
                win_list.append(F'{self.slot_mode} : {active_slot}')
                win_list.append(force_enabld)
            else:
                win_list.append(F'Materials: {len(self.materials)}')
                win_list.append(self.scroll_mode)
                if self.scroll_mode != 'NORMAL':
                    win_list.append(F"Type : {self.material_type} ")
                    if self.material_type == 'PRINCIPLED':
                        msg = "ON" if self.enable_color else "OFF"
                        win_list.append(F"Color :{msg} ")

                win_list.append(F"Slots: {self.slot_mode}")
                win_list.append(F"Active Slot: {active_slot}")
                if self.slot_mode != 'ALL': 
                    win_list.append(F"Force Enabled: {force_enabld}" )

                #win_list.append(f"{self.index}")
             #   win_list.append(f"{self.materials[self.index].name}")

            # Help
            help_list.append(["Shift+Scroll / Z / X", "Increment Active Slot"])
            help_list.append(["Scroll", "Increment Material"])
            help_list.append(["Z / X",  "Increment Material"])
            help_list.append(["V",      "Viewport Scroll Exit"])
            help_list.append(["A",      "Toggle affected slots"])
            help_list.append(["R",      "Randomize ALL"])
            help_list.append(["C",      "Toggle Color"])
            if self.slot_mode == 'ACTIVE': 
               help_list.append(["1-4", "Force Enable Slots"])
            help_list.append(["D",      "Toggle Non-Destructive Blank Scroll"])
            help_list.append(["B",      "Toggle Blank Material Scroll"])
            help_list.append(["T",      "Cycle Blank Material Type"])
            help_list.append(["M",      "Toggle material list."])
            help_list.append(["H",      "Toggle help."])
            help_list.append(["~",      "Toggle viewport displays."])
            help_list.append(["O",      "Toggle viewport rendering"])

            # Mods
            # active_mod = ""
            # filepathprefs = bpy.context.preferences.filepaths
            # for material in [mat for mat in bpy.data.materials if not mat.name.startswith('.')] if filepathprefs.show_hidden_files_datablocks else bpy.data.materials:
            #     if self.materials[self.index] == material:
            #         active_mod = self.materials[self.index].name
            #     mods_list.append([material.name_full, ""])

            self.master.receive_fast_ui(
                win_list=win_list,
                help_list=help_list,
                image="InteractiveBoolean",
                mods_list=mods_list,
                active_mod_name=active_mod,
                mods_label_text="Materials",
                number_mods=False)

        # Finished
        self.master.finished()


    def random_mat(self , material = None):
        color = 1 if self.enable_color else 0
        if self.material_type == 'PRINCIPLED':
            new_mat = random_principled(material=material, color_prob=color,  copy_view = self.copy_view)
        elif self.material_type == 'CARPAINT':
            new_mat = random_carpaint(material=material, copy_view = self.copy_view)
        elif self.material_type == 'EMISSION':
            new_mat = random_emit(material=material, copy_view = self.copy_view)
        #new_mat.node_tree.nodes.update()
        if self.scroll_mode != 'DESTRUCTIVE':
            self.created_mats.add(new_mat.name)
            self.materials.append(new_mat.name)


def random_principled (material = None,  name = 'Material', metal_prob = 0.8, rough_min = 0.01, 
    rough_max = 0.4, color_prob = 0.2, clear_prob = 0.2, 
    val_min = 0.1, val_max =0.8, copy_view = False ):

    material, principled = add_pricipled(material=material)
            
    metal = 1 if roll(metal_prob) else 0
    clearcoat = 1 if roll(clear_prob) else 0
    clearcoat_rough = random.uniform(rough_min, rough_max) if clearcoat else 0
    roughness = random.uniform(rough_min, rough_max)
    roll_color = roll (color_prob)
    
    if roll_color:
        color = random_color (col_min = 0.1, col_max = 0.7)
    
    else:
        color = random_color (color= False, grey_min = 0.1, grey_max= 0.4 ) 

    #viewport
    if copy_view:
        material.diffuse_color = color
        material.metallic = metal
        material.roughness = roughness
    else:
        material.diffuse_color = random_color()

    principled.inputs['Base Color'].default_value = color
    principled.inputs['Metallic'].default_value = metal
    principled.inputs['Roughness'].default_value = roughness
    principled.inputs['Clearcoat'].default_value = clearcoat
    principled.inputs['Clearcoat Roughness'].default_value = clearcoat_rough

    return material


def random_carpaint(material = None,  name = 'Carpaint', metal_prob = 0.8, rough_min = 0.01, 
    rough_max = 0.4, color_prob = 1, clear_prob = 0.2,  copy_view = False):

    material, carpaint_shader = carpaint_material(material = material)

    metal = 1 if roll(metal_prob) else 0
    clearcoat = 1 if roll(clear_prob) else 0
    clearcoat_rough = random.uniform(rough_min, rough_max) if clearcoat else 0
    roughness = random.uniform(rough_min, rough_max)
    color = random_color ()

    #viewport
    if copy_view:
        material.diffuse_color = color
        material.metallic = metal
        material.roughness = roughness
    else:
        material.diffuse_color = random_color()

    
    carpaint_shader.inputs["Hue Variation"].default_value = random.uniform(0,1)
    carpaint_shader.inputs["Hue Shift Base Value"].default_value = 0.5
    carpaint_shader.inputs["Saturation Variation"].default_value = random.uniform(0,1)
    carpaint_shader.inputs["Saturation Base Value"].default_value = 1.0
    carpaint_shader.inputs["Brightness Variation"].default_value = random.uniform(0,1)
    carpaint_shader.inputs["Brightness Value"].default_value = random.uniform(0,1)
    carpaint_shader.inputs["Metallic"].default_value = random.randint(0,1)
    carpaint_shader.inputs["Flake Roughness Minimum"].default_value = 0.23999999463558197
    carpaint_shader.inputs["Flake Roughness Maximum"].default_value = 0.8799999952316284
    carpaint_shader.inputs["Flake Scale"].default_value = 4000.0
    carpaint_shader.inputs["Clearcoat"].default_value = clearcoat
    carpaint_shader.inputs["Clearcoat Roughness"].default_value = clearcoat_rough
    carpaint_shader.inputs["Randomness"].default_value = 0.0
    return material


def random_emit(material = None, name = 'Emission', pulse = True ,
    cycle_count = 4, copy_view = False):
    material, emission_glow = emission_glow_material(material=material)

    cycle_count = cycle_count if pulse else 0
    
    col = Color()
    h = random.uniform(0,1)
    s = random.uniform(0,1)
    v = 1
    col.hsv = (h,s,v)
    color1 =[col.r, col.g, col.b, 1]
    emit_multi = random.uniform(1, 10)

    #viewport
    if copy_view:
        material.diffuse_color = color1
        material.metallic = 0
        material.roughness = 0
    else:
        material.diffuse_color = random_color()

    emission_glow.inputs["Cycle Count"].default_value = cycle_count
    emission_glow.inputs["Transition Sharp"].default_value = 1.0
    emission_glow.inputs["Emit Multiplier"].default_value = emit_multi
    emission_glow.inputs["Color1"].default_value = color1
    emission_glow.inputs["Color2"].default_value = [0.0, 0.0, 0.0, 1.0]
    emission_glow.inputs["Func Offset (deg)"].default_value = 0.0
    emission_glow.inputs["Emit Offset"].default_value = 0.0
    emission_glow.inputs["Color Blend"].default_value = 0.0
    
    return material


def add_pricipled (material = None, name = "Material"):
    if not material:
        material = bpy.data.materials.new (name)
    material.use_nodes = True
    material_nodes = material.node_tree.nodes
    material_nodes.clear()
    output = material_nodes.new(type="ShaderNodeOutputMaterial")
    principled = material_nodes.new("ShaderNodeBsdfPrincipled")
    material.node_tree.links.new(principled.outputs[0], output.inputs[0])
    principled.location = [-300, output.location[1]] 
    return (material, principled)


def roll (chance):
    return random.uniform(0,1) <=chance


def random_color(color = True, col_min = 0.1, col_max = 0.8, grey_min = 0.1 , grey_max = 0.4):
    if color :
        r = random.uniform(col_min, col_max)
        g = random.uniform(col_min, col_max)
        b = random.uniform(col_min, col_max)

    else:
        r = g = b  = random.uniform (grey_min, grey_max)
    
    return [r , g, b, 1]