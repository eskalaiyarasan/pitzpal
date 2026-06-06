import copy
import logging

# from . import base_core as base
# from . import base_early as early
# from . import base_kingz as kingz
from . import base_relay as relay
from . import internal as internal

logger = logging.getLogger("pitzpalgame")


class classic(relay.relay):
    def __init__(self, game_in, req):
        logger.info(f"enter {req}")
        super().__init__(game_in, req)
        self.active = True
        self.progress.append(self.progress_update_pit)
        logger.info(f"exit {game_in}")

    def progress_update_pit(self):
        logger.info("enter")
        if self.kai.Value > 0:
            if self.kai.Value > self.step_value:
                self.raise_pit_value(self.kai.Index, self.step_value)
                self.kai.Value -= self.step_value
            else:
                self.raise_pit_value(self.kai.Index, self.kai.Value)
                self.kai.Value = 0
        else:
            self.kai.Value = self.get_pit_value(self.kai.Index)
            self.set_pit_value(self.kai.Index, 0)
        logger.info("exit True")
        return True

    def classicstep(self):
        logger.info("enter")
        if self.kai:
            cond = True
            while cond:
                self.kai.Index += 1
                if self.kai.Index >= (
                    self.game.Config.Nside * self.game.Config.PitsPerSide
                ):
                    self.kai.Index = 0
                cond = not self.game.Board.Pits[self.kai.Index].Active
            logger.info("exit True")
            return True
        logger.info("exit False")
        return False

    def step(self):
        logger.info("enter")
        self.step_base()
        if (
            (self.state == internal.State.MOVE_PROGRESS)
            or (self.state == internal.State.MOVE_START)
            or (self.state == internal.State.MOVE_CAPTURE)
        ):
            self.classicstep()
        logger.info("exit")
