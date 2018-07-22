
import re
import pprint
import json
import os
import logging

from Entries import Entries
from EntryNew import EntryNew

class EntriesCollection:
    
    def __init__(self ):
        self.entries = []
        self.htmlData = []
        self.navigationHeaders = []
    
    def addMonthEntry(self, month):
        self.navigationHeaders.append ( month.header )
        self.entries.append ( month )
    
    def processData (self):
        head = '<html><head><link rel="stylesheet" type="text/css" href="main.css" /></head><body>' # will not be needed
        tail = '</body></html>'
        
        self.entries.reverse()
        self.navigationHeaders.reverse()

        self.htmlData.append(head)

        for entry in self.entries:
            # month div
            self.htmlData.append ( "<div class=\"{}.{}\">".format ( entry.header[0], entry.header[1] ) )
            self.htmlData.append ( "<h3>Statistics for {}.{}</h3>".format ( entry.header[0], entry.header[1] ) )

            			
            # statistics
            self.htmlData.append ( "<div class=\"{0}\"><table><th colspan=\"2\">{0}</th>".format ( "statistics" ))
            for row in entry.leftListSummary:
                self.htmlData.append ( "<tr><td>{}</td><td>{}<td></tr>".format ( row[0], row[1] )  )
                
            self.htmlData.append ("</table></div>")
            
            # label categories
            self.htmlData.append ( "<div class=\"{0}\"><table><th colspan=\"2\">{0}</th>".format ( "labelCategories" ))
            for row in entry.rightListLabels:
                self.htmlData.append ( "<tr><td>{}</td><td>{}<td></tr>".format ( row[0], row[1] )  )
                
            self.htmlData.append ("</table></div>")
            
            # filtered operations
            self.htmlData.append ( "<div class=\"{0}\"><table><th colspan=\"4\">{0}</th>".format ( "filteredOperations" ))
            
            isNotFood = []            
            isFood = []
            for row in entry.monthEntryData:
                if "food" in row[1]:
                    isFood.append ( row )
                else:
                    isNotFood.append ( row )
                    
            for row in isNotFood:
                self.htmlData.append ( "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format ( row[0], row[1], row[2], row[3] )  )
                
            self.htmlData.append ("</table></div>")
            
            # food detail
            self.htmlData.append ( "<div class=\"{0}\"><table><th colspan=\"4\">{0}</th>".format ( "foodDetail" ))
            for row in isFood:
                self.htmlData.append ( "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format ( row[0], row[1], row[2], row[3] )  )
                
            self.htmlData.append ("</table></div>")
        
            self.htmlData.append ("</div>")
        
        self.htmlData.append(tail)
    
    def writeHtmlReport( self):
        cssContents = """
            h3 {
            	background-color: lightblue;
                padding: 5px;
                padding-left: 10px;
            }
			
    		table {
                border-collapse: collapse;
            }
			
			th {
				background-color: lightgrey;	 
			}
			
            td:nth-child(1) { 
            	padding-right: 30px; 
            }
			
            td:nth-child(2) { 
             	 text-align: right;
            }
			
            td {
            	padding: 0px;
            }
 
			.statistics, .labelCategories, .otherLabelDetail, .filteredOperations, .foodDetail {
				vertical-align:top;
				margin-top: 50px;
				display: inline-block;
                margin-right: 20px
				
			}
			
			.statistics  
			{ 	
				margin-left: 20px;
			}
			
			.filteredOperations, .foodDetail, td:nth-child(2) { 
             	 text-align: left;
				 padding-right:20px;
            }
			.filteredOperations, .foodDetail, td:nth-child(3) { 
             	 text-align: left;
				 white-space: nowrap;				 
				 padding-right:20px;
			 
            }
			.filteredOperations .foodDetail, td:nth-child(4) { 
             	 text-align: right;
				 white-space: nowrap;
            }
			
			.navigation{
				background-color: lightblue;				
				display: block;
				vertical-align: bottom;
                padding-left: 10px;
			}
			.navigation   {

				padding:2px;
				overflow: hidden;
				position: fixed;
				bottom: 0;
				width: 100%;
				}
			a. {
			
				padding-left: 10px;
				padding:2px;
			}	
			a.active {
 
				color: white;
			}
			.navigation a:hover {
				background-color: #ddd;
				color: black;
			} """

        if not os.path.exists( "main.css" ):    
            with open ( "main.css", "w") as f:
                f.write( cssContents )    
        with open ( "reportLatest.html", "w") as f:
            f.write("\n".join (self.htmlData))
    
class PrintEntries:
    
    def __init__(self):
        
        # this object contains only one month
        # values should be passed as an array
        # e.g. [ ['spent', 1000 ], [ 'food', 700 ] ]
        
        self.header = None # YEAR-MONTH
        self.leftListSummary = [] # spent 1000 lei ; food 700 lei
        self.rightListLabels = [] # spent; cash ATM => 10 lei
        self.rightOtherODescription = [] # HERVIG => 380 lei
        self.monthEntryData = []
    
    def __repr__(self):
        string = "leftListSummary has : {} elements\nrightListLabels has: {} elements\notherOpDescription has: {} elements\n".format ( len ( self.leftListSummary ), len ( self.rightListLabels ), len ( self.rightOtherODescription ))
        string = "PrintEntries element for '{}'".format  ( self.header )
        
        return string
        
    def printTerminal (self):
        
        columnSize = 50
        monthStatistics = [] 
        print "%s, %s, %s" % ( self.header[0], self.header[1], self.header[2] )    
        print '-' * 10 + "\n"
        # merge and print labels from liquidation and advance for current month
 
        index = 0
        for item in self.rightListLabels:
            popElem = self.leftListSummary[index] if ( len ( self.leftListSummary ) > index ) else []
            
            if popElem and popElem[0] == "---":
                leftElement = popElem[0].ljust(50)
            else:
                leftElement = "{}   {} lei  ".format ( popElem[0].ljust(31), str ( "%.2f" % popElem[1] ).rjust(10) ) if popElem else "".ljust(columnSize)
                
            if item and item[0] == "---":
                rightElement = item[0].ljust (27)
            else:
                rightElement = "{} => {}".format ( item[0].ljust(20), str ( "%.2f" % item[1]).rjust(10)  ) if item else ""
            
            monthStatistics.append ( "{} | {} ".format ( leftElement, rightElement ) )
            index += 1    
        monthStatistics.append ( "{}   {} ".format( "".ljust(columnSize), "---------------".ljust(20) )  )
        # second part
        # merge other operations from liquidation and advance for current month    
        self.rightOtherODescription
        
        for strOtherOp in sorted( self.rightOtherODescription, key=lambda x: x[1], reverse=False):
            leftElement = "".ljust(columnSize) 
            popElem = strOtherOp
            rightElement = "{} => {}".format ( popElem[0].ljust(40), str( "%.2f" % popElem[1] ).rjust(10)) if popElem else ""
            
            monthStatistics.append ( "%s | %s " % ( leftElement, rightElement ) )
        
        if monthStatistics :
                print "\n".join ( monthStatistics )
                print        
        
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
        generateReportHTML = EntriesCollection()
        
        for monthlyReport in self.entries:
 
            currYear = monthlyReport[0].year
            currMonth = monthlyReport[0].month
            
            logging.info("CHANGED DATE TO: {}-{}".format ( currYear, currMonth ) )            
            printEntries = PrintEntries()
            
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
            for currPeriod in [ 'liquidation' ]:
 
                labelsMonthlyValuesDict = {}
                otherOperations = currPeriod + " entries: \n\n"
                labelSummary = []

                
                for currLabel in keyLabels:
                    labelsMonthlyValuesDict[currLabel] = 0
                entryData = []
                # match values, print others    
                for currLabel in keyLabels:
                    for currEntry in monthlyReport:
                        if ( currEntry.period == currPeriod and
                             currEntry.label == currLabel):
                            
                            logging.info ( "ENTRY: {}-{} | Record {}-{}-{} | {} | {} | {}".format ( currYear, currMonth, currEntry.year, currEntry.month, currEntry.day,
                                                                                                    currEntry.label.ljust (15), currEntry.description.ljust (35), currEntry.value ) )
                            printEntries.monthEntryData.append ( ( "{}-{}-{}".format ( currEntry.year, currEntry.month, currEntry.day),
                                                 currEntry.label, currEntry.description, currEntry.value ) )
                            # get values for each lable
                            labelsMonthlyValuesDict[currLabel] += currEntry.value

                            if currEntry.label == "spent;other":
                            
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
                    
                    printEntries.header = ( currYear, currMonth, currPeriod );
                    lastLabel = ""
                    totalCurrentLabel = 0
                    
                    # { 'spent;food' : 300 }
                    for label in sorted( labelsMonthlyValuesDict ):
            
                        currLabelCategory = label if re.match ( "_", label) else label.split(";")[0]
                        switchLabel = ''
                        
                        if lastLabel != currLabelCategory and lastLabel != "":    # if 'bills != food', when you get to the next category
   
                            if not ( re.match ("_", lastLabel) and re.match ("_", currLabelCategory)): # _salary category
                                
                                if ( re.match ("_", lastLabel)):
                                    printEntries.rightListLabels.append ( [ "---", 0 ] )
                                
                                # first category is called _income as lastLabel value will be _transferredTata
                                
                                if re.match ( "_", lastLabel ):
                                    switchLabel = '_income'
                                    incomeValue = totalCurrentLabel
                                else:
                                    switchLabel = lastLabel
                                    printEntries.rightListLabels.append ( [ "---", 0 ] )
                                    
                                printEntries.leftListSummary.append ( [switchLabel, totalCurrentLabel ] )
                                # do not add input from income in month statistics
                                
                                if not re.match ("_", lastLabel):
                                    sumOfAllLabels += totalCurrentLabel
                                    sumOfAllLabelsByLabel[lastLabel] += totalCurrentLabel
                                totalCurrentLabel = 0

                            else:
                                pass # print "Exception in lastlabel '{}' !".format ( lastLabel )
                                
                        # for each label add to month
                        totalCurrentLabel += labelsMonthlyValuesDict[label]
 
                        if labelsMonthlyValuesDict[label] != 0:
                            printEntries.rightListLabels.append ( [ label, labelsMonthlyValuesDict[label] ] )
                        else:
                            printEntries.rightListLabels.append ( [ label, 0 ] )            
                            
                        lastLabel = label if re.match ( "_", label) else label.split(";")[0]
                        
                    # for the last label (no more labels to compare)
                    
            
                    sumOfAllLabels += totalCurrentLabel
                    sumOfAllLabelsByLabel[lastLabel] += totalCurrentLabel
                    
                    printEntries.leftListSummary. append ( [lastLabel, totalCurrentLabel ] )
            
                    remainingValue = incomeValue + sumOfAllLabels
                    
                    printEntries.leftListSummary.append ( [ "---", 0 ] )
                    printEntries.leftListSummary.append ( printEntries.leftListSummary.pop(0))

                    printEntries.leftListSummary.append ( ['_total_spent', sumOfAllLabels ] )
                    printEntries.leftListSummary.append ( [ "---", 0 ] )
                    printEntries.leftListSummary.append ( ['_remaining', remainingValue ] )
                    printEntries.printTerminal()
                    generateReportHTML.addMonthEntry ( printEntries )
            if 0:
                print "len values: %s %s \n" % (len ( bufferMonth['leftOtherOp'] ), len ( self.rightOtherODescription ))                    
                self.pp.pprint ( bufferMonth['leftOtherOp'] )
                self.pp.pprint ( self.rightOtherODescription)
                print "\n"
            

            
            if sumOfAllLabels != 0:
 
                for label in sorted (sumOfAllLabelsByLabel):
                    pass # self.csvValues += "{};{};{};{}\n".format ( currYear,currMonth,label, sumOfAllLabelsByLabel[label] )
                
        generateReportHTML.processData()
        generateReportHTML.writeHtmlReport()
    
            #self.pp.pprint( bufferMonth )
                
    def __del__(self):

        if self.errorString:
            print "Following errors have been found after run: \n\n" + self.errorString