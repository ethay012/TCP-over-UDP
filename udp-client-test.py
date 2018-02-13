# -*- coding: utf-8 -*-
import random
import pickle
from tcp_packet import TCPPacket
import socket
import sys

SMALLEST_STARTING_SYN = 0
HIGHEST_STARTING_SIN = 4294967295


def gen_starting_syn_num():
    return random.randint(SMALLEST_STARTING_SYN, HIGHEST_STARTING_SIN)


def connection(my_socket, dst_ip):
    hostname = socket.gethostname()
    src_ip = socket.gethostbyname(hostname)
    my_socket.sendto(src_ip, dst_ip)

def connect(udp_socket):

    ip = "127.0.0.1"
    x = TCPPacket(6594, 3200)
    port = x.dst_port
    x = pickle.dumps(x)
    udp_socket.sendto(x, (ip, port))
    y, addr = udp_socket.recvfrom(1024)
    y= pickle.loads(y)
    print y
    temp = y.syn + 1
    y.syn = y.ack + 1
    y.ack = y.syn
    y = pickle.dumps(y)
    udp_socket.sendto(y, (addr, x.dst_port))


def main():

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = ('localhost', 10000)
    message = 'This is the message.  It will be repeated.'

    try:

        x = TCPPacket(6594, 3200)
        port = x.dst_port
        x = pickle.dumps(x)

        # Send data
        print >> sys.stderr, 'sending "%s"' % x
        sent = sock.sendto(x, server_address)

        # Receive response
        print >> sys.stderr, 'waiting to receive'
        y, server = sock.recvfrom(4096)
        y = pickle.loads(y)
        print y
        temp = y.syn + 1
        y.syn = y.ack + 1
        y.ack = y.syn
        y = pickle.dumps(y)
        sock.sendto(y, server_address)

    finally:
        print >> sys.stderr, 'closing socket'
        sock.close()

if __name__ == '__main__':
    main()
