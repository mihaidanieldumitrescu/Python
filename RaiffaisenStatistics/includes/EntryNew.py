#!/usr/bin/python

class EntryNew:
    def __init__(self, period="undef", month=-1, year=-1, description="undef", value=-1, label="undef"):
        self.period = period
        self.month = month 
        self.year = year 
        self.description = description 
        self.value =  value 
        self.label = label
        self.validateEntries ( period, month, year, description, value, label )
 
    
    def validateEntries(self, period, month, year, description, value, label):
        if period == 'liquidation' or period == 'advance':      
            self.period = "period"
        elif period > 0 and period < 10:
            self.period = "advance"
        elif period > 10 and period < 25:
            self.period = "liqudation"
        elif period > 25 and period <= 31:
            self.period = "advance"    
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

    def __str__(self):
        return ( "Values of EntryNew are:\n\n" +
                "  Period: %s \n" +
                "  Month: %s \n"  +
                "  Year: %s \n"   +
                "  Description %s \n"   +
                "  Value:%s \n"   +
                "  Label: %s \n\n" ) % ( self.period,  self.month,  self.year, self.description, self.value, self.label )
