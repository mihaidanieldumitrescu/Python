#!/usr/bin/python

import re

class EntryNew:
    def __init__(self, period='liquidation', year=-1, month=-1, day=-1, description="default", value=-1, label="default"):
        self.period = period
        self.day = day
        self.month = month
        self.year = year 
        self.description = description 
        self.value =  value 
        self.label = label
        self.validateEntries ( period, month, year, day, description, value, label )
 
    
    def validateEntries( self, period, month, year, day, description, value, label):
        advanceSubtractMonth = 0
        year = int ( year )
        day =  int ( day )
        #print "Debug periodInt '%s' \n"  % ( periodInt )
        if period == 'liquidation' or period == 'advance':      
            self.period = 'liquidation'
        else:            
            periodInt = int ( period )
            
        if ( re.match ( "[a-zA-Z]+", str ( month ) ) ):
            self.month = month
        elif ( ( re.match ( "[0-9]+", str ( month ) ) )):
            month = int ( month )
            if month > 0 and month <= 12:      
                self.month = month
        else:
                self.month = -1
                return "Error: Month value is invalid"
        
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
