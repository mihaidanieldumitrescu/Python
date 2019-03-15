from main.EntryNew import EntryNew as EntryNew

from html import HTML

from main.RaiffaisenStatement import Statement
from collections import deque
from dateutil.relativedelta import relativedelta

import logging
import datetime
import xlrd
import glob
import pprint
import os
import sys
import re
import json

class Entries:

    def __init__(self, input_file):
        self.config_dict = {}
        self.currentYear = []
        self.dictCurrentYear = {}

        self.statistics = {}
        self.manualEntries = []
        self.csvValues = ""

        self.dataVerification = []

        self.htmlOutput = HTML()
        self.htmlFrame = {}
        self.verbosity = "none"
        self.errorMsg = ""
        self.debugOutput = ""


        logging.basicConfig(filename='logfile.log', filemode='w', level=logging.DEBUG)

        # used mainly for manually extracted csv files

        self.extract_data_excel_sheets()

    def get_labels(self):
        labels = {}

        for item in self.currentYear:

            labels[item.label] = None

        key_list = labels.keys()

        return key_list

    def return_month_data(self, year, month):
        """returns data entries from first day of the month to the last"""

        data = []
        for item in self.currentYear:
            if item.year == year and item.month == month:
                
                data.append(item)
        return data

    def return_month_segment_data(self, begining_period_date, end_period_date):
        """this contains data from salary payment to the next salary"""

        data = []
        for item in self.currentYear:
            if begining_period_date <= item.datelog < end_period_date:
                data.append(item)
        return data

    def return_salary_payment_dates(self):
        data = []
        liquidation_dates = [datetime.date(2000, 1, 1)]  # dummy date

        for item in self.currentYear:
            if item.label == '_salary' and item.period == 'liquidation':
                data.append(item)

        for element in data:
            liquidation_dates.append(element.datelog)
        liquidation_dates.append(datetime.date(2040, 1, 1)) # dummy date
        return liquidation_dates

    def __iter__(self):

        self.paymentLiquidationDatesArr = self.return_salary_payment_dates()
        self.index = len(self.paymentLiquidationDatesArr) - 1

        if len(self.paymentLiquidationDatesArr) < 2 :
            print("( Entries::__iter__ ) Error! paymentLiquidationDatesArr has less than two elements!")
            sys.exit(1)

        logging.info("__iter__ initialized with paymentLiquidationDatesArr: \n{}\n\n".format(self.paymentLiquidationDatesArr))

        return self

    def __next__(self):

        # this will iterate for each month

        if self.index > 0:

            begining_period_date = self.paymentLiquidationDatesArr[self.index - 1]
            end_period_date = self.paymentLiquidationDatesArr[self.index]
            print("Reading data from '{}' to '{}' ...".format(begining_period_date, end_period_date - datetime.timedelta(days=1)))
            logging.info("__next__ '{}' -> '{}'".format (begining_period_date, end_period_date - datetime.timedelta(days=1)))
            data = self.return_month_segment_data(begining_period_date, end_period_date)

            self.index -= 1
            return data
        else:
            print
            print("Iteration reached it's end. Last begin value is {}".format(self.paymentLiquidationDatesArr[self.index + 1]))
            raise StopIteration

    def __del__(self):
        
        if self.debugOutput != "":
            print("(Entries) Debug output: \n\n" + self.debugOutput + "\n")

        if self.errorMsg != "":
            print("(Entries) Errors found: \n\n" + self.errorMsg + "\n")

    def __str__(self):
        tmp = ""
        for item in self.statistics.iteritems():
            tmp += str(item) + "\n"
        return tmp

    def return_values_dict(self):
        temp_str = ""
        for month in self.dictCurrentYear:
            for period in self.dictCurrentYear[month]:
                for entry in self.dictCurrentYear[month][period]:
                    temp_str += str(entry)
        return temp_str

    def get_entries_for(self, period, month):

        # print("Looking for entries for month '" + month + "' and period '" + period + "' :\n")
        entries_found = []
        for entry in self.currentYear:
            if entry.period == period and entry.month == month:
                entries_found.append(entry)
        return entries_found

    def new_entry(self, newEnt):
        """ Add a new EntryNew object """
        self.currentYear.append(newEnt)
        self.currentYear.sort(key=lambda x: x.datelog)

        self.dictCurrentYear[newEnt.month] = {}
        self.dictCurrentYear[newEnt.month][newEnt.period] = []
        self.dictCurrentYear[newEnt.month][newEnt.period].append(newEnt)

    def extract_data_excel_sheets(self):
        """ Load data from excel statement files """
        
        files = glob.glob(os.path.join(os.environ['OneDrive'], "PythonData", "extrasDeCont", "*xls"))

        with open(os.path.join(os.environ['OneDrive'], "PythonData", "config", "definedLabels.json")) as f:
            self.config_dict = json.load(f)

        if len(files) == 0:
            raise Exception("No files found in folder \n")

        for filename in files:

           statement = Statement ()
           statement.load_statement(filename)

           extract_statement_regex = re.match(r'(\d{2})/(\d{2})/(\d{2})', statement.data['headers']['Data generare extras'])
           if extract_statement_regex:
                   (day, month, year) = (extract_statement_regex.group(1), extract_statement_regex.group(2), extract_statement_regex.group(3))
                   sold_precendent_entry = EntryNew(day=day, month=month, year="20{}".format(year), description="Sold precendent!", value=statement.sold_precendent(), label="_soldPrecendent")
                   self.new_entry(sold_precendent_entry)
                   logging.info("(extractDataXLS ) Sold precendent: '{}'".format(sold_precendent_entry))
           else:
                   logging.warn("(extractDataXLS ) Date format is not what expected! Date found: '{}'".format(statement.data['headers']['Data generare extras']))

           # logging.info ("( extractDataXLS ) For filename '{}', extracted date was '{}.{}.{}'".format(filename, day, month, year ))

           for operation in statement.data['operations']:
                   (day, month, year) = operation['Data utilizarii cardului'].split("/")
                   op_description = operation['Descrierea tranzactiei'].split("|")[0]
                   if re.match("OPIB", operation['Descrierea tranzactiei']):
                      op_description = operation['Descrierea tranzactiei'].split("|")[1]
                   debit_value = operation['Suma debit']
                   credit_value = operation['Suma credit']
                   label_str = self.label_me(op_description)

                   data =("  Data: %s Operatie: %s Eticheta: %s\n " +
                            "  Valoare debit: %s Valoare credit: %s\n") % (operation['Data utilizarii cardului'], op_description, self.label_me(op_description),
                                                                         debit_value, credit_value)
                   if self.verbosity == "high":
                       print(data)

                   #self, period="undef", month=-1, year=-1, description.lower()="undef", value=-1, label="undef"
                   if "Trz IB conturi proprii" in op_description:
                       print("(Does not work!) Skipping 'Trz IB conturi proprii' entry!")

                   if debit_value:
                       self.new_entry(EntryNew(day=day, month=month, year=year, description=op_description, value=-debit_value, label=label_str))
                   elif credit_value:
                       #print("credit: %s : %s \n" %(op_description, credit_value ))
                       
                       if re.search("|".join(self.config_dict['salaryFirmName']), operation['Nume/Denumire ordonator/beneficiar'], re.IGNORECASE):
                           if 1 <= int(day) <= 15:
                                self.new_entry(EntryNew(day=day, month=month, year=year, description=op_description, value=credit_value, label="_salary"))
                           else:
                                self.new_entry(EntryNew(day=day, month=month, year=year, period='advance', description=op_description, value=credit_value, label="_salary"))
                       else:
                           whoTransfered = "_transferredInto"
                           if re.search("dumitrescu mihail", op_description.lower()):
                               whoTransfered = "_transferredTata"
                           self.new_entry(EntryNew(day=day, month=month, year=year, description=op_description, value=credit_value, label=whoTransfered))
                   else:
                       self.errorMsg += "Warn: No debit or credit values! \n\t* Row is: currRow\n\n"
        print( f"\nDone loading statement data ... Found {len(self.currentYear)} entries!\n\n")

    def label_me(self, description):
        """ Selects the correct label from json config file """
        
        master_labels = self.config_dict['labelDict']

        # {    "leisure" :  {
        #           "film": [ "cinema", "avatar media project" ] }
        # ...

        for masterLabel in master_labels:
            for childLabel in master_labels[masterLabel]:
                if re.search (r"|".join(master_labels[masterLabel][childLabel]), description.lower()):
                    return "%s;%s" % (masterLabel, childLabel)

        return "spent;other"

    def write_html_report(self):
        """ Writes html report from entries """

        html_output = HTML()
        table = html_output.table()
        for year in sorted (self.htmlFrame, reverse=True):
            print("%s" % (year))
            tr = table.tr
            tr.td (str(year))
            for month in sorted(self.htmlFrame[year], reverse=True):

                tr = table.tr
                tr.td (str(month))
                tr_per = table.tr

                dict_liq = self.htmlFrame[year][month]['liquidation']
                dict_adv = { 'labelSummary' : [] }
                if 0:
                    # will not be used anymore
                    dict_adv = self.htmlFrame[year][month]['advance']

                for entryLiq, entryAdv in zip(dict_liq['labelSummary'], dict_adv['labelSummary']): #
                    tr_nr = table.tr
                    for key in entryLiq:
                        tr_nr.td(str(key))
                        tr_nr.td(str(entryLiq[key]))

                    for key in entryAdv:
                        tr_nr.td(str(key))
                        tr_nr.td(str(entryAdv[key]))

        with open ("report.html", "w") as f:
            f.write(str (html_output))

    def write_csv_data(self):
        """ Writes CSV report """
        
        with open ("report.csv", "w") as f:
            f.write(self.csvValues )
