# -*- coding: utf-8 -*-
import random
import socket
import sys
import pickle


class TCPPacket(object):
    """
    Add Documentation here
    """
    SMALLEST_STARTING_SYN = 0
    HIGHEST_STARTING_SYN = 9000  # 4294967295

    def __init__(self):
        # self.src_port = src_port  # 16bit
        # self.dst_port = dst_port  # 16bit
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
        return "TCPpacket()"

    def __str__(self):
        return "SYN Number: %d, ACK Number: %d" \
               % (self.syn, self.ack)

    @staticmethod
    def gen_starting_syn_num():
        return random.randint(TCPPacket.SMALLEST_STARTING_SYN, TCPPacket.HIGHEST_STARTING_SYN)




#NOT SURE IF I NEED TO INHERIT THIS MAYBE TCP WILL JUST BE A HELP CLASS
class TCP():

    def __init__(self):
        #self.server_socket =
        pass


    @staticmethod
    def checksum():
        pass

    @staticmethod
    def listen(server_address=('localhost', 10000)):
        """ Server-side Handshake """
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Bind the socket to the port
        print >>sys.stderr, 'starting up on %s port %s' % server_address
        sock.bind(server_address)

        print >> sys.stderr, '\nwaiting to receive message'
        client_first_packet, address = sock.recvfrom(4096)
        client_first_packet = pickle.loads(client_first_packet)
        print "from client first: " + str(client_first_packet)
        print address
        server_first_packet = TCPPacket()
        server_first_packet.ack = client_first_packet.syn + 1
        print "server: " + str(server_first_packet)
        server_first_packet = pickle.dumps(server_first_packet)
        sock.sendto(server_first_packet, address)
        client_second_packet, addr = sock.recvfrom(1024)
        client_second_packet = pickle.loads(client_second_packet)

        print "from client last: ",
        print client_second_packet

        return sock, client_second_packet, server_first_packet

    @staticmethod
    def connect(server_address=('localhost', 10000)):

        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:

            client_first_packet = TCPPacket()
            print "client: " + str(client_first_packet)
            client_first_packet = pickle.dumps(client_first_packet)

            # Send data
            print >> sys.stderr, 'sending "%s"' % client_first_packet
            sock.sendto(client_first_packet, server_address)

            # Receive response
            print >> sys.stderr, 'waiting to receive'
            server_first_packet, server = sock.recvfrom(4096)
            server_first_packet = pickle.loads(server_first_packet)
            print "From server Second: " + str(server_first_packet)
            temp = server_first_packet.syn + 1  # continue handshake
            server_first_packet.syn = server_first_packet.ack + 1
            server_first_packet.ack = temp
            print "client: " + str(server_first_packet)
            server_first_packet = pickle.dumps(server_first_packet)
            sock.sendto(server_first_packet, server)
            return sock, client_first_packet, server_first_packet

        except Exception as error:
            print "Something went wrong: " + str(error)


    # @staticmethod
    # def bind():
    #     pass
