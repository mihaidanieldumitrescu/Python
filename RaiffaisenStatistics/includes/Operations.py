
import re
import pprint
import json
import os
import logging

from mySQL_interface.GenerateSQLfile import GenerateSQLfile
from includes.Entries import Entries
from includes.WriteHtmlOutput import EntriesCollection
from main.EntryNew import EntryNew
from datetime import date


class PrintEntries:

    def __init__(self):

        # this object contains only one month
        # values should be passed as an array
        # e.g. [ ['spent', 1000 ], [ 'food', 700 ] ]

        self.header = None # YEAR-MONTH
        self.subHeader = None
        self.leftListSummary = [] # [( bills, 700 ),( food, 1000 ) ]
        self.rightListLabels = [] #(spent;cash ATM, 100 )
        self.rightOtherODescription = [] #(HERVIG, 380 )
        self.monthEntryData = [] #(date , label, description, value )

    def __repr__(self):
        string = "PrintEntries element for '{}'".format (self.header )

        return string

    def printTerminal (self):

        columnSize = 50
        monthStatistics = []
        print("%s, %s, %s" %(self.header[0], self.header[1], self.header[2] ))
        print('-' * 10 + "\n")
        # merge and print(labels from liquidation and advance for current month)

        index = 0
        for item in self.rightListLabels:
            popElem = self.leftListSummary[index] if(len(self.leftListSummary ) > index ) else []

            if popElem and popElem[0] == "---":
                leftElement = popElem[0].ljust(50)
            else:
                leftElement = "{}   {} lei  ".format(popElem[0].ljust(31), str("%.2f" % popElem[1] ).rjust(10) ) if popElem else "".ljust(columnSize)

            if item and item[0] == "---":
                rightElement = item[0].ljust (27)
            else:
                rightElement = "{} => {}".format(item[0].ljust(20), str("%.2f" % item[1]).rjust(10)  ) if item else ""

            monthStatistics.append("{} | {} ".format(leftElement, rightElement ) )
            index += 1
        monthStatistics.append("{}   {} ".format( "".ljust(columnSize), "---------------".ljust(20) )  )
        # second part
        # merge other operations from liquidation and advance for current month
        self.rightOtherODescription

        for strOtherOp in sorted( self.rightOtherODescription, key=lambda x: x[1], reverse=False):
            leftElement = "".ljust(columnSize)
            popElem = strOtherOp
            rightElement = "{} => {}".format(popElem[0].ljust(40), str( "%.2f" % popElem[1] ).rjust(10)) if popElem else ""

            monthStatistics.append("%s | %s " %(leftElement, rightElement ) )

        if monthStatistics :
                print("\n".join(monthStatistics ))
                print()

class Operations:

    def __init__(self, verbosity="none"):
        self.entries = Entries( '' )
        #self.entries.loadDebugValues()
        self.errorString = ""
        self.totalSpentMonth = {}
        self.verbosity = verbosity
        self.htmlFrame = {}
        self.sql_file = GenerateSQLfile()

        logging.basicConfig(filename='logfile_operations.log',filemode='w', level=logging.DEBUG)
        if 0:
            self.entries.printStatistics()
            self.entries.writeHtmlReport()
            self.entries.writeCSVdata()
        self.parseEntries()

    def parseEntries(self):

        # for each month in ascending order
        keyLabels = self.entries.getLabels()
        generateReportHTML = EntriesCollection()

        for monthlyReport in self.entries:
            if not monthlyReport:
                continue
            currYear = monthlyReport[0].year
            currMonth = monthlyReport[0].month

            logging.info("CHANGED DATE TO: {}-{}".format(currYear, currMonth ) )
            printEntries = PrintEntries()
            printEntries.subHeader = [ monthlyReport[0].datelog, monthlyReport[-1].datelog  ]
            monthStatistics = ""
            tmpStatistics = ""
            liquidationStatistics = []
            advanceStatistics = []
            sumOfAllLabels = 0
            sumOfAllLabelsByLabel = {}

            # first initialisation
            for label in keyLabels:
                key = label.split(';')[0]
                if not re.match ("_", key):
                    sumOfAllLabelsByLabel[key] = 0

            # for advance and liquidation

            labelsMonthlyValuesDict = {}
            currPeriod = ''
            otherOperations = currPeriod + " entries: \n\n"
            labelSummary = []
            entryData = []

            for currLabel in keyLabels:
                labelsMonthlyValuesDict[currLabel] = 0

            # match values, print(others)
            for currLabel in keyLabels:
                for currEntry in monthlyReport:
                    if(currEntry.label == currLabel):

                        self.sql_file.add_entry(currEntry)

                        # print("<...> ;{};{};{}-{}-{};{};;".format(currEntry.label.replace(";","."), currEntry.description, currEntry.year, currEntry.month, currEntry.day, currEntry.value ))
                        logging.info("ENTRY: {}-{} | Record {}-{}-{} | {} | {} | {}".format(currYear, currMonth, currEntry.year, currEntry.month, currEntry.day,
                                                                                                currEntry.label.ljust (15), currEntry.description.ljust (35), currEntry.value ) )
                        printEntries.monthEntryData.append(( "{}-{}-{}".format(currEntry.year, currEntry.month, currEntry.day),
                                             currEntry.label, currEntry.description, currEntry.value ) )
                        # get values for each lable
                        labelsMonthlyValuesDict[currLabel] += currEntry.value

                        if currEntry.label == "spent;other":

                            printEntries.rightOtherODescription.append([ currEntry.description, currEntry.value ])
            lastEntryDate = []
            for item in monthlyReport:
                lastEntryDate.append(item.day )
            lastEntryDate.sort()

            # we finished gathering data, now we use the data
            # check for months that have no data
            hasData = 0

            for label in sorted( labelsMonthlyValuesDict ):

                # bills;internet       => -109.59 lei
                # at least one label has value

                if labelsMonthlyValuesDict[label] != 0:
                    hasData = 1

            if hasData:

                incomeValue = 0

                # headers for each month
                # 2017, 8, liquidation
                # ----------

                printEntries.header =(currYear, currMonth, currPeriod );
                lastLabel = ""
                totalCurrentLabel = 0

                # { 'spent;food' : 300 }
                for label in sorted( labelsMonthlyValuesDict ):

                    currLabelCategory = label if re.match("_", label) else label.split(";")[0]
                    switchLabel = ''

                    if lastLabel != currLabelCategory and lastLabel != "":    # if 'bills != food', when you get to the next category

                        if not(re.match ("_", lastLabel) and re.match ("_", currLabelCategory)): # _salary category

                            if(re.match ("_", lastLabel)):
                                printEntries.rightListLabels.append([ "---", 0 ] )

                            # first category is called _rulaj as lastLabel value will be _transferredTata

                            if re.match("_", lastLabel ):
                                switchLabel = '_rulaj'
                                incomeValue = totalCurrentLabel
                            else:
                                switchLabel = lastLabel
                                printEntries.rightListLabels.append([ "---", 0 ] )

                            printEntries.leftListSummary.append([switchLabel, totalCurrentLabel ] )
                            # do not add input from rulaj in month statistics

                            if not re.match ("_", lastLabel):
                                sumOfAllLabels += totalCurrentLabel
                                sumOfAllLabelsByLabel[lastLabel] += totalCurrentLabel
                            totalCurrentLabel = 0

                        else:
                            pass # print("Exception in lastlabel '{}' !".format(lastLabel ))

                    # for each label add to month
                    totalCurrentLabel += labelsMonthlyValuesDict[label]

                    if labelsMonthlyValuesDict[label] != 0:
                        printEntries.rightListLabels.append([ label, labelsMonthlyValuesDict[label] ] )
                    else:
                        printEntries.rightListLabels.append([ label, 0 ] )

                    lastLabel = label if re.match("_", label) else label.split(";")[0]

                # for the last label (no more labels to compare)


                sumOfAllLabels += totalCurrentLabel
                sumOfAllLabelsByLabel[lastLabel] += totalCurrentLabel

                printEntries.leftListSummary. append([lastLabel, totalCurrentLabel])

                remainingValue = incomeValue + sumOfAllLabels
                printEntries.leftListSummary = sorted(printEntries.leftListSummary, key=lambda x: x[1], reverse=False)
                printEntries.leftListSummary.insert(-1, [ "---", 0 ] )
                #printEntries.leftListSummary.append(printEntries.leftListSummary.pop(0))

                printEntries.leftListSummary.append(['_total_spent', sumOfAllLabels])
                printEntries.leftListSummary.append([ "---", 0 ] )
                printEntries.leftListSummary.append(['_remaining_{}-{}'.format(lastEntryDate[-1], currMonth), remainingValue])
                #printEntries.printTerminal()
                generateReportHTML.addMonthEntry(printEntries)
                generateReportHTML.addChartRow(date(currYear, currMonth, 5), printEntries. leftListSummary)
            if 0:
                print("len values: %s %s \n" % (len(bufferMonth['leftOtherOp']), len(self.rightOtherODescription)))
                print(pprint.pformat(bufferMonth['leftOtherOp']))
                print(pprint.pformat(self.rightOtherODescription))
                print("\n")

            print("SQL file contents\n\n")
            print(str(self.sql_file))
            print()

            if sumOfAllLabels != 0:

                for label in sorted (sumOfAllLabelsByLabel):
                    pass # self.csvValues += "{};{};{};{}\n".format(currYear,currMonth,label, sumOfAllLabelsByLabel[label] )

        generateReportHTML.processData()
        generateReportHTML.writeHtmlReport()

            #self.pp.pprint( bufferMonth )
