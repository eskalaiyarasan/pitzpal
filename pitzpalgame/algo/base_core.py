import ast
import copy
import json
from abc import abstractmethod
from datetime import timedelta

from django.utils import timezone  # Used to check actual server time cleanly

from . import base_utils as base
from . import error
from . import internal as internal


class core(base.base_utils):
    def __init__(self, game_in, req):
        super().__init__(game_in)
        self.state = internal.State.MOVE_VALIDATION
        self.active = False
        self.req = req
        self.step_value = 1
        self.kai = None
        self.captured_sucess = False
        self.skip_early = False
        self.prechecks = [
            self.is_game_active,
            self.is_valid_req,
            self.is_valid_turn,
            self.is_valid_pit,
        ]
        self.start = [self.start_move]
        self.progress = [
            self.progress_check_capture,
            self.progress_update_pit,
        ]
        self.capture = [
            self.capture_action,
        ]
        self.end = [
            self.update_next_turn,
            self.update_moves2games,
            self.check_roundsup,
            self.check_gameend,
        ]
        self.roundsup = [
            self.checkout_allpits,
            self.checkin_allpits,
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
        if internal.is_time_expire(self.req.Move["Timestamp"], 900):
            self.error.raiseExp("Timeout")
        if len(self.game.Moves) > 1:
            if self.req.Move["Sequence"] != self.game.Moves[-1]["Sequence"] + 1:
                self.error.raiseExp("IllegalMove")

        if self.req.Move["Index"] >= self.max_index or self.req.Move["Index"] < 0:
            self.error.raiseExp("IllegalOptions")
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
        self.captured_sucess = False
        for pit in self.game.Board.Pits:
            if pit.Active and pit.Index == index:
                self.kai = copy.deepcopy(pit)
                pit.Value = 0
        self.state = internal.State.MOVE_PROGRESS
        return True

    def progress_check_capture(self):
        if (self.kai.Value == 0) and self.get_pit_value(self.kai.Index) == 0:
            self.state = internal.State.MOVE_CAPTURE
            return False
        return True

    def capture_action(self):
        index = self.kai.Index
        if self.get_pit_value(index) > 0:
            self.captured_sucess = True
            self.move_to_store(index, self.game.Board.Turn)
        self.state = internal.State.MOVE_END
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
        for cond in self.roundsup:
            if callable(cond):
                cond()
        return True

    def checkin_allpits(self):
        seeds = self.game.Config.Nseeds
        for pit in self.game.Board.Pits:
            if not pit.Public:
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
            if (not pit.Public) and pit.Active:
                # print("checkout_allpits: save_to_store", pit.Index, pit.Side, pit.Value)
                self.move_to_store(pit.Index)
        return True

    def check_roundsup(self, endd=False):
        side = self.game.Board.Turn
        # npits = self.game.Config.PitsPerSide
        nactive = 0
        for pit in self.game.Board.Pits:
            if (
                (not pit.Public)
                and pit.Active
                and (side == pit.Side)
                and (pit.Value > 0)
            ):
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
