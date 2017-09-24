#!/usr/bin/env python

 
from Entries import Entries

print "Main ran ..."

debug = 0

lastYear = Entries()
#lastYear.printValues()
if debug == 1:
	#lastYear.loadDebugValues()
lastYear.writeOutputHTML()
lastYear.getEntriesFor("liquidation", "August")
#lastYear.writeGPchart()
