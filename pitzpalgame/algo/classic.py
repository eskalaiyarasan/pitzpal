import copy

import algo.base as base


class classic(base.base):
    def __init__(self, game_in, req):
        super().__init__(game_in, req)
        self.game = game_in
        self.req = req
        self.active = True
        self.start.append(self.classicstep)
        self.capture.append(self.classicstep)
        self.progress.append(self.classicstep)

    def classicstep(self):
        if self.kai:
            self.kai.Index += 1
            if self.kai.Index >= (
                self.game.Config.Nside * self.game.Config.PitsPerSide
            ):
                self.kai.Index = 0
            return True
        return False
