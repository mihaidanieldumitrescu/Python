#!/usr/bin/python

import re
import datetime

class EntryNew:
    def __init__(self, period='liquidation', year=-1, month=-1, day=-1, description="default", value=-1, label="default"):
        self.period = period
        self.day = day
        self.month = month
        self.year = year
        self.datelog = datetime.date ( 2020,12,12)
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
            print " (EntryNew) Error: Period value is invalid: '{}' \n\n".format ( period )            
            
        if ( re.match ( "[a-zA-Z]+", str ( month ) ) ):
            self.month = month
            raise Exception ( " (validateEntries) self.month is not numerical!")
        elif ( ( re.match ( "[0-9]+", str ( month ) ) )):
            month = int ( month )
            if month > 0 and month <= 12:      
                self.month = month

        else:
                raise Exception ( "Error: Month value is invalid" )
        
        if year > 2000 and year < 2040:
           self.year = year
           self.datelog = datetime.date( year, month, day )
        else:
            print " (EntryNew) Error: Year value is invalid: '{}' \n\n".format ( year )
        
        self.description = description
        self.value = value
        self.label = label
        
    def printEntryValues(self):
        print '{:8} {:4} {:20} {:8} {:8} {:8}'.format ( self.period,  self.month,  self.year, self.description, self.value, self.label )
        
    def __repr__(self):
        shortP = ""
        if self.period == 'liquidation':
            shortP = 'L'
        elif self.period == 'liquidation':
            shortP = 'A'
        else:
            shortP = '?'
        return "{} {} {} {} {} {} {}".format ( shortP, self.datelog , self.year, self.month, self.description.ljust (30), str( self.value).rjust(15), self.label.ljust(30) )
    
    def __str__(self):
        return ( "Values of EntryNew are:\n\n" +
                "  Period: %s \n" +
                "  Month: %s \n"  +
                "  Year: %s \n"   +
                "  Description %s \n"   +
                "  Value:%s \n"   +
                "  Label: %s \n\n" ) % ( self.period,  self.month,  self.year, self.description, self.value, self.label )
