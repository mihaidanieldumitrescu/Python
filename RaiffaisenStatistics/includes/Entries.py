from main.EntryNew import EntryNew as EntryNew

from main.RaiffaisenStatement import Statement
from json_config.JsonConfig import JsonConfig

import logging
import datetime
import glob
import os
import sys
import re
import pprint


class Entries:

    def __init__(self, input_file):
        self.config_dict = {}
        self.current_year_list = []
        self.current_year_dict = {}

        self.statistics_dict = {}
        self.manual_entries = []
        self.csv_values = ""

        self.html_frame = {}
        self.verbosity = "none"
        self.error_msg = ""
        self.debug_output = ""
        self.json_config = JsonConfig()

        logging.basicConfig(filename='logfile.log', filemode='w', level=logging.DEBUG)

    def get_labels(self):
        labels = {}

        for item in self.current_year_list:
            labels[item.label] = None

        key_list = labels.keys()

        return key_list

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
            if beginning_period_date <= item.datelog < end_period_date:
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
            liquidation_dates.append(element.datelog)
        liquidation_dates.append(datetime.date(2040, 1, 1))  # dummy date
        return liquidation_dates

    def __iter__(self):

        self.paymentLiquidationDatesArr = self.return_salary_payment_dates()
        self.index = len(self.paymentLiquidationDatesArr) - 1

        if len(self.paymentLiquidationDatesArr) < 2:
            print("( Entries::__iter__ ) Error! paymentLiquidationDatesArr has less than two elements!")
            sys.exit(1)

        logging.info(
            "__iter__ initialized with paymentLiquidationDatesArr: \n{}\n\n".format(self.paymentLiquidationDatesArr))

        return self

    def __next__(self):

        #  this will iterate for each month
        if self.index > 0:

            begining_period_date = self.paymentLiquidationDatesArr[self.index - 1]
            end_period_date = self.paymentLiquidationDatesArr[self.index]
            print("Reading data from '{}' to '{}' ...".format(begining_period_date,
                                                              end_period_date - datetime.timedelta(days=1)))
            logging.info(
                "__next__ '{}' -> '{}'".format(begining_period_date, end_period_date - datetime.timedelta(days=1)))
            data = self.return_month_segment_data(begining_period_date, end_period_date)

            self.index -= 1
            return data
        else:
            print
            print("Iteration reached it's end. Last begin value is {}".format(
                self.paymentLiquidationDatesArr[self.index + 1]))
            raise StopIteration

    def __str__(self):
        tmp = ""
        for item in self.statistics_dict.iteritems():
            tmp += str(item) + "\n"
        return tmp

    def return_values_dict(self):
        temp_str = ""
        for month in self.current_year_dict:
            for period in self.current_year_dict[month]:
                for entry in self.current_year_dict[month][period]:
                    temp_str += str(entry)
        return temp_str

    def get_entries_for(self, period, month):

        # print("Looking for entries for month '" + month + "' and period '" + period + "' :\n")
        entries_found = []
        for entry in self.current_year_list:
            if entry.period == period and entry.month == month:
                entries_found.append(entry)
        return entries_found

    def new_entry(self, newEnt):
        """ Add a new EntryNew object """
        self.current_year_list.append(newEnt)
        self.current_year_list.sort(key=lambda x: x.datelog)

        self.current_year_dict[newEnt.month] = {}
        self.current_year_dict[newEnt.month][newEnt.period] = []
        self.current_year_dict[newEnt.month][newEnt.period].append(newEnt)

    def extract_data_excel_sheets(self):
        """ Load data from excel statement files """

        files = glob.glob(os.path.join(os.environ['OneDrive'], "PythonData", "extrasDeCont", "*xls*"))

        self.json_config.load_file()

        if len(files) == 0:
            raise Exception("No files found in folder \n")

        for filename in sorted(files, key=lambda x: str(re.findall(r'\d{4}\.xlsx?$', x))):

            statement = Statement()
            statement.load_statement(filename)

            if statement.headers.get('Data generare extras'):
                extract_statement_regex = re.match(r'(\d{2})/(\d{2})/(\d{2})',
                                                   statement.headers['Data generare extras'])
            elif statement.headers.get('Perioada'):
                extract_statement_regex = re.match(r'de la (\d{2})/(\d{2})/(\d{2})',
                                                   statement.headers['Perioada'])
            else:
                raise ValueError('Perioada/Data generare extras expected in statement headers')

            if extract_statement_regex:
                (day, month, year) = (extract_statement_regex.group(1), extract_statement_regex.group(2), extract_statement_regex.group(3))
                sold_precendent_entry = EntryNew(day=day, month=month, year="20{}".format(year),
                                                 description="Sold precendent!", value=statement.sold_precendent(),
                                                 label="_soldPrecendent",
                                                 account=statement.accountName, statement_type=statement.statementType)
                self.new_entry(sold_precendent_entry)
                logging.info("(extractDataXLS ) Sold precendent: '{}'".format(sold_precendent_entry))
            else:
                logging.warn("(extractDataXLS ) Date format is not what expected! Date found: '{}'".format(
                    statement.headers['Data generare extras']))

            # logging.info ("( extractDataXLS ) For filename '{}', extracted date was '{}.{}.{}'".format(filename, day, month, year ))

            for operation in statement.operations:
                (day, month, year) = operation['Data utilizarii cardului'].split("/")
                op_description = operation['Descrierea tranzactiei'].split("|")[0]
                if re.match("OPIB", operation['Descrierea tranzactiei']):
                    op_description = operation['Descrierea tranzactiei'].split("|")[1]
                debit_value = operation['Suma debit']
                credit_value = operation['Suma credit']
                label_str = self.label_me(op_description)

                data = ("  Data: %s Operatie: %s Eticheta: %s\n " +
                        "  Valoare debit: %s Valoare credit: %s\n") % (
                       operation['Data utilizarii cardului'], op_description, self.label_me(op_description),
                       debit_value, credit_value)
                if self.verbosity == "high":
                    print(data)

                # self, period="undef", month=-1, year=-1, description.lower()="undef", value=-1, label="undef"
                if "Trz IB conturi proprii" in op_description:
                    print("(Does not work!) Skipping 'Trz IB conturi proprii' entry!")

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
                    # print("credit: %s : %s \n" %(op_description, credit_value ))

                    if re.search(self.json_config.salaryIdentifier, operation['Nume/Denumire ordonator/beneficiar'],
                                 re.IGNORECASE):
                        if 1 <= int(day) <= 15:
                            self.new_entry(EntryNew(day=day,
                                                    month=month,
                                                    year=year,
                                                    description=op_description,
                                                    value=credit_value,
                                                    label="_salary",
                                                    account=statement.accountName,
                                                    statement_type=statement.statementType))
                        else:
                            self.new_entry(
                                EntryNew(day=day,
                                         month=month,
                                         year=year,
                                         period='advance',
                                         description=op_description,
                                         value=credit_value,
                                         label="_salary",
                                         account=statement.accountName,
                                         statement_type=statement.statementType))
                    else:
                        transfer_label = "_transferredInto"

                        # Changing the label to _transferredTata would filter out these entries
                        # if re.search("dumitrescu mihail", op_description, re.I):
                        #     transfer_label = "_transferredTata"

                        self.new_entry(EntryNew(day=day,
                                                month=month,
                                                year=year,
                                                description=op_description,
                                                value=credit_value,
                                                label=transfer_label,
                                                account=statement.accountName,
                                                statement_type=statement.statementType))
                else:
                    self.error_msg += f"Warn: No debit or credit values! \n\t* Row is: {pprint.pformat(operation)}\n\n"
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
