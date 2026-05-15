from enum import Enum


class State(Enum):
    MOVE_UNKNOWN = 0
    MOVE_VALIDATION = 1
    MOVE_START = 2
    MOVE_PROGRESS = 3
    MOVE_CAPTURE = 4
    MOVE_END = 5
    MOVE_ERROR = 6
    MOVE_ROUNDUP = 7
    MOVE_GAMEOVER = 8
