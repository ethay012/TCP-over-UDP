# -*- coding: utf-8 -*-
from TCP_over_UDP import TCP
import sys
from bcolors import bcolors


def main():

    client = TCP()
    client.central_receive()
    client.connect()
    client.send("Hello me")
    name = raw_input("Type your name here --> ").capitalize()
    to_send = "NAME: MESSAGE"
    while True:
        to_send = name + ": " + raw_input(bcolors.OKGREEN + name + ": " + bcolors.ENDC)
        if to_send.split(' ')[1].upper() == "EXIT":
            client.close()
            print "Closed"
            break
        client.send(to_send)
        answer = client.recv()
        if answer == "Disconnected":
            break
        else:
            print bcolors.OKBLUE + answer + bcolors.ENDC
    print "Finished"
    sys.exit()


if __name__ == '__main__':
    main()
