import ast
import copy
import json
import logging
from abc import abstractmethod
from datetime import timedelta

from django.utils import timezone  # Used to check actual server time cleanly

from . import base_utils as base
from . import error
from . import internal as internal

logger = logging.getLogger("pitzpalgame")


class core(base.base_utils):
    def __init__(self, game_in, req):
        logger.debug("enter")
        super().__init__(game_in)
        self.state = internal.State.MOVE_VALIDATION
        self.active = False
        self.req = req
        self.step_value = 1
        self.kai = None
        self.captured_sucess = False

        self.nRound = 0
        self.prechecks = [
            self.is_game_active,
            self.is_valid_req,
            self.is_valid_turn,
            self.is_valid_pit,
        ]
        self.start = [self.start_move]
        self.progress = [
            self.progress_check_capture,
        ]
        self.capture = [
            self.capture_action,
        ]
        self.end = [
            self.update_next_turn,
            self.check_roundsup,
            self.check_gameend,
        ]
        self.roundsup = [
            self.checkout_allpits,
            self.checkin_allpits,
        ]
        self.error = error.error()
        logger.debug("exit")
        # print(str(self.req))

    def step_base(self):
        logger.debug("enter")
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
            if callable(cond):
                if not cond():
                    break
        logger.debug("exit")

    def result(self, detail=[]):
        logger.debug("enter")
        self.step_base()
        self.update_moves2games()
        detail[:] = copy.deepcopy(self.detail)
        # pause = input("pause:")
        # print("pause", self.game)
        logger.debug(f"exit {self.game}")
        return str(self.game)

    def is_game_active(self):
        logger.debug("enter")
        if self.game.Status != "active":
            self.error.raiseExp("GameEndedAgo")
        if (
            (self.game.Config.Nside <= 0)
            or (self.game.Config.Nseeds <= 0)
            or (self.game.Config.PitsPerSide <= 0)
        ):
            self.error.raiseExp("IllegalConfig")
        logger.debug("exit True")
        return True

    def is_valid_turn(self):
        logger.debug("enter")
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
                logger.debug("exit True")
                return True
        else:
            self.error.raiseExp("IllegalAccess")
        logger.debug("exit False")
        return False

    def is_valid_req(self):
        logger.debug("enter")
        if internal.is_time_expire(self.req.Move["Timestamp"], 900):
            self.error.raiseExp("Timeout")
        if len(self.game.Moves) > 1:
            if self.req.Move["Sequence"] != self.game.Moves[-1]["Move"]["Sequence"] + 1:
                self.error.raiseExp("IllegalMove")

        if self.req.Move["Index"] >= self.max_index or self.req.Move["Index"] < 0:
            self.error.raiseExp("IllegalOptions")
        side = self.req.Move["Index"] // self.game.Config.PitsPerSide
        if self.game.Board.Turn != side:
            self.error.raiseExp("IllegalMove")
        logger.debug("exit True")
        return True

    def is_valid_pit(self):
        logger.debug("enter")
        index = self.req.Move["Index"]
        found = False
        for pit in self.game.Board.Pits:
            if pit.Active and pit.Index == index:
                found = True
                if pit.Value <= 0:
                    self.error.raiseExp("IllegalMove")
        if not found:
            self.error.raiseExp("IllegalMove")
        logger.debug("exit True")
        return True

    def start_move(self):
        logger.debug("enter")
        index = self.req.Move["Index"]
        self.captured_sucess = False
        self.detail = []
        self.nRound = 1
        for pit in self.game.Board.Pits:
            if pit.Active and pit.Index == index:
                self.kai = copy.deepcopy(pit)
                self.set_pit_value(pit.Index, 0)
                logger.info(f"{index}<- 0 ")
                break
        self.state = internal.State.MOVE_PROGRESS
        logger.debug("exit True")
        return True

    def progress_check_capture(self):
        logger.debug("enter")
        if (self.kai.Value == 0) and self.get_pit_value(self.kai.Index) == 0:
            self.state = internal.State.MOVE_CAPTURE
            logger.debug("exit False")
            return False
        logger.debug("exit True")
        return True

    def capture_action(self):
        logger.debug("enter")
        index = self.kai.Index
        if self.get_pit_value(index) > 0:
            self.captured_sucess = True
            self.move_to_store(index, self.game.Board.Turn)
        self.state = internal.State.MOVE_END
        logger.debug("exit True")
        return True

    def update_next_turn(self):
        logger.debug("enter")
        self.game.Board.Turn += 1
        if self.game.Board.Turn >= self.game.Config.Nside:
            self.game.Board.Turn = 0
        logger.debug("exit True")
        return True

    def update_moves2games(self):
        logger.debug("enter")
        mvx = {"Move": self.req.Move, "Details": self.detail}
        self.game.Moves.append(mvx)
        logger.debug("exit True")
        return True

    def do_roundsup(self):
        logger.debug("enter")
        self.detail.append({"RoundUp": True})
        self.nRound += 1
        for cond in self.roundsup:
            if callable(cond):
                cond()
        logger.debug("exit True")
        return True

    def checkin_allpits(self):
        logger.debug("enter")
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
        logger.debug("exit True")
        return True

    def checkout_allpits(self):
        logger.debug("enter")
        for pit in self.game.Board.Pits:
            if (not pit.Public) and pit.Active:
                # print("checkout_allpits: save_to_store", pit.Index, pit.Side, pit.Value)
                self.move_to_store(pit.Index)
        logger.debug("exit True")
        return True

    def check_roundsup(self):
        logger.debug("enter")
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
            else:
                print("do_roundsup:", pit.Public, pit.Active, pit.Side, pit.Value)

        if nactive == 0:
            rett = self.do_roundsup()
            logger.debug(f"exit : {rett}")
            return rett
        logger.debug("exit False")
        return False

    def is_gameover(self):
        logger.debug("enter")
        for side in range(self.game.Config.Nside):
            nactive = 0
            for pit in self.game.Board.Pits:
                if (
                    (not pit.Public)
                    and pit.Active
                    and (side == pit.Side)
                    and (pit.Value > 0)
                ):
                    nactive += 1
            if nactive == 0:
                logger.debug("exit True")
                return True
        logger.debug("exit False")
        return False

    def check_gameend(self):
        logger.debug("enter")
        if self.is_gameover():
            self.checkout_allpits()
            self.game.Status = "done"
        logger.debug("exit True")
        return True

    @abstractmethod
    def step(self):
        pass
