import socket
import struct
import threading
import os
import sys
import random
import time
import importlib
importlib.reload(sys)

packet_struct = struct.Struct('II1024s')
feedback_struct = struct.Struct('II')

BUF_SIZE = 1024+24
FILE_SIZE = 1024
IP = '172.17.50.166'
SERVER_PORT = 7777

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.bind((IP, SERVER_PORT))
    print("-----The server has been started.-----")
    string,client_addr = s.recvfrom(BUF_SIZE)
    file_name = string.decode('utf-8')
    f = open(file_name,"ab")

    expectedseqnum = 1

    while True:
        data, client_addr = s.recvfrom(BUF_SIZE)
        unpacked_data = packet_struct.unpack(data)
        seqnum = unpacked_data[0]
        end_flag = unpacked_data[1]
        data = unpacked_data[2]

        # send back ACK info
        if expectedseqnum == seqnum:
            expectedseqnum +=1
        isACK = 1
        sndpkt = feedback_struct.pack(*(expectedseqnum, 1)) # 1 refers to ACK
        # pkt_buffer.append(sndpkt)
        s.sendto(sndpkt, client_addr)
        
        if end_flag == 0:
            f.write(data)
        else:
            break
        
    s.close()