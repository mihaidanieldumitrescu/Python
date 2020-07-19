import os

from mySQL_interface.SQLOperations import SQLOperations
from includes.Entries import Entries

statements_folder = os.path.join(os.environ['OneDrive'], "PythonData", "extrasDeCont")

if __name__ == "__main__":

    ent = Entries(statements_folder)
    ent.extract_data_excel_sheets()

    # Remove empty lines
    entries_list = list(filter(None, ent.get_entries()))

    sql_op = SQLOperations(entries_list)
    print(f"Found a total of {len(sql_op.entries)} entries")
    sql_op.export_contents()