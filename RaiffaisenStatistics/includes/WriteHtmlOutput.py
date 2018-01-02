from html import HTML
from Entries import Entries
from EntryNew import EntryNew

from gpcharts import figure
from pprint import pprint
import os


class WriteHtmlOutput:

	def __init__( self ):

		self.splitPeriodsEntries = {}
		self.buffer = ""
		
	def run ( self ):

		self.loadEntriesCSV ( os.path.join ( "manualInput", "manual_described_operations_2015_2016_2017.csv") )
		if not os.path.exists ( 'output'):
			os.mkdir ( "output" )
			
		for year in self.splitPeriodsEntries:
			entriesForPeriod = self.splitPeriodsEntries[year]
			statistics = self.statistics ( entriesForPeriod )
			self.overviewStatistics ( entriesForPeriod, statistics )
			#self.writeGPchart ( entriesForPeriod, statistics  )
			self.writeIndexHTML ( entriesForPeriod )
		
	def loadEntriesCSV(self, inputFile):
		allEntries = []
		if os.path.isfile( inputFile):
			with open ( inputFile , "r") as file:
				for row in file:
					elements = row.split(";")
					
					if len ( elements ) == 1:
						continue
					if len(elements) == 6:
						elements[5] = elements[5].rstrip()
					elements[4] = elements[4].replace(",", ".")
					
					#    0		  1			  2		3	      4		 5
					# liquidation;September;2017;Decathlon;-286;echipamen
					allEntries.append ( EntryNew ( elements[0], elements[1], elements[2], elements[3], elements[4], elements[5]) )
			
			if 0:
				print "%s | %s | %s | %s | %s | %s \n" % ( elements[0], elements[1], elements[2], elements[3], elements[4], elements[5])

		else:
			print "File '" + inputFile + "' was not found!\n"
		
		monthsFirstSemester  =  [ "August", "September", "October", "November", "December" ]
		monthsSecondSemester  = [  "January", "February", "March", "April", "May", "June", "July" ]

		years = []
		
		for entry in allEntries:
			# how many years are there
			if not ( entry.year in years ):
				years.append ( entry.year )
		for year in years:
			tmpArr = []
			for entry in allEntries:
				if entry.year == year and ( entry.month in monthsFirstSemester ):
					tmpArr.append ( entry ) 
				elif entry.year == ( year + 1 ) and ( entry.month in monthsSecondSemester ):	
					tmpArr.append ( entry )
			self.splitPeriodsEntries[year] = tmpArr

		
	def overviewStatistics(self, data, statistics):

		for currentPeriod in self.splitPeriodsEntries:
			
			index = 0
			totalSpentMonth = statistics['eachMonth']
			totalSpentCategory = statistics['eachCategory']
			htmlOutput = HTML()
			
			table = htmlOutput.table()

			monthsArr  = [  "August", "September", "October", "November",
							"December", "January" , "February" , "March" ,
							"April", "May" , "June" , "July" ]
				
			#for each defined period aug - july
			for currMonth in monthsArr:	
				
				index += 1
				tdBefore = index 
				tdAfter = 12 - index
				entries = data
	

				
				for period in ["liquidation", "advance" ]:
					hasEntries = len ( data )
					headerRow = table.tr (style="border: none")
					headerRow.td ( currMonth, style="background-color: lightblue" )	
					headerRow.td ( period, style="background-color: lightblue; text-align: center" )
					headerRow = table.tr
					secondRow = table.tr
	
					for entryNew in data:
						if currMonth == entryNew.month and period == entryNew.period:
							thirdRow = table.tr
							for time in range(tdBefore):
								#thirdRow.td() #empty div before input
								pass
							thirdRow.td  ( entryNew.description)
							thirdRow.td  ( entryNew.value + " lei", style="text-align: right") 
		
					for time in range( tdAfter ):
						#headerRow.td() #empty div after input
						pass
					headerRow = table.tr ()
					headerRow.td()
					headerRow.td()
				finalRow = table.tr
				finalRow.td( "Total:" , style="background-color:lightgrey; text-align: right")
				finalRow.td ( str ( totalSpentMonth[currMonth] ) + " lei", style="background-color:lightgrey; text-align: right")
				finalRow = table.tr()
				finalRow.td()
				finalRow.td()
		
			outputFilePath = os.path.join ( "output", "%s_%s" % (data[0].year, data[0].year + 1)  + "_overview.html" )
			with open ( outputFilePath, "w") as output:
				output.write ( str ( htmlOutput ) )
				
	def writeGPchart(self, data, statistics):
		totalSpentCategory = statistics['eachCategory']
		totalSpentMonth = statistics['eachMonth']
		
		monthsArr  = [ "August", "September", "October", "November",
					   "December", "January" , "February" , "March" ,
					   "April", "May" , "June" , "July" ]
		os.chdir ("output")
		
		fig = figure  ( title="%s_%s" % (data[0].year, data[0].year + 1 ) + '_labelsCharts', height=600, width=800)   
		fig2 = figure ( title="%s_%s" % (data[0].year, data[0].year + 1 ) + '_yearCharts', height=600, width=800)       

		catData = ['Categories']
		valuesData = ['lei']
		for key, value in sorted(totalSpentCategory.iteritems(), key=lambda (k,v): (v,k)):
			catData.append(key)
			valuesData.append(value * -1)
			
		fig.column(catData,valuesData)
		monthData = ['Months']
		valuesData = ['lei']
		
		for month in monthsArr:
			monthData.append(month)
			valuesData.append( totalSpentMonth[month] * -1 )		

		fig2.column( monthData, valuesData )
		os.chdir ("..")
		
	def writeIndexHTML(self, data):
		with open ( os.path.join ( "output", "index.html" ), "w" ) as f:
			f.write ("<html><body><h4>test</h4></body></html>")
			
	def statistics(self, data):
		statistics = {}
		statistics['eachMonth'] = {}
		statistics['eachCategory'] = {}
		
		monthsArr  = [ "August", "September", "October", "November",
						"December", "January" , "February" , "March" ,
						"April", "May" , "June" , "July" ]
		
		for month in monthsArr:
			statistics['eachMonth'][month] = 0
		
		for entry in data:
			statistics['eachCategory'][entry.label] = 0
			
		for entry in data:	
			statistics['eachMonth'][entry.month] +=  float ( entry.value )
			statistics['eachCategory'][entry.label] += float ( entry.value )
		
		return statistics