# -*- coding: utf-8 -*-
import random
import pickle
from tcp_packet import TCPPacket
import socket
import sys
from tcp_packet import TCP


SMALLEST_STARTING_SYN = 0
HIGHEST_STARTING_SIN = 4294967295


def main():
    # server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # server.bind("localhost", 10000)
    # while True:
    #     data, address = server.recvfrom(1024)
    #     print data
    server = TCP()
    server.listen()
    while(massege!="exsit")
        print server.recv()
        server.send(raw_input("enter massage-->"))
    sys.exsit()


if __name__ == '__main__':
    main()
