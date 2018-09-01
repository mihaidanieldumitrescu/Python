from EntryNew import EntryNew

from html import HTML

from RaiffaisenStatement import Statement
from collections import deque
from dateutil.relativedelta import relativedelta

import logging
import xlrd
import glob
import pprint
import os.path
import re
import json

class Entries(EntryNew):
    
    def __init__(self, inputFile):
        self.configDict = {}
         #another line graph, but with two data types. Also adding title
        self.currentYear = []
        #this is intermediary
        self.dictCurrentYear = {}
        
        #{year}{month}{period} => value
        self.statistics = {}
        self.manualEntries = []
        self.csvValues = ""
        
        self.dataVerification = []

        self.htmlOutput = HTML()
        self.htmlFrame = {}
        self.verbosity = "none" 
        self.pp = pprint.PrettyPrinter()
        self.errorMsg = ""
        self.debugOutput = ""
        self.verbosity = "none"
        
        logging.basicConfig(filename='logfile.log',filemode='w', level=logging.DEBUG)
 
        #used mainly for manually extracted csv files

        self.extractDataXLS( inputFile )
        # self.pp.pprint ( self.currentYear )
    def getLabels (self):
        labels = {}
        
        for item in self.currentYear:

            labels[ item.label ] = None

        keyList = labels.keys()
 
        return keyList
    
    def returnMonthData ( self, year, month ):
        data = []
        for item in self.currentYear:
            if item.year == year and item.month == month:
                data.append ( item )
        return data
        
    def __iter__(self):
        
        # first entry in array by date
        self.dateSeed = self.currentYear[0].datelog
        self.lastDate = self.currentYear[-1].datelog
        logging.info("dateSeed: {} lastDate: {}".format ( self.dateSeed, self.lastDate ) )
        return self
    
    def next(self):
        
        # this will iterate for each month
        if ( self.dateSeed <= self.lastDate + relativedelta(months=1) ) :
            data = self.returnMonthData ( self.dateSeed.year, int ( self.dateSeed.month )  )
            self.dateSeed += relativedelta(months=1)
            return data
        else:
            print "Iteration reached it's end. Dateseed value is {}".format (  self.dateSeed ) 
            raise StopIteration

    
    def __del__(self):
        #print json.dumps( self.htmlFrame )
        if self.debugOutput != "":
            print "(Entries) Debug output: \n\n" + self.debugOutput + "\n" 

        if self.errorMsg != "":
            print "(Entries) Errors found: \n\n" + self.errorMsg + "\n"
            
        #self.pp.pprint( self.dataVerification )
        
    def __str__(self):
        tmp = ""
        for item in self.statistics.iteritems():
            tmp += str( item ) + "\n"
        return tmp
                    
    def retValuesDict(self):
        tempStr = ""
        for month in self.dictCurrentYear:
            for period in self.dictCurrentYear[month]:
                for entry in self.dictCurrentYear[month][period]:
                    tempStr += str ( entry )
        return tempStr
    
    def iterateByDate (self):
        pass
    
    def getEntriesFor(self, period, month):

        # print "Looking for entries for month '" + month + "' and period '" + period + "' :\n"	
        entriesFound = []
        for entry in self.currentYear:
            if entry.period == period and entry.month == month:
                entriesFound.append(entry)
        return entriesFound
    
    def newEntry(self, newEnt):
        self.currentYear.append ( newEnt )
        self.currentYear.sort(key=lambda x: x.datelog)
        
        self.dictCurrentYear[newEnt.month] = {}
        self.dictCurrentYear[newEnt.month][newEnt.period] = []
        self.dictCurrentYear[newEnt.month][newEnt.period].append(newEnt)

    def extractDataXLS(self, dirname):
        
        # define path to where excel files are saved
        
        files = glob.glob( os.path.join ( os.environ['OneDrive'], "PythonData" ,"extrasDeCont", "*xls"))
        
        with open ( os.path.join ( os.environ['OneDrive'], "PythonData", "config", "definedLabels.json") )  as f:
            self.configDict = json.load( f )
            
        if len ( files ) == 0:
            raise Exception ( "No files found in folder \n" )
        
        for filename in files:
           
           statement = Statement ( )
           statement.loadStatement ( filename )
           
           extractStatementRegex = re.match ( r'(\d{2})/(\d{2})/(\d{2})', statement.data['headers']['Data generare extras'] )
           if extractStatementRegex:
                   ( day, month, year ) = ( extractStatementRegex.group(1), extractStatementRegex.group(2), extractStatementRegex.group(3) )
                   soldPrecendentEntry = EntryNew( day=day, month=month, year="20{}".format ( year ) , description="Sold precendent!", value=statement.soldPrecendent(), label="_soldPrecendent" )
                   self.newEntry(soldPrecendentEntry)
                   logging.info(" ( extractDataXLS ) Sold precendent: '{}'".format ( soldPrecendentEntry )  )                 
           else:
                   logging.warn(" ( extractDataXLS ) Date format is not what expected! Date found: '{}'".format ( statement.data['headers']['Data generare extras'] ))                   
 
           #logging.info ("( extractDataXLS ) For filename '{}', extracted date was '{}.{}.{}'".format ( filename, day, month, year ))
 
           for operation in statement.data['operations']:
                    
                   ( day, month, year ) = operation['Data tranzactiei'].split("/")
                   opDescription = operation['Descrierea tranzactiei'].split("|")[0]
                   if re.match("OPIB", operation['Descrierea tranzactiei']):
                      opDescription = operation['Descrierea tranzactiei'].split("|")[1]
                   debitValue = operation['Suma debit']
                   creditValue = operation['Suma credit']
                   labelStr = self.labelMe( opDescription )
   
                   data = ( "  Data: %s Operatie: %s Eticheta: %s\n " +
                            "  Valoare debit: %s Valoare credit: %s\n") % ( operation['Data tranzactiei'],  opDescription, self.labelMe( opDescription ),
                                                                         debitValue,  creditValue )    
                   if self.verbosity == "high":
                       print data
                   
                   #self, period="undef", month=-1, year=-1, description.lower()="undef", value=-1, label="undef"
                   if debitValue:
                       self.newEntry( EntryNew( day=day, month=month, year=year, description=opDescription, value=-(debitValue), label=labelStr ))               
                   elif creditValue:
                       #print "credit: %s : %s \n" % ( opDescription, creditValue )
                       if re.search( "|".join (self.configDict['salaryFirmName'] ), operation['Nume/Denumire ordonator/beneficiar'], re.IGNORECASE):
   
                           self.newEntry( EntryNew ( day=day, month=month, year=year, description=opDescription, value=creditValue, label="_salary" ))
                       else:
                           whoTransfered = "_transferredInto"
                           if re.search ( "dumitrescu mihail", opDescription.lower()):
                               whoTransfered = "_transferredTata"
                           print "%s: '%s'" % ( whoTransfered, opDescription )
                           self.newEntry( EntryNew ( day=day, month=month, year=year, description=opDescription, value=creditValue, label=whoTransfered ) )
                   else:
                       self.errorString += "Warn: No debit or credit values! \n\t* Row is: currRow\n\n"
           
           #self.pp.pprint ( statement.data )

    def labelMe(self, description):

        masterLabels = self.configDict['labelDict']
        
        # { 	"leisure" :  {
		#			            "film": [ "cinema", "avatar media project" ] }
        # ...
        
        for masterLabel in masterLabels:
            for childLabel in masterLabels [ masterLabel ]:    
                if re.search ( "|".join ( masterLabels [ masterLabel ][ childLabel ]), description.lower() ):
                    return "%s;%s" % ( masterLabel, childLabel )  

        return "spent;other"
    
    def writeHtmlReport(self):
        htmlOutput = HTML()
        table = htmlOutput.table()
        for year in sorted ( self.htmlFrame ,reverse=True):
            print "%s" % (year)
            tr = table.tr
            tr.td (str(year))
            for month in sorted ( self.htmlFrame[year], reverse=True ):
 
                tr = table.tr
                tr.td (str(month))
                tr_per = table.tr
                           
                dictLiq = self.htmlFrame[year][month]['liquidation']
                dictAdv = { 'labelSummary' : [] }
                if 0:
                    # will not be used anymore
                    dictAdv = self.htmlFrame[year][month]['advance']
 
                for entryLiq, entryAdv in zip ( dictLiq['labelSummary'], dictAdv['labelSummary'] ): # 
                    tr_nr = table.tr
                    for key in entryLiq:
                        tr_nr.td (str(key))
                        tr_nr.td (str(entryLiq[key]))
                        
                    for key in entryAdv:
                        tr_nr.td (str(key))
                        tr_nr.td (str(entryAdv[key]))
                        
                    #for entry in dictCurr['otherOperations']:
                        #tr_per.td (str(entry))
 
                
        with open ("report.html", "w") as f:
            f.write(str (htmlOutput))
            
    def writeCSVdata(self):
        with open ("report.csv", "w") as f:
            f.write ( self.csvValues )
