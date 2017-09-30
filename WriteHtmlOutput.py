from html import HTML
from Entries import Entries
from EntryNew import EntryNew
from pprint import pprint


class WriteHtmlOutput:

	def __init__(self, entry):

		self.buffer = ""	        
		self.htmlOutput = HTML()
		self.printMe = entry
		self.totalSpentMonth = {}
		self.totalSpentCategory = {}
		for entry in self.printMe.retReference():
			self.totalSpentCategory[entry.label] = 0
		self.bufferMainTable()
		self.writeOutput()
		

	def bufferMainTable(self):
		monthsArr  = [ "August", "September", "October", "November", "December", "January" , "February" , "March" , "April", "May" , "June" , "July" ]
		

		table = self.htmlOutput.table()
		index = 0

		for currMonth in monthsArr:
		#for each defined period aug - july
			
			index += 1
			tdBefore = index 
			tdAfter = 12 - index
 			self.totalSpentMonth[currMonth] = 0
			entries = self.printMe.dictCurrentYear

			headerRow = table.tr (style="border: none")
			headerRow.td ( currMonth, style="background-color: lightblue" )			
			
			for period in ["liquidation", "advance" ]:
				hasEntries = len ( self.printMe.getEntriesFor( period, currMonth ))
				if not hasEntries:
					continue

				headerRow.td(period, style="background-color: lightblue" )
				secondRow = table.tr

				for entryNew in self.printMe.getEntriesFor( period, currMonth ):
					thirdRow = table.tr
					for time in range(tdBefore):
						thirdRow.td() #empty div before input
					thirdRow.td  ( entryNew.description)
					thirdRow.td  ( entryNew.value ) 
 					self.totalSpentMonth[currMonth] +=  float (entryNew.value )
					self.totalSpentCategory[entryNew.label] += float (entryNew.value )
					
				for time in range(tdAfter):
					headerRow.td() #empty div after input
				headerRow = table.tr ( style="background-color: lightblue")
				headerRow.td()

		self.buffer +=   str (self.htmlOutput ) 

	def bufferHeader(self):
		self.buffer += ""

	def bufferFooter(self):
		self.buffer += ""	

	
	def writeOutput(self):
		output = open ( "budgetStatistics.html", "w")
		output.write ( self.buffer )
		output.close
		print  "by Category\n\n"
		pprint (self.totalSpentCategory )
		print  "\nby Month\n\n"
		pprint ( self.totalSpentMonth )
