import bpy
import time
import sys
import traceback
from . graphics.shader import Shader
from . graphics.load import load_image_file
from . database import DB
from . api.create import Create
from . events.event import Event_System
from . presets.preset_a import Preset_A
from . presets.preset_b import Preset_B
from . presets.preset_kit_ops import Preset_Kit_Ops


class Modal_Communications():

    last_created_unique_id = None
    id_offset = 0
    modals = {}


class Modal_Bridge():

    def __init__(self):

        self.master_ref = None
        self.unique_id = None
        self.modal_detached = False
        self.last_receive_time = None
        self.ui_modal_context = None


class Master():

    def __init__(self, context, custom_preset="", show_fast_ui=True):

        # Start the UI modal
        self.unique_id = None
        self.__launch_modal()

        # Persistent data
        self.context = context
        self.db = DB()
        self.preset = None

        # Overrides
        self.only_use_fast_ui = False # Prevents expanded mode
        self.show_fast_ui = show_fast_ui # Only show the expanded

        # Event
        self.event_sys = Event_System(db=self.db)

        # Graphics
        self.shader = Shader(context=Modal_Communications.modals[self.unique_id].ui_modal_context, db=self.db)

        # API
        self.create = Create(db=self.db)

        # Init setup
        self.custom_preset = custom_preset
        self.__get_preset()

        # Setup Modal_Communications
        self.__setup_modal_com()


    def __launch_modal(self):

        Modal_Communications.last_created_unique_id = time.time() + Modal_Communications.id_offset
        Modal_Communications.id_offset += 1
        if Modal_Communications.id_offset > 10:
            Modal_Communications.id_offset = 0
        self.unique_id = Modal_Communications.last_created_unique_id
        
        modal_bridge = Modal_Bridge()
        modal_bridge.last_receive_time = time.time()
        modal_bridge.modal_detached = False
        modal_bridge.unique_id = self.unique_id

        Modal_Communications.modals[self.unique_id] = modal_bridge

        bpy.ops.hops.modal_ui_draw('INVOKE_DEFAULT')


    def __get_preset(self):

        # This is to check for scale updates while modal is running
        self.scale = self.db.prefs.ui.Hops_modal_size

        # Custom Presets
        if self.custom_preset != "":
            if self.custom_preset == "preset_kit_ops":
                self.preset = Preset_Kit_Ops(create=self.create)
                self.db.fast_ui.show = self.show_fast_ui
                return

        # Prefs Presets
        preset = self.db.prefs.ui.Hops_modal_presets

        if preset == "preset_A":
            self.preset = Preset_A(create=self.create)
            
        elif preset == "preset_B":
            self.preset = Preset_B(create=self.create)


    def __setup_modal_com(self):

        Modal_Communications.modals[self.unique_id].master_ref = self


    def setup(self):
        '''Clears the layouts on all the windows.'''

        if self.scale != self.db.prefs.ui.Hops_modal_size:
            self.scale = self.db.prefs.ui.Hops_modal_size
            self.__get_preset()

        if self.only_use_fast_ui == False:
            if self.db.event.tab_pressed:
                self.db.fast_ui.show = False

        self.db.clear_db()
        self.create.cell_index = 0


    def receive_event(self, event):
        '''Update the event data in the database.'''

        self.event_sys.update_event_data(event=event, context=self.context)
        try:
            if self.unique_id in Modal_Communications.modals:
                Modal_Communications.modals[self.unique_id].last_receive_time = time.time()
        except:
            pass

    # Fast UI
    def receive_fast_ui(self, win_list=[], help_list=[], image="", mods_list=[], active_mod_name="", mods_label_text="Press M", number_mods=True):
        '''Receive the main window dictionary.\n
           Image is any image file name from the icons folder, without the extension.'''

        if self.db.fast_ui.show == True:
            self.db.fast_ui.build_main(
                win_list=win_list, 
                help_list=help_list, 
                image=image, 
                mods_list=mods_list, 
                active_mod_name=active_mod_name, 
                mods_label_text=mods_label_text,
                number_mods=number_mods)


    def should_build_fast_ui(self):
        '''Use this to determine if you should build the fast ui or the main ui.'''

        # Override
        if self.only_use_fast_ui == True:
            return True

        if self.db.fast_ui.show:
            return True

        return False


    def receive_main(self, win_dict={}, window_name="MAIN"):
        '''Receive the main window dictionary.'''

        if self.preset != None:
            self.preset.build_main(win_dict=win_dict, window_name=window_name)


    def receive_help(self, hot_keys_dict={}, quick_ops_dict={}):
        '''Receive the help window dictionary.'''

        if self.preset != None:
            self.preset.build_help(hot_keys_dict=hot_keys_dict, quick_ops_dict=quick_ops_dict)


    def receive_mod(self, win_dict={}, active_mod_name=""):
        '''Receive the mod window dictionary.'''

        if self.preset != None:
            self.preset.build_mods(win_dict=win_dict, active_mod_name=active_mod_name)


    def finished(self):
        '''Run the event layer.'''

        if self.db.fast_ui.show == False:
            self.event_sys.run()


    def is_mouse_over_ui(self):
        '''For modal exit.'''

        if self.db.fast_ui.show:
            return False

        elif self.db.ui_event.active_window_key == "":
            return False

        else:
            return True


    def destroy(self):
        '''Remove the shader and graphics data.'''
            
        self.shader.remove_handle()


    def completed(self):

        if self.db.colors.fade_completed == True:
            if self.preset != None:
                self.preset.destroy()

        return self.db.colors.fade_completed


    def run_fade(self):

        try:
            if self.unique_id in Modal_Communications.modals:
                self.shader.db = Modal_Communications.modals[self.unique_id].master_ref.db
                Modal_Communications.modals[self.unique_id].modal_detached = True
            else:
                self.shader.destroy()
        except:
            self.shader.destroy()


class HOPS_MODAL_UI_Draw(bpy.types.Operator):

    bl_idname = "hops.modal_ui_draw"
    bl_label = "Drawing for modals"
    bl_options = {"INTERNAL"}
    
    def __init__(self):

        self.unique_id = None


    def invoke(self, context, event):

        self.unique_id = Modal_Communications.last_created_unique_id
        Modal_Communications.modals[self.unique_id].ui_modal_context = context

        self.timer = context.window_manager.event_timer_add(0.025, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


    def modal(self, context, event):

        should_exit = self.fail_safe()
        if should_exit:
            return {'FINISHED'}

        # Start fading out
        try:
            if self.unique_id in Modal_Communications.modals:
                if Modal_Communications.modals[self.unique_id].modal_detached == True:
                    Modal_Communications.modals[self.unique_id].master_ref.shader.remove_handle()
            else:
                bpy.context.window_manager.event_timer_remove(self.timer)
                return {'FINISHED'}
        except:
            bpy.context.window_manager.event_timer_remove(self.timer)
            return {'FINISHED'}

        # Check if fade out is finished
        try:
            if self.unique_id in Modal_Communications.modals:
                if Modal_Communications.modals[self.unique_id].master_ref.completed():
                    Modal_Communications.modals.pop(self.unique_id)
                    bpy.context.window_manager.event_timer_remove(self.timer)
                    return {'FINISHED'}
        except:
            bpy.context.window_manager.event_timer_remove(self.timer)
            return {'FINISHED'}


        try:
            context.area.tag_redraw()
        except:
            bpy.context.window_manager.event_timer_remove(self.timer)
            return {'FINISHED'}

        return {'PASS_THROUGH'}

    
    def fail_safe(self):

        # Delete because a new modal was created ahead of this
        if Modal_Communications.last_created_unique_id != self.unique_id:
            Modal_Communications.modals[self.unique_id].master_ref.shader.destroy()
            Modal_Communications.modals.pop(self.unique_id)
            bpy.context.window_manager.event_timer_remove(self.timer)
            return True    

        try:
            # Modal stopped sending events and timed out
            if Modal_Communications.modals[self.unique_id].last_receive_time != None:
                if time.time() - Modal_Communications.modals[self.unique_id].last_receive_time > 5:
                    Modal_Communications.modals[self.unique_id].master_ref.shader.destroy()
                    Modal_Communications.modals.pop(self.unique_id)
                    bpy.context.window_manager.event_timer_remove(self.timer)
                    return True

        except:
            pass

        return False