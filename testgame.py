#!/usr/bin/env python3
import pygame
import math
import random
import time

#Initialize pygame
pygame.init()
WIN_W, WIN_H = 960, 720
screen = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("Hell")
run = True
clock = pygame.time.Clock()
count = 0


class Player:

    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.hp = 100
        self.size = 8
        self.movespeed = 4
        self.alive = True

class Controller:

    def move(self, player):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            player.x -= player.movespeed
        if keys[pygame.K_d]:
            player.x += player.movespeed
        if keys[pygame.K_w]:
            player.y -= player.movespeed
        if keys[pygame.K_s]:
            player.y += player.movespeed

#class View:

   # def __init__

class Boss:

    def __init__(self,X,Y):
        self.X = X
        self.Y = Y
        self.HP = 1000
        self.SIZE = 30
    
    #def attack1(self):

class Projectile:

    def __init__(self,p_speed,p_size,p_damage,p_x,p_y):
        self.p_speed = p_speed  
        self.p_size = p_size
        self.p_damage = p_damage
        self.p_x = p_x
        self.p_y = p_y
    def create_projectile(self):
        self.p_x += self.p_speed
        self.p_y += self.p_speed
        pygame.draw.circle(screen, (50, 200, 50), (self.p_x,self.p_y), self.p_size)

class BossProjectile(Projectile):
    
    def player_collision(self):
        dist = math.hypot(instance.x - self.p_x, instance.y - self.p_y)
        if dist < (0.9*self.p_size + instance.size):
            pygame.quit()
            run = False


    #If player get hits
   # def hit_player(self):

        

    

    

instance = Player(50,20)
controller = Controller()
#base_projectile = Projectile(2,10,5,50,50)
boss_proj = BossProjectile(2,10,5,50,50)

while run:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
         run = False
   
    controller.move(instance)
    screen.fill((0, 0, 0))  # clear screen
    pygame.draw.circle(screen, (50, 200, 50), (instance.x,instance.y), 8)
    boss_proj.create_projectile()
    boss_proj.player_collision()
    pygame.display.flip()
    if pygame.time.get_ticks() >= 30000:
        pygame.quit()
        run = False
       