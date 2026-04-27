#!/usr/bin/env python3
# Imports
import pygame
import math
import random
from ytr_config import *
from ytr_classes import *

# Initialize
pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()
# 



# Start Music
pygame.mixer.music.load("audio/pygameboss.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# Game objects
boss = Boss(WIN_W * 0.8, WIN_H/2)
player = Player(WIN_W * 0.05, WIN_H/2)
controller = Controller()
view = View()
restart_button = Button(WIN_W * 0.4, WIN_H * 0.4, restart_img,2)
quit_button = Button(WIN_W * 0.4, WIN_W * 0.45, quit_img, 2)


# ---- VARIABLES ------
# Data
bullets = []
attacks = []
timers = {}

# Game state logic
run = True
game_over = False
phase2 = False

# Variable images
arena_img = arena

# Animation logic
num = 0
num2 = 0
num3 = 0
num4 = 0
transition_num = 0

# Attack logic
inf  = 0
radialusage = 0
spinning_radialusage = 0
blooming_radialusage = 0
starfallusage = 0
meteoractive = False
meteorusage = 0
choose_pos = True
lodge = False
javelinusage = 0
laseractive = False
pattern1usage = 0
pattern2usage = 0
pattern3usage = 0
current_attack = None
javelintimer = 300
transition = True
win_sound_delay = 0
lose_sound_delay = 0
attack_time = 0



while run:

    clock.tick(60)
    boss.hit = False

    # ================= INPUT =================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

            

    if current_attack == 1:
        if delay(timers,"radial",150):
            boss.radial(bullets,random.random()*5)
            radialusage += 1
        if radialusage > 12:
            radialusage = 0
            current_attack = None
    
    if current_attack == 2:
        if delay(timers,"spinning_radial",200):
            boss.spinning_radial(bullets,random.random()*5)
            spinning_radialusage += 1
        if spinning_radialusage > 10:
            spinning_radialusage = 0
            current_attack = None
    

    if current_attack == 3:
        if delay(timers,"blooming_radial",300):
            boss.blooming_radial(bullets,player)
            blooming_radialusage += 1
        if blooming_radialusage > 10:
            blooming_radialactive = False
            blooming_radialusage = 0
            current_attack = None

    if  current_attack == 7:
        
        if delay(timers,"starfall",200):
            boss.starfall(bullets,0.8 + random.random() * 0.2)
            starfallusage += 1
            if starfallusage == 2:
                starfall_laugh.play()
        if starfallusage > 30:
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
            
        if meteorusage > 12:
            meteoractive = False
            meteorusage = 0
            inf = 0
            timers.pop("meteor")

    if phase2 and delay(timers,'meteortimer',15000 + attack_time):
        choose_pos = True
        meteoractive = True
        





    if current_attack == 4:
        if delay(timers,"javelin",javelintimer):
            boss.javelin(bullets,player)
            javelinusage += 1
            
        if javelinusage > 20:
            lodge = True
            javelinusage = 0
            print("start delay")
            current_attack = None

    if lodge and not current_attack == 4 and not current_attack == 5 and not current_attack ==6:
        if delay(timers,"linger",3500):    
                bullets = [b for b in bullets if not b.lodged]
                print("end delay")
                lodge = False
                timers.pop("linger")


    if current_attack == 5:
        if delay(timers,"pattern1-1",400):
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

    if current_attack == 6:
        if delay(timers,"pattern2-1",1500):
            boss.spinning_radial(bullets,random.random()*5)
            pattern2usage += 1
            print("1")
        if delay(timers, "pattern2-2",500):
            boss.javelin(bullets,player)
            pattern2usage += 1
            print("2")
            
        if pattern2usage > 20:
            pattern2usage = 0
            current_attack = None
            if phase2:
                current_attack = 4
            else:
                lodge = True


    if current_attack==8:  
        if delay(timers,"pattern3-1",1000):
            boss.blooming_radial(bullets,player)
            pattern3usage += 1
            print("1")
        if delay(timers,"pattern3-2",500 + inf):
            boss.laser(bullets,player)
            inf = 9999
            laseractive = True
        if pattern3usage > 5:
            pattern3usage = 0
            laseractive = False
            inf = 0
            current_attack = None
    

    # Boss decision
    if delay(timers, "newattack", 2700 + attack_time) and current_attack is None and not phase2:
        current_attack = random.randint(1, 4)
        print(f"Chosen attack: {current_attack}")     
    
    if delay(timers, "newattack2", 1800 + attack_time) and current_attack is None and phase2:
        current_attack = random.randint(1, 8)
        print(f"Chosen attack: {current_attack}")     


    

    
            
            

    # Movement
    controller.move(player)
    controller.attack(player, attacks, timers)
    fire_attack(attacks, boss)

    # ================= DRAW =================
    if boss.hp <= 0 and not phase2:
        bullets = []
        
        while transition:
            if delay(timers,'transitiontime',3500):
                transition = False
            if delay(timers,"transitionframe",50):
                transition_num +=1
                arena_img = pygame.image.load(f"sprites/arenatransition/pixil-frame-{transition_num}.png")
                arena_img = pygame.transform.smoothscale(arena_img,(WIN_W,WIN_H))
                if transition_num == 69:
                    transition_num = 69
                if transition_num == 1:
                    pygame.mixer.music.load("audio/pygameboss2.mp3")
                    pygame.mixer.music.set_volume(0.5)
                    pygame.mixer.music.play(-1)
            screen.fill((0, 0, 0))
            screen.blit(arena_img, (0, 0))
            pygame.display.flip()
        if delay(timers,"aftertransition",1):
            laugh.play()
            transition = False
            phase2 = True
            boss_img = pygame.image.load(f"sprites/BOSS/BOSS - Stage 2 Frames/BOSS-S2-0.png").convert_alpha()
            javelintimer = 150
            arena_img = arena2
            boss_hit_img = pygame.image.load("sprites/BOSS/BOSS Stage 2 damaged.png")
            boss_hit_img = pygame.transform.smoothscale(boss_hit_img, (400, 400))  # resize if needed
            print("New Arena")
            player.x = WIN_W * 0.2
            player.y = WIN_H * 0.5            
            timers.pop("aftertransition")
            boss.hp = 1000
    
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
        boss_img = pygame.transform.scale(boss_img, (boss.size * 5*1.5, boss.size * 5*1.5))
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
            if not laseractive and b.is_laser:
                bullets.remove(b)
            view.draw_bullet(b, True)
            
        if laseractive:    
            if delay(timers,"laser",5000):
                laseractive = False
                beam.stop()
                print("Stops")
                print(laseractive)
                timers.pop("laser")   
                beam.stop()    


        attacks = [a for a in attacks if 0 <= a.p_x <= WIN_W and 0 <= a.p_y <= WIN_H]
        for a in attacks:
            view.draw_bullet(a, not a.hit)
        view.draw_player(player, hero_img)
        view.draw_boss(boss, boss_img)
        view.draw_boss_healthbar(boss)
        view.draw_player_healthbar(player)
        # Draw

        

    # Immunity
    if player.immune:
        if pygame.time.get_ticks() - player.immune_start_time >= IMMUNE_DURATION:
            player.immune = False

    # Check if Player or Boss is defeated, then prompts user with RESTART or QUIT Buttons
    if boss.hp < -7 or player.hp < 0:
        beam.stop()
        bullets = []
        game_over = True
        current_attack = None
        attack_time = 999999999
        pygame.mixer.music.stop()
        if boss.hp < 0 and player.hp>0:
            screen.blit(win_text_img,(310,70))
            if delay(timers,"winsound", win_sound_delay):
                win.play()
                win_sound_delay += 10000
        else:
            screen.blit(lose_text_img,(310,70))
            if delay(timers,"losesound", lose_sound_delay):
                lose.play()
                lose_sound_delay += 999999
        if quit_button.draw():
            break

        if restart_button.draw():
             # Music
            pygame.mixer.music.load("audio/pygameboss.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
            boss_hit_img = pygame.image.load("sprites/BOSS/BOSS damaged.png")
            boss_hit_img = pygame.transform.smoothscale(boss_hit_img, (400, 400))  # resize if needed
            # Game objects
            boss = Boss(WIN_W * 0.8, WIN_H/2)
            player = Player(WIN_W * 0.05, WIN_H/2)
            controller = Controller()
            view = View()
            restart_button = Button(WIN_W * 0.4, WIN_H * 0.4, restart_img,2)
            quit_button = Button(WIN_W * 0.4, WIN_W * 0.45, quit_img, 2)

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
            transition_num=0
            starfallusage = 0
            meteoractive = False
            meteorusage = 0
            choose_pos = True
            javelinactive = False
            lodge = False
            transition = True
            javelinusage = 0
            laseractive = False
            pattern1active = False
            pattern1usage = 0
            pattern2active = False
            pattern2usage = 0
            pattern3active = False
            pattern3usage = 0
            current_attack = None
            javelintimer = 300
            attack_time = 0
            win_sound_delay = 0
            lose_sound_delay = 0
    pygame.display.flip()

pygame.quit()
    


            



