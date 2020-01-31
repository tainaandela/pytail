import random

import pygame
import pymunk
import pymunk.pygame_util
from pygame.color import *
from pygame.color import THECOLORS
from pygame.key import *
from pygame.locals import *
from pymunk import Vec2d

from .constants import SCREEN_HEIGHT, SCREEN_WIDTH

# http://www.pymunk.org/en/latest/pymunk.pyglet_util.html


class Engine(object):
    '''
    This class implements a simple scene in which there is a static platform andd
    ball bounce around.
    '''
    def __init__(self):

        # Space
        self.space = pymunk.Space()
        self.space.gravity = (0.0, -900.0)

        # Physics
        # Time step
        self.dt = 1.0 / 60.0
        # Number of physics steps per screen frame
        self.physics_steps_per_frame = 1

        # pygame
        pygame.init()
        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            HWSURFACE | DOUBLEBUF | RESIZABLE | SCALED
        )
        self.clock = pygame.time.Clock()

        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)

        self.font = pygame.font.SysFont(pygame.font.get_default_font(), 15)

        # Balls that exist in the world
        self.balls = []
        self.left = 100
        self.open_x = 30

        self.static_lines = []
        self.create_static_scenery()

        # Execution control and time until the next ball spawns
        self.running = True

        self.ticks_to_next_ball = 10
        self.texts = []

        self.bounce = False

        # debug variables
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.inc = 5

    def clear_screen(self):
        '''
        Clears the screen.
        :return: None
        '''
        self.screen.fill(THECOLORS['black'])

    def flipy(self, y):
        '''Small hack to convert chipmunk physics to pygame coordinates'''
        return -y + SCREEN_HEIGHT

    def create_static_scenery(self):
        '''
        Create the static bodies.
        :return: None
        '''
        y_incline = 70
        top = 60
        mid = SCREEN_WIDTH / 2
        w = mid - self.left
        bottom_gap = 150
        self.right = mid + w
        line_width = 1

        self.space.remove(self.static_lines)

        self.static_lines = [
            # left vertical line
            pymunk.Segment(
                pymunk.Body(body_type=pymunk.Body.STATIC),
                (self.left, self.flipy(top)),
                (self.left, self.flipy(SCREEN_HEIGHT - bottom_gap)),
                line_width
            ),
            # left base
            pymunk.Segment(
                pymunk.Body(body_type=pymunk.Body.STATIC),
                (self.left, self.flipy(SCREEN_HEIGHT-bottom_gap)),
                (mid-self.open_x, self.flipy(SCREEN_HEIGHT-bottom_gap+y_incline)),
                line_width
            ),
            # right vertical line
            pymunk.Segment(
                pymunk.Body(body_type=pymunk.Body.STATIC),
                (self.right, self.flipy(top)),
                (self.right, self.flipy(SCREEN_HEIGHT-bottom_gap)),
                line_width
            ),
            # right base
            pymunk.Segment(
                pymunk.Body(body_type=pymunk.Body.STATIC),
                (self.right, self.flipy(SCREEN_HEIGHT-bottom_gap)),
                (mid+self.open_x, self.flipy(SCREEN_HEIGHT-bottom_gap+y_incline)),
                line_width
            ),
        ]

        for line in self.static_lines:
            # line.elasticity = 0.35
            line.elasticity = 0.1
            # line.friction = 10.5
        self.space.add(self.static_lines)

    def drop_ball(self, x, y, radius=25, mass=100):
        '''
        Create a ball.
        :return:
        '''
        inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
        body = pymunk.Body(mass, inertia)
        body.position = x, y
        shape = pymunk.Circle(body, radius, (0, 0))
        shape.elasticity = 0.95
        shape.friction = 0.9
        self.space.add(body, shape)
        self.balls.append(shape)

    def project_ball(self, x, y, radius=25, mass=100, force=90000, text=None):
        '''
        Project a ball.
        :return:
        '''
        if text and hasattr(self, 'font'):
            pos_x = x - 60
            if force < 0:
                pos_x = x + 20
            self.texts.append((
                self.font.render(text, 2, THECOLORS['white']),
                (pos_x, self.flipy(y)),
            ))

        inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
        body = pymunk.Body(mass, inertia)
        # body.angular_velocity = 100
        body.position = x, y
        body.apply_impulse_at_local_point((force, 0), (0, 0))
        # apply_force_at_world_point
        shape = pymunk.Circle(body, radius, (0, 0))
        # shape.collision_type = 1
        shape.elasticity = 0.95
        # shape.friction = 10.9
        self.space.add(body, shape)
        self.balls.append(shape)

    def update_balls(self):
        '''
        Create/remove balls as necessary. Call once per frame only.
        :return: None
        '''
        self.ticks_to_next_ball -= 1
        if self.ticks_to_next_ball <= 0:
            # x = random.randint(115, 350)
            # y = random.randint(400, 500)
            # radius = random.randint(5, 30)
            # mass = random.randint(10, 50)
            # self.drop_ball(x, y, radius=radius, mass=mass)
            x = self.left
            y = random.randint(150, 400)
            radius = random.randint(10, 20)
            mass = 100.0
            force = 90000
            if random.randint(1, 20) % 2 == 0:
                x = self.right
                force *= -1
            self.drop_ball(
                random.randint(115, 350),
                random.randint(400, 500),
                random.randint(10, 30),
                mass,
            )
            self.project_ball(x, y, radius=radius, mass=mass, force=force, text='another one')
            self.ticks_to_next_ball = 100
        # Remove balls that fall below vertical threshold
        for ball in self.balls:
            pos_y = 20
            if ball.body.position.y < pos_y:
                self.space.remove(ball, ball.body)
                self.balls.remove(ball)

    # -------------------------------------------------------------------------

    def on_event(self, event):
        '''
        Handle game and events like keyboard input.
        Call once per frame only.
        :return: None
        '''
        if event.type == QUIT:
            self.running = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                self.running = False
            elif event.key == K_p:
                pygame.image.save(self.screen, 'screen_shot.png')
            elif event.key == K_f:
                pygame.display.toggle_fullscreen()
            elif event.key == K_SPACE:
                self.bounce = not self.bounce
                if self.bounce:
                    self.open_x = 0
                else:
                    self.open_x = 30
                self.create_static_scenery()
            elif event.key == K_UP:
                print('Event K_UP')
            elif event.key == K_DOWN:
                print('Event K_DOWN')
            elif event.key == K_RIGHT:
                print('Event K_RIGHT')
                self.x1 += self.inc
            elif event.key == K_LEFT:
                print('Event K_LEFT')
                self.x1 -= self.inc
        elif event.type == MOUSEBUTTONUP:
            print('Mouse Up')
        elif event.type == MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            print(f'Mouse Down x = {pos[0]} y = {pos[1]}')

    '''
    coordinates system
    | y = 0
    |
    |
    | y = height
    | x = 0
    |_________________x = screen width
    '''

    def debug_draw(self):
        self.inc = 10
        # axis
        p1 = Vec2d(0, SCREEN_HEIGHT-SCREEN_HEIGHT/2)
        p2 = Vec2d(SCREEN_WIDTH, SCREEN_HEIGHT-SCREEN_HEIGHT/2)
        p3 = Vec2d(SCREEN_WIDTH/2, 0)
        p4 = Vec2d(SCREEN_WIDTH/2, SCREEN_HEIGHT)
        pygame.draw.lines(self.screen, THECOLORS['white'], False, [p1, p2])
        pygame.draw.lines(self.screen, THECOLORS['white'], False, [p3, p4])
        print(f'x1 = {self.x1} y1 = {self.y1}  x2 = {self.x2}  y2 = {self.y2} ')

        # todo try putting quads here
        # https://github.com/Fudge/gltail/blob/master/lib/gl_tail/engine.rb

        p1 = Vec2d(self.left-80, 60)
        p2 = Vec2d(self.left, 60)
        p3 = Vec2d(self.left, 330)
        p4 = Vec2d(self.left-80, 330)
        # pygame.draw.lines(self.screen, THECOLORS['white'], False, [p1, p2, p3, p4])

        pygame.draw.rect(
            self.screen,
            THECOLORS['gray'],
            [self.left-49, 60, 50, 330], 1)
        pygame.draw.rect(
            self.screen,
            THECOLORS['gray'],
            [self.left-49+490, 60, 50, 330], 1)

    def on_loop(self):
        # 1) update
        self.update_balls()

        # 2) clear
        self.clear_screen()

        # 3) draw objects
        self.debug_draw()
        self.space.debug_draw(self.draw_options)

        self.screen.blit(
            self.font.render(
                f'fps: {self.clock.get_fps()}', 1, THECOLORS['black']
            ),
            (10, 450)
        )
        for text, pos in self.texts:
            self.screen.blit(text, pos)

        # 4)  flip
        pygame.display.flip()

        # Delay fixed time between frames
        self.clock.tick(50)

        pygame.display.set_caption(f'fps: {str(self.clock.get_fps())}')

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        while self.running:
            # Progress time forward
            for _ in range(self.physics_steps_per_frame):
                self.space.step(self.dt)
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
        self.on_cleanup()
