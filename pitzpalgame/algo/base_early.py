from . import base_utils as core
from . import error
from . import internal as internal


class early(core.base_proxy):
    def __init__(self, parent):
        super().__init__(parent)
        if self.game.Config.Early["Enable"]:
            self.prev = -1
            self.start = [self.start_move]
            self.progress.append(self.progress_check_early)
            self.capture.insert(0, self.progress_check_early)
            self.end.insert(0, self.progress_check_early)
            if self.game.Config.Plus["Enable"]:
                self.capture.insert(0, self.progress_check_plus)

    def progress_check_early(self):
        if self.get_pit_value(self.prev) == self.game.Config.Early["Value"]:
            self.move_to_store(self.prev)
        if self.skip_early:
            self.skip_early = False
        elif self.state == internal.State.MOVE_PROGRESS:
            self.prev = self.kai.Index
        else:
            self.prev = -1
        return True

    def start_move(self):
        ret = self.parent.start_move()
        self.prev = -1
        return ret

    def progress_check_plus(self):
        if self.get_pit_value(self.prev) == self.game.Config.Early["Value"]:
            self.move_to_store(self.prev, self.game.Board.Turn)
        return True
