#!/usr/bin/python

import glob

import xlrd
from includes.Entries import Entries
from includes.WriteHtmlOutput import WriteHtmlOutput

print "Main ran ...\n"

debug = 0

files = glob.glob("./input/*xls")

for f in files:
	print "trying to open " + f 
	book = xlrd.open_workbook( f )
	sh = book.sheet_by_index(0)
	for rx in range(sh.nrows):
		index = 0
		for cell in sh.row(rx):
			if ( str (cell).find("empty")) != -1:
				next
			print( str ( cell ) + " ")
			index += 1
		print "\n\n"
	print "\n\n" 


if debug == 1:
	lastYear.loadDebugValues()
#writer = WriteHtmlOutput( Entries("statistici2016.csv") )