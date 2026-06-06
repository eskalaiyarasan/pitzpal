import copy

from . import base_core as base
from . import base_early as early
from . import base_kingz as kingz
from . import base_relay as relay
from . import internal as internal


class classic(base.core):
    def __init__(self, game_in, req):
        super().__init__(game_in, req)
        self.active = True
        self.init_setup()
        self.progress.append(self.progress_update_pit)

    def init_setup(self):
        parent = self
        if self.game.Config.Early["Enable"]:
            parent = early.early(parent)
        if self.game.Config.Kingzpits["Enable"]:
            parent = kingz.kingz(parent)
        if self.game.Config.Relay["Enable"]:
            parent = relay.relay(parent)

    def progress_update_pit(self):
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
        return True

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
