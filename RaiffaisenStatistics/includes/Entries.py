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

    def __iter__(self):

        self.paymentLiquidationDatesArr = self.return_salary_payment_dates()
        self.index = len(self.paymentLiquidationDatesArr) - 1

        if len(self.paymentLiquidationDatesArr) < 2:
            print("( Entries::__iter__ ) Error! paymentLiquidationDatesArr has less than two elements!", file=sys.stderr)
            sys.exit(1)

        # print("__iter__ initialized with paymentLiquidationDatesArr: \n{}\n\n".format(self.paymentLiquidationDatesArr), file=sys.stderr)

        return self

    def __next__(self):

        #  this will iterate for each month
        if self.index > 0:

            begining_period_date = self.paymentLiquidationDatesArr[self.index - 1]
            end_period_date = self.paymentLiquidationDatesArr[self.index]

            # print("__next__ '{}' -> '{}'".format(begining_period_date, end_period_date - datetime.timedelta(days=1)))
            data = self.return_month_segment_data(begining_period_date, end_period_date)

            self.index -= 1
            return data
        else:
            print
            print("Iteration reached it's end. Last begin value is {}".format(
                self.paymentLiquidationDatesArr[self.index + 1]))
            raise StopIteration

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
            statement.load_statement(filename)

            # for entry in operations

            # For each statement entry in excel file
            for statement_entry in statement.operations:
                (day, month, year) = statement_entry['Data utilizarii cardului'].split("/")
                op_description = statement_entry['Descrierea tranzactiei'].split("|")[0]
                if re.match("OPIB", statement_entry['Descrierea tranzactiei']):
                    op_description = statement_entry['Descrierea tranzactiei'].split("|")[1]
                debit_value = statement_entry['Suma debit']
                credit_value = statement_entry['Suma credit']
                label_str = self.label_me(op_description)

                data = ("  Data: %s Operatie: %s Eticheta: %s\n " +
                        "  Valoare debit: %s Valoare credit: %s\n") % (
                       statement_entry['Data utilizarii cardului'], op_description, self.label_me(op_description),
                       debit_value, credit_value)

                if debit_value:
                    self.new_entry(
                        EntryNew(day=day,
                                 month=month,
                                 year=year,
                                 description=op_description,
                                 value=-debit_value,
                                 label=label_str,
                                 account=statement.accountName,
                                 statement_type=statement.statementType))
                elif credit_value:

                    # Salariu lunar
                    if re.search(self.json_config.salaryIdentifier, statement_entry['Nume/Denumire ordonator/beneficiar'],
                                 re.IGNORECASE):
                        label = "_salary"

                        # Perioada advance or liquidation
                        if 1 <= int(day) <= 15:
                            period = "liquidation"
                        else:
                            period = "advance"

                    else:
                        label = "_transferredInto"

                    self.new_entry(EntryNew(day=day,
                                            month=month,
                                            year=year,
                                            period=period,
                                            description=op_description,
                                            value=credit_value,
                                            label=label,
                                            account=statement.accountName,
                                            statement_type=statement.statementType))
                else:
                    pass
                    # print(f"(obs: _transfer_mastercard|visa) Warn: No debit or credit values! \n\t* Row is: {pprint.pformat(statement_entry)}\n\n")
        print(f"\nDone loading statement data ... Found {len(self.current_year_list)} entries!\n\n")

    def label_me(self, description):

        """ Selects the correct label from json config file

        :param description: Operation description that contains service name
        :return: label name
        """

        master_labels = self.json_config.labels

        # {    "leisure" :  {
        #           "film": [ "cinema", "avatar media project" ] }
        # ...

        for masterLabel in master_labels:
            for childLabel in master_labels[masterLabel]:
                if re.search(r"|".join(master_labels[masterLabel][childLabel]), description, re.I):
                    return f"{masterLabel}.{childLabel}"
        return "spent.other"

    def write_csv_data(self):
        """ Writes CSV report """

        with open("report.csv", "w") as f:
            f.write(self.csv_values)
