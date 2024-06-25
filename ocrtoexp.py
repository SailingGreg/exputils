#
# program to parse ocr 'csv' polars to create expedition polars
#
# recommendation is to add the beat/run figures and save this as the 'input' text file
#
# OCR data via https://jieter.github.io/orc-data/site/#extremes
#

import sys

# the extension we add to the generated file
fext = '-polar.txt'

if sys.version_info < (3,6):
    print ("python 3.6 needed for formatting")
    exit(0)

# do command line checks
if len( sys.argv ) <= 1:
    print ("Please specifiy the file to process")
    exit (0)

fname = sys.argv[1]
fbase = fname.split('.')[0] # remove the extension

try:
    fd = open(fname, "r")
except:
    print(f'Error opening "{fname}"')
    exit(0)

lines = fd.readlines()

# now split base on line and build array
cnt = 1
knots = []
angls = []
for line in lines:
    #print(line)
    line = line.strip('\n')
    ents = line.split(';') 
    #print (ents)
    if (cnt == 1): # first line
        idx = 1
        for val in ents:
            if idx != 1:
                knots.append(val )
            idx = idx + 1
        print(f'Winds in the polar for {fbase} are {knots}')
    else:
        angls.append(ents)
        idx = 0
    #print(ents[idx])
    cnt = cnt + 1
        
    
# we need to sort the angles as ocr appends the vmg figures
angls = sorted(angls, key=lambda x: float(x[0]) )

try:
    of = open (fbase + fext, "w")
except:
    print(f"Can't open output file {fname + fext}")
    exit (0)

idx = 1
for spd in knots:
    str = spd
    for ent in angls:
        if (float(ent[0]) == 0): # we allow the first entry to be an angle of '0'
            #print (ent[0], ent[idx])
            str = str + "\t" + ent[0] + "\t" + ent[idx]
        if (float(ent[idx]) > 0.0): # else it has to have velocity
            #print (ent[0], ent[idx])
            str = str + "\t" + ent[0] + "\t" + ent[idx]
    idx = idx + 1
    of.write(str + '\n')
    #print(str)

of.close()
print (f"Polar polars written to {fbase + fext}")

# end of file
