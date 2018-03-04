# -*- coding: utf-8 -*-
import random
import socket
import sys
import pickle
import threading

DATA_DIVIDE_LENGTH = 1024
TCP_PACKET_SIZE = 32
DATA_LENGTH = 1024
SENT_SIZE = TCP_PACKET_SIZE + DATA_LENGTH + 5000  # Pickled objects take a lot of space
LAST_CONNECTION = -1
FIRST = 0

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
        self.data = ""

    def __repr__(self):
        return "TCPpacket()"

    def __str__(self):
        return "SEQ Number: %d, ACK Number: %d" \
               % (self.seq, self.ack)

    def __cmp__(self, other):
        return cmp(self.seq, other.seq)

    def packet_type(self):
        packet_type = ""
        if self.flag_syn == 1 and self.flag_ack == 1:
            packet_type = "SYN-ACK"
        elif self.flag_ack == 1 and self.flag_fin == 1:
            packet_type = "FIN-ACK"
        elif self.flag_syn == 1:
            packet_type = "SYN"
        elif self.flag_ack == 1:
            packet_type = "ACK"
        elif self.flag_fin == 1:
            packet_type = "FIN"
        elif self.data != "":
            packet_type = "DATA"
        return packet_type

    def set_flags(self, ack=False, syn=False, fin=False):
        if ack:
            self.flag_ack = 1
        else:
            self.flag_ack = 0
        if syn:
            self.flag_syn = 1
        else:
            self.flag_syn = 0
        if fin:
            self.flag_fin = 1
        else:
            self.flag_fin = 0

    @staticmethod
    def gen_starting_seq_num():
        return random.randint(TCPPacket.SMALLEST_STARTING_SEQ, TCPPacket.HIGHEST_STARTING_SEQ)


class TCP(object):

    def __init__(self):
        self.status = 1  # socket open or closed
        #seq will have the last packet send and ack will have the next packet waiting to receive
        self.own_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP socket used for communication.
        self.connections = {}
        self.connection_queue = []
        self.queue_lock = threading.Lock()
        self.packets_received = []

    def __repr__(self):
        return "TCP()"

    def __str__(self):
        return "Own Packet: %s" \
               % str(self.connections)

    # Every change of the sequence and acknowledgment numbers
    #  needs to be changed to add the length of the packet itself too
    def send(self, data, connection=None):
        try:
            if connection not in self.connections.keys():
                if connection is None:
                    connection = self.connections.keys()[0]
                else:
                    return "Connection not in connected devices"
            data_parts = TCP.data_divider(data)
            for data_part in data_parts:
                data_not_received = True
                checksum_of_data = TCP.checksum(data_part)
                self.own_packet.checksum = checksum_of_data
                self.own_packet.data = data_part
                packet_to_send = pickle.dumps(self.own_packet)
                while data_not_received:
                    data_not_received = False
                    try:
                        self.own_socket.sendto(packet_to_send, connection)
                        answer, address = self.own_socket.recvfrom(SENT_SIZE)

                    except socket.timeout:
                        print "timeout"
                        data_not_received = True
                self.own_packet.seq += len(data_part)
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

                    data_part, address = self.own_socket.recvfrom(SENT_SIZE)
                    data_part = pickle.loads(data_part)  # Doesnt send anything just waits until its correct
                    checksum_value = TCP.checksum(data_part.data)  #
                data += data_part.data
                self.own_packet.ack = data_part.seq + len(data_part.data)
                self.own_packet.seq += 1  # syn flag is 1 byte
                packet_to_send = pickle.dumps(self.own_packet)
                self.own_socket.sendto(packet_to_send, address)  # after receiving correct info sends ack

                if len(data_part.data) == 0:
                    break

            return data
        except socket.error as error:
            print "Socket was closed before executing command. Error is: %s." % error

    # conditions = ["SYN", "SYN-ACK", "ACK", "FIN", "FIN-ACK", "DATA"]
    def listen_handler(self, max_connections):
        try:
            while True:
                answer, address = self.own_socket.recvfrom(SENT_SIZE)
                answer = pickle.loads(answer)
                if self.sort_answers(answer, "SYN", address):
                    print address, self.connection_queue, self.connections
                    with self.queue_lock:
                        if len(self.connection_queue) < max_connections:
                            self.connection_queue.append((answer, address))
                        else:
                            self.own_socket.sendto("Connections full", address)
                else:
                    answer = self.find_correct_packet("SYN")  # needs to return something
        except socket.error as error:
            print "Something went wrong! Error is: %s." + str(error)

    def listen(self, max_connections=1):
        try:
            TCP.threader(func=self.listen_handler, args=(max_connections,), join=False, daemon=True)
        except Exception as error:
            print "Something went wrong! Error is: %s." % str(error)

    def accept(self):
        # try:
            while True:
                if self.connection_queue:
                    with self.queue_lock:
                        answer, address = self.connection_queue.pop()
                    self.connections[address] = TCPPacket()
                    self.connections[address].ack = answer.seq + 1
                    self.connections[address].seq += 1
                    self.connections[address].set_flags(ack=True, syn=True)
                    packet_to_send = pickle.dumps(self.connections[address])
                    self.own_socket.sendto(packet_to_send, address)
                    self.connections[address].set_flags()
                    #lock address, connections dictionary?
                    answer, address2 = self.own_socket.recvfrom(SENT_SIZE)
                    answer = pickle.loads(answer)
                    # while address2 != address:
                    #     self.own_socket.sendto("Connections full", address2)
                    #     answer, address2 = self.own_socket.recvfrom(SENT_SIZE)
                    if self.sort_answers(answer, "ACK", address2, address):
                        self.connections[address].ack = answer.seq + 1
                        return address
                    else:
                        answer = "Not found"
                        while type(answer) == str:
                            answer = self.find_correct_packet("ACK", address)
                            print str(answer) + "answer"
                        self.connections[address].ack = answer.seq + 1
                        return address
        # except Exception as error:
        #     print "Something went wrong: " + str(error)
        #     self.own_socket.close()

    def connect(self, server_address=("localhost", 10000)):
        try:
            self.connections[server_address] = TCPPacket()
            self.connections[server_address].set_flags(syn=True)
            first_packet_to_send = pickle.dumps(self.connections[server_address])
            self.own_socket.sendto(first_packet_to_send, self.connections.keys()[FIRST])
            answer, address = self.own_socket.recvfrom(SENT_SIZE)
            if answer == "Connections full":
                raise socket.error("Server cant receive any connections right now.")
            answer = pickle.loads(answer)
            self.connections[server_address].ack = answer.seq + 1
            self.connections[server_address].seq += 1
            self.connections[server_address].set_flags(ack=True)
            second_packet_to_send = pickle.dumps(self.connections[server_address])
            self.own_socket.sendto(second_packet_to_send, self.connections.keys()[FIRST])

        except socket.error as error:
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

    @staticmethod
    def threader(func, args, join, daemon):
        t = threading.Thread(target=func, args=args)
        if daemon:
            t.daemon = True
        t.start()
        if join:
            t.join()

    # conditions = ["SYN", "SYN-ACK", "ACK", "FIN", "FIN-ACK", "DATA"]
    def sort_answers(self, packet, condition,  received_address, expected_address="Any"):
        if expected_address == "Any" and packet.packet_type() == condition:
            return True
        if expected_address == received_address and packet.packet_type() == condition:
            return True
        else:
            self.packets_received.append((packet, received_address))
            return False

    def find_correct_packet(self, condition, address="Any"):
        for packet in self.packets_received:
            if address == "Any" and packet[0].packet_type() == condition:
                self.packets_received.remove(packet)
                answer = packet
                return answer
            if packet[1] == address and packet[0].packet_type() == condition:
                self.packets_received.remove(packet)
                answer = packet[0]
                return answer
        return "Not found"



