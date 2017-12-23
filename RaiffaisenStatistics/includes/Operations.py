
import re
import pprint
import json
import os

from Entries import Entries
from EntryNew import EntryNew

class Operations:
       
    def __init__(self, verbosity="none"):
        self.entries = Entries( "" )
        self.errorString = ""
        self.totalSpentMonth = {}
        self.verbosity = verbosity
        
    def __del__(self):
        self.entries.printStatistics()
        if self.errorString:
            print "Following errors have been found after run: \n\n" + self.errorString