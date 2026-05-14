import ast
import copy
import json

import algo.internal as internal
import error
import game
import utils


class base:
    def __init__(self, game_in: game.game, req):
        self.state = internal.State.MOVE_VALIDATION
        self.active = False
        self.game = game_in
        self.req = req
        self.step_value = 1
        self.captureplus = {"Active": False, "Index": -1}
        self.prev = -1
        self.kai = None
        self.prechecks = [
            self.is_game_active,
            self.is_valid_req,
            self.is_valid_turn,
            self.is_valid_pit,
        ]
        self.start = [self.start_move]
        self.progress = [
            self.progress_check_kingpit,
            self.progress_check_capture,
            self.progress_check_captureplus,
            self.progress_check_early,
            self.progress_update_pit,
        ]
        self.capture = [
            self.capture_plus_condition,
            self.progress_check_early,
        ]
        self.end = [self.progress_check_early, self.update_moves2games]
        self.error = error.error()

    def step(self):
        steps = []
        if self.state == internal.State.MOVE_VALIDATION:
            steps = self.prechecks
        elif self.state == internal.State.MOVE_START:
            steps = self.start
        elif self.state == internal.State.MOVE_PROGRESS:
            steps = self.progress
        elif self.state == internal.State.MOVE_CAPTURE:
            steps = self.capture
        elif self.state == internal.State.MOVE_END:
            steps = self.end

        for cond in steps:
            if callable(cond):
                if not cond():
                    break

    def result(self):
        self.step()
        data_dict = ast.literal_eval(str(self.game))
        return json.dumps(data_dict)

    def is_game_active(self):
        if self.game.Staus != "active":
            self.error.raiseExp("GameEndedAgo")
        return True

    def is_valid_turn(self):
        player = self.req.Move["Player"].strip()
        found = False
        side = -1
        for pl in self.game.Toss:
            if player in pl:
                found = True
                side = pl[player]
                break
        if found:
            if side >= self.game.Config.Nside or side < 0:
                self.error.raiseExp("IllegalOptions")
            elif side != self.game.Board.Turn:
                self.error.raiseExp("IllegalTurn")
            else:
                self.state = internal.State.MOVE_START
                return True
        else:
            self.error.raiseExp("IllegalAccess")
        return False

    def is_valid_req(self):
        if utils.is_time_expire(self.req.Move["Timestamp"], 300):
            self.error.raiseExp("Timeout")
        if len(self.game.moves) > 1:
            if self.req.Move["Sequence"] != self.game.moves[-1]["Sequence"] + 1:
                self.error.raiseExp("IllegalMove")
        max_index = self.game.Config.PitsPerSide * self.game.Config.Nside
        if self.req.Move["Index"] >= max_index or self.req.Move["Index"] < 0:
            self.error.raiseExp("IllegalOptions")
        if self.game.Config.Kingzpits["Enable"]:
            if self.req.Move["Index"] in self.game.Config.Kingzpits["Value"]:
                self.error.raiseExp("IllegalMove")
        side = self.req.Move["Index"] // self.game.Config.PitsPerSide
        if self.game.Board.Turn != side:
            self.error.raiseExp("IllegalMove")
        return True

    def is_valid_pit(self):
        index = self.req.Move["Index"]
        found = False
        for pit in self.game.Board.Pits:
            if pit.Active and pit.Index == index:
                found = True
                if pit.Value <= 0:
                    self.error.raiseExp("IllegalMove")
        if not found:
            self.error.raiseExp("IllegalMove")
        return True

    def start_move(self):
        index = self.req.Move["Index"]
        for pit in self.game.Board.Pits:
            if pit.Active and pit.Index == index:
                self.kai = copy.deepcopy(pit)
                pit.Value = 0
        self.state = internal.State.MOVE_PROGRESS
        self.prev = -1
        self.captureplus["Active"] = False
        return True

    def progress_check_kingpit(self):
        if (self.kai.Value == 0) and self.game.Config.Kingzpits["Enable"]:
            if self.kai.Index in self.game.Config.Kingzpits["Value"]:
                self.state = internal.State.MOVE_END
                return False
        return True

    def progress_check_capture(self):
        if (self.kai.Value == 0) and self.game.Board.Pits[self.kai.Index].Value == 0:
            self.state = internal.State.MOVE_CAPTURE
            return False
        return True

    def progress_check_captureplus(self):
        if self.kai.Value == self.step_value:
            if self.kai.Index in self.game.Config.Kingzpits["Value"]:
                self.captureplus["Active"] = False
                return True
            else:
                self.captureplus["Active"] = True
                self.captureplus["Index"] = self.kai.Index
        elif (self.kai.Value == 0) and self.captureplus["Active"]:
            if self.game.Board.Pits[self.kai.Index].Value != 0:
                self.captureplus["Active"] = False
                self.captureplus["Index"] = -1
                return True
            else:
                self.state = internal.State.MOVE_CAPTURE
                return False
        else:
            self.captureplus["Active"] = False
            self.captureplus["Index"] = -1
        return True

    def progress_check_early(self):
        if self.game.Config.Early["Enable"]:
            if self.prev == -1:
                pass
            elif self.prev in self.game.Config.Kingzpits["Value"]:
                self.prev = -1
                return True
            elif (
                self.game.Board.Pits[self.prev].Value % self.game.Config.Early["Value"]
                == 0
            ):
                side = self.game.Board.Pits[self.prev].Side
                value = self.game.Board.Store[str(side)]
                self.game.Board.Store[str(side)] = (
                    value + self.game.Board.Pits[self.prev].Value
                )
                self.game.Board.Pits[self.prev].Value = 0
            if self.state == internal.State.MOVE_PROGRESS:
                self.prev = self.kai.Index
            else:
                self.prev = -1
        return True

    def progress_update_pit(self):
        if self.kai.Value > 0:
            value = self.game.Board.Pits[self.kai.Index].Value
            if self.kai.Value > self.step_value:
                self.game.Board.Pits[self.kai.Index].Value = value + self.step_value
                self.kai.Value -= self.step_value
            else:
                self.game.Board.Pits[self.kai.Index].Value = value + self.kai.Value
                self.kai.Value = 0
        else:
            self.kai.Value = self.game.Board.Pits[self.kai.Index].Value
            self.game.Board.Pits[self.kai.Index].Value = 0
        return True

    def capture_plus_condition(self):
        if self.captureplus["Active"]:
            index = self.captureplus["Index"]
            if self.game.Board.Pits[index].Value % self.game.Config.Early["Value"] == 0:
                side = self.game.Board.Turn
                value = self.game.Board.Store[str(side)]
                self.game.Board.Store[str(side)] = (
                    value + self.game.Board.Pits[index].Value
                )
                self.game.Board.Pits[index].Value = 0
                self.captureplus["Active"] = False
                if self.prev == index:
                    self.prev = -1
        return True

    def capture_action(self):
        if self.state == internal.State.MOVE_CAPTURE:
            index = self.kai.index
            side = self.game.Board.Turn
            value = self.step_value
            if index in self.game.Config.Kingzpits["Value"]:
                self.game.Board.Pits[index].Share[str(side)] += 1
            else:
                value = self.game.Board.Store[str(side)]
                self.game.Board.Store[str(side)] = (
                    value + self.game.Board.Pits[index].Value
                )
                self.game.Board.Pits[index].Value = 0
            if self.game.Config.Relay["Enable"] and value > 0:
                self.state = internal.State.MOVE_PROGRESS
            else:
                self.state = internal.State.MOVE_END
                return False
        return True

    def update_moves2games(self):
        mv = str(self.req.Move)
        data_dict = ast.literal_eval(mv)
        mvx = json.dumps(data_dict)
        self.game.Moves.append(mvx)
        return True
