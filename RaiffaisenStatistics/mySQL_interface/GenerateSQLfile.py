# BRANCH IS REDESIGN

from main.EntryNew import EntryNew
from mySQL_interface.credentials import *
import pymysql

connection = pymysql.connect(host=HOSTNAME, user=USERNAME, password=PASSWORD, db=DATABASE,
                             cursorclass=pymysql.cursors.DictCursor)


class GenerateSQLfile:

    def __init__(self):
        self.entries = []

    def __str__(self):
        return "\n".join([str(x) for x in self.entries])

    def add_entry(self, entry):
        if isinstance(entry, EntryNew):
            self.entries.append(entry)
        else:
            raise TypeError('Only EntryNew objects are supported for this method')

    def export_contents(self):
        print("Exporting data to mySQL database ...")
        global connection

        with connection.cursor() as cursor:
            for entry in self.entries:
                # Create a new record
                sql = "INSERT INTO `Spendings_ExtrasDeCont` (`SpreadsheetType`, `Account`, " \
                      "`Label`, `Name`, `Date`, `Value`) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (entry.statementType, entry.account, entry.label, entry.description, entry.datelog.isoformat(), entry.value))
        connection.commit()






