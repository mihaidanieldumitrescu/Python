
import re
import pprint
import json
import os

from Entries import Entries
from EntryNew import EntryNew

class Operations:
       
    def __init__(self, verbosity="none"):
        self.entries = Entries( '' )
        #self.entries.loadDebugValues()
        self.errorString = ""
        self.totalSpentMonth = {}
        self.verbosity = verbosity
        self.entries.printStatistics()
        self.entries.writeHtmlReport()
        self.entries.writeCSVdata()
        
    def __del__(self):

        if self.errorString:
            print "Following errors have been found after run: \n\n" + self.errorString