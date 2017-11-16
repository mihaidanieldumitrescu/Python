from EntryNew import EntryNew

from html import HTML
from pprint import pprint

import os.path
import re

class Entries(EntryNew):
    
    def __init__(self, inputFile):

         #another line graph, but with two data types. Also adding title
        self.csvInputfile = inputFile
        self.currentYear = []
        #this is intermediary
        self.dictCurrentYear = {}
        #{year}{month}{period} => value
        self.statistics = {}
        
        #used mainly for manually extracted csv files
        self.loadEntriesSCV()

    def __str__(self):
        tmp = ""
        for item in self.statistics.iteritems():
            tmp += str( item ) + "\n"
        return tmp

    def retReference(self):
        return self.currentYear
        
    def printValues(self):
        for entry in self.currentYear:
            print str( entry )
    
    def printStatistics(self):
        #how do I convert array to hash?
        
        ( keyYears, keyMonth, keyPeriods, keyLabels ) = ( {}, {}, {}, {})
        for entryNewItem in self.currentYear:
            ( keyYears[entryNewItem.year],
              keyMonth[entryNewItem.month],
              keyPeriods[entryNewItem.period],
              keyLabels[ entryNewItem.label] ) = (  "", "", "", "" )
        
        #dict initialisation
        for currYear in sorted(keyYears):
            for currMonth in sorted(keyMonth):
                for currPeriod in sorted( keyPeriods ):
                    print "%s, %s, %s \n\n" % ( currYear, currMonth, currPeriod )
                    
                    labelsPeriod = {}
                    
                    for currLabel in keyLabels:
                        labelsPeriod[currLabel] = 0
                        
                    for currLabel in keyLabels:
                        for currEntry in self.currentYear:
                            if currEntry.year == currYear and currEntry.month == currMonth and currEntry.period == currPeriod and currEntry.label == currLabel:
                                labelsPeriod[currLabel] += currEntry.value 
                    for label in sorted(labelsPeriod):
                        print "%s => %s lei" % ( label, labelsPeriod[label])
                    print "\n"
                    
                    
    def retValuesDict(self):
        tempStr = ""
        for month in self.dictCurrentYear:
            for period in self.dictCurrentYear[month]:
                for entry in self.dictCurrentYear[month][period]:
                    tempStr += str ( entry )
        return tempStr 

    def getEntriesFor(self, period, month):

        # print "Looking for entries for month '" + month + "' and period '" + period + "' :\n"	
        entriesFound = []
        for entry in self.currentYear:
            if entry.period == period and entry.month == month:
                entriesFound.append(entry)
        return entriesFound
    
    def newEntry(self, newEnt):
        self.currentYear.append ( newEnt )
        
        self.dictCurrentYear[newEnt.month] = {}
        self.dictCurrentYear[newEnt.month][newEnt.period] = []
        self.dictCurrentYear[newEnt.month][newEnt.period].append(newEnt)

    def loadEntriesSCV(self):
        if os.path.isfile(self.csvInputfile):
            file = open (self.csvInputfile , "r")
            for row in file:
                elements = row.split(";")
                if len(elements) == 6:
                    elements[5] = elements[5].rstrip()
                elements[4] = elements[4].replace(",", ".")
            
            self.newEntry ( EntryNew( elements[0], elements[1], elements[2], elements[3], elements[4], elements[5]))
                    
            file.close()
        else:
            print "File '" + self.csvInputfile + "' was not found!\n"
        
    def loadDebugValues(self):
        if 0:
            self.currentYear.append ( EntryNew('liquidation', "1", 2017, "Drinks all night", '273', 'fun') )
            self.currentYear.append ( EntryNew('advance', "2", 2017, "Drinks all night", '153', 'fun') )
            self.currentYear.append ( EntryNew('liquidation', 2, 2017, "Girls night!", '457', 'fun') )
            self.currentYear.append ( EntryNew('liquidation', 2, 2017, "Girls night!", '846', 'fun') )
            self.currentYear.append ( EntryNew('advance', 3, 2017, "Boys night", '121', 'fun') )
            self.currentYear.append ( EntryNew('advance', 3, 2017, "Cinema", '121', 'movies') )
            self.currentYear.append ( EntryNew('advance', 3, 2017, "Popcorn", '121', 'movies') )
