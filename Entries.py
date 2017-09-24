
from EntryNew import EntryNew
from gpcharts import figure 

from html import HTML

import os.path
import re

class Entries(EntryNew):
    
    def __init__(self):
        print "Entries contructor ..."
         #another line graph, but with two data types. Also adding title
        self.fig = figure(title='Cheltuieli', height=600, width=800)
        self.htmlOutput = HTML()
        self.currentYear = []
        self.loadEntriesSCV()
        
    def printValues(self):
        for entry in self.currentYear:
            entry.printEntryValues()
    
    def newEntry(self, newEnt):
        self.currentYear.append ( newEnt )
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
            
    def writeOutputHTML(self):
        output = open ( "budgetStatistics.html", "w")
        current = EntryNew()
        table = self.htmlOutput.table()
        for entry in self.currentYear:
            row = table.tr
            if current.period != entry.period:
                current.period = entry.period
                row.td( entry.period )
            else:
                row.td()
                
            if current.month != entry.month:
                current.month = entry.month
                row.td( entry.month )
            else:
                row.td()
                
            if current.year != entry.year:
                current.year = entry.year
                row.td( entry.year )
            else:
                row.td()
            row.td( entry.description )
            row.td( entry.value )
            row.td( entry.label )

        output.write ( str (self.htmlOutput ) )
        output.close
        
    def writeGPchart(self):
        self.fig.column(['Aug-av','Aug-li','Sept-av','Sept-li'],['Suma',1303,440,600,200],['test',1])
        
    def sandbox(self):
        if 0:
            self.currentYear.append ( EntryNew('liquidation', "1", 2017, "Drinks all night", '273', 'fun') )
            self.currentYear.append ( EntryNew('advance', "2", 2017, "Drinks all night", '153', 'fun') )
            self.currentYear.append ( EntryNew('liquidation', 2, 2017, "Girls night!", '457', 'fun') )
            self.currentYear.append ( EntryNew('liquidation', 2, 2017, "Girls night!", '846', 'fun') )
            self.currentYear.append ( EntryNew('advance', 3, 2017, "Boys night", '121', 'fun') )
            self.currentYear.append ( EntryNew('advance', 3, 2017, "Cinema", '121', 'movies') )
            self.currentYear.append ( EntryNew('advance', 3, 2017, "Popcorn", '121', 'movies') )

