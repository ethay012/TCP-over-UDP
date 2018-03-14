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
            for connection in connections:
                sock.send('[b][color=#cc0000]' + str(address[IP]) + ":" + str(address[PORT])
                          + " Disconnected." + '[/b][/color]', connection)
            connections.remove(address)
            break
        else:
            with connections_lock:
                for connection in connections:
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
        for connection in connections:
            print connection
            sock.send('[b][color=#00B200]' + str(address[0]) + ":" + str(address[1]) + " Connected."
                      + '[/b][/color]', connection)

    sys.exit()




if __name__ == "__main__":
    main()

