import bpy, os, json
from pathlib import Path
from . pizza_ops_data import get_pizza_ops_data
from ... icons import icons_directory
from ... utils.addons import addon_exists
from ... ui_framework.master import Master
from ... preferences import get_preferences
from ... utility.base_modal_controls import Base_Modal_Controls


class HOPS_OT_Pizza_Ops_Window(bpy.types.Operator):
    """Pizza Ops Window"""
    bl_idname = "hops.pizza_ops_window"
    bl_label = "Pizza Ops Window"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = """Pizza Ops V2
    
    The ultimate pizza ordering popup.
    
    Add locations or images here!
    \HOps\operators\misc\pizza_ops_data\

    """


    def invoke(self, context, event):
        
        self.preference = get_preferences()
        self.pizza_data = get_pizza_ops_data()

        if self.pizza_data == {} or self.pizza_data == None:
            return {'FINISHED'}
        
        # Base Systems
        self.master = Master(context=context, custom_preset="pizza_ops", show_fast_ui=False)
        self.base_controls = Base_Modal_Controls(context, event)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


    def modal(self, context, event):

        #######################
        #   Base Systems
        #######################
        self.master.receive_event(event=event)
        self.base_controls.update(context, event)

        #######################
        #   Base Controls
        #######################
        if self.base_controls.pass_through:
            if not self.master.is_mouse_over_ui():
                return {'PASS_THROUGH'}
        elif self.base_controls.cancel:
            if not self.master.is_mouse_over_ui():
                self.remove_images()
                self.master.run_fade()
                return {'CANCELLED'}
        elif self.base_controls.confirm:
            if not self.master.is_mouse_over_ui():
                self.remove_images()
                self.master.run_fade()
                return {'FINISHED'}

        self.draw_window(context=context)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}


    def draw_window(self, context):

        self.master.setup()
        self.master.receive_main(win_dict=self.pizza_data)
        self.master.finished()


    def remove_images(self):
        '''Remove the images.'''

        if self.pizza_data != {}:
            if self.pizza_data != None:
                for key, val in self.pizza_data.items():
                    if "icon" in val:
                        image = val["icon"]

                        if image != None:
                            try:
                                bpy.data.images.remove(image)
                            except:
                                pass


