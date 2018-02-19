# -*- coding: utf-8 -*-
import random
import pickle
from tcp_packet import TCPPacket
import socket
import sys
from tcp_packet import TCP
def main():
    client = TCP()
    client.connect()
    client.send("hello me")


if __name__ == '__main__':
    main()
