# -*- coding: utf-8 -*-
from TCP_over_UDP import TCP
import sys
from bcolors import bcolors
WAIT_FOR_CLOSING = 5


def main():
    server = TCP()
    server.own_socket.bind(("127.0.0.1", 10000))
    server.central_receive()
    server.listen(3)
    connection = server.accept()
    print server.recv(connection)
    name = raw_input("Type your name here --> ").capitalize()
    to_send = "NAME: MESSAGE"
    print bcolors.WARNING + "Waiting to receive message from friend" + bcolors.ENDC
    while server.status and to_send.split(' ')[1].upper() != "EXIT":
        answer = server.recv(connection)
        if answer == "Disconnected":
            break
        else:
            print bcolors.OKBLUE + answer + bcolors.ENDC
        to_send = name + ": " + raw_input(bcolors.OKGREEN + name + ": " + bcolors.ENDC)
        if to_send.split(' ')[1].upper() == "EXIT":
            server.close()
            print "Closed"
            break
        server.send(to_send, connection)
    print "Finished"
    sys.exit()


if __name__ == '__main__':
    main()
