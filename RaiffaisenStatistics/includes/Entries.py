from main.EntryNew import EntryNew as EntryNew

from main.RaiffaisenStatement import Statement
import glob
import os
import re


class Entries:

    def __init__(self, folder=os.path.join(os.environ['OneDrive'], "PythonData", "extrasDeCont")):
        self.files = glob.glob(os.path.join(folder, "*.xls*"))
        self.current_year_list = []

    def get_entries(self):
        return self.current_year_list

    def __str__(self):
        return "Entries.__str__ Undefined!"

    def extract_data_excel_sheets(self):
        """ Load data from excel statement files """

        if len(self.files) == 0:
            raise Exception("No files found in folder \n")

        excel_statement_files = sorted(self.files, key=lambda x: str(re.findall(r'\d{4}\.xlsx?$', x)))

        for file in excel_statement_files:

            statement = Statement()
            self.current_year_list.extend(statement.load_statement(file))

        print(f"\nDone loading statement data ... Found {len(self.current_year_list)} entries!\n\n")

