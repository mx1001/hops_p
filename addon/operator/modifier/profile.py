import bpy, bpy_extras, pathlib
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper, ExportHelper
from pathlib import Path
from bpy.props import StringProperty, BoolProperty
from ...utility.addon import preference
from ...utility.profile import save_bevel_profile, load_bevel_profile


class SaveBevelProfile(Operator, ExportHelper):
    bl_idname = 'hops.save_bevel_profile'
    bl_label = 'Save Bevel Profile'
    bl_options = {'REGISTER', 'INTERNAL'}
    bl_description = 'Save custom bevel profile to a json file'


    filter_glob: StringProperty(default='*.json', options={'HIDDEN'})
    filename_ext: bpy.props.StringProperty(default='.json', options={'HIDDEN'})
    obj: StringProperty(name='Object Name', options={'HIDDEN'})
    mod: StringProperty(name='Modifier Name', options={'HIDDEN'})


    def invoke(self, context, event):
        folder = Path(preference().property.profile_folder).resolve()

        try:
            folder.mkdir(parents=True, exist_ok=True)
        except:
            print(f'Unable to create {folder}')

        self.filepath = str(folder.joinpath('bevel.json'))
        return super().invoke(context, event)


    def execute(self, context):
        obj = bpy.data.objects[self.obj]
        mod = obj.modifiers[self.mod]
        result = save_bevel_profile(mod, self.filepath)
        self.report(result[0], result[1])
        return result[2]


class LoadBevelProfile(Operator, ImportHelper):
    bl_idname = 'hops.load_bevel_profile'
    bl_label = 'Load Bevel Profile'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    bl_description = 'LMB - Load custom bevel profile from a json file'


    filter_glob: StringProperty(default='*.json', options={'HIDDEN'})
    obj: StringProperty(name='Object Name', options={'HIDDEN'})
    mod: StringProperty(name='Modifier Name', options={'HIDDEN'})
    sync_segments: BoolProperty(name='Sync Segments', description = 'Set segment count to number of profile points')


    def invoke(self, context, event):
        folder = Path(preference().property.profile_folder).resolve()

        try:
            folder.mkdir(parents=True, exist_ok=True)
        except:
            print(f'Unable to create {folder}')

        self.filepath = str(folder.joinpath('bevel.json'))
        return super().invoke(context, event)


    def execute(self, context):
        obj = bpy.data.objects[self.obj]
        mod = obj.modifiers[self.mod]
        result = load_bevel_profile(mod, self.filepath, self.sync_segments)
        self.report(result[0], result[1])
        return result[2]
