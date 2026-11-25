import socket  # noqa: F401
import threading
import time

store = {}  # shared by all client threads
store_lock = threading.Lock()  # guards every access to store


def now_ms():
    return time.monotonic() * 1000


def handle_client(connection):
    while True:
        data = connection.recv(1024)
        if not data:  # client closed the connection
            connection.close()
            break
        # *N\r\n$len\r\nitem\r\n... -> items are every 2nd part after the array header
        items = data.split(b"\r\n")[2::2]
        command = items[0].upper()
        if command == b"PING":
            connection.sendall(b"+PONG\r\n")
        elif command == b"ECHO":
            arg = items[1]
            connection.sendall(b"$%d\r\n%s\r\n" % (len(arg), arg))
        elif command == b"SET":
            deadline = 0  # 0 = no expiry
            if len(items) > 4 and items[3].upper() == b"PX":
                px = int(items[4])
                if px <= 0:
                    connection.sendall(b"-ERR invalid expire time in 'set' command\r\n")
                    continue
                deadline = now_ms() + px
            with store_lock:
                store[items[1]] = (items[2], deadline)
            connection.sendall(b"+OK\r\n")
        elif command == b"GET":
            value = None
            with store_lock:  # check + delete must be one step
                entry = store.get(items[1])
                if entry is not None:
                    value, deadline = entry
                    if deadline != 0 and now_ms() > deadline:  # expired: lazy delete
                        del store[items[1]]
                        value = None
            if value is None:
                connection.sendall(b"$-1\r\n")
            else:
                connection.sendall(b"$%d\r\n%s\r\n" % (len(value), value))
        elif command == b"RPUSH":
            with store_lock:  # get-or-create + append must be one step
                entry = store.get(items[1])
                if entry is None:
                    entry = ([], 0)  # new list, no expiry
                    store[items[1]] = entry
                entry[0].append(items[2])
                length = len(entry[0])
            connection.sendall(b":%d\r\n" % length)
        else:
            connection.sendall(b"-ERR unknown command '%s'\r\n" % items[0])


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
