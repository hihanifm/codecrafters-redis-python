import socket  # noqa: F401
import threading

from app.commands import execute
from app.resp import parse_command


def handle_client(connection):
    while True:
        data = connection.recv(1024)
        if not data:  # client closed the connection
            connection.close()
            break
        name, *args = parse_command(data)
        connection.sendall(execute(name, args))


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)

    while True:
        connection, _ = server_socket.accept()  # wait for client
        threading.Thread(target=handle_client, args=(connection,)).start()


if __name__ == "__main__":
    main()
