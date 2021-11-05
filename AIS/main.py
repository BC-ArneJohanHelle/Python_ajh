import socket
from pyais import NMEAMessage, decode_msg

UDP_IP = "0.0.0.0"
UDP_PORT = 11194

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    #print("received message: %s" % data)
    #print(decode_msg(data))
    try:
        if "AIVD" in str(data):
            print(decode_msg(data))
    except:
        print("error")

