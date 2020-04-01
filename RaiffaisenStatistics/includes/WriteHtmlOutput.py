from includes.Entries import Entries
from main.EntryNew import EntryNew
import xml.dom.minidom

from gpcharts import figure
from pprint import pprint
import os
import json


class WriteHtmlOutput:

    def __init__(self):

        self.splitPeriodsEntries = {}
        self.buffer = ""

    def run(self ):

        self.load_entries_csv(os.path.join(os.environ['OneDrive'], "PythonData", "manualInput", "manual_described_operations_2015_2016_2017.csv"))
        if not os.path.exists('output'):
            os.mkdir("output")

        for year in self.splitPeriodsEntries:
            entries_for_period = self.splitPeriodsEntries[year]
            statistics = self.statistics(entries_for_period)
            self.overview_statistics(entries_for_period, statistics)
            # self.writeGPchart(entries_for_period, statistics_dict  )
            self.write_index_html(entries_for_period)

    def load_entries_csv(self, input_file):
        all_entries = []
        if os.path.isfile(input_file):
            with open(input_file, "r") as file:
                for row in file:
                    elements = row.split(";")

                    if len(elements ) == 1:
                        continue
                    if len(elements) == 6:
                        elements[5] = elements[5].rstrip()
                    elements[4] = elements[4].replace(",", ".")

                    #    0		  1			  2		3	      4		 5
                    # liquidation;September;2017;Decathlon;-286;echipamen
                    all_entries.append(EntryNew(elements[0], elements[1], elements[2], elements[3], elements[4], elements[5]))

            if 0:
                print("%s | %s | %s | %s | %s | %s \n" % (elements[0], elements[1], elements[2], elements[3], elements[4], elements[5]))

        else:
            print("File '" + input_file + "' was not found!\n")

        months_first_semester = ["August", "September", "October", "November", "December"]
        months_second_semester = ["January", "February", "March", "April", "May", "June", "July"]

        years = []

        for entry in all_entries:
            # how many years are there
            if not(entry.year in years):
                years.append(entry.year)
        for year in years:
            tmp_arr = []
            for entry in all_entries:
                if entry.year == year and (entry.month in months_first_semester):
                    tmp_arr.append(entry)
                elif entry.year == (year + 1) and (entry.month in months_second_semester):
                    tmp_arr.append(entry)
            self.splitPeriodsEntries[year] = tmp_arr
        return all_entries

    def overview_statistics(self, data, statistics):

        for current_period in self.splitPeriodsEntries:

            index = 0
            total_spent_month = statistics['eachMonth']
            total_spent_category = statistics['eachCategory']
            html_output = HTML()

            table = html_output.table(style="width: 50%; padding-left: 20px")

            months_arr = ["August", "September", "October", "November", "December", "January", "February", "March",
                            "April", "May", "June", "July"]

            # for each defined period aug - july
            for curr_month in months_arr:

                index += 1
                td_before = index
                td_after = 12 - index
                entries = data

                for period in ["liquidation", "advance" ]:
                    has_entries = len(data )
                    header_row = table.tr (style="border: none")
                    header_row.td(curr_month, style="background-color: lightblue" )
                    header_row.td(period, style="background-color: lightblue; text-align: center" )
                    header_row = table.tr
                    second_row = table.tr

                    for entryNew in data:
                        if curr_month == entryNew.month and period == entryNew.period:
                            third_row = table.tr
                            for time in range(td_before):
                                # third_row.td() #empty div before input
                                pass
                            third_row.td (entryNew.description)
                            third_row.td (entryNew.value + " lei", style="text-align: right")

                    for time in range( td_after ):
                        #header_row.td() #empty div after input
                        pass
                    header_row = table.tr ()
                    header_row.td()
                    header_row.td()
                final_row = table.tr
                final_row.td( "Total:" , style="text-align: right")
                final_row.td(str(total_spent_month[curr_month]) + " lei", style="background-color:lightgrey; text-align: right")
                final_row = table.tr()
                final_row.td()
                final_row.td()

            output_file_path = os.path.join("output", "%s_%s" % (data[0].year, data[0].year + 1) + "_overview.html")
            with open(output_file_path, "w") as output:
                output.write(str(html_output))

    def write_gpchart(self, data, statistics):
        total_spent_category = statistics['eachCategory']
        total_spent_month = statistics['eachMonth']

        months_arr = ["August", "September", "October", "November",
                       "December", "January", "February", "March",
                       "April", "May", "June", "July"]
        os.chdir("output")

        fig = figure(title="%s_%s" % (data[0].year, data[0].year + 1) + '_labelsCharts', height=600, width=800)
        fig2 = figure(title="%s_%s" % (data[0].year, data[0].year + 1) + '_yearCharts', height=600, width=800)

        cat_data = ['Categories']
        values_data = ['lei']
        for key, value in sorted(total_spent_category.iteritems(), key=lambda k, v: (v, k)):
            cat_data.append(key)
            values_data.append(value * -1)

        fig.column(cat_data, values_data)
        month_data = ['Months']
        values_data = ['lei']

        for month in months_arr:
            month_data.append(month)
            values_data.append(total_spent_month[month] * -1)

        fig2.column(month_data, values_data)
        os.chdir("..")

    def write_index_html(self, data):
        with open(os.path.join("output", "index.html"), "w") as f:
            f.write ("<html><body><h4>test</h4></body></html>")

    def statistics(self, data):
        statistics = {}
        statistics['eachMonth'] = {}
        statistics['eachCategory'] = {}

        months_arr = [ "August", "September", "October", "November",
                        "December", "January", "February", "March",
                        "April", "May", "June", "July"]

        for month in months_arr:
            statistics['eachMonth'][month] = 0

        for entry in data:
            statistics['eachCategory'][entry.label] = 0

        for entry in data:
            statistics['eachMonth'][entry.month] += float(entry.value)
            statistics['eachCategory'][entry.label] += float(entry.value)

        return statistics


class EntriesCollection:
    ''' Google table generation from collected entries data '''

    def __init__(self):
        self.entries = []
        self.htmlData = []
        self.navigationHeaders = []
        self.chartData = []
        self.chartDataBills = []
        self.chartDataTotals = []
        self.rentValue = self.load_rent_value()

    def load_rent_value (self):
        with open(os.path.join(os.environ['OneDrive'], "PythonData", "config", "definedLabels.json")) as f:
            tmp = json.load(f)
        return tmp['rent']

    def add_chart_row(self, date, labels_arr):
        divider_line_value = 6000

        # labelsArr: [ [ labelName, value ], [ labelName, value ], [ labelName, value ], [ labelName, value ] ]
        month_conversion = " new Date(\"{}-{:02d}-{:02d}\" )".format(date.year, date.month, date.day)

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
        values_arr = []
        values_total = 0
        def_labels = ('cash', 'spent', 'bills', 'transport', 'food', 'leisure', 'travel')
        sold_precendent = 0
        for elem in self.entries:
            for pair in elem.rightListLabels:
                if '_soldPrecendent' == pair[0]:
                    sold_precendent = (int(pair[1]))
        for seekedLabel in def_labels:
            # ['_rulaj', -100]
            for pair in labels_arr:
                if seekedLabel == pair[0]:
                    values_arr.append ("{: <8}".format(int(pair[1] * -1)))
                    values_total += int(pair[1] * -1)
                    control += 1

        income_value = 0

        for pair in labels_arr:
            if '_rulaj' == pair[0]:
                income_value = "{: <8}".format(int(pair[1]))

        values_to_str = ""
        if control == len (def_labels):
            #  [ new Date(2018, 8, 3 )

            rent_value = 0

            #  [  new Date("2018-09-05" ),  6000  , 1100    , 286     , 0       , 244     , 225     , 0       , 0   ] ,
            self.chartData.append("\t\t\t\t[ {},  {: <6}, {: <6} ] ".format(month_conversion, divider_line_value, ", ".join(values_arr)))

            self.chartDataBills.append("\t\t\t\t[ {},  {: <6}, {: <6},  {: <6},  {: <6} ] ".format(month_conversion, divider_line_value, self.rentValue, values_arr[2], values_arr[4]))
            #  [  new Date("2018-09-05" ),  6000  , 1855  , 6001     ] , 2
            self.chartDataTotals.append("\t\t\t\t[ {},  {: <6}, {: <6}, {: <6}, {: <6} ] ".format(month_conversion, divider_line_value, values_total, income_value, sold_precendent))

        else:
            logging.warn("EntriesCollection::addChartRow: Error! Expected '{}' labels! \n\n Value of labelsArr is: {}".format(len(def_labels), labels_arr))

    def add_month_entry(self, month):
        self.navigationHeaders.append(month.header)
        self.entries.append(month)

    def chart_data_to_string(self, chartData):
        tmp = ""
        chart_data_cpy = chartData

        while len(chart_data_cpy) > 0:

            tmp += chart_data_cpy.pop()
            if len(chart_data_cpy) > 0:
                tmp += ", \n"

        return tmp

    def process_data(self):
        head = """       
    <!doctype html>
        <html lang="en">
            <head>  
                <!-- Required meta tags -->
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
            
                <!-- Bootstrap CSS -->
                <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
    
                <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
                <script src="chart.js"></script>
                <link rel="stylesheet" type="text/css" href="main.css" />
            </head>
            <body>
        """

        tail = """
            <!-- Optional JavaScript -->
            <!-- jQuery first, then Popper.js, then Bootstrap JS -->
            <script src="https://code.jquery.com/jquery-3.4.1.slim.min.js" integrity="sha384-J6qa4849blE2+poT4WnyKhv5vZF5SrPo0iEjwBvKU7imGFAV0wwj1yYfoRSJoZ+n" crossorigin="anonymous"></script>
            <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo" crossorigin="anonymous"></script>
            <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js" integrity="sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6" crossorigin="anonymous"></script>
          </body>
        </html>
        """

        self.htmlData.append(head)
        no_graphs = True

        if no_graphs:
            pass
        else:
            self.htmlData.append("""
         <h3>Yearly graphics</h3>       
         <div id='chart_wrapper'>
            <div id='chart_div'></div>
        </div>    
         <div id='chart_wrapper'>
            <div id='chart_div2'></div>
        </div>
         <div id='chart_wrapper'>
            <div id='chart_div3'></div>
        </div>
            """)

        for entry in self.entries:
            # month div
            self.htmlData.append("<div class=\"{}.{}\">".format(entry.header[0], entry.header[1]))
            self.htmlData.append("<h3>Statistics for {}.{} -> Period segment from {} to {} </h3>".format(entry.header[0], entry.header[1], entry.subHeader[0], entry.subHeader[1]))

            # statistics_dict
            self.htmlData.append("<div class=\"{0}\"><table><th colspan=\"2\">{0}</th>".format("statistics_dict"))
            for row in entry.leftListSummary:
                self.htmlData.append("<tr><td>{}</td><td>{}</td></tr>".format(row[0], "%.2f" % round(row[1], 2) if row[1] != 0 else ""))

            self.htmlData.append("</table></div>")

            # label categories
            self.htmlData.append( "<div class=\"{0}\"><table><th colspan=\"2\">{0}</th>".format("labelCategories" ))
            for row in entry.rightListLabels:
                self.htmlData.append("<tr><td>{}</td><td>{}</td></tr>".format(row[0], "%.2f" % round(row[1], 2) if row[1] != 0 else ""))

            self.htmlData.append("</table></div>")

            is_everything_else = []
            is_food = []
            is_transport = []
            is_bill = []
            for row in entry.monthEntryData:
                if "bills" in row[1]:
                    is_bill.append(row)
                elif "food" in row[1]:
                    is_food.append(row)
                elif "transport" in row[1]:
                    is_transport.append(row)
                else:
                    is_everything_else.append(row)

            # bills and spendings

            self.htmlData.append("<div class=\"{0}\"><table><th colspan=\"4\">{1}</th>".format("billsAndOtherDetail", "otherDetail" ))

            totals = 0
            rulaj = 0
            for row in is_everything_else:
                self.htmlData.append("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(row[0], row[1], row [2].title(), "%.2f" % round(row[3], 2)))
                if row[3] <= 0:
                    totals += row[3]
                else:
                    rulaj += row[3]
            self.htmlData.append("<tr class='totals'><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format("", "", "Total spent", "%.2f" % round(totals, 2)))
            self.htmlData.append("<tr class='totals'><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format("", "", "Income", "%.2f" % round(rulaj, 2)))

            totals = 0

            self.htmlData.append("</table><table style=\"margin-top: 20px;\"><th colspan=\"4\">{0}</th>".format("bills"))

            for row in is_bill:
                self.htmlData.append("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(row[0], row[1], row [2].title(), "%.2f" % round(row[3], 2)))
                totals += row[3]
            self.htmlData.append("<tr class='totals'><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format("", "", "Total", "%.2f" % round( totals, 2)))

            self.htmlData.append("</table></div>")

            # food and transport detail

            self.htmlData.append("<div class=\"{0}\"><table><th colspan=\"4\">{1}</th>".format("foodAndTransportDetail", "transportDetail"))

            totals = 0
            for row in is_transport:
                self.htmlData.append("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(row[0], row[1], row [2].title(), "%.2f" % round(row[3], 2)))
                totals += row[3]
            self.htmlData.append("<tr class='totals'><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format( "", "", "Total", "%.2f" % round( totals, 2)))

            self.htmlData.append("</table><table style=\"margin-top: 20px;\"><th colspan=\"4\">{0}</th>".format("foodDetail"))
            totals = 0
            for row in is_food:
                self.htmlData.append("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(row[0], row[1], row [2].title(), "%.2f" % round(row[3], 2)))
                totals += row[3]

            self.htmlData.append("<tr class='totals'><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format("", "", "Total", "%.2f" % round(totals, 2)))
            self.htmlData.append("</table></div>")
            self.htmlData.append("</div>")

        self.htmlData.append(tail)

    def write_html_report(self):
        css_contents = '''
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

            .statistics_dict, .labelCategories, .otherLabelDetail, .otherDetail, .billsAndOtherDetail, .foodAndTransportDetail {
                vertical-align:top;
                margin-top: 50px;
                display: inline-block;
                margin-right: 20px
            }

            .statistics_dict  { 	margin-left: 20px;
            }
            .statistics_dict td:nth-child(2), .labelCategories  td:nth-child(2) {
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

        chart_js = '''
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

            var dataArr = [ \n\n''' + self.chart_data_to_string(self.chartData) + ''' \n\t\t\t];
            var dataArr3= [ \n\n''' + self.chart_data_to_string(self.chartDataBills) + ''' \n\t\t\t];
            var dataArr2 = [ \n\n''' + self.chart_data_to_string(self.chartDataTotals) + ''' \n\t\t\t];

        '''

        with open("main.css", "w") as f:
            f.write(css_contents)

        with open("chart.js", "w" ) as f:
            f.write(chart_js)

        with open("reportLatest.html", "w") as f:
            f.write("\n".join(self.htmlData))
