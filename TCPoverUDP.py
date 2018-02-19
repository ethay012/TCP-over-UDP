# -*- coding: utf-8 -*-
import socket
import random
import pickle

from tcp_packet import TCPPacket


SMALLEST_STARTING_SEQ = 0
HIGHEST_STARTING_SEQ = 4294967295


def gen_starting_seq_num():
    return random.randint(SMALLEST_STARTING_SEQ, HIGHEST_STARTING_SEQ)


def connection(my_socket, dst_ip):
    hostname = socket.gethostname()
    src_ip = socket.gethostbyname(hostname)
    my_socket.sendto(src_ip, dst_ip)


def main():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packet = TCPPacket()
    print packet.seq
    packet_string = pickle.dumps(packet)
    udp_socket.sendto(packet_string, ("127.0.0.1", 5566))
    x = udp_socket.recv(1024)
    print x


if __name__ == '__main__':
    main()