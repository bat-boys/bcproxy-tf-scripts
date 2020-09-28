from multiprocessing.connection import Client
from os import getuid
from tf import eval  # type: ignore

from utils import tfprint

SOCKET_FILE = "/var/run/user/{0}/bcproxy-tf-scripts-chat".format(getuid())
CONN = Client(SOCKET_FILE, "AF_UNIX")


def trigger(msg: str):
    CONN.send(msg)


def setup():
    CONN.send("testing connection")
    eval("/def -mglob -q -t'chan_party: *' chat_party = /python_call chat.trigger \%-1")
    eval("/def -mglob -q -t'chan_tell: *' chat_tell = /python_call chat.trigger \%-1")
    tfprint("Loaded chat.py")


setup()
