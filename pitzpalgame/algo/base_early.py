import logging

from . import base_core as core
from . import error
from . import internal as internal

logger = logging.getLogger("pitzpalgame")


class early(core.core):
    def __init__(self, game_in, req):
        logger.info("enter")
        super().__init__(game_in, req)
        if self.game.Config.Early["Enable"]:
            self.prev = -1
            # self.start = [self.start_move]
            self.progress.append(self.progress_check_early)
            self.capture.insert(0, self.progress_check_early)
            self.end.insert(0, self.progress_check_early)
            if self.game.Config.Plus["Enable"]:
                self.capture.insert(0, self.progress_check_plus)
        logger.info("exit")

    def progress_check_early(self):
        logger.info("enter")
        if self.get_pit_value(self.prev) == self.game.Config.Early["Value"]:
            self.move_to_store(self.prev)
        if self.skip_early:
            self.skip_early = False
        elif self.state == internal.State.MOVE_PROGRESS:
            self.prev = self.kai.Index
        else:
            self.prev = -1
        logger.info("exit True")
        return True

    def start_move(self):
        logger.info("enter")
        ret = super().start_move()
        self.prev = -1
        logger.info(f"exit {ret}")
        return ret

    def progress_check_plus(self):
        logger.info("enter")
        if self.get_pit_value(self.prev) == self.game.Config.Early["Value"]:
            self.move_to_store(self.prev, self.game.Board.Turn)
        logger.info("exit True")
        return True
