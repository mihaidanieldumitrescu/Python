from main.EntryNew import EntryNew as EntryNew

from main.RaiffaisenStatement import Statement
from json_config.JsonConfig import JsonConfig

import datetime
import glob
import os
import sys
import re
import pprint

class Entries:

    def __init__(self, input_file):
        self.current_year_list = []

        self.manual_entries = []
        self.csv_values = ""

        self.verbosity = "none"
        self.json_config = JsonConfig()


    def get_entries(self):
        return self.current_year_list
    def get_labels(self):
        """ Returns label array
        :return: Array of unique labels from self.current_year_list
        """
        labels = set()

        for item in self.current_year_list:
            labels.add(item.label)

        return sorted(list(labels))

    def return_month_data(self, year, month):
        """ Returns data entries from first day of the month to the last

        :param year:
        :param month:
        :return:
        """

        data = []
        for item in self.current_year_list:
            if item.year == year and item.month == month:
                data.append(item)
        return data

    def return_month_segment_data(self, beginning_period_date, end_period_date):
        """ This contains data from salary payment to the next salary

        :param beginning_period_date:
        :param end_period_date:
        :return:
        """

        data = []
        for item in self.current_year_list:
            if beginning_period_date <= item.date_log < end_period_date:
                data.append(item)
        return data

    def return_salary_payment_dates(self):
        data = []
        liquidation_dates = [datetime.date(2000, 1, 1)]  # dummy date

        for item in self.current_year_list:
            if item.label == '_salary' and \
               item.period == 'liquidation':
                data.append(item)

        for element in data:
            liquidation_dates.append(element.date_log)
        liquidation_dates.append(datetime.date(2040, 1, 1))  # dummy date
        return liquidation_dates

    def __str__(self):
        return "Entries.__str__ Undefined!"

    def new_entry(self, entry):
        """ Add a new EntryNew object """
        self.current_year_list.append(entry)
        self.current_year_list.sort(key=lambda x: x.date_log)

    def extract_data_excel_sheets(self):
        """ Load data from excel statement files """

        files = glob.glob(os.path.join(os.environ['OneDrive'], "PythonData", "extrasDeCont", "*xls*"))

        self.json_config.load_file()

        if len(files) == 0:
            raise Exception("No files found in folder \n")

        excel_statement_files = sorted(files, key=lambda x: str(re.findall(r'\d{4}\.xlsx?$', x)))

        for filename in excel_statement_files:

            statement = Statement()
            self.current_year_list.extend(statement.load_statement(filename))
            self.current_year_list

        print(f"\nDone loading statement data ... Found {len(self.current_year_list)} entries!\n\n")



    def write_csv_data(self):
        """ Writes CSV report """

        with open("report.csv", "w") as f:
            f.write(self.csv_values)
