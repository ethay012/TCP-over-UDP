# -*- coding: utf-8 -*-
from please_work import TCP
import sys
WAIT_FOR_CLOSING = 5


def main():
    server = TCP()
    server.own_socket.bind(("127.0.0.1", 10000))
    server.central_receive()
    # while server.status != 0:
    server.listen(3)
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
    # name = raw_input("Type your name here --> ").capitalize()
    # to_send = "NAME: MESSAGE"
    # print bcolors.WARNING + "Waiting to receive message from friend" + bcolors.ENDC
    # while server.status and to_send.split(' ')[1].upper() != "EXIT":
    #     answer = server.recv()
    #     if answer == "Disconnected":
    #         break
    #     else:
    #         print bcolors.OKBLUE + answer + bcolors.ENDC
    #     to_send = name + ": " + raw_input(bcolors.OKGREEN + name + ": " + bcolors.ENDC)
    #     if to_send.split(' ')[1].upper() == "EXIT":
    #         server.close()
    #         print "Closed"
    #         break
    #     server.send(to_send)
    #
    # print "Finished"
    # sys.exit()
    address_list = []
    print "packets", server.packets_received
    for i in range(3):
        address_list.append(server.accept())
        print server.recv(address_list[-1])
        server.send("hello", address_list[-1])
        print "Accepted " + str(server.connections)

if __name__ == '__main__':
    main()
