#
# Analysis the Expedition routing file and grade wind and angles
#
# this read the filtered output file and summarises
#

import os
import sys
from pathlib import Path
import datetime as dt
from datetime import timedelta
import csv
from openpyxl import Workbook
from openpyxl import load_workbook
#from openpyxl.cell import get_column_letter
from openpyxl.utils import get_column_letter
#from openpyxl.styles import Font
from openpyxl.styles import Color, PatternFill, Font, Border
from openpyxl.styles import Alignment

# columns for TWS and TWA
TWSCOL = 4
TWACOL = 6

# The input is the CSV file - default for testing
fname = "fastnet 210328 filt"

#print(f"Arguments count: {len(sys.argv)}")
for i, arg in enumerate(sys.argv):
    #print(f"Argument {i:>6}: {arg}")
    if (i == 1):
        fname = arg

ffile = Path(fname)
if ffile.is_file():
    print(f"Processing file {fname}")
else:
    fname = fname + '.csv'
    ffile = Path(fname)
    if ffile.is_file():
        print(f"Processing file {fname}")
    else:
        print(f"File {fname} not found")
        exit(1)

# and the output an Excel spreashsheet & name the sheet
exWorkbook = Workbook() # for Expedition
#exSheet = exWorkbook.active
exSheet = exWorkbook.worksheets[0]
exSheet.title = "Filter Summary" # different to default

# opens the csv file defined below.
inputfile = open(fname, 'rt')

# creates the reader object
reader = csv.reader(inputfile)
rownum = 0

#import winds.py # the shading file
# need to externalised these
# define the colours for shading
# see https://www.rapidtables.com/web/color/RGB_Color.html
Bft1Fill = PatternFill(start_color='778899', end_color='778899', fill_type='solid')
Bft2Fill = PatternFill(start_color='87CEFA', end_color='87CEFA', fill_type='solid')
Bft3Fill = PatternFill(start_color='00BFFF', end_color='00BFFF', fill_type='solid')
Bft4Fill = PatternFill(start_color='4682B4', end_color='4682B4', fill_type='solid')
Bft5Fill = PatternFill(start_color='008000', end_color='008000', fill_type='solid')
Bft6Fill = PatternFill(start_color='FF8C00', end_color='FF8C00', fill_type='solid')
Bft7Fill = PatternFill(start_color='FA8072', end_color='FA8072', fill_type='solid')
Bft8Fill = PatternFill(start_color='DC143C', end_color='DC143C', fill_type='solid')
Bft9Fill = PatternFill(start_color='DB7093', end_color='DB7093', fill_type='solid')
Bft10Fill = PatternFill(start_color='DC143C', end_color='DC143C', fill_type='solid')

colours = Bft1Fill, Bft2Fill, Bft3Fill, Bft3Fill, Bft5Fill, Bft6Fill, Bft7Fill, Bft8Fill, Bft9Fill
# add - list of dicts
Winds = [
    {'low': 0.0, 'high': 4.0, 'fill': Bft1Fill}, # 1
    {'low': 4.0, 'high': 7.0, 'fill': Bft2Fill}, # 2
    {'low': 7.0, 'high': 11.0, 'fill': Bft3Fill}, # 3
    {'low': 11.0, 'high': 17.0, 'fill': Bft4Fill},
    {'low': 17.0, 'high': 22.0, 'fill': Bft5Fill},
    {'low': 22.0, 'high': 28.0, 'fill': Bft6Fill},
    {'low': 28.0, 'high': 34.0, 'fill': Bft7Fill},
    {'low': 34.0, 'high': 41.0, 'fill': Bft8Fill},
    {'low': 41.0, 'high': 48.0, 'fill': Bft9Fill}
]

dateDelta = timedelta(days=0, hours=0, minutes=0, seconds=0)
Angles = [
    {"low": 0, "high": 30, "tot": 0, "percent": 0}, # high
    {"low": 30, "high": 60, "tot": 0, "percent": 0}, # close hauled
    {"low": 60, "high": 90, "tot": 0, "percent": 0}, # cracked
    {"low": 90, "high": 120, "tot": 0, "percent": 0}, # reaching
    {"low": 120, "high": 150, "tot": 0, "percent": 0}, 
    {"low": 150, "high": 180, "tot": 0, "percent": 0} # running
]

twsTotal = 0.0
twsCnt = 0
offset = 0
bucket = [0, 0, 0]
# add rows to spreadsheet from csv file
# csv starts from 0,0 and worksheet 1,1 so '+1' needed
prevDttm = 0
dttmInv = 0
totalDttm = 0

# construct the 2 dim array for the times of 40 x 8
rows = 40
cols = 18
Times = [[0.0] * cols for i in range(rows)] 

#dateDelta = timedelta(days=0, hours=0, minutes=0, seconds=0)
for row_index, row in enumerate(reader):
    totWind = 0
    col = 0 # used to count output columns
    for column_index, cell in enumerate(row):
        #if (column_index >= 15 and column_index <= 28): # skip Rain/MSLP
        #    continue

        if (cell.isnumeric()): # doesn't cover '.'
            cell = int(cell)

        # we assume wind range is 1 to 40
        if (row_index > 8 and row_index < 49): # the filter data
            #
            if (column_index == 0): # label
                cell = float(cell)
                rowLabel = cell

            if (column_index > 0): # column to process
                col = col + 1
                column_letter = get_column_letter((column_index + 1))

                cell = float(cell)
                totWind = totWind + cell

                Times[row_index - 9][col - 1] = cell

                # shade TWS based on wind strenght
                #for bft in Winds:
                    #if (cell >= bft["low"] and cell < bft["high"]):
                        #exSheet.cell((row_index + 1), (column_index + 1)).fill = bft["fill"]
                        #continue;

        exSheet.cell((row_index + 1), (column_index + 1)).value = cell
        #exSheet.cell('%s%s'%(column_letter, (row_index + 1))).value = cell

    # now we've processed a row if a filt row add the total hours
    if (row_index > 8 and row_index < 49): # the filter data
        exSheet.cell((row_index + 1), (column_index + 1 + 2)).value = totWind
        exSheet.cell((row_index + 1), (column_index + 1 + 2)).number_format = '0.000'

    #print (totWind)

# define an array of 6 x 6 for the Summ
Summ = [[0.0] * 6 for i in range(6)]

# total should be 40
Rows = [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, # 22+
        4, 4, 4, 4,  # 18 - 21
        3, 3, 3, 3,  # 14 - 17
        2, 2, 2, 2,  # range 10 - 13
        1, 1, 1, 1, # range 6 - 9
        0, 0, 0, 0, 0, 0] # range 1-5

# and 18 columns
Cols = [0, 0, 0, 0, 0, 0,
        1, 1,
        2, 2,
        3, 3,
        4, 4,
        5, 5, 5, 5]

tot = 0 # do the summing
for row in range (rows):
    for col in range (cols):
        tot = tot + Times[row][col]

        # use a data structure to do the mapping into buckets
        Summ[Rows[row]][Cols[col]] = Summ[Rows[row]][Cols[col]] + Times[row][col]

# location of hr summ 
rowoff = 53
coloff = 5
tabloff = 10

# Add the row col headers for the summary
col = 0
for hdr in ("0-60", "60-80", "80-100", "100-120", "120-140", "140+", "Total"):
    exSheet.cell((rowoff - 1), (coloff + col)).value = hdr
    exSheet.cell((rowoff - 1), (coloff + col)).font = Font(bold = True)
    exSheet.cell((rowoff - 1), (coloff + col)).alignment = Alignment(horizontal = 'right')

    exSheet.cell((rowoff - 1 + tabloff), (coloff + col)).value = hdr
    exSheet.cell((rowoff - 1 + tabloff), (coloff + col)).font = Font(bold = True)
    exSheet.cell((rowoff - 1 + tabloff), (coloff + col)).alignment = Alignment(horizontal = 'right')
    col = col + 1

row = 0
for hdr in ("0 - 6", "6 - 10", "10 - 14", "14 - 18", "18 - 22", "22+", "Total"):
    exSheet.cell((rowoff + row), (coloff - 1)).value = hdr
    exSheet.cell((rowoff + row), (coloff - 1)).font = Font(bold = True)
    exSheet.cell((rowoff + row), (coloff - 1)).alignment = Alignment(horizontal = 'right')

    exSheet.cell((rowoff + row + tabloff), (coloff - 1)).value = hdr
    exSheet.cell((rowoff + row + tabloff), (coloff - 1)).font = Font(bold = True)
    exSheet.cell((rowoff + row + tabloff), (coloff - 1)).alignment = Alignment(horizontal = 'right')
    row = row + 1

# Sum rows - we calc this first so we have it for percentage calc
totHrs = 0.0
for row in range(40):
    #print (row, Times[row][0])
    for col in range (18):
        totHrs = totHrs + Times[row][col]

exSheet.cell((rowoff + 6), (coloff + 6)).value = totHrs
exSheet.cell((rowoff + 6), (coloff + 6)).number_format = '0.00'

# add summ to sheet
for row in range(6):
    tot = 0
    for col in range (6):
        # houra
        exSheet.cell((rowoff + row), (coloff + col)).value = Summ[row][col]
        exSheet.cell((rowoff + row), (coloff + col)).number_format = '0.00'
        # and percentage
        exSheet.cell((rowoff + row + tabloff), (coloff + col)).value = Summ[row][col]/totHrs
        exSheet.cell((rowoff + row + tabloff), (coloff + col)).number_format = '0.0%'
        tot = tot + Summ[row][col]

    exSheet.cell((rowoff + row), (coloff + 6)).value = tot
    exSheet.cell((rowoff + row), (coloff + 6)).number_format = '0.00'
    exSheet.cell((rowoff + row + tabloff), (coloff + 6)).value = tot/totHrs
    exSheet.cell((rowoff + row + tabloff), (coloff + 6)).number_format = '0.0%'

for col in range(6):
    tot = 0
    for row in range (6):
        #exSheet.cell((rowoff + row), (coloff + col)).value = Summ[row][col]
        #exSheet.cell((rowoff + row), (coloff + col)).number_format = '0.00'
        tot = tot + Summ[row][col]
    exSheet.cell((rowoff + 6), (coloff + col)).value = tot
    exSheet.cell((rowoff + 6), (coloff + col)).number_format = '0.00'
    exSheet.cell((rowoff + 6 + tabloff), (coloff + col)).value = tot/totHrs
    exSheet.cell((rowoff + 6 + tabloff), (coloff + col)).number_format = '0.0%'

# Sum rows
totHrs = 0.0
for row in range(40):
    #print (row, Times[row][0])
    for col in range (18):
        totHrs = totHrs + Times[row][col]

exSheet.cell((rowoff + 6), (coloff + 6)).value = totHrs
exSheet.cell((rowoff + 6), (coloff + 6)).number_format = '0.00'
print (f"Total hours {totHrs}")



# added the avg wind at the bollot
#exSheet.cell((twsCnt + 2), (TWSCOL)).value = 'Average:'
#exSheet.cell((twsCnt + 2), (TWSCOL + 1)).value = twsTotal/twsCnt
#exSheet.cell((twsCnt + 2), (TWSCOL + 1)).number_format = '0.0'
#exSheet.cell((twsCnt + 2), (TWSCOL + 1)).font = Font(bold = True)
# format 1 decimal place - ws['A1'].number_format = '0.00%'

# And the wind buckets - 
clr = 0
#for rng in Angles:
    #per = rng["percent"]/totalDttm
    #exSheet.cell(twsCnt + 6 + clr, 6).value = clr + 1
    #exSheet.cell(twsCnt + 6 + clr, 7).value = str(int(rng["low"])+1) + "-" + str(int(rng["high"]))
    #exSheet.cell(twsCnt + 6 + clr, 8).value = per # rng["percent"]
    #exSheet.cell(twsCnt + 6 + clr, 8).number_format = '00.0%'
    #clr = clr + 1

# added the wind scaling @53 x 12 - the scaling
#exSheet.cell(twsCnt + 6, 11).value = "Wind (Bft)"

#clr = 0
#for clr in range(9):
    #exSheet.cell(twsCnt + 6 + clr, 12).value = clr + 1
    #exSheet.cell(twsCnt + 6 + clr, 13).value = str(int(Winds[clr]["low"])) + "-" + str(int(Winds[clr]["high"])-1)
    #exSheet.cell(twsCnt + 6 + clr, 13).fill = Winds[clr]["fill"]


#print ("TWS ", twsTotal, twsTotal/twsCnt, twsCnt) # Avg wind
# and remove extension
oname, fext = os.path.splitext(fname)
exWorkbook.save(oname + ".xlsx")

# end of file

