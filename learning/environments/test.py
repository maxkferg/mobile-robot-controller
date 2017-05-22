# Test Environment
# Interface between learning algorith and physical car
# Represents the worlrd as a MDP

import random
import math
import numpy as np
import pygame
import pymunk
from pygame.color import THECOLORS
from pymunk.vec2d import Vec2d
from pymunk.pygame_util import draw
from ..q_learning.configs.linear import config


class TestEnvironment(object):
    """
    Test environment
    """
    crash_distance = 10

    def __init__(self,draw):
        self.steps = 0
        self.resets = 0
        self.state = GameState(draw)
        self.action_space = ActionSpace()
        self.observation_space = ObservationSpace()

        # Init PyGame

    def render(self):
        """
        Render the environment
        """
        pygame.display.flip()


    def reset(self):
        """
        Reset the environment
        Return the state
        """
        self.resets += 1
        action = self.action_space.sample()
        _,sonar,_ = self.state.frame_step(action)
        return self.get_state(sonar)


    def step(self,action):
        """
        Move the car.
        Return (new_state, reward, done, info) tuple
        """
        reward,sonar,done = self.state.frame_step(action)
        state = self.get_state(sonar)
        if self.steps%1000==0:
            done = True # Restart if it survives 1000 steps
        if done:
            self.reset()
        self.steps += 0
        return (state,reward,done,False)


    def get_state(self,sonar):
        """
        Return the current state
        """
        steering = self.state.steering
        throttle = self.state.throttle
        controls = [steering,throttle]
        state = np.array(sonar+controls)
        return state[None,:,None]



class ActionSpace(object):
    """
    Represents the actions which can be taken
    """
    n = 4

    def sample(self):
        return random.randint(0,self.n-1)


class ObservationSpace(object):
    """
    Represents the observations which can be made
    """
    shape = (1,4)



class GameState(object):
    """
    Simulated game environment
    Renders the game using PyGame
    Computes Game Physics using PyMunk
    """
    env_width = 1000
    env_height = 700
    sonar_scale = 10
    crash_distance = 2

    def __init__(self,draw=False):
        # Start pygame
        self.init_pygame()

        # Global-ish.
        self.crashed = False

        # Drawing
        self.show_sensors = draw
        self.draw_screen = draw

        # Physics stuff.
        self.space = pymunk.Space()
        self.space.gravity = pymunk.Vec2d(0., 0.)

        # Create the car.
        self.create_car(100, 100, 0.5)

        self.steering = 0
        self.throttle = 0

        # Record steps.
        self.num_steps = 0

        # Create walls.
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

        # Create some obstacles, semi-randomly.
        # We'll create three and they'll move around to prevent over-fitting.
        self.obstacles = []
        self.obstacles.append(self.create_obstacle(200, 350, 10))
        self.obstacles.append(self.create_obstacle(700, 200, 25))

        # Create a cat.
        self.create_cat()

    def init_pygame(self):
        # PyGame init
        pygame.init()
        self.screen = pygame.display.set_mode((self.env_width, self.env_height))
        self.clock = pygame.time.Clock()
        self.screen.set_alpha(None)


    def create_obstacle(self, x, y, r):
        c_body = pymunk.Body(pymunk.inf, pymunk.inf)
        c_shape = pymunk.Circle(c_body, r)
        c_shape.elasticity = 1.0
        c_body.position = x, y
        c_shape.color = THECOLORS["blue"]
        self.space.add(c_body, c_shape)
        return c_body


    def create_cat(self):
        inertia = pymunk.moment_for_circle(1, 0, 14, (0, 0))
        self.cat_body = pymunk.Body(1, inertia)
        self.cat_body.position = 50, height - 100
        self.cat_shape = pymunk.Circle(self.cat_body, 30)
        self.cat_shape.color = THECOLORS["orange"]
        self.cat_shape.elasticity = 1.0
        self.cat_shape.angle = 0.5
        direction = Vec2d(1, 0).rotated(self.cat_body.angle)
        self.space.add(self.cat_body, self.cat_shape)


    def create_car(self, x, y, r):
        inertia = pymunk.moment_for_circle(1, 0, 14, (0, 0))
        self.car_body = pymunk.Body(1, inertia)
        self.position = x, y
        self.car_shape = pymunk.Circle(self.car_body, 25)
        self.car_shape.color = THECOLORS["green"]
        self.car_shape.elasticity = 1.0
        self.car_body.angle = r
        self.car_body.friction = 0.01
        driving_direction = Vec2d(1, 0).rotated(self.car_body.angle)
        self.car_body.apply_impulse(driving_direction)
        self.space.add(self.car_body, self.car_shape)


    def turn(self,amount):
        """
        Turn the steeing left or right
        """
        noise = 0.05*(random.random()-0.5)
        self.steering += amount
        self.steering += noise
        self.steering = min(self.steering,+0.6)
        self.steering = max(self.steering,-0.6)


    def drive(self,throttle):
        """
        Drive the car forward or backward
        """
        driving_direction = self.get_driving_direction()
        self.car_body.velocity = 1000 * driving_direction * throttle
        self.car_body.angle += throttle*self.steering # Update angle

    def get_driving_direction(self):
        """
        Return the driving direction in global coordinates
        """
        return Vec2d(1, 0).rotated(self.car_body.angle)


    def get_reward(self,throttle,readings):
        readings = -5 + int(self.sum_readings(readings) / 10)
        return 4*throttle+readings


    def frame_step(self, action):
        if action == 0:  # Left
            self.rotation = -0.2
            self.throttle = 0

        elif action == 1:  # Right
            self.rotation = 0.2
            self.throttle = 0

        elif action == 2:  # Forward
            self.rotation = 0
            self.throttle = 0.4

        elif action == 3:  # Backward
            self.throttle = -0.4
            self.rotation = 0

        self.turn(self.rotation)
        self.drive(self.throttle)

        # Move obstacles.
        if self.num_steps % 100 == 0:
            self.move_obstacles()

        # Move cat.
        if self.num_steps % 5 == 0:
            self.move_cat()

        # Update the screen and stuff.
        self.screen.fill(THECOLORS["black"])
        draw(self.screen, self.space)
        self.space.step(1./10)
        if self.draw_screen:
            pygame.display.flip()
        self.clock.tick()

        # Get the current location and the readings there.
        x, y = self.car_body.position
        readings = self.get_sonar_readings(x, y, self.car_body.angle)

        # Set the reward.
        # Car crashed when any reading == 1
        if self.car_is_crashed(readings):
            self.crashed = True
            self.recover_from_crash()
            reward = -100
            done = True
        else:
            # Higher readings are better, so return the sum.
            reward = -5 + int(self.sum_readings(readings) / 10)
            done = False
        self.num_steps += 1

        return reward, readings, done


    def move_obstacles(self):
        # Randomly move obstacles around.
        for obstacle in self.obstacles:
            speed = random.randint(1, 5)
            direction = Vec2d(1, 0).rotated(self.car_body.angle + random.randint(-2, 2))
            obstacle.velocity = speed * direction


    def move_cat(self):
        speed = random.randint(10, 20)
        self.cat_body.angle -= random.randint(-1, 1)
        direction = Vec2d(1, 0).rotated(self.cat_body.angle)
        self.cat_body.velocity = speed * direction


    def car_is_crashed(self, readings):
        threshold = self.crash_distance * self.sonar_scale
        if readings[0] <= threshold or readings[1] <= threshold:
            return True
        return False


    def recover_from_crash(self):
        """
        We hit something, so recover.
        """
        driving_direction = self.get_driving_direction()
        x,y = self.car_body.position
        if x<0 or y<0 or x>width or y>height:
            self.car_body.position.x = 200
            self.car_body.position.y = 200
        self.crashed = False
        for i in range(10):
            self.screen.fill(THECOLORS["red"])
            draw(self.screen, self.space)


    def sum_readings(self, readings):
        """Sum the number of non-zero readings."""
        tot = 0
        for i in readings:
            tot += i
        return tot


    def get_sonar_readings(self, x, y, angle):
        readings = []
        """
        Instead of using a grid of boolean(ish) sensors, sonar readings
        simply return N "distance" readings, one for each sonar
        we're simulating. The distance is a count of the first non-zero
        reading starting at the object. For instance, if the fifth sensor
        in a sonar "arm" is non-zero, then that arm returns a distance of 5.
        """
        # Make our arms.
        arm_front = self.make_sonar_arm(x, y)
        arm_rear = arm_front

        # Rotate them and get readings.
        front = self.get_arm_distance(arm_front, x, y, angle, 0)
        rear = self.get_arm_distance(arm_rear, x, y, angle, math.pi)

        readings.append(self.sonar_scale*front)
        readings.append(self.sonar_scale*rear)

        if self.show_sensors:
            pygame.display.update()

        return readings


    def get_arm_distance(self, arm, x, y, angle, offset):
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
                    or rotated_p[0] >= width or rotated_p[1] >= height:
                return i  # Sensor is off the screen.
            else:
                obs = self.screen.get_at(rotated_p)
                if self.get_track_or_not(obs) != 0:
                    return i

            if self.show_sensors:
                pygame.draw.circle(self.screen, (255, 255, 255), (rotated_p), 2)

        # Return the distance for the arm.
        return i


    def make_sonar_arm(self, x, y):
        spread = 10  # Default spread.
        distance = 20  # Gap before first sensor.
        arm_points = []
        # Make an arm. We build it flat because we'll rotate it about the
        # center later.
        for i in range(1, 40):
            arm_points.append((distance + x + (spread * i), y))

        return arm_points


    def get_rotated_point(self, x_1, y_1, x_2, y_2, radians):
        # Rotate x_2, y_2 around x_1, y_1 by angle.
        x_change = (x_2 - x_1) * math.cos(radians) + \
            (y_2 - y_1) * math.sin(radians)
        y_change = (y_1 - y_2) * math.cos(radians) - \
            (x_1 - x_2) * math.sin(radians)
        new_x = x_change + x_1
        new_y = height - (y_change + y_1)
        return int(new_x), int(new_y)


    def get_track_or_not(self, reading):
        if reading == THECOLORS['black']:
            return 0
        else:
            return 1
