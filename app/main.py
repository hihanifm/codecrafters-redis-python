import socket  # noqa: F401
import threading


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
