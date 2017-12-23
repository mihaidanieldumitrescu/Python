#!/usr/bin/python

import glob

import xlrd

from includes.Operations import Operations
from includes.Entries import Entries
from includes.WriteHtmlOutput import WriteHtmlOutput

print "Main ran ...\n"

debug = 0
fDebug = "./extrasDeCont/Extras_15165113_21042017.xls"

if debug == 1:
	files = [fDebug]

loadData = Operations ()
#writer = WriteHtmlOutput( Entries("statistici2016.csv") )