from . import base_utils as core
from . import error
from . import internal as internal


class relay(core.base_proxy):
    def __init__(self, parent):
        super().__init__(parent)
        if self.game.Config.Relay["Enable"]:
            self.capture = [
                self.capture_action,
            ]

    def capture_action(self):
        ret = self.parent.capture_action()
        if self.captured_sucess:
            self.state = internal.State.MOVE_PROGRESS
        return ret
