# -*- coding: utf-8 -*-
from please_work import TCP
import sys


def main():

    client = TCP()
    client.central_receive()
    client.connect()
    client.send("Hello me")
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
    # name = raw_input("Type your name here --> ").capitalize()
    # to_send = "NAME: MESSAGE"
    # while True:
    #     to_send = name + ": " + raw_input(bcolors.OKGREEN + name + ": " + bcolors.ENDC)
    #     if to_send.split(' ')[1].upper() == "EXIT":
    #         client.close()
    #         print "Closed"
    #         break
    #     client.send(to_send)
    #     answer = client.recv()
    #     if answer == "Disconnected":
    #         break
    #     else:
    #         print bcolors.OKBLUE + answer + bcolors.ENDC
    # print "Finished"
    # sys.exit()
    print client.packets_received
    raw_input("Finished")



if __name__ == '__main__':
    main()
