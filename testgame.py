#!/usr/bin/env python3
import pygame
import math
import random
import time

#Initialize pygame
pygame.init()
WIN_W, WIN_H    = 960, 720
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


instance = Player(50,20)
controller = Controller()
while run:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
         run = False
    controller.move(instance)
    screen.fill((0, 0, 0))  # clear screen
    pygame.draw.circle(screen, (50, 200, 50), (instance.x,instance.y), 8)
    pygame.display.flip()
    if pygame.time.get_ticks() >= 2000:
        pygame.quit()
        run = False
       