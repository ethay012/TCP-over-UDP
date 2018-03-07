# -*- coding: utf-8 -*-
from TCP_over_UDP import TCP
import threading
import sys


def send_msg(sock, name):
    try:
        while True:
            message = raw_input()
            to_send = "\n" + name + message + "\n"
            if message.upper() == "EXIT":
                sock.close()
            else:
                sock.send(to_send)

    except KeyboardInterrupt:
        sock.close()


def run(sock, address):

        name = raw_input("Name: ") + ": "

        sock.connect((address, 10000))

        input_thread = threading.Thread(target=send_msg, args=(sock, name))
        input_thread.daemon = True
        input_thread.start()

        while True:
            data = sock.recv()
            if data == "Disconnected":
                break
            else:
                print data


def main():
    sock = TCP()
    server_address = sys.argv[1]
    run(sock, server_address)


if __name__ == '__main__':
    main()