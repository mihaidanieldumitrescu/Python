#!/usr/bin/python

 
from Entries import Entries
from WriteHtmlOutput import WriteHtmlOutput

print "Main ran ...\n"

debug = 0



if debug == 1:
	lastYear.loadDebugValues()
writer = WriteHtmlOutput( Entries("statistici2016.csv") )
