from html import HTML
from includes.Entries import Entries
from main.EntryNew import EntryNew

from gpcharts import figure
from pprint import pprint
import os
import json


class WriteHtmlOutput:

    def __init__( self ):

        self.splitPeriodsEntries = {}
        self.buffer = ""

    def run(self ):

        self.loadEntriesCSV(os.path.join(os.environ['OneDrive'], "PythonData", "manualInput", "manual_described_operations_2015_2016_2017.csv"))
        if not os.path.exists('output'):
            os.mkdir("output")

        for year in self.splitPeriodsEntries:
            entriesForPeriod = self.splitPeriodsEntries[year]
            statistics = self.statistics(entriesForPeriod )
            self.overviewStatistics(entriesForPeriod, statistics )
            #self.writeGPchart(entriesForPeriod, statistics  )
            self.writeIndexHTML(entriesForPeriod )

    def loadEntriesCSV(self, inputFile):
        allEntries = []
        if os.path.isfile( inputFile):
            with open(inputFile , "r") as file:
                for row in file:
                    elements = row.split(";")

                    if len(elements ) == 1:
                        continue
                    if len(elements) == 6:
                        elements[5] = elements[5].rstrip()
                    elements[4] = elements[4].replace(",", ".")

                    #    0		  1			  2		3	      4		 5
                    # liquidation;September;2017;Decathlon;-286;echipamen
                    allEntries.append(EntryNew(elements[0], elements[1], elements[2], elements[3], elements[4], elements[5]) )

            if 0:
                print("%s | %s | %s | %s | %s | %s \n" %(elements[0], elements[1], elements[2], elements[3], elements[4], elements[5]))

        else:
            print("File '" + inputFile + "' was not found!\n")

        monthsFirstSemester  =  [ "August", "September", "October", "November", "December" ]
        monthsSecondSemester  = [  "January", "February", "March", "April", "May", "June", "July" ]

        years = []

        for entry in allEntries:
            # how many years are there
            if not(entry.year in years ):
                years.append(entry.year )
        for year in years:
            tmpArr = []
            for entry in allEntries:
                if entry.year == year and(entry.month in monthsFirstSemester ):
                    tmpArr.append(entry )
                elif entry.year ==(year + 1 ) and(entry.month in monthsSecondSemester ):
                    tmpArr.append(entry )
            self.splitPeriodsEntries[year] = tmpArr
        return allEntries

    def overviewStatistics(self, data, statistics):

        for currentPeriod in self.splitPeriodsEntries:

            index = 0
            totalSpentMonth = statistics['eachMonth']
            totalSpentCategory = statistics['eachCategory']
            htmlOutput = HTML()

            table = htmlOutput.table( style="width: 50%; padding-left: 20px" )

            monthsArr  = [  "August", "September", "October", "November",
                            "December", "January" , "February" , "March" ,
                            "April", "May" , "June" , "July" ]

            #for each defined period aug - july
            for currMonth in monthsArr:

                index += 1
                tdBefore = index
                tdAfter = 12 - index
                entries = data



                for period in ["liquidation", "advance" ]:
                    hasEntries = len(data )
                    headerRow = table.tr (style="border: none")
                    headerRow.td(currMonth, style="background-color: lightblue" )
                    headerRow.td(period, style="background-color: lightblue; text-align: center" )
                    headerRow = table.tr
                    secondRow = table.tr

                    for entryNew in data:
                        if currMonth == entryNew.month and period == entryNew.period:
                            thirdRow = table.tr
                            for time in range(tdBefore):
                                #thirdRow.td() #empty div before input
                                pass
                            thirdRow.td (entryNew.description)
                            thirdRow.td (entryNew.value + " lei", style="text-align: right")

                    for time in range( tdAfter ):
                        #headerRow.td() #empty div after input
                        pass
                    headerRow = table.tr ()
                    headerRow.td()
                    headerRow.td()
                finalRow = table.tr
                finalRow.td( "Total:" , style="text-align: right")
                finalRow.td(str(totalSpentMonth[currMonth] ) + " lei", style="background-color:lightgrey; text-align: right")
                finalRow = table.tr()
                finalRow.td()
                finalRow.td()

            outputFilePath = os.path.join("output", "%s_%s" % (data[0].year, data[0].year + 1)  + "_overview.html" )
            with open(outputFilePath, "w") as output:
                output.write(str(htmlOutput ) )

    def writeGPchart(self, data, statistics):
        totalSpentCategory = statistics['eachCategory']
        totalSpentMonth = statistics['eachMonth']

        monthsArr  = [ "August", "September", "October", "November",
                       "December", "January" , "February" , "March" ,
                       "April", "May" , "June" , "July" ]
        os.chdir ("output")

        fig = figure(title="%s_%s" % (data[0].year, data[0].year + 1) + '_labelsCharts', height=600, width=800)
        fig2 = figure(title="%s_%s" % (data[0].year, data[0].year + 1) + '_yearCharts', height=600, width=800)

        catData = ['Categories']
        valuesData = ['lei']
        for key, value in sorted(totalSpentCategory.iteritems(), key=lambda k, v: (v, k)):
            catData.append(key)
            valuesData.append(value * -1)

        fig.column(catData, valuesData)
        monthData = ['Months']
        valuesData = ['lei']

        for month in monthsArr:
            monthData.append(month)
            valuesData.append( totalSpentMonth[month] * -1 )

        fig2.column( monthData, valuesData )
        os.chdir ("..")

    def writeIndexHTML(self, data):
        with open(os.path.join("output", "index.html" ), "w" ) as f:
            f.write ("<html><body><h4>test</h4></body></html>")

    def statistics(self, data):
        statistics = {}
        statistics['eachMonth'] = {}
        statistics['eachCategory'] = {}

        monthsArr  = [ "August", "September", "October", "November",
                        "December", "January" , "February" , "March" ,
                        "April", "May" , "June" , "July" ]

        for month in monthsArr:
            statistics['eachMonth'][month] = 0

        for entry in data:
            statistics['eachCategory'][entry.label] = 0

        for entry in data:
            statistics['eachMonth'][entry.month] += float(entry.value)
            statistics['eachCategory'][entry.label] += float(entry.value)

        return statistics


class EntriesCollection:
    ''' Google table generation from collected entries data '''

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
        with open(os.path.join(os.environ['OneDrive'], "PythonData", "config", "definedLabels.json")) as f:
            tmp = json.load(f)
        return tmp['rentValue']

    def addChartRow(self, date, labelsArr ):
        dividerLineValue = 6000

        # labelsArr: [ [ labelName, value ], [ labelName, value ], [ labelName, value ], [ labelName, value ] ]
        monthConversion = " new Date(\"{}-{:02d}-{:02d}\" )".format(date.year, date.month, date.day)

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
        defLabels = ('cash', 'spent', 'bills', 'transport', 'food', 'leisure', 'travel')
        soldPrecendent = 0
        for elem in self.entries:
            for pair in elem.rightListLabels:
                if '_soldPrecendent' == pair[0]:
                    soldPrecendent = (int(pair[1]))
                    print("Found soldPrecendent '{}'".format(soldPrecendent))
        for seekedLabel in defLabels:
            # ['_rulaj', -100]
            for pair in labelsArr:
                if seekedLabel == pair[0]:
                    valuesArr.append ("{: <8}".format(int(pair[1] * -1)))
                    valuesTotal += int(pair[1] * -1)
                    control += 1

        incomeValue = 0

        for pair in labelsArr:
            if '_rulaj'  == pair[0]:
                incomeValue = "{: <8}".format(int(pair[1]))

        valuesToStr = ""
        if control == len (defLabels):
            #  [ new Date(2018, 8, 3 )

            rentValue = 0

            #  [  new Date("2018-09-05" ),  6000  , 1100    , 286     , 0       , 244     , 225     , 0       , 0        ] ,
            self.chartData.append("\t\t\t\t[ {},  {: <6}, {: <6} ] ".format(monthConversion, dividerLineValue, ", ".join(valuesArr)))

            self.chartDataBills.append("\t\t\t\t[ {},  {: <6}, {: <6},  {: <6},  {: <6} ] ".format(monthConversion, dividerLineValue, self.rentValue, valuesArr[2], valuesArr[4]))
            #  [  new Date("2018-09-05" ),  6000  , 1855  , 6001     ] , 2
            self.chartDataTotals.append("\t\t\t\t[ {},  {: <6}, {: <6}, {: <6}, {: <6} ] ".format(monthConversion, dividerLineValue, valuesTotal, incomeValue , soldPrecendent))

        else:
            logging.warn("EntriesCollection::addChartRow: Error! Expected '{}' labels! \n\n Value of labelsArr is: {}".format(len(defLabels), labelsArr))

    def addMonthEntry(self, month):
        self.navigationHeaders.append(month.header)
        self.entries.append(month)

    def chartDataToString(self, chartData):
        tmp = ""
        chartDataCpy = chartData

        while (len(chartDataCpy) > 0):

            tmp += chartDataCpy.pop()
            if len(chartDataCpy) > 0:
                tmp += ", \n"

        return tmp

    def processData(self):
        head = '''<html>
                    <head>  <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
                    <script src="chart.js"></script>
                  <link rel="stylesheet" type="text/css" href="main.css" /></head><body>''' # will not be needed
        tail = '</body></html>'

        self.htmlData.append(head)
        self.htmlData.append("<h3>Yearly graphics</h3>")
        self.htmlData.append("<div id='chart_wrapper'><div id='chart_div'></div></div>")
        self.htmlData.append("<div id='chart_wrapper'><div id='chart_div2'></div></div>")
        self.htmlData.append("<div id='chart_wrapper'><div id='chart_div3'></div></div>")

        for entry in self.entries:
            # month div
            self.htmlData.append("<div class=\"{}.{}\">".format(entry.header[0], entry.header[1]))
            self.htmlData.append("<h3>Statistics for {}.{} -> Period segment from {} to {} </h3>".format(entry.header[0], entry.header[1], entry.subHeader[0], entry.subHeader[1]))

            # statistics
            self.htmlData.append("<div class=\"{0}\"><table><th colspan=\"2\">{0}</th>".format("statistics"))
            for row in entry.leftListSummary:
                self.htmlData.append("<tr><td>{}</td><td>{}</td></tr>".format(row[0], "%.2f" % round(row[1], 2) if row[1] != 0 else ""))

            self.htmlData.append("</table></div>")

            # label categories
            self.htmlData.append( "<div class=\"{0}\"><table><th colspan=\"2\">{0}</th>".format("labelCategories" ))
            for row in entry.rightListLabels:
                self.htmlData.append("<tr><td>{}</td><td>{}</td></tr>".format(row[0], "%.2f" % round(row[1] ,2) if row[1] != 0 else ""))

            self.htmlData.append("</table></div>")

            isEverythingElse = []
            isFood = []
            isTransport = []
            isBill = []
            for row in entry.monthEntryData:
                if "bills" in row[1]:
                    isBill.append(row)
                elif "food" in row[1]:
                    isFood.append(row)
                elif "transport" in row[1]:
                    isTransport.append(row)
                else:
                    isEverythingElse.append(row)

            # bills and spendings

            self.htmlData.append("<div class=\"{0}\"><table><th colspan=\"4\">{1}</th>".format("billsAndOtherDetail", "otherDetail" ))

            totals = 0
            rulaj = 0
            for row in isEverythingElse:
                self.htmlData.append("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(row[0], row[1], row [2].title(), "%.2f" % round(row[3], 2)))
                if row[3] <= 0:
                    totals += row[3]
                else:
                    rulaj += row[3]
            self.htmlData.append("<tr class='totals'><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format("", "", "Total spent", "%.2f" % round(totals, 2)))
            self.htmlData.append("<tr class='totals'><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format("", "", "Income", "%.2f" % round(rulaj, 2)))

            totals = 0

            self.htmlData.append("</table><table style=\"margin-top: 20px;\"><th colspan=\"4\">{0}</th>".format("bills"))

            for row in isBill:
                self.htmlData.append("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(row[0], row[1], row [2].title(), "%.2f" % round(row[3], 2)))
                totals +=  row[3]
            self.htmlData.append("<tr class='totals'><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format("", "", "Total", "%.2f" % round( totals, 2)))

            self.htmlData.append("</table></div>")

            # food and transport detail


            self.htmlData.append("<div class=\"{0}\"><table><th colspan=\"4\">{1}</th>".format("foodAndTransportDetail", "transportDetail"))

            totals = 0
            for row in isTransport:
                self.htmlData.append("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(row[0], row[1], row [2].title(), "%.2f" % round(row[3], 2)))
                totals += row[3]
            self.htmlData.append("<tr class='totals'><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format( "", "", "Total", "%.2f" % round( totals, 2)))

            self.htmlData.append("</table><table style=\"margin-top: 20px;\"><th colspan=\"4\">{0}</th>".format("foodDetail"))
            totals = 0
            for row in isFood:
                self.htmlData.append("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(row[0], row[1], row [2].title(), "%.2f" % round(row[3], 2)))
                totals += row[3]

            self.htmlData.append("<tr class='totals'><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format("", "", "Total", "%.2f" % round(totals, 2)))
            totals = 0

            self.htmlData.append("</table></div>")

            self.htmlData.append("</div>")

        self.htmlData.append(tail)

    def writeHtmlReport(self):
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

        with open("main.css", "w") as f:
            f.write(cssContents)

        with open("chart.js", "w" ) as f:
            f.write(chartJS)

        with open("reportLatest.html", "w") as f:
            f.write("\n".join(self.htmlData))