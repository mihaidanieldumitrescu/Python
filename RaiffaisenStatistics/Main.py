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
	print("{0} {1} {2}".format(sh.name, sh.nrows, sh.ncols))
	for rx in range(sh.nrows):
    		print(sh.row(rx))	


if debug == 1:
	lastYear.loadDebugValues()
#writer = WriteHtmlOutput( Entries("statistici2016.csv") )
