import pygame
import math
import random

# Initialize
pygame.init()
WIDTH, HEIGHT = 960, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bullet Hell Bossfight")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("arial", 48)
small_font = pygame.font.SysFont("arial", 28)

# Load images
bullet_img = pygame.image.load("sprites/BOSS/BOSS - attacks/Boss small attack.png").convert_alpha()
bullet_img = pygame.transform.scale(bullet_img, (16, 16))

boss_img = pygame.image.load("sprites/BOSS/BOSS - frames/BOSS1.png").convert_alpha()
boss_img = pygame.transform.scale(boss_img, (400, 400))

# -------- GAME RESET FUNCTION --------
def reset_game():
    return {
        "player_pos": [WIDTH // 2, HEIGHT - 60],
        "boss_pos": [WIDTH // 2, 100],
        "bullets": [],
        "health": 100,
        "immune": False,
        "immune_start": 0,
        "shoot_timer": 0,
        "shoot_delay": 60,
        "count": 0,
        "movement1": 10,
        "movement2": 10,
        "displace": 0
    }

# Initial state
game_data = reset_game()
game_state = "menu"  # menu, game, dead

player_speed = 5
player_radius = 8
bullet_speed = 3
IMMUNE_DURATION = 500

running = True
while running:
    clock.tick(60)
    screen.fill((10, 10, 20))

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if game_state == "menu":
                game_data = reset_game()
                game_state = "game"

            elif game_state == "dead":
                if event.key == pygame.K_r:  # Restart
                    game_data = reset_game()
                    game_state = "game"
                elif event.key == pygame.K_m:  # Menu
                    game_state = "menu"

    # ================= MENU =================
    if game_state == "menu":
        title = font.render("Bullet Hell Bossfight", True, (255, 255, 255))
        prompt = small_font.render("Press any key to start", True, (180, 180, 180))

        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))

        if pygame.time.get_ticks() % 1000 < 500:
            screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2))

        pygame.display.flip()
        continue

    # ================= GAME =================
    if game_state == "game":
        g = game_data

        # Boss movement
        g["boss_pos"][0] += random.random() + g["movement1"]/2
        g["boss_pos"][1] += random.random() + g["movement2"]/2

        if g["boss_pos"][0] > 700 or g["boss_pos"][1] > 500:
            g["movement1"] = -8 * random.random() - 2
            g["movement2"] = -10 * random.random() - 2

        if g["boss_pos"][0] < 100 or g["boss_pos"][1] < 100:
            g["movement1"] = 8 * random.random() + 2
            g["movement2"] = 10 * random.random() + 2

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            g["player_pos"][0] -= player_speed
        if keys[pygame.K_d]:
            g["player_pos"][0] += player_speed
        if keys[pygame.K_w]:
            g["player_pos"][1] -= player_speed
        if keys[pygame.K_s]:
            g["player_pos"][1] += player_speed

        # Clamp player
        g["player_pos"][0] = max(0, min(WIDTH, g["player_pos"][0]))
        g["player_pos"][1] = max(0, min(HEIGHT, g["player_pos"][1]))

        # Shooting
        g["shoot_timer"] += 5
        g["displace"] += 5 * random.random()

        if g["shoot_timer"] >= g["shoot_delay"]:
            g["shoot_timer"] = 0
            g["count"] += 1

            if g["count"] >= 50:
                g["shoot_delay"] = 2000

            for i in range(30):
                angle = (2 * math.pi / 30) * i + g["displace"]
                dx = math.cos(angle)
                dy = math.sin(angle)
                g["bullets"].append([g["boss_pos"][0], g["boss_pos"][1], dx, dy])

        # Update bullets
        for b in g["bullets"]:
            b[0] += b[2] * bullet_speed
            b[1] += b[3] * bullet_speed

        # Cull bullets
        g["bullets"] = [b for b in g["bullets"] if 0 <= b[0] <= WIDTH and 0 <= b[1] <= HEIGHT]

        # Collision
        for b in g["bullets"]:
            dist = math.hypot(b[0] - g["player_pos"][0], b[1] - g["player_pos"][1])
            if dist < player_radius and not g["immune"]:
                g["health"] -= 40
                g["immune"] = True
                g["immune_start"] = pygame.time.get_ticks()

                if g["health"] <= 0:
                    game_state = "dead"
                break

        # Immunity timer
        if g["immune"]:
            if pygame.time.get_ticks() - g["immune_start"] >= IMMUNE_DURATION:
                g["immune"] = False

        # Draw boss
        rect = boss_img.get_rect(center=g["boss_pos"])
        screen.blit(boss_img, rect)

        # Draw player
        pygame.draw.circle(screen, (50, 200, 50), g["player_pos"], player_radius)

        # Draw bullets
        for b in g["bullets"]:
            rect = bullet_img.get_rect(center=(int(b[0]), int(b[1])))
            screen.blit(bullet_img, rect)

        # Health
        health_text = small_font.render(f"Health: {g['health']}", True, (255, 255, 255))
        screen.blit(health_text, (10, 10))

    # ================= DEATH SCREEN =================
    elif game_state == "dead":
        dead_text = font.render("You Died", True, (255, 80, 80))
        restart = small_font.render("Press R to Restart", True, (200, 200, 200))
        menu = small_font.render("Press M for Main Menu", True, (200, 200, 200))

        screen.blit(dead_text, (WIDTH//2 - dead_text.get_width()//2, HEIGHT//3))
        screen.blit(restart, (WIDTH//2 - restart.get_width()//2, HEIGHT//2))
        screen.blit(menu, (WIDTH//2 - menu.get_width()//2, HEIGHT//2 + 40))

    pygame.display.flip()

pygame.quit()