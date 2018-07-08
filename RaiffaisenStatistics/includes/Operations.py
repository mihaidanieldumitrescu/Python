
import re
import pprint
import json
import os
import logging

from Entries import Entries
from EntryNew import EntryNew

class PrintEntries:
    
    def __init__(self):
        
        # this object contains only one month
        # values should be passed as an array
        # e.g. [ ['spent', 1000 ], [ 'food', 700 ] ]
        
        self.header = None # YEAR-MONTH
        self.leftListSummary = [] # spent 1000 lei ; food 700 lei
        self.rightListLabels = [] # spent; cash ATM => 10 lei
        self.rightOtherODescription = [] # HERVIG => 380 lei
    
    def __repr__(self):
        string = "leftListSummary has : {} elements\nrightListLabels has: {} elements\notherOpDescription has: {} elements\n".format ( len ( self.leftListSummary ), len ( self.rightListLabels ), len ( self.rightOtherODescription ))
        return string
        
    def printTerminal (self):
        
        columnSize = 50
        monthStatistics = [] 
        
        # merge and print labels from liquidation and advance for current month
        self.rightListLabels.reverse()
        for strLabels in self.leftListSummary:
            leftElement = "{}:  {} lei  ".format ( strLabels[0].ljust(columnSize), strLabels[1] ) if strLabels else "".ljust(columnSize)
            popElem = self.rightListLabels.pop()
            rightElement = popElem[0].ljust(columnSize) if popElem else ""
            
            monthStatistics.append ( "%s | %s " % ( leftElement, rightElement ) )
        print 
        # second part
        # merge other operations from liquidation and advance for current month    
        self.rightOtherODescription.reverse()    
        for strOtherOp in self.rightOtherODescription:
            leftElement = "".ljust(columnSize) 
            popElem = self.rightOtherODescription.pop()
            rightElement = popElem[0].ljust(columnSize) if popElem else ""
            
            monthStatistics.append ( "%s | %s " % ( leftElement, rightElement ) )
        
        if monthStatistics :
                print "\n".join ( monthStatistics )
                print        
    
    def printHTML(self):
        head = '<HTML><BODY>' # will not be needed
        tail = '</BODY></HTML>'
        
        data = []
        
        data.append ( "<TABLE>" ) 
        
class Operations:
       
    def __init__(self, verbosity="none"):
        self.entries = Entries( '' )
        #self.entries.loadDebugValues()
        self.errorString = ""
        self.totalSpentMonth = {}
        self.verbosity = verbosity
        self.htmlFrame = {}
        
        logging.basicConfig(filename='logfile_operations.log',filemode='w', level=logging.DEBUG)
        if 0:
            self.entries.printStatistics()
            self.entries.writeHtmlReport()
            self.entries.writeCSVdata()
        self.parseEntries()
        
    def parseEntries(self):
        
        # for each month in ascending order
        keyLabels = self.entries.getLabels()
        
        for monthlyReport in self.entries:
 
            currYear = monthlyReport[0].year
            currMonth = monthlyReport[0].month
            
            logging.info("CHANGED DATE TO: {}-{}".format ( currYear, currMonth ) )            
            printEntries = PrintEntries()
            
            # delete below
            monthStatistics = ""
            bufferMonth = {
                            "leftOtherOp" : [],
                            "rightOtherOp" : [],
                            "leftLabels" : [],
                            "rightLabels" : []
                        }
            tmpStatistics = ""
            liquidationStatistics = []
            advanceStatistics = []
            totalMonth = 0
            totalMonthByLabel = {}
            
            # first initialisation
            for label in keyLabels:
                key = label.split(';')[0]
                if not re.match ("_", key):
                    totalMonthByLabel[key] = 0
                    
            labelSummaryTotal = []
                                
            # for advance and liquidation
            for currPeriod in [ 'liquidation' ]:
 
                labelsMonthlyValuesDict = {}
                otherOperations = currPeriod + " entries: \n\n"
                labelSummary = []

                
                for currLabel in keyLabels:
                    labelsMonthlyValuesDict[currLabel] = 0
                
                # match values, print others    
                for currLabel in keyLabels:
                    for currEntry in monthlyReport:
                        if ( currEntry.period == currPeriod and
                             currEntry.label == currLabel):
                            
                            logging.info ( "ENTRY: {}-{} | Record {}-{}-{} | {} | {} | {}".format ( currYear, currMonth, currEntry.year, currEntry.month, currEntry.day,
                                                                                                    currEntry.label.ljust (15), currEntry.description.ljust (35), currEntry.value ) )
                            # get values for each lable
                            labelsMonthlyValuesDict[currLabel] += currEntry.value

                            if currEntry.label == "spent;other":
                                
                                # delete below
                                otherOperations += ( "%s - %s\n" % ( currEntry.description.ljust(30),
                                                                    ( str( currEntry.value) + " lei" ).ljust(10) ) )
                                printEntries.rightOtherODescription.append ( [ currEntry.description, currEntry.value ])
                                
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

                    print "%s, %s, %s" % ( currYear, currMonth, currPeriod )    
                    print '-' * 10 + "\n"
                    lastLabel = ""
                    totalLabel = 0
                    
                    for label in sorted( labelsMonthlyValuesDict ):
            
                        currLabelCategory = label.split(";")[0]
                        switchLabel = ''
                        
                        if lastLabel != currLabelCategory and lastLabel != "":    # if 'bills != food', when you get to the next category
                            if not ( re.match ("^_", lastLabel) and re.match ("^_", currLabelCategory)): # _salary category
                                if re.match ( "_", lastLabel ):
                                    switchLabel = '_income'
                                    incomeValue = totalLabel
                                else:
                                    switchLabel = lastLabel
                                    
                                # delete below
                                labelSummaryTotal.append ( "%s:  %s lei" % ( switchLabel.ljust(20), str( totalLabel ).rjust(7)   )  )
                                printEntries.leftListSummary.append ( [switchLabel, totalLabel ] )
                                # do not add input from income in month statistics
                                
                                if not re.match ("_", lastLabel):
                                    totalMonth += totalLabel
                                    totalMonthByLabel[lastLabel] += totalLabel
                                totalLabel = 0
                            else:
                                pass # print "Exception in lastlabel '{}' !".format ( lastLabel )
                            
                        # for each label add to month
                        totalLabel += labelsMonthlyValuesDict[label]
 
                        if labelsMonthlyValuesDict[label] != 0:
                            # delete below
                            labelSummary.append ("\t%s => %s lei  " % ( label.ljust(20), str( labelsMonthlyValuesDict[label] ).rjust(7)))
                            printEntries.rightListLabels.append ( [ label, labelsMonthlyValuesDict[label] ] )
                        else:
                            
                            # print formatting: use "-" instead of "0"
                            
                            # delete below
                            labelSummary.append ("\t%s    %s  -   " % ( label.ljust(20), "".rjust(7)))
                            printEntries.rightListLabels.append ( [ label, 0 ] )            
                            
                        lastLabel = label.split(";")[0]
                        
                    # for the last label (no more labels to compare)
                    
            
                    totalMonth += totalLabel
                    totalMonthByLabel[lastLabel] += totalLabel
                    
                    # delete below
                    labelSummaryTotal.append ("%s:  %s lei  " % ( lastLabel.ljust(20), str ( totalLabel ).rjust(7) ))
                    printEntries.leftListSummary. append ( [switchLabel, totalLabel ] )
                    labelSummaryTotal.append ("")
                    labelSummaryTotal.append( labelSummaryTotal.pop(0) ) # income will be last
            
                    remainingValue = incomeValue + totalMonth
                    
                    # delete below
                    labelSummaryTotal.append ("\n%s:  %s lei  " % ( "_total_spent".ljust(20), str ( totalMonth ).rjust(7) ))
                    labelSummaryTotal.append ("\n%s:  %s lei  " % ( "_remaining".ljust(20), str ( remainingValue ).rjust(7) ))
                    printEntries.leftListSummary.append ( ['_total_spent', totalMonth ] )
                    printEntries.leftListSummary.append ( ['_remaining', remainingValue ] )
                    printEntries.printTerminal()

            if 0:
                print "len values: %s %s \n" % (len ( bufferMonth['leftOtherOp'] ), len ( self.rightOtherODescription ))                    
                self.pp.pprint ( bufferMonth['leftOtherOp'] )
                self.pp.pprint ( self.rightOtherODescription)
                print "\n"
            

            
            if totalMonth != 0:
                print "_total_spent: {}\n\n".format ( totalMonth )
                for label in sorted (totalMonthByLabel):
                    pass # self.csvValues += "{};{};{};{}\n".format ( currYear,currMonth,label, totalMonthByLabel[label] )
                
            
            #self.pp.pprint( bufferMonth )
                
    def __del__(self):

        if self.errorString:
            print "Following errors have been found after run: \n\n" + self.errorString