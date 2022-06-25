from __future__ import annotations
from typing import Optional, TYPE_CHECKING

import tcod.event

from actions import Action, EscapeAction, BumpAction, WaitAction
if TYPE_CHECKING:
    from engine import Engine


MOVE_KEYS = {
    # Arrow keys + numpad arrow state.
    tcod.event.K_UP: (0, -1),
    tcod.event.K_DOWN: (0, 1),
    tcod.event.K_LEFT: (-1, 0),
    tcod.event.K_RIGHT: (1, 0),
    tcod.event.K_HOME: (-1, -1),
    tcod.event.K_END: (-1, 1),
    tcod.event.K_PAGEUP: (1, -1),
    tcod.event.K_PAGEDOWN: (1, 1),
    # Numpad numbers state.
    tcod.event.K_KP_1: (-1, 1),
    tcod.event.K_KP_2: (0, 1),
    tcod.event.K_KP_3: (1, 1),
    tcod.event.K_KP_4: (-1, 0),
    tcod.event.K_KP_6: (1, 0),
    tcod.event.K_KP_7: (-1, -1),
    tcod.event.K_KP_8: (0, -1),
    tcod.event.K_KP_9: (1, -1),
    # Vi keys.
    tcod.event.K_h: (-1, 0),
    tcod.event.K_j: (0, 1),
    tcod.event.K_k: (0, -1),
    tcod.event.K_l: (1, 0),
    tcod.event.K_y: (-1, -1),
    tcod.event.K_u: (1, -1),
    tcod.event.K_b: (-1, 1),
    tcod.event.K_n: (1, 1),
    # WASD + QEZ(X)C.
    tcod.event.K_w: (0, -1),
    tcod.event.K_s: (0, 1),
    tcod.event.K_x: (0, 1),
    tcod.event.K_a: (-1, 0),
    tcod.event.K_d: (1, 0),
    tcod.event.K_q: (-1, -1),
    tcod.event.K_z: (-1, 1),
    tcod.event.K_e: (1, -1),
    tcod.event.K_c: (1, 1),
}

WAIT_KEYS = {
    tcod.event.K_PERIOD,
    tcod.event.K_KP_5,
    tcod.event.K_CLEAR,
    tcod.event.K_SPACE,
}


class EventHandler(tcod.event.EventDispatch[Action]):
    def __init__(self, engine: Engine):
        self.engine = engine

        def handle_events(self) -> None:
            raise NotImplementedError()

        def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
            raise SystemExit()


class MainGameEventHandler(EventHandler):
    def handle_events(self) -> None:
        for event in tcod.event.wait():
            action = self.dispatch(event)

            if action is None:
                continue

            action.perform()

            self.engine.handle_enemy_turns()
            self.engine.update_fov()  # Update the FOV before the players next action.

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        key = event.sym

        player = self.engine.player

        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            action = BumpAction(player, dx, dy)
        elif key in WAIT_KEYS:  # just do nothing, patience is a key to victory
            action = WaitAction(player)
        elif key == tcod.event.K_ESCAPE:
            action = EscapeAction(player)

        # No valid key was pressed
        return action


class GameOverEventHandler(EventHandler):  # player is unable to move if the game is over
    def handle_events(self) -> None:
        for event in tcod.event.wait():
            action = self.dispatch(event)

            if action is None:
                continue

            action.perform()

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        key = event.sym

        if key == tcod.event.K_ESCAPE:
            action = EscapeAction(self.engine.player)

        # No valid key was pressed
        return action
