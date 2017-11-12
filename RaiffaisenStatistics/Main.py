#!/usr/bin/python

import glob

import xlrd

from includes.Operations import Operations
from includes.Entries import Entries
from includes.WriteHtmlOutput import WriteHtmlOutput

print "Main ran ...\n"

debug = 1
fDebug = "./extrasDeCont/Extras_15165113_21042017.xls"


files = glob.glob("./extrasDeCont/*xls")

#for f in files:


if debug == 1:
	files = [fDebug]

loadData = Operations ()
for f in files:
	loadData.extractDataXLS(f)
#writer = WriteHtmlOutput( Entries("statistici2016.csv") )