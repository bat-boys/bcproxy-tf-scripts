from threading import Timer
from typing import Any, cast, Deque, FrozenSet, NamedTuple, Optional, Sequence

from utils import NoValue


class StatusType(NoValue):
    RESISTS = "resists"
    HEARTBEAT_RESET = "heartbeat_reset"
    TICK_RESET = "tick_reset"


class Message(NamedTuple):
    statusType: StatusType
    message: Any


class State(NamedTuple):
    resists: str
    heartbeat: int
    tick: int
    heartbeatTimer: Timer
    stethoscope: bool
