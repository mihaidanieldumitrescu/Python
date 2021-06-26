import os

from mySQL_interface.InsertDatabaseEntries import InsertDatabaseEntries
from includes.StatementData import StatementData

statements_folder = os.path.join(os.environ['OneDrive'], "PythonData", "extrasDeCont")

if __name__ == "__main__":

    ent = StatementData(statements_folder)
    ent.extract_data_excel_sheets()

    sql_op = InsertDatabaseEntries(ent.statements)
    sql_op.export_contents()
