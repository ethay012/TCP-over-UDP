# -*- coding: utf-8 -*-
from TCP_over_UDP import TCP
import threading
import sys


IP = 0
PORT = 1
connections = []
connections_lock = threading.Lock()


def handler(sock, address):
    while True:
        data = sock.recv(address)

        if data == "Disconnected":
            print str(address[IP]) + ":" + str(address[PORT]) + " Disconnected."
            connections.remove(address)
            print connections
            break
        else:
            with connections_lock:
                for connection in connections:
                    if connection != address:
                        sock.send(data, connection)


def main():
    print "Starting"

    sock = TCP()

    sock.own_socket.bind(('0.0.0.0', 10000))
    sock.listen(1)

    while True:
        address = sock.accept()
        connection_thread = threading.Thread(target=handler, args=(sock, address))
        connection_thread.daemon = True
        connection_thread.start()
        connections.append(address)
        print str(address[0]) + ":" + str(address[1]) + " Connected."

    sys.exit()




if __name__ == "__main__":
    main()

