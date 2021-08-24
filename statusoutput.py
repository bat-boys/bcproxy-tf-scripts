from collections import deque  # type: ignore
import dill  # type: ignore
from multiprocessing.connection import Listener
from os import getuid
from threading import Timer
from typing import cast

from utils import colorize

STATUS_SOCKET_FILE = "/var/run/user/{0}/bcproxy-tf-scripts-status".format(getuid())

from statustypes import Message, State, StatusType


def tickStr(i: int) -> str:
    return "{0} {1}".format(i, "#" * i)


def draw(state: State):
    print("\033c", end="")  # clear screen
    print(
        "tick  {0:<14} hb {1:<6}".format(tickStr(state.tick), tickStr(state.heartbeat))
    )
    print("res  {0}".format(state.resists))


def doHeartbeat(resetHeartbeat: bool, resetTick: bool):
    global state

    heartbeat = state.heartbeat - 1
    if resetHeartbeat == True or (state.stethoscope == False and heartbeat < 1):
        heartbeat = 3

    stethoscope = state.stethoscope
    if resetHeartbeat == True:
        stethoscope = True
    if heartbeat < -10:
        heartbeat = 3
        stethoscope = False

    tick = state.tick
    if heartbeat == 3:
        tick = state.tick - 1
    if tick < 1 or resetTick == True:
        tick = 10

    if resetHeartbeat == True or resetTick == True:
        state.heartbeatTimer.cancel()

    heartbeatTimer = Timer(1, doHeartbeat, (False, False))
    state = state._replace(
        heartbeat=heartbeat,
        heartbeatTimer=heartbeatTimer,
        tick=tick,
        stethoscope=stethoscope,
    )
    heartbeatTimer.start()
    draw(state)


def receiveMessage(msg: Message):
    global state
    if msg.statusType == StatusType.RESISTS and msg.message is not None:
        state = state._replace(resists=msg.message)
    elif msg.statusType == StatusType.HEARTBEAT_RESET:
        doHeartbeat(True, False)
    elif msg.statusType == StatusType.TICK_RESET:
        doHeartbeat(False, True)
    draw(state)


heartbeatTimer = Timer(1, doHeartbeat, (False, False))
state = State("", 3, 10, heartbeatTimer, False)
heartbeatTimer.start()

with Listener(STATUS_SOCKET_FILE, "AF_UNIX") as listener:
    while True:
        with listener.accept() as conn:
            try:
                msg = cast(Message, dill.loads(conn.recv_bytes()))
                receiveMessage(msg)
            except EOFError:
                None
