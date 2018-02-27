import socket
import threading


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.listen(1)

    connections = []

    def handler(connection, address):
        while True:
            data = connection.recv(1024)
            for connection in connections:
                connection.send(data)
            if not data:
                break

    while True:
        connection, address = sock.accept()
        connection_thread = threading.Thread(target=handler, args=(connection, address))
        connection_thread.daemon = True
        connection_thread.start()
        connections.append(connection)
        print connections

if __name__ == "__main__":
    main()