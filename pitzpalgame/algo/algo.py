import algo.base as base
import algo.classic as classic
import algo.internal as internal
import error
import movereq


def move(game_in, req: movereq.movereq):
    _algo = base.base(game_in, req)
    if game_in.Config.Algorithm["Value"].strip() == "classic":
        _algo = classic.classic(game_in, req)
    else:
        error.error().raiseExp("IllegalGameType")

    if _algo.active:
        while _algo.state != internal.State.MOVE_END:
            _algo.step()
            if _algo.state == internal.State.MOVE_ERROR:
                error.error().raiseExp("IllegalMove")
        return _algo.result()
    else:
        error.error().raiseExp("IllegalOptions")
