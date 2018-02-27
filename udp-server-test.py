# -*- coding: utf-8 -*-
from tcp_packet import TCP
import sys
import time

WAIT_FOR_CLOSING = 5

def main():
    server = TCP()
    # while server.status != 0:
    server.listen()
            # while message != "exit":
            #     print server.recv()
            #     server.send(raw_input("enter massage-->"))
            # sys.exit()
    # print server
    # print server.recv()
    # my_file = server.recv()
    # with open(r"ReceivedPicture.jpg", 'wb') as my_picture:
    #     my_picture.write(my_file)
    #     # if server.status == 0:
    #     #     print "Server Disconnected"
    #     #     break
    # print server.recv()
    # print "Goodbye..."
    name = raw_input("Type your name here --> ").capitalize()
    to_send = "NAME: MESSAGE"
    while server.status and to_send.split(' ')[1].upper() != "EXIT":
        print "Waiting to receive message from your friend"
        answer = server.recv()
        if answer.split(' ')[1].upper() == "EXIT":
            break
        else:
            print answer
        to_send = name + ": " + raw_input("Type to your friend --> ")
        server.send(to_send)
    if to_send.split(' ')[1].upper() == "EXIT":
        server.close()
        print "Closed"
    print "Finished"
    sys.exit()




if __name__ == '__main__':
    main()
