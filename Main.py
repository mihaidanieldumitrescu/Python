#!/usr/bin/env python

 
from Entries import Entries

print "Main ran ..."

debug = 0

lastYear = Entries()
#lastYear.printValues()
if debug == 1:
	lastYear.loadDebugValues()
lastYear.writeOutputHTML()

months  = [ "August", "September", "November", "December" ]
period  = ["liquidation", "advance" ]
for month in months:
	for per in period:
		lastYear.getEntriesFor( per, month)
#lastYear.writeGPchart()
