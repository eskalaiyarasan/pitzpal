import ast
import json
import logging
import sys
import traceback
from datetime import datetime, timedelta
from datetime import timezone as dt_timezone

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from pitzpalgame import move, toss
from pitzpalgame import newgame as ng

from .models import PitzpalGame

logger = logging.getLogger(__name__)


def check_and_handle_timeout(z):
    """
    Checks if 900 seconds have passed since the last move's timestamp.
    If expired, marks the game as abandoned. Returns True if expired, False otherwise.
    """
    y = z.game
    if y.get("Status") in ["done", "abandoned"]:
        return y["Status"] == "abandoned"

    moves = y.get("Moves", [])
    if moves:
        try:
            last_move = moves[-1]
            timestamp_str = last_move["Timestamp"]
            clean_ts_str = timestamp_str.rstrip("Z")
            last_move_dt = datetime.strptime(clean_ts_str, "%Y-%m-%dT%H:%M:%S.%f")
            last_move_dt = timezone.make_aware(last_move_dt, dt_timezone.utc)

            if timezone.now() > last_move_dt + timedelta(seconds=900):
                y["Status"] = "done"
                z.game = y
                z.save()
                return True
        except (KeyError, ValueError, IndexError) as e:
            print(f"Timeout parsing error: {e}")
            return False
    return False


def start_game(request):
    if request.method == "POST":
        logger.info(f"enter {request}")
        data = json.loads(request.body)
        data["Players"] = [
            str(request.user.username),
            "Computer-1ae4de1c-4ac5-3e42ec2d59e0",
        ]
        x = ng.newgame.from_json(data)
        y = x.build()
        new_game = PitzpalGame.objects.create(player1=request.user, game=y)
        # Return only the GameID as requested
        logger.info(f"exit {y}")
        return JsonResponse(
            {"GameID": str(new_game.id), "Board": y["Board"], "Status": y["Status"]}
        )


def toss_action(request, game_id):
    if request.method in ["POST", "GET"]:
        logger.info(f"enter {request}")
        z = get_object_or_404(PitzpalGame, id=game_id)
        y = z.game
        ret = {
            "GameID": game_id,
            "Board": y["Board"],
            "Status": y["Status"],
            "Error": {"Value": 0},
        }
        if y["Status"] == "toss":
            toss.action(y)
            z.game = y
            z.save()
            ret["Toss"] = y["Toss"]
        else:
            ret["Toss"] = y["Toss"]
            ret["Error"] = {"Value": 17}
        logger.info(f"exit {ret}")
        return JsonResponse(ret)


def update_stat_at_end(request, y, out):
    logger.info(f"enter {request}")
    is_win = move.updateReport(y, out, str(request.user.username))
    if is_win[0]:
        request.user.complete_game(is_win=is_win[1], difficulty=y["Level"]["Value"])


def make_comp_move(request, game_id):
    if request.method == "POST":
        logger.info(f"enter {request}")
        z = get_object_or_404(PitzpalGame, id=game_id)
        y = z.game
        ret = {
            "GameID": game_id,
            "Board": y["Board"],
            "Toss": y["Toss"],
            "Status": y["Status"],
            "Moves": y["Moves"],
            "Error": {"Value": 14},
        }
        try:
            turn = y["Board"]["Turn"]
            if y["Toss"][turn]["Player"] == "Computer-1ae4de1c-4ac5-3e42ec2d59e0":
                req = move.createreq(y)
                detail = []
                outdata = move.move(y, req, detail)
                logger.info(f"move: {outdata}")
                out = ast.literal_eval(outdata)
                try:
                    update_stat_at_end(request, y, out)
                    if "Report" in out:
                        ret["Report"] = out["Report"]
                except Exception as e:
                    print(f"update_stat_at_end {e}")
                y = out
                ret.update(
                    {
                        "GameID": game_id,
                        "Board": y["Board"],
                        "Toss": y["Toss"],
                        "Status": y["Status"],
                        "Moves": y["Moves"],
                        "Detail": detail,
                        "Error": {"Value": 0},
                    }
                )
        except Exception as e:
            print(f"exception {e}")
            traceback.print_exc(limit=10, file=sys.stdout)
            y = {}
        if len(y) > 0:
            z.game = y
            z.save()
        logger.info(f"exit {ret}")
        return JsonResponse(ret)


def make_resign_move(request, game_id):
    if request.method == "POST":
        logger.info(f"enter {request}")
        z = get_object_or_404(PitzpalGame, id=game_id)
        y = z.game
        try:
            player = str(request.user.username)
            out = move.resign(y, player)
            y = out
        except Exception as e:
            print(f"exception {e}")
            y = {}
        if len(y) > 0:
            z.game = y
            z.save()
            logger.info(f"exit {y}")
            return JsonResponse(
                {
                    "GameID": game_id,
                    "Board": y["Board"],
                    "Toss": y["Toss"],
                    "Status": y["Status"],
                    "Error": {"Value": 0},
                    "Moves": y["Moves"],
                }
            )
        else:
            y = z.game
            logger.info(f"exit {y}")
            return JsonResponse(
                {
                    "GameID": game_id,
                    "Board": y["Board"],
                    "Toss": y["Toss"],
                    "Status": y["Status"],
                    "Error": {"Value": 14},
                    "Moves": y["Moves"],
                }
            )


def make_move(request, game_id):
    if request.method == "POST":
        logger.info(f"enter {request}")
        data = json.loads(request.body)
        z = get_object_or_404(PitzpalGame, id=game_id)
        y = z.game
        ret = {
            "GameID": data["GameID"],
            "Board": y["Board"],
            "Toss": y["Toss"],
            "Status": y["Status"],
            "Error": {"Value": 14},
            "Moves": y["Moves"],
        }
        try:
            turn = y["Board"]["Turn"]
            if y["Toss"][turn]["Player"] == str(request.user.username):
                req = data
                detail = []
                outdata = move.move(y, req, detail)
                logger.info(f"move {outdata}")
                out = ast.literal_eval(outdata)
                try:
                    update_stat_at_end(request, y, out)
                    if "Report" in out:
                        ret["Report"] = out["Report"]
                except Exception as e:
                    print(f"update_stat_at_end {e}")
                    traceback.print_exc(limit=10, file=sys.stdout)
                y = out
                ret.update(
                    {
                        "GameID": data["GameID"],
                        "Board": y["Board"],
                        "Toss": y["Toss"],
                        "Status": y["Status"],
                        "Error": {"Value": 0},
                        "Moves": y["Moves"],
                        "Detail": detail,
                    }
                )
        except Exception as e:
            print(f"exception {e}")
            traceback.print_exc(limit=10, file=sys.stdout)
            y = {}
        if len(y) > 0:
            z.game = y
            z.save()
        logger.info(f"exit {ret}")
        return JsonResponse(ret)


def refresh(request, game_id):
    if request.method in ["POST", "GET"]:
        logger.info(f"enter {request}")
        z = get_object_or_404(PitzpalGame, id=game_id)
        y = z.game
        ret = {
            "GameID": game_id,
            "Board": y["Board"],
            "Error": {"Value": 0},
            "Status": y["Status"],
        }
        if y["Status"] != "toss":
            ret["Toss"] = y["Toss"]
            ret["Moves"] = y["Moves"]
        logger.info(f"exit {ret}")
        return JsonResponse(ret)


@login_required
def game_list(request):
    # Get all games where the user is player1 or player2
    logger.info(f"enter {request}")
    games = PitzpalGame.objects.filter(
        player1=request.user
    ) | PitzpalGame.objects.filter(player2=request.user)
    return render(request, "home/game_list.html", {"games": games.order_by("-id")})


@login_required
def delete_game(request, game_id):
    if request.method == "POST":
        logger.info(f"enter {request}")
        game = get_object_or_404(PitzpalGame, id=game_id, player1=request.user)
        game.delete()
        messages.success(request, "Game deleted successfully.")
    return redirect("game_list")
