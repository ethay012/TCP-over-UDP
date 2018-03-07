# -*- coding: utf-8 -*-
import random
import socket
import sys
import pickle
import threading
import time

DATA_DIVIDE_LENGTH = 1024
TCP_PACKET_SIZE = 32
DATA_LENGTH = DATA_DIVIDE_LENGTH
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
        return "SEQ Number: %d, ACK Number: %d, ACK:%d, SYN:%d, FIN:%d, TYPE:%s, DATA:%s" \
               % (self.seq, self.ack, self.flag_ack, self.flag_syn, self.flag_fin, self.packet_type(), self.data)

    def __cmp__(self, other):
        return cmp(self.seq, other.seq)

    def packet_type(self):
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
        else:
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

    def __init__(self, timeout=5):
        self.status = 1  # socket open or closed
        #seq will have the last packet send and ack will have the next packet waiting to receive
        self.own_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP socket used for communication.
        self.own_socket.settimeout(timeout)
        self.connections = {}
        self.connection_queue = []
        self.connection_lock = threading.Lock()
        self.queue_lock = threading.Lock()
        # each condition will have a dictionary of an address and it's corresponding packet.
        self.packets_received = {"SYN": {}, "ACK": {}, "SYN-ACK": {}, "DATA or FIN": {}}

        self.central_receive()

    def __repr__(self):
        return "TCP()"

    def __str__(self):
        return "Connections: %s" \
               % str(self.connections)

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
                self.connections[connection].checksum = checksum_of_data
                self.connections[connection].data = data_part
                self.connections[connection].set_flags()
                packet_to_send = pickle.dumps(self.connections[connection])
                while data_not_received:
                    data_not_received = False
                    try:
                        self.own_socket.sendto(packet_to_send, connection)
                        answer = self.find_correct_packet("ACK", connection)

                    except socket.timeout:
                        print "timeout"
                        data_not_received = True
                self.connections[connection].seq += len(data_part)
        except socket.error as error:
            print "Socket was closed before executing command. Error is: %s." % error

    def recv(self, connection=None):
        try:
            data = ""

            if connection not in self.connections.keys():
                if connection is None:
                    connection = self.connections.keys()[0]
                else:
                    return "Connection not in connected devices"

            while True:

                data_part = self.find_correct_packet("DATA or FIN", connection)
                if data_part.packet_type() == "FIN":
                    self.disconnect(connection)
                    return "Disconnected"
                checksum_value = TCP.checksum(data_part.data)

                while checksum_value != data_part.checksum:

                    data_part = self.find_correct_packet("DATA or FIN", connection)
                    checksum_value = TCP.checksum(data_part.data)

                data += data_part.data
                self.connections[connection].ack = data_part.seq + len(data_part.data)
                self.connections[connection].seq += 1  # syn flag is 1 byte
                self.connections[connection].set_flags(ack=True)
                packet_to_send = pickle.dumps(self.connections[connection])
                self.own_socket.sendto(packet_to_send, connection)  # after receiving correct info sends ack
                self.connections[connection].set_flags()

                if len(data_part.data) == 0:
                    break

            return data
        except socket.error as error:
            print "Socket was closed before executing command. Error is: %s." % error

    # conditions = ["SYN", "SYN-ACK", "ACK", "FIN", "FIN-ACK", "DATA"]
    def listen_handler(self, max_connections):
        try:
            while True:
                try:
                    answer, address = self.find_correct_packet("SYN")

                    with self.queue_lock:
                        if len(self.connection_queue) < max_connections:
                            self.connection_queue.append((answer, address))
                        else:
                            self.own_socket.sendto("Connections full", address)
                except KeyError:
                    continue
        except socket.error as error:
            print "Something went wrong in listen_handler func! Error is: %s." + str(error)

    def listen(self, max_connections=1):
        try:
            TCP.threader(func=self.listen_handler, args=(max_connections,), join=False, daemon=True)
        except Exception as error:
            print "Something went wrong in listen func! Error is: %s." % str(error)

    def accept(self):
        try:
            while True:
                if self.connection_queue:
                    with self.queue_lock:
                        answer, address = self.connection_queue.pop()
                    self.connections[address] = TCPPacket()
                    self.connections[address].ack = answer.seq + 1
                    self.connections[address].seq += 1
                    self.connections[address].set_flags(ack=True, syn=True)
                    packet_to_send = pickle.dumps(self.connections[address])

                    #lock address, connections dictionary?
                    packet_not_sent_correctly = True
                    while packet_not_sent_correctly or answer is None:
                        try:
                            packet_not_sent_correctly = False
                            self.own_socket.sendto(packet_to_send, address)
                            answer = self.find_correct_packet("ACK", address)
                        except socket.timeout:
                            packet_not_sent_correctly = True
                    self.connections[address].set_flags()
                    self.connections[address].ack = answer.seq + 1
                    print address
                    return address
        except Exception as error:
            print "Something went wrong in accept func: " + str(error)
            self.own_socket.close()

    def connect(self, server_address=("127.0.0.1", 10000)):
        try:
            self.connections[server_address] = TCPPacket()
            self.connections[server_address].set_flags(syn=True)
            first_packet_to_send = pickle.dumps(self.connections[server_address])
            self.own_socket.sendto(first_packet_to_send, self.connections.keys()[FIRST])
            self.connections[server_address].set_flags()
            answer = self.find_correct_packet("SYN-ACK", server_address)
            if type(answer) == str:  # == "Connections full":
                raise socket.error("Server cant receive any connections right now.")
            self.connections[server_address].ack = answer.seq + 1
            self.connections[server_address].seq += 1
            self.connections[server_address].set_flags(ack=True)
            second_packet_to_send = pickle.dumps(self.connections[server_address])
            self.own_socket.sendto(second_packet_to_send, self.connections.keys()[FIRST])
            self.connections[server_address].set_flags()

        except socket.error as error:
            print "Something went wrong in connect func: " + str(error)
            self.own_socket.close()

    def close(self, connection=None):
        try:
            if connection not in self.connections.keys():
                if connection is None:
                    connection = self.connections.keys()[0]
                else:
                    return "Connection not in connected devices"
            self.connections[connection].set_flags(fin=True)
            self.connections[connection].seq += 1
            packet_to_send = pickle.dumps(self.connections[connection])
            self.own_socket.sendto(packet_to_send, connection)
            answer = self.find_correct_packet("ACK", connection)  # change cause may get a None value
            self.connections[connection].ack += 1
            time.sleep(0.5)
            answer = self.find_correct_packet("DATA or FIN", connection)
            if answer.flag_fin != 1:
                raise Exception("The receiver didn't send the fin packet")
            else:
                self.connections[connection].ack += 1
                self.connections[connection].seq += 1
                self.connections[connection].set_flags(ack=True)
                packet_to_send = pickle.dumps(self.connections[connection])
                self.own_socket.sendto(packet_to_send, connection)
                with self.connection_lock:
                    self.connections.pop(connection)
                if len(self.connections) == 0:
                    self.own_socket.close()
                    self.status = 0
        except Exception as error:
            print "Something went wrong in the close func! Error is: %s." % error
            
    def disconnect(self, connection):
        try:
            self.connections[connection].ack += 1
            self.connections[connection].seq += 1
            self.connections[connection].set_flags(ack=True)
            packet_to_send = pickle.dumps(self.connections[connection])
            self.own_socket.sendto(packet_to_send, connection)
            self.connections[connection].set_flags(fin=True)
            self.connections[connection].seq += 1
            packet_to_send = pickle.dumps(self.connections[connection])
            self.own_socket.sendto(packet_to_send, connection)
            answer = self.find_correct_packet("ACK", connection)
            with self.connection_lock:
                self.connections.pop(connection)
            # if len(self.connections) == 0:
            #     self.own_socket.close()
            #     self.status = 0
        except Exception as error:
            print "Something went wrong in disconnect func:%s " % error

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
    def threader(func, args, join=False, daemon=False):
        t = threading.Thread(target=func, args=args)
        if daemon:
            t.daemon = True
        t.start()
        if join:
            t.join()

    # conditions = ["SYN", "SYN-ACK", "ACK", "FIN", "FIN-ACK", "DATA"]
    # packet = (packet,
    def sort_answers(self, packet, address):
        if packet.packet_type() == "DATA" or packet.packet_type() == "FIN":
            self.packets_received["DATA or FIN"][address] = packet
        else:
            self.packets_received[packet.packet_type()][address] = packet

    def find_correct_packet(self, condition, address=("Any",)):
        not_found = True
        tries = 0
        while not_found and tries < 2:
            try:
                not_found = False
                if address[0] == "Any":
                    order = self.packets_received[condition].popitem()  # to reverse the tuple received
                    return order[1], order[0]
                if condition == "ACK":
                    tries += 1
                return self.packets_received[condition].pop(address)
            except KeyError:
                not_found = True
                time.sleep(0.25)

    def central_receive_handler(self):
        while True and self.status == 1:
            try:
                packet, address = self.own_socket.recvfrom(SENT_SIZE)
                packet = pickle.loads(packet)
                self.sort_answers(packet, address)
            except socket.timeout:
                continue
            except socket.error:
                continue

    def central_receive(self):
        t = threading.Thread(target=self.central_receive_handler)
        t.daemon = True
        t.start()