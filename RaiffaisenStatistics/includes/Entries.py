from main.EntryNew import EntryNew as EntryNew

from html import HTML

from main.RaiffaisenStatement import Statement
from collections import deque
from dateutil.relativedelta import relativedelta

import logging,datetime
import xlrd
import glob
import pprint
import os,sys
import re
import json

class Entries:

    def __init__(self, inputFile):
        #EntryNew.__init__()
        self.config_dict = {}
         #another line graph, but with two data types. Also adding title
        self.currentYear = []
        #this is intermediary
        self.dictCurrentYear = {}

        #{year}{month}{period} => value
        self.statistics = {}
        self.manualEntries = []
        self.csvValues = ""

        self.dataVerification = []

        self.htmlOutput = HTML()
        self.htmlFrame = {}
        self.verbosity = "none"
        self.pp = pprint.PrettyPrinter()
        self.errorMsg = ""
        self.debugOutput = ""
        self.verbosity = "none"
        

        logging.basicConfig(filename='logfile.log', filemode='w', level=logging.DEBUG)

        #used mainly for manually extracted csv files

        self.extractDataXLS(inputFile)

    def getLabels(self):
        labels = {}

        for item in self.currentYear:

            labels[item.label] = None

        key_list = labels.keys()

        return key_list

    def returnMonthData(self, year, month):
        """returns data entries from first day of the month to the last"""

        data = []
        for item in self.currentYear:
            if item.year == year and item.month == month:
                
                data.append(item)
        return data

    def returnMonthSegmentData(self, begining_period_date, end_period_date):
        """this contains data from salary payment to the next salary"""

        data = []
        for item in self.currentYear:
            if begining_period_date <= item.datelog < end_period_date:
                data.append(item)
        return data

    def returnSalaryPaymentDates(self):
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

        self.paymentLiquidationDatesArr = self.returnSalaryPaymentDates()
        self.index = len(self.paymentLiquidationDatesArr) - 1

        if len(self.paymentLiquidationDatesArr) < 2 :
            print("( Entries::__iter__ ) Error! paymentLiquidationDatesArr has less than two elements!")
            sys.exit(1)

        logging.info("__iter__ initialized with paymentLiquidationDatesArr: \n{}\n\n".format(self.paymentLiquidationDatesArr))

        return self

    def __next__(self):

        # this will iterate for each month

        if(self.index > 0 ) :

            begining_period_date = self.paymentLiquidationDatesArr[self.index - 1]
            end_period_date = self.paymentLiquidationDatesArr[self.index]
            print("Reading data from '{}' to '{}' ...".format(begining_period_date, end_period_date - datetime.timedelta(days=1)))
            logging.info("__next__ '{}' -> '{}'".format (begining_period_date, end_period_date  - datetime.timedelta(days=1)))
            data = self.returnMonthSegmentData(begining_period_date, end_period_date)

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

    def retValuesDict(self):
        tempStr = ""
        for month in self.dictCurrentYear:
            for period in self.dictCurrentYear[month]:
                for entry in self.dictCurrentYear[month][period]:
                    tempStr += str(entry)
        return tempStr

    def getEntriesFor(self, period, month):

        # print("Looking for entries for month '" + month + "' and period '" + period + "' :\n")
        entriesFound = []
        for entry in self.currentYear:
            if entry.period == period and entry.month == month:
                entriesFound.append(entry)
        return entriesFound

    def newEntry(self, newEnt):
        """ Add a new EntryNew object """
        self.currentYear.append(newEnt)
        self.currentYear.sort(key=lambda x: x.datelog)

        self.dictCurrentYear[newEnt.month] = {}
        self.dictCurrentYear[newEnt.month][newEnt.period] = []
        self.dictCurrentYear[newEnt.month][newEnt.period].append(newEnt)

    def extractDataXLS(self, dirname):
        """ Load data from excel statement files """
        
        files = glob.glob(os.path.join(os.environ['OneDrive'], "PythonData", "extrasDeCont", "*xls"))

        with open(os.path.join(os.environ['OneDrive'], "PythonData", "config", "definedLabels.json")) as f:
            self.config_dict = json.load(f)

        if len(files) == 0:
            raise Exception("No files found in folder \n")

        for filename in files:

           statement = Statement ()
           statement.loadStatement(filename)

           extractStatementRegex = re.match(r'(\d{2})/(\d{2})/(\d{2})', statement.data['headers']['Data generare extras'])
           if extractStatementRegex:
                   (day, month, year) = (extractStatementRegex.group(1), extractStatementRegex.group(2), extractStatementRegex.group(3))
                   soldPrecendentEntry = EntryNew(day=day, month=month, year="20{}".format(year), description="Sold precendent!", value=statement.soldPrecendent(), label="_soldPrecendent")
                   self.newEntry(soldPrecendentEntry)
                   logging.info("(extractDataXLS ) Sold precendent: '{}'".format(soldPrecendentEntry))
           else:
                   logging.warn("(extractDataXLS ) Date format is not what expected! Date found: '{}'".format(statement.data['headers']['Data generare extras']))

           #logging.info ("( extractDataXLS ) For filename '{}', extracted date was '{}.{}.{}'".format(filename, day, month, year ))

           for operation in statement.data['operations']:
                   (day, month, year) = operation['Data utilizarii cardului'].split("/")
                   opDescription = operation['Descrierea tranzactiei'].split("|")[0]
                   if re.match("OPIB", operation['Descrierea tranzactiei']):
                      opDescription = operation['Descrierea tranzactiei'].split("|")[1]
                   debitValue = operation['Suma debit']
                   creditValue = operation['Suma credit']
                   labelStr = self.labelMe(opDescription)

                   data =("  Data: %s Operatie: %s Eticheta: %s\n " +
                            "  Valoare debit: %s Valoare credit: %s\n") % (operation['Data utilizarii cardului'], opDescription, self.labelMe(opDescription),
                                                                         debitValue, creditValue)
                   if self.verbosity == "high":
                       print(data)

                   #self, period="undef", month=-1, year=-1, description.lower()="undef", value=-1, label="undef"
                   if "Trz IB conturi proprii" in opDescription:
                       print("(Does not work!) Skipping 'Trz IB conturi proprii' entry!")
                       
                       #next
                       
                   if debitValue:
                       self.newEntry(EntryNew(day=day, month=month, year=year, description=opDescription, value=-(debitValue), label=labelStr))
                   elif creditValue:
                       #print("credit: %s : %s \n" %(opDescription, creditValue ))
                       
                       if re.search("|".join(self.config_dict['salaryFirmName']), operation['Nume/Denumire ordonator/beneficiar'], re.IGNORECASE):
                           if (1 <= int(day) <= 15):
                                self.newEntry(EntryNew(day=day, month=month, year=year, description=opDescription, value=creditValue, label="_salary"))
                           else:
                                self.newEntry(EntryNew(day=day, month=month, year=year, period='advance', description=opDescription, value=creditValue, label="_salary"))
                       else:
                           whoTransfered = "_transferredInto"
                           if re.search("dumitrescu mihail", opDescription.lower()):
                               whoTransfered = "_transferredTata"
                           self.newEntry(EntryNew(day=day, month=month, year=year, description=opDescription, value=creditValue, label=whoTransfered))
                   else:
                       self.errorMsg += "Warn: No debit or credit values! \n\t* Row is: currRow\n\n"
        print( f"\nDone loading statement data ... Found {len(self.currentYear)} entries!\n\n")
           #self.pp.pprint((statement.data))

    def labelMe(self, description):
        """ Selects the correct label from json config file """
        
        masterLabels = self.config_dict['labelDict']

        # {    "leisure" :  {
        #           "film": [ "cinema", "avatar media project" ] }
        # ...

        for masterLabel in masterLabels:
            for childLabel in masterLabels[masterLabel]:
                if re.search (r"|".join(masterLabels[masterLabel][childLabel]), description.lower()):
                    return "%s;%s" % (masterLabel, childLabel)

        return "spent;other"

    def writeHtmlReport(self):
        """ Writes html report from entries """

        htmlOutput = HTML()
        table = htmlOutput.table()
        for year in sorted (self.htmlFrame, reverse=True):
            print("%s" % (year))
            tr = table.tr
            tr.td (str(year))
            for month in sorted(self.htmlFrame[year], reverse=True):

                tr = table.tr
                tr.td (str(month))
                tr_per = table.tr

                dictLiq = self.htmlFrame[year][month]['liquidation']
                dictAdv = { 'labelSummary' : [] }
                if 0:
                    # will not be used anymore
                    dictAdv = self.htmlFrame[year][month]['advance']

                for entryLiq, entryAdv in zip(dictLiq['labelSummary'], dictAdv['labelSummary']): #
                    tr_nr = table.tr
                    for key in entryLiq:
                        tr_nr.td(str(key))
                        tr_nr.td(str(entryLiq[key]))

                    for key in entryAdv:
                        tr_nr.td(str(key))
                        tr_nr.td(str(entryAdv[key]))

                    #for entry in dictCurr['otherOperations']:
                        #tr_per.td (str(entry))


        with open ("report.html", "w") as f:
            f.write(str (htmlOutput))

    def writeCSVdata(self):
        """ Writes CSV report """
        
        with open ("report.csv", "w") as f:
            f.write(self.csvValues )
