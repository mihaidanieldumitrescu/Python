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
        advanceSubtractMonth = 0 
        periodInt = int (period)
        print "Debug periodInt '%s' \n"  % ( periodInt )
        if period == 'liquidation' or period == 'advance':      
            self.period = period
        elif periodInt >= 1 and periodInt < 10:
            self.period = "advance"
            advanceSubtractMonth = 1
        elif periodInt >= 10 and periodInt < 25:
            self.period = "liquidation"
        elif periodInt >= 25 and periodInt <= 31:
            self.period = "advance"    
        else:
            return "Error: Period must be either 'liquidation' or 'advance'"
        month = int ( month )
        if month > 0 and month <= 12:      
            self.month = month
            if advanceSubtractMonth:
                if month == 1: 
                    self.month = 12
                else:
                    self.month -= 1
        else:
            return "Error: Month value is invalid"
        year = int ( year )
        if year > 2000:
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
