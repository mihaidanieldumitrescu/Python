from html import HTML
from Entries import Entries
from EntryNew import EntryNew

from gpcharts import figure
from pprint import pprint


class WriteHtmlOutput:

	def __init__(self, entry):
		self.inputFileName = entry.csvInputfile
		self.buffer = ""
		self.monthsArr  = [ "August", "September", "October", "November", "December", "January" , "February" , "March" , "April", "May" , "June" , "July" ]	
		self.fig = figure(title=self.inputFileName + '_by_categories', height=600, width=800)   
		self.fig2 = figure(title=self.inputFileName + '_by_months', height=600, width=800)       
		self.htmlOutput = HTML()
		self.printMe = entry
		self.totalSpentMonth = {}
		self.totalSpentCategory = {}
		for entry in self.printMe.retReference():
			self.totalSpentCategory[entry.label] = 0
		self.bufferMainTable()
		self.writeOutput()
		self.writeGPchart()


	def bufferMainTable(self):

		monthsArr = self.monthsArr
		table = self.htmlOutput.table()
		index = 0

		#for each defined period aug - july
		for currMonth in monthsArr:
		
			
			index += 1
			tdBefore = index 
			tdAfter = 12 - index
			self.totalSpentMonth[currMonth] = 0
			entries = self.printMe.dictCurrentYear

			headerRow = table.tr (style="border: none")
			headerRow.td ( currMonth, style="background-color: lightblue" )	
			headerRow.td ()		
			
			for period in ["liquidation", "advance" ]:
				hasEntries = len ( self.printMe.getEntriesFor( period, currMonth ))
				if not hasEntries:
					continue

				headerRow.td(period, style="background-color: lightblue; text-align: center" )
				headerRow = table.tr
				secondRow = table.tr

				for entryNew in self.printMe.getEntriesFor( period, currMonth ):
					thirdRow = table.tr
					for time in range(tdBefore):
						thirdRow.td() #empty div before input
					thirdRow.td  ( entryNew.description)
					thirdRow.td  ( entryNew.value + " lei", style="text-align: right") 
					self.totalSpentMonth[currMonth] +=  float (entryNew.value )
					self.totalSpentCategory[entryNew.label] += float (entryNew.value )

				for time in range(tdAfter):
					headerRow.td() #empty div after input
				headerRow = table.tr ()
				headerRow.td()
				headerRow.td()
		finalRow = table.tr
		finalRow.td( "Total:" , style="background-color:lightgrey; text-align: right")
		for currMonth in monthsArr:
			if self.totalSpentMonth[currMonth] != 0:
				finalRow.td ( str ( self.totalSpentMonth[currMonth] ) + " lei", style="background-color:lightgreen; text-align: right")

		self.buffer +=   str (self.htmlOutput )

	def bufferHeader(self):
		self.buffer += ""

	def bufferFooter(self):
		self.buffer += ""	

	
	def writeOutput(self):
		output = open ( self.inputFileName + "_table_by_month.html", "w")
		output.write ( self.buffer )
		output.close
		print  "by Category\n\n"
		pprint ( self.totalSpentCategory )
		print  "\nby Month\n\n"
		pprint ( self.totalSpentMonth )

	def writeGPchart(self):
		catData = ['Categories']
		valuesData = ['lei']
		for cat in self.totalSpentCategory:
			catData.append(cat)
			valuesData.append(self.totalSpentCategory[cat] * -1)
		self.fig.column(catData,valuesData)
		monthData = ['Months']
		valuesData = ['lei']
		for month in self.monthsArr:
			monthData.append(month)
			valuesData.append(self.totalSpentMonth[month] * -1)		

		self.fig2.column(monthData,valuesData)
