from . import base_utils as core
from . import error
from . import internal as internal


class kingz(core.base_proxy):
    def __init__(self, parent):
        super().__init__(parent)
        if self.game.Config.Kingzpits["Enable"]:
            self.capture = [
                self.capture_action,
            ]
            self.prechecks.append(self.is_not_kingzpit)
            self.progress.insert(0, self.progress_check_kingpit)
            self.roundsup.insert(0, self.checkout_shares2store)

    def is_not_kingzpit(self):
        if self.req.Move["Index"] in self.game.Config.Kingzpits["Value"]:
            self.error.raiseExp("IllegalMove")
        return True

    def progress_check_kingpit(self):
        if self.kai.Value == 0:
            if self.kai.Index in self.game.Config.Kingzpits["Value"]:
                self.state = internal.State.MOVE_END
                return False

        if self.prev in self.game.Config.Kingzpits["Value"]:
            self.skip_early = True
        return True

    def capture_action(self):
        index = self.kai.Index
        if index in self.game.Config.Kingzpits["Value"]:
            self.raise_pit_share(index, self.game.Board.Turn)
            self.captured_sucess = True
            self.state = internal.State.MOVE_END
        else:
            return self.parent.capture_action()
        return True

    def checkout_shares2store(self):
        for index in self.game.Config.Kingzpits["Value"]:
            total_share = 0
            for share in self.game.Board.Pits[index].Share:
                for side in share:
                    total_share += share[side]
            if total_share == 0:
                continue
            total_value = self.game.Board.Pits[index].Value
            rem_seeds = total_value
            for share in self.game.Board.Pits[index].Share:
                for side in share:
                    seeds = (total_value * share[side]) // total_share
                    # print("share2store: save_to_store", index, side, seeds)
                    self.save_to_store(side, seeds)
                    rem_seeds -= seeds
                    break
            self.set_pit_value(index, rem_seeds)
        return True
