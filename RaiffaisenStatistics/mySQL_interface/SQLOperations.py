# BRANCH IS REDESIGN

from main.EntryNew import EntryNew
from mySQL_interface.credentials import *
import pymysql

connection = pymysql.connect(host=HOSTNAME, user=USERNAME, password=PASSWORD, db=DATABASE,
                             cursorclass=pymysql.cursors.DictCursor)


class SQLOperations:

    def __init__(self, entries=[]):
        self.entries = entries

    def __str__(self):
        return "\n".join([str(x) for x in self.entries])

    def add_entry(self, entry):
        if isinstance(entry, EntryNew):
            self.entries.append(entry)
        else:
            raise TypeError('Only EntryNew() objects are supported for this method')

    def export_contents(self):
        """ Export data to mySQL database ...
        :return:
        """
        print("Exporting data to mySQL database ...")
        global connection

        commit = True
        with connection.cursor() as cursor:
            print("Warning! ExtrasDeCont table will be truncated!")
            input("Press enter to continue!")
            cursor.execute("TRUNCATE TABLE ExtrasDeCont")
            print("Done! Attempting to write entries to the database ...")
            for entry in self.entries:
                # Create a new record

                sql = "INSERT INTO " \
                      "     `ExtrasDeCont` " \
                      "         (`SpreadsheetType`, `Account`, `Label`, `Name`, `Date`, `Value`) " \
                      "     VALUES " \
                      "         (%s, %s, %s, %s, %s, %s)"
                cursor.execute(sql,
                               (entry.statementType,
                                entry.account,
                                entry.label,
                                entry.description,
                                entry.date_log.isoformat(),
                                entry.value))
        if commit:
            connection.commit()
            print("Changes committed!")
        else:
            print("No changes were made to the database!")

        print("Done!\n")






