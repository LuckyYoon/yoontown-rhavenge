#!/usr/bin/env python3
# Imports
import pygame
import math
import random
from zconfig import *


# Initialize
pygame.init()
pygame.mixer.init()

clock = pygame.time.Clock()
run = True

# Music
pygame.mixer.music.load("audio/pygameboss.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

from zclasses import *
# Game objects
boss = Boss(800, WIN_H/2)
player = Player(50, 20)
controller = Controller()
view = View()

# Data
bullets = []
attacks = []
timers = {}

# Animation
num = 0


while run:
    clock.tick(60)
    boss.hit = False

    # ================= INPUT =================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:

            # Manual attack testing
            if event.key == pygame.K_1:
                print("Attack 1")
                boss.attack1(bullets, random.random()*5)

            if event.key == pygame.K_2:
                print("Attack 2")
                boss.attack2(bullets, random.random()*5)

            if event.key == pygame.K_3:
                print("Attack 3")
                boss.attack3(player, bullets)

            if event.key == pygame.K_4:
                print("Attack 4")
                boss.attack4(bullets)

            if event.key == pygame.K_5:
                print("Attack 5")
                boss.attack5(bullets,(0.2+random.random()*0.6)*WIN_W)

            if event.key == pygame.K_6:
                print("Attack 6")
                boss.attack6(bullets,player)
            
            if event.key == pygame.K_7:
                print("Attack 7")
                boss.attack7(bullets,boss)




            if event.key == pygame.K_8:
                print("Attack 8 (spam test)")
                for _ in range(10):
                    boss.attack1(bullets, random.random()*5)
            
            

    # Movement
    controller.move(player)
    controller.attack(player, attacks, timers)
    fire_attack(attacks, boss)

    # ================= DRAW =================
    screen.fill((0, 0, 0))
    screen.blit(arena, (0, 0))

    # Animation update
    if delay(timers, "newframe", 200):
        boss_img = pygame.image.load(f"sprites/BOSS/BOSS - frames/BOSS{num}.png").convert_alpha()
        boss_img = pygame.transform.scale(boss_img, (boss.size * 3, boss.size * 5))

        hero_img = pygame.image.load(f"sprites/HERO/HERO - frames/HERO{num}.png").convert_alpha()
        hero_img = pygame.transform.scale(hero_img, (player.size * 16, player.size * 16))

        num = (num + 1) % 4

    # Clamp player
    player.x = max(0, min(WIN_W - 20, player.x))
    player.y = max(0, min(WIN_H - 20, player.y))

    # Move bullets
    fire_bullet(bullets, player)

    # Draw
    

    # Bullet cleanup
    bullets = [b for b in bullets if 0 <= b.p_x <= WIN_W and 0 <= b.p_y <= WIN_H or b.is_laser]
    for b in bullets:
        view.draw_bullet(b, True)


    attacks = [a for a in attacks if 0 <= a.p_x <= WIN_W and 0 <= a.p_y <= WIN_H]
    for a in attacks:
        view.draw_bullet(a, not a.hit)

    view.draw_player(player, hero_img)
    view.draw_boss(boss, boss_img)
    view.draw_boss_healthbar(boss)
    view.draw_player_healthbar(player)
    # Immunity
    if player.immune:
        if pygame.time.get_ticks() - player.immune_start_time >= IMMUNE_DURATION:
            player.immune = False

    pygame.display.flip()

pygame.quit()