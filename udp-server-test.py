import socket
import pickle
from tcp_packet import TCPPacket
import sys

# class UDPServer(object):
#     def __init__(self, host, port):
#         self._host = host
#         self._port = port
#
#     def __enter__(self):
#         sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         sock.bind((self._host, self._port))
#         self._sock = sock
#         return sock
#
#     def __exit__(self, *exc_info):
#         if exc_info[0]:
#             import traceback
#             traceback.print_exception(*exc_info)
#         self._sock.close()
# def connect_server(udp_socket):
#
#     ip = "127.0.0.1"
#     x, addr = udp_socket.recvfrom(1024)
#     x= pickle.loads(x)
#     print x
#     y= TCPPacket(3200, 6594)
#     y.ack = x.syn + 1
#     y = pickle.dumps(y)
#     udp_socket.sendto(addr, y)
#
# if __name__ == '__main__':
#     host = 'localhost'
#     port = 5566
#     with UDPServer(host,port) as s:
#         while True:
#             ip = "127.0.0.1"
#             x, addr = s.recvfrom(1024)
#             x = pickle.loads(x)
#             print x
#             y = TCPPacket(3200, 6594)
#             y.ack = x.syn + 1
#             port = y.src_port
#             y = pickle.dumps(y)
#             s.sendto(y, (addr, port))
#             x, addr = s.recvfrom(1024)
#             print x
#             raw_input()
import socket
import sys

def main():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port
    server_address = ('localhost', 10000)
    print >>sys.stderr, 'starting up on %s port %s' % server_address
    sock.bind(server_address)

    while True:
        print >> sys.stderr, '\nwaiting to receive message'
        x, address = sock.recvfrom(4096)
        x = pickle.loads(x)
        print x

        y = TCPPacket(3200, 6594)
        y.ack = x.syn + 1
        port = y.src_port
        y = pickle.dumps(y)
        sent = sock.sendto(y, (address, 10000))
        z, addr = sock.recvfrom(1024)
        z = pickle.loads(z)

        print >> sys.stderr, z

    sock.close()


if __name__ == '__main__':
    main()
