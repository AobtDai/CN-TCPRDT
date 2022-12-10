import socket
import struct
import os
import stat
import re
import sys
import time
import random
import threading

import FDFTPsocket

# HEADER_SIZE = 32
BUF_SIZE = 1024 + 32
CLIENT_PORT = 7777
FILE_SIZE = 1024
TimeoutInterval = 3600

packet_struct = struct.Struct('II1024s')
feedback_struct = struct.Struct('II')

# buffer to store possibly retrasmitting packet 
pkt_buffer = []
base = 1
nextseqnum = 1
rwnd = 10 # N
pkt_start_time = 0.0
pktsum = 1

over_flag = 0

def GBNsend():
    global nextseqnum, base, rwnd, pktsum
    while True:
        data_ = f.read(FILE_SIZE)
        pkt_buffer.append(data_)
        pktsum +=1
        if str(data_)=="b''":
            break
            
    while True:
        try:
            pass
        except KeyboardInterrupt:
            print("CtrlC-QUITed")
            sys.exit(0)

        while nextseqnum < base + rwnd:
            data = pkt_buffer[nextseqnum]
            if str(data)!="b''":
                end_flag = 0
                sndpkt = packet_struct.pack(*(nextseqnum, end_flag, data))
                pkt_buffer.append(sndpkt)
                Task.sendto(s, sndpkt, server_addr)
                print("*****sendout ",nextseqnum," pkt")
                if base == nextseqnum:
                    pkt_start_time = time.time()
                nextseqnum +=1
            else:
                data = 'end'.encode('utf-8')
                end_flag = 1
                sndpkt = packet_struct.pack(*(nextseqnum, end_flag, data))
                Task.sendto(s, sndpkt, server_addr)
                over_flag = 1
                print("***** transmit over *****")
                break
        
        if over_flag == 1:
            break
        
        # timeout estimate
        pkt_end_time = time.time()
        if pkt_end_time - pkt_start_time > TimeoutInterval:
            print("*****timeout*****")
            pkt_start_time = time.time()
            for i in (base, nextseqnum) :
                Task.sendto(s, pkt_buffer[i], server_addr)

def ACKrcv():
    global base, nextseqnum
    while True:
        try:
            pass
        except KeyboardInterrupt:
            print("CtrlC-QUITed")
            sys.exit(0)

        raw_data, server_addr2 = s.recvfrom(BUF_SIZE)
        rec_data = feedback_struct.unpack(raw_data)
        if rec_data[1]==1:
            acknum = rec_data[0] #### expext num
            if acknum >= pktsum:
                break
            if base < acknum :
                base = acknum
                if base==nextseqnum:
                    pkt_start_time = 0.0
                else :
                    pkt_start_time = time.time()

if __name__ == "__main__":
    server_ip="8.218.117.184"
    #file_name = "chain.py"
    file_name = "host_iperf.py"
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    data = (file_name).encode('utf-8')
    server_addr=(server_ip,CLIENT_PORT)
    
    Task = FDFTPsocket.Task(file_name)
    
    #s.sendto(data,server_addr)
    Task.sendto(s,data,server_addr)
    f = open(file_name,"rb")

    # acksum = 0 # fast retransmit 3 packets

    t_GBNsend = threading.Thread(target=GBNsend)
    t_ACKrcv = threading.Thread(target=ACKrcv)
    t_GBNsend.start()
    t_ACKrcv.start()
    t_GBNsend.join()
    t_ACKrcv.join()


    Task.finish()
    s.close()
