#
# bt server
#

#from bluetooth import *
import socket
import signal
import sys # needed for exit

BTAddr = '40:1C:83:C9:9F:81'
#BTAddr = ''

#BTsocket = BluetoothSocket (RFCOMM)
#BTsocket.connect ((BTAddr), 1)

#socket s;

# graceful exit on CNTRL-C
def signal_handler(sig, frame):
    # close port and exit
    print("\nCaught signal, exiting ....")
    s.close() # not shutdown as this is a broadcast stream

    sys.exit(0)

# SIGINT
signal.signal(signal.SIGINT, signal_handler)

s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)

s.bind((BTAddr, 5))

s.listen(1)

print("Bind and listen, waiting for call")
conn, addr = s.accept() # creates a new socket

print("connection from", addr)

while (True):
    data = conn.recv(1024)
    if not data: # socket was closed
        break
    print(data)