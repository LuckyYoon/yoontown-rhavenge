"""
Game unittests for Yoontown Rhavenge.
"""

import pygame

from ytr_classes import (
    delay,
    Controller,
    Player,
    Boss,
    BossProjectile,
    PlayerProjectile,
)


class KeyState(dict):
    """A dict that returns False for any key that has not been explicitly set."""

    def __missing__(self, key):
        return False


def make_key_state(*pressed_keys):
    """
    Builds a KeyState with the given pygame key constants set to True.

    Args:
        pressed_keys: Zero or more pygame key constants to mark as pressed.

    Returns:
        A KeyState where each supplied key maps to True and all others to False.
    """
    state = KeyState()
    for key in pressed_keys:
        state[key] = True
    return state


class TestDelay:
    """Tests for the delay timer utility function."""

    def test_new_key_returns_false(self, monkeypatch):
        """Verifies that a key not yet in timers returns False and is recorded."""
        monkeypatch.setattr(pygame.time, "get_ticks", lambda: 1000)
        timers = {}
        assert delay(timers, "shoot", 500) is False
        assert timers["shoot"] == 1000

    def test_fires_when_interval_elapsed(self, monkeypatch):
        """Verifies that delay returns True and resets the timer once the interval has passed."""
        monkeypatch.setattr(pygame.time, "get_ticks", lambda: 1600)
        timers = {"shoot": 1000}
        assert delay(timers, "shoot", 500) is True
        assert timers["shoot"] == 1600

    def test_does_not_fire_before_interval(self, monkeypatch):
        """
        Verifies that delay returns False and leaves the timer unchanged
        before the interval passes.
        """
        monkeypatch.setattr(pygame.time, "get_ticks", lambda: 1499)
        timers = {"shoot": 1000}
        assert delay(timers, "shoot", 500) is False
        assert timers["shoot"] == 1000


class TestPlayer:
    """Tests for Player initialization."""

    def test_initial_position(self):
        """Verifies that x and y are set to the values passed to the constructor."""
        player = Player(75, 150)
        assert player.x == 75
        assert player.y == 150

    def test_initial_hp(self):
        """Verifies that a new player starts with 100 HP."""
        player = Player(0, 0)
        assert player.hp == 325

    def test_initial_alive_and_not_immune(self):
        """Verifies that a new player starts alive and without immunity."""
        player = Player(0, 0)
        assert player.alive is True
        assert player.immune is False

    def test_initial_movespeed(self):
        """Verifies that a new player starts with a movespeed of 4."""
        player = Player(0, 0)
        assert player.movespeed == 4


class TestControllerMove:
    """Tests for Controller.move using WASD input."""

    def _patched_move(self, monkeypatch, player, *pressed_keys):
        """
        Calls Controller.move with a simulated key state.

        Args:
            monkeypatch: The pytest monkeypatch fixture.
            player: The Player instance to move.
            pressed_keys: Zero or more pygame key constants to simulate as held.
        """
        monkeypatch.setattr(
            pygame.key, "get_pressed", lambda: make_key_state(*pressed_keys)
        )
        controller = Controller()
        controller.phase2 = lambda: None
        controller.move(player)

    def test_move_left(self, monkeypatch):
        """Verifies that holding A decreases the player's x by movespeed."""
        player = Player(100, 50)
        self._patched_move(monkeypatch, player, pygame.K_a)  # pylint: disable=no-member
        assert player.x == 96

    def test_move_right(self, monkeypatch):
        """Verifies that holding D increases the player's x by movespeed."""
        player = Player(100, 50)
        self._patched_move(monkeypatch, player, pygame.K_d)  # pylint: disable=no-member
        assert player.x == 104

    def test_move_up(self, monkeypatch):
        """Verifies that holding W decreases the player's y by movespeed."""
        player = Player(50, 100)
        self._patched_move(monkeypatch, player, pygame.K_w)  # pylint: disable=no-member
        assert player.y == 96

    def test_move_down(self, monkeypatch):
        """Verifies that holding S increases the player's y by movespeed."""
        player = Player(50, 100)
        self._patched_move(monkeypatch, player, pygame.K_s)  # pylint: disable=no-member
        assert player.y == 104

    def test_no_keys_no_movement(self, monkeypatch):
        """Verifies that the player does not move when no keys are held."""
        player = Player(50, 50)
        self._patched_move(monkeypatch, player)
        assert player.x == 50
        assert player.y == 50

    def test_move_left_and_up_simultaneously(self, monkeypatch):
        """Verifies that holding A and W together moves the player diagonally."""
        player = Player(100, 100)
        self._patched_move(
            monkeypatch, player, pygame.K_a, pygame.K_w # pylint: disable=no-member
        )
        assert player.x == 96
        assert player.y == 96


class TestControllerAttack:
    """Tests for Controller.attack using spacebar input and shot delay."""

    def _patched_attack(
        self, monkeypatch, player, attacks, timers, press_space=True, ticks=1500
    ):  # pylint: disable=too-many-arguments, too-many-positional-arguments
        """
        Calls Controller.attack with simulated input and clock state.

        Args:
            monkeypatch: The pytest monkeypatch fixture.
            player: The Player instance that fires the attack.
            attacks: The list to which new PlayerProjectile instances are appended.
            timers: The timers dict used by the delay function.
            press_space: Whether the spacebar is simulated as held.
            ticks: The value returned by pygame.time.get_ticks.
        """
        keys = (
            make_key_state(pygame.K_SPACE) if press_space else make_key_state() # pylint: disable=no-member
        )
        monkeypatch.setattr(pygame.key, "get_pressed", lambda: keys)
        monkeypatch.setattr(pygame.mouse, "get_pressed", lambda: (0, 0, 0))
        monkeypatch.setattr(pygame.time, "get_ticks", lambda: ticks)
        Controller().attack(player, attacks, timers)

    def test_attack_adds_projectile(self, monkeypatch):
        """Verifies that pressing space fires exactly one projectile."""
        player = Player(100, 100)
        attacks = []
        timers = {"player_shot": 1000}
        self._patched_attack(monkeypatch, player, attacks, timers)
        assert len(attacks) == 1

    def test_attack_projectile_spawns_at_player_position(self, monkeypatch):
        """Verifies that the fired projectile spawns at the player's current position."""
        player = Player(200, 300)
        attacks = []
        timers = {"player_shot": 1000}
        self._patched_attack(monkeypatch, player, attacks, timers)
        assert attacks[0].p_x == 200
        assert attacks[0].p_y == 300

    def test_no_attack_without_key(self, monkeypatch):
        """Verifies that no projectile is fired when spacebar is not held."""
        player = Player(100, 100)
        attacks = []
        timers = {"player_shot": 1000}
        self._patched_attack(monkeypatch, player, attacks, timers, press_space=False)
        assert len(attacks) == 0

    def test_no_attack_before_delay_elapsed(self, monkeypatch):
        """Verifies that no projectile is fired if the shot cooldown has not expired."""
        player = Player(100, 100)
        attacks = []
        timers = {"player_shot": 1000}
        self._patched_attack(monkeypatch, player, attacks, timers, ticks=1100)
        assert len(attacks) == 0


class TestBossProjectileLaunch:
    """Tests for BossProjectile.launch_projectile movement and delay behavior."""

    def test_moves_when_launched(self):
        """Verifies that a launched projectile advances by speed along its direction."""
        proj = BossProjectile(5, 10, 20, 100, 100)
        proj.dx = 1
        proj.dy = 0
        proj.launch = True
        proj.launch_projectile()
        assert proj.p_x == 105
        assert proj.p_y == 100

    def test_moves_diagonally(self):
        """Verifies that a launched projectile moves correctly along both axes."""
        proj = BossProjectile(10, 10, 20, 0, 0)
        proj.dx = 1
        proj.dy = 1
        proj.launch = True
        proj.launch_projectile()
        assert proj.p_x == 10
        assert proj.p_y == 10

    def test_no_movement_when_not_launched(self):
        """Verifies that a projectile with launch=False does not move."""
        proj = BossProjectile(5, 10, 20, 100, 100)
        proj.dx = 1
        proj.dy = 0
        proj.launch = False
        proj.launch_projectile()
        assert proj.p_x == 100
        assert proj.p_y == 100

    def test_follows_prime_bullet_position(self):
        """
        Verifies that a follower projectile tracks behind its prime bullet
        by the given offset.
        """
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
        """
        Verifies that a projectile with an active delay does not move
        before the delay expires.
        """
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
    """Tests for BossProjectile.player_collision damage and immunity behavior."""

    def test_collision_reduces_player_hp(self, monkeypatch):
        """Verifies that a direct hit subtracts the projectile's damage from the player's HP."""
        monkeypatch.setattr(pygame.time, "get_ticks", lambda: 0)
        monkeypatch.setattr(pygame.time, "delay", lambda ms: None)
        player = Player(100, 100)
        proj = BossProjectile(5, 40, 25, 100, 100)
        proj.delay = 0
        proj.player_collision(player)
        assert player.hp == 300

    def test_collision_makes_player_immune(self, monkeypatch):
        """Verifies that a successful hit sets the player's immune flag to True."""
        monkeypatch.setattr(pygame.time, "get_ticks", lambda: 0)
        monkeypatch.setattr(pygame.time, "delay", lambda ms: None)
        player = Player(100, 100)
        proj = BossProjectile(5, 40, 25, 100, 100)
        proj.delay = 0
        proj.player_collision(player)
        assert player.immune is True

    def test_no_damage_when_out_of_range(self, monkeypatch):
        """Verifies that a projectile far from the player deals no damage."""
        monkeypatch.setattr(pygame.time, "delay", lambda ms: None)
        player = Player(100, 100)
        proj = BossProjectile(5, 10, 25, 500, 500)
        proj.delay = 0
        proj.player_collision(player)
        assert player.hp == 325
        assert player.immune is False

    def test_no_damage_when_player_is_immune(self, monkeypatch):
        """Verifies that an immune player takes no damage even on contact."""
        monkeypatch.setattr(pygame.time, "delay", lambda ms: None)
        player = Player(100, 100)
        player.immune = True
        proj = BossProjectile(5, 40, 25, 100, 100)
        proj.delay = 0
        proj.player_collision(player)
        assert player.hp == 325

    def test_no_collision_check_during_delay(self):
        """Verifies that a projectile with an active delay skips the collision check entirely."""
        player = Player(100, 100)
        proj = BossProjectile(5, 40, 25, 100, 100)
        proj.delay = 1000
        proj.player_collision(player)
        assert player.hp == 325


class TestPlayerProjectileLaunch:
    """Tests for PlayerProjectile.launch_projectile movement and hitbox updates."""

    def test_moves_horizontally(self):
        """Verifies that the projectile advances by speed along the x-axis."""
        proj = PlayerProjectile(8, 4, 20, 50, 50)
        proj.dx = 1
        proj.dy = 0
        proj.launch_projectile()
        assert proj.p_x == 58
        assert proj.p_y == 50

    def test_hitbox_updates_after_launch(self):
        """Verifies that player_p_hitbox reflects the new position after each step."""
        proj = PlayerProjectile(8, 4, 20, 50, 50)
        proj.dx = 1
        proj.dy = 0
        proj.launch_projectile()
        assert proj.player_p_hitbox[0] == 58
        assert proj.player_p_hitbox[1] == 50

    def test_multiple_steps_accumulate(self):
        """Verifies that position accumulates correctly across multiple launch calls."""
        proj = PlayerProjectile(5, 4, 20, 0, 0)
        proj.dx = 1
        proj.dy = 0
        proj.launch_projectile()
        proj.launch_projectile()
        assert proj.p_x == 10


class TestPlayerProjectileBossCollision:
    """Tests for PlayerProjectile.boss_collision damage and hit-once behavior."""

    def test_collision_reduces_boss_hp(self):
        """Verifies that a hit inside the boss hitbox subtracts the projectile's damage."""
        boss = Boss(400, 300)
        proj = PlayerProjectile(8, 4, 20, boss.x, boss.y)
        proj.player_p_hitbox = (boss.hitbox[0] + 1, boss.hitbox[1] + 1, 2, 5)
        proj.boss_collision(boss)
        assert boss.hp == 980

    def test_no_damage_when_already_hit(self):
        """Verifies that a projectile marked as hit does not damage the boss again."""
        boss = Boss(400, 300)
        proj = PlayerProjectile(8, 4, 20, boss.x, boss.y)
        proj.hit = True
        proj.player_p_hitbox = (boss.hitbox[0] + 1, boss.hitbox[1] + 1, 2, 5)
        proj.boss_collision(boss)
        assert boss.hp == 1000

    def test_no_damage_when_out_of_range(self):
        """Verifies that a projectile outside the boss hitbox deals no damage."""
        boss = Boss(400, 300)
        proj = PlayerProjectile(8, 4, 20, 0, 0)
        proj.player_p_hitbox = (0, 0, 2, 5)
        proj.boss_collision(boss)
        assert boss.hp == 1000
