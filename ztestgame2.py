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
game_over = False

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
restart_button = Button(370,200,restart_img,2)
quit_button = Button(370,400, quit_img,2)

# Data
bullets = []
attacks = []

timers = {}
arena_img = arena

# Animation
num = 0
num2 = 0
num3 = 0
num4 = 0
inf  = 0
phase2 = False
radialactive = False
radialusage = 0
spinning_radialactive = False
spinning_radialusage = 0
blooming_radialactive = False
blooming_radialusage = 0
starfallactive = False
starfallusage = 0
meteoractive = False
meteorusage = 0
choose_pos = True
javelinactive = False
lodge = False
javelinusage = 0
attack7active = False
pattern1active = False
pattern1usage = 0
pattern2active = False
pattern2usage = 0
pattern3active = False
pattern3usage = 0
current_attack = None
javelintimer = 300
movelist = [radialactive,spinning_radialactive,blooming_radialactive,javelinactive]




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
                radialactive = True
                
            if event.key == pygame.K_2:
                print("Attack 2")
                spinning_radialactive = True

            if event.key == pygame.K_3:
                print("Attack 3")
                blooming_radialactive = True
            
            if event.key == pygame.K_4:
                print("Attack 4")
                starfallactive = True

            if event.key == pygame.K_5:
                print("Attack 5")
                meteoractive = True
                choose_pos = True

            if event.key == pygame.K_6:
                print("Attack 6")
                javelinactive = True
    
            if event.key == pygame.K_8:
                print("Pattern1")
                pattern1active = True
            if event.key == pygame.K_9:
                print("Pattern2")
                pattern2active = True
            if event.key == pygame.K_0:
                print("Pattern3")
                pattern3active = True

            

    if radialactive or current_attack == 1:
        if delay(timers,"radial",200):
            boss.radial(bullets,random.random()*5)
            radialusage += 1
        if radialusage > 10:
            radialactive = False
            radialusage = 0
            current_attack = None
    
    if spinning_radialactive or current_attack ==2:
        if delay(timers,"spinning_radial",200):
            boss.spinning_radial(bullets,random.random()*5)
            spinning_radialusage += 1
        if spinning_radialusage > 10:
            spinning_radialactive = False
            spinning_radialusage = 0
            current_attack = None
    

    if blooming_radialactive or current_attack ==3:
        if delay(timers,"blooming_radial",200):
            boss.blooming_radial(bullets,player)
            blooming_radialusage += 1
        if blooming_radialusage > 4:
            blooming_radialactive = False
            blooming_radialusage = 0
            current_attack = None

    if starfallactive or current_attack == 7:
        if delay(timers,"starfall",200):
            boss.starfall(bullets,0.8 + random.random() * 0.2)
            starfallusage += 1
        if starfallusage > 30:
            starfallactive = False
            starfallusage = 0
            current_attack = None

    if meteoractive:
        if choose_pos:
            pos = WIN_H * (0.2 + random.random() * 0.6)
            choose_pos = False
            inf = 1500
            boss.meteor(bullets, pos * (0.9 + random.random() * 0.3),True)
        if delay(timers,"meteor",200 + inf):
            inf = 0
            boss.meteor(bullets, pos * (0.9 + random.random() * 0.3),False)
            meteorusage += 1
            
        if meteorusage > 10:
            meteoractive = False
            meteorusage = 0
            inf = 0
            timers.pop("meteor")

    if phase2 and delay(timers,'meteortimer',15000):
        meteoractive = True
        choose_pos = True





    if javelinactive or current_attack == 4:
        if delay(timers,"javelin",javelintimer):
            boss.javelin(bullets,player)
            javelinusage += 1
            
        if javelinusage > 20:
            lodge = True
            javelinactive = False
            javelinusage = 0
            print("start delay")
            current_attack = None

    if lodge and not javelinactive:
        if delay(timers,"linger",3000):    
                bullets = [b for b in bullets if not b.lodged]
                print("end delay")
                lodge = False
                timers.pop("linger")


    if pattern1active or current_attack == 5:
        if delay(timers,"pattern1-1",500):
            boss.radial(bullets,random.random()*5)
            pattern1usage += 1
            print("1")
        if delay(timers, "pattern1-2",1500):
            boss.javelin(bullets,player)
            pattern1usage += 1
            print("2")
        if pattern1usage > 20:
            pattern1active = False
            pattern1usage = 0
            current_attack = None

    if pattern2active or current_attack == 6:
        if delay(timers,"pattern2-1",1500):
            boss.spinning_radial(bullets,random.random()*5)
            pattern2usage += 1
            print("1")
        if delay(timers, "pattern2-2",500):
            boss.javelin(bullets,player)
            pattern2usage += 1
            print("2")
            
        if pattern2usage > 20:
            pattern2active = False
            pattern2usage = 0
            current_attack = None
            if phase2:
                current_attack = 4
            else:
                lodge = True


    if pattern3active or current_attack==8:  
        if delay(timers,"pattern3-1",1000):
            boss.blooming_radial(bullets,player)
            pattern3usage += 1
            print("1")
        if delay(timers,"pattern3-2",500 + inf):
            boss.attack7(bullets,player)
            inf = 9999
            attack7active = True
        if pattern3usage > 5:
            pattern3active = False
            pattern3usage = 0
            attack7active = False
            inf = 0
            current_attack = None
    

    # Boss Decision
    if delay(timers, "newattack", 3000) and current_attack is None and not phase2:
        current_attack = random.randint(1, 4)
        print(f"Chosen attack: {current_attack}")     
    
    if delay(timers, "newattack2", 2000) and current_attack is None and phase2:
        current_attack = random.randint(1, 8)
        print(f"Chosen attack: {current_attack}")     


    

    
            
            

    # Movement
    controller.move(player)
    controller.attack(player, attacks, timers)
    fire_attack(attacks, boss)

    # ================= DRAW =================
    if boss.hp <= 500 and not phase2:
        javelintimer = 150
        arena_img = arena2
        print("New Arena")
        phase2 = True
        pygame.mixer.music.load("audio/pygameboss2.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)     
    if boss.hit == True:
        boss_img = boss_hit_img
    screen.fill((0, 0, 0))
    screen.blit(arena_img, (0, 0))

    # Animation update
    if delay(timers, "newframeboss", 200) and not phase2:
        boss_img = pygame.image.load(f"sprites/BOSS/BOSS - frames/BOSS{num}.png").convert_alpha()
        boss_img = pygame.transform.scale(boss_img, (boss.size * 3, boss.size * 5))

        num = (num + 1) % 4

    if delay(timers, "newframehero", 200):
        hero_img = pygame.image.load(f"sprites/HERO/HERO - frames/HERO{num2}.png").convert_alpha()
        hero_img = pygame.transform.scale(hero_img, (player.size * 16, player.size * 16))

        num2 = (num2 + 1) % 4

    if delay(timers, "newframearena", 50) and phase2:
        arena_img = pygame.image.load(f"sprites/ARENA Frames/pixil-frame-{num3}.png").convert_alpha()
        arena_img = pygame.transform.scale(arena_img,(WIN_W,WIN_H))
        num3 = (num3 + 1) % 12

    if delay(timers, "newframeboss2", 150) and phase2:
        boss_img = pygame.image.load(f"sprites/BOSS/BOSS - Stage 2 Frames/BOSS-S2-{num4}.png").convert_alpha()
        boss_img = pygame.transform.scale(boss_img, (boss.size * 5*1.3, boss.size * 5*1.3))
        num4 = (num4 + 1) % 4



    # Clamp player
    player.x = max(0, min(WIN_W - 20, player.x))
    player.y = max(0, min(WIN_H - 20, player.y))

    # Move bullets
    fire_bullet(bullets, player)

    if not game_over: 
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
                beam.stop()    


        attacks = [a for a in attacks if 0 <= a.p_x <= WIN_W and 0 <= a.p_y <= WIN_H]
        for a in attacks:
            view.draw_bullet(a, not a.hit)


        # Draw

        view.draw_player(player, hero_img)
        view.draw_boss(boss, boss_img)
        view.draw_boss_healthbar(boss)
        view.draw_player_healthbar(player)

    # Immunity
    if player.immune:
        if pygame.time.get_ticks() - player.immune_start_time >= IMMUNE_DURATION:
            player.immune = False

    # Check if Player or Boss is defeated, then prompts user with RESTART or QUIT Buttons
    if boss.hp < 0:
        game_over = True
        screen.blit(win_text_img,(310,70))
        if quit_button.draw():
            break

        if restart_button.draw():
            pygame.mixer.music.load("audio/pygameboss.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
            boss = Boss(800, WIN_H/2)
            player = Player(50, 20)
            controller = Controller()
            view = View()
            restart_button = Button(370,200,restart_img,2)
            quit_button = Button(370,400, quit_img,2)

            # Data
            bullets = []
            attacks = []
            game_over = False
            timers = {}
            arena_img = arena

            # Animation
            num = 0
            num2 = 0
            num3 = 0
            num4 = 0
            inf  = 0
            phase2 = False
            radialactive = False
            radialusage = 0
            spinning_radialactive = False
            spinning_radialusage = 0
            blooming_radialactive = False
            blooming_radialusage = 0
            starfallactive = False
            starfallusage = 0
            meteoractive = False
            meteorusage = 0
            choose_pos = True
            javelinactive = False
            lodge = False
            javelinusage = 0
            attack7active = False
            pattern1active = False
            pattern1usage = 0
            pattern2active = False
            pattern2usage = 0
            pattern3active = False
            pattern3usage = 0
            current_attack = None
            javelintimer = 300
            movelist = [radialactive,spinning_radialactive,blooming_radialactive,javelinactive]

    if player.hp < 0:
        game_over = True

        screen.blit(lose_text_img,(310,70))
        if quit_button.draw():
            break

        if restart_button.draw():
            pygame.mixer.music.load("audio/pygameboss.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
            boss = Boss(800, WIN_H/2)
            player = Player(50, 20)
            controller = Controller()
            view = View()
            restart_button = Button(370,200,restart_img,2)
            quit_button = Button(370,400, quit_img,2)

            # Data
            bullets = []
            attacks = []
            game_over = False
            timers = {}
            arena_img = arena

            # Animation
            num = 0
            num2 = 0
            num3 = 0
            num4 = 0
            inf  = 0
            phase2 = False
            radialactive = False
            radialusage = 0
            spinning_radialactive = False
            spinning_radialusage = 0
            blooming_radialactive = False
            blooming_radialusage = 0
            starfallactive = False
            starfallusage = 0
            meteoractive = False
            meteorusage = 0
            choose_pos = True
            javelinactive = False
            lodge = False
            javelinusage = 0
            attack7active = False
            pattern1active = False
            pattern1usage = 0
            pattern2active = False
            pattern2usage = 0
            pattern3active = False
            pattern3usage = 0
            current_attack = None
            javelintimer = 300
            movelist = [radialactive,spinning_radialactive,blooming_radialactive,javelinactive]
    
    
    pygame.display.flip()

pygame.quit()
    


            



