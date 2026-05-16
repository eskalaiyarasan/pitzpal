import ast
import copy
import json
from abc import abstractmethod

import error
import game
import utils

from .algo import internal as internal


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
            self.capture_action,
        ]
        self.end = [
            self.progress_check_early,
            self.update_next_turn,
            self.update_moves2games,
        ]
        self.error = error.error()
        # print(str(self.req))

    def step_base(self):
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
        # pause = input(f"pause/{self.state}:")
        for cond in steps:
            # if pause.strip() == "1":
            #     pause = input("pause:")
            #     print(pause, cond)
            if callable(cond):
                if not cond():
                    break

    def result(self):
        self.step_base()
        self.check_roundsup()
        self.check_gameend()
        # pause = input("pause:")
        # print("pause", self.game)
        return str(self.game)

    def is_game_active(self):
        if self.game.Status != "active":
            self.error.raiseExp("GameEndedAgo")
        if (
            (self.game.Config.Nside <= 0)
            or (self.game.Config.Nseeds <= 0)
            or (self.game.Config.PitsPerSide <= 0)
        ):
            self.error.raiseExp("IllegalConfig")
        return True

    def is_valid_turn(self):
        player = self.req.Move["Player"].strip()
        found = False
        side = -1
        for pl in self.game.Toss:
            if player in pl["Player"]:
                found = True
                side = pl["Side"]
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
        if utils.is_time_expire(self.req.Move["Timestamp"], 900):
            self.error.raiseExp("Timeout")
        if len(self.game.Moves) > 1:
            if self.req.Move["Sequence"] != self.game.Moves[-1]["Sequence"] + 1:
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
        if not (self.game.Config.Plus["Enable"] and self.game.Config.Early["Enable"]):
            return True
        if self.kai.Value == self.step_value:
            if self.game.Config.Kingzpits["Enable"] and (
                self.kai.Index in self.game.Config.Kingzpits["Value"]
            ):
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
            elif self.game.Config.Kingzpits["Enable"] and (
                self.prev in self.game.Config.Kingzpits["Value"]
            ):
                self.prev = -1
                return True
            elif (
                self.game.Board.Pits[self.prev].Value % self.game.Config.Early["Value"]
                == 0
            ):
                side = self.game.Board.Pits[self.prev].Side
                value = self.game.Board.Store[side][str(side)]
                self.game.Board.Store[side] = {
                    str(side): value + self.game.Board.Pits[self.prev].Value
                }
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
            if (
                self.game.Config.Early["Enable"]
                and self.game.Config.Early["Value"] != 0
            ) and (
                self.game.Board.Pits[index].Value % self.game.Config.Early["Value"] == 0
            ):
                side = self.game.Board.Turn
                value = self.game.Board.Store[side][str(side)]
                self.game.Board.Store[side] = {
                    str(side): value + self.game.Board.Pits[index].Value
                }
                self.game.Board.Pits[index].Value = 0
                self.captureplus["Active"] = False
                if self.prev == index:
                    self.prev = -1
        return True

    def save_to_store(self, side, seeds):
        value = self.game.Board.Store[side][str(side)]
        self.game.Board.Store[side] = {str(side): value + seeds}

    def capture_action(self):
        if self.state == internal.State.MOVE_CAPTURE:
            index = self.kai.Index
            side = self.game.Board.Turn
            value = 0
            pondi = False
            if (self.game.Config.Kingzpits["Enable"]) and (
                index in self.game.Config.Kingzpits["Value"]
            ):
                value = self.game.Board.Pits[index].Share[side][str(side)]
                self.game.Board.Pits[index].Share[side] = {str(side): value + 1}
                pondi = True
            else:
                # pause = input("pause:")
                # print("pause", "base.capture_action:", index)
                self.save_to_store(side, self.game.Board.Pits[index].Value)
                self.game.Board.Pits[index].Value = 0
            if self.game.Config.Relay["Enable"] and ((value > 0) or pondi):
                self.state = internal.State.MOVE_PROGRESS
            else:
                self.state = internal.State.MOVE_END
                return False
        return True

    def update_next_turn(self):
        self.game.Board.Turn += 1
        if self.game.Board.Turn >= self.game.Config.Nside:
            self.game.Board.Turn = 0
        return True

    def update_moves2games(self):
        mvx = self.req.Move
        self.game.Moves.append(mvx)
        return True

    def do_roundsup(self):
        self.checkout_shares2store()
        self.checkout_allpits()
        self.checkin_allpits()
        return True

    def checkin_allpits(self):
        seeds = self.game.Config.Nseeds
        for pit in self.game.Board.Pits:
            if self.game.Config.Kingzpits["Enable"] and (
                pit.Index in self.game.Config.Kingzpits["Value"]
            ):
                pass
            else:
                value = self.game.Board.Store[pit.Side][str(pit.Side)]
                # print("checkin_allpits: value", pit.Index, pit.Side)
                if value >= seeds:
                    pit.Active = True
                    pit.Value = seeds
                    value -= seeds
                    self.game.Board.Store[pit.Side][str(pit.Side)] = value
                else:
                    pit.Active = False
                    pit.Value = 0
        return True

    def checkout_allpits(self):
        for pit in self.game.Board.Pits:
            if self.game.Config.Kingzpits["Enable"] and (
                pit.Index in self.game.Config.Kingzpits["Value"]
            ):
                pass
            elif pit.Active:
                print("checkout_allpits: save_to_store", pit.Index, pit.Side, pit.Value)
                self.save_to_store(pit.Side, pit.Value)
                pit.Value = 0
        return True

    def checkout_shares2store(self):
        if self.game.Config.Kingzpits["Enable"]:
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

                self.game.Board.Pits[index].Value == rem_seeds if rem_seeds > 0 else 0
        return True

    def check_roundsup(self, endd=False):
        side = self.game.Board.Turn
        # npits = self.game.Config.PitsPerSide
        nactive = 0
        for pit in self.game.Board.Pits:
            if self.game.Config.Kingzpits["Enable"] and (
                pit.Index in self.game.Config.Kingzpits["Value"]
            ):
                pass
            elif pit.Active and (side == pit.Side) and (pit.Value > 0):
                nactive += 1

        if endd:
            return nactive == 0
        elif nactive == 0:
            return self.do_roundsup()

        return False

    def check_gameend(self):
        if self.check_roundsup(True):
            self.game.Status = "done"
        return True

    @abstractmethod
    def step(self):
        pass
