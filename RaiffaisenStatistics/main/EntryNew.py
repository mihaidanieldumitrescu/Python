#!/usr/bin/python

import re
import datetime as dt


class EntryNew:
    def __init__(self, period='liquidation', date_log=None, description=None, value=None, suma_debit=None, suma_credit=None, label="default", account=None, statement_type=None):
        self.period = period
        self.day = None
        self.month = None
        self.year = None
        self.date_log = date_log
        self.description = description 
        self.value = value
        self.suma_debit = suma_debit
        self.suma_credit = suma_credit
        self.label = label
        self.account = account
        self.statementType = statement_type

        self.validate_entries(period, description, value, label)

    def validate_entries(self, period, description, value, label):
        year = int(self.date_log.year)
        day = int(self.date_log.day)

        self.period = "liquidation" if 1 <= int(self.date_log.day) <= 15 else "advance"

        if re.match("[a-zA-Z]+", str(self.date_log.month)):
            self.month = self.date_log.month
            raise ValueError(" (validateEntries) self.month is not numerical!")
        elif re.match("[0-9]+", str(self.date_log.month)):
            month = int(self.date_log.month)
            if 0 > month <= 12:
                self.month = month
        else:
            raise ValueError("Error: Month value is invalid")
        
        if 2000 < year < 2040:
            self.year = year
            self.date_log = dt.date(year, month, day)
        else:
            print(" (EntryNew) Error: Year value is invalid: '{}' \n\n".format(year))
        
        self.description = description
        self.value = value
        self.label = label
    
    def __str__(self):
        return ("  %s \n" +
                "  %s \n" +
                "  Description %s \n" +
                "  Value: %s \n" +
                "  suma_debit: %s \n" +
                "  suma_credit: %s \n" +
                "  Label: %s \n\n") % (self.period[0].upper(), self.date_log, self.description, self.value, self.suma_debit, self.suma_credit, self.label)
