# -*- coding: utf-8 -*-
import random
import socket
import sys
import pickle

DATA_DIVIDE_LENGTH = 1024
TCP_PACKET_SIZE = 32
DATA_LENGTH = 1024
SENT_SIZE = TCP_PACKET_SIZE + DATA_LENGTH + 5000  # Pickled objects take a lot of space


class TCPPacket(object):
    """
    Add Documentation here
    """
    SMALLEST_STARTING_SEQ = 0
    HIGHEST_STARTING_SEQ = 9000  # 4294967295

    def __init__(self):
        # self.src_port = src_port  # 16bit
        # self.dst_port = dst_port  # 16bit
        self.seq = TCPPacket.gen_starting_seq_num()  # 32bit
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
        self.flag_seq = 0  # 1bit
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
        self.data = ""

    def __repr__(self):
        return "TCPpacket()"

    def __str__(self):
        return "SEQ Number: %d, ACK Number: %d" \
               % (self.seq, self.ack)

    @staticmethod
    def gen_starting_seq_num():
        return random.randint(TCPPacket.SMALLEST_STARTING_SEQ, TCPPacket.HIGHEST_STARTING_SEQ)


class TCP(object):

    def __init__(self):
        self.status = 1  # socket open or closed
        self.own_packet = TCPPacket()  # last packet of communication.
        #seq will have the last packet send and ack will have the next packet waiting to receive
        self.own_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP socket used for communication.
        self.receiver_address = ""
        self.own_address = ""  # maybe change listen to listen to own address and to send to receiver

    def __repr__(self):
        return "TCP()"

    def __str__(self):
        return "Own Packet: %s" \
               % self.own_packet

    # Every change of the sequence and acknowledgment numbers needs to be changed to add the length of the packet itself too
    def send(self, data):
        try:
            data_parts = TCP.data_divider(data)
            for data_part in data_parts:
                self.own_packet.seq += len(data_part)
                checksum_of_data = TCP.checksum(data_part)
                self.own_packet.checksum = checksum_of_data
                self.own_packet.data = data_part
                packet_to_send = pickle.dumps(self.own_packet)
                self.own_socket.sendto(packet_to_send, self.receiver_address)
                answer, address = self.own_socket.recvfrom(SENT_SIZE)
                # self.own_packet.ack += 1
                answer = pickle.loads(answer)
                while (answer.ack - 1) != self.own_packet.seq:
                    packet_to_send = pickle.dumps(self.own_packet)
                    self.own_socket.sendto(packet_to_send, self.receiver_address)
                    answer, address = self.own_socket.recvfrom(SENT_SIZE)
                    answer = pickle.loads(answer)
                    # self.own_packet.ack += 1
        except socket.error as error:
            print "Socket was closed before executing command. Error is: %s." % error

    def recv(self):
        try:
            data = ""

            while True:

                data_part, address = self.own_socket.recvfrom(SENT_SIZE)
                data_part = pickle.loads(data_part)
                if data_part.flag_fin == 1:
                    self.disconnect()
                    return "Disconnected"
                checksum_value = TCP.checksum(data_part.data)

                while checksum_value != data_part.checksum:

                    self.own_socket.sendto(self.own_packet, address)
                    data_part, address = self.own_socket.recvfrom(SENT_SIZE)
                    data_part = pickle.loads(data_part)
                    checksum_value = TCP.checksum(data_part.data)
                data += data_part.data
                self.own_packet.ack += len(data_part.data)
                self.own_packet.seq += 1
                packet_to_send = pickle.dumps(self.own_packet)
                self.own_socket.sendto(packet_to_send, address)

                if len(data_part.data) == 0:
                    break

            return data
        except socket.error as error:
            print "Socket was closed before executing command. Error is: %s." % error

    def listen(self, server_address=("localhost", 10000)):
        try:
            print >> sys.stderr, 'starting up on %s port %s' % server_address
            self.own_socket.bind(server_address)
            print >> sys.stderr, '\nwaiting to receive message'
            answer, self.receiver_address = self.own_socket.recvfrom(SENT_SIZE)
            answer = pickle.loads(answer)
            self.own_packet.ack = answer.seq + 1
            self.own_packet.seq += 1
            packet_to_send = pickle.dumps(self.own_packet)
            self.own_socket.sendto(packet_to_send, self.receiver_address)
            answer, address = self.own_socket.recvfrom(SENT_SIZE)
            answer = pickle.loads(answer)
            self.own_packet.ack = answer.seq + 1
            self.own_address = server_address
        except Exception as error:
            print "Something went wrong: " + str(error)
            self.own_socket.close()

    def connect(self, server_address=("localhost", 10000)):
        try:
            self.receiver_address = server_address
            first_packet_to_send = pickle.dumps(self.own_packet)
            #  print >> sys.stderr, 'sending "%s"' % self.own_packet
            self.own_socket.sendto(first_packet_to_send, self.receiver_address)
            answer, address = self.own_socket.recvfrom(SENT_SIZE)
            answer = pickle.loads(answer)
            self.own_packet.ack = answer.seq + 1
            self.own_packet.seq += 1
            second_packet_to_send = pickle.dumps(self.own_packet)
            #  print >> sys.stderr, 'sending "%s"' % self.own_packet
            self.own_socket.sendto(second_packet_to_send, self.receiver_address)

        except Exception as error:
            print "Something went wrong: " + str(error)
            self.own_socket.close()

    def close(self):
        try:
            self.own_packet.flag_fin = 1
            # self.own_packet.flag_ack = 1
            self.own_packet.seq += 1
            packet_to_send = pickle.dumps(self.own_packet)
            self.own_socket.sendto(packet_to_send, self.receiver_address)
            answer, address = self.own_socket.recvfrom(SENT_SIZE)
            self.own_packet.ack += 1
            answer = pickle.loads(answer)
            # while (answer.ack - 1) != self.own_packet.seq:
            #     packet_to_send = pickle.dumps(self.own_packet)
            #     self.own_socket.sendto(packet_to_send, self.receiver_address)
            #     answer, address = self.own_socket.recvfrom(SENT_SIZE)
            #     answer = pickle.loads(answer)
            # self.own_packet.ack += 1
            # self.own_packet.seq += 1
            # packet_to_send = pickle.dumps(self.own_packet)
            # self.own_socket.sendto(packet_to_send, self.receiver_address)
            answer, address = self.own_socket.recvfrom(SENT_SIZE)
            answer = pickle.loads(answer)
            if answer.flag_fin != 1:
                print "The receiver didn't send the fin packet"
                raise Exception
            else:
                self.own_packet.ack += 1
                self.own_packet.seq += 1
                packet_to_send = pickle.dumps(self.own_packet)
                self.own_socket.sendto(packet_to_send, self.receiver_address)
                self.own_socket.close()
                self.status = 0

            # while checksum_value != answer.checksum:
            #     self.own_socket.sendto(self.own_packet, address)
            #     answer, address = self.own_socket.recvfrom(SENT_SIZE)
            #     answer = pickle.loads(answer)
            #     checksum_value = TCP.checksum(answer.data)

            self.own_socket.close()
        except Exception as error:
            print "Something went wrong:%s " % error

    def disconnect(self):
        try:
            self.own_packet.ack += 1
            self.own_packet.seq += 1
            packet_to_send = pickle.dumps(self.own_packet)
            self.own_socket.sendto(packet_to_send, self.receiver_address)
            # answer, address = self.own_socket.recvfrom(SENT_SIZE)
            # answer = pickle.loads(answer)
            #checksum_value = TCP.checksum(answer.data)
            # while checksum_value != answer.checksum:
            #     self.own_socket.sendto(self.own_packet, address)
            #     answer, address = self.own_socket.recvfrom(SENT_SIZE)
            #     answer = pickle.loads(answer)
            #     checksum_value = TCP.checksum(answer.data)
            self.own_packet.flag_fin = 1
            self.own_packet.seq += 1
            packet_to_send = pickle.dumps(self.own_packet)
            self.own_socket.sendto(packet_to_send, self.receiver_address)
            answer = self.own_socket.recvfrom(SENT_SIZE)
            # while (answer.ack - 1) != self.own_packet.seq:
            #     packet_to_send = pickle.dumps(self.own_packet)
            #     self.own_socket.sendto(packet_to_send, self.receiver_address)
            #     answer, address = self.own_socket.recvfrom(SENT_SIZE)
            #     answer = pickle.loads(answer)
            # self.own_packet.ack += 1
            self.own_socket.close()
            self.status = 0
        except Exception as error:
            print "Something went wrong:%s " % error

    @staticmethod
    def data_divider(data):
        """Divides the data into a list where each element's length is 1024"""
        data = [data[i:i + DATA_DIVIDE_LENGTH] for i in range(0, len(data), DATA_DIVIDE_LENGTH)]
        data.append("")
        return data

    @staticmethod
    def checksum(source_string):
        my_sum = 0
        count_to = (len(source_string) / 2) * 2
        count = 0
        while count < count_to:
            this_val = ord(source_string[count + 1])*256+ord(source_string[count])
            my_sum += this_val
            count += 2
        if count_to < len(source_string):
            my_sum += ord(source_string[len(source_string) - 1])
        my_sum = (my_sum >> 16) + (my_sum & 0xffff)
        my_sum += (my_sum >> 16)
        answer = ~my_sum
        answer = answer & 0xffff
        answer = answer >> 8 | (answer << 8 & 0xff00)
        return answer
