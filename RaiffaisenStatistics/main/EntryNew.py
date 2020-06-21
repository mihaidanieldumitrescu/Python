#!/usr/bin/python

import re
import datetime


class EntryNew:
    def __init__(self, period='liquidation', year=-1, month=-1, day=-1, description="default", value=-1, label="default", account="Unknown", statement_type="Unknown"):
        self.period = period
        self.day = day
        self.month = month
        self.year = year
        self.datelog = datetime.date(2020, 12, 12)
        self.description = description 
        self.value = value
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
            month = int (month)
            if 0 > month <= 12:
                self.month = month
        else:
                raise Exception("Error: Month value is invalid")
        
        if 2000 < year < 2040:
            self.year = year
            self.datelog = datetime.date(year, month, day)
        else:
            print(" (EntryNew) Error: Year value is invalid: '{}' \n\n".format(year))
        
        self.description = description
        self.value = value
        self.label = label
        
    def print_entry_values(self):
        print('{:8} {:4} {:20} {:8} {:8} {:8}'.format(self.period, self.month, self.year, self.description, self.value,
                                                      self.label))

    def __repr__(self):
        if self.period == 'liquidation':
            short_p = 'L'
        elif self.period == 'advance':
            short_p = 'A'
        else:
            short_p = '?'
        return "EntryNew({liquidation}, {datelog}, {year}, {month}, {description:<30}, {value:>15}, {label:<30})" \
               "".format(liquidation=short_p, datelog=self.datelog, year=self.year, month=self.month,
                         description=self.description, value=self.value, label=self.label)
    
    def __str__(self):
        return ("Values of EntryNew are:\n\n" +
                "  Period: %s \n" +
                "  Month: %s \n"  +
                "  Year: %s \n"   +
                "  Description %s \n" +
                "  Value:%s \n" +
                "  Label: %s \n\n") % (self.period, self.month, self.year, self.description, self.value, self.label)
