#
# connect to expedition and create the profiles
# based on the data feed
#

import sys
import signal
import socket

# import the UDP_IP and UDP_PORT
from expconf import *

# the following is created based on the usrchannel.h header file in Expedition
# format is metric, the expedition variable name and value
# Note added abbreviations to profile 
from expchdata import expdata # load the the data channels

print("Number of user defined channels: ", len(expdata))


# has name and up to 4 variables which map to metrics
# to build the json string just interate over profiles and add name and values from expdata

# BSP TRG RNG BRG
# BSP TRG% DST
# BSP RNG TIM SOG
# BSP BRG COG SOG
# marktime - 88
# markrng - 105
# markbrg - 106


profiles = [
    {"profile": "helm", "metric0": 1, "metric1": 54, "metric2": 105, "metric3": 106},
    {"profile": "trim", "metric0": 1, "metric1": 264, "metric2": 105, "metric3": 0},
    {"profile": "crew", "metric0": 1, "metric1": 105, "metric2": 88, "metric3": 0},
    {"profile": "nav", "metric0": 1, "metric1": 106, "metric2": 50, "metric3": 51}
]
'''
extend this so it is variable, tag, index and value
need to add one additional level of indirection for this
if label null string then use variable name as tag
This strucuture is simple to extend, just add more variables to a profile
This would allow the nav to have 2 pages, one with position data
'''
profilesext = {
     "helm": {  1: {"variable": "BSP", "label": "", "index": 1},
        2: {"variable": "TargBspN", "label": "TRG", "index": 54},
        3: {"variable": "MarkRng", "label": "", "index": 105},
        4:  {"variable": "MarkBrg", "label": "", "index": 106}  },
     "trim": { 1: {"variable": "BSP", "label": "", "index": 1},
        2: {"variable": "HeadingToSteer", "label": "HDR", "index": 264},
        3: {"variable": "MarkRng", "label": "", "index": 105}  } ,
     "crew": { 1: {"variable": "BSP", "label": "", "index": 1},
        2: {"variable": "MarkRng", "label": "RNG", "index": 105},
        3: {"variable": "MarkTime", "label": "", "index": 88} },
     "nav": {  1: {"variable": "BSP", "label": "", "index": 1},
        2: {"variable": "MarkBrg", "label": "", "index": 106},
        3: {"variable": "Cog", "label": "COG", "index": 50},
        4:  {"variable": "Sog", "label": "SOG", "index": 51},
        5: {"variable": "Lat", "label": "LAT", "index": 48},
        6:  {"variable": "Lon", "label": "LON", "index": 49}
          }
}


# graceful exit on CNTRL-C
def signal_handler(sig, frame):
    # close port and exit
    print("\nCaught signal, exiting ....")
    client.close() # not shutdown as this is a broadcast stream
    cnt = 0
    for ent in expdata:
        if (ent["value"] > 0):
            print (ent["name"], ent["value"])
            cnt = cnt + 1
    print ("Found: ", cnt)
    sys.exit(0)

# calc the checksumm ala NMEA 0183
def calcChecksum(nmea):
    calc_cksum = 0
    for s in nmea:
        # it is XOR of each Unicode integer representation
        calc_cksum ^= ord(s)

    calc_cksum = hex(calc_cksum) # get hex representation of the int value
    calc_cksum = f'{calc_cksum}'[2:] # cut 0x

    return calc_cksum

# change the data structure to make this more efficient - issue is spareness?
# now the structure is generated we can index it directly
def updateData (idx, val):

    expdata[idx]["value"] = float(val)
    '''
    for ent in expdata:
        #print (ent)
        if (ent["metric"] == idx):
            ent["value"] = val
            break;
    '''

def findMetric (idx):
    val = 0.0
    for ent in expdata:
        #print (ent)
        if (ent["metric"] == idx):
            lab = ent["name"]
            val = ent["value"]
            break;
    return lab, val

def createProf():
    js = '{ "profiles": {' # the prefix
    for prof in profilesext:
        cnt = 0
        if (len(js) > 20):
            js = js + ',\n'
        js = js + '"' + prof + '": {'
        # we now have the profile
        for metric in profilesext[prof]:
            if cnt > 0:
                js = js + ', '
            # and each metric
            dt = profilesext[prof][metric]
            if (dt["label"] != ""):
                tag = dt["label"]
            else:
                tag = dt["variable"]
            val = expdata[dt["index"]]["value"]
            #print(prof, tag, val)
            #lab = expdata[prof[metric]]["name"]
            #val = expdata[prof[metric]]["value"]
            js = js + '"' + tag + '": ,"' + str(val) + '"'
            cnt = cnt + 1
        js = js + ' }'

    js = js + '\n} }'
    return js

'''
    for prof in profiles:
        cnt = 0
        #if (prof["profile"] == pr): # found
        if (len(js) > 20):
            js = js + ',\n'
        js = js + '"' + prof["profile"] + '": {'
        for m in range(4): # interate over the 4 entries
            metric = "metric" + str(m) # this will metric0 - metric3
            if (prof[metric] > 0): # if the index is non zero
                if cnt > 0:
                    js = js + ', '
                #lab, val = findMetric(prof[metric])
                #idx = prof[metric]
                lab = expdata[prof[metric]]["name"]
                val = expdata[prof[metric]]["value"]
                js = js + '"' + lab + '": ,"' + str(val) + '"'
                cnt = cnt + 1
            #print (prof)
        js = js + ' }'
        #break;
'''

# end createProfile

# SIGINT
signal.signal(signal.SIGINT, signal_handler)

# network setup
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# and bind to the interface
try:
    client.bind((UDP_IP, UDP_PORT))
except:
    print("Error", sys.exc_info()[0])

dots = 0
# run the following on a client thread with a server thread for the profile handling
print ("Processing: ", end = '', flush=True)
while True:
    data, addr = client.recvfrom(1024)
    #print("received data: %s", data)

    # parse the data - b'#0,1,8.000,2,-56.3,3,14.42,4,-90.0,5,12.00,6,0.0,11,0.0*3B\r\n'
    # structure is #{boat}, {var}, {value}, {var}, {value} * {checksum}\r\n
    datastr = str(data)

    datastr = datastr.removeprefix("b'") # leave '#' for now
    ostr = datastr
    pos = datastr.find("*")
    chksumm = datastr[pos+1:pos+3] # the checksumm
    datastr = datastr[0:pos] # and remove the checksumm and \r\n

    # validate checksum & discard if not correct
    val = calcChecksum(datastr)
    #print (ostr, val, chksumm)
    if (int(val, 16) != int(chksumm, 16)):
        print ("miss match", ostr, val, chksumm)
        continue;

    # remove the # prefix
    datastr = datastr.removeprefix("#") # and remove the '#'
    #pos = datastr.find("*")
    #datastr = datastr[0:pos]
    vars = datastr.split(",") # split into list which we can iterate over
    #print (vars)

    cnt = 0
    prev = 0
    # update the expdata based on what's in the string
    for var in vars:
        if (cnt == 0): # note the boat number
            boat = var
        #prev = int(var)
        if (cnt > 0 and (cnt % 2) == 0):
            updateData(prev, float(var))
            #print ("Updated", prev, var)
        else:
            prev = int(var) # expedition 'variable'
        cnt = cnt + 1

    print(".",end='', flush=True)
    dots = dots + 1
    if (dots % 60 == 0):
        dots = 0
        print ('')


    # test for the json profiles
    json = createProf()
    # 'log' it for now
    with open("profile.json", "w") as fi:
        fi.write(json)

    #end of while true

# end of file