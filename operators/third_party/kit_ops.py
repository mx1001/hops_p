import os
import bpy
from pathlib import Path
from bpy_extras.image_utils import load_image
from ...preferences import get_preferences
from ...ui_framework.master import Master
from ...utils.addons import addon_exists
from ... icons import icons_directory


def load_image_file(filename="", directory=""):
    '''Return the loaded image.'''

    return load_image(filename + ".png", dirname=directory)


class HOPS_OT_Kit_Ops_Window(bpy.types.Operator):

    """Kit Ops Window"""
    bl_idname = "hops.kit_ops_window"
    bl_label = "Kit Ops Window"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = """Kit Ops Window"""


    def invoke(self, context, event):

        # Keep track of original object
        self.obj = context.active_object

        # Asset loaded
        self.exit_modal = False

        # Kit ops
        self.option = None  
        self.folders = None
        self.images = {}

        # Enter mode
        self.stay_mode = True if event.shift else False

        # Decal
        self.build_collection = True
        self.collections = {}
        self.active_pack = ""

        # Get asset loader options
        self.asset_opts = []
        if addon_exists("kitops" or "kitops_free"):
            self.asset_opts.append('KO')
        if addon_exists("DECALmachine"):
            self.asset_opts.append('DM')
        if addon_exists("PowerLink"):
            self.asset_opts.append('PL')
            try:
                bpy.ops.powerlink.refresh_blend_file_list('INVOKE_DEFAULT')
            except:
                pass

        # No addons where found : EXIT
        if self.asset_opts == []:
            return {'FINISHED'}

        # Check that window loads into exsisting addon
        prefs = get_preferences()
        if prefs.ui.Hops_asset_loader_window not in self.asset_opts:
            if len(self.asset_opts) > 0:
                prefs.ui.Hops_asset_loader_window = self.asset_opts[0]

        # UI / Run modal
        self.master = Master(context=context, custom_preset="preset_kit_ops", show_fast_ui=False)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


    def modal(self, context, event):

        # UI Update
        self.master.receive_event(event=event)

        # Navigation
        if (event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} and event.ctrl != True):

            if not self.master.is_mouse_over_ui():
                return {'PASS_THROUGH'}

        # Confirm
        elif (event.type == 'LEFTMOUSE') and self.stay_mode == False:
            if not self.master.is_mouse_over_ui():
                self.master.run_fade()
                self.remove_images()
                return {'FINISHED'}

        # Cancel
        elif (event.type in {'RIGHTMOUSE', 'ESC'}):
            if not self.master.is_mouse_over_ui():
                self.master.run_fade()
                self.remove_images()
                return {'CANCELLED'}

        elif event.type == 'S':
            bpy.ops.transform.resize('INVOKE_DEFAULT')

        elif event.type == 'R':
            bpy.ops.transform.rotate('INVOKE_DEFAULT')

        elif event.type == 'G':
            bpy.ops.transform.translate('INVOKE_DEFAULT')

        # Exit after load
        if self.exit_modal:
            self.master.run_fade()
            self.remove_images()
            return {'FINISHED'}

        self.draw_window(context, event)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}


    def draw_window(self, context, event):

        self.master.setup()
        prefs = get_preferences()

        window_name = ""
        main_window = {
            "folders" : [],
            "files"   : [],
            "images"  : []}

        # Build Kit-Ops Window
        if prefs.ui.Hops_asset_loader_window == 'KO':

            if addon_exists("kitops" or "kitops_free"):
                
                window_name = "KIT-OPS"

                # Get Version
                from kitops import bl_info
                if bl_info['version'][0] > 1:
                    window_name += ' 2'
                else:
                    window_name += ' 1'

                from kitops.addon.utility import addon
                self.option = addon.option()

                # Folders
                for category in enumerate(self.option.kpack.categories):

                    highlight = False
                    active_kpack = self.option.kpack.categories[self.option.kpack.active_index].folder
                    if category[1].folder == active_kpack:
                        highlight = True

                    main_window["folders"].append([category[1].name, self.ko_set_kpack, (category[0],), highlight])

                # Files
                if len(self.option.kpack.categories):
                    category = self.option.kpack.categories[self.option.kpack.active_index]
                    blends = category.blends

                    for blend in reversed(blends):
                        main_window["files"].append([blend.name])

                # Images
                if len(self.option.kpack.categories):
                    category = self.option.kpack.categories[self.option.kpack.active_index]
                    blends = category.blends

                    for blend in reversed(blends):
                        image = self.ko_get_image(blend)
                        if event.ctrl == True and hasattr(bpy.ops.ko, 'add_insert_material'):
                            main_window["images"].append([image, self.ko_call_insert_linked_mat, (blend.location,)])
                        else:
                            main_window["images"].append([image, self.ko_call_insert, (blend.location,)])

        # Build Decal Machine Window
        elif prefs.ui.Hops_asset_loader_window == 'DM':
            window_name = "DECALmachine"

            from DECALmachine.utils.registration import get_prefs

            prefs = get_prefs()
            assets_path = prefs.assetspath
            decal_libs = prefs.decallibsCOL

            # Build collections data
            if self.build_collection:
                self.build_collection = False
                for col in decal_libs:
                    self.collections[col.name] = self.dm_get_image_data(assets_path, col.name)

                    for item in reversed(self.collections[col.name]):
                        main_window["files"].append( [item[1]] )

            # Add collection
            for key, val in self.collections.items():

                # Set initial pack
                if self.active_pack == "":
                    self.active_pack = key

                # Highlight the active pack
                highlight = False
                if key == self.active_pack:
                    highlight = True

                main_window["folders"].append([key, self.dm_set_active_pack, (key,), highlight])

                if key == self.active_pack:
                    for items in reversed(val):
                        image = items[1]
                        if image != None:

                            path = Path(image.filepath)
                            decal_dir = path.parts[-2]

                            main_window["images"].append( [image, self.dm_call_decal_insert, (key, decal_dir)] )
                            main_window["files"].append( [decal_dir] )
                            
                main_window["folders"].sort()
                main_window["folders"].reverse()

        # Build Power Link Window
        elif prefs.ui.Hops_asset_loader_window == 'PL':
            from PowerLink.addon.utils.common import prefs
            window_name = "PowerLink"
            pl_prefs = prefs()

            for index, item in enumerate(pl_prefs.blend_file_items):
                highlight = False
                if index == pl_prefs.blend_file_index:
                    highlight = True
                main_window["folders"].append([item.name, self.pl_set_active_index, (index,), highlight])
            #main_window["folders"].reverse()

            # Special key for powerlink : check preset (kit_ops)
            main_window['powerlink'] = []

            # Collections
            for index, item in enumerate(pl_prefs.collection_items):
                main_window['powerlink'].append([item.name, self.pl_load_collection, (index, )])


        main_window["function_call_back_for_tab"] = [self.toggle_asset_loader, (context, )]
        self.master.receive_main(win_dict=main_window, window_name=window_name)
        self.master.finished()

    ##################################
    #   KIT OPS
    ##################################

    def ko_get_image(self, blend):

        if blend in self.images:
            return self.images[blend]

        else:
            folder = os.path.dirname(blend.location)
            image_directory = os.path.splitext(blend.location)[0]
            image_name = os.path.basename(image_directory)
            image = load_image_file(filename=image_name, directory=folder)

            if image != None:
                if bpy.app.version[1] < 83:
                    image.colorspace_settings.name = 'Linear'
                else:
                    image.colorspace_settings.name = 'sRGB'

            if image == None:
                image = load_image_file(filename="Insert", directory=icons_directory)

            self.images[blend] = image

            return image


    def ko_set_kpack(self, index):

        if self.option != None:
            self.option.kpack.active_index = index


    def ko_call_insert(self, location):

        if self.stay_mode == False:
            self.exit_modal = True
        bpy.ops.ko.add_insert('INVOKE_DEFAULT', location=location)


    def ko_call_insert_linked_mat(self, location):

        if self.stay_mode == False:
            self.exit_modal = True
        bpy.ops.ko.add_insert_material('INVOKE_DEFAULT', location=location, material=True, material_link=True)

    ##################################
    #   DECAL MACHINE
    ##################################

    def dm_get_image_data(self, assets_path="", col_name=""):

        directory = os.path.join(assets_path, col_name)
        paths = []
        
        with os.scandir(directory) as it:
            for entry in it:
                if not entry.name.startswith('.'):

                    image_folder =  os.path.join(directory, entry.name)
                    image = self.dm_get_image(image_folder, image_name="decal")

                    image_directory = os.path.join(directory, entry.name, "decal")

                    paths.append((image_directory, image))

        return paths


    def dm_get_image(self, image_folder, image_name):

        image = load_image_file(filename=image_name, directory=image_folder)

        if image != None:

            if bpy.app.version[1] < 83:
                image.colorspace_settings.name = 'Linear'
            else:
                image.colorspace_settings.name = 'sRGB'

        if image == None:
            image = load_image_file(filename="Insert", directory=icons_directory)

        return image


    def dm_set_active_pack(self, pack):

        if pack in self.collections:
            self.active_pack = pack


    def dm_call_decal_insert(self, library_name, decal_name):

        if self.stay_mode == False:
            self.exit_modal = True

        bpy.ops.machin3.insert_decal('INVOKE_DEFAULT', library=library_name, decal=decal_name, force_cursor_align=True)

    ##################################
    #   Power Link
    ##################################

    def pl_set_active_index(self, index):
        '''Sets the power link active index to this file.'''

        from PowerLink.addon.utils.common import prefs
        pl_prefs = prefs()
        pl_prefs.blend_file_index = index


    def pl_load_collection(self, collection_index=0):
        '''Set the powerlink index and call the operator to load it.'''

        if self.stay_mode == False:
            self.exit_modal = True

        from PowerLink.addon.utils.common import prefs
        pl_prefs = prefs()
        pl_prefs.collection_index = collection_index

        bpy.ops.hops.powerlink(link=True)

    ##################################
    #   UTILS
    ##################################

    def toggle_asset_loader(self, context):
        '''Toggle the window using the tab'''

        prefs = get_preferences()
        index = self.asset_opts.index(prefs.ui.Hops_asset_loader_window)
        next_asset = self.asset_opts[ (index + 1) % len(self.asset_opts) ]
        prefs.ui.Hops_asset_loader_window = next_asset

        # Set back the original object after switching
        if self.obj != None:
            self.obj.select_set(True)
            context.view_layer.objects.active =self.obj


    def remove_images(self):

        # Unload images : KO
        if self.images != {}:
            for blend, image in self.images.items():
                if image != None:
                    try:
                        bpy.data.images.remove(image)
                    except:
                        pass

        # Unload images : DM
        if self.collections != {}:
            for key, val in self.collections.items():
                for items in val:
                    image = items[1]
                    if image != None:
                        try:
                            bpy.data.images.remove(image)
                        except:
                            pass