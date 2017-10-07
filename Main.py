#!/usr/bin/python

 
from Entries import Entries
from WriteHtmlOutput import WriteHtmlOutput

print "Main ran ...\n"

debug = 0

lastYear = Entries("statistici2016.csv")

if debug == 1:
	lastYear.loadDebugValues()
writer = WriteHtmlOutput(lastYear)
