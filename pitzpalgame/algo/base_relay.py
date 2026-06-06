import logging

from . import base_kingz as core
from . import error
from . import internal as internal

logger = logging.getLogger("pitzpalgame")


class relay(core.kingz):
    def __init__(self, game_in, req):
        logger.info("enter")
        super().__init__(game_in, req)
        if self.game.Config.Relay["Enable"]:
            self.capture = [
                self.capture_action,
            ]

    def capture_action(self):
        logger.info("enter")
        ret = super().capture_action()
        if self.captured_sucess and self.game.Config.Relay["Enable"]:
            self.captured_sucess = False
            self.state = internal.State.MOVE_PROGRESS
        return ret
