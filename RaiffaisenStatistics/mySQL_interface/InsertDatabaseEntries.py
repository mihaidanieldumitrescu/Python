# BRANCH IS REDESIGN

from main.EntryNew import EntryNew
from mySQL_interface.credentials import *
import pymysql

connection = pymysql.connect(host=HOSTNAME, user=USERNAME, password=PASSWORD, db=DATABASE,
                             cursorclass=pymysql.cursors.DictCursor)

TABLE_NAME = 'spreadsheet_entries'
STATEMENT_SHEETS = 'statement_sheets'


class InsertDatabaseEntries:

    def __init__(self, statements=[]):
        self.statements = statements

    def __str__(self):
        return "\n".join([str(x) for x in self.entries])

    def add_entry(self, entry):
        if isinstance(entry, EntryNew):
            self.entries.append(entry)
        else:
            raise TypeError('Only EntryNew() objects are supported for this method')

    @staticmethod
    def is_statement_already_inserted(statement, inserted_statements):

        for cmp in inserted_statements:

            attribute_1 = 'data_generare_extras'
            attribute_2 = 'cod_iban'
            attribute_3 = 'tranzactii'

            if statement.get(attribute_1) == cmp.get(attribute_1) and \
               statement.get(attribute_2) == cmp.get(attribute_2):
                assert statement.get(attribute_3) == cmp.get(attribute_3), \
                       f"Local statement {statement} has a different transaction value than expected: " \
                       f"{statement.get(attribute_3)} !=  {cmp.get(attribute_3)}\n"
                return True
        return False

    def export_contents(self):
        """ Export data to mySQL database ...
        :return:
        """
        print("Exporting data to mySQL database ...")
        global connection

        with connection.cursor() as cursor:
            cursor.execute("SELECT data_generare_extras, cod_iban, tranzactii FROM statement_sheets")
            database_statements = cursor.fetchall()

        nothing_exported = True
        for spreadsheet_statement in self.statements:

            if not self.is_statement_already_inserted(spreadsheet_statement.get_identifier_dict(),
                                                      database_statements):
                sql = f"""\
            INSERT INTO {STATEMENT_SHEETS}
                (data_generare_extras, numar_extras, cod_iban, tranzactii)
                    VALUES
                        (%s, %s, %s, %s)"""

                s_dict = spreadsheet_statement.get_identifier_dict()

                with connection.cursor() as cursor:
                    cursor.execute(sql,
                                   (s_dict.get('data_generare_extras'),
                                    0,  # numar extras
                                    s_dict.get('cod_iban'),
                                    s_dict.get('tranzactii')))

                commit = True
                with connection.cursor() as cursor:
                    nothing_exported = False
                    print(f"Inserting new data from {spreadsheet_statement.get_identifier_dict()}")

                    for entry in spreadsheet_statement.entries:

                        sql = f"""\
            INSERT INTO `{TABLE_NAME}`
                (`spreadsheet_type`, `account_name`, `label`, `category`,
                 `transaction_description`, `transaction_date`, `transaction_debit`, `transaction_credit`)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s)"""

                        cursor.execute(sql,
                                       (entry.statementType,
                                        entry.account,
                                        "".join(entry.label.split('.')[:1]),
                                        "".join(entry.label.split('.')[1:]),
                                        entry.description,
                                        entry.date_log.isoformat(),
                                        entry.suma_debit if entry.suma_debit else 0.0,
                                        entry.suma_credit if entry.suma_credit else 0.0))
                if commit:
                    connection.commit()
                    print("Changes committed!")
                else:
                    print("No changes were made to the database!")
        if nothing_exported:
            print("No new entries added to db...")






