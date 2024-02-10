import bpy, bmesh, gpu, bgl
from gpu_extras.batch import batch_for_shader
from ... graphics.drawing2d import draw_text, set_drawing_dpi, draw_box
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... preferences import get_preferences
from ... utility import modifier
from ... utility.addon import method_handler


class HOPS_OT_MOD_Template(bpy.types.Operator):
    bl_idname = "hops.mod_template"
    bl_label = "Modal Operator Template"
    bl_options = {'REGISTER', 'UNDO', 'BLOCKING', 'GRAB_CURSOR'}
    bl_description = """
LMB - Adjust some modifier
LMB + Ctrl - Create a new modifier
LMB + Shift - Some special behavior

Press H for help
"""

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and obj.mode == 'OBJECT'


    def invoke(self, context, event):
        self.modal_scale = get_preferences().ui.Hops_modal_scale

        self.create_new = event.ctrl
        self.special_behavior = event.shift

        self.obj = context.active_object
        self.mods = [m for m in self.obj.modifiers if m.type == 'TYPE_HERE']

        if not self.mods:
            self.create_new = True

        if self.create_new:
            self.mod = self.obj.modifiers.new("Name Here", 'TYPE_HERE')
            self.mods.append(self.mod)

        else:
            self.mod = self.mods[-1]

        self.values = {m:{} for m in self.mods}
        for mod in self.mods:
            self.store(mod)

        self.buffer = self.mod.some_value
        self.mouse_prev_x = event.mouse_region_x

        self.mouse_start_x = event.mouse_region_x
        self.mouse_start_y = event.mouse_region_y

        self.add_draw_handler(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


    def modal(self, context, event):
        if event.type == 'MIDDLEMOUSE':
            return {'PASS_THROUGH'}

        elif event.type == 'Z' and (event.shift or event.alt):
            return {'PASS_THROUGH'}

        elif event.type in {'LEFTMOUSE', 'SPACE'}:
            self.remove_draw_handler(context)
            self.report({'INFO'}, "Finished")
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.remove_draw_handler(context)
            self.cancel(context)
            self.report({'INFO'}, "Cancelled")
            return {'CANCELLED'}

        elif event.type in {'WHEELDOWNMOUSE', 'WHEELUPMOUSE'} and event.shift:
            if event.type == 'WHEELDOWNMOUSE':
                self.scroll(1)
            elif event.type == 'WHEELUPMOUSE':
                self.scroll(-1)
            self.buffer = self.mod.some_value
            self.report({'INFO'}, f"Scrolled to {self.mod.name}")

        elif event.type == 'MOUSEMOVE':
            divisor = self.modal_scale * (10000 if event.shift else 1000)
            offset = event.mouse_region_x - self.mouse_prev_x
            self.buffer -= offset / divisor / get_dpi_factor()
            self.buffer = max(self.buffer, 0)
            digits = 2 if event.ctrl and event.shift else 1 if event.ctrl else 3
            self.mod.some_value = round(self.buffer, digits)

        elif event.type == "H" and event.value == "PRESS":
            get_preferences().property.hops_modal_help = not get_preferences().property.hops_modal_help
            context.area.tag_redraw()
            self.report({'INFO'}, f"{'Show' if get_preferences().property.hops_modal_help else 'Hide'} Help")

        self.mouse_prev_x = event.mouse_region_x
        return {'RUNNING_MODAL'}


    def cancel(self, context):
        for mod in self.mods:
            self.reset(mod)

        if self.create_new:
            self.obj.modifiers.remove(self.mods[-1])


    def scroll(self, direction):
        index = self.mods.index(self.mod)
        index = (index + direction) % len(self.mods)
        self.mod = self.mods[index]


    def store(self, mod):
        self.values[mod]["some_value"] = mod.some_value


    def reset(self, mod):
        mod.some_value = self.values[mod]["some_value"]


    def add_draw_handler(self, context):
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_ui, (context, ), "WINDOW", "POST_PIXEL")
        context.area.header_text_set(text=None)
        context.area.tag_redraw()


    def remove_draw_handler(self, context):
        self.remove_ui()
        context.area.header_text_set(text=None)
        context.area.tag_redraw()


    def draw_ui(self, context):
        method_handler(self._draw_ui,
            arguments = (context, ),
            identifier = f'{self.bl_label} UI Shader',
            exit_method = self.remove_ui)


    def _draw_ui(self, context):
        x = self.mouse_start_x
        y = self.mouse_start_y

        c1 = get_preferences().color.Hops_hud_color
        c2 = get_preferences().color.Hops_hud_help_color
        c3 = get_preferences().color.Hops_hud_text_color

        set_drawing_dpi(get_dpi())
        f = get_dpi_factor()
        o = 5

        l1 = (3, 23, 4, 44)
        l2 = (46, 23, 4, 146)
        l3 = (149, 23, 4, 280)

        vertices = (
            (x + (l1[0] - o) * f, y + l1[1] * f),
            (x + l1[0] * f, y + l1[2] * f),
            (x + (l1[3] - o) * f, y + l1[1] * f),
            (x + l1[3] * f, y + l1[2] * f),

            (x + (l2[0] - o) * f, y + l2[1] * f),
            (x + l2[0] * f, y + l2[2] * f),
            (x + (l2[3] - o) * f, y + l2[1] * f),
            (x + l2[3] * f, y + l2[2] * f),

            (x + (l3[0] - o) * f, y + l3[1] * f),
            (x + l3[0] * f, y + l3[2] * f),
            (x + (l3[3] - o) * f, y + l3[1] * f),
            (x + l3[3] * f, y + l3[2] * f))

        l1 = (l1[0] - 15, l1[1], l1[2], l1[0] - 6)

        vertices2 = (
            (x + (l1[0] - o) * f, y + l1[1] * f),
            (x + l1[0] * f, y + l1[2] * f),
            (x + (l1[3] - o) * f, y + l1[1] * f),
            (x + l1[3] * f, y + l1[2] * f))

        indices = (
            (0, 1, 2),
            (1, 2, 3),
            (4, 5, 6),
            (5, 6, 7),
            (8, 9, 10),
            (9, 10, 11))

        indices2 = (
            (0, 1, 2),
            (1, 2, 3))

        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)
        shader.bind()
        shader.uniform_float("color", c1)

        bgl.glEnable(bgl.GL_BLEND)
        batch.draw(shader)
        bgl.glDisable(bgl.GL_BLEND)

        shader2 = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        batch2 = batch_for_shader(shader2, 'TRIS', {"pos": vertices2}, indices=indices2)
        shader2.bind()
        shader2.uniform_float("color", c2)

        bgl.glEnable(bgl.GL_BLEND)
        batch2.draw(shader2)
        bgl.glDisable(bgl.GL_BLEND)

        draw_text(f"{self.mod.some_value}", x + 10 * f, y + 9 * f, size=12, color=c3)

        self.draw_help(context, x, y, f)


    def draw_help(self, context, x, y, f):
        c2 = get_preferences().color.Hops_hud_help_color

        if get_preferences().property.hops_modal_help:
            draw_text(" Key - Adjust Some Value", x + 45 * f, y - 14 * f, size=11, color=c2)
            draw_text(" H - Show/Hide Help", x + 45 * f, y - 26 * f, size=11, color=c2)

        else:
            draw_text(" H - Show/Hide Help", x + 45 * f, y - 14 * f, size=11, color=c2)


    def remove_ui(self):
        if self.draw_handler:
            self.draw_handler = bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
