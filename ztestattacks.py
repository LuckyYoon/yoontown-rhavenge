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
arena_img = arena
# Animation
num = 0
phase2 = False
beam_over = False
attack7active = False
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
                boss.radial(bullets, random.random()*5)

            if event.key == pygame.K_2:
                print("Attack 2")
                boss.spinning_radial(bullets, random.random()*5)

            if event.key == pygame.K_3:
                print("Attack 3")
                boss.blooming_radial(bullets, player)

            if event.key == pygame.K_4:
                print("Attack 4")
                boss.starfall(bullets,0.8 + random.random() * 0.2)

            if event.key == pygame.K_5:
                print("Attack 5")
                boss.meteor(bullets,(0.3 + random.random()*0.3)*WIN_H)

            if event.key == pygame.K_6:
                print("Attack 6")
                boss.javelin(bullets,player)
            
            if event.key == pygame.K_7:
                print("Attack 7")
                attack7active = True
                boss.attack7(bullets,player)


            if event.key == pygame.K_8:
                print("Attack 8 (spam test)")
                for _ in range(10):
                    boss.radial(bullets, random.random()*5)
            
            

    # Movement
    controller.move(player)
    controller.attack(player, attacks, timers)
    fire_attack(attacks, boss)

    # ================= DRAW =================
    if boss.hp <= 500 and not phase2:
        arena_img = arena2
        print("New Arena")
        phase2 = True
    if boss.hit == True:
        boss_img = boss_hit_img
    screen.fill((0, 0, 0))
    screen.blit(arena_img, (0, 0))

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
        if not attack7active and b.is_laser:
            bullets.remove(b)
        view.draw_bullet(b, True)
        
    if attack7active:    
        if delay(timers,"attack7",5000):
            attack7active = False
            print("Stops")
            print(attack7active)
            timers.pop("attack7")        

    
    

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