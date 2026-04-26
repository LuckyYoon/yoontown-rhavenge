import math
import pytest
import pygame

from zclasses import delay, Controller, Player, Boss, BossProjectile, PlayerProjectile


class KeyState(dict):
    def __missing__(self, key):
        return False


def make_key_state(*pressed_keys):
    state = KeyState()
    for key in pressed_keys:
        state[key] = True
    return state


class TestDelay:

    def test_new_key_returns_false(self, monkeypatch):
        monkeypatch.setattr(pygame.time, "get_ticks", lambda: 1000)
        timers = {}
        assert delay(timers, "shoot", 500) is False
        assert timers["shoot"] == 1000

    def test_fires_when_interval_elapsed(self, monkeypatch):
        monkeypatch.setattr(pygame.time, "get_ticks", lambda: 1600)
        timers = {"shoot": 1000}
        assert delay(timers, "shoot", 500) is True
        assert timers["shoot"] == 1600

    def test_does_not_fire_before_interval(self, monkeypatch):
        monkeypatch.setattr(pygame.time, "get_ticks", lambda: 1499)
        timers = {"shoot": 1000}
        assert delay(timers, "shoot", 500) is False
        assert timers["shoot"] == 1000


class TestPlayer:

    def test_initial_position(self):
        player = Player(75, 150)
        assert player.x == 75
        assert player.y == 150

    def test_initial_hp(self):
        player = Player(0, 0)
        assert player.hp == 100

    def test_initial_alive_and_not_immune(self):
        player = Player(0, 0)
        assert player.alive is True
        assert player.immune is False

    def test_initial_movespeed(self):
        player = Player(0, 0)
        assert player.movespeed == 4


class TestControllerMove:

    def _patched_move(self, monkeypatch, player, *pressed_keys):
        monkeypatch.setattr(pygame.key, "get_pressed", lambda: make_key_state(*pressed_keys))
        controller = Controller()
        controller.phase2 = lambda: None
        controller.move(player)

    def test_move_left(self, monkeypatch):
        player = Player(100, 50)
        self._patched_move(monkeypatch, player, pygame.K_a)
        assert player.x == 96

    def test_move_right(self, monkeypatch):
        player = Player(100, 50)
        self._patched_move(monkeypatch, player, pygame.K_d)
        assert player.x == 104

    def test_move_up(self, monkeypatch):
        player = Player(50, 100)
        self._patched_move(monkeypatch, player, pygame.K_w)
        assert player.y == 96

    def test_move_down(self, monkeypatch):
        player = Player(50, 100)
        self._patched_move(monkeypatch, player, pygame.K_s)
        assert player.y == 104

    def test_no_keys_no_movement(self, monkeypatch):
        player = Player(50, 50)
        self._patched_move(monkeypatch, player)
        assert player.x == 50
        assert player.y == 50

    def test_move_left_and_up_simultaneously(self, monkeypatch):
        player = Player(100, 100)
        self._patched_move(monkeypatch, player, pygame.K_a, pygame.K_w)
        assert player.x == 96
        assert player.y == 96


class TestControllerAttack:

    def _patched_attack(self, monkeypatch, player, attacks, timers, press_space=True, ticks=1500):
        keys = make_key_state(pygame.K_SPACE) if press_space else make_key_state()
        monkeypatch.setattr(pygame.key, "get_pressed", lambda: keys)
        monkeypatch.setattr(pygame.mouse, "get_pressed", lambda: (0, 0, 0))
        monkeypatch.setattr(pygame.time, "get_ticks", lambda: ticks)
        Controller().attack(player, attacks, timers)

    def test_attack_adds_projectile(self, monkeypatch):
        player = Player(100, 100)
        attacks = []
        timers = {"player_shot": 1000}
        self._patched_attack(monkeypatch, player, attacks, timers)
        assert len(attacks) == 1

    def test_attack_projectile_spawns_at_player_position(self, monkeypatch):
        player = Player(200, 300)
        attacks = []
        timers = {"player_shot": 1000}
        self._patched_attack(monkeypatch, player, attacks, timers)
        assert attacks[0].p_x == 200
        assert attacks[0].p_y == 300

    def test_no_attack_without_key(self, monkeypatch):
        player = Player(100, 100)
        attacks = []
        timers = {"player_shot": 1000}
        self._patched_attack(monkeypatch, player, attacks, timers, press_space=False)
        assert len(attacks) == 0

    def test_no_attack_before_delay_elapsed(self, monkeypatch):
        player = Player(100, 100)
        attacks = []
        timers = {"player_shot": 1000}
        self._patched_attack(monkeypatch, player, attacks, timers, ticks=1100)
        assert len(attacks) == 0


class TestBossRandomMove:

    def test_direction_is_normalized(self, monkeypatch):
        monkeypatch.setattr("random.random", iter([0.6, 0.4]).__next__)
        boss = Boss(400, 300)
        boss.random_move()
        assert abs(math.hypot(boss.dx, boss.dy) - 1.0) < 1e-6

    def test_new_target_is_set(self, monkeypatch):
        monkeypatch.setattr("random.random", iter([0.6, 0.4]).__next__)
        boss = Boss(400, 300)
        boss.random_move()
        assert boss.new_x != 400 or boss.new_y != 300


class TestBossProjectileLaunch:

    def test_moves_when_launched(self):
        proj = BossProjectile(5, 10, 20, 100, 100)
        proj.dx = 1
        proj.dy = 0
        proj.launch = True
        proj.launch_projectile()
        assert proj.p_x == 105
        assert proj.p_y == 100

    def test_moves_diagonally(self):
        proj = BossProjectile(10, 10, 20, 0, 0)
        proj.dx = 1
        proj.dy = 1
        proj.launch = True
        proj.launch_projectile()
        assert proj.p_x == 10
        assert proj.p_y == 10

    def test_no_movement_when_not_launched(self):
        proj = BossProjectile(5, 10, 20, 100, 100)
        proj.dx = 1
        proj.dy = 0
        proj.launch = False
        proj.launch_projectile()
        assert proj.p_x == 100
        assert proj.p_y == 100

    def test_follows_prime_bullet_position(self):
        prime = BossProjectile(5, 10, 20, 200, 150)
        prime.dx = 1
        prime.dy = 0
        follower = BossProjectile(0, 10, 20, 0, 0)
        follower.follow_prime_bullet = prime
        follower.offset = 10
        follower.launch_projectile()
        assert follower.p_x == 190
        assert follower.p_y == 150

    def test_delay_prevents_movement(self, monkeypatch):
        monkeypatch.setattr(pygame.time, "get_ticks", lambda: 500)
        proj = BossProjectile(5, 10, 20, 100, 100)
        proj.dx = 1
        proj.dy = 0
        proj.launch = True
        proj.delay = 1000
        proj.spawn_time = 0
        proj.launch_projectile()
        assert proj.p_x == 100


class TestBossProjectilePlayerCollision:

    def test_collision_reduces_player_hp(self, monkeypatch):
        monkeypatch.setattr(pygame.time, "get_ticks", lambda: 0)
        monkeypatch.setattr(pygame.time, "delay", lambda ms: None)
        player = Player(100, 100)
        proj = BossProjectile(5, 40, 25, 100, 100)
        proj.delay = 0
        proj.player_collision(player)
        assert player.hp == 75

    def test_collision_makes_player_immune(self, monkeypatch):
        monkeypatch.setattr(pygame.time, "get_ticks", lambda: 0)
        monkeypatch.setattr(pygame.time, "delay", lambda ms: None)
        player = Player(100, 100)
        proj = BossProjectile(5, 40, 25, 100, 100)
        proj.delay = 0
        proj.player_collision(player)
        assert player.immune is True

    def test_no_damage_when_out_of_range(self, monkeypatch):
        monkeypatch.setattr(pygame.time, "delay", lambda ms: None)
        player = Player(100, 100)
        proj = BossProjectile(5, 10, 25, 500, 500)
        proj.delay = 0
        proj.player_collision(player)
        assert player.hp == 100
        assert player.immune is False

    def test_no_damage_when_player_is_immune(self, monkeypatch):
        monkeypatch.setattr(pygame.time, "delay", lambda ms: None)
        player = Player(100, 100)
        player.immune = True
        proj = BossProjectile(5, 40, 25, 100, 100)
        proj.delay = 0
        proj.player_collision(player)
        assert player.hp == 100

    def test_no_collision_check_during_delay(self):
        player = Player(100, 100)
        proj = BossProjectile(5, 40, 25, 100, 100)
        proj.delay = 1000
        proj.player_collision(player)
        assert player.hp == 100


class TestPlayerProjectileLaunch:

    def test_moves_horizontally(self):
        proj = PlayerProjectile(8, 4, 20, 50, 50)
        proj.dx = 1
        proj.dy = 0
        proj.launch_projectile()
        assert proj.p_x == 58
        assert proj.p_y == 50

    def test_hitbox_updates_after_launch(self):
        proj = PlayerProjectile(8, 4, 20, 50, 50)
        proj.dx = 1
        proj.dy = 0
        proj.launch_projectile()
        assert proj.player_p_hitbox[0] == 58
        assert proj.player_p_hitbox[1] == 50

    def test_multiple_steps_accumulate(self):
        proj = PlayerProjectile(5, 4, 20, 0, 0)
        proj.dx = 1
        proj.dy = 0
        proj.launch_projectile()
        proj.launch_projectile()
        assert proj.p_x == 10


class TestPlayerProjectileBossCollision:

    def test_collision_reduces_boss_hp(self):
        boss = Boss(400, 300)
        proj = PlayerProjectile(8, 4, 20, boss.x, boss.y)
        proj.player_p_hitbox = (boss.hitbox[0] + 1, boss.hitbox[1] + 1, 2, 5)
        proj.boss_collision(boss)
        assert boss.hp == 980

    def test_no_damage_when_already_hit(self):
        boss = Boss(400, 300)
        proj = PlayerProjectile(8, 4, 20, boss.x, boss.y)
        proj.hit = True
        proj.player_p_hitbox = (boss.hitbox[0] + 1, boss.hitbox[1] + 1, 2, 5)
        proj.boss_collision(boss)
        assert boss.hp == 1000

    def test_no_damage_when_out_of_range(self):
        boss = Boss(400, 300)
        proj = PlayerProjectile(8, 4, 20, 0, 0)
        proj.player_p_hitbox = (0, 0, 2, 5)
        proj.boss_collision(boss)
        assert boss.hp == 1000