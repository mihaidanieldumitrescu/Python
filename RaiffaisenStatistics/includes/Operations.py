
import re
import pprint
import json
import os
import logging

from Entries import Entries
from EntryNew import EntryNew
from datetime import date

class EntriesCollection:
    
    def __init__(self ):
        self.entries = []
        self.htmlData = []
        self.navigationHeaders = []
        self.chartData = []
        self.chartDataBills = []
        self.chartDataTotals = []
        self.rentValue = self.loadRentValue ()
        
    def loadRentValue (self):
        tmp = ""
        with open ( os.path.join ( os.environ['OneDrive'], "PythonData", "config", "definedLabels.json") )  as f:
            tmp = json.load( f )
        return tmp['rentValue']
    
    def addChartRow ( self, date, labelsArr ):
        dividerLineValue = 6000
        
        # labelsArr: [ [ labelName, value ], [ labelName, value ], [ labelName, value ], [ labelName, value ] ]
        monthConversion = " new Date ( \"{}-{:02d}-{:02d}\" )".format ( date.year, date.month, date.day )
        
        '''
            data.addColumn('number', 'cash');
            data.addColumn('number', 'spent');
            data.addColumn('number', 'bills');
            data.addColumn('number', 'transport');
            data.addColumn('number', 'food');
            data.addColumn('number', 'leisure');
            data.addColumn('number', 'travel');
        '''
        
        control = 0
        valuesArr = []
        valuesTotal = 0
        defLabels = (  'cash', 'spent', 'bills', 'transport', 'food', 'leisure', 'travel' )
        soldPrecendent = 0
        for elem in self.entries:
            for pair in elem.rightListLabels:
                if '_soldPrecendent' == pair[0]:
                    soldPrecendent = ( int ( pair[1] ))
                    print "Found soldPrecendent '{}'".format (soldPrecendent)
        for seekedLabel in defLabels:
            # ['_rulaj', -100]
            for pair in labelsArr:
                if seekedLabel == pair[0]:
                    valuesArr.append ( "{: <8}".format ( int ( pair[1] * -1) ) )
                    valuesTotal += int ( pair[1] * -1) 
                    control += 1
                    
        incomeValue = 0
        
        for pair in labelsArr:
            if '_rulaj'  == pair[0]:
                incomeValue = "{: <8}".format ( int ( pair[1] ) ) 
                
        valuesToStr = ""
        if control == len (defLabels):
            #  [ new Date ( 2018, 8, 3 ) 

            rentValue = 0
            
            #  [  new Date ( "2018-09-05" ),  6000  , 1100    , 286     , 0       , 244     , 225     , 0       , 0        ] ,             
            self.chartData.append ( "\t\t\t\t[ {},  {: <6}, {: <6} ] ".format ( monthConversion, dividerLineValue, ", ".join ( valuesArr ) ) )
            
            self.chartDataBills.append ( "\t\t\t\t[ {},  {: <6}, {: <6},  {: <6},  {: <6} ] ".format ( monthConversion, dividerLineValue, self.rentValue, valuesArr[2], valuesArr[4] ) )  
            #  [  new Date ( "2018-09-05" ),  6000  , 1855  , 6001     ] , 2
            self.chartDataTotals.append ( "\t\t\t\t[ {},  {: <6}, {: <6}, {: <6}, {: <6} ] ".format ( monthConversion, dividerLineValue, valuesTotal, incomeValue , soldPrecendent ) )

        else:
            logging.warn ( "EntriesCollection::addChartRow: Error! Expected '{}' labels! \n\n Value of labelsArr is: {}".format ( len ( defLabels ),  labelsArr )  )
                                
    def addMonthEntry(self, month):
        self.navigationHeaders.append ( month.header )
        self.entries.append ( month )
        
    def chartDataToString ( self, chartData):
        tmp = ""
        chartDataCpy = chartData
        
        while ( len ( chartDataCpy ) > 0 ):
            
            tmp += chartDataCpy.pop()             
            if len ( chartDataCpy ) > 0:
                tmp += ", \n"
        
        return tmp

    def processData (self):
        head = '''<html>
                    <head>  <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
                    <script src="chart.js"></script>
                  <link rel="stylesheet" type="text/css" href="main.css" /></head><body>''' # will not be needed
        tail = '</body></html>'
        
        self.htmlData.append ( head )
        self.htmlData.append ( "<h3>Yearly graphics</h3>" )
        self.htmlData.append ( "<div id='chart_wrapper'><div id='chart_div'></div></div>" )
        self.htmlData.append ( "<div id='chart_wrapper'><div id='chart_div2'></div></div>" )
        self.htmlData.append ( "<div id='chart_wrapper'><div id='chart_div3'></div></div>" )


        for entry in self.entries:
            # month div
            self.htmlData.append ( "<div class=\"{}.{}\">".format ( entry.header[0], entry.header[1] ) )
            self.htmlData.append ( "<h3>Statistics for {}.{} -> Period segment from {} to {} </h3>".format ( entry.header[0], entry.header[1], entry.subHeader[0], entry.subHeader[1] ) )

            			
            # statistics
            self.htmlData.append ( "<div class=\"{0}\"><table><th colspan=\"2\">{0}</th>".format ( "statistics" ))
            for row in entry.leftListSummary:
                self.htmlData.append ( "<tr><td>{}</td><td>{}</td></tr>".format ( row[0], "%.2f" % round(row[1] ,2) if row[1] != 0 else "" )  )
                
            self.htmlData.append ("</table></div>")
            
            # label categories
            self.htmlData.append ( "<div class=\"{0}\"><table><th colspan=\"2\">{0}</th>".format ( "labelCategories" ))
            for row in entry.rightListLabels:
                self.htmlData.append ( "<tr><td>{}</td><td>{}</td></tr>".format ( row[0], "%.2f" % round(row[1] ,2) if row[1] != 0 else "" )  )
                
            self.htmlData.append ("</table></div>")
            
            
            isEverythingElse= []            
            isFood = []
            isTransport = []
            isBill = []
            for row in entry.monthEntryData:
                if   "bills" in row[1]:
                    isBill.append ( row )   
                elif "food" in row[1]:
                    isFood.append ( row )
                elif "transport" in row[1]:
                    isTransport.append ( row )
                else:
                    isEverythingElse.append ( row )
            
            # bills and spendings
            
            self.htmlData.append ( "<div class=\"{0}\"><table><th colspan=\"4\">{1}</th>".format ( "billsAndOtherDetail", "otherDetail" ))
            
            totals = 0
            rulaj = 0
            for row in isEverythingElse:
                self.htmlData.append ( "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format ( row[0], row[1], row [2].title( ), "%.2f" % round(row[3] ,2) )  )
                if row[3] <= 0:
                    totals +=  row[3]
                else:
                    rulaj += row[3]
            self.htmlData.append ( "<tr class='totals'><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format ( "", "", "Total spent", "%.2f" % round( totals, 2 ) )  )
            self.htmlData.append ( "<tr class='totals'><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format ( "", "", "Income", "%.2f" % round( rulaj, 2 ) )  )

            totals = 0
            
            self.htmlData.append ( "</table><table style=\"margin-top: 20px;\"><th colspan=\"4\">{0}</th>".format ( "bills" ))
            
            for row in isBill:
                self.htmlData.append ( "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format ( row[0], row[1], row [2].title( ), "%.2f" % round(row[3] ,2) )  )
                totals +=  row[3] 
            self.htmlData.append ( "<tr class='totals'><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format ( "", "", "Total", "%.2f" % round( totals, 2 ) )  )

            self.htmlData.append ("</table></div>")
            
            # food and transport detail
            

            self.htmlData.append ( "<div class=\"{0}\"><table><th colspan=\"4\">{1}</th>".format ( "foodAndTransportDetail", "transportDetail" ))
            
            totals = 0
            for row in isTransport:
                self.htmlData.append ( "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format ( row[0], row[1], row [2].title( ), "%.2f" % round(row[3] ,2) )  )
                totals +=  row[3] 
            self.htmlData.append ( "<tr class='totals'><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format ( "", "", "Total", "%.2f" % round( totals, 2 ) )  )
    
            self.htmlData.append ( "</table><table style=\"margin-top: 20px;\"><th colspan=\"4\">{0}</th>".format ( "foodDetail" ))
            totals = 0
            for row in isFood:
                self.htmlData.append ( "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format ( row[0], row[1], row [2].title( ), "%.2f" % round(row[3] ,2) )  )
                totals +=  row[3] 

            self.htmlData.append ( "<tr class='totals'><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format ( "", "", "Total", "%.2f" % round( totals, 2 ) )  )
            totals = 0
            
            self.htmlData.append ("</table></div>")
        
            self.htmlData.append ("</div>")
        
        self.htmlData.append(tail)
    
    def writeHtmlReport( self):
        cssContents = '''  
            h3 {
                background-color: lightblue;
                padding: 5px;
                padding-left: 10px;
            }
            
            table {
                background-color: beige;
                border-collapse: collapse;
                width: 100%;
            }
            
            .totals { background-color: lightgreen; }
            th { background-color: burlywood; }
            
            td:nth-child(1) { padding-right: 30px; }
            
            td:nth-child(2) { text-align: right; }
            
            td { padding: 0px; }
            
            #chart_wrapper {
                overflow-x: scroll;
                overflow-y: hidden;
                width: 1900px;
            }
            
            .statistics, .labelCategories, .otherLabelDetail, .otherDetail, .billsAndOtherDetail, .foodAndTransportDetail {
                vertical-align:top;
                margin-top: 50px;
                display: inline-block;
                margin-right: 20px
            }
            
            .statistics  { 	margin-left: 20px;
            }
            .statistics td:nth-child(2), .labelCategories  td:nth-child(2) { 
                text-align: right;
                padding-right: 0px;
            }
            
            .otherDetail, .foodAndTransportDetail, td:nth-child(2) { 
                text-align: left;
                padding-right:20px;
            }
            .otherDetail, .foodAndTransportDetail, td:nth-child(3) { 
                text-align: left;
                white-space: nowrap;                
                padding-right:20px;
            
            }
            .otherDetail .foodAndTransportDetail, td:nth-child(4) { 
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
            a.active { color: white; }
            
            .navigation a:hover {
                background-color: #ddd;
                color: black;
            } '''
            
        chartJS = '''
            google.charts.load('current', {packages: ['corechart']});
            google.charts.setOnLoadCallback(drawCategoryStacked);
            google.charts.setOnLoadCallback(drawCategorySideBySide);
            google.charts.setOnLoadCallback(drawDetail);
            
            function drawCategoryStacked() {
                  var data = new google.visualization.DataTable();
                  data.addColumn('date', 'month');
                  data.addColumn('number', 'divider');
                  data.addColumn('number', 'cash');
                  data.addColumn('number', 'spent');
                  data.addColumn('number', 'bills');
                  data.addColumn('number', 'transport');
                  data.addColumn('number', 'food');
                  data.addColumn('number', 'leisure');
                  data.addColumn('number', 'travel');
                  data.addRows(dataArr);
                  
                  var options = {
                    height: 800,
                    width: 3000,
                    hAxis: { title: 'Segmente luna' },
                    vAxis: { title: 'Lei' },
                    seriesType: 'bars',
                    isStacked: true,
                    series: { 0: {type: 'line', color: 'grey', enableInteractivity: false, visibleInLegend: false }}
                  };
            
                  var chart = new google.visualization.ComboChart(document.getElementById('chart_div2'));
            
                  chart.draw(data, options);
            }
            
            function drawCategorySideBySide() {
                  var data = new google.visualization.DataTable();
                  data.addColumn('date', 'month');
                  data.addColumn('number', 'divider');
                  data.addColumn('number', 'rent');
                  data.addColumn('number', 'bills');
                  data.addColumn('number', 'food');

                  data.addRows(dataArr3);
                  
                  var view = new google.visualization.DataView(data);
                  view.setColumns([ 0, 2, 3, 4,
                        {
                            calc: function (dt, row) {
                            return dt.getValue(row, 2) + dt.getValue(row, 3)+ dt.getValue(row, 4);
                        },
                            type: "number",
                            role: "annotation"
                        } ]);
                  var options = {
                    height: 800,
                    width: 3000,
                    hAxis: { title: 'Luna' },
                    vAxis: { title: 'Lei' },
                    seriesType: 'bars',
                    isStacked: true,
                  };
            
                  var chart = new google.visualization.ComboChart(document.getElementById('chart_div3'));
            
                  chart.draw(view, options);
            }
            
            
            function drawDetail() {
                  var data = new google.visualization.DataTable();
                  data.addColumn('date', 'month');
                  data.addColumn('number', 'divider');
                  data.addColumn('number', 'spent');
                  data.addColumn('number', 'rulaj');
                  data.addColumn('number', 'soldPrecendent');

                  

                  data.addRows(dataArr2);
                  
                var view = new google.visualization.DataView(data);
                view.setColumns([ 0, 1,
                       2,
                       { calc: "stringify",
                         sourceColumn: 2,
                         type: "string",
                         role: "annotation" },
                       3,
                       { calc: "stringify",
                         sourceColumn: 3,
                         type: "string",
                         role: "annotation" },
                        4,
                        { calc: "stringify",
                         sourceColumn: 4,
                         type: "string",
                         role: "annotation" }]);
                  var options = {
                    height: 800,
                    width: 3000,
                    hAxis: { title: 'Luna' },
                    vAxis: { title: 'Lei' },
                    seriesType: 'bars',
                    series: { 0: {type: 'line', color: 'grey', enableInteractivity: false, visibleInLegend: false }}
                  };
            
                  var chart = new google.visualization.ComboChart(document.getElementById('chart_div'));
            
                  chart.draw(view, options);
            }

            var dataArr = [ \n\n''' + self.chartDataToString(self.chartData) + ''' \n\t\t\t];          
            var dataArr3= [ \n\n''' + self.chartDataToString(self.chartDataBills ) + ''' \n\t\t\t];
            var dataArr2 = [ \n\n''' + self.chartDataToString(self.chartDataTotals ) + ''' \n\t\t\t];
            
        '''

        with open ( "main.css", "w") as f:
            f.write( cssContents )
            
        with open ( "chart.js", "w" ) as f:
            f.write ( chartJS )
            
        with open ( "reportLatest.html", "w") as f:
            f.write("\n".join (self.htmlData))
    
class PrintEntries:
    
    def __init__(self):
        
        # this object contains only one month
        # values should be passed as an array
        # e.g. [ ['spent', 1000 ], [ 'food', 700 ] ]
        
        self.header = None # YEAR-MONTH
        self.subHeader = None
        self.leftListSummary = [] # [( bills, 700 ), (  food, 1000 ) ]
        self.rightListLabels = [] # ( spent;cash ATM, 100 )
        self.rightOtherODescription = [] # ( HERVIG, 380 )
        self.monthEntryData = [] # ( date , label, description, value )
    
    def __repr__(self):
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
            if not monthlyReport:
                continue
            currYear = monthlyReport[0].year
            currMonth = monthlyReport[0].month
            
            logging.info("CHANGED DATE TO: {}-{}".format ( currYear, currMonth ) )            
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
                
            # match values, print others    
            for currLabel in keyLabels:
                for currEntry in monthlyReport:
                    if ( currEntry.label == currLabel ):
                        
                        logging.info ( "ENTRY: {}-{} | Record {}-{}-{} | {} | {} | {}".format ( currYear, currMonth, currEntry.year, currEntry.month, currEntry.day,
                                                                                                currEntry.label.ljust (15), currEntry.description.ljust (35), currEntry.value ) )
                        printEntries.monthEntryData.append ( ( "{}-{}-{}".format ( currEntry.year, currEntry.month, currEntry.day),
                                             currEntry.label, currEntry.description, currEntry.value ) )
                        # get values for each lable
                        labelsMonthlyValuesDict[currLabel] += currEntry.value

                        if currEntry.label == "spent;other":
                        
                            printEntries.rightOtherODescription.append ( [ currEntry.description, currEntry.value ])
            lastEntryDate = []
            for item in monthlyReport:
                lastEntryDate.append ( item.day )
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
                            
                            # first category is called _rulaj as lastLabel value will be _transferredTata
                            
                            if re.match ( "_", lastLabel ):
                                switchLabel = '_rulaj'
                                incomeValue = totalCurrentLabel
                            else:
                                switchLabel = lastLabel
                                printEntries.rightListLabels.append ( [ "---", 0 ] )
                                
                            printEntries.leftListSummary.append ( [switchLabel, totalCurrentLabel ] )
                            # do not add input from rulaj in month statistics
                            
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
                printEntries.leftListSummary = sorted(printEntries.leftListSummary, key=lambda x: x[1], reverse=False)
                printEntries.leftListSummary.insert ( -1, [ "---", 0 ] )
                #printEntries.leftListSummary.append ( printEntries.leftListSummary.pop(0))

                printEntries.leftListSummary.append ( ['_total_spent', sumOfAllLabels ] )
                printEntries.leftListSummary.append ( [ "---", 0 ] )
                printEntries.leftListSummary.append ( ['_remaining_{}-{}'.format(lastEntryDate[-1], currMonth) , remainingValue ] )
                #printEntries.printTerminal()
                generateReportHTML.addMonthEntry ( printEntries )
                generateReportHTML.addChartRow ( date ( currYear, currMonth, 5 ) , printEntries.leftListSummary )
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