from multiprocessing.connection import Listener
from os import getuid

SOCKET_FILE = "/var/run/user/{0}/bcproxy-tf-scripts-chat".format(getuid())

with Listener(SOCKET_FILE, "AF_UNIX") as listener:
    print("listening to connections on {0}".format(SOCKET_FILE))

    while True:
        with listener.accept() as conn:
            print("connection opened", listener.last_accepted)

            while True:
                try:
                    msg = conn.recv()
                    print(msg)
                except EOFError:
                    print("connection closed")
                    break
