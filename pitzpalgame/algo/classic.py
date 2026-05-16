import copy

from . import base as base
from . import internal as internal


class classic(base.base):
    def __init__(self, game_in, req):
        super().__init__(game_in, req)
        self.game = game_in
        self.req = req
        self.active = True
        # self.start.append(self.classicstep)
        # self.capture.append(self.classicstep)
        # self.progress.append(self.classicstep)

    def classicstep(self):
        if self.kai:
            cond = True
            while cond:
                self.kai.Index += 1
                if self.kai.Index >= (
                    self.game.Config.Nside * self.game.Config.PitsPerSide
                ):
                    self.kai.Index = 0
                cond = not self.game.Board.Pits[self.kai.Index].Active

            return True
        return False

    def step(self):
        self.step_base()
        if (
            (self.state == internal.State.MOVE_PROGRESS)
            or (self.state == internal.State.MOVE_START)
            or (self.state == internal.State.MOVE_CAPTURE)
        ):
            self.classicstep()
