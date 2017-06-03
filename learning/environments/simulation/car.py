import sys
import math
import random
import pygame
import pymunk
import pymunk.pygame_util
from pygame.locals import *
from pygame.color import THECOLORS
from pymunk.vec2d import Vec2d


class CarSimulation:
    """
    Simulated game environment
    Renders the game using PyGame
    Computes Game Physics using PyMunk
    """
    env_width = 1000
    env_height = 700
    sonar_scale = 0.1
    steering_scale = 0.05
    throttle_scale = 100

    def __init__(self):

        # Public properties
        self.throttle = 0
        self.steering = 0
        self.front_sonar = 0
        self.rear_sonar = 0

        # Start pygame
        self.init_pygame()

        # Global-ish.
        self.crashed = False

        # Physics stuff.
        self.space = pymunk.Space()
        self.space.gravity = pymunk.Vec2d(0., 0.)

        # Create the car.
        self.create_car(300, 300, 25)

        # Record steps.
        self.num_steps = 0

        # Create walls.
        height = self.env_height
        width = self.env_width
        static = [
            pymunk.Segment(
                self.space.static_body,
                (0, 1), (0, height), 1),
            pymunk.Segment(
                self.space.static_body,
                (1, height), (width, height), 1),
            pymunk.Segment(
                self.space.static_body,
                (width-1, height), (width-1, 1), 1),
            pymunk.Segment(
                self.space.static_body,
                (1, 1), (width, 1), 1)
        ]
        for s in static:
            s.friction = 1.
            s.group = 1
            s.collision_type = 1
            s.color = THECOLORS['red']
        self.space.add(static)
        self.space.add(self.create_wall())

        # Create some obstacles, semi-randomly.
        # We'll create three and they'll move around to prevent over-fitting.
        self.obstacles = []
        #self.obstacles.append(self.create_obstacle(200, 550, 20))
        #self.obstacles.append(self.create_obstacle(700, 200, 30))
        #self.obstacles.append(self.create_obstacle(550, 600, 20))
        #self.obstacles.append(self.create_obstacle(200, 200, 20))

        # Create a cat.
        #self.create_cat()


    def init_pygame(self):
        """
        Initilize pygame simulation
        """
        pygame.init()
        self.screen = pygame.display.set_mode((self.env_width, self.env_height))
        self.clock = pygame.time.Clock()
        self.screen.set_alpha(None)
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        print("Initialized PyGame")


    def render(self):
        """
        Render the game simulation
        """
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.flip()


    def render_position(text, x, y, size = 50, color = (200, 000, 000)):
        font_type = 'data/fonts/orecrusherexpand.ttf'
        text = str(text)
        font = pygame.font.Font(font_type, size)
        text = font.render(text, True, color)
        screen.blit(text, (x, y))


    def reset(self):
        """
        Reset the game simulation
        """
        x = random.randint(-20,20)+self.env_width/2
        y = random.randint(-20,20)+self.env_height/4
        self.car_body.position = x,y
        self.car_body.angle = 0.5*random.random()


    def create_obstacle(self, x, y, r):
        """
        Create an obstacle in the environment
        """
        inertia = pymunk.moment_for_circle(10, 0, 140, (0, 0))
        c_body = pymunk.Body(1,inertia)
        c_shape = pymunk.Circle(c_body, r)
        c_shape.elasticity = 1.0
        c_body.position = x, y
        c_shape.color = THECOLORS["blue"]
        self.space.add(c_body, c_shape)
        return c_body


    def create_wall(self,thickness=10):
        """
        Create wall in the environment
        """
        start = (200, self.env_height/2)
        end = (self.env_width-200, self.env_height/2)
        wall = pymunk.Segment(self.space.static_body, start, end, thickness)
        wall.friction = 1.
        wall.group = 1
        wall.collision_type = 1
        wall.color = THECOLORS['red']
        return wall


    def create_cat(self):
        """
        Create an moving obstacle in the environment
        """
        inertia = pymunk.moment_for_circle(1, 0, 14, (0, 0))
        self.cat_body = pymunk.Body(1, inertia)
        self.cat_body.position = self.env_width/2, self.env_height/2
        self.cat_shape = pymunk.Circle(self.cat_body, 30)
        self.cat_shape.color = THECOLORS["orange"]
        self.cat_shape.elasticity = 1.0
        self.cat_shape.angle = 0.5
        direction = Vec2d(1, 0).rotated(self.cat_body.angle)
        self.space.add(self.cat_body, self.cat_shape)


    def create_car(self,x,y,radius):
        """
        Create a siumlated representation of the car
        """
        inertia = pymunk.moment_for_circle(1, 0, 14, (0, 0))
        self.car_body = pymunk.Body(1, inertia)
        self.car_body.position = x, y
        self.car_shape = pymunk.Circle(self.car_body, radius)
        self.car_shape.color = THECOLORS["green"]
        self.car_shape.elasticity = 0.4
        self.car_body.angle = 0
        self.car_body.friction = 0.1
        self.space.add(self.car_body, self.car_shape)
        # Move the car towards the center
        #self.space.step(1/10)
        #driving_direction = 100*Vec2d(1, 0).rotated(0.45)
        #$elf.car_body.apply_impulse_at_local_point(driving_direction)



    def get_driving_direction(self):
        """
        Return the driving direction in global coordinates
        """
        return Vec2d(1, 0).rotated(self.car_body.angle)


    def frame_step(self, action):
        """
        Take @action and move forward one time step
        """
        self.steering = action[0]
        self.throttle = action[1]

        self.move_car()
        #self.move_obstacles()
        #self.move_cat()

        # Update the screen and stuff.
        self.screen.fill(THECOLORS["black"])
        self.space.step(1/10)
        self.space.debug_draw(self.draw_options)
        self.clock.tick()

        # Update the sonar readings
        x, y = self.car_body.position
        readings = self.get_sonar_readings(x, y, self.car_body.angle)
        self.num_steps += 1
        self.front_sonar = readings[0]
        self.rear_sonar = readings[1]



    def move_car(self):
        """
        Update the car position based on the current throttle and steering
        """
        driving_direction = self.get_driving_direction()
        self.car_body.velocity = self.throttle_scale * self.throttle * driving_direction
        self.car_body.angle += self.throttle * self.steering * self.steering_scale # Update angle


    def move_obstacles(self):
        """
        Randomly move obstacles around.
        """
        for obstacle in self.obstacles:
            speed = random.randint(20, 100)
            angle = 2*math.pi*random.random()
            direction = Vec2d(1, 0).rotated(angle)
            obstacle.angle = angle
            obstacle.velocity = speed * direction


    def move_cat(self):
        """
        Randomly move cat around.
        """
        speed = random.random()
        direction = Vec2d(self.car_body.position)-Vec2d(self.cat_body.position)
        self.cat_body.velocity = speed * direction


    def get_sonar_readings(self, x, y, angle):
        """
        Instead of using a grid of boolean(ish) sensors, sonar readings
        simply return N "distance" readings, one for each sonar
        we're simulating. The distance is a count of the first non-zero
        reading starting at the object. For instance, if the fifth sensor
        in a sonar "arm" is non-zero, then that arm returns a distance of 5.
        """
        readings = []
        arm_front = self.make_sonar_arm(x, y)
        arm_rear = arm_front

        # Rotate them and get readings.
        front = self.get_arm_distance(arm_front, x, y, angle, 0)
        rear = self.get_arm_distance(arm_rear, x, y, angle, math.pi)

        readings.append(self.sonar_scale*front)
        readings.append(self.sonar_scale*rear)
        return readings


    def get_arm_distance(self, arm, x, y, angle, offset):
        """
        Get the distance reading from a sonar arm
        """
        # Used to count the distance.
        i = 0

        # Look at each point and see if we've hit something.
        for point in arm:
            i += 1

            # Move the point to the right spot.
            rotated_p = self.get_rotated_point(
                x, y, point[0], point[1], angle + offset
            )

            # Check if we've hit something. Return the current i (distance)
            # if we did.
            if rotated_p[0] <= 0 or rotated_p[1] <= 0 \
                    or rotated_p[0] >= self.env_width or rotated_p[1] >= self.env_height:
                return i  # Sensor is off the screen.
            else:
                obs = self.screen.get_at(rotated_p)
                if self.get_track_or_not(obs) != 0:
                    return i

            pygame.draw.circle(self.screen, (255, 255, 255), (rotated_p), 2)

        # Return the distance for the arm.
        return i


    def make_sonar_arm(self, x, y):
        """
        Make a sonar arm
        """
        spread = 10  # Default spread.
        distance = 30  # Gap before first sensor.
        arm_points = []
        # Make an arm. We build it flat because we'll rotate it about the
        # center later.
        for i in range(1, 40):
            arm_points.append((distance + x + (spread * i), y))

        return arm_points


    def get_rotated_point(self, x_1, y_1, x_2, y_2, radians):
        """
        Rotate x_2, y_2 around x_1, y_1 by angle.
        """
        x_change = (x_2 - x_1) * math.cos(radians) + \
            (y_2 - y_1) * math.sin(radians)
        y_change = (y_1 - y_2) * math.cos(radians) - \
            (x_1 - x_2) * math.sin(radians)
        new_x = x_change + x_1
        new_y = self.env_height - (y_change + y_1)
        return int(new_x), int(new_y)


    def get_track_or_not(self, reading):
        """
        Return whether an object is tracked
        """
        if reading == THECOLORS['black']:
            return 0
        else:
            return 1