import xlrd
import re
import pprint

from Entries import Entries
from EntryNew import EntryNew

class Operations:
    
    
    def __init__(self):
        self.entries = Entries( "" )
        self.errorString = ""
        self.totalSpentMonth = {}
        
    def __del__(self):
        self.entries.printStatistics()
        if self.errorString:
            print "Following errors have been found after run: \n\n" + self.errorString
    
    def extractDataXLS(self, filename):
        print "trying to open " + filename
        book = xlrd.open_workbook( filename )
        sh = book.sheet_by_index(0)
        for rx in range(sh.nrows):
            index = 0
            currRow = sh.row(rx)
            #validate rows
            if ( re.search ( "\d\d\/\d\d/\\d\d\d\d", str(currRow[0]) ) and
                 re.search ( "\d\d\/\d\d/\\d\d\d\d", str(currRow[1]) )):
                data = ( "Read from Excel \n\n" +
                       "  Data: %s \n " +
                       "  Nume: %s\n " +
                       "  Valoare debit: %s Valoare credit: %s\n") % (currRow[1].value,  currRow[11].value.split("|")[0],
                                                                      currRow[2].value,  currRow[3].value )
                (day, month, year) = str(currRow[1].value).split("/")
                opDescription = currRow[11].value.split("|")[0]
                debitValue = currRow[2].value
                creditValue = currRow[3].value
                labelStr = self.labelMe( opDescription )
                
                #self, period="undef", month=-1, year=-1, description.lower()="undef", value=-1, label="undef"
                if debitValue:
                    self.entries.newEntry( EntryNew( day, month, year, opDescription, debitValue, labelStr ))               
                elif creditValue:
                    self.entries.newEntry( EntryNew( day, month, year, opDescription, creditValue, "alimentare cont" ))
                else:
                    self.errorString += "Warn: No debit or credit values! \n\t* Row is: currRow\n\n"

            else:
                #these are the rows we are not interested in
                pass


    def labelMe(self, description):
        label = ""
        food = []
        if re.search ("lebanese food|q s inn|chopstix|subway|toan|kfc|" +
                       "us food|novo|restaurant|taksim|deliciul|expert pranzo",description.lower() ):
            return "food"
        
        if re.search ("lidl|mega|cora|carrefour", description.lower() ):
            return "supermarket"
        
        if re.search ("atm", description.lower()):
            return "cash ATM"

        if re.search ("uber",description.lower() ):
            return "uber"

        if re.search("cinema|therme", description.lower()):
            return "fun"

        if re.search("roumasport", description.lower()):
            return "decathlon"
        
        if re.search("emag", description.lower()):
            return "emag"

        if re.search("enel|engie|upc", description.lower()):
            return "utilitati"

        return "other"