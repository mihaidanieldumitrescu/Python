from EntryNew import EntryNew

from html import HTML

from RaiffaisenStatement import Statement

import xlrd
import glob
import pprint
import os.path
import re
import json

class Entries(EntryNew):
    
    def __init__(self, inputFile):
        self.configFile = json.load(open(os.path.join (os.environ['OneDrive'], "PythonData", "config", "definedLabels.json")))
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
                
        #used mainly for manually extracted csv files

        self.extractDataXLS( inputFile )
        
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

    def retReference(self):
        return self.currentYear
        
    def printValues(self):
        for entry in self.currentYear:
            print str( entry )
    
    def printStatistics(self):
        
        # generate a dict out of all extracted values which will be used to iterate the main dict
        
        ( keyYears, keyMonth, keyPeriods, keyLabels ) = ( {}, {}, {}, {})
        for entryNewItem in self.currentYear:
            ( keyYears[entryNewItem.year],
              keyMonth[entryNewItem.month],
              keyPeriods[entryNewItem.period],
              keyLabels[ entryNewItem.label] ) = (  "", "", "", "" )
        
        # each extracted key found in data array
        for currYear in sorted(keyYears):
            self.htmlFrame[currYear] = {}
            
            for currMonth in sorted(keyMonth):
                
                self.htmlFrame[currYear][currMonth] = {}
                monthStatistics = ""
                bufferMonth = {
                                "leftOtherOp" : [],
                                "rightOtherOp" : [],
                                "leftLabels" : [],
                                "rightLabels" : []
                              }
                tmpStatistics = ""
                liquidationStatistics = []
                advanceStatistics = []
                totalMonth = 0
                totalMonthByLabel = {}
                # first initialisation
                for label in keyLabels:
                    key = label.split(';')[0]
                    if not re.match ("_", key):
                        totalMonthByLabel[key] = 0
                # for advance and liquidation
                for currPeriod in sorted( keyPeriods ):
                    self.htmlFrame[currYear][currMonth][currPeriod] = {
                                                                        'labelSummary' : [],
                                                                        'otherOperations' : []
                                                                      }
                    labelsPeriod = {}
                    otherOperations = currPeriod + " entries: \n\n"
                    labelSummary = ""
                    columnSize = 50
                    
                    for currLabel in keyLabels:
                        labelsPeriod[currLabel] = 0
                    
                    # match values, print others    
                    for currLabel in keyLabels:
                        for currEntry in self.currentYear:
                            if ( currEntry.year == currYear and
                                 currEntry.month == currMonth and
                                 currEntry.period == currPeriod and
                                 currEntry.label == currLabel):
                                
                                # debug print str ( currEntry ) 
                                labelsPeriod[currLabel] += currEntry.value
                                if currEntry.label == "spent;other":
                                    self.htmlFrame[currYear][currMonth][currPeriod]['otherOperations'].append (
                                        { currEntry.description : currEntry.value } )
                                    otherOperations += ( "%s - %s\n" % ( currEntry.description.ljust(30),
                                                                        ( str( currEntry.value) + " lei" ).ljust(10) ) )
                    
                    hasData = 0
                    for label in sorted( labelsPeriod ):
                        
                        # bills;internet       => -109.59 lei
                        # at least one label has value
                        if labelsPeriod[label] != 0:
                            hasData = 1
            
                    if hasData:                    
                        # 2017, 8, liquidation 
                        print "%s, %s, %s" % ( currYear, currMonth, currPeriod )    
                        print '-' * 10 + "\n"
                        lastLabel = ""
                        totalLabel = 0
                        for label in sorted( labelsPeriod ):
                            # if bills != food
                            if lastLabel != label.split(";")[0] and lastLabel != "":
                                if not ( re.match ("^_", lastLabel) and re.match ("^_", label.split(";")[0])):
                                    labelSummary += "\t---\n"
                                    labelSummary += ("\t%s:  %s lei \n" % ( lastLabel, str(totalLabel ).rjust(7)))
                                    labelSummary += "\t\n"
                                    if not re.match ("_", lastLabel):
                                        totalMonth += totalLabel
                                        totalMonthByLabel[lastLabel] += totalLabel
                                    totalLabel = 0
                            totalLabel += labelsPeriod[label]
                            
                            self.htmlFrame[currYear][currMonth][currPeriod]['labelSummary'].append (
                                { label : labelsPeriod [label] } )
                            if labelsPeriod[label] != 0:
                                labelSummary += ("\t%s => %s lei \n" % ( label.ljust(20), str( labelsPeriod[label] ).rjust(7)))
                            else:
                                labelSummary += ("\t%s    %s  -  \n" % ( label.ljust(20), "".rjust(7)))

                                
                            lastLabel = label.split(";")[0]
                            
                        # for the last label (no more labels to compare)
                        labelSummary += "\t---\n"
                        labelSummary += ("\t%s:  %s lei \n" % ( lastLabel, str(  totalLabel ).rjust(7)))
                        totalMonth += totalLabel
                        totalMonthByLabel[lastLabel] += totalLabel
                        
                           # print lastLabel + "\n"
                        #print otherOperations
                        #print labelSummary + "\n"
                        
                        if currPeriod == "liquidation":
                           
                            if otherOperations.split("\n"): 
                                bufferMonth["leftOtherOp"] = otherOperations.split("\n")
                            if labelSummary.split("\n"):
                                bufferMonth["leftLabels"] = labelSummary.split("\n")
                                
                        elif currPeriod == "advance":
                            
                            if otherOperations.split("\n"):
                                bufferMonth["rightOtherOp"] = otherOperations.split("\n")
                                
                            if labelSummary.split("\n"):
                                bufferMonth["rightLabels"] = labelSummary.split("\n")
                        else:
                            self.errorMsg += ( "Error: Label '" + currPeriod + "' should not exist! \n\n " +
                                               otherOperations + labelSummary + "\n"
                                              )
                        # balance elemnts -> equal number of elemnts left and right 
                        deltaOtherOp = int ( len ( bufferMonth['leftOtherOp']) - len (bufferMonth['rightOtherOp']) )
                        deltaLabels =  int ( len ( bufferMonth['leftLabels'] ) - len (bufferMonth['rightLabels'])  )
                        
                        # balancing number of elements from left and right divisions
                        
                        if deltaOtherOp > 0:
                            for i in range ( deltaOtherOp ) : 
                                bufferMonth['rightOtherOp'].append( ( "") )
                        elif deltaOtherOp < 0:
                            for i in range ( - deltaOtherOp ) : 
                                bufferMonth['leftOtherOp'].append( "" )
                        
                        #for labels alsot 
                        if deltaLabels > 0:
                            for i in range ( deltaLabels  ) :
                                bufferMonth['rightLabels'].append( "" )
                        elif deltaLabels < 0:
                            for i in range ( - deltaLabels ) :
                                bufferMonth['leftLabels'].append( "" )
                                
                        if self.verbosity == "low":
                            print "delta values are: '%s' '%s' \n" % (deltaOtherOp, deltaLabels)
                # after each month print results
                
                
                if 0:
                    print "len values: %s %s \n" % (len ( bufferMonth['leftOtherOp'] ), len ( bufferMonth['rightOtherOp'] ))                    
                    self.pp.pprint ( bufferMonth['leftOtherOp'] )
                    self.pp.pprint ( bufferMonth['rightOtherOp'])
                    print "\n"

                # merge and print labels from liquidation and advance for current month
                bufferMonth['rightLabels'].reverse()
                for strLabels in bufferMonth['leftLabels']:
                    monthStatistics += ( "%s | %s \n" % ( strLabels.ljust(columnSize),
                                                          bufferMonth['rightLabels'].pop().ljust(columnSize) ))
                
                # merge other operations from liquidation and advance for current month    
                bufferMonth['rightOtherOp'].reverse()    
                for strOtherOp in bufferMonth['leftOtherOp']:
                    monthStatistics += ( "%s | %s \n" % ( strOtherOp.ljust(columnSize),
                                                          bufferMonth['rightOtherOp'].pop().ljust(columnSize) )) 

                #self.debugOutput = advanceStatistics.join()
                print monthStatistics + "\n"
                
                if totalMonth != 0:
                    print "\t---\n\tMonth total spent: {}\n\n".format( totalMonth )
                    for label in sorted (totalMonthByLabel):
                        self.csvValues += "{};{};{};{}\n".format ( currYear,currMonth,label, totalMonthByLabel[label] )
                    

                #self.pp.pprint( bufferMonth )
                    
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
        
        self.dictCurrentYear[newEnt.month] = {}
        self.dictCurrentYear[newEnt.month][newEnt.period] = []
        self.dictCurrentYear[newEnt.month][newEnt.period].append(newEnt)

    def extractDataXLS(self, dirname):
        files = glob.glob( os.path.join ( os.environ['OneDrive'], "PythonData" ,"extrasDeCont", "*xls"))
        if len ( files ) == 0:
            print "No files found in folder \n"
        
        for filename in files:
           
           statement = Statement ( )
           statement.loadStatement ( filename )
           
           self.dataVerification.append ( "{}-{}".format ( statement.data['headers']['Data generare extras'].split("/")[2],
                                                      statement.data['headers']['Data generare extras'].split("/")[1] ) )
           self.dataVerification = sorted ( self.dataVerification )
           if len  ( statement.data['headers']['Data generare extras'].split("/") ) == 3:
                   (day, month, year) = statement.data['headers']['Data generare extras'].split("/")
           self.newEntry( EntryNew( day, month, "20{}".format ( year ) , "sold precendent", statement.soldPrecendent(), "_soldPrecendent" ))
           for operation in statement.data['operations']:
                    

                   (day, month, year) = operation['Data tranzactiei'].split("/")
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
                       self.newEntry( EntryNew( day, month, year, opDescription, - (debitValue), labelStr ))               
                   elif creditValue:
                       #print "credit: %s : %s \n" % ( opDescription, creditValue )
                       if re.search( self.configFile['salaryFirmName'], operation['Nume/Denumire ordonator/beneficiar'], re.IGNORECASE):
   
                           self.newEntry( EntryNew( day, month, year, opDescription, creditValue, "_salary" ))
                       else:
                           whoTransfered = "_transferredInto"
                           if re.search ( "dumitrescu mihail", opDescription.lower()):
                               whoTransfered = "_transferredTata"
                           print "%s: '%s'" % ( whoTransfered, opDescription )
                           self.newEntry( EntryNew( day, month, year, opDescription, creditValue, whoTransfered ))
                   else:
                       self.errorString += "Warn: No debit or credit values! \n\t* Row is: currRow\n\n"
           
           #self.pp.pprint ( statement.data )

    def labelMe(self, description):

        labelDict = self.configFile['labelDict']
        
        for labelCat in labelDict:
            for label in labelDict [ labelCat ]:    
                if re.search ( labelDict[ labelCat ][ label ], description.lower() ):
                    return "%s;%s" % (labelCat, label)

        return "spent;other"
    def writeHtmlReport(self):
        htmlOutput = HTML()
        table = htmlOutput.table()
        for year in sorted ( self.htmlFrame ,reverse=True):
            print "%s" % (year)
            tr = table.tr
            tr.td (str(year))
            for month in sorted ( self.htmlFrame[year] ,reverse=True):
 
                tr = table.tr
                tr.td (str(month))
                tr_per = table.tr
 
                           
                dictLiq = self.htmlFrame[year][month]['liquidation']
                dictAdv = self.htmlFrame[year][month]['advance']
 
                for entryLiq, entryAdv in zip ( dictLiq['labelSummary'],dictAdv['labelSummary']):
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
            
    def loadDebugValues(self):

        self.currentYear.append ( EntryNew('liquidation', 1, 2017, "Drinks all night", 273, 'fun') )
        self.currentYear.append ( EntryNew('advance', 2, 2017, "Drinks all night", 153, 'fun') )
        self.currentYear.append ( EntryNew('liquidation', 2, 2017, "Girls night", 457, 'fun') )
        self.currentYear.append ( EntryNew('liquidation', 2, 2017, "Girls night", 846, 'fun') )
        self.currentYear.append ( EntryNew('advance', 3, 2017, "Boys night", 121, 'fun') )
        self.currentYear.append ( EntryNew('advance', 3, 2017, "Cinema", 121, 'movies') )
        self.currentYear.append ( EntryNew('advance', 3, 2017, "Popcorn", 121, 'movies') )
