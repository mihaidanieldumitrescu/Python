import re
import pprint
import logging

from mySQL_interface.GenerateSQLfile import GenerateSQLfile
from includes.Entries import Entries
from includes.WriteHtmlOutput import EntriesCollection
from datetime import date


class PrintEntries:

    def __init__(self):

        # this object contains only one month
        # values should be passed as an array
        # e.g. [ ['spent', 1000 ], [ 'food', 700 ] ]

        self.header = None # YEAR-MONTH
        self.subHeader = None
        self.leftListSummary = [] # [( bills, 700 ),( food, 1000 ) ]
        self.rightListLabels = [] # (spent;cash ATM, 100 )
        self.rightOtherODescription = [] #(HERVIG, 380 )
        self.monthEntryData = [] # (date , label, description, value )

    def __repr__(self):
        string = "PrintEntries element for '{}'".format(self.header)

        return string

    def print_to_terminal(self):

        column_size = 50
        month_statistics = []
        print(f"{self.header[0]}, {self.header[1]}, {self.header[2]}")
        print('-' * 10 + "\n")

        # merge and print(labels from liquidation and advance for current month)
        index = 0
        for item in self.rightListLabels:
            pop_elem = self.leftListSummary[index] if(len(self.leftListSummary) > index) else []

            if pop_elem and pop_elem[0] == "---":
                left_element = pop_elem[0].ljust(50)
            else:
                left_element = "{}   {} lei  ".format(pop_elem[0].ljust(31), str("%.2f" % pop_elem[1]).rjust(10)) if pop_elem else "".ljust(column_size)

            if item and item[0] == "---":
                right_element = item[0].ljust(27)
            else:
                right_element = "{} => {}".format(item[0].ljust(20), str("%.2f" % item[1]).rjust(10)) if item else ""

            month_statistics.append("{} | {} ".format(left_element, right_element ) )
            index += 1
        month_statistics.append("{}   {} ".format("".ljust(column_size), "---------------".ljust(20)))
        # second part
        # merge other operations from liquidation and advance for current month
        self.rightOtherODescription

        for str_other_op in sorted(self.rightOtherODescription, key=lambda x: x[1], reverse=False):
            left_element = "".ljust(column_size)
            pop_elem = str_other_op
            right_element = "{} => {}".format(pop_elem[0].ljust(40), str("%.2f" % pop_elem[1]).rjust(10)) if pop_elem else ""

            month_statistics.append("%s | %s " % (left_element, right_element))

        if month_statistics :
                print("\n".join(month_statistics ))
                print()


class Operations:

    def __init__(self, verbosity="none"):
        self.entries = Entries('')
        # self.entries.loadDebugValues()
        self.errorString = ""
        self.totalSpentMonth = {}
        self.verbosity = verbosity
        self.htmlFrame = {}
        self.sql_file = GenerateSQLfile()

        logging.basicConfig(filename='logfile_operations.log',filemode='w', level=logging.DEBUG)
        if 0:
            self.entries.printStatistics()
            self.entries.write_html_report()
            self.entries.write_csv_data()
        self.parse_entries()

    def parse_entries(self):

        # for each month in ascending order
        key_labels = self.entries.get_labels()
        generate_report_html = EntriesCollection()

        for monthly_report in self.entries:
            if not monthly_report:
                continue
            curr_year = monthly_report[0].year
            curr_month = monthly_report[0].month

            logging.info("CHANGED DATE TO: {}-{}".format(curr_year, curr_month))
            print_entries = PrintEntries()
            print_entries.subHeader = [monthly_report[0].datelog, monthly_report[-1].datelog]
            month_statistics = ""
            tmp_statistics = ""
            liquidation_statistics = []
            advance_statistics = []
            sum_of_all_labels = 0
            sum_of_all_labels_by_label = {}

            # first initialisation
            for label in key_labels:
                key = label.split(';')[0]
                if not re.match ("_", key):
                    sum_of_all_labels_by_label[key] = 0

            # for advance and liquidation

            labels_monthly_values_dict = {}
            curr_period = ''
            other_operations = curr_period + " entries: \n\n"
            label_summary = []
            entry_data = []

            for currLabel in key_labels:
                labels_monthly_values_dict[currLabel] = 0

            # match values, print(others)
            for currLabel in key_labels:
                for currEntry in monthly_report:
                    if currEntry.label == currLabel:

                        self.sql_file.add_entry(currEntry)

                        # print("<...> ;{};{};{}-{}-{};{};;".format(currEntry.label.replace(";","."),
                        # currEntry.description, currEntry.year, currEntry.month, currEntry.day, currEntry.value ))
                        logging.info("ENTRY: {}-{} | Record {}-{}-{} | {} | {} | {}".format(curr_year, curr_month, currEntry.year, currEntry.month, currEntry.day,
                                                                                                currEntry.label.ljust (15), currEntry.description.ljust (35), currEntry.value ) )
                        print_entries.monthEntryData.append(( "{}-{}-{}".format(currEntry.year, currEntry.month, currEntry.day),
                                             currEntry.label, currEntry.description, currEntry.value ) )
                        # get values for each lable
                        labels_monthly_values_dict[currLabel] += currEntry.value

                        if currEntry.label == "spent;other":

                            print_entries.rightOtherODescription.append([ currEntry.description, currEntry.value ])
            last_entry_date = []
            for item in monthly_report:
                last_entry_date.append(item.day )
            last_entry_date.sort()

            # we finished gathering data, now we use the data
            # check for months that have no data
            has_data = 0

            for label in sorted(labels_monthly_values_dict):

                # bills;internet       => -109.59 lei
                # at least one label has value

                if labels_monthly_values_dict[label] != 0:
                    has_data = 1

            if has_data:

                income_value = 0

                # headers for each month
                # 2017, 8, liquidation
                # ----------

                print_entries.header = (curr_year, curr_month, curr_period);
                last_label = ""
                total_current_label = 0

                # { 'spent;food' : 300 }
                for label in sorted(labels_monthly_values_dict):

                    curr_label_category = label if re.match("_", label) else label.split(";")[0]
                    switch_label = ''

                    if last_label != curr_label_category and last_label != "":
                        # if 'bills != food', when you get to the next category

                        if not(re.match("_", last_label) and re.match("_", curr_label_category)):
                            # _salary category

                            if re.match("_", last_label):
                                print_entries.rightListLabels.append(["---", 0])

                            # first category is called _rulaj as last_label value will be _transferredTata

                            if re.match("_", last_label):
                                switch_label = '_rulaj'
                                income_value = total_current_label
                            else:
                                switch_label = last_label
                                print_entries.rightListLabels.append(["---", 0])

                            print_entries.leftListSummary.append([switch_label, total_current_label])
                            # do not add input from rulaj in month statistics

                            if not re.match ("_", last_label):
                                sum_of_all_labels += total_current_label
                                sum_of_all_labels_by_label[last_label] += total_current_label
                            total_current_label = 0

                        else:
                            pass # print("Exception in lastlabel '{}' !".format(last_label ))

                    # for each label add to month
                    total_current_label += labels_monthly_values_dict[label]

                    if labels_monthly_values_dict[label] != 0:
                        print_entries.rightListLabels.append([label, labels_monthly_values_dict[label]])
                    else:
                        print_entries.rightListLabels.append([label, 0])

                    last_label = label if re.match("_", label) else label.split(";")[0]

                # for the last label (no more labels to compare)

                sum_of_all_labels += total_current_label
                sum_of_all_labels_by_label[last_label] += total_current_label

                print_entries.leftListSummary. append([last_label, total_current_label])

                remaining_value = income_value + sum_of_all_labels
                print_entries.leftListSummary = sorted(print_entries.leftListSummary, key=lambda x: x[1], reverse=False)
                print_entries.leftListSummary.insert(-1, ["---", 0])
                # print_entries.leftListSummary.append(print_entries.leftListSummary.pop(0))

                print_entries.leftListSummary.append(['_total_spent', sum_of_all_labels])
                print_entries.leftListSummary.append(["---", 0])
                print_entries.leftListSummary.append(['_remaining_{}-{}'.format(last_entry_date[-1], curr_month), remaining_value])
                # print_entries.printTerminal()
                generate_report_html.add_month_entry(print_entries)
                print(type(curr_year), type(curr_month))
                exit()
                generate_report_html.add_chart_row(date(curr_year, curr_month, 5), print_entries.leftListSummary)
            if 0:
                print("len values: %s %s \n" % (len(bufferMonth['leftOtherOp']), len(self.rightOtherODescription)))
                print(pprint.pformat(bufferMonth['leftOtherOp']))
                print(pprint.pformat(self.rightOtherODescription))
                print("\n")

            print("SQL file contents\n\n")
            print(str(self.sql_file))
            print()

            if sum_of_all_labels != 0:

                for label in sorted(sum_of_all_labels_by_label):
                    pass
                    # self.csvValues += "{};{};{};{}\n".format(curr_year,curr_month,label, sum_of_all_labels_by_label[label] )

        generate_report_html.process_data()
        generate_report_html.write_html_report()
