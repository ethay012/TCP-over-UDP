# -*- coding: utf-8 -*-
from tcp_packet import TCP


def main():
    client = TCP()
    client.connect()
    print client
    client.send("hello me")
    # while (to_send != exit)
    #     to_send=raw_input("enter text-->")
    #     client.send(to_send)
    #     print client.recv()
    # sys.exit()
    with open(r"SentPicture.jpg", 'rb') as my_file:
        my_file = my_file.read()
        client.send(my_file)
    client.close()
    print "Goodbye..."


if __name__ == '__main__':
    main()
