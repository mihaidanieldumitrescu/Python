#!/usr/bin/python

import re
import datetime


class EntryNew:
    def __init__(self, period='liquidation', year=None, month=None, day=None, date_log=None, description=None, value=None, suma_debit=None, suma_credit=None, label="default", account=None, statement_type=None):
        self.period = period
        self.day = day
        self.month = month
        self.year = year
        self.date_log = datetime.date(2020, 12, 12)
        self.description = description 
        self.value = value
        self.suma_debit = suma_debit
        self.suma_credit = suma_credit
        self.label = label
        self.account = account
        self.statementType = statement_type

        self.validate_entries(period, month, year, day, description, value, label)

    def validate_entries(self, period, month, year, day, description, value, label):
        year = int(year)
        day = int(day)

        # print("Debug periodInt '%s' \n"  %(periodInt )        )
        
        if period == 'liquidation' or period == 'advance':      
            self.period = period
        else:
            # shouldn't I try to categorize the period here?
            
            # 15 < days < lastDay of Month => advance, only for salary?
            
            print("(EntryNew) Error: Period value is invalid: '{}' \n\n".format(period))
            
        if re.match("[a-zA-Z]+", str(month)):
            self.month = month
            raise Exception(" (validateEntries) self.month is not numerical!")
        elif re.match("[0-9]+", str(month)):
            month = int(month)
            if 0 > month <= 12:
                self.month = month
        else:
            raise Exception("Error: Month value is invalid")
        
        if 2000 < year < 2040:
            self.year = year
            self.date_log = datetime.date(year, month, day)
        else:
            print(" (EntryNew) Error: Year value is invalid: '{}' \n\n".format(year))
        
        self.description = description
        self.value = value
        self.label = label
        
    def __repr__(self):
        if self.period == 'liquidation':
            short_p = 'L'
        elif self.period == 'advance':
            short_p = 'A'
        else:
            short_p = '?'
        return f"EntryNew({short_p}, {self.date_log}, {self.year}, {self.month}, {self.description:<30}, {self.value:>15}, {self.label:<30})"
    
    def __str__(self):
        return ("\n\n" +
                "  P: %s \n" +
                "  %s-%s-%s \n" +
                "  Description %s \n" +
                "  Value:%s \n" +
                "  Label: %s \n\n") % (self.period[0].upper(), self.day, self.month, self.year, self.description, self.value, self.label)
