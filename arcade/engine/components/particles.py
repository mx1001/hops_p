import bpy, math, time, mathutils
from mathutils import Vector
from .... addon.utility.screen import dpi_factor
from ..drawing.gl_funcs import draw_2D_points


class Particle_Data:
    '''Particle data for emitters.'''
    
    def __init__(self):

        self.finished = False
        self.start_time = time.time()
        self.fade_time = 1.25
        self.original_alpha = 1
        self.alpha = 1
        self.color = (0,0,0,1)
        self.location = (0,0)
        self.gravity = -1
        self.force = 5
        self.point_size = 2
        self.points = []


class Explosion_Particle_Effect:
    '''Simple particle emitter.'''

    def __init__(self):

        self.scale_factor = dpi_factor()
        if bpy.context.preferences.system.pixel_size == 2:
            self.scale_factor *= .75

        # Component Props
        self.emitters = []


    def spawn_emitter(self, location=(0,0), color=(0,0,0,1,), gravity=-1, force=5, point_size=2, particle_count=20, fade_time=1.25):
        '''Call this function to explode particles.'''
        
        p_data = Particle_Data()
        p_data.location = location
        p_data.fade_time = fade_time
        p_data.original_alpha = color[3]
        p_data.alpha = color[3]
        p_data.color = color
        p_data.gravity = gravity
        p_data.force = force
        p_data.point_size = point_size

        # Add points in a ring formation
        radius = 5
        points = []
        for i in range(particle_count):
            index = i + 1
            angle = i * 3.14159 * 2 / particle_count
            x = math.cos(angle) * radius
            y = math.sin(angle) * radius
            x += location[0]
            y += location[1]
            points.append((x, y))

        p_data.points = points

        self.emitters.append(p_data)


    def update(self, delta_time):
        '''Update all the particles'''

        current_time = time.time()
        for p_data in self.emitters:
            for i in range(len(p_data.points)):

                point = p_data.points[i]

                direction = Vector((
                    point[0] - p_data.location[0],
                    point[1] - p_data.location[1]
                ))

                direction.normalize()
                
                time_diff = time.time() - p_data.start_time
                additive_force = (time.time() - p_data.start_time) * 250

                force_vec = [
                    p_data.force * delta_time * direction[0],
                    p_data.force * delta_time * direction[1],
                ]

                force_vec[0] *= additive_force
                force_vec[1] *= additive_force

                force_vec[1] += p_data.gravity * delta_time * time_diff

                p_data.points[i] = (
                    point[0] + force_vec[0],
                    point[1] + force_vec[1]
                )

                p_data.alpha = 1 - (p_data.original_alpha / p_data.fade_time) * time_diff
        
        self.emitters = [p for p in self.emitters if p.alpha > 0]


    def draw(self, context):
        '''Draw any particles.'''

        for p_data in self.emitters:
            color = (p_data.color[0], p_data.color[1], p_data.color[2], p_data.alpha)
            draw_2D_points(p_data.points, size=p_data.point_size, color=color)