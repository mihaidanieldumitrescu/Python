import os

from mySQL_interface.SQLOperations import SQLOperations
from includes.Entries import Entries

class Operations:

    def __init__(self, verbosity="none"):
        self.entries = None

    def load_excel_statements(self, statement_input_dir):
        self.entries = Entries(statement_input_dir)
        self.entries.extract_data_excel_sheets()

    def get_entries_as_list(self):

        # monthly_report = [ EntryNew( ... ), EntryNew( ... ), ... ]
        for monthly_report in self.entries:
            for currEntry in monthly_report:
                yield currEntry


if __name__ == "__main__":
    statements_folder = os.path.join(os.environ['OneDrive'], "PythonData", "extrasDeCont")
    o = Operations()
    o.load_excel_statements(statements_folder)
    entries_list = list(o.get_entries_as_list())
    sql_op = SQLOperations(entries_list)
    print(f"Found a total of {len(sql_op.entries)} entries")
    sql_op.export_contents()
