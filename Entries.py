from EntryNew import EntryNew
from gpcharts import figure


from html import HTML
from pprint import pprint

import os.path
import re

class Entries(EntryNew):
    
    def __init__(self):

         #another line graph, but with two data types. Also adding title
        self.fig = figure(title='Cheltuieli', height=600, width=800)
        self.htmlOutput = HTML()
        self.currentYear = []
        self.dictCurrentYear = {}
        self.loadEntriesSCV()

    def retReference(self):
	return self.currentYear
        
    def printValues(self):
        for entry in self.currentYear:
            entry.printEntryValues()
            
    def printValuesDict(self):
        pprint (self.dictCurrentYear)
        for month in self.dictCurrentYear:
            for period in self.dictCurrentYear[month]:
                for entry in self.dictCurrentYear[month][period]:
                    entry.printEntryValues()

    def getEntriesFor(self,period, month):

        print "Looking for entries for month '" + month + "' and period '" + period + "' :\n"	
        entriesFound = []
        for entry in self.currentYear:
            if entry.period == period and entry.month == month:
                entriesFound.append(entry)
                entry.printEntryValues()
        return entriesFound
    
    def newEntry(self, newEnt):
        self.currentYear.append ( newEnt )
        self.dictCurrentYear[newEnt.month] = {}
        self.dictCurrentYear[newEnt.month][newEnt.period] = []
        self.dictCurrentYear[newEnt.month][newEnt.period].append(newEnt)
        #sort elements by EntryNew.month

    def loadEntriesSCV(self):
        if os.path.isfile("values.csv"):
            file = open ("values.csv" , "r")
            for row in file:
                elements = row.split(";")
                if len(elements) == 6:
                    elements[5] = elements[5].rstrip()
                    self.newEntry ( EntryNew( elements[0], elements[1], elements[2], elements[3], elements[4], elements[5]))
                    
            file.close()
        
    def writeGPchart(self):
        self.fig.column(['Aug-av','Aug-li','Sept-av','Sept-li'],['Suma',1303,440,600,200],['test',1])
        
    def loadDebugValues(self):
        if 0:
            self.currentYear.append ( EntryNew('liquidation', "1", 2017, "Drinks all night", '273', 'fun') )
            self.currentYear.append ( EntryNew('advance', "2", 2017, "Drinks all night", '153', 'fun') )
            self.currentYear.append ( EntryNew('liquidation', 2, 2017, "Girls night!", '457', 'fun') )
            self.currentYear.append ( EntryNew('liquidation', 2, 2017, "Girls night!", '846', 'fun') )
            self.currentYear.append ( EntryNew('advance', 3, 2017, "Boys night", '121', 'fun') )
            self.currentYear.append ( EntryNew('advance', 3, 2017, "Cinema", '121', 'movies') )
            self.currentYear.append ( EntryNew('advance', 3, 2017, "Popcorn", '121', 'movies') )
