import bpy, time
from mathutils import Vector
import random
from .... addon.utility.screen import dpi_factor
from .... preferences import get_preferences
from .... utility.base_modal_controls import Base_Modal_Controls
from .... addon.utility import method_handler
from .... import bl_info

# Engine
from ... engine import *


class HOPS_OT_Arcade_Pong(bpy.types.Operator):
    bl_idname = "hops.pong"
    bl_label = "Play Pong"
    bl_description = "Play pong in the 3D view"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}


    def invoke(self, context, event):

        ###########################
        # <--- Setup Windows ---> #
        ###########################
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        space.show_region_toolbar = False
                        space.show_region_ui = False

        self.scale_factor = dpi_factor()
        self.window_padding = 120 * self.scale_factor

        context.window.cursor_modal_set('HAND')

        ########################
        # <--- Game Props ---> #
        ########################
        self.screen_width = context.area.width - self.window_padding
        self.screen_height = context.area.height - self.window_padding
        self.delta_time = time.time()
        self.last_frame_end_time = time.time()
        self.mouse_pos = (event.mouse_region_x, event.mouse_region_y)
        self.ball_vec = (random.uniform(500, 1000), random.uniform(-1000, 1000))
        self.max_speed = self.screen_width
        self.paddle_padding = 20
        self.player_score = 0
        self.npc_score = 0

        ###########################
        # <--- Drawing Props ---> #
        ###########################
        self.hops_logo_scale = self.screen_height / (100 * self.scale_factor)

        ########################
        # <--- Components ---> #
        ########################

        # Background
        self.background = Rectangle_Comp(use_scale_factor=False)
        self.background.height = context.area.height - self.window_padding * 2
        self.background.width = context.area.width - self.window_padding * 2
        self.background.location = (context.area.width * .5, context.area.height * .5)
        self.background.line_color = (.5,.5,.5,1)
        self.background.poly_color = (0,0,0,.375)

        # Background Lines
        self.bg_lines = Lines_Comp()
        self.bg_lines.line_color = (.5,.5,.5,1)
        self.bg_lines.line_width = 6
        self.bg_lines.vertices = [
            (context.area.width * .5, self.window_padding + self.hops_logo_scale * (12 * self.scale_factor)),
            (context.area.width * .5, self.screen_height)]

        # HOPS Label Text Release Name
        self.hops_label_text = Text_Comp()
        self.hops_label_text.center = False
        self.hops_label_text.font_color = (.5,.5,.5,1)
        self.hops_label_text.font_size = 24
        self.hops_label_text.location = (self.window_padding, self.screen_height + 10 * self.scale_factor)
        self.hops_label_text.text = f"{bl_info['description']}"

        # HOPS Label Text Version Number
        self.hops_label_text_v_number = Text_Comp()
        self.hops_label_text_v_number.center = False
        self.hops_label_text_v_number.font_color = (.5,.5,.5,1)
        self.hops_label_text_v_number.font_size = 24
        self.hops_label_text_v_number.location = (self.screen_width - 220 * self.scale_factor, self.window_padding - 24 * self.scale_factor)
        self.hops_label_text_v_number.text = f"HOps: {bl_info['version'][0]}.{bl_info['version'][1]}.{bl_info['version'][2]}.{bl_info['version'][3]}"

        # Hot Key
        self.hot_key = Text_Comp()
        self.hot_key.center = False
        self.hot_key.font_color = (.5,.5,.5,1)
        self.hot_key.font_size = 16
        self.hot_key.location = (self.screen_width - 220 * self.scale_factor, self.window_padding - 48 * self.scale_factor)
        self.hot_key.text = "A : Toggle Animation"

        # Hot Key
        self.hot_key_scroll = Text_Comp()
        self.hot_key_scroll.center = False
        self.hot_key_scroll.font_color = (.5,.5,.5,1)
        self.hot_key_scroll.font_size = 16
        self.hot_key_scroll.location = (self.screen_width - 220 * self.scale_factor, self.window_padding - 72 * self.scale_factor)
        self.hot_key_scroll.text = "Scroll : Adjust Paddle Height"

        # Credits Marquee
        self.marquee = Marquee_Comp()
        self.marquee.top_left = (self.window_padding, self.window_padding - 6 * self.scale_factor)
        self.marquee.marquee_text = {} 
        self.marquee.header_font_color = (.5,.5,.5,1)
        self.marquee.body_font_color = (.5,.5,.5,.75)
        self.setup_marquee_text()
        self.marquee.setup()

        # Player Combo Text
        self.player_combo_text = Combo_Counter_Comp()
        self.player_combo_text.lead_font_size = 26
        self.player_combo_text.lead_font_color = (.5,.5,.5,1)
        self.player_combo_text.font_size = 42
        self.player_combo_text.font_color = (0,0,1,1)
        self.player_combo_text.particle_color = (0,0,1,1)
        self.player_combo_text.location = (self.player_combo_text.font_size * 2 + self.window_padding, self.screen_height - self.player_combo_text.font_size * 2)
        self.player_combo_text.current_text = str(self.player_score)

        # NPC Combo Text
        self.npc_combo_text = Combo_Counter_Comp()
        self.npc_combo_text.lead_font_size = 26
        self.npc_combo_text.lead_font_color = (.5,.5,.5,1)
        self.npc_combo_text.font_size = 42
        self.npc_combo_text.font_color = (1,0,0,1)
        self.npc_combo_text.particle_color = (1,0,0,1)
        self.npc_combo_text.location = (self.screen_width - self.player_combo_text.font_size * 2, self.screen_height - self.player_combo_text.font_size * 2)
        self.npc_combo_text.current_text = str(self.npc_score)

        # Main Player
        self.main_player = Rectangle_Comp()
        self.main_player.height = 70
        self.main_player.width = 20
        self.main_player.line_color = (0,0,1,1)
        self.main_player.poly_color = (0,0,.5,1)

        # NPC
        self.npc = Rectangle_Comp()
        self.npc.height = 70
        self.npc.width = 20
        self.npc.line_color = (1,0,0,1)
        self.npc.poly_color = (.5,0,0,1)

        # Ball Trail Render
        self.trail_render = Trail_Render_Comp()
        self.trail_render.line_color = (.5,.5,.5,1)

        # Ball
        self.ball = Circle_Comp()
        self.ball.location = (context.area.width * .5, context.area.height * .5)
        self.ball.radius = 10
        self.ball.line_color = (1,1,1,1)
        self.ball.poly_color = (.5,.5,.5,1)

        # Particles
        self.particles = Explosion_Particle_Effect()

        # Store all the objects
        self.components = [
            self.hops_label_text,
            self.hops_label_text_v_number,
            self.hot_key,
            self.hot_key_scroll,
            self.marquee,
            self.background,
            self.bg_lines,
            self.player_combo_text,
            self.npc_combo_text,
            self.main_player,
            self.npc,
            self.trail_render,
            self.ball,
            self.particles]

        ##########################
        # <--- Base Systems ---> #
        ##########################
        self.base_controls = Base_Modal_Controls(context, event)
        self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.safe_draw_shader, (context,), 'WINDOW', 'POST_PIXEL')
        self.timer = context.window_manager.event_timer_add(0.0166, window=context.window)

        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}


    def modal(self, context, event):

        # FPS
        self.delta_time = time.time() - self.last_frame_end_time

        ##########################
        # <--- Base Systems ---> #
        ##########################
        self.base_controls.update(context, event)

        ########################
        # <--- Game Props ---> #
        ########################
        self.mouse_pos = (event.mouse_region_x, event.mouse_region_y)

        ##########################
        # <--- Game Updates ---> #
        ##########################
        self.update(context, event)

        # Base controls
        if self.base_controls.cancel:
            self.remove_shader()
            context.window_manager.event_timer_remove(self.timer)
            context.area.tag_redraw()
            context.window.cursor_modal_set('DEFAULT')
            return {'CANCELLED'}

        elif self.base_controls.confirm:
            self.remove_shader()
            context.window_manager.event_timer_remove(self.timer)
            context.area.tag_redraw()
            context.window.cursor_modal_set('DEFAULT')
            return {'FINISHED'}

        # Toggle the viewport animation
        if event.type == "A" and event.value == "PRESS":
            bpy.ops.screen.animation_play('INVOKE_DEFAULT')

        if self.base_controls.scroll:
            if self.base_controls.scroll > 0:
                self.adjust_player_paddle_size(scale_factor=5)
            else:
                self.adjust_player_paddle_size(scale_factor=-5)

        self.last_frame_end_time = time.time()
        context.area.tag_redraw()
        return {"RUNNING_MODAL"}

    
    def update(self, context, event):
        '''Setup game objects.'''

        self.main_player_update(context)
        self.npc_update(context)
        self.ball_location_update(context)
        self.trail_render.update(new_point=self.ball.location)
        self.particles.update(self.delta_time)


    def safe_draw_shader(self, context):
        method_handler(self.draw_shader,
            arguments = (context,),
            identifier = 'Pong Game',
            exit_method = self.remove_shader)


    def remove_shader(self):
        '''Remove shader handle.'''

        if self.draw_handle:
            self.draw_handle = bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle, "WINDOW")


    def draw_shader(self, context):
        '''Draw shader handle.'''

        # Draw the hops logo
        color = (0,0,0,.5)
        if self.player_score > self.npc_score:
            color = (0,0,1,.5)
        elif self.player_score < self.npc_score:
            color = (1,0,0,.5)

        draw_arcade_hops_logo(
            color=color,
            size=self.hops_logo_scale, 
            x=(context.area.width * .5) - (self.hops_logo_scale * .5) * (10 * self.scale_factor),
            y=self.window_padding + (10 * self.scale_factor))

        # Draw game
        for component in self.components:
            component.draw(context)


    def main_player_update(self, context):
        '''Update the player paddle.'''

        self.main_player.location = (self.window_padding + self.paddle_padding, self.mouse_pos[1])

        # Paddle Y Clamp
        if self.main_player.location[1] + self.main_player.height * .5 >= self.screen_height:
            self.main_player.location = (self.main_player.location[0], self.screen_height - self.main_player.height * .5)

        elif self.main_player.location[1] - self.main_player.height * .5 <= self.window_padding:
            self.main_player.location = (self.main_player.location[0], self.window_padding + self.main_player.height * .5)


    def npc_update(self, context):
        '''Update the player paddle.'''

        chase_increment = (self.ball.location[1] - self.npc.location[1]) * self.delta_time * 15
        idle_increment = (context.area.height * .5 - self.npc.location[1]) * self.delta_time * 5

        # Chase ball when vec is coming towards
        if self.ball_vec[0] > 0:
            self.npc.location = (
                context.area.width - self.window_padding - self.paddle_padding, 
                self.npc.location[1] + chase_increment)
        # Start towards center
        else:
            self.npc.location = (
                context.area.width - self.window_padding - self.paddle_padding, 
                self.npc.location[1] + idle_increment)


        # Paddle Y Clamp
        if self.npc.location[1] + self.npc.height * .5 >= self.screen_height:
            self.npc.location = (self.npc.location[0], self.screen_height - self.npc.height * .5)

        elif self.npc.location[1] - self.npc.height * .5 <= self.window_padding:
            self.npc.location = (self.npc.location[0], self.window_padding + self.npc.height * .5)


    def ball_location_update(self, context):
        '''Update the location of the main ball.'''

        # Move the ball with the ball vec
        self.ball.location = (
            self.ball.location[0] + self.ball_vec[0] * self.delta_time, 
            self.ball.location[1] + self.ball_vec[1] * self.delta_time)

        # Player Paddle
        if self.ball.location[0] + self.ball.radius <= self.main_player.location[0] + self.main_player.width * .5:
            if self.ball.location[1] + self.ball.radius >= self.main_player.location[1] - self.main_player.height * .5:
                if self.ball.location[1] - self.ball.radius <= self.main_player.location[1] + self.main_player.height * .5:
                    x = random.uniform(self.max_speed * .75, self.max_speed)
                    y = random.uniform(-self.max_speed, self.max_speed)
                    self.ball_vec = (x, y)
                    self.ball.location = (
                        self.main_player.location[0] + self.ball.radius + (2 * self.scale_factor) + self.main_player.width * .5, 
                        self.ball.location[1])
                    
        # NPC Paddle
        if self.ball.location[0] + self.ball.radius >= self.npc.location[0] - self.npc.width * .5:
            if self.ball.location[1] + self.ball.radius >= self.npc.location[1] - self.npc.height * .5:
                if self.ball.location[1] - self.ball.radius <= self.npc.location[1] + self.npc.height * .5:
                    x = -random.uniform(self.max_speed * .75, self.max_speed)
                    y = random.uniform(-self.max_speed, self.max_speed)
                    self.ball_vec = (x, y)
                    self.ball.location = (
                        self.npc.location[0] - self.ball.radius - (2 * self.scale_factor) - self.npc.width * .5, 
                        self.ball.location[1])

        # Clamp ball speed
        if self.ball_vec[0] > self.max_speed or self.ball_vec[1] > self.max_speed:
            x_sign = 1 if self.ball_vec[0] >= 0 else -1
            y_sign = 1 if self.ball_vec[1] >= 0 else -1
            self.ball_vec = (self.max_speed * x_sign, self.max_speed * y_sign)

        # Window X Clamp
        if self.ball.location[0] + self.ball.radius >= self.screen_width:
            self.player_scored_point(context)

        elif self.ball.location[0] - self.ball.radius <= self.window_padding:
            self.npc_scored_point(context)

        # Window Y Clamp
        if self.ball.location[1] + self.ball.radius >= self.screen_height:
            self.ball_vec = (self.ball_vec[0], -abs(self.ball_vec[1]))
            self.ball.location = (self.ball.location[0], self.screen_height - self.ball.radius)

        elif self.ball.location[1] - self.ball.radius <= self.window_padding:
            self.ball_vec = (self.ball_vec[0], abs(self.ball_vec[1]))
            self.ball.location = (self.ball.location[0], self.window_padding + self.ball.radius)


    def player_scored_point(self, context):
        '''The ball hit the opposite sides wall.'''

        x = -random.uniform(500, self.max_speed)
        y = random.uniform(-1000, self.max_speed)
        self.player_score += 1
        self.player_combo_text.update_combo(location=self.player_combo_text.location, new_text=str(self.player_score))
        self.ball_vec = (x, y)
        hit_loc = (self.screen_width - self.ball.radius - 2, self.ball.location[1])
        self.particles.spawn_emitter(location=hit_loc, color=(0,0,1,1,), gravity=-1000, force=10, point_size=5, particle_count=26)
        self.ball.location = (context.area.width * .5, context.area.height * .5)
        self.particles.spawn_emitter(location=self.ball.location, color=(.5,.5,.5,1), gravity=-500, force=5, point_size=5, particle_count=26)


    def npc_scored_point(self, context):
        '''The ball hit the opposite sides wall.'''

        x = random.uniform(500, self.max_speed)
        y = random.uniform(-1000, self.max_speed)
        self.npc_score += 1
        self.npc_combo_text.update_combo(location=self.npc_combo_text.location, new_text=str(self.npc_score))
        self.ball_vec = (x, y)
        hit_loc = (self.window_padding + self.ball.radius + 2, self.ball.location[1])
        self.particles.spawn_emitter(location=hit_loc, color=(1,0,0,1,), gravity=-1000, force=10, point_size=5, particle_count=26)
        self.ball.location = (context.area.width * .5, context.area.height * .5)
        self.particles.spawn_emitter(location=self.ball.location, color=(.5,.5,.5,1), gravity=-500, force=5, point_size=5, particle_count=26)


    def setup_marquee_text(self):
        '''Setups all the marquee text.'''

        # Authors
        self.marquee.marquee_text["Authors"] = []
        
        authors = bl_info['author'].split(",")
        for author in authors:
            author = author.strip()
            self.marquee.marquee_text["Authors"].append(author)

        # Addons
        self.marquee.marquee_text["Addons"] = []

        addons = bpy.context.preferences.addons.keys()
        new_addons = []
        for addon in addons:
            addon = addon.strip()
            if addon[:2] != "io":
                self.marquee.marquee_text["Addons"].append(addon)


    def adjust_player_paddle_size(self, scale_factor=1):
        '''Increase the player paddle size by the scale_factor.'''

        if scale_factor > 0:
            if self.main_player.height + scale_factor < self.screen_height * .5:
                self.main_player.adjust_width_height(add_height=scale_factor)
        elif scale_factor < 0:
            if self.main_player.height + scale_factor > 70 * self.scale_factor:
                self.main_player.adjust_width_height(add_height=scale_factor)
            else:
                self.main_player.height = 70
