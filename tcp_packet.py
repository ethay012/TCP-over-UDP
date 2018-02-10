# -*- coding: utf-8 -*-
import random


class TCPPacket(object):
    """
    Add Documentation here
    """
    SMALLEST_STARTING_SYN = 0
    HIGHEST_STARTING_SYN = 4294967295

    def __init__(self, src_port, dst_port):
        self.src_port = src_port  # 16bit
        self.dst_port = dst_port  # 16bit
        self.syn = TCPPacket.gen_starting_syn_num()  # 32bit
        self.ack = 0  # 32bit
        self.data_offset = 0  # 4 bits
        self.reserved_field = 0  # 3bits saved for future use must be zero assert self.reserved_field = 0
        #FLAGS
        self.flag_ns = 0  # 1bit
        self.flag_cwr = 0  # 1bit
        self.flag_ece = 0  # 1bit
        self.flag_urg = 0  # 1bit
        self.flag_ack = 0  # 1bit
        self.flag_psh = 0  # 1bit
        self.flag_rst = 0  # 1bit
        self.flag_syn = 0  # 1bit
        self.flag_fin = 0  # 1bit
        #window size
        self.window_size = 0  # 16bit
        #checksum
        self.checksum = 0  # 16bit
        #urgent pointer
        self.urgent_pointer = 0  # 16bit
        #options
        self.options = 0  # 0-320bits, divisible by 32
        #padding - TCP packet must be on a 32bit boundary this ensures that it is the padding is filled with 0's
        self.padding = 0  # as much as needed

    def __repr__(self):
        return "TCPpacket({0}, {1})".format(self.src_port, self.dst_port)

    def __str__(self):
        return "Source Port: %d, Destination Port:: %d, SYN Number: %d" % (self.src_port, self.dst_port, self.syn)

    @staticmethod
    def gen_starting_syn_num():
        return random.randint(TCPPacket.SMALLEST_STARTING_SYN, TCPPacket.HIGHEST_STARTING_SYN)


#NOT SURE IF I NEED TO INHERIT THIS MAYBE TCP WILL JUST BE A HELP CLASS
class TCP(TCPPacket):

    def __init__(self, src_port, dst_port):
        super(TCP, self).__init__(src_port, dst_port)

    @staticmethod
    def checksum():
        pass

    @staticmethod
    def listen():
        pass

    @staticmethod
    def bind():
        pass