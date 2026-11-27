import socket  # noqa: F401
import threading
import time
from collections import deque
from itertools import islice

from app.ranges import redis_range_to_python_slice

store = {}  # shared by all client threads
store_lock = threading.Lock()  # guards every access to store


def now_ms():
    return time.monotonic() * 1000


def get_or_create_list(key):
    # caller must hold store_lock
    record = store.get(key)
    if record is None:
        record = (deque(), 0)  # new list, no expiry; O(1) push at both ends
        store[key] = record
    return record[0]


def handle_client(connection):
    while True:
        data = connection.recv(1024)
        if not data:  # client closed the connection
            connection.close()
            break
        # *N\r\n$len\r\nitem\r\n... -> values are every 2nd part after the array header
        name, *args = data.split(b"\r\n")[2::2]
        command = name.upper()
        if command == b"PING":
            connection.sendall(b"+PONG\r\n")
        elif command == b"ECHO":
            arg = args[0]
            connection.sendall(b"$%d\r\n%s\r\n" % (len(arg), arg))
        elif command == b"SET":
            deadline = 0  # 0 = no expiry
            if len(args) > 3 and args[2].upper() == b"PX":
                px = int(args[3])
                if px <= 0:
                    connection.sendall(b"-ERR invalid expire time in 'set' command\r\n")
                    continue
                deadline = now_ms() + px
            with store_lock:
                store[args[0]] = (args[1], deadline)
            connection.sendall(b"+OK\r\n")
        elif command == b"GET":
            value = None
            with store_lock:  # check + delete must be one step
                record = store.get(args[0])
                if record is not None:
                    value, deadline = record
                    if deadline != 0 and now_ms() > deadline:  # expired: lazy delete
                        del store[args[0]]
                        value = None
            if value is None:
                connection.sendall(b"$-1\r\n")
            else:
                connection.sendall(b"$%d\r\n%s\r\n" % (len(value), value))
        elif command == b"RPUSH":
            with store_lock:  # get-or-create + append must be one step
                items = get_or_create_list(args[0])
                items.extend(args[1:])  # all values in one step
                length = len(items)
            connection.sendall(b":%d\r\n" % length)
        elif command == b"LPUSH":
            with store_lock:  # get-or-create + prepend must be one step
                items = get_or_create_list(args[0])
                items.extendleft(args[1:])  # appendleft each in order: a b c -> [c, b, a]
                length = len(items)
            connection.sendall(b":%d\r\n" % length)
        elif command == b"LRANGE":
            start, stop = int(args[1]), int(args[2])
            with store_lock:
                record = store.get(args[0])
                if record:
                    py_start, py_stop = redis_range_to_python_slice(start, stop, len(record[0]))
                    # deque has no slicing; islice walks from the left (O(stop), like Redis's O(S+N))
                    # list() copies, so we can send after releasing the lock
                    values = list(islice(record[0], py_start, py_stop))
                else:
                    values = []
            reply = b"*%d\r\n" % len(values)
            for v in values:
                reply += b"$%d\r\n%s\r\n" % (len(v), v)
            connection.sendall(reply)
        else:
            connection.sendall(b"-ERR unknown command '%s'\r\n" % name)


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment the code below to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)

    while True:
        connection, _ = server_socket.accept()  # wait for client
        threading.Thread(target=handle_client, args=(connection,)).start()


if __name__ == "__main__":
    main()
