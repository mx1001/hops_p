import bpy, math
from bpy.props import BoolProperty
from math import radians, degrees
from . import infobar
from . adjust_bevel import add_bevel_modifier
from ... preferences import get_preferences
from ... ui_framework.master import Master
from ... utility.base_modal_controls import Base_Modal_Controls

# Cursor Warp imports
from ... utils.toggle_view3d_panels import collapse_3D_view_panels
from ... utils.modal_frame_drawing import draw_modal_frame
from ... utils.cursor_warp import mouse_warp
from ... addon.utility import method_handler


class HOPS_OT_AdjustAutoSmooth(bpy.types.Operator):
    bl_idname = 'hops.adjust_auto_smooth'
    bl_label = 'Adjust Auto Smooth'
    bl_options = {'REGISTER', 'UNDO', 'BLOCKING'}
    bl_description = """Interactive Autosmooth Adjustment

LMB   - Adjust autosmoothing
CTRL  - Start at 60°
SHIFT - Start at 30°
ALT   - Start at 15°

Press H for help"""

    def __init__(self):
        self.master = None

        self.number_to_angle = {
            'ONE': 15,
            'TWO': 20,
            'THREE': 30,
            'FOUR': 45,
            'FIVE': 60,
            'SIX': 75,
            'SEVEN': 90,
            'EIGHT': 180,
        }


    angle: bpy.props.FloatProperty(
        name='Auto Smooth Angle',
        description='The angle at which to automatically sharpen edges',
        default=35,
        min=0,
        max=180,
    )

    flag: BoolProperty(
        name = 'Use Bevel Special Behavior',
        default = False,
        description = 'Ignore Ctrl keypress')

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)


    def invoke(self, context, event):

        bpy.ops.object.shade_smooth()
        self.objects = [o for o in context.selected_objects if o.type == 'MESH']
        self.settings = {o: {} for o in self.objects}

        # if event.ctrl:
        #     self.angle = 60
        # if event.shift:
        #     self.angle = 30
        # if event.alt:
        #     self.angle = 15

        for obj in self.objects:
            self.settings[obj]['use_auto_smooth'] = obj.data.use_auto_smooth
            obj.data.use_auto_smooth = True

            self.settings[obj]['auto_smooth_angle'] = obj.data.auto_smooth_angle
            obj.data.auto_smooth_angle = math.radians(self.angle)

            bevmods = bevels(obj, angle=True)

            if self.flag:
                if bevmods:
                    for mod in bevmods:
                        mod.show_viewport = False

        self.modal_scale = get_preferences().ui.Hops_modal_scale
        self.buffer = self.angle

        # Base Systems
        self.master = Master(context=context)
        self.master.only_use_fast_ui = True
        self.base_controls = Base_Modal_Controls(context, event)
        self.original_tool_shelf, self.original_n_panel = collapse_3D_view_panels()
        self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.safe_draw_shader, (context,), 'WINDOW', 'POST_PIXEL')

        context.area.header_text_set(text=f'Auto Smooth Angle: {self.angle:.1f}')
        context.window_manager.modal_handler_add(self)
        infobar.initiate(self)
        return {'RUNNING_MODAL'}


    def modal(self, context, event):

        # Base Systems
        self.master.receive_event(event=event)
        self.base_controls.update(context, event)
        mouse_warp(context, event)

        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        offset = self.base_controls.mouse * 10

        if event.type == 'MOUSEMOVE':
            self.buffer = min(max(self.buffer + offset, 0), 180)
            self.angle = round(self.buffer, 0 if event.ctrl else 1)
            self.update(context)

        elif event.type == 'Z' and (event.shift or event.alt):
            return {'PASS_THROUGH'}

        elif event.type in {'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT'} and event.value == 'PRESS':
            self.buffer = self.number_to_angle[event.type]
            self.angle = self.number_to_angle[event.type]
            self.update(context)

        elif self.base_controls.scroll:
            self.buffer += 5 * self.base_controls.scroll
            self.angle += 5 * self.base_controls.scroll
            self.update(context)

        elif self.base_controls.cancel:
            self.cancel(context)

            obj = bpy.context.object
            for mod in obj.modifiers:
                if mod.type == 'BEVEL': #and mod.limit_method == 'ANGLE':
                    mod.show_viewport = True

            context.area.header_text_set(text=None)
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            infobar.remove(self)
            return {'CANCELLED'}

        elif self.base_controls.confirm:
            obj = bpy.context.object

            if self.flag :
                for mod in obj.modifiers:
                    if mod.type == 'BEVEL': # and mod.limit_method == 'ANGLE':
                        mod.show_viewport = True
                self.angle = 60
                self.buffer = 60
                bpy.context.object.data.auto_smooth_angle = radians(60)
                self.flag = False
            else:
                for mod in obj.modifiers:
                    if mod.type == 'BEVEL': #and mod.limit_method == 'ANGLE':
                        mod.show_viewport = True
            context.area.header_text_set(text=None)
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            infobar.remove(self)
            return {'FINISHED'}

        elif event.type == 'G' and event.value == 'PRESS':
            bpy.context.object.hops.is_global = not bpy.context.object.hops.is_global

        elif event.type == 'B' and event.value == 'PRESS':
            obj = bpy.context.object

            for mod in obj.modifiers:
                if mod.type == 'BEVEL': #and mod.limit_method == 'ANGLE':
                    mod.show_viewport = not mod.show_viewport

        elif event.type == "A" and event.value == "PRESS" and not event.shift and not event.alt:
            mod = None
            obj = bpy.context.object

            bevmods = bevels(obj, angle=True)

            if bevmods:
                for mod in bevmods:
                    mod.show_viewport = True
                    mod.angle_limit = radians(self.angle)

                    self.report({'INFO'}, F'AngleFound')
                    self.update(context)
                #_____________
                self.angle = 60
                self.buffer = 60
                context.area.header_text_set(text=None)
                self.finished = True
                self.remove_shader()
                collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
                self.master.run_fade()
                bpy.ops.hops.adjust_bevel('INVOKE_DEFAULT')
                return {"FINISHED"}
            else:
                context.area.header_text_set(text=None)
                self.finished = True
                self.remove_shader()
                collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
                self.master.run_fade()
                #_____________
                #mod.show_viewport = True
                if not bevmods:
                    add_bevel_modifier(context, obj, radians(self.angle))
                bpy.ops.hops.adjust_bevel('INVOKE_DEFAULT')
                bpy.context.object.data.auto_smooth_angle = radians(60)
                self.report({'INFO'}, F'Bevel Added')
                return {"FINISHED"}
            self.update(context)

        elif event.type == "A" and event.value == "PRESS" and event.shift:
            bpy.context.object.data.use_auto_smooth = not bpy.context.object.data.use_auto_smooth
            self.report({'INFO'}, F'Autosmooth {bpy.context.object.data.use_auto_smooth}')

        elif event.type == 'S' and event.value == 'PRESS':
            bpy.ops.hops.sharpen(behavior='SSHARP', mode='SSHARP', additive_mode=True, auto_smooth_angle=radians(self.angle), is_global=bpy.context.object.hops.is_global)
            self.report({'INFO'}, F'Sharpen - Exit')
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            infobar.remove(self)
            return {'FINISHED'}

        elif event.type == 'R' and event.value == 'PRESS':
            bpy.ops.hops.sharpen(behavior='RESHARP', mode='SSHARP', additive_mode=False, auto_smooth_angle=radians(self.angle), is_global=bpy.context.object.hops.is_global)
            self.report({'INFO'}, F'Resharpen - Exit')
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            infobar.remove(self)
            return {'FINISHED'}

        #elif event.type == 'B' and event.value == 'PRESS':


        self.draw_master(context=context)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}


    def update(self, context):
        angle = math.radians(self.angle)

        context.area.header_text_set(text=f'Auto Smooth Angle: {self.angle:.1f}')

        for obj in self.objects:
            obj.data.auto_smooth_angle = angle


    def cancel(self, context):
        for obj in self.objects:
            # obj.data.use_auto_smooth = self.settings[obj]['use_auto_smooth'] # Commented out because mx prefers it this way
            obj.data.auto_smooth_angle = self.settings[obj]['auto_smooth_angle']


    def finish(self, context):
        context.area.header_text_set(text=None)
        self.remove_ui()
        infobar.remove(self)
        return {"FINISHED"}


    def draw_master(self, context):
        self.master.setup()

        if self.master.should_build_fast_ui():
            win_list = []
            help_list = []
            mods_list = []
            active_mod = ''
            obj = bpy.context.object

            if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1: #fast
                win_list.append(f'{self.angle:.1f}')
                win_list.append(f'{bpy.context.object.hops.is_global}')
                win_list.append(f'{bpy.context.object.data.use_auto_smooth}')
            else:
                if self.flag:
                    win_list.append('Auto Smooth Scan') #not fast
                else:
                    win_list.append('Auto Smooth') #not fast
                win_list.append(f'{self.angle:.1f}')
                win_list.append(f'Global Sharpen :{bpy.context.object.hops.is_global}')
                if not obj.modifiers:
                    win_list.append('[A] Add Bevel')
                if bpy.context.object.data.use_auto_smooth == False:
                    win_list.append('Autosmooth OFF')
                if self.flag:
                    win_list.append('[A] Return / [B] Toggle Bevel')
                    win_list.append('[LMB] Apply')

            help_list.append(['8',          'Set angle to 180°'])
            help_list.append(['7',          'Set angle to 90°'])
            help_list.append(['6',          'Set angle to 75°'])
            help_list.append(['5',          'Set angle to 60°'])
            help_list.append(['4',          'Set angle to 45°'])
            help_list.append(['3',          'Set angle to 30°'])
            help_list.append(['2',          'Set angle to 20°'])
            help_list.append(['1',          'Set angle to 15°'])
            help_list.append(['S',          f'Sharpen {self.angle:.1f}° - Exit'])
            help_list.append(['R',          f'Resharpen - Exit'])
            help_list.append(['G',          f'Toggle Global : {bpy.context.object.hops.is_global}'])
            #help_list.append(['B',          f'Transfer Autosmooth to Bevel - Exit'])
            help_list.append(['Shift + A',  f'Autosmooth Toggle {bpy.context.object.data.use_auto_smooth}'])
            help_list.append(['Scroll   ',  'Increment angle by 5°'])
            help_list.append(['Mouse    ',  f'Adjust angle smoothly: {self.angle:.1f}'])
            help_list.append(['A',          'Transfer Autosmooth to Bevel - Exit'])
            help_list.append(['M',          'Toggle mods list'])
            help_list.append(['H',          'Toggle help'])
            help_list.append(['~',          'Toggle viewport displays'])
            help_list.append(["O",          "Toggle viewport rendering"])


            for mod in reversed(context.active_object.modifiers):
                mods_list.append([mod.name, str(mod.type)])

            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image='Tthick', mods_list=mods_list, active_mod_name=active_mod)

        self.master.finished()

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


def bevels(obj, angle=False, weight=False, vertex_group=False, props={}):
    if not hasattr(obj, 'modifiers'):
        return []

    bevel_mods = [mod for mod in obj.modifiers if mod.type == 'BEVEL']

    if not angle and not weight and not vertex_group and not props:
        return bevel_mods

    modifiers = []
    limit_method_in = lambda method, mod: mod not in modifiers and mod.limit_method == method

    if angle:
        for mod in bevel_mods:
            if limit_method_in('ANGLE', mod):
                modifiers.append(mod)

    if weight:
        for mod in bevel_mods:
            if limit_method_in('WEIGHT', mod):
                #modifiers.append(mod)
                break

    if vertex_group:
        for mod in bevel_mods:
            if limit_method_in('VGROUP', mod):
                #modifiers.append(mod)
                break

    if props:

        for mod in bevel_mods:
            if mod in modifiers:
                continue

            for pointer in props:
                prop = hasattr(mod, pointer) and getattr(mod, pointer) == props[pointer]
                if not prop:
                    continue

                modifiers.append(mod)

    return sorted(modifiers, key=lambda mod: bevel_mods.index(mod))
