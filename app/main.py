import socket  # noqa: F401
import threading

store = {}  # shared by all client threads


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
            store[items[1]] = items[2]
            connection.sendall(b"+OK\r\n")
        elif command == b"GET":
            value = store.get(items[1])
            if value is None:
                connection.sendall(b"$-1\r\n")
            else:
                connection.sendall(b"$%d\r\n%s\r\n" % (len(value), value))
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
