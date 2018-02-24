# -*- coding: utf-8 -*-
from tcp_packet import TCP


def main():
    server = TCP()
    # while server.status != 0:
    server.listen()
            # while message != "exit":
            #     print server.recv()
            #     server.send(raw_input("enter massage-->"))
            # sys.exit()
    print server
    print server.recv()
    my_file = server.recv()
    with open(r"ReceivedPicture.jpg", 'wb') as my_picture:
        my_picture.write(my_file)
        # if server.status == 0:
        #     print "Server Disconnected"
        #     break
    print server.recv()
    print "Goodbye..."



if __name__ == '__main__':
    main()
