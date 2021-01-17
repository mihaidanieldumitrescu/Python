import os

from mySQL_interface.SQLOperations import SQLOperations
from includes.Entries import Entries

statements_folder = os.path.join(os.environ['OneDrive'], "PythonData", "extrasDeCont")

if __name__ == "__main__":

    ent = Entries(statements_folder)
    ent.extract_data_excel_sheets()

    sql_op = SQLOperations(ent.statements)
    sql_op.export_contents()
