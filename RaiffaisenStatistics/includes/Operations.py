import xlrd
import re
import pprint
import json

from Entries import Entries
from EntryNew import EntryNew

class Operations:
    
    
    def __init__(self, verbosity="none"):
        self.configFile = json.load(open('config/config.json'))
        self.entries = Entries( "" )
        self.errorString = ""
        self.totalSpentMonth = {}
        self.verbosity = verbosity
        
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

                (day, month, year) = str(currRow[1].value).split("/")
                opDescription = currRow[11].value.split("|")[0]
                if re.search("^OPIB", currRow[11].value):
                   opDescription = currRow[11].value.split("|")[1]
                debitValue = currRow[2].value
                creditValue = currRow[3].value
                labelStr = self.labelMe( opDescription )

                data = ( "  Data: %s Operatie: %s Eticheta: %s\n " +
                         "  Valoare debit: %s Valoare credit: %s\n") % (currRow[1].value,  opDescription, self.labelMe( opDescription ),
                                                                      debitValue,  creditValue )
                if self.verbosity == "high":
                    print data
                
                #self, period="undef", month=-1, year=-1, description.lower()="undef", value=-1, label="undef"
                if debitValue:
                    self.entries.newEntry( EntryNew( day, month, year, opDescription, debitValue, labelStr ))               
                elif creditValue:
                    #print "credit: %s : %s \n" % ( opDescription, creditValue )
                    if re.search( self.configFile['salaryFirmName'], currRow[8].value, re.IGNORECASE):

                        self.entries.newEntry( EntryNew( day, month, year, opDescription, creditValue, "_salary" ))
                    else:
                        self.entries.newEntry( EntryNew( day, month, year, opDescription, creditValue, "_transferredInto" ))
                else:
                    self.errorString += "Warn: No debit or credit values! \n\t* Row is: currRow\n\n"

            else:
                #these are the rows we are not interested in
                pass


    def labelMe(self, description):

        labelDict = self.configFile['labelDict']
        
        for label in labelDict:    
            if re.search ( labelDict[label], description.lower() ):
                return label

        return "spent.other"