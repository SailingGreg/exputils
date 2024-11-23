#
# parse Expedition's UsrChannels.h and create a python data structure
# this is imported to support the client element
#
# from expchdata import expdata # load the the data channels
#
import os

#exploc = "C:\Program Files (x86)\Expedition\Expedition4D"
#fname = "UsrChannels.h"
exploc = "C:\Program Files\Expedition\Expedition"
fname = "user_channels.h"
foutput = "expchdata.py"

# open and read file

print("Workding directory is", os.getcwd())
#f = open(fname, "r")

if (os.path.isfile(exploc + "\\" + fname) == True):
    print("Expedition user channels files found")
    fname = exploc + "\\" + fname
else:
    print("Expedition user channel file not found , using local copy")

# create the output file and add header
fo = open(foutput, "wt")
fo.write("#\n\
# expedition user data channels\n\
#\n\n\
expdata = [\n")

cnt = 0
# open user channel file and iterate
with open(fname, "r") as fi:
    for line in fi:
        if (len(line) > 1):
            if (line[0:2] != '//' and line.find(",") > 0):
                var = line.split(",")
                vname = var[0].removeprefix("\tEx")
                #print (vname, var)

                # add check for calculated variables which have '=' in the string
                # if '=' in string then split vname again
                if (cnt > 0):
                    fo.write(",\n")
                #print ('    {"metric": %d, "name": "%s", "value": 0}' % (cnt, vname))
                fo.write ('    {"metric": %d, "name": "%s", "value": 0}' % (cnt, vname))
                cnt = cnt + 1

# terminate the data structure
fo.write("\n]\n")

fo.close()

print ("Found %d user channels" % cnt)
# end of file