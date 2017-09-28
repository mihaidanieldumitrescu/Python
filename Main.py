#!/usr/bin/python

 
from Entries import Entries
from WriteHtmlOutput import WriteHtmlOutput

print "Main ran ..."

debug = 0

lastYear = Entries()
#lastYear.printValues()
if debug == 1:
	lastYear.loadDebugValues()
writer = WriteHtmlOutput(lastYear)
#lastYear.writeOutputHTML()

months  = [ "August", "September", "November", "December" ]
period  = ["liquidation", "advance" ]

lastYear.printValuesDict()
#lastYear.writeGPchart()
