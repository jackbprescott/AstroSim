#AstroSim
#Copyright Jack Prescott
#March 11, 2018
#Test 5

import pygame
import sys
import math
import csv
from pygame.locals import *

# Constants
PINK = (1,2,3)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLACK = (0,0,0)
WIDTH = 1440
HEIGHT = 900
METERS_PER_PIXEL = 1e10
TIMESTEP = 3600*24
GRAV_CONST = TIMESTEP * 6.7e-11
ZOOM = 20
HOR_SHIFT = 0
VERT_SHIFT = 0

#Setup Screen
screen = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
screen.fill(BLACK)

#Global Variables
body_list = []
checking_stability = False
first_crossing = False
second_crossing = False
sign = 0
count = 0
alpha_sum = 0
alpha_list = []
alpha_deltas_list = [0.0]
draw = True
strobo_orbit_time = 0
first_orbit = True
strobo_distances = []
strobo_count = 0

def distance(body1, body2):
    #Get distance between two bodies
    return math.sqrt( (body1.x - body2.x)**2 + (body1.y - body2.y)**2 + (body1.z - body2.z)**2 )

def sign_of(x):
    if x < 0:
        return -1
    else:
        return 1

class Body:
    #Class body
    def __init__(self, isStar, x, y, dx, dy, rad, mass, z=0, dz=0) :
        #Initiate the body
        self.isStar = isStar
        self.x = x + WIDTH/2
        self.y = y + HEIGHT/2
        self.z = z
        self.dx = dx
        self.dy = dy
        self.dz = dz
        self.mass = mass
        self.rad = rad
        if isStar:
            self.color = (255, 255, 255)
        else:
            self.color = (0, 255, 0)
        self.thickness = 1
        self.screen = screen
        body_list.append(self)

    def display(self):
        #Draw the body
        pygame.draw.circle(screen, self.color, (int(ZOOM * self.x / METERS_PER_PIXEL) + WIDTH / 2 - HOR_SHIFT, int(ZOOM * self.y / METERS_PER_PIXEL) + HEIGHT / 2 - VERT_SHIFT), self.rad, self.thickness)

    def move(self):
        #Update position
        self.x += self.dx * TIMESTEP
        self.y += self.dy * TIMESTEP
        self.z += self.dz * TIMESTEP

    def accelerate(self, i):
        #Update velocity
        for j in range(i, len(body_list)):
            body = body_list[j]
            x_acc = (self.x - body.x) * GRAV_CONST / distance(self, body)**3
            y_acc = (self.y - body.y) * GRAV_CONST / distance(self, body)**3
            z_acc = (self.z - body.z) * GRAV_CONST / distance(self, body)**3
            self.dx += -x_acc * body.mass
            body.dx += x_acc * self.mass
            self.dy += -y_acc * body.mass
            body.dy += y_acc * self.mass
            self.dz += -z_acc * body.mass
            body.dz += z_acc * self.mass

def create_bodies():
    #Create all bodies, automatically added to body list
    #Circular orbits:
    #star1 = Body(isStar = True, x = 0, y = -1.49e11/2, dx = -4.2409e4/2, dy = 0, rad = 3, mass = 2e30)
    #star2 = Body(isStar = True, x = 0, y = 1.49e11/2, dx = 4.2409e4/2, dy = 0, rad = 3, mass = 2e30)
    #dm1 = Body(isStar=False, x=1.49e11/1.2, y=1.8e12 / 2, dx=0 / 2, dy=-4.2409e4, rad=3, mass=2e30)
    star1 = Body(isStar = True, x = 0, y = -3e11/2, dx = -1e4/2, dy = 0, rad = 3, mass = 2e30)
    star2 = Body(isStar = True, x = 0, y = 3e11/2, dx = 1e4/2, dy = 0, rad = 3, mass = 2e30)
    dm1 = Body(isStar=False, x=-1e12, y=-2e11 / 2, dx=4.2409e4, dy=0, rad=3, mass=2e29)

def calculate_alpha(body1, body2):
    #Check alpha Equation between two masses
    K = (body1.mass * (body1.dx**2 + body1.dy**2) + body2.mass * (body2.dx**2 + body2.dy**2)) / 2
    U = -6.7e-11 * body1.mass * body2.mass / distance(body1, body2)
    return -(2 * K)/U - 1

def check_stability():
    global checking_stability
    global count
    global alpha_sum
    global first_crossing
    global second_crossing
    global sign
    global alpha_list
    global alpha_deltas_list
    global strobo_distances
    global strobo_orbit_time
    global first_orbit
    
    new_sign = sign_of(body_list[1].x - body_list[0].x)

    if checking_stability:
        count += 1
        alpha_sum += calculate_alpha(body_list[0], body_list[1])

    if new_sign != sign and not first_crossing:
        checking_stability = True
        count += 1
        alpha_sum += calculate_alpha(body_list[0], body_list[1])
        sign = new_sign
        first_crossing = True
    elif new_sign != sign and not second_crossing:
        second_crossing = True
        sign = new_sign
        count += 1
    elif new_sign != sign:
        alpha = alpha_sum/count
        if first_orbit:
            strobo_orbit_time = count
            first_orbit = False
            strobo_distances.append(distance(body_list[0], body_list[1]))
        if len(alpha_list) != 0:
            alpha_deltas_list.append(alpha - alpha_list[-1])
        alpha_list.append(alpha)
        count = 0
        alpha = 0
        alpha_sum = 0
        first_crossing = False
        second_crossing = False
        checking_stability = False

def strobo_orbit_tracker():
    global strobo_count
    global strobo_orbit_tracker
    global strobo_distances
    global strobo_orbit_time
    global first_orbit
    
    if not first_orbit:
        strobo_count += 1
        if strobo_count == strobo_orbit_time:
            strobo_distances.append(distance(body_list[0], body_list[1]))
            strobo_count = 0


#Create bodies and set running to true
create_bodies()
running = True

sign = sign_of(body_list[1].x - body_list[0].x)

while running:
    #Draw and update game
    if draw:
        screen.fill(BLACK)
        
        i = 0
        x_sum = 0
        y_sum = 0
        num_stars = 0
        
        for body in body_list:
            body.move()
            body.accelerate(i + 1)
            body.display()
            i += 1
            
            if body.isStar:
                x_sum += body.x
                y_sum += body.y
                num_stars += 1

            HOR_SHIFT = int(ZOOM * x_sum / METERS_PER_PIXEL / num_stars)
            VERT_SHIFT = int(ZOOM * y_sum / METERS_PER_PIXEL / num_stars)
                
        pygame.display.update()
    else:
        i = 0
        for body in body_list:
            body.move()
            body.accelerate(i + 1)
            body.display()
            i += 1
            
    #Run functional to track alpha
    check_stability()

    #Keep track of stroboscopic distances
    strobo_orbit_tracker()

    #Check keystrokes
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_EQUALS:
                ZOOM += 1
            if event.key == pygame.K_MINUS:
                if ZOOM > 1:
                    ZOOM -= 1
                else:
                    ZOOM -= 0.05 
            if event.key == pygame.K_d:
                draw = not draw

        if event.type == pygame.QUIT:
            file = open("alpha_deltas.txt", "w")
            file.write(', '.join([str(value) for value in alpha_deltas_list]))
            file.close()
            file = open("strobo_distances.txt", "w")
            file.write(', '.join([str(value) for value in strobo_distances]))
            file.close()
            running = False
