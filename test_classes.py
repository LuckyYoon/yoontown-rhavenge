import pytest
from collections import defaultdict
from unittest.mock import patch
import pygame

from zclasses import delay, Controller, Player


_KEY_MAP = {
    "K_a": pygame.K_a,
    "K_d": pygame.K_d,
    "K_w": pygame.K_w,
    "K_s": pygame.K_s,
}

def make_key_state(pressed_key_names):
    state = defaultdict(bool)
    for name in pressed_key_names:
        state[_KEY_MAP[name]] = True
    return state


class TestDelay:

    @patch("pygame.time.get_ticks", return_value=1000)
    def test_new_key_returns_false(self, mock_ticks):
        timers = {}
        assert delay(timers, "shoot", 500) is False
        assert timers["shoot"] == 1000

    @patch("pygame.time.get_ticks", return_value=1600)
    def test_fires_when_interval_elapsed(self, mock_ticks):
        timers = {"shoot": 1000}
        assert delay(timers, "shoot", 500) is True
        assert timers["shoot"] == 1600

    @patch("pygame.time.get_ticks", return_value=1499)
    def test_does_not_fire_before_interval(self, mock_ticks):
        timers = {"shoot": 1000}
        assert delay(timers, "shoot", 500) is False
        assert timers["shoot"] == 1000


class TestControllerMove:

    def _patched_move(self, controller, player, pressed_key_names):
        key_state = make_key_state(pressed_key_names)
        with patch("pygame.key.get_pressed", return_value=key_state):
            controller.phase2 = lambda: None
            controller.move(player)

    def test_move_left(self):
        player = Player(100, 50)
        self._patched_move(Controller(), player, {"K_a"})
        assert player.x == 96

    def test_move_right(self):
        player = Player(100, 50)
        self._patched_move(Controller(), player, {"K_d"})
        assert player.x == 104

    def test_move_up(self):
        player = Player(50, 100)
        self._patched_move(Controller(), player, {"K_w"})
        assert player.y == 96

    def test_move_down(self):
        player = Player(50, 100)
        self._patched_move(Controller(), player, {"K_s"})
        assert player.y == 104

    def test_no_keys_no_movement(self):
        player = Player(50, 50)
        self._patched_move(Controller(), player, set())
        assert player.x == 50
        assert player.y == 50