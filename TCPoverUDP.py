# -*- coding: utf-8 -*-
import socket
import random
import pickle

from tcp_packet import TCPPacket
import sys
from tcp_packet import TCP

def main():
    test2 = TCP()
    test = TCPPacket()
    test.data = "012345678912341235134651723948712983657862347821389578942yhfjkbdsnvmbnmcxzbvnmawehkjlrbvqkhjwaeblhjkfbskdnvmnx,mc.bnlkjerhstojkhkjASDSBvncmbxz,vbtn,mbskyjl;qawj4y5uiq23hjkbfdszcn,mvb.,cvxmbn;elakweh54jqi2hb3j4kb4awem,v.cmnzbvzxm.,dcnt;pkah4j5klsdv56782364578617823687r6781263874678`2163406127835678634758627834657862347856283465876w78qerfyfuasdihvkjn54[03896uy394hgjbahjgdsurgyu123h54kj43n5jklnribshdyvos76e4756uhjkfzbv"
    test.data += test.data
    test.data += test.data
    test.data += test.data
    print len(test.data)
    test.ack = 42949672951231234123
    test.seq = 123424598677841234
    test2.own_packet = test
    print sys.getsizeof(test2, "Not found")




if __name__ == '__main__':
    main()