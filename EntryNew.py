#!/usr/bin/python

class EntryNew:
    def __init__(self,period="undef", month=-1, year=-1, description="undef", value=-1, label="undef"):
        self.period = period
        self.month = month
        self.year = year
        self.description = description
        self.value = value
        self.label = label
 
    
    def newEntry(self, period, month, year, description, value, label):
        if period == 'liquidation' or period == 'advance':      
            self.period = period
        else:
            return "Error: Period must be either 'liquidation' or 'advance'"
        
        if month > 0 and month <= 12:      
            self.month = month
        else:
            return "Error: Month value is invalid"
        
        if year > 2000 and  year % 4 == 0:
           self.year = year
        else:
            return "Error: Year value is invalid"
        self.description = description
        self.value = value
        self.label = label
        
    def printEntryValues(self):
        print '{:8} {:4} {:20} {:8} {:8} {:8}'.format ( self.period,  self.month,  self.year, self.description, self.value, self.label )
