# -*- coding: utf-8 -*-
from tcp_packet import TCP
import sys


def main():
    client = TCP()
    client.connect()
    print client
    # client.send("hello me")
    # while (to_send != exit)
    #     to_send=raw_input("enter text-->")
    #     client.send(to_send)
    #     print client.recv()
    # sys.exit()
    # with open(r"SentPicture.jpg", 'rb') as my_file:
    #     my_file = my_file.read()
    #     client.send(my_file)
    # client.close()
    # print "Goodbye..."
    name = raw_input("Type your name here --> ").capitalize()
    while True:
        to_send = name + ": " + raw_input("Type to your friend --> ")
        client.send(to_send)
        print "Waiting to receive message from your friend"
        answer = client.recv()
        if answer.split(' ')[1].upper() == "EXIT":
            break
        else:
            print answer
    if to_send.split(' ')[1].upper() == "EXIT":
        client.send(to_send)
        client.close()
        print "Closed"
    print "Finished"
    sys.exit()



if __name__ == '__main__':
    main()
