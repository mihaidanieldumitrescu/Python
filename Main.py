#!/usr/bin/env python

 
from Entries import Entries

print "Main ran ..."
lastYear = Entries()
lastYear.printValues()
lastYear.writeOutputHTML()
lastYear.writeGPchart()