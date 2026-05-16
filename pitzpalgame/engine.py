from . import movereq
from .algo import base as base
from .algo import classic as classic
from .algo import error
from .algo import internal as internal


def move(game_in, req: movereq.movereq):
    _algo = None
    if game_in.Config.Algorithm["Value"].strip() == "classic":
        print("classic is chosen")
        _algo = classic.classic(game_in, req)
    else:
        error.error().raiseExp("IllegalGameType")

    if _algo is not None:
        while _algo.state != internal.State.MOVE_END:
            _algo.step()
            if _algo.state == internal.State.MOVE_ERROR:
                error.error().raiseExp("IllegalMove")

        return _algo.result()
    else:
        error.error().raiseExp("IllegalOptions")
