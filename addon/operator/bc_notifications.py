import importlib

from copy import deepcopy as copy

import bpy

from bpy.types import Operator
from bpy.props import StringProperty
from bpy.utils import register_class, unregister_class
from ... preferences import get_preferences
from .. utility import addon
from ... ui_framework.operator_ui import Master

# tracked_events = None
tracked_states = None


class HOPS_OT_bc_notifications(Operator):
    bl_idname = 'hops.bc_notifications'
    bl_label = 'BoxCutter Notifications'
    bl_options = {'INTERNAL'}

    info: StringProperty(default='Notification')


    def notifications(self, prop_name):
        notification = 'Notification'
        prop = getattr(self, prop_name)

        if prop_name in self.exclude_notifications:
            return notification

        if prop_name == 'mode':
            value = self.mode
            notification = F'{value.title()[:-1 if value in {"SLICE", "MAKE"} else len(value)] if value != "KNIFE" else "Using Knife"}{"t" if value in {"CUT", "INSET"} else ""}{"ing" if value != "KNIFE" else ""}'

        elif prop_name == 'operation':
            if self.operation == 'NONE':
                notification = 'Shape Locked'
            else:
                value = self.operation
                notification = F'{"Added " if value == "ARRAY" else ""}{value.title()[:-1 if value in {"MOVE", "ROTATE", "SCALE", "EXTRUDE", "DISPLACE"} else len(value)]}{"ing" if value != "ARRAY" else ""}'

        elif isinstance(prop, str):
            notification = F'{prop_name.replace("_", " ").title()}: {prop}'

        elif isinstance(prop, float):
            notification = F'{self.operation.title()} {prop_name.partition("_")[-1].title()}: {getattr(self, prop_name):.3f}'

        elif isinstance(prop, bool):
            notification = F'{prop_name.replace("_", " ").title()} is {"En" if prop else "Dis"}abled'

        elif isinstance(prop, int):
            notification = F'{self.operation.title()} {prop_name.partition("_")[-1].title()}: {getattr(self, prop_name)}'

        return notification


    def execute(self, context):
        # global tracked_events
        global tracked_states

        if not tracked_states:
            BC = importlib.import_module(context.window_manager.bc.addon)

            # tracked_events = BC.addon.operator.shape.utility.tracked_events
            tracked_states = BC.addon.operator.shape.utility.tracked_states

        preference = addon.bc()

        self.shape_name = ''
        self.tracked_props = {
            'active_material': context.window_manager.Hard_Ops_material_options,
            'mode': tracked_states,
            'operation': tracked_states,
            'shape_type': tracked_states,
            'array_distance': tracked_states,
            'modified': tracked_states,
            'cancelled': tracked_states,
            'axis': context.scene.bc,
            'mirror_axis': context.scene.bc,
            'solidify_thickness': preference.shape,
            'inset_thickness': preference.shape,
            'circle_vertices': preference.shape,
            'bevel_segments': preference.shape,
            'bevel_width': preference.shape,
            'array_count': preference.shape,
            'show_shape': preference.behavior,
            'hops_mark': preference.behavior,
            'q_bevel': context.scene.bc,
            'wedge': preference.shape, #new additions
            'grid_units': preference.snap,
            'set_origin': preference.behavior,
            'show_shape': preference.behavior,
            'recut': preference.behavior,
            'origin': tracked_states,
        }

        self.forced = [
            'active_material',
            'mirror_axis',
            'dimensions',
        ]

        self.iter = [
            'mirror_axis',
        ]

        self.array_axis = 'X'

        self.exclude_notifications = [
            'modified',
            # 'cancelled',
        ]

        for prop_name, value in self.tracked_props.items():
            if prop_name not in self.iter:
                setattr(self, prop_name, copy(getattr(value, prop_name)) if value else None)
                continue

            setattr(self, prop_name, [copy(i) for i in getattr(value, prop_name)] if value else [])

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


    def modal(self, context, event):
        bc = context.scene.bc
        self.force = False

        default = 'Notification'
        info = default

        if bc.shape:
            if 'array_axis' not in self.tracked_props.keys():
                self.tracked_props['array_axis'] = bc.shape.bc

            elif 'dimensions' not in self.tracked_props.keys():
                self.tracked_props['dimensions'] = bc.shape
                self.dimensions = list(bc.shape.dimensions[:])
                self.iter.append('dimensions')

        for prop_name, value in self.tracked_props.items():
            if prop_name not in self.iter and getattr(self, prop_name) != getattr(value, prop_name):
                if bc.running:
                    setattr(self, prop_name, getattr(value, prop_name))

                info = self.notifications(prop_name)
                self.force = prop_name in self.forced
                continue

            elif prop_name not in self.iter:
                continue

            it = getattr(self, prop_name)
            for i in range(len(it)):
                if 'dimension' in prop_name and not bc.running:
                    break

                prop = getattr(value, prop_name)
                if it[i] != prop[i]:
                    getattr(self, prop_name)[i] = prop[i]

                    # axis = {
                    #     0: 'X',
                    #     1: 'Y',
                    #     2: 'Z',}

                    if 'axis' in prop_name:
                        if not it[i]:
                            continue

                        if info == default:
                            self.force = prop_name in self.forced
                            info = F'{prop_name.replace("_", " ").title()}  {"XYZ"[i]}'

                        # info += axis[i]

                    elif 'dimension' in prop_name and self.operation in {'DRAW', 'EXTRUDE', 'OFFSET'}:
                        if not it[i]:
                            continue

                        if info == default:
                            self.force = prop_name in self.forced

                            if i in {0, 1}:
                                info = F'{self.operation.title()}  X: {getattr(value, prop_name)[0]:.3f} Y: {getattr(value, prop_name)[1]:.3f}'
                                continue

                            elif self.operation != 'DRAW':
                                info = F'{"Extrude" if self.operation != "OFFSET" else "Dimension Z"}: {getattr(value, prop_name)[i]:.3f}'

                    elif self.operation in {'ROTATE', 'SCALE', 'MOVE'}:
                        if not it[i]:
                            continue

                        if info == default:
                            self.force = prop_name in self.forced
                            info = F'{self.operation.title()}'

        if not bc.running:
            info = 'Finished'

        if info != default and info != self.info and (self.modified or self.force):
            self.info = info

            new_notification(self.info)

        return {'PASS_THROUGH' if bc.running else 'FINISHED'}


def new_notification(info):
    ui = Master()

    draw_data = [[info]]

    ui.receive_draw_data(draw_data=draw_data)
    ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)


def register():
    register_class(HOPS_OT_bc_notifications)


def unregister():
    unregister_class(HOPS_OT_bc_notifications)
