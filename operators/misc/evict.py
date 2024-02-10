import bpy
from enum import Enum
from ...utility.collections import link_obj, unlink_obj
from ... preferences import get_preferences
from ...ui_framework.operator_ui import Master
from os import path

class Modes(Enum):
    Unify = 1
    Evict = 2
    Sync = 3
    Collect = 4


class HOPS_OT_EVICT(bpy.types.Operator):
    bl_idname = "hops.evict"
    bl_label = "Evict / Unify Cutters"
    bl_options = {"REGISTER", 'UNDO'}
    bl_description = """Scene/Mod Assistant

LMB - Unify all renderable shapes into collection of active
CTRL - Evict cutters from selection into Cutters 
SHIFT - Sync mod render settings to viewport settings
ALT - Collect all renderable items into a collection

"""

    called_ui = False
    text = 'none'

    def __init__(self):

        HOPS_OT_EVICT.called_ui = False

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        if  self.mode == Modes.Collect:
            self.layout.prop(self, 'collection_name')
            self.layout.prop(self, 'collection_link')
            self.layout.prop(self, 'collect_mode')

    collection_name: bpy.props.StringProperty(
        name="Name", description="Name of the collection to link to", 
        default = '')

    collection_link: bpy.props.BoolProperty(
        name="Link", description="Link new collection into scene", 
        default = False)

    collect_mode: bpy.props.EnumProperty(
        name="Mode", description="What type of objects are selected",
        items = [ ('Rendered', 'Rendered', 'Rendered'), 
        ('Lights','Lights','Lights') 
        ], 
        default = 'Rendered')

    def invoke (self, context, event):

        # Set the operation mode
        self.mode = Modes.Unify
        if event.ctrl == True:
            self.mode = Modes.Evict
        elif event.shift == True:
            self.mode = Modes.Sync
        elif event.alt == True:
            self.mode = Modes.Collect

        return self.execute(context)


    def execute(self, context):

        hops_coll        = "Cutters"
        collections      = context.scene.collection.children
        view_collections = context.view_layer.layer_collection.children

        if self.mode == Modes.Unify and context.active_object:
            shape_count = 0
            shapes = [obj for obj in context.scene.objects if obj.type == 'MESH' and  obj.display_type not in {'WIRE', 'BOUNDS'} and not obj.hide_get() and obj != context.active_object]
            for shape in shapes:
                shape_count += 1
                full_unlink(shape)
                link_to_active(shape, context.active_object)

        elif self.mode == Modes.Evict:
            evicted_cutters = 0
            cutters = [obj for obj in context.selected_objects if (obj.type == 'MESH' and obj.display_type in {'WIRE', 'BOUNDS'}) or (obj.type == 'EMPTY' and not obj.is_instancer)]
            evicted_cutters += len(cutters)
            for cutter in cutters:
                full_unlink( cutter)
                link_obj(context, cutter)
            if hops_coll in view_collections:
                view_collections[hops_coll].hide_viewport = True
            print(F"Cutters evicted:{evicted_cutters}")

        elif self.mode == Modes.Collect:
            
            synced = collect(collect_mode=self.collect_mode, collection_name=self.collection_name, collection_link= self.collection_link)
            

        elif self.mode == Modes.Sync:
            synced = 0
            mesh_objs = [o for o in context.selected_objects if o.type == 'MESH']

            # If mod visible -> Set the rendering visible
            for mesh_obj in mesh_objs:
                for mod in mesh_obj.modifiers:
                    if hasattr(mod, 'show_render'):
                        if hasattr(mod, 'show_viewport'):
                            if mod.show_render != mod.show_viewport:
                                synced += 1
                            mod.show_render = mod.show_viewport

                            # If boolean -> Get boolean and set its render settings
                            if mod.type == 'BOOLEAN':
                                if mod.object != None:
                                    target_obj = mod.object
                                    for mod in target_obj.modifiers:
                                        if hasattr(mod, 'show_render'):
                                            if hasattr(mod, 'show_viewport'):
                                                if mod.show_render != mod.show_viewport:
                                                    synced += 1
                                                mod.show_render = mod.show_viewport         

                            # Setting viewport to rendering settings
                            if mod.type == 'SCREW':
                                if hasattr(mod, 'steps'):
                                    if hasattr(mod, 'render_steps'):
                                        if mod.steps != mod.render_steps:
                                            synced += 1
                                        mod.render_steps = mod.steps

                            elif mod.type == 'SUBSURF':
                                if hasattr(mod, 'levels'):
                                    if hasattr(mod, 'render_levels'):
                                        if mod.levels != mod.render_levels:
                                            synced += 1
                                        mod.render_levels = mod.levels

                            elif mod.type == 'MULTIRES':
                                if hasattr(mod, 'levels'):
                                    if hasattr(mod, 'render_levels'):
                                        if mod.levels != mod.render_levels:
                                            synced += 1
                                        mod.render_levels = mod.levels

        if self.mode == Modes.Unify:
            text = 'Unify'
            substat = shape_count
            info = 'Amount Unified'
        elif self.mode == Modes.Evict:
            text = 'Evict'
            substat = evicted_cutters
            info = 'Amount Evicted'
        elif self.mode == Modes.Sync:
            text = 'Sync'
            substat = synced
            info = "Synced Settings"
        elif self.mode == Modes.Collect:
            text = 'Collect'
            substat = synced
            info = "Renderable Objects Collected"

        # Operator UI
        if not HOPS_OT_EVICT.called_ui:
            HOPS_OT_EVICT.called_ui = True
            ui = Master()
            draw_data = [
                [text],
                [info, substat]]
            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return {"FINISHED"}


def full_unlink (obj):
    for col in list(obj.users_collection):
        col.objects.unlink(obj)

def link_to_active(obj, active ):
    for col in active.users_collection:
        col.objects.link(obj)

def collect_filter(object):
    if object.type not in {'MESH', 'EMPTY', 'FONT', 'CURVE', 'META', 'SURFACE'}:
        return False
    
    if object.type == 'EMPTY' and object.instance_type != 'COLLECTION' and not object.instance_collection:
        return False
    
    if object.display_type not in {'TEXTURED', 'SOLID'}:
        return False
    
    if object.hide_viewport or object.hide_render or object.hide_get():
        return False 
    
    return True 


def collect(collect_mode = 'Rendered', collection_name = '', collection_link = False ):
    if not collection_name:
        collection_name = path.splitext( bpy.path.basename(bpy.data.filepath))[0]

    if collect_mode == 'Rendered':
        objects = list( filter ( collect_filter ,bpy.context.view_layer.objects) )
    
    else:
        objects = [o for o in bpy.context.view_layer.objects if o.type == 'LIGHT' and not (o.hide_viewport or o.hide_render or o.hide_get()) ]       


    if collection_name in bpy.data.collections:
        new_collection = bpy.data.collections[collection_name]

    else:
        new_collection = bpy.data.collections.new(collection_name)

        if collection_link:
            bpy.context.scene.collection.children.link(new_collection)
       
        else:
            new_collection.use_fake_user = True

    for object in objects:
        if new_collection not in object.users_collection and new_collection is not object.instance_collection :
            new_collection.objects.link(object)

    return len(objects)

class HOPS_OT_COLLECT(bpy.types.Operator):
    bl_idname = "hops.collect"
    bl_label = "HOPS COLLECT"
    bl_options = {"REGISTER", 'UNDO'}
    bl_description = """COLLECT Standalone

Utilizes HOPS COLLECT to get all meshes into a collection 
able to be named in the F9 panel.

"""
    called_ui = False
    text = 'none'

    def __init__(self):

        HOPS_OT_COLLECT.called_ui = False

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        self.layout.prop(self, 'collection_name')
        self.layout.prop(self, 'collection_link')
        self.layout.prop(self, 'collect_mode')

    collection_name: bpy.props.StringProperty(
        name="Name", description="Name of the collection to link to", 
        default = '')

    collection_link: bpy.props.BoolProperty(
        name="Link", description="Link new collection into scene", 
        default = False)

    collect_mode: bpy.props.EnumProperty(
        name="Mode", description="What type of objects are selected",
        items = [ ('Rendered', 'Rendered', 'Rendered'), 
        ('Lights','Lights','Lights') 
        ], 
        default = 'Rendered')

    def invoke (self, context, event):

        return self.execute(context)

    def execute(self, context):

        hops_coll        = "Cutters"
        collections      = context.scene.collection.children
        view_collections = context.view_layer.layer_collection.children

        synced = collect(collect_mode=self.collect_mode, collection_name=self.collection_name, collection_link= self.collection_link)
        collect(self.collect_mode, self.collection_name, self.collection_link)
        
        text = 'Collect'
        substat = synced
        info = "Renderable Objects Collected"

        # Operator UI
        if not HOPS_OT_COLLECT.called_ui:
            HOPS_OT_COLLECT.called_ui = True
            ui = Master()
            draw_data = [
                [text],
                [info, substat]]
            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return {"FINISHED"}
