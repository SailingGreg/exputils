#
# bt client
#

#from bluetooth import *
import socket
import signal
import sys
from time import sleep
from datetime import datetime



#BTAddr = '40:1C:83:C9:9F:81' # pc
#BTAddr = 'DC:A6:32:8D:3F:87' # devhost
BTAddr = 'B8:27:EB:C5:C7:EE' # devhost

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



for i in range(3):
    snow = datetime.now()
    #print("now =", snow)
    try:

        s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        s.connect((BTAddr,5))

        req = "profiles"
        encReq = req.encode()

        #s.send(b'profiles')
        s.send(bytearray(encReq))

        profiles = s.recv(1024)
        #print (profiles)
        print (profiles.decode())
    except:
        print ("Connection failed")
        s.close()

    tnow = datetime.now()
    print("now =", tnow, tnow - snow)
    sleep(3)
    s.close

s.close()


'''
while (True):
    data = conn.recv(1024)
    if not data: # socket was closed
        break
    print(data)
'''